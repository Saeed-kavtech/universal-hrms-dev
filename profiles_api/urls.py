from django.urls import path
from .views import * 
from .views_users import * 
from .views_emp import HrmsUserProfileUpdatesViewset, ResetPassword

urlpatterns = [
    path('login/', HrmsUserLogin.as_view(), name="login"),
    path('logout/', HrmsUserLogout.as_view(), name="logout"),
    path('profile/', HrmsUserProfile.as_view(), name="profile"),
    path('change_password/', HrmsUserChangePassword().as_view(), name="change_password"),
    path('reset_password_email/', SendPasswordResetEmail().as_view(), name="reset_password_email"),
    path('reset_password/<uid>/<token>/',  HrmsUserResetPassword().as_view(), name="reset_password"),
    path('update/', HrmsUserUpdate.as_view(), name='update'),

    path('admin/registeration/', RegisterHrmsAdminView.as_view()),

    path('view/', HrmsUsersListView.as_view(), name="hrms_users_view"),

    path('<int:uid>/assign/organization/', OrganizationAssignmentViewset.as_view({'get': 'list'})),

    path('<int:uid>/assign/organization/<int:org_id>/', OrganizationAssignmentViewset.as_view({'get': 'retrieve', 'post': 'post'})),
    path('<int:uid>/assign/organization/to/subadmin/<int:org_id>/', OrganizationAssignmentViewset.as_view({'get':'get_subadminorganization_data','post': 'assign_org_subadmin'})),
    path('rud/operations/', HrmsUsersGenericView.as_view(), name="admin-RUD"),

    path('change/password/' , HrmsUserProfileUpdatesViewset.as_view({'post': 'create'})),
    path('profile/image/update/' , HrmsUserProfileUpdatesViewset.as_view({'patch': 'profile_update'})),
    path('reset/password/email/' , ResetPassword.as_view({'post': 'post_send_password_email'})),
    path('reset/password/<uid>/<token>/' , ResetPassword.as_view({'post': 'post_reset_password'})),

]
