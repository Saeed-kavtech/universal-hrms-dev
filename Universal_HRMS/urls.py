from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings #add this
from django.conf.urls.static import static #add this
from .router import router


urlpatterns = [ 
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/hrms_user/', include('profiles_api.urls')),
    path('api/organizations/', include('organizations.urls')),
    path('api/organization/', include('departments.urls')),
    path('api/organization/positions/', include('positions.urls')),
    path('api/', include(router.urls)),
    path('api/jd/', include('jd.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/candidates/', include('candidates.urls')),
    path('api/assessments/', include('assessments.urls')),
    path("api/certification/", include('certifyskills.urls')),
    path('api/taskify/',include('taskify.urls')),
    path('api/ticket/',include('tickets.urls')),
    path('api/training/',include('training.urls')),
    path('api/employees/', include('employees.urls')),
    path('api/employee/', include('banks.urls')),
    path('api/emp/', include('institutes.urls')),
    path('api/employee/', include('companies.urls')),
    path('api/employee/', include('skills.urls')),

    path('api/courses/', include('courses.urls')),
    path('api/stages/', include('stages.urls')),
    path('api/procedure/types/', include('stages.urls')),

    path('api/email/templates/', include('email_templates.urls')),
    path('api/roles/', include('roles.urls')),
    path('api/evaluations/', include('evaluations.urls')), 
    path('api/interviews/', include('interviews.urls')), 
    path('api/time/intervals/', include('time_intervals.urls')),
    path('api/datahive/', include('datahive.urls')),
    path('api/', include('feedback.urls')),



    path('api/instructors/', include('instructors.urls')),
    path('api/applicants/', include('applicants.urls')),

    path('api/scores/', include('scores.urls')),
    path('api/', include('employees_attendance.urls')),
    path('api/', include('kind_notes.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/payroll/', include('payroll_compositions.urls')),
    path('api/evaluation/', include('performance_evaluation.urls')), 
    path('api/navigations/', include('navigations.urls')),
    path('api/', include('dashboards.urls')),
    path('api/jira/', include('jira.urls')),
    path('api/reimbursements/', include('reimbursements.urls')),
    path('api/course-applicant-emails/', include('course_applicant_emails.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/kpis/', include('kpis.urls')),
    path('api/', include('kav_apis.urls')),
    path('api/manuals/', include('manuals.urls')),
    path('api/kav_skills/', include('kav_skills.urls')),
    path('api/integrations/',include('integrations.urls')),
    path('api/meetings/',include('meetings.urls')),
    path('api/requisition/', include('Requisition.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
