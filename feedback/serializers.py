# from django.forms import ValidationError
# from django.utils import timezone
# import jwt
# from requests import request
# from rest_framework import serializers
# from .models import Feedback, MonthlyFeedbackSummary, WeeklyFeedbackSummary, UserScore
# from employees.models import Employees
# from projects.models import Projects
# from profiles_api.models import HrmsUsers
# from .services.sentiment_analyzer import SentimentAnalyzer
# from .permissions import FeedbackPermissions, UserScorePermissions
# import json
# import os

# class FeedbackSerializer(serializers.ModelSerializer):
#     sender_name = serializers.SerializerMethodField()
#     receiver_name = serializers.SerializerMethodField()
#     categories_display = serializers.SerializerMethodField()
#     project_name = serializers.SerializerMethodField()
#     sender_details = serializers.SerializerMethodField()
#     sender_organization_id = serializers.SerializerMethodField()
#     receiver_organization_id = serializers.SerializerMethodField()
#     project_organization_id = serializers.SerializerMethodField()
#     project = serializers.PrimaryKeyRelatedField(
#         queryset=Projects.objects.all(), 
#         required=False, 
#         allow_null=True
#     )

#     class Meta:
#         model = Feedback
#         fields = [
#             'id',
#             'sender',
#             'sender_name',
#             'sender_details',
#             'sender_organization_id',
#             'receiver',
#             'receiver_name',
#             'receiver_organization_id',
#             'project',
#             'project_name',
#             'project_organization_id',
#             'message',
#             'rating',
#             'categories',  
#             'categories_display',  
#             'sentiment_label',
#             'sentiment_score',
#             'sentiment_raw',
#             'sentiment_spans',  
#             'category',
#             'tone',
#             'strengths',
#             'improvement_areas',
#             'suggested_action',
#             'impact_level',
#             'created_at',
#             'updated_at',
#         ]
#         read_only_fields = [
#             'sentiment_label',
#             'sentiment_score',
#             'sentiment_raw',
#             'sentiment_spans',  
#             'category',
#             'tone',
#             'strengths',
#             'improvement_areas',
#             'suggested_action',
#             'impact_level',
#             'created_at',
#             'updated_at',
#             'categories_display',
#             'project_name',
#             'sender_details',
#             'sender_organization_id',
#             'receiver_organization_id',
#             'project_organization_id',
#         ]

#     def _get_user_name(self, user):
#         """Helper method to get user name safely"""
#         if not user:
#             return None
#         if hasattr(user, 'email'):  
#             name = f"{user.first_name} {user.last_name}".strip()
#             return name or user.email
#         elif hasattr(user, 'name'):  
#             return user.name
#         return None

#     def get_sender_name(self, obj):
#         """Get sender name - works for both HrmsUsers and Employees"""
#         return self._get_user_name(obj.sender)

#     def get_sender_details(self, obj):
#         """Get sender details - works for both HrmsUsers and Employees"""
#         try:
#             sender = obj.sender
#             if hasattr(sender, 'email'):  
#                 return {
#                     'id': sender.id,
#                     'email': sender.email,
#                     'first_name': sender.first_name,
#                     'last_name': sender.last_name,
#                     'is_admin': sender.is_admin,
#                     'user_type': 'hrms_user'
#                 }
#             elif hasattr(sender, 'emp_code'):  
#                 return {
#                     'id': sender.id,
#                     'emp_code': sender.emp_code,
#                     'name': sender.name,
#                     'user_type': 'employee'
#                 }
#         except Exception:
#             return None

#     def _get_organization_id(self, obj_or_field):
#         """Helper method to get organization ID safely"""
#         try:
#             if hasattr(obj_or_field, 'organization_id'):
#                 return obj_or_field.organization_id
#         except Exception:
#             pass
#         return None

#     def get_sender_organization_id(self, obj):
#         """Get sender's organization ID"""
#         return self._get_organization_id(obj.sender)

#     def get_receiver_organization_id(self, obj):
#         """Get receiver's organization ID"""
#         return self._get_organization_id(obj.receiver)

#     def get_project_organization_id(self, obj):
#         """Get project's organization ID"""
#         return self._get_organization_id(obj.project) if obj.project else None

#     def get_receiver_name(self, obj):
#         """Get receiver name"""
#         try:
#             return obj.receiver.name
#         except Exception:
#             return None

#     def get_categories_display(self, obj):
#         """Returns human-readable category names"""
#         return obj.get_categories_display()
    
#     def get_project_name(self, obj):
#         """Returns project name if exists"""
#         return obj.project.name if obj.project else None
        
#     def validate_message(self, message):
#         if len(message) > 500:
#             raise serializers.ValidationError("Message cannot exceed 500 characters.")
#         return message

#     def validate_rating(self, rating):
#         if rating < 0 or rating > 5:
#             raise serializers.ValidationError("Rating must be between 0 and 5.")
#         return rating

#     def validate_categories(self, categories):
#         """Validate that categories are from the allowed choices"""
#         if categories:
#             if not isinstance(categories, list):
#                 raise serializers.ValidationError("Categories must be a list.")
            
#             valid_categories = [choice[0] for choice in Feedback.FEEDBACK_CATEGORY_CHOICES]
#             invalid_categories = [cat for cat in categories if cat not in valid_categories]
            
#             if invalid_categories:
#                 raise serializers.ValidationError(
#                     f"Invalid categories: {invalid_categories}. "
#                     f"Must be from: {valid_categories}"
#                 )
#         return categories
    
#     def validate(self, data):
#         """
#         Add role-based validation with organization filtering
#         """
#         request = self.context.get('request')
#         if not request or not hasattr(request, 'user'):
#             return data
        
#         sender_user = request.user
        
#         sender = data.get('sender')
#         if not sender:
#             try:
#                 sender = Employees.objects.get(hrmsuser=sender_user)
#             except Employees.DoesNotExist:
#                 sender = sender_user
#             data['sender'] = sender
        
