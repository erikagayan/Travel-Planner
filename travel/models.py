from django.core.exceptions import ValidationError
from django.db import models


class TravelProject(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    start_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def sync_status_from_places(self):
        has_places = self.places.exists()
        if not has_places:
            new_status = self.Status.ACTIVE
        elif self.places.filter(visited=False).exists():
            new_status = self.Status.ACTIVE
        else:
            new_status = self.Status.COMPLETED
        if self.status != new_status:
            type(self).objects.filter(pk=self.pk).update(status=new_status)
            self.status = new_status


class ProjectPlace(models.Model):
    project = models.ForeignKey(
        TravelProject,
        on_delete=models.CASCADE,
        related_name='places',
    )
    external_id = models.CharField(max_length=64, db_index=True)
    title = models.CharField(max_length=512)
    notes = models.TextField(blank=True, null=True)
    visited = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['added_at']
        unique_together = [['project', 'external_id']]

    def __str__(self):
        return f'{self.title} ({self.external_id})'

    def clean(self):
        super().clean()
        if self.project_id is None:
            return
        if self.pk is None and self.project.places.count() >= 10:
            raise ValidationError('Maximum 10 places per project.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
