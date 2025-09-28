from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import DrivingSlot, ParentProfile, Unavailability, Holiday
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count, Q, F
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import datetime
import json
from collections import defaultdict

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if User.objects.count() == 1:
                user.is_staff = True
                user.is_superuser = True
                user.save()
            ParentProfile.objects.create(user=user)
            login(request, user)
            return redirect('schedule')
    else:
        if User.objects.exists() and not request.user.is_staff:
             return redirect('login')
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def schedule_view(request):
    context = { 'is_admin': request.user.is_staff }
    return render(request, 'scheduler/schedule.html', context)

def schedule_events(request):
    events = []
    holidays = Holiday.objects.all()
    for holiday in holidays:
        events.append({ 'title': holiday.name, 'start': holiday.date.strftime('%Y-%m-%d'), 'display': 'background', 'color': '#ff9f89' })
    slots = DrivingSlot.objects.all()
    for slot in slots:
        is_mine = False
        admin_url = reverse('admin:scheduler_drivingslot_change', args=[slot.id])
        if request.user.is_authenticated and slot.driver:
            is_mine = (slot.driver.user == request.user)
        title = f"Водій: {slot.driver}" if slot.driver else "ПОТРІБЕН ВОДІЙ!"
        className = 'other-drive-event'
        if slot.is_swap_requested:
            title = f"ЗАМІНА: {slot.driver}"
            className = 'swap-request-event'
        elif slot.driver is None:
            className = 'unassigned-event'
        elif is_mine:
            className = 'my-drive-event'
        events.append({ 'id': slot.id, 'title': title, 'start': slot.date.strftime('%Y-%m-%d'), 'extendedProps': { 'is_mine': is_mine, 'is_swap_requested': slot.is_swap_requested, 'admin_url': admin_url }, 'className': className })
    return JsonResponse(events, safe=False)