#         receiver_employee = data.get('receiver')
#         if not receiver_employee:
#             raise serializers.ValidationError({
#                 "receiver": "Receiver is required"
#             })
#         project = data.get('project')
        
#         # Get sender organization using the correct method
#         sender_org_id = FeedbackPermissions.get_user_organization(request)  # FIXED: pass request
        
#         if sender_org_id:
#             if hasattr(receiver_employee, 'organization_id'):
#                 if receiver_employee.organization_id != sender_org_id:
#                     raise serializers.ValidationError({
#                         "receiver": f"Employee belongs to different organization (Org ID: {receiver_employee.organization_id})"
#                     })
#             if project and hasattr(project, 'organization_id'):
#                 if project.organization_id != sender_org_id:
#                     raise serializers.ValidationError({
#                         "project": f"Project belongs to different organization (Org ID: {project.organization_id})"
#                     })
        
#         # Check permission with organization filtering
#         project_id = project.id if project else None
        
#         # FIXED: Pass request object, not sender_user
#         try:
#             can_assign, reason, allowed_projects = FeedbackPermissions.can_assign_feedback(
#                 request, receiver_employee, project_id  # FIXED: pass request
#             )
#         except AttributeError as ae:
#             # Handle the 'user' attribute error
#             if "'HrmsUsers' object has no attribute 'user'" in str(ae):
#                 # Fallback to simpler permission check
#                 from profiles_api.models import HrmsUsers
#                 try:
#                     hrms_user = HrmsUsers.objects.get(id=sender_user.id)
#                     if not getattr(hrms_user, 'is_admin', False):
#                         # For non-admins, do basic organization check
#                         if sender_org_id and hasattr(receiver_employee, 'organization_id'):
#                             if receiver_employee.organization_id != sender_org_id:
#                                 raise serializers.ValidationError({
#                                     "receiver": "Cannot assign feedback to employee in different organization"
#                                 })
#                         can_assign = True
#                         reason = "Basic permission check"
#                         allowed_projects = []
#                     else:
#                         can_assign = True
#                         reason = "Admin permission"
#                         allowed_projects = []
#                 except Exception:
#                     raise serializers.ValidationError({
#                         "project": "Permission check failed"
#                     })
#             else:
#                 raise serializers.ValidationError({
#                     "project": f"Permission check error: {str(ae)}"
#                 })
        
#         if not can_assign:
#             error_msg = f"Cannot assign feedback: {reason}"
#             raise serializers.ValidationError({
#                 "project": [error_msg]
#             })
        
#         # Verify project is in allowed list (only if project exists)
#         if project and project.id not in allowed_projects:
#             raise serializers.ValidationError({
#                 "project": f"Project '{project.name}' is not in allowed projects list"
#             })
        
#         return data

#     def create(self, validated_data):
#         """
#         Override create to ensure sender is set from request user and run sentiment analysis
#         """
#         request = self.context.get('request')
#         if request and hasattr(request, 'user'):
#             sender_user = request.user
            
#             # Ensure sender is current user
#             if 'sender' not in validated_data:
#                 try:
#                     validated_data['sender'] = Employees.objects.get(hrmsuser=sender_user)
#                 except Employees.DoesNotExist:
#                     validated_data['sender'] = sender_user
            
#             # Organization validation - use request-based method
#             sender_org_id = FeedbackPermissions.get_user_organization(request)  # FIXED: pass request
#             receiver_employee = validated_data.get('receiver')
#             project = validated_data.get('project')
            
#             if sender_org_id:
#                 # Verify receiver organization
#                 if (hasattr(receiver_employee, 'organization_id') and 
#                     receiver_employee.organization_id != sender_org_id):
#                     raise serializers.ValidationError({
#                         "receiver": "Cannot assign feedback to employee in different organization"
#                     })
                
#                 # Verify project organization (only if project exists)
#                 if (project and hasattr(project, 'organization_id') and 
#                     project.organization_id != sender_org_id):
#                     raise serializers.ValidationError({
#                         "project": "Cannot assign feedback for project in different organization"
#                     })
        
#         # Run sentiment analysis
#         message = validated_data.get("message", "")
#         user_category = validated_data.get('category')
#         analyzer = SentimentAnalyzer()
#         sentiment_result = analyzer.analyze_text(message)
        
#         # Update validated_data with sentiment analysis results
#         sentiment_fields = {
#             "sentiment_label": sentiment_result.get("label", "neutral"),
#             "sentiment_score": sentiment_result.get("score", 0.5),
#             "sentiment_raw": sentiment_result,
#             "category": user_category,
#             "tone": sentiment_result.get("tone"),
#             "strengths": sentiment_result.get("strengths"),
#             "improvement_areas": sentiment_result.get("improvement_areas"),
#             "suggested_action": sentiment_result.get("suggested_action"),
#             "impact_level": sentiment_result.get("impact_level")
#         }
        
#         validated_data.update(sentiment_fields)
#         return super().create(validated_data)

#     def update(self, instance, validated_data):
#         message = validated_data.get("message", instance.message)
#         user_category = validated_data.get('category')
        
#         if 'categories' in validated_data:
#             instance.categories = validated_data['categories']

#         if message != instance.message or 'categories' in validated_data:
#             analyzer = SentimentAnalyzer()
#             sentiment_result = analyzer.analyze_text(message)
            
#             instance.sentiment_label = sentiment_result.get("label", "neutral")
#             instance.sentiment_score = sentiment_result.get("score", 0.5)
#             instance.sentiment_raw = sentiment_result
#             if user_category is not None:
#                 instance.category = user_category
                
#             instance.tone = sentiment_result.get("tone", "Formal")
#             instance.strengths = sentiment_result.get("strengths", "")
#             instance.improvement_areas = sentiment_result.get("improvement_areas", "")
#             instance.suggested_action = sentiment_result.get("suggested_action", "")
#             instance.impact_level = sentiment_result.get("impact_level", "Medium")
#             instance.rating = validated_data.get("rating", instance.rating)
#             instance.message = message
            
