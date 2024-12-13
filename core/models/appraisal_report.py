# core/models/appraisal_report.py
from mongoengine import Document, StringField, DateTimeField, ReferenceField, DecimalField
from datetime import datetime

class AppraisalReport(Document):
    appraisal_request = ReferenceField('AppraisalRequest', required=True)
    appraiser = ReferenceField('UserProfile', required=True)
    report_date = DateTimeField(default=datetime.now)
    value = DecimalField(precision=2)
    status = StringField(
        choices=['draft', 'review', 'complete', 'archived'],
        default='draft'
    )
    methodology = StringField()
    comments = StringField()
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    meta = {
        'collection': 'appraisal_reports',
        'indexes': [
            'appraisal_request',
            'appraiser',
            'status',
            'created_at'
        ]
    }

    def __str__(self):
        return f"Report {self.id} - {self.status}"