@login_required
def toggle_holiday(request):
    if not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Доступ заборонено.'}, status=403)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date_str = data.get('date')
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            holiday, created = Holiday.objects.get_or_create(date=date_obj, defaults={'name': 'Вихідний'})
            if not created:
                holiday.delete()
                return JsonResponse({'status': 'deleted'})
            else:
                return JsonResponse({'status': 'created'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def my_schedule_view(request):
    return render(request, 'scheduler/my_schedule.html')

@login_required
def unavailability_events(request):
    events = []
    all_periods = Unavailability.objects.all()
    for period in all_periods:
        end_date = period.end_date + datetime.timedelta(days=1)
        is_mine = (period.parent.user == request.user)
        events.append({ 'id': f"unavail_{period.id}", 'title': f"{period.parent}: Зайнятий", 'start': period.start_date.strftime('%Y-%m-%d'), 'end': end_date.strftime('%Y-%m-%d'), 'allDay': True, 'extendedProps': { 'is_mine': is_mine }, 'classNames': ['my-unavailability'] if is_mine else ['other-unavailability'] })
    all_drives = DrivingSlot.objects.filter(driver__isnull=False)
    for drive in all_drives:
        is_mine = (drive.driver.user == request.user)
        title = f"Водій: {drive.driver}"
        className = 'other-drive'
        if drive.is_swap_requested:
            title = f"ЗАМІНА: {drive.driver}"
            className = 'swap-request-event'
        elif is_mine:
            className = 'my-drive'
        events.append({ 'id': f"drive_{drive.id}", 'title': title, 'start': drive.date.strftime('%Y-%m-%d'), 'extendedProps': { 'is_mine': is_mine, 'is_swap_requested': drive.is_swap_requested }, 'classNames': [className] })
    return JsonResponse(events, safe=False)

@login_required
def update_unavailability(request):
    if request.method == 'POST':
        try:
            parent_profile = ParentProfile.objects.get(user=request.user)
            data = json.loads(request.body)
            start_date_str = data.get('start_date')
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            existing_event = Unavailability.objects.filter(parent=parent_profile, start_date__lte=start_date, end_date__gte=start_date).first()
            if existing_event:
                existing_event.delete()
                return JsonResponse({'status': 'deleted'})
            else:
                new_event = Unavailability.objects.create(parent=parent_profile, start_date=start_date, end_date=start_date, reason='Зайнятий')
                if (new_event.start_date - datetime.date.today()).days < 7:
                    conflicting_drives = DrivingSlot.objects.filter(driver=parent_profile, date=new_event.start_date, is_swap_requested=False)
                    for drive in conflicting_drives:
                        drive.is_swap_requested = True
                        drive.save()
                    return JsonResponse({'status': 'created_swap_requested'})
                else:
                    start_recalc_date = new_event.start_date
                    today = datetime.date.today()
                    end_year = today.year
                    if today.month >= 9:
                        end_year += 1
                    end_recalc_date = datetime.date(end_year, 9, 1)
                    DrivingSlot.objects.filter(date__gte=start_recalc_date).delete()
                    all_parents = list(ParentProfile.objects.filter(is_driver=True))
                    holidays = set(Holiday.objects.values_list('date', flat=True))
                    current_date = start_recalc_date
                    while current_date < end_recalc_date:
                        if current_date.weekday() == 4 and current_date not in holidays:
                            unavailable_parents = Unavailability.objects.filter(start_date__lte=current_date, end_date__gte=current_date).values_list('parent_id', flat=True)
                            available_parents = [p for p in all_parents if p.id not in unavailable_parents]
                            if available_parents:
                                parent_counts = ParentProfile.objects.filter(id__in=[p.id for p in available_parents]).annotate(drive_count=Count('drivingslot', filter=Q(drivingslot__date__lt=current_date))).order_by('drive_count')
                                fairest_driver = parent_counts[0]
                                DrivingSlot.objects.create(date=current_date, driver=fairest_driver)
                        current_date += datetime.timedelta(days=1)
                    return JsonResponse({'status': 'created_recalculated'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def accept_swap(request, slot_id):
    if request.method == 'POST':
        try:
            slot = DrivingSlot.objects.get(id=slot_id, is_swap_requested=True)
            new_driver_profile = ParentProfile.objects.get(user=request.user)
            if slot.driver == new_driver_profile:
                return JsonResponse({'status': 'error', 'message': 'Ви не можете прийняти власний запит на заміну.'}, status=400)
            slot.driver = new_driver_profile
            slot.is_swap_requested = False
            slot.save()
            return JsonResponse({'status': 'ok'})
        except (DrivingSlot.DoesNotExist, ParentProfile.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Слот або профіль не знайдено.'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def request_swap(request, slot_id):
    if request.method == 'POST':
        try:
            slot = DrivingSlot.objects.get(id=slot_id)
            if slot.driver and slot.driver.user == request.user:
                slot.is_swap_requested = True
                slot.save()
                return JsonResponse({'status': 'ok'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Доступ заборонено.'}, status=403)
        except DrivingSlot.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Слот не знайдено.'}, status=404)
    return JsonResponse({'status': 'error'}, status=400)

@staff_member_required
def statistics_view(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Створюємо базовий запит
    drives_query = DrivingSlot.objects.filter(driver__isnull=False)

    # Додаємо фільтри за датою, якщо вони є
    if start_date_str:
        drives_query = drives_query.filter(date__gte=start_date_str)
    if end_date_str:
        drives_query = drives_query.filter(date__lte=end_date_str)

    # Рахуємо кількість поїздок для кожного унікального користувача
    stats = drives_query.values(
        'driver__user__first_name', 
        'driver__user__username'
    ).annotate(
        drive_count=Count('id')
    ).order_by('-drive_count')

    # Готуємо дані для відображення
    parent_stats = []
    for stat in stats:
        # Використовуємо first_name, якщо воно є, інакше username
        display_name = stat['driver__user__first_name'] or stat['driver__user__username']
        parent_stats.append({
            'name': display_name,
            'count': stat['drive_count']
        })

    context = {
        'parent_stats': parent_stats,
        'start_date': start_date_str,
        'end_date': end_date_str,
    }
    return render(request, 'scheduler/statistics.html', context)

@staff_member_required
def recalculate_schedule_view(request):
    if request.method == 'POST':
        today = datetime.date.today()
        start_recalculation_date = today + datetime.timedelta(days=7)
        end_year = today.year
        if today.month >= 9:
            end_year += 1
        end_recalculation_date = datetime.date(end_year, 9, 1)
        DrivingSlot.objects.filter(date__gte=start_recalculation_date).delete()
        all_parents = list(ParentProfile.objects.filter(is_driver=True))
        holidays = set(Holiday.objects.values_list('date', flat=True))
        slots_created = 0
        current_date = start_recalculation_date
        while current_date < end_recalculation_date:
            if current_date.weekday() == 4 and current_date not in holidays:
                unavailable_parents = Unavailability.objects.filter(start_date__lte=current_date, end_date__gte=current_date).values_list('parent_id', flat=True)
                available_parents = [p for p in all_parents if p.id not in unavailable_parents]
                if available_parents:
                    parent_counts = ParentProfile.objects.filter(id__in=[p.id for p in available_parents]).annotate(
                        drive_count=Count('drivingslot', filter=Q(drivingslot__date__lt=current_date))
                    ).order_by('drive_count')
                    fairest_driver = parent_counts[0]
                    DrivingSlot.objects.create(date=current_date, driver=fairest_driver)
                    slots_created += 1
            current_date += datetime.timedelta(days=1)
        return JsonResponse({'status': 'ok', 'message': f'Майбутній розклад було успішно перераховано. Створено {slots_created} нових чергувань.'})
    return JsonResponse({'status': 'error'}, status=400)

@staff_member_required
def manage_users_view(request):
    parent_profiles = ParentProfile.objects.exclude(user__is_superuser=True)
    context = { 'parent_profiles': parent_profiles }
    return render(request, 'scheduler/manage_users.html', context)

@staff_member_required
def promote_to_admin(request, user_id):
    if request.method == 'POST':
        try:
            user_to_promote = User.objects.get(id=user_id)
            user_to_promote.is_staff = True
            user_to_promote.save()
        except User.DoesNotExist:
            pass
    return redirect('manage_users')

@staff_member_required
def demote_from_admin(request, user_id):
    if request.method == 'POST':
        try:
            user_to_demote = User.objects.get(id=user_id)
            if not user_to_demote.is_superuser:
                user_to_demote.is_staff = False
                user_to_demote.save()
        except User.DoesNotExist:
            pass
    return redirect('manage_users')