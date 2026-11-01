"""Защита доступа: кто что может, проверено на уровне представлений, а не шаблонов."""
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

from conferences.models import Conference, Participation, Review
from conferences.permissions import is_admin, reviews_manageable_by

from .base import BaseTestCase, make_participation, make_review


class IsAdminTests(BaseTestCase):
    def test_roles(self):
        self.assertFalse(is_admin(AnonymousUser()))
        self.assertFalse(is_admin(self.user))
        self.assertTrue(is_admin(self.staff))


class StaffOnlyViewsTests(BaseTestCase):
    def urls(self):
        p = make_participation(self.conf, self.user)
        return [
            reverse("conference-create"),
            reverse("conference-update", args=[self.conf.pk]),
            reverse("conference-delete", args=[self.conf.pk]),
            reverse("participation-result", args=[p.pk]),
        ]

    def test_anonymous_is_redirected_to_login(self):
        for url in self.urls():
            with self.subTest(url=url):
                r = self.client.get(url)
                self.assertEqual(r.status_code, 302)
                self.assertIn(reverse("login"), r["Location"])

    def test_regular_user_gets_403_on_get_and_post(self):
        self.login("user")
        for url in self.urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)
                self.assertEqual(self.client.post(url, {}).status_code, 403)

    def test_staff_has_access(self):
        self.login("staff")
        for url in self.urls():
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_regular_user_cannot_change_result(self):
        p = make_participation(self.conf, self.user)
        self.login("user")
        self.client.post(reverse("participation-result", args=[p.pk]), {"result": "recommended"})
        p.refresh_from_db()
        self.assertEqual(p.result, Participation.Result.PENDING)

    def test_regular_user_cannot_delete_conference(self):
        self.login("user")
        self.client.post(reverse("conference-delete", args=[self.conf.pk]))
        self.assertTrue(Conference.objects.filter(pk=self.conf.pk).exists())


class LoginRequiredTests(BaseTestCase):
    def test_anonymous_is_redirected(self):
        p = make_participation(self.conf, self.user)
        for name, args in [
            ("participation-create", [self.conf.pk]),
            ("review-create", [self.conf.pk]),
            ("my-participations", []),
            ("participation-update", [p.pk]),
            ("participation-delete", [p.pk]),
        ]:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 302)


class OwnParticipationTests(BaseTestCase):
    def test_foreign_participation_is_404(self):
        p = make_participation(self.conf, self.other)
        self.login("user")
        self.assertEqual(self.client.get(reverse("participation-update", args=[p.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("participation-delete", args=[p.pk])).status_code, 404)
        self.assertTrue(Participation.objects.filter(pk=p.pk).exists())

    def test_staff_has_no_special_access_to_foreign_participation(self):
        p = make_participation(self.conf, self.other)
        self.login("staff")
        self.assertEqual(self.client.get(reverse("participation-update", args=[p.pk])).status_code, 404)


class ReviewPermissionsTests(BaseTestCase):
    def test_queryset_scoping(self):
        mine = make_review(self.conf, self.user)
        theirs = make_review(self.conf, self.other)
        self.assertEqual(list(reviews_manageable_by(self.user, Review.objects.all())), [mine])
        self.assertEqual(set(reviews_manageable_by(self.staff, Review.objects.all())), {mine, theirs})

    def test_delete_views(self):
        review = make_review(self.conf, self.user)
        url = reverse("review-delete", args=[review.pk])
        self.login("other")
        self.assertEqual(self.client.post(url).status_code, 404)
        self.assertTrue(Review.objects.exists())
        self.login("user")
        self.assertEqual(self.client.post(url).status_code, 302)
        self.assertFalse(Review.objects.exists())

    def test_staff_can_delete_any_review(self):
        review = make_review(self.conf, self.user)
        self.login("staff")
        self.assertEqual(self.client.post(reverse("review-delete", args=[review.pk])).status_code, 302)
        self.assertFalse(Review.objects.exists())
