from datetime import date, timedelta

from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APITestCase

from . import models


class ZooApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", verbosity=0)

    def setUp(self):
        self.assertEqual(self.client.get("/api/animals/").status_code, 401)
        credentials = {"username": "lev_test", "password": "Violet-robin-by-the-lake-63"}
        self.assertEqual(self.client.post("/api/auth/users/", credentials).status_code, 201)
        login = self.client.post("/api/auth/token/login/", credentials)
        self.assertEqual(login.status_code, 200, login.data)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + login.data["auth_token"])

    def test_analytics_and_nested_relations(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/api/auth/users/me/").data["username"], "lev_test")
        bird = models.Animal.objects.get(name="Ива")
        departments = self.client.get("/api/departments/").data
        self.assertEqual(len(departments[0]["enclosures"]), 2)
        self.assertEqual(len(self.client.get(f"/api/animals/{bird.id}/").data["employees"]), 2)
        self.assertEqual(len(self.client.get(f"/api/animals/{bird.id}/building-neighbors/").data), 1)
        self.assertEqual(self.client.get("/api/reports/department-counts/").data[0]["animal_count"], 2)
        self.assertEqual(len(self.client.get("/api/reports/shared-enclosures/").data), 2)
        self.assertEqual(len(self.client.get("/api/reports/empty-enclosures/").data), 1)
        self.assertEqual(self.client.get("/api/reports/incoming-leases/").data[0]["animal_count"], 1)
        outgoing = self.client.get("/api/reports/outgoing-leases/").data
        self.assertEqual(outgoing["total"]["animal_count"], 1)
        self.assertEqual(outgoing["total"]["total_cost"], 24000)
        self.assertIn("species", self.client.options("/api/animals/").data["actions"]["POST"])

    def test_seasons_accept_history_and_reject_conflicts(self):
        bird = models.Animal.objects.get(name="Ива")
        reptile = models.Animal.objects.get(name="Лист")
        data = {
            "animal": bird.id, "wintering_code": "TR-02", "wintering_country": "Турция",
            "departure_date": "2026-10-20", "arrival_date": "2027-03-01",
        }
        response = self.client.post("/api/bird-winterings/", data)
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(bird.winterings.count(), 3)
        self.assertEqual(self.client.post("/api/bird-winterings/", data).status_code, 400)
        self.assertEqual(self.client.post("/api/bird-winterings/", {**data, "animal": reptile.id}).status_code, 400)
        response = self.client.post("/api/reptile-hibernations/", {
            "animal": reptile.id, "starts_on": "2026-10-20", "ends_on": None,
        }, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(reptile.hibernations.count(), 3)

    def test_lease_transfer_and_return_update_occupancy(self):
        bird = models.Animal.objects.get(name="Ива")
        enclosure = bird.enclosure
        visitor = models.Zoo.objects.get(is_local=False)
        today = timezone.localdate()
        response = self.client.post("/api/leases/", {
            "animal": bird.id, "lessor": bird.owner_zoo_id, "lessee": visitor.id,
            "starts_on": today.isoformat(), "ends_on": (today + timedelta(days=5)).isoformat(),
            "total_cost": "1000.00",
        })
        self.assertEqual(response.status_code, 201, response.data)
        endpoint = f"/api/leases/{response.data['id']}/"
        self.assertEqual(self.client.post(endpoint + "transfer/").status_code, 200)
        bird.refresh_from_db()
        self.assertIsNone(bird.enclosure_id)
        self.assertEqual(self.client.post(endpoint + "return/", {"enclosure": enclosure.id}).status_code, 200)
        bird.refresh_from_db()
        self.assertEqual(bird.enclosure_id, enclosure.id)

    def test_practice_endpoints(self):
        response = self.client.post("/api/practice/skills/", {"title": "Тестирование"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.client.get("/api/practice/skills/").data), 2)
        self.assertEqual(self.client.get("/api/practice/warriors/professions/").data[0]["profession"]["title"], "Разработчик")
        warrior = self.client.get("/api/practice/warriors/skills/").data[0]
        self.assertEqual(warrior["skills"][0]["level"], 3)
        url = f"/api/practice/warriors/{warrior['id']}/"
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.client.patch(url, {"level": 9}).data["level"], 9)
        self.assertEqual(self.client.delete(url).status_code, 204)
