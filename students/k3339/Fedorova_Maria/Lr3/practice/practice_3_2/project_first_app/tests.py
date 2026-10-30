from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Profession, Skill, SkillOfWarrior, Warrior


class PracticeApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.skill = Skill.objects.create(name="Fireball")
        self.profession = Profession.objects.create(
            title="Mage",
            description="Caster",
        )
        self.warrior = Warrior.objects.create(
            race="Elf",
            name="Legolas",
            level=5,
            profession=self.profession,
        )
        SkillOfWarrior.objects.create(
            warrior=self.warrior,
            skill=self.skill,
            level=3,
        )

    def test_warrior_list_and_related_demo(self):
        warriors = self.client.get("/api/warriors/")
        self.assertEqual(warriors.status_code, status.HTTP_200_OK)
        self.assertEqual(len(warriors.data), 1)
        self.assertEqual(warriors.data[0]["skill_links"][0]["skill"]["name"], "Fireball")

        demo = self.client.get("/api/related-demo/")
        self.assertEqual(demo.status_code, status.HTTP_200_OK)
        self.assertIn("Legolas", demo.data["skills_to_warriors"]["Fireball"])
        self.assertIn("Legolas", demo.data["professions_to_warriors"]["Mage"])
