from django.urls import path
from .views import *
from .views_contacts import *
from .views_emp_dependent import *
# from .views_emp_roles import EmployeeRolesViewset
from .views_project_roles import EmployeeProjectsRolesViewset, PreEmployeesProjectRoleDataView
from .views_system_roles import SystemRolesViewset

urlpatterns = [
    path('', EmployeeViewset.as_view({'get': 'list', 'post': 'create'})),
    path('<uuid>/', EmployeeViewset.as_view({'get': 'retrieve', 'patch': 'patch',  'destroy': 'delete'})),
    path('activate/<uuid>/', EmployeeViewset.as_view({'get': 'activate'})),
    path('generate/report/',EmployeeViewset.as_view({'get':'employee_report'})),
    path('<emp_uuid>/emergency/contact/', EmployeeEmergencyContactsViewset.as_view({'get':'list', 'post': 'create'})),
    path('<emp_uuid>/emergency/contact/<contact_id>/', EmployeeEmergencyContactsViewset.as_view({'get': 'retrieve',  'destroy': 'delete', 'patch': 'patch'})),
    path('pre/data/<org_id>/', PreEmployeesDataView.as_view()),

    # employee dependent url
    path('<emp_uuid>/dependent/contact/', EmployeeDependentViewset.as_view({'get': 'list', 'post': 'create'})),
    path('<emp_uuid>/dependent/contact/<dependent_id>/', EmployeeDependentViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'destroy': 'delete'})),

    # path('<emp_uuid>/roles/', EmployeeRolesViewset.as_view({'get': 'list', 'post': 'create'})),
    # path('roles/<emp_role_id>/', EmployeeRolesViewset.as_view({'get': 'retrieve', 'destroy': 'delete', 'patch': 'patch'})),
    # path('<emp_uuid>/multi/roles/', EmployeeRolesViewset.as_view({'patch': 'is_emp_multi_role'})), 

    path('projects/roles/data/', EmployeeProjectsRolesViewset.as_view({'post': 'create'})),
    path('projects/roles/<emp_role_id>/data/', EmployeeProjectsRolesViewset.as_view({'get': 'retrieve', 'patch': 'patch', 'delete': 'delete'})),
    path('<emp_uuid>/projects/roles/data/', EmployeeProjectsRolesViewset.as_view({'get': 'list'}), name="get_employee_projects"),
    path('projects/<project_id>/roles/data/', EmployeeProjectsRolesViewset.as_view({'get': 'get_emp_projects'}), name="get_employees_based_on_project"),
    path('pre/projects/roles/data/view/', PreEmployeesProjectRoleDataView.as_view()),

    path('pre/complete/data/<emp_uuid>/', PreEmployeesCompleteDataView.as_view()),
    path('pre/dependent/data/', PreEmployeeDependentView.as_view()),
    path('import/employee/data/updates/', EmployeeImportDataView.as_view({'get': 'update_import_employee_data'})),
    path('temp/queries/', EmployeeImportDataView.as_view({'get': 'temp_queries'})),
    # path('import/employee/data/', EmployeeImportDataView.as_view({'get': 'import_employee'})),
    # path('import/employee/data/update/', EmployeeImportDataView.as_view({'get': 'update_employee_data'})),

    # emp system role
    path('system/roles/', SystemRolesViewset.as_view({'post': 'create'})),
    path('required/fields/<pk>/',EmployeeViewset.as_view({'get':'emp_required_fields'})),
    path('system/roles/<role_id>/', SystemRolesViewset.as_view({'get': 'list'})),
    path('<user_id>/system/roles/', SystemRolesViewset.as_view({'delete': 'delete'})),
    path('pre/data/system/roles/', SystemRolesViewset.as_view({'get': 'predata'})),
    path('system/assign/admin/roles/', SystemRolesViewset.as_view({'create': 'admin_role'})),
    
    path('add/resume/', EmployeeResumeView.as_view({'post': 'create'})),
    path('view/resume/', EmployeeResumeView.as_view({'post' :'view'})),
]
