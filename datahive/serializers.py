from rest_framework import serializers

from employees.models import Employees
from .models import Categories, Tags, Documents

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['id','name','organization','created_by', 'is_active', 'created_at', 'updated_at']

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id','title','organization','created_by', 'is_active', 'created_at', 'updated_at']

class DocumentsSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    category_title=serializers.SerializerMethodField()
    created_by_profile_image=serializers.SerializerMethodField()
    created_by_name=serializers.SerializerMethodField()
    class Meta:
        model = Documents
        fields = ['id', 'title', 'description','project', 'file','organization', 'is_public', 'tags','category','category_title', 'created_by','created_by_name','created_by_profile_image', 'is_active', 'created_at', 'updated_at']
    

    def get_category_title(self,obj):
        try:
            if obj.category:
                return obj.category.title
            return None
        except Exception as e:
            return None
        
    def get_tags(self, obj):
        # Filter tags where is_active=True
        active_tags = obj.tags.filter(is_active=True)
        return TagsSerializer(active_tags, many=True).data
    
    def get_created_by_profile_image(self, obj):
        try:
            employee = Employees.objects.filter(hrmsuser=obj.created_by.id, is_active=True).first()
            if employee and employee.profile_image:
                return employee.profile_image.url
            return None
        except Exception as e:
            print(str(e))
            return None 
        
    def get_created_by_name(self,obj):
        try:
            if obj.created_by:
                return obj.created_by.first_name+' '+obj.created_by.last_name
            return None
        except Exception as e:
            return None    
        
        

