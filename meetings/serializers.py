from rest_framework import serializers
from .models import InternalMeetingParticipant, ExternalMeetingParticipant, Meetings, MeetingCategory

class MeetingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingCategory
        fields = '__all__'

class MeetingSerializer(serializers.ModelSerializer):
    meeting_category_name  = serializers.SerializerMethodField()
    meeting_medium_name = serializers.SerializerMethodField()
    class Meta:
        model = Meetings
        fields = [
            'id',
            'meeting_id',
            'meeting_uuid',
            "meeting_type",
            "organization",
            'host_id',
            'topic',
            'start_time',
            'date',
            'duration',
            "timezone",
            'status',
            'join_url',
            "start_url",
            'password',
            'meeting_medium',
            'meeting_category',
            'meeting_medium_name',
            'meeting_category_name',
            'is_active',
            'created_at',
            'updated_at'
        ]
    def get_meeting_category_name(self,obj):
        try:
            return obj.meeting_category.title
        except Exception as e:
            return None
    def get_meeting_medium_name(self,obj):
        try:
            return obj.meeting_medium.title
        except Exception as e:
            return None


class InternalMeetingParticipantSerializer(serializers.ModelSerializer):
    name=serializers.SerializerMethodField()
    meeting_id=serializers.SerializerMethodField()
    official_email=serializers.SerializerMethodField()
    class Meta:
        model = InternalMeetingParticipant
        fields = [
            'id',
            'hrms_user',
            'name',  # Reference to the employee object
            'official_email',
            'meeting',
            'meeting_id',
            'is_active',  # Whether the participant is active
            'is_host',
            'created_at',  # Timestamp for when the record was created
            'updated_at',  # Timestamp for when the record was last updated
        ]

    def get_name(self,obj):
        try:
            return obj.hrms_user.first_name+" "+obj.hrms_user.last_name
        except Exception as e:
            return None
        
    def get_official_email(self,obj):
        try:
            return obj.hrms_user.email
        except Exception as e:
            return None

        
    def get_meeting_id(self,obj):
        try:
            return obj.meeting.meeting_id
        except Exception as e:
            return None


class ExternalMeetingParticipantSerializer(serializers.ModelSerializer):
    meeting_id=serializers.SerializerMethodField()
    class Meta:
        model = ExternalMeetingParticipant
        fields = [
            'id',
            'meeting',  # Identifier for the meeting
            'meeting_id',
            'name',  # Name of the external participant
            'email',  # Email of the external participant
            'is_host',
            'is_active',  # Whether the participant is active
            'created_at',  # Timestamp for when the record was created
            'updated_at',  # Timestamp for when the record was last updated
        ]

    def get_meeting_id(self,obj):
        try:
            return obj.meeting.meeting_id
        except Exception as e:
            return None


class ListMeetingSerializer(serializers.ModelSerializer):
    meeting_id=serializers.SerializerMethodField()
    join_url=serializers.SerializerMethodField()
    start_url=serializers.SerializerMethodField()
    topic=serializers.SerializerMethodField()
    date=serializers.SerializerMethodField()
    start_time=serializers.SerializerMethodField()
    status=serializers.SerializerMethodField()
    password=serializers.SerializerMethodField()
    meeting_medium_title = serializers.SerializerMethodField()
    class Meta:
        model = InternalMeetingParticipant
        fields = [
            'id',
            'hrms_user',  # Reference to the employee object
            'meeting',
            'meeting_id',
            'meeting_medium_title',
            'status',
            'password',
            "topic",
            'start_time',
            "date",
            "join_url",
            'start_url',
            'is_active',  # Whether the participant is active
            'is_host',
            'created_at',  # Timestamp for when the record was created
            'updated_at',  # Timestamp for when the record was last updated
        ]

    def get_meeting_id(self,obj):
        try:
            return obj.meeting.meeting_id
        except Exception as e:
            return None
    def get_meeting_medium_title(self,obj):
        try:
            return obj.meeting.meeting_medium.title
        except Exception as e:
            return None
        
    def get_topic(self,obj):
        try:
            return obj.meeting.topic
        except Exception as e:
            return None
        
    def get_start_time(self,obj):
        try:
            return obj.meeting.start_time
        except Exception as e:
            return None
        
    def get_date(self,obj):
        try:
            return obj.meeting.date
        except Exception as e:
            return None
        
    def get_join_url(self,obj):
        try:
            return obj.meeting.join_url
        except Exception as e:
            return None
        
    def get_start_url(self,obj):
        try:
            if obj.is_host==True:
              return obj.meeting.start_url
        except Exception as e:
            return None
        
    def get_password(self,obj):
        try:
            return obj.meeting.password
        except Exception as e:
            return None
        

    def get_status(self,obj):
        try:
              return obj.meeting.status
        except Exception as e:
            return None