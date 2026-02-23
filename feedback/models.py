# # apps/feedback/models.py
# import os
# from django.db import models
# from django.utils import timezone
# from employees.models import Employees
# from projects.models import Projects
# from profiles_api.models import HrmsUsers  # Changed from hrms_users.models import HrmsUsers
# from django.core.serializers.json import DjangoJSONEncoder
# from django.core.validators import MinValueValidator, MaxValueValidator
# import json


# class Feedback(models.Model):
#     FEEDBACK_CATEGORY_CHOICES = [
#         ('demo', 'Demo'),
#         ('timelines', 'Timelines'),
#         ('adherence', 'Adherence'),
#         ('code_quality', 'Code Quality'),
#         ('time_management', 'Time Management'),
#     ]  
#     sender = models.ForeignKey(
#         HrmsUsers,
#         related_name='feedback_sent',
#         on_delete=models.CASCADE,
#         help_text="User sending the feedback"
#     )
#     receiver = models.ForeignKey(
#         Employees, 
#         related_name='feedback_received', 
#         on_delete=models.CASCADE,
#         help_text="Employee receiving the feedback"
#     )  
#     project = models.ForeignKey(
#         Projects, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True,
#         help_text="Project for which feedback is given"
#     )   
#     message = models.TextField()
#     rating = models.FloatField(default=0.0)
#     categories = models.JSONField(
#         null=True, 
#         blank=True,
#         help_text="Selected feedback categories/tags like Demo, Timelines, etc."
#     )  
#     sentiment_label = models.CharField(max_length=20, null=True, blank=True)
#     sentiment_score = models.FloatField(null=True, blank=True)
#     sentiment_raw = models.JSONField(null=True, blank=True)
#     sentiment_spans = models.JSONField(
#         null=True, 
#         blank=True,
#         encoder=DjangoJSONEncoder,
#         help_text="Sentiment analysis spans for text highlighting"
#     )  
#     CATEGORY_CHOICES = [
#         ('constructive', 'Constructive'),  
#         ('corrective', 'Corrective'),    
#         ('warning', 'Warning'),          
#         ('time_management', 'Time Management'),
#     ]
#     category = models.CharField(
#         max_length=30, choices=CATEGORY_CHOICES, null=True, blank=True,
#         help_text="Feedback category derived from sentiment (positive/corrective/negative)"
#     )
#     tone = models.CharField(
#         max_length=50, null=True, blank=True,
#         help_text="Tone of the feedback, e.g. encouraging, formal, direct"
#     )
#     strengths = models.JSONField(
#         null=True, blank=True,
#         help_text="List of positive aspects or skills identified in the feedback"
#     )
#     improvement_areas = models.JSONField(
#         null=True, blank=True,
#         help_text="List of improvement points identified in the feedback"
#     )
#     suggested_action = models.TextField(
#         null=True, blank=True,
#         help_text="Automatically generated suggestion for improvement or continuation"
#     )
#     IMPACT_LEVEL_CHOICES = [
#         ('low', 'Low'),
#         ('medium', 'Medium'),
#         ('high', 'High'),
#     ]
#     impact_level = models.CharField(
#         max_length=10, choices=IMPACT_LEVEL_CHOICES, null=True, blank=True,
#         help_text="Impact or urgency level derived from feedback sentiment"
#     )
#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         sender_name = f"{self.sender.first_name} {self.sender.last_name}" if hasattr(self.sender, 'first_name') else self.sender.email
#         receiver_name = f"{self.receiver.first_name} {self.receiver.last_name}"
#         return f"Feedback({sender_name} -> {receiver_name})"

#     def get_categories_display(self):
#         """Returns human-readable category names"""
#         if not self.categories:
#             return []
        
#         category_map = dict(self.FEEDBACK_CATEGORY_CHOICES)
#         return [category_map.get(cat, cat) for cat in self.categories if cat in category_map]

#     class Meta:
#         verbose_name = "Feedback"
#         verbose_name_plural = "Feedback"
#         ordering = ['-created_at']


