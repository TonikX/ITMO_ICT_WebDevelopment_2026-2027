"""Защита доступа: кто что может делать. Права проверяются в представлениях,
а скрытие кнопок в шаблонах — лишь удобство, а не защита."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def is_admin(user):
    return user.is_authenticated and user.is_staff


def reviews_manageable_by(user, reviews):
    """Отзывы, которые пользователь вправе удалить: свои, а администратор — любые."""
    return reviews if is_admin(user) else reviews.filter(author=user)


class StaffRequiredMixin(UserPassesTestMixin):
    """Аноним уходит на вход, обычный пользователь получает 403."""

    def test_func(self):
        return is_admin(self.request.user)


class OwnerOnlyMixin(LoginRequiredMixin):
    """Объект доступен только владельцу: чужой даёт 404, а не 403, чтобы не раскрывать, что он есть."""

    owner_field = "user"

    def get_queryset(self):
        return super().get_queryset().filter(**{self.owner_field: self.request.user})