#             # Update project if provided (optional)
#             if 'project' in validated_data:
#                 instance.project = validated_data['project']
            
#             instance.save()
#         else:
#             # Update only provided fields
#             if 'rating' in validated_data:
#                 instance.rating = validated_data['rating']
            
#             if user_category is not None:
#                 instance.category = user_category
            
#             if 'project' in validated_data:
#                 instance.project = validated_data['project']
            
#             instance.save()
        
#         return instance

# class FeedbackPreDataSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Employees
#         fields = ['id', 'name', 'emp_code', 'official_email']

# class WeeklySummarySerializer(serializers.ModelSerializer):
#     week_range = serializers.SerializerMethodField()
#     week_label = serializers.SerializerMethodField()
#     feedback_report = serializers.SerializerMethodField()  
    
#     class Meta:
#         model = WeeklyFeedbackSummary
#         fields = [
#             'id',
#             'week_start_date',
#             'week_end_date', 
#             'week_range',
#             'week_label',
#             'total_feedbacks',
#             'average_rating',
#             'category_distribution',
#             'sentiment_distribution',
#             'daily_rating_trends',
#             'employee_id',
#             'employee_name',
#             'feedback_report', 
#             'strengths',        
#             'improvement_areas',
#             'created_at'
#         ]
    
#     def get_week_range(self, obj):
#         return f"{obj.week_start_date} to {obj.week_end_date}"
    
#     def get_week_label(self, obj):
#         return f"Week of {obj.week_start_date.strftime('%b %d')}"
    
#     def get_feedback_report(self, obj):
#         """Safely get feedback report as JSON"""
#         return obj.get_feedback_report()
    
#     def to_representation(self, instance):
#         """Ensure all JSON fields are properly serialized"""
#         data = super().to_representation(instance)
        
#         # Safely handle all JSON fields
#         json_fields = [
#             'category_distribution',
#             'sentiment_distribution',
#             'daily_rating_trends',
#             'strengths',
#             'improvement_areas'
#         ]
        
#         for field in json_fields:
#             value = getattr(instance, field)
#             if isinstance(value, str):
#                 try:
#                     data[field] = json.loads(value)
#                 except (json.JSONDecodeError, TypeError, ValueError):
#                     if field in ['category_distribution', 'sentiment_distribution']:
#                         data[field] = {}
#                     elif field in ['daily_rating_trends', 'strengths', 'improvement_areas']:
#                         data[field] = []
#             elif value is None:
#                 if field in ['category_distribution', 'sentiment_distribution']:
#                     data[field] = {}
#                 elif field in ['daily_rating_trends', 'strengths', 'improvement_areas']:
#                     data[field] = []
        
#         return data

# class WeeklySummaryDetailSerializer(WeeklySummarySerializer):
#     """Extended serializer for detailed view with formatted feedback report"""
#     formatted_report = serializers.SerializerMethodField()
    
#     class Meta(WeeklySummarySerializer.Meta):
#         fields = WeeklySummarySerializer.Meta.fields + ['formatted_report']
    
#     def get_formatted_report(self, obj):
#         """Get the formatted feedback report with fallback structure"""
#         return obj.formatted_feedback_report


# class MonthlyFeedbackSummarySerializer(serializers.ModelSerializer):
#     month_label = serializers.SerializerMethodField()
#     month_value = serializers.SerializerMethodField()
#     trend_icon = serializers.SerializerMethodField()
    
#     class Meta:
#         model = MonthlyFeedbackSummary
#         fields = [
#             'id',
#             'month_start_date',
#             'month_end_date',
#             'month_label',
#             'month_value',
#             'employee_id',
#             'employee_name',
#             'feedback_count',
#             'average_rating',
#             'previous_month_rating',
#             'trend',
#             'trend_icon',
#             'category_breakdown',
#             'sentiment_breakdown',
#             'created_at'
#         ]
    
#     def get_month_label(self, obj):
#         return obj.month_label
    
#     def get_month_value(self, obj):
#         return obj.month_value
    
#     def get_trend_icon(self, obj):
#         trend_icons = {
#             'improving': '↗️',
#             'declining': '↘️',
#             'stable': '➡️'
#         }
#         return trend_icons.get(obj.trend, '➡️')


# class MonthlySummaryListSerializer(serializers.Serializer):
#     """Serializer for monthly summary list view - aggregates by month"""
#     month = serializers.CharField()
#     month_label = serializers.CharField()
#     total_feedbacks = serializers.IntegerField()
#     unique_employees = serializers.IntegerField()
#     overall_average_rating = serializers.FloatField()
#     employees = MonthlyFeedbackSummarySerializer(many=True)


# class UserScoreSerializer(serializers.ModelSerializer):
#     """Simple serializer for UserScore - points auto-assigned based on action"""
    
#     employee_name = serializers.CharField(source='employee.name', read_only=True)
#     awarded_by_name = serializers.SerializerMethodField()
#     category_display = serializers.CharField(source='get_category_display', read_only=True)
#     action_display = serializers.CharField(source='get_action_display', read_only=True)
#     reference_file_url = serializers.SerializerMethodField()
#     file_name = serializers.SerializerMethodField()
#     employee_details = serializers.SerializerMethodField()
#     awarded_by_details = serializers.SerializerMethodField()
#     project_name = serializers.SerializerMethodField()
#     employee_organization = serializers.SerializerMethodField()
#     awarded_by_organization = serializers.SerializerMethodField()
#     project_organization = serializers.SerializerMethodField()
    
#     class Meta:
#         model = UserScore
#         fields = '__all__'
#         read_only_fields = [
#             'merit_points', 'demerit_points', 'total_points',
#             'action_display', 'date_awarded', 'created_at',
#             'employee_name', 'awarded_by_name', 'category_display',
#             'reference_file_url', 'file_name',
#             'awarded_by',
#             'employee_details', 'awarded_by_details', 'project_name',
#             'employee_organization', 'awarded_by_organization', 'project_organization'
#         ]
    
