from django.db import models
from django.contrib.auth.models import User

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Child(models.Model):
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name} (дитина {self.parent})"

class DrivingSlot(models.Model):
    date = models.DateField()
    driver = models.ForeignKey(ParentProfile, on_delete=models.SET_NULL, null=True, blank=True)
    is_swap_requested = models.BooleanField(default=False)
    class Meta:
        ordering = ['date']
    def __str__(self):
        driver_name = self.driver.user.get_full_name() if self.driver else "Водія не призначено"
        return f"{self.date.strftime('%d.%m.%Y')} - {driver_name}"

class Unavailability(models.Model):
    parent = models.ForeignKey(ParentProfile, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return f"{self.parent} unavailable from {self.start_date} to {self.end_date}"

class Holiday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=255)
    class Meta:
        ordering = ['date']
    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')}: {self.name}"