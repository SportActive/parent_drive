from django.core.management.base import BaseCommand
from scheduler.models import ParentProfile
import random

def get_random_color():
    # Генерує приємний, не надто темний випадковий колір
    return f"#{random.randint(50, 200):02x}{random.randint(50, 200):02x}{random.randint(50, 200):02x}"

class Command(BaseCommand):
    help = 'Assigns a random color to any parent profiles that do not have one.'

    def handle(self, *args, **options):
        # Знаходимо всіх батьків, у яких колір встановлено за замовчуванням
        parents_without_color = ParentProfile.objects.filter(color="#007BFF")
        
        if not parents_without_color.exists():
            self.stdout.write(self.style.SUCCESS('All parents already have a unique color.'))
            return

        updated_count = 0
        for parent in parents_without_color:
            parent.color = get_random_color()
            parent.save()
            updated_count += 1
            self.stdout.write(f'Assigned new color to {parent}')

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} parent profiles.'))