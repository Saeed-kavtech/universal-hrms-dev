from django.urls import path
from .views import InstructorViewset, PreCompleteInstructorDataView
from .views_lectures import LecturesViewset, PreLecturesDataView
from .views_session_instructors import SessionInstructorsViewset, PreSessionInstructorsDataView

urlpatterns = [
    path('', InstructorViewset.as_view({'get': 'list', 'post': 'create'})),

    path('session/', SessionInstructorsViewset.as_view({'post': 'create', 'get': 'list'})),
    path('session/<course_session_id>/', SessionInstructorsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),

    path('lectures/<course_session_id>/', LecturesViewset.as_view({'get': 'list', 'post': 'create'})),
    path('get/all/lectures/', LecturesViewset.as_view({'get': 'listAllLectures'})),
    path('lectures/manage/<lecture_id>/', LecturesViewset.as_view({'get': 'retrieve', 'patch': 'patch',  'destroy': 'delete'})),
    
    path('pre/lectures/data/view/', PreLecturesDataView.as_view()), 
    path('pre/course/sessions/data/view/', PreSessionInstructorsDataView.as_view()),
    path('pre/complete/data/view/', PreCompleteInstructorDataView.as_view()),    

    path('<slug>/<uuid>/', InstructorViewset.as_view({'get': 'retrieve', 'patch': 'patch',  'destroy': 'delete'})),
]