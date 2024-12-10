# core/models/time_slot.py
from django.db import models

class TimeSlot(models.Model):
    SLOT_CHOICES = [
        ('morning', 'Morning (9:00 AM - 12:00 PM)'),
        ('afternoon', 'Afternoon (1:00 PM - 4:00 PM)'),
        ('evening', 'Evening (5:00 PM - 7:00 PM)')
    ]

    slot = models.CharField(
        max_length=20,
        choices=SLOT_CHOICES,
        default='morning'
    )
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.get_slot_display()

    class Meta:
        db_table = 'time_slots'