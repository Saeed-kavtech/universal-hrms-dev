from datahive.views import CategoriesViewset
from interviews.views import InterviewMediumViewSet
from organizations.views import OrganizationViewset
from jd.views_jds import JdTypesViewset, JdDimensionsViewset
from jobs.views import JobTypesViewset
from candidates.views import RecruitmentStagesViewSet
from assessments.views import *
from rest_framework import routers
from email_templates.views import EmailRecipientsViewset
from employees.views_emp_routers import *
from banks.views import *
from institutes.views import DegreeTypesViewset, InstitutesViewset
from companies.views import CompaniesViewset
from skills.views import SkillCategoriesViewset, SkillsViewset, ProficiencyLevelsViewset
from employees.views_emp_dependent import DependentViewset
from courses.subject_types_routers import SubjectTypesViewset
from email_templates.views import TemplateVariablesViewset
from instructors.views import ModeOfInstructionsViewset
from instructors.views import CourseSessionTypesViewset
from roles.views import RoleTypesViewset
from reimbursements.views_loan import LoanTypesViewset, PurposeOfLoansViewset, TimeFrequencyViewset, TimePeriodViewset
from employees_attendance.views import AttendanceMachinesViewset,MyModelViewSet
from kpis.views import KpisObjectivesViewset, KpisStatusViewset,StatusGroupViewset, EPTypesViewset, EPComplexityViewset, EPScalingViewset,ScaleComplexityViewset
from manuals.views import ManualTypesViewsets
from kav_skills.views import SkillTypesViewset
from performance_configuration.views import *
from payroll_compositions.views import CustomizedAttribuesViewset, ValueTypeChoicesViewset
from Requisition.views import ReplacementForViewset
from logs.views import *
from taskify.views import *
from tickets.views import *
from reimbursements.views_wfh import *
router = routers.DefaultRouter()
router.register(r'organizations', OrganizationViewset, basename='organization')

router.register(r'jd/types', JdTypesViewset, basename='jd_types')
router.register(r'jd/dimensions', JdDimensionsViewset, basename='jd_dimension')
router.register(r'recruitment/stages', RecruitmentStagesViewSet, basename='recruitment_stages')

router.register(r'job/types', JobTypesViewset, basename='job_types')

# Assessment Test Routes
router.register(r'assessment/types', AssessmentTypesViewset, basename='assessment_types')
router.register(r'assessment/tests', AssessmentTestsViewset, basename='assessment_tests')

#Email Templates Routes
router.register(r'email/template/variables', TemplateVariablesViewset, basename='assessment_types')
router.register(r'email/recipients',EmailRecipientsViewset)

# From Employee App
router.register(r'employees/types', EmployeeTypesViewset)
router.register(r'employees/attachment/types', AttachmentTypesViewset)
router.register(r'employees/contact/relations', ContactRelationsViewset)


router.register(r'banks', BanksViewset) 

router.register(r'employees/institutes', InstitutesViewset)
router.register(r'employees/degree/types', DegreeTypesViewset)

router.register(r'companies', CompaniesViewset)

router.register(r'skills/categories', SkillCategoriesViewset)
router.register(r'skills/proficiency/level', ProficiencyLevelsViewset)
router.register(r'skills', SkillsViewset)

router.register(r'employee/dependents', DependentViewset)

router.register(r'attendance/machines', AttendanceMachinesViewset, basename='attendance_machines')
router.register(r'attendance/hoilday', MyModelViewSet)

router.register(r'roles/types', RoleTypesViewset, basename="roles_type")

# courses app
router.register(r'subjects', SubjectTypesViewset)
router.register(r'mode/of/instructions', ModeOfInstructionsViewset)
router.register(r'course/session/types', CourseSessionTypesViewset)

router.register(r'set/loan/types', LoanTypesViewset)
router.register(r'set/purpose/of/loan', PurposeOfLoansViewset)
router.register(r'set/time/frequency', TimeFrequencyViewset)
router.register(r'set/time/period', TimePeriodViewset)

# kpis
router.register(r'kpis/types', EPTypesViewset)
router.register(r'kpis/scaling', EPScalingViewset)
router.register(r'kpis/status', KpisStatusViewset)
router.register(r'kpis/group', StatusGroupViewset)
router.register(r'kpis/complexity', EPComplexityViewset)
router.register(r'kpis/scale_complexity', ScaleComplexityViewset)
router.register(r'manual/types', ManualTypesViewsets)
router.register(r'kav_skills/types', SkillTypesViewset)
router.register(r'kpis/objectives', KpisObjectivesViewset)

#kpis Configuration

router.register(r'configuration/scalegroups', ScaleGroupsViewset)
router.register(r'configuration/scalerating', ScaleRatingViewset)
router.register(r'configuration/groupaspects', GroupAspectsViewset)
router.register(r'configuration/aspectsparameters', AspectsParametersViewset)

# # Payroll
router.register(r'payroll_compositions/customizedpayrollattributes', CustomizedAttribuesViewset)
router.register(r'payroll_compositions/valueTypechoices', ValueTypeChoicesViewset)

# Organization Bank Detail 
router.register(r'OrganizationBankDetail', OrganizationBankDetailViewset, basename='organization-bank-detail') 

#interviews
router.register(r'interview/medium', InterviewMediumViewSet)
# router.register(r'meeting/category', MeetingCategoryViewset)

# Requisition
router.register(r'requisition/replacement', ReplacementForViewset)

#Taskify
router.register(r'taskify/status',TasksStatusViewset)
router.register(r'taskify/type',TaskTypesViewset)
#Ticket
router.register(r'ticket/category',TicketCategoryViewset)
router.register(r'ticket/category_department',TicketCategoryDepartmentViewset)
router.register(r'ticket/department_employee',TicketDepartmentEmployeeViewset)

#Reimbursements
router.register(r'reimbursements/wfh/allowance',EmployeeWFHAllowanceviewset)

#Datahive
router.register(r'datahive/categories',CategoriesViewset)



urlpatterns = router.urls