# class WeeklyFeedbackSummary(models.Model):
#     week_start_date = models.DateField()
#     week_end_date = models.DateField()
#     total_feedbacks = models.IntegerField(default=0)
#     average_rating = models.FloatField(default=0.0)
#     category_distribution = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
#     sentiment_distribution = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
#     daily_rating_trends = models.JSONField(default=list, encoder=DjangoJSONEncoder)  
#     employee_id = models.IntegerField(null=True, blank=True)
#     employee_name = models.CharField(max_length=255, null=True, blank=True)  
#     feedback_report = models.JSONField(
#         default=dict, 
#         encoder=DjangoJSONEncoder,
#         blank=True,
#         help_text="Comprehensive feedback analysis report as JSON"
#     )  
#     strengths = models.JSONField(
#         default=list, 
#         encoder=DjangoJSONEncoder,
#         blank=True, 
#         help_text="List of identified strengths"
#     )
#     improvement_areas = models.JSONField(
#         default=list, 
#         encoder=DjangoJSONEncoder,
#         blank=True, 
#         help_text="List of improvement areas"
#     )    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         unique_together = ['week_start_date', 'week_end_date', 'employee_id']
#         verbose_name_plural = "Weekly Feedback Summaries"
#         ordering = ['-week_start_date']
    
#     def __str__(self):
#         if self.employee_name:
#             return f"{self.employee_name} - {self.week_start_date} to {self.week_end_date}"
#         return f"Organization Summary - {self.week_start_date} to {self.week_end_date}"

#     def save(self, *args, **kwargs):
#         """Ensure feedback_report is properly formatted before saving"""
#         if isinstance(self.feedback_report, str):
#             try:
#                 self.feedback_report = json.loads(self.feedback_report)
#             except json.JSONDecodeError:
#                 self.feedback_report = {}
#         super().save(*args, **kwargs)
    
#     def get_feedback_report(self):
#         """Safely get feedback report as dictionary"""
#         if isinstance(self.feedback_report, str):
#             try:
#                 return json.loads(self.feedback_report)
#             except json.JSONDecodeError:
#                 return {}
#         return self.feedback_report or {}


# class MonthlyFeedbackSummary(models.Model):
#     """Monthly feedback summary for admin dashboard"""
#     month_start_date = models.DateField(help_text="First day of the month")
#     month_end_date = models.DateField(help_text="Last day of the month")
#     employee_id = models.IntegerField()
#     employee_name = models.CharField(max_length=255)
#     feedback_count = models.IntegerField(default=0)
#     average_rating = models.FloatField(default=0.0)
#     previous_month_rating = models.FloatField(null=True, blank=True)
#     trend = models.CharField(
#         max_length=20, 
#         choices=[('improving', 'Improving'), ('declining', 'Declining'), ('stable', 'Stable')],
#         default='stable'
#     )
#     category_breakdown = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
#     sentiment_breakdown = models.JSONField(default=dict, encoder=DjangoJSONEncoder)    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)   
#     class Meta:
#         unique_together = ['month_start_date', 'employee_id']
#         verbose_name_plural = "Monthly Feedback Summaries"
#         ordering = ['-month_start_date', 'employee_name']
    
#     def __str__(self):
#         return f"{self.employee_name} - {self.month_start_date.strftime('%B %Y')}"
    
#     @property
#     def month_label(self):
#         return self.month_start_date.strftime('%B %Y')
    
#     @property
#     def month_value(self):
#         return self.month_start_date.strftime('%Y-%m')


# def user_score_file_path(instance, filename):
#     """File upload path for user score attachments"""
#     ext = filename.split('.')[-1]
#     timestamp = timezone.now().strftime('%Y%m%d_%H%M%S') 
#     if instance.id:
#         return f'user_scores/{instance.employee.id}/{instance.id}_{timestamp}.{ext}'
#     return f'user_scores/{instance.employee.id}/{timestamp}.{ext}'


