# core/models/appraisal_report.py
from mongoengine import Document, StringField, DateTimeField, ReferenceField, FloatField
from datetime import datetime

class AppraisalReport(Document):
    appraisal_request = ReferenceField('AppraisalRequest', required=True)
    property_value = FloatField(required=True)
    report_date = DateTimeField(default=datetime.now)
    status = StringField(
        choices=['draft', 'submitted', 'approved', 'rejected'],
        default='draft'
    )
    comments = StringField()
    appraiser_notes = StringField()

    meta = {
        'collection': 'appraisal_reports',
        'indexes': ['appraisal_request', 'report_date']
    }