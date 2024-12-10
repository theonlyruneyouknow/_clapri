from mongoengine import Document, ReferenceField, DateTimeField, StringField, BooleanField
from datetime import datetime

class Appointment(Document):
    appraisal_request = ReferenceField('AppraisalRequest', required=True)
    scheduled_date = DateTimeField(required=True)
    status = StringField(choices=['scheduled', 'completed', 'cancelled', 'rescheduled'], default='scheduled')
    notes = StringField()
    confirmation_sent = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'appointments',
        'ordering': ['-scheduled_date'],
        'indexes': [
            'appraisal_request',
            'scheduled_date',
            'status'
        ]
    }

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(Appointment, self).save(*args, **kwargs)

    def reschedule(self, new_date):
        old_date = self.scheduled_date
        self.scheduled_date = new_date
        self.status = 'rescheduled'
        self.save()
        return old_date
