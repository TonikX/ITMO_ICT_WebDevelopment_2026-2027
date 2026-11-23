"""Signed bidirectional keyset pagination for the flight board."""
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
from django.core import signing
from django.db.models import Max, Q
from django.utils.timezone import is_aware

PAGE_SIZE = 10
SALT = 'skyboard.flight-cursor.v1'


class InvalidCursor(ValueError):
    pass


@dataclass
class CursorPage:
    objects: list
    previous_cursor: str | None
    next_cursor: str | None

    def __iter__(self):
        return iter(self.objects)


def boundary(at, pk, *, before=False):
    lookup = 'lt' if before else 'gt'
    return Q(**{f'departure_at__{lookup}': at}) | (
        Q(departure_at=at) & Q(**{f'pk__{lookup}': pk}))


def paginate(qs, token, filters):
    # departure_at alone is not unique; pk is the tie-breaker and both are indexed.
    digest = hashlib.sha256(json.dumps(filters, sort_keys=True, default=str).encode()).hexdigest()
    direction = 'next'
    anchor = None
    if token:
        try:
            payload = signing.loads(token, salt=SALT, max_age=86400)
            at = datetime.fromisoformat(payload['at'])
            pk, ceiling, direction = payload['pk'], payload['ceiling'], payload['direction']
            if (payload['filters'] != digest or direction not in {'next', 'previous'}
                or not is_aware(at) or type(pk) is not int or type(ceiling) is not int
                or pk < 1 or ceiling < pk):
                raise ValueError
            anchor = (at, pk)
        except (signing.BadSignature, ValueError, TypeError, KeyError, AttributeError):
            raise InvalidCursor('Курсор повреждён, устарел или относится к другому поиску.') from None
    else:
        ceiling = qs.aggregate(value=Max('pk'))['value'] or 0
    base = qs.filter(pk__lte=ceiling)
    page_qs = base.filter(boundary(*anchor, before=direction == 'previous')) if anchor else base
    backwards = direction == 'previous'
    ordering = ('-departure_at', '-pk') if backwards else ('departure_at', 'pk')
    items = list(page_qs.order_by(*ordering)[:PAGE_SIZE + 1])[:PAGE_SIZE]
    if backwards:
        items.reverse()

    def encode(item, direction):
        return signing.dumps({'at': item.departure_at.isoformat(), 'pk': item.pk,
            'direction': direction, 'ceiling': ceiling, 'filters': digest}, salt=SALT, compress=True)

    previous = next_token = None
    if items:
        first, last = items[0], items[-1]
        if base.filter(boundary(first.departure_at, first.pk, before=True)).exists():
            previous = encode(first, 'previous')
        if base.filter(boundary(last.departure_at, last.pk)).exists():
            next_token = encode(last, 'next')
    return CursorPage(items, previous, next_token)
