from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} (score: {self.score})"


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # profile might not exist yet for users created before this code existed
        Profile.objects.get_or_create(user=instance)


class Activity(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    week_date = models.DateField()
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    max_participants = models.PositiveIntegerField(default=4)
    points = models.PositiveIntegerField(default=0)
    is_hidden = models.BooleanField(default=False)
    is_marked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['week_date', 'name']

    def __str__(self):
        return f"{self.name} ({self.week_date})"

    @property
    def spots_taken(self):
        return self.enrollments.count()

    @property
    def spots_left(self):
        return max(self.max_participants - self.spots_taken, 0)

    @property
    def is_full(self):
        return self.spots_taken >= self.max_participants


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    final_score = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'activity')  # can't enroll twice in the same activity
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.user.username} -> {self.activity.name}"