#     def get_awarded_by_name(self, obj):
#         """Get awarded by name - works for both HrmsUsers and Employees"""
#         try:
#             if isinstance(obj.awarded_by, HrmsUsers):
#                 name = f"{obj.awarded_by.first_name} {obj.awarded_by.last_name}".strip()
#                 return name if name else obj.awarded_by.email
#             elif isinstance(obj.awarded_by, Employees):
#                 return obj.awarded_by.name
#         except Exception:
#             return None
    
#     def _get_organization_from_object(self, obj, field_name='organization_id'):
#         """Helper to get organization from object"""
#         try:
#             if hasattr(obj, field_name) and getattr(obj, field_name):
#                 return getattr(obj, field_name)
#             elif hasattr(obj, 'organization') and obj.organization:
#                 return obj.organization.id if hasattr(obj.organization, 'id') else obj.organization
#         except Exception:
#             pass
#         return None
    
#     def get_employee_organization(self, obj):
#         """Get employee's organization ID"""
#         return self._get_organization_from_object(obj.employee) if obj.employee else None
    
#     def get_project_organization(self, obj):
#         """Get project's organization ID"""
#         return self._get_organization_from_object(obj.project) if obj.project else None
    
#     def get_awarded_by_organization(self, obj):
#         """Get awarded_by's organization ID"""
#         try:
#             if isinstance(obj.awarded_by, HrmsUsers):
#                 # Check HrmsUsers directly
#                 org_id = self._get_organization_from_object(obj.awarded_by)
#                 if org_id:
#                     return org_id
                
#                 # Get organization from associated Employee record
#                 try:
#                     employee = Employees.objects.filter(hrmsuser=obj.awarded_by).first()
#                     return self._get_organization_from_object(employee) if employee else None
#                 except Exception:
#                     pass
                
#                 # Get organization from JWT token
#                 request = self.context.get('request')
#                 if request:
#                     auth_header = request.META.get('HTTP_AUTHORIZATION', '')
#                     if auth_header and auth_header.startswith('Bearer '):
#                         try:
#                             token = auth_header.split(' ')[1]
#                             decoded = jwt.decode(token, options={"verify_signature": False})
                            
#                             # Check different locations in JWT
#                             for key in ['payload.organization_id', 'organization_id', 'org_id']:
#                                 if '.' in key:
#                                     parts = key.split('.')
#                                     value = decoded
#                                     for part in parts:
#                                         if isinstance(value, dict) and part in value:
#                                             value = value[part]
#                                         else:
#                                             value = None
#                                             break
#                                     if value:
#                                         return value
#                                 elif key in decoded:
#                                     return decoded[key]
#                         except Exception:
#                             pass

#             elif isinstance(obj.awarded_by, Employees):
#                 return self._get_organization_from_object(obj.awarded_by)
                
#         except Exception:
#             pass
#         return None
    
#     def get_reference_file_url(self, obj):
#         """Generate URL for the uploaded file"""
#         if obj.reference_file:
#             request = self.context.get('request')
#             if request:
#                 return request.build_absolute_uri(obj.reference_file.url)
#             return obj.reference_file.url
#         return None
    
#     def get_file_name(self, obj):
#         """Extract filename from file path"""
#         if obj.reference_file:
#             return os.path.basename(obj.reference_file.name)
#         return None
    
#     def get_employee_details(self, obj):
#         """Get employee details"""
#         try:
#             return {
#                 'id': obj.employee.id,
#                 'name': obj.employee.name,
#                 'emp_code': obj.employee.emp_code if hasattr(obj.employee, 'emp_code') else None,
#                 'department': obj.employee.department.title if obj.employee.department else None,
#                 'organization_id': self.get_employee_organization(obj)
#             }
#         except Exception:
#             return None
    
#     def get_awarded_by_details(self, obj):
#         """Get awarded by details - works for both HrmsUsers and Employees"""
#         try:
#             awarded_by = obj.awarded_by
#             if isinstance(awarded_by, HrmsUsers):
#                 return {
#                     'id': awarded_by.id,
#                     'email': awarded_by.email,
#                     'first_name': awarded_by.first_name,
#                     'last_name': awarded_by.last_name,
#                     'is_admin': awarded_by.is_admin,
#                     'user_type': 'hrms_user',
#                     'organization_id': self.get_awarded_by_organization(obj)
#                 }
#             elif isinstance(awarded_by, Employees):
#                 return {
#                     'id': awarded_by.id,
#                     'emp_code': awarded_by.emp_code if hasattr(awarded_by, 'emp_code') else None,
#                     'name': awarded_by.name,
#                     'user_type': 'employee',
#                     'organization_id': self.get_awarded_by_organization(obj)
#                 }
#         except Exception:
#             return None
    
#     def get_project_name(self, obj):
#         """Returns project name if exists"""
#         return obj.project.name if obj.project else None

#     def validate(self, data):
#         """Validation for UserScore"""
#         request = self.context.get('request')
        
#         if request and hasattr(request, 'user'):
#             receiver_employee = data.get('employee')
            
#             if not receiver_employee:
#                 raise serializers.ValidationError({
#                     "employee": "Employee is required"
#                 })
            
#             project = data.get('project')
#             project_id = project.id if project else None
            
#             # Use permissions.py validation
#             try:
#                 receiver_employee_id = receiver_employee.id if hasattr(receiver_employee, 'id') else receiver_employee
                
#                 UserScorePermissions.validate_score_assignment(
#                     request, receiver_employee_id, project_id
#                 )
#             except ValidationError as e:
#                 raise
#             except Exception as e:
#                 raise serializers.ValidationError(str(e))
        
#         return data

#     def create(self, validated_data):
#         """Auto-assign points based on selected action"""
#         request = self.context.get('request')
        
#         # Get HrmsUsers instance - handle different cases
#         if 'awarded_by' in validated_data:
#             hrms_user = validated_data['awarded_by']
#         else:
#             hrms_user = self.context.get('hrms_user')
        
#         return super().create(validated_data)
    