# class UserScore(models.Model):
#     """
#     Model to track merit and demerit points for employees based on PMO Scoring Table
#     Points are AUTOMATICALLY assigned based on selected category and action
#     """
#     CATEGORY_CHOICES = [
#         ('task_leadership', 'Task Leadership in Critical Situations'),
#         ('task_responsiveness', 'Task Responsiveness & Resolution'),
#         ('technical_guidance', 'Technical Guidance'),
#         ('team_communication', 'Team Communication and Collaboration'),
#         ('organizational_skills', 'Organizational Skills'),
#         ('work_standards', 'Adherence to Work Standards'),
#     ]   
#     ACTION_CHOICES = [
#         ('leadership_critical_tasks', 'Taking ownership and completing critical tasks outside normal responsibilities'),
#         ('leadership_failure', 'Failure to effectively manage additional responsibilities, causing delays'),
#         ('response_individual', 'Prompt response to client inquiries regarding individual tasks outside of regular working hours'),
#         ('resolution_individual', 'Timely resolution of any client concerns related to individual tasks during non-working hours'),
#         ('response_team', 'Prompt response to client inquiries regarding team tasks outside of regular working hours'),
#         ('resolution_team', 'Timely resolution of any client concerns related to team tasks during non-working hours'),
#         ('mentorship_support', 'Providing mentorship or support to peers on complex tasks when needed, during non-working hours'),
#         ('collaboration_failure', 'Failure to collaborate or assist team members as needed during non-working hours'),
#         ('cross_department', 'Volunteering and completing tasks for cross-department collaborations during critical phases'),
#         ('poor_collaboration', 'Poor collaboration impacting high-stakes outcomes'),
#         ('positive_feedback', 'Positive client feedback on handling additional responsibilities'),
#         ('negative_feedback', 'Negative client feedback on additional tasks or responsiveness'),
#         ('proactive_prevention', 'Proactively preventing potential delays that would impact project criticality'),
#         ('ineffective_management', 'Ineffective task management leading to team delays in high-criticality situations'),
#         ('missing_work', 'Missing work without prior notice or reason'),
#         ('repeated_delays', 'Repeated delays and bugs without a valid reason'),
#         ('valuable_optimizations', 'Proposing valuable optimizations and leading implementation'),
#     ]
#     STATUS_CHOICES = [
#         ('active', 'Active'),
#         ('pending', 'Pending Approval'),
#         ('rejected', 'Rejected'),
#         ('revoked', 'Revoked'),
#     ]
#     ACTION_POINTS_MAP = {
#         'leadership_critical_tasks': {'merit': 20, 'demerit': 0},
#         'leadership_failure': {'merit': 0, 'demerit': 5},
#         'response_individual': {'merit': 5, 'demerit': 0},
#         'resolution_individual': {'merit': 10, 'demerit': 0},
#         'response_team': {'merit': 10, 'demerit': 0},
#         'resolution_team': {'merit': 20, 'demerit': 0},
#         'mentorship_support': {'merit': 15, 'demerit': 0},
#         'collaboration_failure': {'merit': 0, 'demerit': 10},
#         'cross_department': {'merit': 15, 'demerit': 0},
#         'poor_collaboration': {'merit': 0, 'demerit': 10},
#         'positive_feedback': {'merit': 10, 'demerit': 0},
#         'negative_feedback': {'merit': 0, 'demerit': 15},
#         'proactive_prevention': {'merit': 15, 'demerit': 0},
#         'ineffective_management': {'merit': 0, 'demerit': 10},
#         'missing_work': {'merit': 0, 'demerit': 10},
#         'repeated_delays': {'merit': 0, 'demerit': 15},
#         'valuable_optimizations': {'merit': 25, 'demerit': 0},
#     }
#     CATEGORY_ACTION_MAP = {
#         'task_leadership': ['leadership_critical_tasks', 'leadership_failure'],
#         'task_responsiveness': ['response_individual', 'resolution_individual', 
#                                'response_team', 'resolution_team'],
#         'technical_guidance': ['mentorship_support', 'collaboration_failure'],
#         'team_communication': ['cross_department', 'poor_collaboration', 
#                               'positive_feedback', 'negative_feedback'],
#         'organizational_skills': ['proactive_prevention', 'ineffective_management'],
#         'work_standards': ['missing_work', 'repeated_delays', 'valuable_optimizations'],
#     }   
#     employee = models.ForeignKey(
#         'employees.Employees',
#         related_name='scores_received',
#         on_delete=models.CASCADE,
#         help_text="Employee receiving the score"
#     )   
#     awarded_by = models.ForeignKey(
#         HrmsUsers, 
#         related_name='scores_awarded',
#         on_delete=models.CASCADE,
#         help_text="User who awarded the score"
#     ) 
#     project = models.ForeignKey(
#         'projects.Projects',
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         help_text="Project for which score is awarded (optional)"
#     )   
#     category = models.CharField(
#         max_length=50,
#         choices=CATEGORY_CHOICES,
#         help_text="Main category from PMO Scoring Table"
#     )   
#     action = models.CharField(
#         max_length=50,
#         choices=ACTION_CHOICES,
#         help_text="Selected action/activity"
#     )   
#     action_display = models.CharField(
#         max_length=255,
#         blank=True,
#         help_text="Display name of the selected action"
#     )   
#     merit_points = models.IntegerField(
#         default=0,
#         validators=[MinValueValidator(0), MaxValueValidator(25)],
#         help_text="Automatically assigned merit points"
#     )   
#     demerit_points = models.IntegerField(
#         default=0,
#         validators=[MinValueValidator(0), MaxValueValidator(20)],
#         help_text="Automatically assigned demerit points (stored as positive)"
#     )   
#     evidence = models.TextField(
#         blank=True,
#         help_text="Evidence or reference (JIRA ticket, email, document, etc.)"
#     )   
#     reference_file = models.FileField(
#         upload_to=user_score_file_path,
#         null=True,
#         blank=True,
#         max_length=500,
#         help_text="Optional file upload for evidence (images, documents, etc.)"
#     )  
#     notes = models.TextField(
#         blank=True,
#         help_text="Additional comments or context"
#     )   
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='active'
#     )  
#     date_occurred = models.DateField(
#         default=timezone.now,
#         help_text="Date when the action occurred"
#     )   
#     date_awarded = models.DateTimeField(
#         auto_now_add=True,
#         help_text="Date when score was recorded"
#     )   
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         verbose_name = "User Score"
#         verbose_name_plural = "User Scores"
#         ordering = ['-date_awarded', '-created_at']
#         indexes = [
#             models.Index(fields=['employee', 'category']),
#             models.Index(fields=['status', 'date_awarded']),
#         ]
    
