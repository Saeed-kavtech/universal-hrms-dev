from rest_framework import serializers
from .models import *


class ScaleGroupsSerializers(serializers.ModelSerializer):
    class Meta:
        model = ScaleGroups
        fields = [
            'id',
            'title',
            'organization',
            'created_by',
            'have_aspects',
            'is_default_group',
            'created_at',
            'updated_at',
            'is_active',
        ]

    

class ScaleRatingSerializers(serializers.ModelSerializer):
  
    class Meta:
        model = ScaleRating
        fields = [
            'id',
            'title',
            'organization',
            'level',
            'created_by',
            'created_at',
            'updated_at',
            'is_active',
        ]

class GroupAspectsSerializers(serializers.ModelSerializer):
    scale_group_title=serializers.SerializerMethodField()
    class Meta:
        model = GroupAspects
        fields = [
            'id',
            'title',
            'scale_group',
            'scale_group_title',
            'created_by',
            'created_at',
            'updated_at',
            'is_active',
        ]

    def get_scale_group_title(self, obj):
            try:
                
                return obj.scale_group.title
            except Exception as e:
                print(str(e))
                return None

class AspectsParametersSerializers(serializers.ModelSerializer):
    aspect_group_title=serializers.SerializerMethodField()
  
    class Meta:
        model = AspectsParameters
        fields = [
            'id',
            'title',
            'aspects',
            'aspect_group_title',
            'created_by',
            'is_required',
            'created_at',
            'updated_at',
            'is_active',
        ]
   
    def get_aspect_group_title(self, obj):
            try:
                
                return obj.aspects.title
            except Exception as e:
                print(str(e))
                return None



class ListScaleGroupSerializers(serializers.ModelSerializer):
    group_aspects=serializers.SerializerMethodField()
    aspects_count=serializers.SerializerMethodField()
    parameters_count=serializers.SerializerMethodField()
    class Meta:
        model = ScaleGroups
        fields = [
            'id',
            'title',
            'organization',
            'created_by',
            'created_at',
            'updated_at',
            'is_active',
            'aspects_count',
            'parameters_count',
            'group_aspects',
        ]

    def get_group_aspects(self, obj):
            try:
                # print(obj.id)
                query = GroupAspects.objects.filter(scale_group=obj.id, is_active=True)
                # print(query.values())
                serializers = ListGroupAspectsSerializers(query, many=True)
                return serializers.data
            except Exception as e:
                print(str(e))
                return None
            
    def get_aspects_count(self, obj):
            try:
                query = GroupAspects.objects.filter(scale_group=obj.id, is_active=True)
                aspects_count=0
                aspects_count=len(query)
               
                return aspects_count
            except Exception as e:
                print(str(e))
                return None
            
    def get_parameters_count(self, obj):
            try:
                query = GroupAspects.objects.filter(scale_group=obj.id, is_active=True)
                parameters_count=0

                for aspect in query:
                    query1 = AspectsParameters.objects.filter(aspects=aspect.id, is_active=True)
                    parameters_count +=len(query1)

                
               
                return parameters_count
            except Exception as e:
                print(str(e))
                return None
            
class ListGroupAspectsSerializers(serializers.ModelSerializer):
    aspect_parameters=serializers.SerializerMethodField()
    parameters_count=serializers.SerializerMethodField()
    class Meta:
        model = GroupAspects
        fields = [
            'id',
            'title',
            'scale_group',
            'created_by',
            'created_at',
            'updated_at',
            'is_active',
            'parameters_count',
            'aspect_parameters'
        ]

    def get_aspect_parameters(self, obj):
            try:
                # print(obj.id)
                query = AspectsParameters.objects.filter(aspects=obj.id, is_active=True)
                # print(query.values())
                serializers = AspectsParametersSerializers(query, many=True)
                return serializers.data
            except Exception as e:
                print(str(e))
                return None
    
    def get_parameters_count(self, obj):
            try:
                query = AspectsParameters.objects.filter(aspects=obj.id, is_active=True)
                parameters_count=0
                parameters_count=len(query)
                return parameters_count
            except Exception as e:
                print(str(e))
                return None