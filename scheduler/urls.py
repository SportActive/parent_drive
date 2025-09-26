from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('', views.schedule_view, name='schedule'),
    path('events/', views.schedule_events, name='schedule_events'),
    path('toggle-holiday/', views.toggle_holiday, name='toggle_holiday'),
    path('my-schedule/', views.my_schedule_view, name='my_schedule'),
    path('my-schedule/events/', views.unavailability_events, name='unavailability_events'),
    path('my-schedule/update/', views.update_unavailability, name='update_unavailability'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('swap/<int:slot_id>/', views.request_swap, name='request_swap'),
    path('accept_swap/<int:slot_id>/', views.accept_swap, name='accept_swap'),
    path('recalculate/', views.recalculate_schedule_view, name='recalculate_schedule'),
    path('manage-users/', views.manage_users_view, name='manage_users'),
    path('promote/<int:user_id>/', views.promote_to_admin, name='promote_to_admin'),
    path('demote/<int:user_id>/', views.demote_from_admin, name='demote_from_admin'),
]