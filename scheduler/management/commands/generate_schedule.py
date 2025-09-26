from django.core.management.base import BaseCommand
from scheduler.models import ParentProfile, DrivingSlot, Unavailability, Holiday
from django.db.models import Count, Q
import datetime
from calendar import monthrange

class Command(BaseCommand):
    help = 'Intelligently updates or creates a schedule for the next month.'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete the schedule for the target month before generating a new one.')

    def handle(self, *args, **options):
        today = datetime.date.today()
        if today.month == 12:
            target_year, target_month = today.year + 1, 1
        else:
            target_year, target_month = today.year, today.month + 1
        
        if options['reset']:
            DrivingSlot.objects.filter(date__year=target_year, date__month=target_month).delete()

        start_of_month = datetime.date(target_year, target_month, 1)
        num_days = monthrange(target_year, target_month)[1]
        holidays_in_month = set(Holiday.objects.filter(date__year=target_year, date__month=target_month).values_list('date', flat=True))
        
        all_parents = list(ParentProfile.objects.filter(is_driver=True))

        if not all_parents:
            self.stdout.write(self.style.ERROR('Не знайдено батьків-водіїв у базі даних.'))
            return

        self.stdout.write(f"Оновлення розкладу для {start_of_month.strftime('%B %Y')}...")

        for day in range(1, num_days + 1):
            current_date = datetime.date(target_year, target_month, day)
            if current_date in holidays_in_month or current_date.weekday() != 4:
                continue

            existing_slot = DrivingSlot.objects.filter(date=current_date).first()
            if existing_slot and existing_slot.driver and not existing_slot.is_swap_requested:
                continue

            unavailable_parents = Unavailability.objects.filter(start_date__lte=current_date, end_date__gte=current_date).values_list('parent_id', flat=True)
            available_parents = [p for p in all_parents if p.id not in unavailable_parents]

            if not available_parents:
                self.stdout.write(self.style.WARNING(f"  ! Не вдалося знайти вільного водія для {current_date}"))
                continue

            parent_counts = ParentProfile.objects.filter(id__in=[p.id for p in available_parents]).annotate(
                drive_count=Count('drivingslot', filter=Q(drivingslot__date__lt=current_date))
            ).order_by('drive_count')
            
            fairest_driver = parent_counts[0]
            
            slot, _ = DrivingSlot.objects.get_or_create(date=current_date)
            slot.driver = fairest_driver
            slot.is_swap_requested = False
            slot.save()
            self.stdout.write(self.style.SUCCESS(f"  > Призначено {fairest_driver} на {current_date} (Всього поїздок: {fairest_driver.drive_count})"))

        self.stdout.write(self.style.SUCCESS('\nОновлення розкладу завершено.'))