#     def __str__(self):
#         awarded_by_name = f"{self.awarded_by.first_name} {self.awarded_by.last_name}" if hasattr(self.awarded_by, 'first_name') else self.awarded_by.email
#         return f"{self.employee} - {self.get_category_display()}: {self.points_display} (by {awarded_by_name})"
    
#     @property
#     def total_points(self):
#         """Calculate net points (merits - demerits)"""
#         return self.merit_points - self.demerit_points
    
#     @property
#     def points_display(self):
#         """Display points as +X or -Y"""
#         if self.merit_points > 0:
#             return f"+{self.merit_points}"
#         elif self.demerit_points > 0:
#             return f"-{self.demerit_points}"
#         return "0"
    
#     @classmethod
#     def get_points_for_action(cls, action_code):
#         """Get predefined points for a given action code"""
#         points = cls.ACTION_POINTS_MAP.get(action_code, {'merit': 0, 'demerit': 0})
#         display = dict(cls.ACTION_CHOICES).get(action_code, '')
        
#         return {
#             'merit_points': points['merit'],
#             'demerit_points': points['demerit'],
#             'action_display': display
#         }
    
#     @classmethod
#     def get_actions_by_category(cls, category_code):
#         """Get all actions for a specific category"""
#         action_codes = cls.CATEGORY_ACTION_MAP.get(category_code, [])
#         actions = []
        
#         for code in action_codes:
#             points = cls.ACTION_POINTS_MAP.get(code, {'merit': 0, 'demerit': 0})
#             display = dict(cls.ACTION_CHOICES).get(code, '')
            
#             points_display = f"+{points['merit']}" if points['merit'] > 0 else f"-{points['demerit']}" if points['demerit'] > 0 else "0"
            
#             actions.append({
#                 'code': code,
#                 'display': display,
#                 'merit_points': points['merit'],
#                 'demerit_points': points['demerit'],
#                 'points_display': points_display
#             })
        
#         return actions
    
#     def save(self, *args, **kwargs):
#         """Automatically assign points based on selected action"""
#         if self.action:
#             points_info = self.get_points_for_action(self.action)
            
