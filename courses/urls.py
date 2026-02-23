from django.urls import path
from .subjects_views import *
from .programs_views import *
from .pre_requisite_views import *
from .skills_views import *
from .topics_views import *
from .modules_views import *
from .views import *

urlpatterns = [
    path('subjects/', SubjectsViewset.as_view({'post': 'create', 'get': 'list'})),
    path('subjects/<slug>/<uuid>/', SubjectsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),

    path('programs/', ProgramsViewset.as_view({'post': 'create', 'get': 'list'})),
    path('programs/<slug>/<uuid>/', ProgramsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),

    path('', CoursesViewset.as_view({'post': 'create', 'get': 'list'})),
    path('<slug>/<uuid>/', CoursesViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),
    path('<course_id>/session/data/', CoursesViewset.as_view({'get': 'get_session_courses'})),

    path('complete/course/plan/',CoursesViewset.as_view({'get':'get_course_data','post':'course_creation'})),
    path('complete/course/plan/<pk>/',CoursesViewset.as_view({'patch':'course_creation_update','delete':'course_creation_delete'})),
    
    
    path('details/<slug>/<uuid>/pre/requisite/', CoursePreRequisiteViewset.as_view({'post': 'create', 'get': 'list'})),
    path('details/<slug>/<uuid>/pre/requisite/<pre_req>/', CoursePreRequisiteViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),

    path('details/<slug>/<uuid>/skills/', CourseSkillsViewset.as_view({'post': 'create', 'get': 'list'})),
    path('details/<slug>/<uuid>/skills/<skill_id>/', CourseSkillsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),


    path('details/<slug>/<uuid>/modules/', CourseModulesViewset.as_view({'post': 'create', 'get': 'list'})),
    path('details/<slug>/<uuid>/modules/<module_id>/', CourseModulesViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),

    path('details/module/<module_id>/topics/', ModuleTopicsViewset.as_view({'post': 'create', 'get': 'list'})),
    path('details/module/<module_id>/topics/<topic_id>/', ModuleTopicsViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})), 

    path('pre/complete/data/view/<course_slug>/<course_uuid>/', PreCourseCompleteDataView.as_view()),
    
    path('pre/course/data/view/', PreCourseDataView.as_view()),
    path('pre/program/data/view/', PreProgramDataView.as_view()),

]