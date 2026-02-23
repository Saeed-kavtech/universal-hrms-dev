from rest_framework import serializers
from .models import KindNotes
from employees.models import Employees

class KindNotesViewsetSerializers(serializers.ModelSerializer):
    notes = serializers.CharField(max_length=None)
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    class Meta:
        model = KindNotes
        fields = [
            'id',
            'sender',
            'sender_name',
            'receiver',
            'receiver_name',
            'notes',
            'is_active', 
            'created_at',
        ]
        

    def get_sender_name(self, obj):
        try:
            return obj.sender.name
        except Exception as e:
            print(str(e))
            return None
        

    def get_receiver_name(self, obj):
        try:
            return obj.receiver.name
        except Exception as e:
            print(str(e))
            return None
        
    def validate_notes(self, notes):
        if len(notes) > 300:
            raise serializers.ValidationError("length cannot be greater than 300 characters")
        return notes


class kindNotesPreDataViewSerializers(serializers.ModelSerializer):
    class Meta:
        model = Employees
        fields = [
            'id',
            'name',
            'emp_code',
            'official_email'
        ]