from rest_framework import serializers
from .models import ManualTypes, Manuals

class ManualTypesSerializers(serializers.ModelSerializer):
    class Meta:
        model = ManualTypes
        fields = [
            'id',
            'title',
            'level',
            'organization',
            'created_by',
            'is_active',
        ]

class ManualPreDataSerializers(serializers.ModelSerializer):
    class Meta:
        model = ManualTypes
        fields = [
            'id',
            'title',
        ]

class ManualsSerializers(serializers.ModelSerializer):
    manual_type_title = serializers.SerializerMethodField()
    class Meta:
        model = Manuals
        fields = [
            'id',
            'manual_type',
            'manual_type_title',
            'title',
            'document',
            'created_by',
            'is_active',
        ]

    def get_manual_type_title(self, obj):
        try:
            return obj.manual_type.title
        except Exception as e:
            print(str(e))
            return None

class UpdateManualsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Manuals
        fields = [
            'id',
            'title',
            'document',
            'is_active',
        ]

