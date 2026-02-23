from django.urls import path
from .views import CourseApplicantCustomEmailsViewset

urlpatterns = [    
    path('', CourseApplicantCustomEmailsViewset.as_view({'get': 'list', 'post': 'create'})),
    path('get/<course_applicant_id>/', CourseApplicantCustomEmailsViewset.as_view({'get': 'get_list_of_applicant'})),
    # path('<course_session_id>/', CourseApplicantCustomEmailsViewset.as_view({'get': 'get_email_list_against_course_session'})),
]