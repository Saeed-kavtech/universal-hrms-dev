from django.urls import path
from .views import CourseApplicantsViewset
from .views_course_session_trainees import *
from .views_attendance import *
from .views import PreCourseApplicantDataView, CourseApplicantPortalViewset

urlpatterns = [    
    path('<course_session_id>/', CourseApplicantsViewset.as_view({'get': 'list', 'post': 'create'})),
    path('get/<course_applicant_id>/', CourseApplicantsViewset.as_view({'get': 'retrieve', 'patch': 'patch',  'destroy': 'delete'})),
    path('get/approval/<course_applicant_id>/', CourseApplicantsViewset.as_view({'patch': 'decision_by_management'})),
    path('multiple/<course_session_id>/', CourseApplicantsViewset.as_view({'post': 'multiple_applicant_selection'})),

    path('enrolled/as/trainee/<course_applicant_id>/', CourseSessionTraineesViewset.as_view({'post': 'create'})),
    path('multiple/trainees/<course_session_id>/', MultipleTraineeSelectionViewset.as_view({'post': 'create_multiple_trainees'})),
    path('trainee/<course_session_id>/', CourseSessionTraineesViewset.as_view({'get': 'list'})),
    path('trainee/data/<course_session_trainee_id>/', CourseSessionTraineesViewset.as_view({'get': 'retrieve', 'patch': 'patch',  'destroy': 'delete'})),
    path('waitlisted/list/<course_session_id>/', CourseSessionTraineesViewset.as_view({'get': 'waitlisted_applicant_list'})),
    path('rejected/list/<course_session_id>/', CourseSessionTraineesViewset.as_view({'get': 'rejected_applicant_list'})),


    path('trainee/start/lecture/<lecture_id>/', CourseSessionTraineeAttendanceViewset.as_view({'get': 'list', 'post': 'start_lecture'})),
    path('trainee/end/lecture/<lecture_id>/', CourseSessionTraineeAttendanceViewset.as_view({'get': 'end_lecture'})),
    path('trainee/lecture/attendance/<cst_attendance_id>/', CourseSessionTraineeAttendanceViewset.as_view({'get': 'retrieve', 'patch': 'patch',  'destroy': 'delete'})),

    #PRE DATA APIS
    path('pre/applicant/data/view/', PreCourseApplicantDataView.as_view()),
    path('pre/trainee/data/view/<course_session_id>/', PreCourseSessionTraineesDataView.as_view()),
    path('pre/attendance/data/view/<lecture_id>/', PreAttendanceDataView.as_view()),

    # employee apply to a course through ESS
    path('register/course_session/<course_session_id>/', CourseApplicantPortalViewset.as_view({'post': 'application_for_course'})),
    path('register/course_session/', CourseApplicantPortalViewset.as_view({'get': 'list'})),


]