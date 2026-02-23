from rest_framework import serializers
from .models import CourseApplicantCustomEmails


class CourseApplicantCustomEmailsSerializers(serializers.ModelSerializer):
    class Meta:
        model = CourseApplicantCustomEmails
        fields = [
            'id',
            'course_applicant',
            'subject',
            'body',
            'footer',
            'is_trainee',
            'attachment',
            'action_by',
            'is_active',
        ]