#     def update(self, instance, validated_data):
#         """Handle file update if needed"""
#         if 'reference_file' in validated_data and instance.reference_file:
#             instance.reference_file.delete(save=False)
#         return super().update(instance, validated_data)


# class CategoryActionsSerializer(serializers.BaseSerializer):
#     """
#     Simple serializer to provide categories and actions for frontend dropdowns
#     """
    
#     def to_representation(self, instance):
#         """Return formatted data"""
#         categories = [
#             {'value': code, 'label': display}
#             for code, display in UserScore.CATEGORY_CHOICES
#         ]
        
#         actions_by_category = {}
#         for category_code, _ in UserScore.CATEGORY_CHOICES:
#             actions = UserScore.get_actions_by_category(category_code)
#             if actions:
#                 formatted_actions = [
#                     {
#                         'value': action['code'],
#                         'label': action['display'],
#                         'points': action['points_display']
#                     }
#                     for action in actions
#                 ]
#                 actions_by_category[category_code] = formatted_actions
        
#         return {
#             'categories': categories,
#             'actions_by_category': actions_by_category
#         }




from django.forms import ValidationError
from django.utils import timezone
import jwt
from requests import request
from rest_framework import serializers
from .models import Feedback, MonthlyFeedbackSummary, WeeklyFeedbackSummary, UserScore
from employees.models import Employees
from projects.models import Projects
from profiles_api.models import HrmsUsers
from .services.sentiment_analyzer import SentimentAnalyzer
from .permissions import FeedbackPermissions, UserScorePermissions
import json
import os

class FeedbackSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    categories_display = serializers.SerializerMethodField()
    performance_category_display = serializers.SerializerMethodField()  # New field
    project_name = serializers.SerializerMethodField()
    sender_details = serializers.SerializerMethodField()
    sender_organization_id = serializers.SerializerMethodField()
    receiver_organization_id = serializers.SerializerMethodField()
    project_organization_id = serializers.SerializerMethodField()
    project = serializers.PrimaryKeyRelatedField(
        queryset=Projects.objects.all(), 
        required=False, 
        allow_null=True
    )

    class Meta:
        model = Feedback
        fields = [
            'id',
            'sender',
            'sender_name',
            'sender_details',
            'sender_organization_id',
            'receiver',
            'receiver_name',
            'receiver_organization_id',
            'project',
            'project_name',
            'project_organization_id',
            'message',
            'rating',
            'categories',  
            'categories_display',
            'performance_categories',  # New field added
            'performance_category_display',  # Display field
            'sentiment_label',
            'sentiment_score',
            'sentiment_raw',
            'sentiment_spans',  
            'category',
            'tone',
            'strengths',
            'improvement_areas',
            'suggested_action',
            'impact_level',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'sentiment_label',
            'sentiment_score',
            'sentiment_raw',
            'sentiment_spans',  
            'category',
            'tone',
            'strengths',
            'improvement_areas',
            'suggested_action',
            'impact_level',
            'created_at',
            'updated_at',
            'categories_display',
            'performance_category_display',  # Added to read-only
            'project_name',
            'sender_details',
            'sender_organization_id',
            'receiver_organization_id',
            'project_organization_id',
        ]

    def get_performance_category_display(self, obj):
        """Returns human-readable performance category name"""
        return obj.get_performance_category_display()

    def _get_user_name(self, user):
        """Helper method to get user name safely"""
        if not user:
            return None
        if hasattr(user, 'email'):  
            name = f"{user.first_name} {user.last_name}".strip()
            return name or user.email
        elif hasattr(user, 'name'):  
            return user.name
        return None

    def get_sender_name(self, obj):
        """Get sender name - works for both HrmsUsers and Employees"""
        return self._get_user_name(obj.sender)

    def get_sender_details(self, obj):
        """Get sender details - works for both HrmsUsers and Employees"""
        try:
            sender = obj.sender
            if hasattr(sender, 'email'):  
                return {
                    'id': sender.id,
                    'email': sender.email,
                    'first_name': sender.first_name,
                    'last_name': sender.last_name,
                    'is_admin': sender.is_admin,
                    'user_type': 'hrms_user'
                }
            elif hasattr(sender, 'emp_code'):  
                return {
                    'id': sender.id,
                    'emp_code': sender.emp_code,
                    'name': sender.name,
                    'user_type': 'employee'
                }
        except Exception:
            return None

    def _get_organization_id(self, obj_or_field):
        """Helper method to get organization ID safely"""
        try:
            if hasattr(obj_or_field, 'organization_id'):
                return obj_or_field.organization_id
        except Exception:
            pass
        return None

    def get_sender_organization_id(self, obj):
        """Get sender's organization ID"""
        return self._get_organization_id(obj.sender)

    def get_receiver_organization_id(self, obj):
        """Get receiver's organization ID"""
        return self._get_organization_id(obj.receiver)

    def get_project_organization_id(self, obj):
        """Get project's organization ID"""
        return self._get_organization_id(obj.project) if obj.project else None

    def get_receiver_name(self, obj):
        """Get receiver name"""
        try:
            return obj.receiver.name
        except Exception:
            return None

    def get_categories_display(self, obj):
        """Returns human-readable category names"""
        return obj.get_categories_display()
    
    def get_project_name(self, obj):
        """Returns project name if exists"""
        return obj.project.name if obj.project else None
        
    def validate_message(self, message):
        if len(message) > 500:
            raise serializers.ValidationError("Message cannot exceed 500 characters.")
        return message

    def validate_rating(self, rating):
        if rating < 0 or rating > 5:
            raise serializers.ValidationError("Rating must be between 0 and 5.")
        return rating

    def validate_categories(self, categories):
        """Validate that categories are from the allowed choices"""
        if categories:
            if not isinstance(categories, list):
                raise serializers.ValidationError("Categories must be a list.")
            
            valid_categories = [choice[0] for choice in Feedback.FEEDBACK_CATEGORY_CHOICES]
            invalid_categories = [cat for cat in categories if cat not in valid_categories]
            
            if invalid_categories:
                raise serializers.ValidationError(
                    f"Invalid categories: {invalid_categories}. "
                    f"Must be from: {valid_categories}"
                )
        return categories

    def validate_performance_categories(self, value):
        """Validate performance_categories field"""
        if value:
            valid_choices = [choice[0] for choice in Feedback.PERFORMANCE_CATEGORY_CHOICES]
            if value not in valid_choices:
                raise serializers.ValidationError(
                    f"Invalid performance category. Must be one of: {valid_choices}"
                )
        return value
    
    def validate(self, data):
        """
        Add role-based validation with organization filtering
        """
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            return data
        
        sender_user = request.user
        
        sender = data.get('sender')
        if not sender:
            try:
                sender = Employees.objects.get(hrmsuser=sender_user)
            except Employees.DoesNotExist:
                sender = sender_user
            data['sender'] = sender
        
        receiver_employee = data.get('receiver')
        if not receiver_employee:
            raise serializers.ValidationError({
                "receiver": "Receiver is required"
            })
        project = data.get('project')
        
        # Get sender organization using the correct method
        sender_org_id = FeedbackPermissions.get_user_organization(request)  # FIXED: pass request
        
        if sender_org_id:
            if hasattr(receiver_employee, 'organization_id'):
                if receiver_employee.organization_id != sender_org_id:
                    raise serializers.ValidationError({
                        "receiver": f"Employee belongs to different organization (Org ID: {receiver_employee.organization_id})"
                    })
            if project and hasattr(project, 'organization_id'):
                if project.organization_id != sender_org_id:
                    raise serializers.ValidationError({
                        "project": f"Project belongs to different organization (Org ID: {project.organization_id})"
                    })
        
        # Check permission with organization filtering
        project_id = project.id if project else None
        
        # FIXED: Pass request object, not sender_user
        try:
            can_assign, reason, allowed_projects = FeedbackPermissions.can_assign_feedback(
                request, receiver_employee, project_id  # FIXED: pass request
            )
        except AttributeError as ae:
            # Handle the 'user' attribute error
            if "'HrmsUsers' object has no attribute 'user'" in str(ae):
                # Fallback to simpler permission check
                from profiles_api.models import HrmsUsers
                try:
                    hrms_user = HrmsUsers.objects.get(id=sender_user.id)
                    if not getattr(hrms_user, 'is_admin', False):
                        # For non-admins, do basic organization check
                        if sender_org_id and hasattr(receiver_employee, 'organization_id'):
                            if receiver_employee.organization_id != sender_org_id:
                                raise serializers.ValidationError({
                                    "receiver": "Cannot assign feedback to employee in different organization"
                                })
                        can_assign = True
                        reason = "Basic permission check"
                        allowed_projects = []
                    else:
                        can_assign = True
                        reason = "Admin permission"
                        allowed_projects = []
                except Exception:
                    raise serializers.ValidationError({
                        "project": "Permission check failed"
                    })
            else:
                raise serializers.ValidationError({
                    "project": f"Permission check error: {str(ae)}"
                })
        
        if not can_assign:
            error_msg = f"Cannot assign feedback: {reason}"
            raise serializers.ValidationError({
                "project": [error_msg]
            })
        
        # Verify project is in allowed list (only if project exists)
        if project and project.id not in allowed_projects:
            raise serializers.ValidationError({
                "project": f"Project '{project.name}' is not in allowed projects list"
            })
        
        return data

    def create(self, validated_data):
        """
        Override create to ensure sender is set from request user and run sentiment analysis
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            sender_user = request.user
            
            # Ensure sender is current user
            if 'sender' not in validated_data:
                try:
                    validated_data['sender'] = Employees.objects.get(hrmsuser=sender_user)
                except Employees.DoesNotExist:
                    validated_data['sender'] = sender_user
            
            # Organization validation - use request-based method
            sender_org_id = FeedbackPermissions.get_user_organization(request)  # FIXED: pass request
            receiver_employee = validated_data.get('receiver')
            project = validated_data.get('project')
            
            if sender_org_id:
                # Verify receiver organization
                if (hasattr(receiver_employee, 'organization_id') and 
                    receiver_employee.organization_id != sender_org_id):
                    raise serializers.ValidationError({
                        "receiver": "Cannot assign feedback to employee in different organization"
                    })
                
                # Verify project organization (only if project exists)
                if (project and hasattr(project, 'organization_id') and 
                    project.organization_id != sender_org_id):
                    raise serializers.ValidationError({
                        "project": "Cannot assign feedback for project in different organization"
                    })
        
        # Run sentiment analysis
        message = validated_data.get("message", "")
        user_category = validated_data.get('category')
        analyzer = SentimentAnalyzer()
        sentiment_result = analyzer.analyze_text(message)
        
        # Update validated_data with sentiment analysis results
        sentiment_fields = {
            "sentiment_label": sentiment_result.get("label", "neutral"),
            "sentiment_score": sentiment_result.get("score", 0.5),
            "sentiment_raw": sentiment_result,
            "category": user_category,
            "tone": sentiment_result.get("tone"),
            "strengths": sentiment_result.get("strengths"),
            "improvement_areas": sentiment_result.get("improvement_areas"),
            "suggested_action": sentiment_result.get("suggested_action"),
            "impact_level": sentiment_result.get("impact_level")
        }
        
        validated_data.update(sentiment_fields)
        
        # Note: performance_categories field will be automatically saved as it's in the model
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Override update to exclude performance_categories from being updated
        """
        # Remove performance_categories from validated_data if present
        validated_data.pop('performance_categories', None)
        
        message = validated_data.get("message", instance.message)
        user_category = validated_data.get('category')
        
        if 'categories' in validated_data:
            instance.categories = validated_data['categories']

        if message != instance.message or 'categories' in validated_data:
            analyzer = SentimentAnalyzer()
            sentiment_result = analyzer.analyze_text(message)
            
            instance.sentiment_label = sentiment_result.get("label", "neutral")
            instance.sentiment_score = sentiment_result.get("score", 0.5)
            instance.sentiment_raw = sentiment_result
            if user_category is not None:
                instance.category = user_category
                
            instance.tone = sentiment_result.get("tone", "Formal")
            instance.strengths = sentiment_result.get("strengths", "")
            instance.improvement_areas = sentiment_result.get("improvement_areas", "")
            instance.suggested_action = sentiment_result.get("suggested_action", "")
            instance.impact_level = sentiment_result.get("impact_level", "Medium")
            instance.rating = validated_data.get("rating", instance.rating)
            instance.message = message
            
            # Update project if provided (optional)
            if 'project' in validated_data:
                instance.project = validated_data['project']
            
            instance.save()
        else:
            # Update only provided fields
            if 'rating' in validated_data:
                instance.rating = validated_data['rating']
            
            if user_category is not None:
                instance.category = user_category
            
            if 'project' in validated_data:
                instance.project = validated_data['project']
            
            instance.save()
        
        return instance

class FeedbackPreDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employees
        fields = ['id', 'name', 'emp_code', 'official_email']

class WeeklySummarySerializer(serializers.ModelSerializer):
    week_range = serializers.SerializerMethodField()
    week_label = serializers.SerializerMethodField()
    feedback_report = serializers.SerializerMethodField()  
    
    class Meta:
        model = WeeklyFeedbackSummary
        fields = [
            'id',
            'week_start_date',
            'week_end_date', 
            'week_range',
            'week_label',
            'total_feedbacks',
            'average_rating',
            'category_distribution',
            'sentiment_distribution',
            'daily_rating_trends',
            'employee_id',
            'employee_name',
            'feedback_report', 
            'strengths',        
            'improvement_areas',
            'created_at'
        ]
    
    def get_week_range(self, obj):
        return f"{obj.week_start_date} to {obj.week_end_date}"
    
    def get_week_label(self, obj):
        return f"Week of {obj.week_start_date.strftime('%b %d')}"
    
    def get_feedback_report(self, obj):
        """Safely get feedback report as JSON"""
        return obj.get_feedback_report()
    
    def to_representation(self, instance):
        """Ensure all JSON fields are properly serialized"""
        data = super().to_representation(instance)
        
        # Safely handle all JSON fields
        json_fields = [
            'category_distribution',
            'sentiment_distribution',
            'daily_rating_trends',
            'strengths',
            'improvement_areas'
        ]
        
        for field in json_fields:
            value = getattr(instance, field)
            if isinstance(value, str):
                try:
                    data[field] = json.loads(value)
                except (json.JSONDecodeError, TypeError, ValueError):
                    if field in ['category_distribution', 'sentiment_distribution']:
                        data[field] = {}
                    elif field in ['daily_rating_trends', 'strengths', 'improvement_areas']:
                        data[field] = []
            elif value is None:
                if field in ['category_distribution', 'sentiment_distribution']:
                    data[field] = {}
                elif field in ['daily_rating_trends', 'strengths', 'improvement_areas']:
                    data[field] = []
        
        return data

class WeeklySummaryDetailSerializer(WeeklySummarySerializer):
    """Extended serializer for detailed view with formatted feedback report"""
    formatted_report = serializers.SerializerMethodField()
    
    class Meta(WeeklySummarySerializer.Meta):
        fields = WeeklySummarySerializer.Meta.fields + ['formatted_report']
    
    def get_formatted_report(self, obj):
        """Get the formatted feedback report with fallback structure"""
        return obj.formatted_feedback_report


class MonthlyFeedbackSummarySerializer(serializers.ModelSerializer):
    month_label = serializers.SerializerMethodField()
    month_value = serializers.SerializerMethodField()
    trend_icon = serializers.SerializerMethodField()
    
    class Meta:
        model = MonthlyFeedbackSummary
        fields = [
            'id',
            'month_start_date',
            'month_end_date',
            'month_label',
            'month_value',
            'employee_id',
            'employee_name',
            'feedback_count',
            'average_rating',
            'previous_month_rating',
            'trend',
            'trend_icon',
            'category_breakdown',
            'sentiment_breakdown',
            'created_at'
        ]
    
    def get_month_label(self, obj):
        return obj.month_label
    
    def get_month_value(self, obj):
        return obj.month_value
    
    def get_trend_icon(self, obj):
        trend_icons = {
            'improving': '↗️',
            'declining': '↘️',
            'stable': '➡️'
        }
        return trend_icons.get(obj.trend, '➡️')


class MonthlySummaryListSerializer(serializers.Serializer):
    """Serializer for monthly summary list view - aggregates by month"""
    month = serializers.CharField()
    month_label = serializers.CharField()
    total_feedbacks = serializers.IntegerField()
    unique_employees = serializers.IntegerField()
    overall_average_rating = serializers.FloatField()
    employees = MonthlyFeedbackSummarySerializer(many=True)


