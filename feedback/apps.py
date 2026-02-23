# from django.apps import AppConfig

# class FeedbackConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'feedback'    
#     def ready(self):
#         from .tasks import generate_weekly_summaries_background
#         generate_weekly_summaries_background(schedule=60*60*24*7)