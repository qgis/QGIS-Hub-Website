from django.core.management.base import BaseCommand
from styles.models import Style

class Command(BaseCommand):
  help = "Migrate existing Style.style_type to Style.style_types (many-to-many)"

  def handle(self, *args, **options):
    migrated = 0
    total = Style.objects.count()
    for style in Style.objects.all():
      if style.style_type:
        # Add the single style_type to the style_types M2M field
        style.style_types.add(style.style_type)
        migrated += 1
    self.stdout.write(self.style.SUCCESS(
      f"Migration complete: {migrated} of {total} Style objects updated."
    ))