#             self.merit_points = points_info['merit_points']
#             self.demerit_points = points_info['demerit_points']
            
#             if not self.action_display:
#                 self.action_display = points_info['action_display']
        
#         if not self.category and self.action:
#             for cat_code, actions_list in self.CATEGORY_ACTION_MAP.items():
#                 if self.action in actions_list:
#                     self.category = cat_code
#                     break
        
#         super().save(*args, **kwargs)


# apps/feedback/models.py
import os
from django.db import models
from django.utils import timezone
from employees.models import Employees
from projects.models import Projects
from profiles_api.models import HrmsUsers  # Changed from hrms_users.models import HrmsUsers
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinValueValidator, MaxValueValidator
import json



class Feedback(models.Model):
    FEEDBACK_CATEGORY_CHOICES = [
        ('demo', 'Demo'),
        ('timelines', 'Timelines'),
        ('adherence', 'Adherence'),
        ('code_quality', 'Code Quality'),
        ('time_management', 'Time Management'),
    ]
    
    PERFORMANCE_CATEGORY_CHOICES = [
        ('job_related_skills', 'Job-Related Skills'),
        ('productivity', 'Productivity'),
        ('quality_of_work', 'Quality of Work'),
        ('behaviour_with_superiors', 'Behaviour with Superiors'),
        ('interaction_with_colleagues', 'Interaction with Colleagues'),
        ('work_initiative_responsibility', 'Work Initiative & Responsibility'),
        ('capacity_to_learn_and_grow', 'Capacity to Learn and Grow'),
        ('stress_and_time_management', 'Stress and Time Management'),
        ('attendance_and_punctuality', 'Attendance and Punctuality'),
        ('compliance_with_company_policies', 'Compliance with Company Policies'),
    ]
    
    performance_categories = models.CharField(
        max_length=50,
        choices=PERFORMANCE_CATEGORY_CHOICES,
        null=True,
        blank=True,
        help_text="Performance evaluation categories"
    )
    
    sender = models.ForeignKey(
        HrmsUsers,
        related_name='feedback_sent',
        on_delete=models.CASCADE,
        help_text="User sending the feedback"
    )
    receiver = models.ForeignKey(
        Employees, 
        related_name='feedback_received', 
        on_delete=models.CASCADE,
        help_text="Employee receiving the feedback"
    )  
    project = models.ForeignKey(
        Projects, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Project for which feedback is given"
    )   
    message = models.TextField()
    rating = models.FloatField(default=0.0)
    categories = models.JSONField(
        null=True, 
        blank=True,
        help_text="Selected feedback categories/tags like Demo, Timelines, etc."
    )  
    sentiment_label = models.CharField(max_length=20, null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    sentiment_raw = models.JSONField(null=True, blank=True)
    sentiment_spans = models.JSONField(
        null=True, 
        blank=True,
        encoder=DjangoJSONEncoder,
        help_text="Sentiment analysis spans for text highlighting"
    )  
    CATEGORY_CHOICES = [
        ('constructive', 'Constructive'),  
        ('corrective', 'Corrective'),    
        ('warning', 'Warning'),          
        ('time_management', 'Time Management'),
    ]
    category = models.CharField(
        max_length=30, choices=CATEGORY_CHOICES, null=True, blank=True,
        help_text="Feedback category derived from sentiment (positive/corrective/negative)"
    )
    tone = models.CharField(
        max_length=50, null=True, blank=True,
        help_text="Tone of the feedback, e.g. encouraging, formal, direct"
    )
    strengths = models.JSONField(
        null=True, blank=True,
        help_text="List of positive aspects or skills identified in the feedback"
    )
    improvement_areas = models.JSONField(
        null=True, blank=True,
        help_text="List of improvement points identified in the feedback"
    )
    suggested_action = models.TextField(
        null=True, blank=True,
        help_text="Automatically generated suggestion for improvement or continuation"
    )
    IMPACT_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    impact_level = models.CharField(
        max_length=10, choices=IMPACT_LEVEL_CHOICES, null=True, blank=True,
        help_text="Impact or urgency level derived from feedback sentiment"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        sender_name = f"{self.sender.first_name} {self.sender.last_name}" if hasattr(self.sender, 'first_name') else self.sender.email
        receiver_name = f"{self.receiver.first_name} {self.receiver.last_name}"
        return f"Feedback({sender_name} -> {receiver_name})"

    def get_categories_display(self):
        """Returns human-readable category names"""
        if not self.categories:
            return []
        
        category_map = dict(self.FEEDBACK_CATEGORY_CHOICES)
        return [category_map.get(cat, cat) for cat in self.categories if cat in category_map]
    
    def get_performance_category_display(self):
        """Returns human-readable performance category name"""
        if not self.performance_categories:
            return None
        
        category_map = dict(self.PERFORMANCE_CATEGORY_CHOICES)
        return category_map.get(self.performance_categories, self.performance_categories)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"
        ordering = ['-created_at']


class WeeklyFeedbackSummary(models.Model):
    week_start_date = models.DateField()
    week_end_date = models.DateField()
    total_feedbacks = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    category_distribution = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    sentiment_distribution = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    daily_rating_trends = models.JSONField(default=list, encoder=DjangoJSONEncoder)  
    employee_id = models.IntegerField(null=True, blank=True)
    employee_name = models.CharField(max_length=255, null=True, blank=True)  
    feedback_report = models.JSONField(
        default=dict, 
        encoder=DjangoJSONEncoder,
        blank=True,
        help_text="Comprehensive feedback analysis report as JSON"
    )  
    strengths = models.JSONField(
        default=list, 
        encoder=DjangoJSONEncoder,
        blank=True, 
        help_text="List of identified strengths"
    )
    improvement_areas = models.JSONField(
        default=list, 
        encoder=DjangoJSONEncoder,
        blank=True, 
        help_text="List of improvement areas"
    )    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['week_start_date', 'week_end_date', 'employee_id']
        verbose_name_plural = "Weekly Feedback Summaries"
        ordering = ['-week_start_date']
    
    def __str__(self):
        if self.employee_name:
            return f"{self.employee_name} - {self.week_start_date} to {self.week_end_date}"
        return f"Organization Summary - {self.week_start_date} to {self.week_end_date}"

    def save(self, *args, **kwargs):
        """Ensure feedback_report is properly formatted before saving"""
        if isinstance(self.feedback_report, str):
            try:
                self.feedback_report = json.loads(self.feedback_report)
            except json.JSONDecodeError:
                self.feedback_report = {}
        super().save(*args, **kwargs)
    
    def get_feedback_report(self):
        """Safely get feedback report as dictionary"""
        if isinstance(self.feedback_report, str):
            try:
                return json.loads(self.feedback_report)
            except json.JSONDecodeError:
                return {}
        return self.feedback_report or {}


class MonthlyFeedbackSummary(models.Model):
    """Monthly feedback summary for admin dashboard"""
    month_start_date = models.DateField(help_text="First day of the month")
    month_end_date = models.DateField(help_text="Last day of the month")
    employee_id = models.IntegerField()
    employee_name = models.CharField(max_length=255)
    feedback_count = models.IntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    previous_month_rating = models.FloatField(null=True, blank=True)
    trend = models.CharField(
        max_length=20, 
        choices=[('improving', 'Improving'), ('declining', 'Declining'), ('stable', 'Stable')],
        default='stable'
    )
    category_breakdown = models.JSONField(default=dict, encoder=DjangoJSONEncoder)
    sentiment_breakdown = models.JSONField(default=dict, encoder=DjangoJSONEncoder)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)   
    class Meta:
        unique_together = ['month_start_date', 'employee_id']
        verbose_name_plural = "Monthly Feedback Summaries"
        ordering = ['-month_start_date', 'employee_name']
    
    def __str__(self):
        return f"{self.employee_name} - {self.month_start_date.strftime('%B %Y')}"
    
    @property
    def month_label(self):
        return self.month_start_date.strftime('%B %Y')
    
    @property
    def month_value(self):
        return self.month_start_date.strftime('%Y-%m')


def user_score_file_path(instance, filename):
    """File upload path for user score attachments"""
    ext = filename.split('.')[-1]
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S') 
    if instance.id:
        return f'user_scores/{instance.employee.id}/{instance.id}_{timestamp}.{ext}'
    return f'user_scores/{instance.employee.id}/{timestamp}.{ext}'


class UserScore(models.Model):
    """
    Model to track merit and demerit points for employees based on PMO Scoring Table
    Points are AUTOMATICALLY assigned based on selected category and action
    """
    CATEGORY_CHOICES = [
        ('task_leadership', 'Task Leadership in Critical Situations'),
        ('task_responsiveness', 'Task Responsiveness & Resolution'),
        ('technical_guidance', 'Technical Guidance'),
        ('team_communication', 'Team Communication and Collaboration'),
        ('organizational_skills', 'Organizational Skills'),
        ('work_standards', 'Adherence to Work Standards'),
    ]   
    ACTION_CHOICES = [
        ('leadership_critical_tasks', 'Taking ownership and completing critical tasks outside normal responsibilities'),
        ('leadership_failure', 'Failure to effectively manage additional responsibilities, causing delays'),
        ('response_individual', 'Prompt response to client inquiries regarding individual tasks outside of regular working hours'),
        ('resolution_individual', 'Timely resolution of any client concerns related to individual tasks during non-working hours'),
        ('response_team', 'Prompt response to client inquiries regarding team tasks outside of regular working hours'),
        ('resolution_team', 'Timely resolution of any client concerns related to team tasks during non-working hours'),
        ('mentorship_support', 'Providing mentorship or support to peers on complex tasks when needed, during non-working hours'),
        ('collaboration_failure', 'Failure to collaborate or assist team members as needed during non-working hours'),
        ('cross_department', 'Volunteering and completing tasks for cross-department collaborations during critical phases'),
        ('poor_collaboration', 'Poor collaboration impacting high-stakes outcomes'),
        ('positive_feedback', 'Positive client feedback on handling additional responsibilities'),
        ('negative_feedback', 'Negative client feedback on additional tasks or responsiveness'),
        ('proactive_prevention', 'Proactively preventing potential delays that would impact project criticality'),
        ('ineffective_management', 'Ineffective task management leading to team delays in high-criticality situations'),
        ('missing_work', 'Missing work without prior notice or reason'),
        ('repeated_delays', 'Repeated delays and bugs without a valid reason'),
        ('valuable_optimizations', 'Proposing valuable optimizations and leading implementation'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending Approval'),
        ('rejected', 'Rejected'),
        ('revoked', 'Revoked'),
    ]
    ACTION_POINTS_MAP = {
        'leadership_critical_tasks': {'merit': 20, 'demerit': 0},
        'leadership_failure': {'merit': 0, 'demerit': 5},
        'response_individual': {'merit': 5, 'demerit': 0},
        'resolution_individual': {'merit': 10, 'demerit': 0},
        'response_team': {'merit': 10, 'demerit': 0},
        'resolution_team': {'merit': 20, 'demerit': 0},
        'mentorship_support': {'merit': 15, 'demerit': 0},
        'collaboration_failure': {'merit': 0, 'demerit': 10},
        'cross_department': {'merit': 15, 'demerit': 0},
        'poor_collaboration': {'merit': 0, 'demerit': 10},
        'positive_feedback': {'merit': 10, 'demerit': 0},
        'negative_feedback': {'merit': 0, 'demerit': 15},
        'proactive_prevention': {'merit': 15, 'demerit': 0},
        'ineffective_management': {'merit': 0, 'demerit': 10},
        'missing_work': {'merit': 0, 'demerit': 10},
        'repeated_delays': {'merit': 0, 'demerit': 15},
        'valuable_optimizations': {'merit': 25, 'demerit': 0},
    }
    CATEGORY_ACTION_MAP = {
        'task_leadership': ['leadership_critical_tasks', 'leadership_failure'],
        'task_responsiveness': ['response_individual', 'resolution_individual', 
                               'response_team', 'resolution_team'],
        'technical_guidance': ['mentorship_support', 'collaboration_failure'],
        'team_communication': ['cross_department', 'poor_collaboration', 
                              'positive_feedback', 'negative_feedback'],
        'organizational_skills': ['proactive_prevention', 'ineffective_management'],
        'work_standards': ['missing_work', 'repeated_delays', 'valuable_optimizations'],
    }   
    employee = models.ForeignKey(
        'employees.Employees',
        related_name='scores_received',
        on_delete=models.CASCADE,
        help_text="Employee receiving the score"
    )   
    awarded_by = models.ForeignKey(
        HrmsUsers, 
        related_name='scores_awarded',
        on_delete=models.CASCADE,
        help_text="User who awarded the score"
    ) 
    project = models.ForeignKey(
        'projects.Projects',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Project for which score is awarded (optional)"
    )   
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        help_text="Main category from PMO Scoring Table"
    )   
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        help_text="Selected action/activity"
    )   
    action_display = models.CharField(
        max_length=255,
        blank=True,
        help_text="Display name of the selected action"
    )   
    merit_points = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(25)],
        help_text="Automatically assigned merit points"
    )   
    demerit_points = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text="Automatically assigned demerit points (stored as positive)"
    )   
    evidence = models.TextField(
        blank=True,
        help_text="Evidence or reference (JIRA ticket, email, document, etc.)"
    )   
    reference_file = models.FileField(
        upload_to=user_score_file_path,
        null=True,
        blank=True,
        max_length=500,
        help_text="Optional file upload for evidence (images, documents, etc.)"
    )  
    notes = models.TextField(
        blank=True,
        help_text="Additional comments or context"
    )   
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )  
    date_occurred = models.DateField(
        default=timezone.now,
        help_text="Date when the action occurred"
    )   
    date_awarded = models.DateTimeField(
        auto_now_add=True,
        help_text="Date when score was recorded"
    )   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Score"
        verbose_name_plural = "User Scores"
        ordering = ['-date_awarded', '-created_at']
        indexes = [
            models.Index(fields=['employee', 'category']),
            models.Index(fields=['status', 'date_awarded']),
        ]
    
    def __str__(self):
        awarded_by_name = f"{self.awarded_by.first_name} {self.awarded_by.last_name}" if hasattr(self.awarded_by, 'first_name') else self.awarded_by.email
        return f"{self.employee} - {self.get_category_display()}: {self.points_display} (by {awarded_by_name})"
    
    @property
    def total_points(self):
        """Calculate net points (merits - demerits)"""
        return self.merit_points - self.demerit_points
    
    @property
    def points_display(self):
        """Display points as +X or -Y"""
        if self.merit_points > 0:
            return f"+{self.merit_points}"
        elif self.demerit_points > 0:
            return f"-{self.demerit_points}"
        return "0"
    
    @classmethod
    def get_points_for_action(cls, action_code):
        """Get predefined points for a given action code"""
        points = cls.ACTION_POINTS_MAP.get(action_code, {'merit': 0, 'demerit': 0})
        display = dict(cls.ACTION_CHOICES).get(action_code, '')
        
        return {
            'merit_points': points['merit'],
            'demerit_points': points['demerit'],
            'action_display': display
        }
    
    @classmethod
    def get_actions_by_category(cls, category_code):
        """Get all actions for a specific category"""
        action_codes = cls.CATEGORY_ACTION_MAP.get(category_code, [])
        actions = []
        
        for code in action_codes:
            points = cls.ACTION_POINTS_MAP.get(code, {'merit': 0, 'demerit': 0})
            display = dict(cls.ACTION_CHOICES).get(code, '')
            
            points_display = f"+{points['merit']}" if points['merit'] > 0 else f"-{points['demerit']}" if points['demerit'] > 0 else "0"
            
            actions.append({
                'code': code,
                'display': display,
                'merit_points': points['merit'],
                'demerit_points': points['demerit'],
                'points_display': points_display
            })
        
        return actions
    
    def save(self, *args, **kwargs):
        """Automatically assign points based on selected action"""
        if self.action:
            points_info = self.get_points_for_action(self.action)
            
            self.merit_points = points_info['merit_points']
            self.demerit_points = points_info['demerit_points']
            
            if not self.action_display:
                self.action_display = points_info['action_display']
        
        if not self.category and self.action:
            for cat_code, actions_list in self.CATEGORY_ACTION_MAP.items():
                if self.action in actions_list:
                    self.category = cat_code
                    break
        
        super().save(*args, **kwargs)
