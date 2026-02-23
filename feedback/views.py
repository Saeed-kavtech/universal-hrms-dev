# apps/feedback/views.py
from collections import defaultdict
from datetime import datetime, timedelta
from unittest import result
from unittest import result
from django.utils import timezone
from regex import F
from requests import request
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Feedback, UserScore, WeeklyFeedbackSummary, MonthlyFeedbackSummary
from .serializers import FeedbackSerializer, FeedbackPreDataSerializer, WeeklySummarySerializer, WeeklySummaryDetailSerializer, CategoryActionsSerializer, UserScoreSerializer
from employees.models import Employees, EmployeeProjects, Projects
from .services.sentiment_analyzer import SentimentAnalyzer
from django.db.models import Avg, Count, Sum, Q
import json
from .services.trend_analyzer import TrendAnalyzer

# UPDATED IMPORTS
from .permissions import FeedbackPermissions, UserScorePermissions, UserDataManager, PermissionCore
from profiles_api.models import HrmsUsers


class FeedbackViewset(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by("-created_at")
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Override get_queryset to filter by organization
        """
        org_id = FeedbackPermissions.get_user_organization(self.request)
        
        # Start with base query
        queryset = super().get_queryset()
        
        # Add organization filter if available
        if org_id:
            queryset = queryset.filter(
                Q(receiver__organization_id=org_id) | 
                Q(project__organization_id=org_id)
            )
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        user_category = request.data.get("category")
        categories = request.data.get("categories", [])
        performance_categories = request.data.get("performance_categories")  
    
        # Ensure project field is properly set
        if 'project_id' in request.data and 'project' not in request.data:
            request.data['project'] = request.data['project_id']
   
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ADD ORGANIZATION VALIDATION BEFORE SAVING
        validated_data = serializer.validated_data
        receiver_employee = validated_data.get('receiver')
        project = validated_data.get('project')
        
        if receiver_employee and project:
            # USE THE NEW VALIDATION METHOD
            try:
                FeedbackPermissions.validate_feedback_assignment(
                    request, receiver_employee.id, project.id
                )
            except ValidationError as e:
                raise PermissionDenied(f"Cannot assign feedback: {e.detail}")
        
        feedback_text = serializer.validated_data.get("message", "")
        analyzer = SentimentAnalyzer()
        sentiment_result = analyzer.analyze_text(feedback_text, _category=user_category)

        # Include performance_categories in save
        serializer.save(
            sentiment_label=sentiment_result.get("label"),
            sentiment_score=sentiment_result.get("score"),
            sentiment_raw=sentiment_result,
            category=user_category,  
            tone=sentiment_result.get("tone"),
            strengths=sentiment_result.get("strengths"),
            improvement_areas=sentiment_result.get("improvement_areas"),
            suggested_action=sentiment_result.get("suggested_action"),
            impact_level=sentiment_result.get("impact_level"),
            categories=categories,
            performance_categories=performance_categories,  # Save performance category
        )

        return Response(
            {
                "message": "Feedback created successfully",
                "feedback": serializer.data,
                "sentiment_analysis": sentiment_result,
            },
            status=status.HTTP_201_CREATED,
        )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        
        # CHECK ORGANIZATION PERMISSION BEFORE UPDATE
        org_id = FeedbackPermissions.get_user_organization(request)
        
        if org_id:
            if (instance.receiver and hasattr(instance.receiver, 'organization_id') and 
                instance.receiver.organization_id != org_id):
                raise PermissionDenied("Cannot update feedback for employee in different organization")
            
            if (instance.project and hasattr(instance.project, 'organization_id') and 
                instance.project.organization_id != org_id):
                raise PermissionDenied("Cannot update feedback for project in different organization")
        
        user_category = request.data.get("category")
        categories = request.data.get("categories", [])
        if 'performance_categories' in request.data:
            raise ValidationError({
                "performance_categories": "This field cannot be updated after creation"
            })
        
        if 'project_id' in request.data and 'project' not in request.data:
            request.data['project'] = request.data['project_id']
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            category=user_category,  
            categories=categories
        )
        
        return Response(
            {
                "message": "Feedback updated successfully",
                "feedback": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
    
    def received_feedbacks(self, request, *args, **kwargs):
        """
        Get all feedbacks received by the current user
        Available for ALL users (admin, high-level roles, regular employees)
        """
        try: 
            # Get employee ID using the new permission system
            employee_id = PermissionCore.get_employee_id(request)
            
            if not employee_id:
                # Try direct database lookup as fallback
                current_user_id = request.user.id
                try:
                    employee = Employees.objects.filter(
                        Q(hrmsuser_id=current_user_id) | 
                        Q(hrms_user_id=current_user_id) | 
                        Q(user_id=current_user_id),
                        is_active=True
                    ).first()
                    if employee:
                        employee_id = employee.id
                    else:
                        return Response({
                            "status": "success",
                            "hasData": False,
                            "isArray": True,
                            "count": 0,
                            "data": [],
                            "message": "Employee profile not found or no feedbacks received"
                        }, status=status.HTTP_200_OK)
                except Exception:
                    return Response({
                        "status": "success",
                        "hasData": False,
                        "isArray": True,
                        "count": 0,
                        "data": [],
                        "message": "Employee profile not found or no feedbacks received"
                    }, status=status.HTTP_200_OK)
        
            notes = Feedback.objects.filter(receiver_id=employee_id)
        
            org_id = FeedbackPermissions.get_user_organization(request)
        
            if org_id:
                notes = notes.filter(
                    Q(receiver__organization_id=org_id) | 
                    Q(project__organization_id=org_id)
                )
        
            if not notes.exists():
                return Response({
                    "status": "success",
                    "hasData": False,
                    "isArray": True,
                    "count": 0,
                    "data": [],
                    "message": "No feedbacks found for this employee"
                }, status=status.HTTP_200_OK)
        
            serializer = FeedbackSerializer(notes, many=True)

            return Response({
                "status": "success",
                "hasData": True,
                "isArray": True,
                "count": notes.count(),
                "data": serializer.data,
                "message": f"Found {notes.count()} feedback(s)"
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "status": "error",
                "hasData": False,
                "isArray": False,
                "count": 0,
                "data": None,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        """
        Get sent feedbacks
        - Admins: Can see ALL sent feedbacks in organization
        - High-level roles: Can see ONLY feedbacks they sent
        - Regular employees: Can see ONLY feedbacks they sent
        """
        queryset = self.get_queryset()
        
        permission_status = FeedbackPermissions.get_permission_status(request)
        is_admin = permission_status.get('is_admin', False)
        if not is_admin:
            queryset = queryset.filter(sender=request.user)
        receiver_id = request.query_params.get("receiver")
        project_id = request.query_params.get("project")
        performance_category = request.query_params.get("performance_categories")

        if receiver_id:
            queryset = queryset.filter(receiver_id=receiver_id)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if performance_category:
            queryset = queryset.filter(performance_categories=performance_category)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        org_id = FeedbackPermissions.get_user_organization(request)
        
        if org_id:
            if (instance.receiver and hasattr(instance.receiver, 'organization_id') and 
                instance.receiver.organization_id != org_id):
                raise PermissionDenied("Cannot access feedback for employee in different organization")
        
        permission_status = FeedbackPermissions.get_permission_status(request)
        is_admin = permission_status.get('is_admin', False)
        
        if not is_admin:
            if instance.sender != request.user:
                raise PermissionDenied("You can only view feedback you sent")
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        org_id = FeedbackPermissions.get_user_organization(request)
        permission_status = FeedbackPermissions.get_permission_status(request)
        is_admin = permission_status.get('is_admin', False)
        
        if org_id:
            if is_admin:
                if (instance.receiver and hasattr(instance.receiver, 'organization_id') and 
                    instance.receiver.organization_id != org_id):
                    raise PermissionDenied("Cannot delete feedback for employee in different organization")
            else:
                if instance.sender != request.user:
                    raise PermissionDenied("You can only delete feedback you created")
        
        feedback_id = instance.id
        instance.delete()
        return Response(
            {"message": f"Feedback with ID {feedback_id} deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )
    
    def employee_feedbacks(self, request, *args, **kwargs):
        """
        Get all feedbacks for a specific employee (for HR/Manager view)
        """
        try:
            employee_id = self.kwargs.get('employee_id')

            if not employee_id:
                return Response(
                    {"error": "Employee ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                employee = Employees.objects.get(id=employee_id, is_active=True)
            except Employees.DoesNotExist:
                return Response(
                    {"error": "Employee not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
    
            permission_status = FeedbackPermissions.get_permission_status(request)
            if permission_status is None:
                permission_status = {}
    
            is_admin = permission_status.get('is_admin', False)
            can_assign = permission_status.get('can_assign', False) 
  
            user_org_id = FeedbackPermissions.get_user_organization(request)
            if user_org_id and hasattr(employee, 'organization_id'):
                if employee.organization_id != user_org_id:
                    return Response(
                        {"error": f"Cannot view feedbacks for employee in different organization"}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            feedbacks = Feedback.objects.filter(receiver_id=employee_id).order_by('-created_at')
    
            if user_org_id:
                feedbacks = feedbacks.filter(
                    Q(receiver__organization_id=user_org_id) | 
                    Q(project__organization_id=user_org_id)
                )
            if is_admin:
            # Admin: Can see all feedbacks
                pass
            else:
                current_user_employee_id = None
                try:
                    current_user_employee = Employees.objects.filter(user=request.user, is_active=True).first()
                    if current_user_employee:
                        current_user_employee_id = current_user_employee.id
                except:
                    pass
            
                if current_user_employee_id and int(employee_id) == current_user_employee_id:
                    pass
                elif can_assign:
                    feedbacks = feedbacks.filter(sender=request.user)
                else:
                    feedbacks = feedbacks.none()
    
            if not feedbacks.exists():
                if is_admin:
                    message = "No feedbacks found for this employee"
                else:
                    if current_user_employee_id and int(employee_id) == current_user_employee_id:
                        message = "No feedbacks found assigned to you"
                    elif can_assign:
                        message = "No feedbacks found that you sent to this employee"
                    else:
                        message = "No feedbacks found"
            
                return Response({
                    "employee": {
                        "id": employee.id,
                        "name": employee.name,
                        "department": employee.department.title if employee.department else None,
                        "official_email": employee.official_email
                    },
                    "feedbacks": [],
                    "total_feedbacks": 0,
                    "average_rating": 0.0,
                    "message": message
                })

            serializer = FeedbackSerializer(feedbacks, many=True)

            return Response({
                "employee": {
                    "id": employee.id,
                    "name": employee.name,
                    "department": employee.department.title if employee.department else None,
                    "official_email": employee.official_email
                },
                "feedbacks": serializer.data,
                "total_feedbacks": feedbacks.count(),
                "average_rating": feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0.0
            })

        except Exception as e:
            return Response(
                {"error": f"Failed to fetch employee feedbacks: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FeedbackPreDataView(APIView):
    """
    Provides role-based pre-data with projects and employees
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            permission_status = FeedbackPermissions.get_permission_status(request)
            
            if not permission_status.get('can_assign', False):
                return Response({
                    "success": False,
                    "error": "You don't have permission to assign feedback",
                    "permission_status": permission_status,
                    "projects": [],
                    "employees": [],
                    "has_permission": False
                }, status=status.HTTP_403_FORBIDDEN)
            
            projects = FeedbackPermissions.get_assignable_projects(request)
            
            # Get detailed employee data with their projects
            employees = FeedbackPermissions.get_assignable_employees(request)
            
            employee_list = []
            for emp in employees:
                # Get employee's projects for better UI display
                emp_projects = EmployeeProjects.objects.filter(
                    employee=emp,
                    is_active=True,
                    project__is_active=True
                ).select_related('project')
                
                project_list = []
                for ep in emp_projects:
                    project_list.append({
                        'id': ep.project.id,
                        'name': ep.project.name,
                        'code': ep.project.code
                    })
                
                employee_list.append({
                    "id": emp.id,
                    "name": emp.name,
                    "emp_code": emp.emp_code,
                    "official_email": emp.official_email,
                    "department": emp.department.title if emp.department else None,
                    "projects": project_list
                })
            
            sentiment_categories = ["positive", "corrective", "negative"]
            tones = ["encouraging", "neutral", "formal", "direct", "critical"]
            impact_levels = ["low", "medium", "high"]
            
            feedback_categories = [
                {'value': 'demo', 'label': 'Demo'},
                {'value': 'timelines', 'label': 'Timelines'},
                {'value': 'adherence', 'label': 'Adherence'},
                {'value': 'code_quality', 'label': 'Code Quality'},
                {'value': 'time_management', 'label': 'Time Management'},
            ]

            return Response(
                {
                    "success": True,
                    "permission_status": permission_status,
                    "projects": projects,
                    "employees": employee_list,
                    "has_permission": len(projects) > 0,
                    "sentiment_categories": sentiment_categories,
                    "tones": tones,
                    "impact_levels": impact_levels,
                    "feedback_categories": feedback_categories,
                    "message": "Preloaded data for feedback form",
                },
                status=status.HTTP_200_OK,
            )
            
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": str(e),
                    "projects": [],
                    "employees": [],
                    "has_permission": False
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class FeedbackUniversalViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        organization_id = self.kwargs.get("organization_id")
        
        user_org_id = FeedbackPermissions.get_user_organization(self.request)
        
        if organization_id and user_org_id and int(organization_id) != user_org_id:
            permission_status = FeedbackPermissions.get_permission_status(self.request)
            if not permission_status.get('is_admin'):
                raise PermissionDenied("Cannot access feedbacks from different organization")
        
        return Feedback.objects.filter(
            receiver__organization_id=organization_id
        ).order_by("-created_at")

class FeedbackRewriteView(APIView):
    """
    Rewrites feedback text based on the selected tone using SentimentAnalyzer.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        text = request.data.get("text")
        tone = request.data.get("tone")
        category = request.data.get("category") 
        if not text or not tone:
            return Response(
                {"error": "Both 'text' and 'tone' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
                # Pass category if provided
            result = SentimentAnalyzer().rewrite_text_in_tone(text, tone, category)           
            if not isinstance(result, dict):
                return Response(
                    {"error": "Unexpected response from sentiment analyzer."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            if "error" in result:
                return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            rewritten_text = (
                result.get("rewritten_text")
                or result.get("feedback")
                or str(result)
            )
            return Response(
                {"rewritten_text": rewritten_text},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": f"Rewrite failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FeedbackSentimentAnalysisAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Analyze feedback text for sentiment highlighting"""
        try:
            feedback_text = request.data.get("text", "")
            
            if not feedback_text:
                return Response(
                    {"error": "Text is required for sentiment analysis"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            from .services.generate_weekly_summaries import IntelligentFeedbackAnalyzer
            analyzer = IntelligentFeedbackAnalyzer()
            
            sentiment_data = analyzer.analyze_feedback_sentiment_spans(feedback_text)
            
            return Response({
                "sentiment_analysis": sentiment_data,
                "message": "Sentiment analysis completed successfully"
            })
            
        except Exception as e:
            return Response(
                {"error": f"Sentiment analysis failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BatchSentimentAnalysisAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Analyze multiple feedbacks for sentiment highlighting"""
        try:
            feedback_ids = request.data.get("feedback_ids", [])
            
            if not feedback_ids:
                return Response(
                    {"error": "Feedback IDs are required for batch analysis"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user_org_id = FeedbackPermissions.get_user_organization(request)
            
            feedbacks = Feedback.objects.filter(id__in=feedback_ids)
            
            if user_org_id:
                feedbacks = feedbacks.filter(
                    Q(receiver__organization_id=user_org_id) | 
                    Q(project__organization_id=user_org_id)
                )
            
            if not feedbacks.exists():
                return Response(
                    {"error": "No feedbacks found with the provided IDs in your organization"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            from .services.generate_weekly_summaries import IntelligentFeedbackAnalyzer
            analyzer = IntelligentFeedbackAnalyzer()
            
            results = []
            for feedback in feedbacks:
                sentiment_data = analyzer.analyze_feedback_sentiment_spans(feedback.message)
                
                feedback.sentiment_spans = sentiment_data
                feedback.save()
                
                results.append({
                    "feedback_id": feedback.id,
                    "sentiment_analysis": sentiment_data
                })
            
            return Response({
                "results": results,
                "message": f"Batch sentiment analysis completed for {len(results)} feedbacks"
            })
            
        except Exception as e:
            return Response(
                {"error": f"Batch sentiment analysis failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class FeedbackAnalyzerHelper:
    @staticmethod
    def get_feedback_text(feedback):
        """Safely get feedback text from Feedback object"""
        if hasattr(feedback, 'message') and feedback.message:
            return feedback.message
        elif hasattr(feedback, 'feedback_text') and feedback.feedback_text:
            return feedback.feedback_text
        elif hasattr(feedback, 'comments') and feedback.comments:
            return feedback.comments
        elif hasattr(feedback, 'content') and feedback.content:
            return feedback.content
        else:
            return ""

    @staticmethod
    def generate_feedback_report(employee_name, feedbacks, average_rating):
        """Generate feedback report using the intelligent analyzer"""
        
        try:
            from .services.generate_weekly_summaries import IntelligentFeedbackAnalyzer
            analyzer = IntelligentFeedbackAnalyzer()
            
            feedback_texts = []
            for feedback in feedbacks:
                text = FeedbackAnalyzerHelper.get_feedback_text(feedback)
                if text and text.strip():
                    feedback_texts.append(text)
            
            if not feedback_texts:
                return FeedbackAnalyzerHelper._get_fallback_report(employee_name, average_rating, len(feedbacks))
            report = analyzer.generate_feedback_report(employee_name, feedback_texts)
            return report
            
        except Exception:
            return FeedbackAnalyzerHelper._get_fallback_report(employee_name, average_rating, len(feedbacks))

    @staticmethod
    def _get_fallback_report(employee_name, average_rating, total_feedbacks):
        """Fallback report when intelligent analyzer fails"""
        return {
            "employee_name": employee_name,
            "sections": {
                "header": f"{employee_name}, here is your feedback analysis:",
                "areas_of_improvement": {
                    "title": "Areas of Improvement:",
                    "items": ["Focus on continuous improvement based on team feedback"]
                },
                "positives": {
                    "title": "Positives:",
                    "items": ["Demonstrating commitment and work ethic"]
                },
                "negatives": {
                    "title": "Negatives:",
                    "items": ["No significant negative feedback received"]
                },
                "conclusion": {
                    "title": "",
                    "content": f"Based on {total_feedbacks} feedback(s) with an average rating of {average_rating:.1f}/5."
                }
            }
        }


class WeeklySummaryAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try: 
            current_user_id = request.user.id
            
            # Get employee
            try:
                employee = Employees.objects.get(hrmsuser__id=current_user_id)
                employee_id = employee.id
            except Employees.DoesNotExist:
                return Response({
                    "status": "success",
                    "hasData": False,
                    "isArray": True,
                    "count": 0,
                    "data": [],
                    "summaries": [],
                    "message": "Employee profile not found or no weekly summaries"
                }, status=status.HTTP_200_OK)
                
            weeks_back = int(request.query_params.get('weeks_back', 12))
            end_date = datetime.now().date()
            start_date = end_date - timedelta(weeks=weeks_back)
            summaries = WeeklyFeedbackSummary.objects.filter(
                employee_id=employee_id,
                week_start_date__gte=start_date
            ).order_by('-week_start_date')
            
            if not summaries.exists():
                return Response({
                    "status": "success",
                    "hasData": False,
                    "isArray": True,
                    "count": 0,
                    "data": [],
                    "summaries": [],
                    "total_weeks": 0,
                    "date_range": f"{start_date} to {end_date}",
                    "employee_name": employee.name,
                    "message": "No weekly summaries found for this period"
                }, status=status.HTTP_200_OK)
            
            serializer = WeeklySummarySerializer(summaries, many=True)
            
            return Response({
                "status": "success",
                "hasData": True,
                "isArray": True,
                "count": summaries.count(),
                "data": serializer.data,
                "summaries": serializer.data,
                'total_weeks': summaries.count(),
                'date_range': f"{start_date} to {end_date}",
                'employee_name': employee.name,
                "message": f"Found {summaries.count()} weekly summary/ies"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "status": "error",
                "hasData": False,
                "isArray": False,
                "count": 0,
                "data": None,
                "error": f"Server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WeeklySummaryDetailAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, summary_id):
        """Get detailed weekly summary with formatted feedback report"""
        try:
            current_user_id = request.user.id
            try:
                employee = Employees.objects.get(hrmsuser__id=current_user_id)
                employee_id = employee.id
            except Employees.DoesNotExist:
                return Response({
                    "status": "error",
                    "hasData": False,
                    "isArray": False,
                    "count": 0,
                    "data": None,
                    "error": "Employee profile not found for current user"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # ADD ORGANIZATION FILTER TO SUMMARY QUERY
            summary = WeeklyFeedbackSummary.objects.get(
                id=summary_id,
                employee_id=employee_id
            )
            
            # Verify organization consistency
            user_org_id = FeedbackPermissions.get_user_organization(request.user)
            if user_org_id and hasattr(employee, 'organization_id'):
                if employee.organization_id != user_org_id:
                    return Response({
                        "status": "error",
                        "hasData": False,
                        "isArray": False,
                        "count": 0,
                        "data": None,
                        "error": "Cannot access summary from different organization"
                    }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = WeeklySummaryDetailSerializer(summary)
            
            return Response({
                "status": "success",
                "hasData": True,
                "isArray": False,
                "count": 1,
                "data": serializer.data,
                'summary': serializer.data,
                'employee_name': employee.name,
                "message": "Weekly summary details retrieved successfully"
            }, status=status.HTTP_200_OK)
            
        except WeeklyFeedbackSummary.DoesNotExist:
            return Response({
                "status": "error",
                "hasData": False,
                "isArray": False,
                "count": 0,
                "data": None,
                "error": "Weekly summary not found"
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "status": "error",
                "hasData": False,
                "isArray": False,
                "count": 0,
                "data": None,
                "error": f"Server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateInitialSummaryAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Generate summary for ALL existing feedbacks till today (for initial setup)"""
        try:
            current_user_id = request.user.id
            employee = Employees.objects.get(hrmsuser__id=current_user_id)
            employee_id = employee.id
            user_org_id = None
            
            # Option 1: Get from employee 
            if hasattr(employee, 'organization_id'):
                user_org_id = employee.organization_id
            elif hasattr(employee, 'organization') and employee.organization:
                user_org_id = employee.organization.id
            # Option 2: Get from user
            elif hasattr(request.user, 'organization_id'):
                user_org_id = request.user.organization_id
            elif hasattr(request.user, 'organization') and request.user.organization:
                user_org_id = request.user.organization.id
            # Option 3: Try UserScorePermissions if it exists (from your other API)
            elif hasattr(UserScorePermissions, 'get_user_organization'):
                try:
                    user_org_id = UserScorePermissions.get_user_organization(request.user)
                except:
                    user_org_id = None
            
            # Apply organization check if we have an org ID
            if user_org_id and hasattr(employee, 'organization_id'):
                if employee.organization_id != user_org_id:
                    raise PermissionDenied("Cannot generate summaries for employee in different organization")
            
            employee_feedbacks = Feedback.objects.filter(receiver_id=employee_id)
            
            # Apply organization filter
            if user_org_id:
                employee_feedbacks = employee_feedbacks.filter(
                    Q(receiver__organization_id=user_org_id) |  
                    Q(project__organization_id=user_org_id)     
                )
            
            if not employee_feedbacks.exists():
                return Response(
                    {"error": "No feedbacks found for this employee"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Delete existing summaries WITH ORGANIZATION FILTER
            WeeklyFeedbackSummary.objects.filter(employee_id=employee_id).delete()
            
            from django.db.models import Min, Max
            date_range = employee_feedbacks.aggregate(
                Min('created_at'),
                Max('created_at')
            )
            
            earliest_date = date_range['created_at__min'].date()
            latest_date = date_range['created_at__max'].date()
            
            summaries_created = 0
            current_date = earliest_date
            
            while current_date <= latest_date:
                start_of_week = current_date - timedelta(days=current_date.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                week_feedbacks = employee_feedbacks.filter(
                    created_at__date__range=[start_of_week, end_of_week]
                )
                
                if week_feedbacks.exists():
                    total_feedbacks = week_feedbacks.count()
                    average_rating = week_feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0.0
                    
                    # Category distribution
                    category_counts = {}
                    for feedback in week_feedbacks:
                        category = feedback.category
                        if category in category_counts:
                            category_counts[category] += 1
                        else:
                            category_counts[category] = 1
                    
                    category_distribution = {}
                    for category, count in category_counts.items():
                        percentage = (count / total_feedbacks) * 100
                        category_distribution[category] = {
                            'count': count,
                            'percentage': round(percentage, 1)
                        }
                    
                    # Sentiment distribution
                    sentiment_counts = {}
                    for feedback in week_feedbacks:
                        sentiment = feedback.sentiment_label
                        if sentiment in sentiment_counts:
                            sentiment_counts[sentiment] += 1
                        else:
                            sentiment_counts[sentiment] = 1
                    
                    sentiment_distribution = {}
                    for sentiment, count in sentiment_counts.items():
                        percentage = (count / total_feedbacks) * 100
                        sentiment_distribution[sentiment] = {
                            'count': count,
                            'percentage': round(percentage, 1)
                        }
                    
                    # NEW: Use the direct intelligent analyzer helper for feedback report
                    feedback_report = FeedbackAnalyzerHelper.generate_feedback_report(
                        employee.name, 
                        list(week_feedbacks), 
                        average_rating
                    )
                    
                    # Analyze feedback content for strengths and improvement areas (for separate fields)
                    from .services.generate_weekly_summaries import Command as SummaryCommand
                    summary_command = SummaryCommand()
                    analysis_results = summary_command.analyze_feedback_content(week_feedbacks)
                    
                    # Ensure proper JSON format for all fields
                    if isinstance(feedback_report, str):
                        try:
                            feedback_report = json.loads(feedback_report)
                        except (json.JSONDecodeError, TypeError, ValueError):
                            feedback_report = {}
                    
                    if isinstance(analysis_results['strengths'], str):
                        try:
                            analysis_results['strengths'] = json.loads(analysis_results['strengths'])
                        except (json.JSONDecodeError, TypeError, ValueError):
                            analysis_results['strengths'] = []
                    
                    if isinstance(analysis_results['improvement_areas'], str):
                        try:
                            analysis_results['improvement_areas'] = json.loads(analysis_results['improvement_areas'])
                        except (json.JSONDecodeError, TypeError, ValueError):
                            analysis_results['improvement_areas'] = []
                    
                    # Create summary with enhanced analysis
                    WeeklyFeedbackSummary.objects.create(
                        week_start_date=start_of_week,
                        week_end_date=end_of_week,
                        employee_id=employee_id,
                        employee_name=employee.name,
                        total_feedbacks=total_feedbacks,
                        average_rating=round(average_rating, 2),
                        category_distribution=category_distribution,
                        sentiment_distribution=sentiment_distribution,
                        daily_rating_trends=[],  # We'll add this later
                        # New fields for enhanced reporting - ensure proper JSON
                        feedback_report=feedback_report,
                        strengths=analysis_results['strengths'],
                        improvement_areas=analysis_results['improvement_areas']
                    )
                    summaries_created += 1
                    print(f"✅ Created enhanced summary for {start_of_week} to {end_of_week}: {total_feedbacks} feedbacks")
                
                current_date = end_of_week + timedelta(days=1)
            
            return Response({
                "status": "success",
                "hasData": True,
                "isArray": False,
                "count": summaries_created,
                "data": {
                    "message": f"Created {summaries_created} enhanced weekly summaries",
                    "total_feedbacks": employee_feedbacks.count(),
                    "date_range": f"{earliest_date} to {latest_date}"
                },
                "message": f"Created {summaries_created} enhanced weekly summaries",
                "total_feedbacks": employee_feedbacks.count(),
                "date_range": f"{earliest_date} to {latest_date}"
            }, status=status.HTTP_201_CREATED)
            
        except Employees.DoesNotExist:
            return Response(
                {"error": "Employee profile not found"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(f"GenerateInitialSummaryAPI Error: {str(e)}")
            import traceback
            print(f"TRACEBACK: {traceback.format_exc()}")
            return Response(
                {"error": f"Failed to generate initial summaries: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MonthlyFeedbackSummaryAPI(APIView):
    """API for monthly feedback summaries (Admin Dashboard) - Now includes User Scores"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get monthly performance summaries for admin dashboard
        Combines Feedback + User Scores (Merits/Demerits)
        Query params: month (YYYY-MM), employee_name (search)
        """
        try:
            month_param = request.query_params.get('month')
            employee_search = request.query_params.get('employee_name', '').strip()
            
            if not month_param:
                month_param = timezone.now().strftime('%Y-%m')
            
            try:
                year, month = map(int, month_param.split('-'))
                month_start = timezone.datetime(year, month, 1).date()
                
                if month == 12:
                    month_end = timezone.datetime(year, month, 31).date()
                else:
                    next_month_start = timezone.datetime(year, month + 1, 1).date()
                    month_end = next_month_start - timedelta(days=1)
                    
            except (ValueError, IndexError):
                return Response(
                    {"error": "Invalid month format. Use YYYY-MM"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user_org_id = FeedbackPermissions.get_user_organization(request)
            
            if not user_org_id:
                return Response({
                    "status": "success",
                    "hasData": False,
                    "isArray": True,
                    "count": 0,
                    "data": [],
                    "month": month_param,
                    "month_label": month_start.strftime('%B %Y'),
                    "total_feedbacks": 0,
                    "total_scores": 0,
                    "unique_employees": 0,
                    "overall_average_rating": 0.0,
                    "overall_net_points": 0,
                    "message": "No organization found in token"
                }, status=status.HTTP_200_OK)
            
            permission_status = FeedbackPermissions.get_permission_status(request)
            is_admin = permission_status.get('is_admin', False)
            
            all_feedbacks = self._get_feedback_data(
                request, month_start, month_end, user_org_id, is_admin, employee_search
            )
            
            all_user_scores = self._get_user_score_data(
                request, month_start, month_end, user_org_id, is_admin, employee_search
            )
            
            employee_ids = set()
            
            for feedback in all_feedbacks:
                if feedback.receiver:
                    employee_ids.add(feedback.receiver_id)
            
            for score in all_user_scores:
                if hasattr(score, 'employee_id'):
                    employee_ids.add(score.employee_id)
            
            if not employee_ids:
                return Response({
                    "status": "success",
                    "hasData": False,
                    "isArray": True,
                    "count": 0,
                    "data": [],
                    "month": month_param,
                    "month_label": month_start.strftime('%B %Y'),
                    "total_feedbacks": 0,
                    "total_scores": 0,
                    "unique_employees": 0,
                    "overall_average_rating": 0.0,
                    "overall_net_points": 0,
                    "message": "No data found for this month"
                }, status=status.HTTP_200_OK)
            
            employee_query = Employees.objects.filter(
                id__in=employee_ids,
                organization_id=user_org_id
            )
            
            employee_details = employee_query.select_related('department').values(
                'id', 'name', 'department__title'
            )
            
            employee_lookup = {
                emp['id']: {
                    'id': emp['id'],
                    'name': emp['name'],
                    'department': emp['department__title'] or 'N/A'
                }
                for emp in employee_details
            }
            
            monthly_data = []
            
            for employee_id in employee_ids:
                if employee_id not in employee_lookup:
                    continue
                    
                emp_info = employee_lookup[employee_id]
                
                employee_feedbacks = all_feedbacks.filter(receiver_id=employee_id)
                feedback_count = employee_feedbacks.count()
                
                employee_scores = all_user_scores.filter(employee_id=employee_id)
                
                # FIX: Initialize score_summary for all cases
                score_summary = {'total_merits': 0, 'total_demerits': 0}
                
                if feedback_count > 0:
                    average_rating = employee_feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0.0
                    category_breakdown = self._get_category_breakdown(employee_feedbacks)
                    sentiment_breakdown = self._get_sentiment_breakdown(employee_feedbacks)
                    
                    trend = TrendAnalyzer.calculate_monthly_trend(
                        employee_feedbacks, month_start, month_end
                    )
                else:
                    average_rating = 0.0
                    category_breakdown = {}
                    sentiment_breakdown = {}
                    trend = 'stable'
                
                if employee_scores.exists():
                    score_summary = employee_scores.aggregate(
                        total_merits=Sum('merit_points'),
                        total_demerits=Sum('demerit_points')
                    )
                    net_points = (score_summary['total_merits'] or 0) - (score_summary['total_demerits'] or 0)
                    
                    score_breakdown = employee_scores.values('category').annotate(
                        total_merits=Sum('merit_points'),
                        total_demerits=Sum('demerit_points'),
                        count=Count('id')
                    )
                    
                    score_category_breakdown = {}
                    for breakdown in score_breakdown:
                        category = breakdown['category']
                        merit = breakdown['total_merits'] or 0
                        demerit = breakdown['total_demerits'] or 0
                        net = merit - demerit
                        
                        score_category_breakdown[category] = {
                            'merit_points': merit,
                            'demerit_points': demerit,
                            'net_points': net,
                            'count': breakdown['count']
                        }
                else:
                    net_points = 0
                    score_category_breakdown = {}
                
                monthly_data.append({
                    'employee_id': employee_id,
                    'employee_name': emp_info['name'],
                    'department': emp_info['department'],
                    'feedback_count': feedback_count,
                    'average_rating': round(average_rating, 2),
                    'total_merit_points': score_summary.get('total_merits', 0),
                    'total_demerit_points': score_summary.get('total_demerits', 0),
                    'net_points': net_points,
                    'trend': trend,
                    'category_breakdown': category_breakdown,
                    'sentiment_breakdown': sentiment_breakdown,
                    'score_breakdown': score_category_breakdown,
                    'has_scores': employee_scores.exists(),
                    'has_feedbacks': feedback_count > 0
                })
            
            monthly_data.sort(key=lambda x: x['employee_name'])
            
            total_feedbacks = all_feedbacks.count()
            total_scores = all_user_scores.count()
            unique_employees = len(monthly_data)
            overall_avg_rating = all_feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0.0
            
            if all_user_scores.exists():
                overall_score_summary = all_user_scores.aggregate(
                    total_merits=Sum('merit_points'),
                    total_demerits=Sum('demerit_points')
                )
                overall_net_points = (overall_score_summary['total_merits'] or 0) - (overall_score_summary['total_demerits'] or 0)
            else:
                overall_net_points = 0
            
            response_data = {
                "status": "success",
                "hasData": len(monthly_data) > 0,
                "isArray": True,
                "count": len(monthly_data),
                "data": monthly_data,
                "month": month_param,
                "month_label": month_start.strftime('%B %Y'),
                "total_feedbacks": total_feedbacks,
                "total_scores": total_scores,
                "unique_employees": unique_employees,
                "overall_average_rating": round(overall_avg_rating, 2),
                "overall_net_points": overall_net_points,
                "user_permissions": {
                    "is_admin": is_admin,
                    "has_high_level_role": permission_status.get('has_high_level_role', False),
                    "can_assign": permission_status.get('can_assign', False)
                },
                "message": f"Found data for {unique_employees} employee(s) for {month_start.strftime('%B %Y')}"
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch monthly summary: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_feedback_data(self, request, month_start, month_end, user_org_id, is_admin, employee_search):
        """Get feedback data"""
        all_feedbacks = Feedback.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=month_end
        )
        
        all_feedbacks = all_feedbacks.filter(
            Q(project__isnull=True, receiver__organization_id=user_org_id) | 
            Q(project__isnull=False, project__organization_id=user_org_id)
        )
        
        if not is_admin:
            all_feedbacks = all_feedbacks.filter(sender=request.user)
        
        if employee_search:
            all_feedbacks = all_feedbacks.filter(
                receiver__name__icontains=employee_search
            )
        
        return all_feedbacks.distinct()
    
    def _get_user_score_data(self, request, month_start, month_end, user_org_id, is_admin, employee_search):
        """Get user score data"""
        all_scores = UserScore.objects.filter(
            date_occurred__gte=month_start,
            date_occurred__lte=month_end,
            status='active'
        )
        
        all_scores = all_scores.filter(
            Q(project__isnull=True, employee__organization_id=user_org_id) | 
            Q(project__isnull=False, project__organization_id=user_org_id)
        )
        
        if not is_admin:
            if hasattr(UserScore, 'awarded_by'):
                all_scores = all_scores.filter(awarded_by=request.user)
        
        if employee_search:
            all_scores = all_scores.filter(
                employee__name__icontains=employee_search
            )
        
        return all_scores
    
    def _get_category_breakdown(self, feedbacks):
        """Calculate feedback category distribution - FIXED VERSION"""
        # FIX: Handle null/empty categories and ensure count matches feedbacks
        category_distribution = feedbacks.values('category').annotate(
            count=Count('id')
        ).order_by('category')
        
        # Create breakdown including feedbacks with null categories
        breakdown = {}
        total_counted = 0
        
        for item in category_distribution:
            category_key = item['category'] if item['category'] else 'Uncategorized'
            breakdown[category_key] = item['count']
            total_counted += item['count']
        
        # If there are feedbacks but none have categories, add uncategorized
        total_feedbacks = feedbacks.count()
        if total_feedbacks > 0 and total_counted < total_feedbacks:
            uncategorized_count = total_feedbacks - total_counted
            if uncategorized_count > 0:
                if 'Uncategorized' in breakdown:
                    breakdown['Uncategorized'] += uncategorized_count
                else:
                    breakdown['Uncategorized'] = uncategorized_count
        
        return breakdown
    
    def _get_sentiment_breakdown(self, feedbacks):
        """Calculate feedback sentiment distribution - FIXED VERSION"""
        # FIX: Handle null/empty sentiment labels
        sentiment_distribution = feedbacks.values('sentiment_label').annotate(
            count=Count('id')
        ).order_by('sentiment_label')
        
        breakdown = {}
        total_counted = 0
        
        for item in sentiment_distribution:
            sentiment_key = item['sentiment_label'] if item['sentiment_label'] else 'Unknown'
            breakdown[sentiment_key] = item['count']
            total_counted += item['count']
        
        # Handle feedbacks without sentiment labels
        total_feedbacks = feedbacks.count()
        if total_feedbacks > 0 and total_counted < total_feedbacks:
            unknown_count = total_feedbacks - total_counted
            if unknown_count > 0:
                if 'Unknown' in breakdown:
                    breakdown['Unknown'] += unknown_count
                else:
                    breakdown['Unknown'] = unknown_count
        
        return breakdown

class UserScoreAPI(APIView):
    """
    API for creating and listing merit/demerit scores
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get scores for current user or specified employee
        """
        try:
            employee_id = request.query_params.get('employee_id')
            category = request.query_params.get('category')
            limit = int(request.query_params.get('limit', 50))
    
            # Get permission info (but don't include in response)
            permission_status = UserScorePermissions.get_permission_status(request)
            is_admin = permission_status.get('is_admin', False)
            can_award_scores = permission_status.get('can_assign', False)
        
            # Get current user's employee ID
            current_employee_id = PermissionCore.get_employee_id(request)
        
            # Determine which employee's scores to show
            if employee_id:
                try:
                    target_employee_id = int(employee_id)
                except ValueError:
                    return Response({
                        "success": False,
                        "error": "Invalid employee_id"
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # No employee_id specified - default to current user's scores
                target_employee_id = current_employee_id
        
            # Start with base queryset
            scores = UserScore.objects.all()
        
            # Apply organization filter
            user_org_id = UserScorePermissions.get_user_organization(request)
            if user_org_id:
                scores = scores.filter(
                    Q(employee__organization_id=user_org_id) | 
                    Q(project__organization_id=user_org_id)
                )
        
            # Permission-based filtering
            if is_admin:
                # Admin can see all scores
                if employee_id:
                    scores = scores.filter(employee_id=employee_id)
            else:
                # Non-admin users
                if not current_employee_id:
                    # User doesn't have an employee record
                    return Response({
                        "success": False,
                        "error": "Employee profile not found"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
                if target_employee_id == current_employee_id:
                    # User viewing their own scores - show only scores RECEIVED by them
                    scores = scores.filter(employee_id=current_employee_id)
                else:
                    if can_award_scores:
                        scores = scores.filter(
                            Q(awarded_by=request.user) & 
                            Q(employee_id=target_employee_id)
                        )
                    else:
                        scores = scores.filter(employee_id=current_employee_id)
        
            if category:
                scores = scores.filter(category=category)
        
            scores_count = scores.count()
        
            scores = scores.order_by('-date_awarded', '-created_at')[:limit]
        
            serializer = UserScoreSerializer(scores, many=True, context={'request': request})
        
            response_data = {
                "success": True,
                "scores": serializer.data,
                "count": scores_count, 
                "limit_applied": limit,
                "viewing_own_scores": target_employee_id == current_employee_id if current_employee_id else False
            }
            if target_employee_id:
                totals_queryset = UserScore.objects.all()
            
                if user_org_id:
                    totals_queryset = totals_queryset.filter(
                        Q(employee__organization_id=user_org_id) | 
                        Q(project__organization_id=user_org_id)
                    )
            
                totals_queryset = totals_queryset.filter(employee_id=target_employee_id)
            
                if category:
                    totals_queryset = totals_queryset.filter(category=category)
            
                if not is_admin and target_employee_id != current_employee_id and can_award_scores:
                    totals_queryset = totals_queryset.filter(awarded_by=request.user)
            
                totals = totals_queryset.aggregate(
                    total_merits=Sum('merit_points'),
                    total_demerits=Sum('demerit_points')
                )
                response_data["totals"] = {
                    "total_merits": totals['total_merits'] or 0,
                    "total_demerits": totals['total_demerits'] or 0,
                    "net_score": (totals['total_merits'] or 0) - (totals['total_demerits'] or 0)
                }
        
            return Response(response_data)
    
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": f"Failed to fetch scores: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """
        Create a new merit/demerit score entry
        """
        try:
            required_fields = ['employee', 'category', 'action']
            for field in required_fields:
                if field not in request.data:
                    return Response(
                        {
                            "success": False,
                            "error": f"Missing required field: {field}"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
    
            if 'project_id' in request.data and 'project' not in request.data:
                request.data['project'] = request.data['project_id']
    
            serializer = UserScoreSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
    
            # Get employee and check permission
            employee_id = request.data.get('employee')
            project_id = request.data.get('project')
        
            try:
                employee = Employees.objects.get(id=employee_id, is_active=True)
            except Employees.DoesNotExist:
                return Response({
                    "success": False,
                    "error": "Employee not found"
                }, status=status.HTTP_400_BAD_REQUEST)
        
            try:
                can_award, reason, _ = UserScorePermissions.can_award_score(
                    request, employee, project_id
                )
            except Exception as perm_error:
                return Response({
                    "success": False,
                    "error": f"Permission check error: {str(perm_error)}"
                }, status=status.HTTP_403_FORBIDDEN)
        
            if not can_award:
                return Response({
                    "success": False,
                    "error": f"Cannot award score: {reason}"
                }, status=status.HTTP_403_FORBIDDEN)
    
            # Save with current user
            try:
                score = serializer.save(awarded_by=request.user)
            except Exception as save_error:
                raise
    
            response_serializer = UserScoreSerializer(score, context={'request': request})
        
            return Response({
                "success": True,
                "message": "Score added successfully",
                "score": response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            return Response({
                "success": False,
                "error": "Validation failed",
                "details": e.detail if hasattr(e, 'detail') else str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "error": f"Failed to create score: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryActionsAPI(APIView):
    """API to get categories and actions for dropdowns"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all categories and their actions"""
        try:
            serializer = CategoryActionsSerializer(data={})
            if serializer.is_valid():
                return Response({
                    "success": True,
                    "data": serializer.data
                })
            return Response({
                "success": False,
                "error": "Failed to load categories"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to load categories: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ScoreCategoriesAPI(APIView):
    """API to provide score categories and actions"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get categories and actions for merit/demerit form"""
        try:
            permission_status = UserScorePermissions.get_permission_status(request)
            has_permission = permission_status.get('can_assign', False)
            
            if not has_permission:
                return Response({
                    "success": False,
                    "error": "No permission to award scores",
                    "has_permission": False,
                    "categories": [],
                    "actions_by_category": {}
                }, status=status.HTTP_403_FORBIDDEN)
            
            categories_data = []
            actions_by_category = {}
            
            for code, display in UserScore.CATEGORY_CHOICES:
                categories_data.append({
                    'value': code,
                    'label': display
                })
                
                actions = UserScore.get_actions_by_category(code)
                if actions:
                    formatted_actions = []
                    for action in actions:
                        formatted_actions.append({
                            'value': action['code'],
                            'label': action['display'],
                            'points': action['points_display']
                        })
                    actions_by_category[code] = formatted_actions
            
            return Response({
                "success": True,
                "has_permission": True,
                "permission_status": permission_status,
                "categories": categories_data,
                "actions_by_category": actions_by_category,
                "message": "Categories loaded successfully"
            })
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to load categories: {str(e)}",
                "has_permission": False,
                "categories": [],
                "actions_by_category": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PermissionCheckAPI(APIView):
    """API to check user permissions for feedback/score assignment"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Check if user has permission to assign feedback/scores"""
        try:
            permission_status = UserScorePermissions.get_permission_status(request)
            
            return Response({
                "success": True,
                "permission_status": permission_status,
                "can_assign": permission_status.get('can_assign', False),
                "message": "Permission check completed"
            })
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to check permissions: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FeedbackPermissionDataAPI(APIView):
    """API to provide permission data for feedback form"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get permission data for feedback form"""
        try:
            permission_status = FeedbackPermissions.get_permission_status(request)
            
            has_permission = permission_status.get('can_assign', False)
            
            if not has_permission:
                return Response({
                    "success": False,
                    "error": permission_status.get('message', 'No permission to assign feedback'),
                    "has_permission": False,
                    "projects": [],
                    "employees": [],
                    "message": "Permission denied"
                }, status=status.HTTP_403_FORBIDDEN)
            
            projects = FeedbackPermissions.get_assignable_projects(request)
            
            all_employees = FeedbackPermissions.get_assignable_employees(request)
            
            employee_list = []
            for emp in all_employees:
                employee_list.append({
                    "id": emp.id,
                    "name": emp.name,
                    "emp_code": emp.emp_code,
                    "official_email": emp.official_email,
                    "department": emp.department.title if emp.department else None
                })
            
            return Response({
                "success": True,
                "has_permission": True,
                "permission_status": permission_status,
                "projects": projects,
                "employees": employee_list,
                "message": "Permission data loaded successfully"
            })
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to load permission data: {str(e)}",
                "has_permission": False,
                "projects": [],
                "employees": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ScorePermissionDataAPI(APIView):
    """API to provide permission data for score form"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get permission data for score form"""
        try:
            permission_status = UserScorePermissions.get_permission_status(request)
            
            has_permission = permission_status.get('can_assign', False)
            
            if not has_permission:
                return Response({
                    "success": False,
                    "error": permission_status.get('message', 'No permission to award scores'),
                    "has_permission": False,
                    "projects": [],
                    "employees": [],
                    "categories": [],
                    "actions_by_category": {}
                }, status=status.HTTP_403_FORBIDDEN)
            
            projects = UserScorePermissions.get_assignable_projects(request)
            
            employees = UserScorePermissions.get_assignable_employees(request)
            
            employee_list = []
            for emp in employees:
                employee_list.append({
                    "id": emp.id,
                    "name": emp.name,
                    "emp_code": emp.emp_code,
                    "official_email": emp.official_email,
                    "department": emp.department.title if emp.department else None
                })
            
            categories_data = []
            actions_by_category = {}
            
            for code, display in UserScore.CATEGORY_CHOICES:
                categories_data.append({
                    'value': code,
                    'label': display
                })
                
                actions = UserScore.get_actions_by_category(code)
                if actions:
                    formatted_actions = []
                    for action in actions:
                        formatted_actions.append({
                            'value': action['code'],
                            'label': action['display'],
                            'points': action['points_display']
                        })
                    actions_by_category[code] = formatted_actions
            
            return Response({
                "success": True,
                "has_permission": True,
                "permission_status": permission_status,
                "projects": projects,
                "employees": employee_list,
                "categories": categories_data,
                "actions_by_category": actions_by_category,
                "message": "Permission data loaded successfully"
            })
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to load permission data: {str(e)}",
                "has_permission": False,
                "projects": [],
                "employees": [],
                "categories": [],
                "actions_by_category": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProjectEmployeesAPI(APIView):
    """API to get employees for a specific project"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get employees for a specific project"""
        try:
            project_id = request.query_params.get('project_id')
            
            if not project_id:
                return Response({
                    "success": False,
                    "error": "project_id parameter is required",
                    "employees": []
                }, status=status.HTTP_400_BAD_REQUEST)
            
            org_id = FeedbackPermissions.get_user_organization(request)
            
            permission_status = FeedbackPermissions.get_permission_status(request)
            has_permission = permission_status.get('can_assign', False)
            
            if not has_permission:
                return Response({
                    "success": False,
                    "error": permission_status.get('message', 'No permission to assign feedback'),
                    "has_permission": False,
                    "employees": []
                }, status=status.HTTP_403_FORBIDDEN)
            
            if org_id:
                from django.db.models import Q
                
                employee_ids = EmployeeProjects.objects.filter(
                    project_id=project_id,
                    is_active=True,
                    project__is_active=True,
                    project__organization_id=org_id,
                    employee__organization_id=org_id
                ).values_list('employee_id', flat=True).distinct()
                
                employees = Employees.objects.filter(
                    id__in=employee_ids,
                    is_active=True,
                    organization_id=org_id
                )
            else:
                employees = FeedbackPermissions.get_assignable_employees(request, project_id)
            
            employee_list = []
            for emp in employees:
                employee_list.append({
                    "id": emp.id,
                    "name": emp.name,
                    "emp_code": emp.emp_code,
                    "official_email": emp.official_email,
                    "department": emp.department.title if emp.department else None
                })
            
            project_name = "Unknown Project"
            try:
                project = Projects.objects.get(id=project_id, is_active=True)
                project_name = project.name
            except Projects.DoesNotExist:
                return Response({
                    "success": False,
                    "error": "Project not found or inactive",
                    "employees": []
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                "success": True,
                "has_permission": True,
                "project_id": int(project_id),
                "project_name": project_name,
                "employees": employee_list,
                "employee_count": len(employee_list),
                "message": f"Loaded {len(employee_list)} employees for project {project_name}"
            })
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to load employees: {str(e)}",
                "has_permission": False,
                "employees": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ScoreProjectEmployeesAPI(APIView):
    """API to get employees for a specific project (for scores)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get employees for a specific project for scoring"""
        try:
            project_id = request.query_params.get('project_id')
            
            if not project_id:
                return Response({
                    "success": False,
                    "error": "project_id parameter is required",
                    "employees": []
                }, status=status.HTTP_400_BAD_REQUEST)
            
            permission_status = UserScorePermissions.get_permission_status(request)
            has_permission = permission_status.get('can_assign', False)
            
            if not has_permission:
                return Response({
                    "success": False,
                    "error": permission_status.get('message', 'No permission to award scores'),
                    "has_permission": False,
                    "employees": []
                }, status=status.HTTP_403_FORBIDDEN)
            
            employees = UserScorePermissions.get_assignable_employees(request, project_id)
            
            employee_list = []
            for emp in employees:
                employee_list.append({
                    "id": emp.id,
                    "name": emp.name,
                    "emp_code": emp.emp_code,
                    "official_email": emp.official_email,
                    "department": emp.department.title if emp.department else None
                })
            
            project_name = "Unknown Project"
            try:
                project = Projects.objects.get(id=project_id, is_active=True)
                project_name = project.name
            except Projects.DoesNotExist:
                pass
            
            return Response({
                "success": True,
                "has_permission": True,
                "project_id": int(project_id),
                "project_name": project_name,
                "employees": employee_list,
                "employee_count": len(employee_list),
                "message": f"Loaded {len(employee_list)} employees for project {project_name}"
            })
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to load employees: {str(e)}",
                "has_permission": False,
                "employees": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDashboardInfoAPI(APIView):
    """API to get user dashboard information and permissions"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user info for dashboard display"""
        try:
            permission_status = FeedbackPermissions.get_permission_status(request)
            
            # Get employee info from permission status
            employee_info = permission_status.get('employee_record')
            
            if not employee_info:
                # Try to get employee ID and fetch from database
                employee_id = PermissionCore.get_employee_id(request)
                if employee_id:
                    try:
                        employee = Employees.objects.get(id=employee_id, is_active=True)
                        employee_info = {
                            "id": employee.id,
                            "name": employee.name,
                            "emp_code": employee.emp_code,
                            "department": employee.department.title if employee.department else None,
                            "official_email": employee.official_email
                        }
                    except Employees.DoesNotExist:
                        employee_info = None
            
            high_level_roles = UserDataManager.get_high_level_roles(request)
            
            # Get user's project roles for dashboard display
            user_details = UserDataManager.get_user_permission_details(request)
            user_project_roles = user_details.get('all_project_roles', [])
            
            response_data = {
                "success": True,
                "user": {
                    "id": request.user.id,
                    "email": request.user.email,
                    "is_admin": permission_status.get('is_admin', False),
                    "is_employee": permission_status.get('has_active_role', False)
                },
                "employee": employee_info,
                "permissions": {
                    "can_assign_feedback": permission_status.get('can_assign', False),
                    "can_assign_scores": permission_status.get('can_assign', False),
                    "show_sent_feedbacks": True,
                    "show_received_feedbacks": True,
                    "show_all_sent_feedbacks": permission_status.get('is_admin', False),
                    "is_admin": permission_status.get('is_admin', False),
                    "has_high_level_role": permission_status.get('has_high_level_role', False),
                    "has_assigned_projects": permission_status.get('has_assigned_projects', False)
                },
                "roles": high_level_roles,
                "project_roles": user_project_roles,  # Added project roles for dashboard
                "specific_role": permission_status.get('specific_role_details'),
                "message": "User dashboard info retrieved successfully"
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                "success": False,
                "error": f"Failed to get user dashboard info: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AnnualFeedbackSummaryAPI(APIView):
    """API for annual performance summaries"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get annual performance summary for a specific employee and year
        Query params: 
            - employee_id: ID of the employee
            - year: Year (YYYY)
        Returns:
            - Average rating for each month
            - Performance category counts throughout the year
            - Category field counts associated with each performance category (monthly)
            - Monthly UserScore totals (merits, demerits, net score)
        """
        try:
            employee_id = request.query_params.get('employee_id')
            year_param = request.query_params.get('year')
            
            if not employee_id or not year_param:
                return Response(
                    {"error": "Both employee_id and year parameters are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                year = int(year_param)
                if year < 2000 or year > timezone.now().year:
                    return Response(
                        {"error": "Invalid year"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except ValueError:
                return Response(
                    {"error": "Year must be a valid integer (YYYY)"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate employee exists and belongs to user's organization
            user_org_id = FeedbackPermissions.get_user_organization(request)
            
            try:
                employee = Employees.objects.get(
                    id=employee_id,
                    organization_id=user_org_id
                )
            except Employees.DoesNotExist:
                return Response(
                    {"error": "Employee not found or not authorized"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate date range for the year
            year_start = timezone.datetime(year, 1, 1).date()
            year_end = timezone.datetime(year, 12, 31).date()
            
            # Get all feedback for the employee in the given year
            feedbacks = Feedback.objects.filter(
                receiver=employee,
                created_at__date__gte=year_start,
                created_at__date__lte=year_end
            )
            
            # Get all user scores for the employee in the given year
            user_scores = UserScore.objects.filter(
                employee=employee,
                date_occurred__gte=year_start,
                date_occurred__lte=year_end,
                status='active'
            )
            
            # Get category choices dictionaries for efficient lookups
            category_choices_dict = dict(Feedback.CATEGORY_CHOICES)
            performance_category_dict = dict(Feedback.PERFORMANCE_CATEGORY_CHOICES)
            
            # Initialize monthly data structure
            monthly_data = []
            
            for month in range(1, 13):
                month_start = timezone.datetime(year, month, 1).date()
                if month == 12:
                    month_end = timezone.datetime(year, month, 31).date()
                else:
                    next_month_start = timezone.datetime(year, month + 1, 1).date()
                    month_end = next_month_start - timedelta(days=1)
                
                # Monthly feedback metrics
                month_feedbacks = feedbacks.filter(
                    created_at__date__gte=month_start,
                    created_at__date__lte=month_end
                )
                
                # Monthly user score metrics
                month_scores = user_scores.filter(
                    date_occurred__gte=month_start,
                    date_occurred__lte=month_end
                )
                
                # Average rating for the month
                avg_rating = month_feedbacks.aggregate(
                    avg_rating=Avg('rating')
                )['avg_rating'] or 0.0
                
                # UserScore totals for the month
                score_summary = month_scores.aggregate(
                    total_merits=Sum('merit_points'),
                    total_demerits=Sum('demerit_points')
                )
                
                total_merits = score_summary.get('total_merits') or 0
                total_demerits = score_summary.get('total_demerits') or 0
                net_score = total_merits - total_demerits
                
                # Get performance category analysis for this month
                month_performance_categories = self._get_performance_category_analysis(month_feedbacks)
                
                # Get category field counts for this month
                month_category_field_counts = self._get_category_field_counts_for_month(
                    month_feedbacks, 
                    category_choices_dict, 
                    performance_category_dict
                )
                
                monthly_data.append({
                    'month': month,
                    'month_name': month_start.strftime('%B'),
                    'average_rating': round(avg_rating, 2),
                    'feedback_count': month_feedbacks.count(),
                    'merit_points': total_merits,
                    'demerit_points': total_demerits,
                    'net_score': net_score,
                    'performance_categories': month_performance_categories,
                    'category_field_counts': month_category_field_counts
                })
            
            # Performance category analysis for the entire year (still useful for overall view)
            performance_category_data = self._get_performance_category_analysis(feedbacks)
            
            # Yearly category field counts (aggregated from monthly data)
            yearly_category_field_counts = self._aggregate_yearly_category_field_counts(monthly_data)
            
            # UserScore summary for the year
            yearly_score_summary = self._get_yearly_score_summary(user_scores)
            
            # Overall statistics
            overall_stats = {
                'total_feedbacks': feedbacks.count(),
                'average_rating_year': round(feedbacks.aggregate(Avg('rating'))['rating__avg'] or 0.0, 2),
                'performance_categories_count': len(performance_category_data),
                'months_with_feedback': sum(1 for month in monthly_data if month['feedback_count'] > 0),
                'months_with_scores': sum(1 for month in monthly_data if month['merit_points'] > 0 or month['demerit_points'] > 0)
            }
            
            response_data = {
                "status": "success",
                "employee_id": employee_id,
                "employee_name": employee.name,
                "year": year,
                "overall_stats": overall_stats,
                "monthly_breakdown": monthly_data,
                "performance_categories": performance_category_data,
                "category_field_counts": yearly_category_field_counts,  # Yearly aggregated version
                "yearly_score_summary": yearly_score_summary,
                "message": f"Annual summary for {employee.name} in {year}"
            }
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to fetch annual summary: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_performance_category_analysis(self, feedbacks):
        """Analyze performance categories for given feedbacks"""
        # Get count of each performance category
        category_counts = feedbacks.filter(
            performance_categories__isnull=False
        ).values('performance_categories').annotate(
            count=Count('id'),
            avg_rating=Avg('rating')
        )
        
        # Get performance category display names
        performance_category_map = dict(Feedback.PERFORMANCE_CATEGORY_CHOICES)
        
        category_data = []
        for category in category_counts:
            category_code = category['performance_categories']
            category_data.append({
                'category_code': category_code,
                'category_name': performance_category_map.get(category_code, category_code),
                'count': category['count'],
                'average_rating': round(category['avg_rating'] or 0.0, 2)
            })
        
        # Sort by count descending
        category_data.sort(key=lambda x: x['count'], reverse=True)
        
        return category_data

    def _get_category_field_counts_for_month(self, month_feedbacks, category_choices_dict, performance_category_dict):
        """Get count of each category field associated with performance categories for a specific month"""
        # Initialize result structure
        result = {}
        
        # Get all feedbacks with performance categories for this month
        relevant_feedbacks = month_feedbacks.filter(
            performance_categories__isnull=False
        )
        
        for feedback in relevant_feedbacks:
            perf_category = feedback.performance_categories
            category = feedback.category
            
            if not perf_category:
                continue
            
            # Initialize for this performance category if not exists
            if perf_category not in result:
                result[perf_category] = {
                    'performance_category_name': performance_category_dict.get(perf_category, perf_category),
                    'associated_categories': defaultdict(int),
                    'total_associations': 0,
                    'total_feedbacks': 0,
                    'average_rating': 0.0
                }
            
            # Track total feedbacks for this performance category
            result[perf_category]['total_feedbacks'] += 1
            
            # Add rating for average calculation
            result[perf_category]['average_rating'] += feedback.rating
            
            # Process the single category
            if not category:
                # If no category, count as "Uncategorized"
                result[perf_category]['associated_categories']['uncategorized'] += 1
                result[perf_category]['total_associations'] += 1
            else:
                # Find the category code
                category_code = None
                
                # If category is already a code from choices
                if category in category_choices_dict:
                    category_code = category
                else:
                    # Try to match by name
                    for code, name in Feedback.CATEGORY_CHOICES:
                        if name == category:
                            category_code = code
                            break
                
                if category_code:
                    result[perf_category]['associated_categories'][category_code] += 1
                    result[perf_category]['total_associations'] += 1
                else:
                    # If category not found in choices, use as-is
                    result[perf_category]['associated_categories'][category] += 1
                    result[perf_category]['total_associations'] += 1
        
        # Calculate averages and convert to final structure
        final_result = {}
        for perf_category, data in result.items():
            # Calculate average rating
            if data['total_feedbacks'] > 0:
                data['average_rating'] = round(data['average_rating'] / data['total_feedbacks'], 2)
            
            category_list = []
            
            for cat_code, count in data['associated_categories'].items():
                # Get display name
                if cat_code == 'uncategorized':
                    display_name = 'Uncategorized'
                else:
                    display_name = category_choices_dict.get(cat_code, cat_code)
                
                category_list.append({
                    'category_code': cat_code,
                    'category_name': display_name,
                    'count': count
                })
            
            # Sort by count descending
            category_list.sort(key=lambda x: x['count'], reverse=True)
            
            final_result[perf_category] = {
                'performance_category_name': data['performance_category_name'],
                'associated_categories': category_list,
                'total_associations': data['total_associations'],
                'total_feedbacks': data['total_feedbacks'],
                'average_rating': data['average_rating']
            }
        
        return final_result
    
    def _aggregate_yearly_category_field_counts(self, monthly_data):
        """Aggregate category field counts from all months for yearly view"""
        yearly_aggregate = {}
        
        for month_data in monthly_data:
            month_category_counts = month_data.get('category_field_counts', {})
            
            for perf_category, month_data in month_category_counts.items():
                if perf_category not in yearly_aggregate:
                    # Initialize with month_data structure
                    yearly_aggregate[perf_category] = {
                        'performance_category_name': month_data['performance_category_name'],
                        'associated_categories': defaultdict(int),
                        'total_associations': 0,
                        'total_feedbacks': 0,
                        'total_rating': 0.0
                    }
                
                # Add counts
                yearly_aggregate[perf_category]['total_associations'] += month_data['total_associations']
                yearly_aggregate[perf_category]['total_feedbacks'] += month_data['total_feedbacks']
                yearly_aggregate[perf_category]['total_rating'] += month_data['average_rating'] * month_data['total_feedbacks']
                
                # Add category counts
                for category_item in month_data['associated_categories']:
                    cat_code = category_item['category_code']
                    yearly_aggregate[perf_category]['associated_categories'][cat_code] += category_item['count']
        
        # Convert to final structure with averages
        final_result = {}
        for perf_category, data in yearly_aggregate.items():
            # Calculate yearly average rating
            avg_rating = 0.0
            if data['total_feedbacks'] > 0:
                avg_rating = round(data['total_rating'] / data['total_feedbacks'], 2)
            
            category_list = []
            for cat_code, count in data['associated_categories'].items():
                # Get display name
                if cat_code == 'uncategorized':
                    display_name = 'Uncategorized'
                else:
                    display_name = dict(Feedback.CATEGORY_CHOICES).get(cat_code, cat_code)
                
                category_list.append({
                    'category_code': cat_code,
                    'category_name': display_name,
                    'count': count
                })
            
            # Sort by count descending
            category_list.sort(key=lambda x: x['count'], reverse=True)
            
            final_result[perf_category] = {
                'performance_category_name': data['performance_category_name'],
                'associated_categories': category_list,
                'total_associations': data['total_associations'],
                'total_feedbacks': data['total_feedbacks'],
                'average_rating': avg_rating
            }
        
        return final_result
    
    def _get_yearly_score_summary(self, user_scores):
        """Get yearly UserScore summary"""
        if not user_scores.exists():
            return {
                'total_merits': 0,
                'total_demerits': 0,
                'net_score': 0,
                'score_breakdown': []
            }
        
        # Overall summary
        overall_summary = user_scores.aggregate(
            total_merits=Sum('merit_points'),
            total_demerits=Sum('demerit_points')
        )
        
        total_merits = overall_summary.get('total_merits') or 0
        total_demerits = overall_summary.get('total_demerits') or 0
        
        # Category breakdown
        category_breakdown = user_scores.values('category').annotate(
            total_merits=Sum('merit_points'),
            total_demerits=Sum('demerit_points'),
            count=Count('id')
        ).order_by('-total_merits')
        
        # Get category display names
        category_map = dict(UserScore.CATEGORY_CHOICES)
        
        breakdown_data = []
        for item in category_breakdown:
            category_code = item['category']
            breakdown_data.append({
                'category_code': category_code,
                'category_name': category_map.get(category_code, category_code),
                'merit_points': item['total_merits'] or 0,
                'demerit_points': item['total_demerits'] or 0,
                'net_points': (item['total_merits'] or 0) - (item['total_demerits'] or 0),
                'count': item['count']
            })
        
        return {
            'total_merits': total_merits,
            'total_demerits': total_demerits,
            'net_score': total_merits - total_demerits,
            'score_breakdown': breakdown_data
        }
