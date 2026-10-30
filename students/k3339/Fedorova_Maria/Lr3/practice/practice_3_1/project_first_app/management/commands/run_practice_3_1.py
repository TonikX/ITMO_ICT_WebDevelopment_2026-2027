from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed car domain and run Practice 3.1 ORM queries"

    def handle(self, *args, **options):
        script = Path(__file__).resolve().parents[2] / "orm_queries.py"
        code = script.read_text(encoding="utf-8")
        exec(compile(code, str(script), "exec"), {"__name__": "__main__"})
        self.stdout.write(self.style.SUCCESS("Practice 3.1 queries finished."))