class UserScoreSerializer(serializers.ModelSerializer):
    """Simple serializer for UserScore - points auto-assigned based on action"""
    
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    awarded_by_name = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    reference_file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    employee_details = serializers.SerializerMethodField()
    awarded_by_details = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    employee_organization = serializers.SerializerMethodField()
    awarded_by_organization = serializers.SerializerMethodField()
    project_organization = serializers.SerializerMethodField()
    
    class Meta:
        model = UserScore
        fields = '__all__'
        read_only_fields = [
            'merit_points', 'demerit_points', 'total_points',
            'action_display', 'date_awarded', 'created_at',
            'employee_name', 'awarded_by_name', 'category_display',
            'reference_file_url', 'file_name',
            'awarded_by',
            'employee_details', 'awarded_by_details', 'project_name',
            'employee_organization', 'awarded_by_organization', 'project_organization'
        ]
    
    def get_awarded_by_name(self, obj):
        """Get awarded by name - works for both HrmsUsers and Employees"""
        try:
            if isinstance(obj.awarded_by, HrmsUsers):
                name = f"{obj.awarded_by.first_name} {obj.awarded_by.last_name}".strip()
                return name if name else obj.awarded_by.email
            elif isinstance(obj.awarded_by, Employees):
                return obj.awarded_by.name
        except Exception:
            return None
    
    def _get_organization_from_object(self, obj, field_name='organization_id'):
        """Helper to get organization from object"""
        try:
            if hasattr(obj, field_name) and getattr(obj, field_name):
                return getattr(obj, field_name)
            elif hasattr(obj, 'organization') and obj.organization:
                return obj.organization.id if hasattr(obj.organization, 'id') else obj.organization
        except Exception:
            pass
        return None
    
    def get_employee_organization(self, obj):
        """Get employee's organization ID"""
        return self._get_organization_from_object(obj.employee) if obj.employee else None
    
    def get_project_organization(self, obj):
        """Get project's organization ID"""
        return self._get_organization_from_object(obj.project) if obj.project else None
    
    def get_awarded_by_organization(self, obj):
        """Get awarded_by's organization ID"""
        try:
            if isinstance(obj.awarded_by, HrmsUsers):
                # Check HrmsUsers directly
                org_id = self._get_organization_from_object(obj.awarded_by)
                if org_id:
                    return org_id
                
                # Get organization from associated Employee record
                try:
                    employee = Employees.objects.filter(hrmsuser=obj.awarded_by).first()
                    return self._get_organization_from_object(employee) if employee else None
                except Exception:
                    pass
                
                # Get organization from JWT token
                request = self.context.get('request')
                if request:
                    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
                    if auth_header and auth_header.startswith('Bearer '):
                        try:
                            token = auth_header.split(' ')[1]
                            decoded = jwt.decode(token, options={"verify_signature": False})
                            
                            # Check different locations in JWT
                            for key in ['payload.organization_id', 'organization_id', 'org_id']:
                                if '.' in key:
                                    parts = key.split('.')
                                    value = decoded
                                    for part in parts:
                                        if isinstance(value, dict) and part in value:
                                            value = value[part]
                                        else:
                                            value = None
                                            break
                                    if value:
                                        return value
                                elif key in decoded:
                                    return decoded[key]
                        except Exception:
                            pass

            elif isinstance(obj.awarded_by, Employees):
                return self._get_organization_from_object(obj.awarded_by)
                
        except Exception:
            pass
        return None
    
    def get_reference_file_url(self, obj):
        """Generate URL for the uploaded file"""
        if obj.reference_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.reference_file.url)
            return obj.reference_file.url
        return None
    
    def get_file_name(self, obj):
        """Extract filename from file path"""
        if obj.reference_file:
            return os.path.basename(obj.reference_file.name)
        return None
    
    def get_employee_details(self, obj):
        """Get employee details"""
        try:
            return {
                'id': obj.employee.id,
                'name': obj.employee.name,
                'emp_code': obj.employee.emp_code if hasattr(obj.employee, 'emp_code') else None,
                'department': obj.employee.department.title if obj.employee.department else None,
                'organization_id': self.get_employee_organization(obj)
            }
        except Exception:
            return None
    
    def get_awarded_by_details(self, obj):
        """Get awarded by details - works for both HrmsUsers and Employees"""
        try:
            awarded_by = obj.awarded_by
            if isinstance(awarded_by, HrmsUsers):
                return {
                    'id': awarded_by.id,
                    'email': awarded_by.email,
                    'first_name': awarded_by.first_name,
                    'last_name': awarded_by.last_name,
                    'is_admin': awarded_by.is_admin,
                    'user_type': 'hrms_user',
                    'organization_id': self.get_awarded_by_organization(obj)
                }
            elif isinstance(awarded_by, Employees):
                return {
                    'id': awarded_by.id,
                    'emp_code': awarded_by.emp_code if hasattr(awarded_by, 'emp_code') else None,
                    'name': awarded_by.name,
                    'user_type': 'employee',
                    'organization_id': self.get_awarded_by_organization(obj)
                }
        except Exception:
            return None
    
    def get_project_name(self, obj):
        """Returns project name if exists"""
        return obj.project.name if obj.project else None

    def validate(self, data):
        """Validation for UserScore"""
        request = self.context.get('request')
        
        if request and hasattr(request, 'user'):
            receiver_employee = data.get('employee')
            
            if not receiver_employee:
                raise serializers.ValidationError({
                    "employee": "Employee is required"
                })
            
            project = data.get('project')
            project_id = project.id if project else None
            
            # Use permissions.py validation
            try:
                receiver_employee_id = receiver_employee.id if hasattr(receiver_employee, 'id') else receiver_employee
                
                UserScorePermissions.validate_score_assignment(
                    request, receiver_employee_id, project_id
                )
            except ValidationError as e:
                raise
            except Exception as e:
                raise serializers.ValidationError(str(e))
        
        return data

    def create(self, validated_data):
        """Auto-assign points based on selected action"""
        request = self.context.get('request')
        
        # Get HrmsUsers instance - handle different cases
        if 'awarded_by' in validated_data:
            hrms_user = validated_data['awarded_by']
        else:
            hrms_user = self.context.get('hrms_user')
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Handle file update if needed"""
        if 'reference_file' in validated_data and instance.reference_file:
            instance.reference_file.delete(save=False)
        return super().update(instance, validated_data)


class CategoryActionsSerializer(serializers.BaseSerializer):
    """
    Simple serializer to provide categories and actions for frontend dropdowns
    """
    
    def to_representation(self, instance):
        """Return formatted data"""
        categories = [
            {'value': code, 'label': display}
            for code, display in UserScore.CATEGORY_CHOICES
        ]
        
        actions_by_category = {}
        for category_code, _ in UserScore.CATEGORY_CHOICES:
            actions = UserScore.get_actions_by_category(category_code)
            if actions:
                formatted_actions = [
                    {
                        'value': action['code'],
                        'label': action['display'],
                        'points': action['points_display']
                    }
                    for action in actions
                ]
                actions_by_category[category_code] = formatted_actions
        
        return {
            'categories': categories,
            'actions_by_category': actions_by_category
        }