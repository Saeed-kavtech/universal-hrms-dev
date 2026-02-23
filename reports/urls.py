# from django.urls import path
# from .views import GymAllowanceReportsViewset, MedicalAllowanceReportsViewset, LeavesReportsViewset
# from .views_organogram import OrganogramViewset

# urlpatterns = [    
#     path('analysis/gym/allowance/', GymAllowanceReportsViewset.as_view({'post': 'create'})),
#     path('analysis/medical/allowance/', MedicalAllowanceReportsViewset.as_view({'post': 'create'})),
#     path('analysis/employees/leaves/', LeavesReportsViewset.as_view({'post': 'create'})),
#     path('organogram/departments/', OrganogramViewset.as_view({'post': 'new_post_department_based_organogram'})),
#     path('organogram/projects/', OrganogramViewset.as_view({'post': 'post_project_based_organogram'})),
#     path('pre/data/',OrganogramViewset.as_view({'get': 'predata'}))
# ]



from django.urls import path
from .views import GymAllowanceReportsViewset, MedicalAllowanceReportsViewset, LeavesReportsViewset, LeavesSummaryReportsViewset
from .views_organogram import OrganogramViewset

urlpatterns = [    
    path('analysis/gym/allowance/', GymAllowanceReportsViewset.as_view({'post': 'create'})),
    path('analysis/medical/allowance/', MedicalAllowanceReportsViewset.as_view({'post': 'create'})),
    path('analysis/employees/leaves/', LeavesReportsViewset.as_view({'post': 'create'})),
    path('analysis/employees/leaves-summary/', LeavesSummaryReportsViewset.as_view({'post': 'create'})),  # This line
    path('organogram/departments/', OrganogramViewset.as_view({'post': 'new_post_department_based_organogram'})),
    path('organogram/projects/', OrganogramViewset.as_view({'post': 'post_project_based_organogram'})),
    path('pre/data/', OrganogramViewset.as_view({'get': 'predata'}))
]