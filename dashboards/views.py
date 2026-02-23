from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q
from helpers.custom_permissions import IsAuthenticated, TokenDataPermissions
from helpers.status_messages import success, exception, errorMessage, successMessageWithData
from helpers.decode_token import decodeToken
from instructors.models import CourseSessions
from instructors.serializers import SessionInstructorsSerializers, SessionInstructorsHomepageSerializers
from reimbursements.views_gym import GymStatusLogsViewset
from reimbursements.views_leaves import EmployeesOfficialHolidaysViewset, LeavesStatusLogsViewset
from reimbursements.views_medical import MedicalStatusLogsViewset
from .serializers import LearningAndDevelopmentDashboardSerializers

from applicants.models import CourseApplicants, CourseSessionTrainees, CourseSessionTraineeAttendance
from courses.models import Courses, Programs, Subjects
from courses.serializers import CoursesViewsetSerializers, ProgramsViewsetSerializers, SubjectsViewsetSerializers
from employees.models import Employees, EmployeeProjects, EmployeeRoles
from employees.serializers import EmployeeJDCMSerializer, ListEmployeeViewsetSerializers, EmployeeRolesViewsetSerializers
from employees_attendance.models import EmployeesAttendance, EmployeesAttendanceLabel
from employees_attendance.serializers import DashboardEmployeesAttendanceLabelSerializers, EmployeesAttendanceViewsetSerializers
from applicants.serializers import CourseApplicantsViewsetSerializers, CourseSessionTraineesViewsetSerializers
from applicants.serializers import CourseSessionTraineeAttendanceViewsetSerializers
from kind_notes.models import KindNotes
from kind_notes.serializers import KindNotesViewsetSerializers
from reimbursements.models import (
    EmployeeLeaveDates, EmployeesGymAllowance, EmployeesMedicalAllowance, EmployeeProvidentFunds,
    EmployeesLeaves, EmployeesLoan,EmployeesRemainingMedicalAllowance,EmployeeLeaveCalculations
)
from reimbursements.serializers import (
    DashboardEmployeesLeavesSerializers, EmployeesGymAllowanceSerializers, EmployeesMedicalAllowanceSerializers,
    EmployeeProvidentFundsSerializers, EmployeesLeavesSerializers, EmployeesLoanSerializers
)
from instructors.models import Lectures
from instructors.serializers import LecturesViewsetSerializers
import datetime
from django.db import connection
# Create your views here.
class LearningAndDevelopmentDashboardViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, TokenDataPermissions]

    def list(self, request, *args, **kwargs):
        try:
            organization_id = request.data.get('current_organization')
            obj = CourseSessions.objects.filter(is_active=True, course__organization=organization_id)
            serializer = LearningAndDevelopmentDashboardSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
 
    
    
    def get_dashboard_data(self, request, *args, **kwargs):
        try:
            organization_id = request.data.get('current_organization')

            # sessions data
            course_sessions = CourseSessions.objects.filter(course__organization=organization_id, is_active=True)
            total_sessions = course_sessions.count()
            completed_sessions = course_sessions.filter(session_status='Completed').count()
            ongoing_sessions = course_sessions.filter(session_status='InProgress').count()
            not_initiated_sessions = course_sessions.filter(session_status='Not initiated').count()

            # applicants data
            course_applicants = CourseApplicants.objects.filter(course__organization=organization_id, employee__is_active=True, is_active=True)
            total_applicants = course_applicants.count()
            unprocessed_applicants = course_applicants.filter(status=1).count()
            inprocess_applicants = course_applicants.filter(status=2).count()
            approved_applicants = course_applicants.filter(status=3).count()
            rejected_applicants = course_applicants.filter(status=4).count()
            waitlisted_applicants = course_applicants.filter(status=5).count()

            course_trainees = CourseSessionTrainees.objects.filter(course__organization=organization_id, course_applicant__employee__is_active=True, is_active=True)
            total_trainees = course_trainees.count()

            total_courses = Courses.objects.filter(organization=organization_id, is_active=True)
            total_courses = total_courses.count()

            session_list = []
            for session in course_sessions:
                session_id = session.id
                course_name = session.course.title
                total_session_applicants = course_applicants.filter(course_session=session_id).count()
                unprocessed_session_applicants = course_applicants.filter(course_session=session_id, status=1).count()
                inprocess_session_applicants = course_applicants.filter(course_session=session_id, status=2).count()
                approved_session_applicants = course_applicants.filter(course_session=session_id, status=3).count()
                rejected_session_applicants = course_applicants.filter(course_session=session_id, status=4).count()
                waitlisted_session_applicants = course_applicants.filter(course_session=session_id, status=5).count()
                total_session_trainees = course_trainees.filter(course_session=session_id).count()
                
                session_data = {
                    'session_id': session_id,
                    'session_name': course_name + ' (' + str(session.start_date) + ' - ' + str(session.end_date) + ')',
                    'total_session_applicants': total_session_applicants,
                    'unprocessed_session_applicants': unprocessed_session_applicants,
                    'inprocess_session_applicants': inprocess_session_applicants,
                    'approved_session_applicants': approved_session_applicants,
                    'rejected_session_applicants': rejected_session_applicants,
                    'waitlisted_session_applicants': waitlisted_session_applicants,
                    'total_session_trainees': total_session_trainees
                }
                session_list.append(session_data)

            data = {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'ongoing_sessions': ongoing_sessions,
                'not_initiated_sessions': not_initiated_sessions,
                'total_applicants': total_applicants,
                'unprocessed_applicants': unprocessed_applicants,
                'inprocess_applicants': inprocess_applicants,
                'approved_applicants': approved_applicants,
                'rejected_applicants': rejected_applicants,
                'waitlisted_applicants': waitlisted_applicants,
                'total_trainees': total_trainees,
                'total_courses': total_courses
            }
            
            return Response({'status': 200, 'data': data, 'session_data': session_list, 'message': 'Success'})
        except Exception as e:
            return exception(e)
        

class EmployeesDashboard(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, TokenDataPermissions]

    def list(self, request, *args, **kwargs):
        try:
            hrmsuser_id = request.user.id
            organization_id = request.data.get('current_organization')
            emp_query = Employees.objects.filter(hrmsuser=hrmsuser_id)
            if not emp_query.exists():
                return errorMessage('Employee is not registered')
            elif not emp_query.filter(is_active=True):
                return errorMessage('Employee is deactivated')
            emp = emp_query.get()
            emp_id = emp.id


            emp_serializer = ListEmployeeViewsetSerializers(emp_query, many=True)

            # all the attendance of a specific employee
            attendance_query = EmployeesAttendance.objects.filter(employee=emp_id, employee__organization=organization_id)
            attendance_serializer = EmployeesAttendanceViewsetSerializers(attendance_query, many=True)
            
            # Get the current date
            current_date = datetime.date.today()

            # Calculate the date 7 days ago
            seven_days_ago = current_date - datetime.timedelta(days=7)
        
            # Filter the attendance records for the employee in the last 7 days
            last_week_attendance = attendance_query.filter(date__range=[seven_days_ago, current_date], date__week_day__gte=2) 
            last_week_attendance_serializer = EmployeesAttendanceViewsetSerializers(last_week_attendance, many=True)

            # retrieve all the sessions
            cs_query = CourseSessions.objects.filter(course__organization=organization_id, is_active=True)
            cs_serializer = SessionInstructorsSerializers(cs_query, many=True)

            # session where applicant is not a trainee
            applicant_query = CourseApplicants.objects.filter(employee=emp_id, employee__organization=organization_id)
            applicant_serializer = CourseApplicantsViewsetSerializers(applicant_query.filter(is_trainee=False), many=True)

            # sessions where applicant is a trainee
            cst_query = CourseSessionTrainees.objects.filter(course_applicant__employee=emp_id, is_active=True)
            cst_serializer = CourseSessionTraineesViewsetSerializers(cst_query, many=True)

            # session in which employee can be registered
            unregistered_sessions = cs_query.exclude(id__in=applicant_query.values_list('course_session__id', flat=True), session_status = 'Complete')
            unregistered_sessions_serializer = SessionInstructorsSerializers(unregistered_sessions, many=True)

            # session where employee is registered
            registered_sessions = cs_query.filter(id__in=applicant_query.values_list('course_session__id', flat=True))
            registered_sessions_serializer = SessionInstructorsSerializers(registered_sessions, many=True)

            courses_query = Courses.objects.filter(organization=organization_id, is_active=True)
            courses_serializer = CoursesViewsetSerializers(courses_query, many=True)

            program_query = Programs.objects.filter(subject__organization=organization_id, is_active=True)
            program_serializer = ProgramsViewsetSerializers(program_query, many=True)

            subject_query = Subjects.objects.filter(organization=organization_id, is_active=True)
            subject_serializer = SubjectsViewsetSerializers(subject_query, many=True)

            lecture_attendance_query = CourseSessionTraineeAttendance.objects.filter(course_session_trainee__course_applicant__employee=emp_id, is_active=True)
            lecture_attendance_serializer = CourseSessionTraineeAttendanceViewsetSerializers(lecture_attendance_query, many=True)


            data = {
                'employee': emp_serializer.data,
                'attendance': attendance_serializer.data,
                'employee_last_week_attendance': last_week_attendance_serializer.data,
                'subjects': subject_serializer.data,
                'programs': program_serializer.data,
                'courses': courses_serializer.data,
                'session_instructors': cs_serializer.data,
                'applicant': applicant_serializer.data,
                'course_session_trainee': cst_serializer.data,
                'employee_lecture_attendance': lecture_attendance_serializer.data,
                'employee_registered_session': registered_sessions_serializer.data,
                'employee_unregistered_session': unregistered_sessions_serializer.data,
            }

            return success(data)
        except Exception as e:
            return exception(e)

    def get_homepage(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']

            # all the attendance of a specific employee
            attendance_query = EmployeesAttendance.objects.filter(
                employee=employee_id, employee__organization=organization_id
            )
            
            # Get the current date
            current_date = datetime.date.today()
            current_month = current_date.month
            current_year = current_date.year

            # Calculate the date 7 days ago
            seven_days_ago = current_date - datetime.timedelta(days=7)
        
            # Filter the attendance records for the employee in the last 7 days
            last_week_attendance = attendance_query.filter(date__range=[seven_days_ago, current_date]).order_by('-date')
            last_week_attendance_serializer = EmployeesAttendanceViewsetSerializers(last_week_attendance, many=True)


            kind_notes = KindNotes.objects.filter(created_at__date__range=[seven_days_ago, current_date], is_active=True)
            receiver_kind_notes = kind_notes.filter(receiver=employee_id).order_by('-id')
            sender_kind_notes =  kind_notes.filter(sender=employee_id).order_by('-id')
            receiver_kind_notes_serializer = KindNotesViewsetSerializers(receiver_kind_notes, many=True)
            sender_kind_notes_serializer = KindNotesViewsetSerializers(sender_kind_notes, many=True)

            gym = EmployeesGymAllowance.objects.filter(employee=employee_id, date__month=current_month, date__year=current_year, is_active=True)
            gym_serializer = EmployeesGymAllowanceSerializers(gym, many=True)

            medical = EmployeesMedicalAllowance.objects.filter(employee=employee_id, date__month=current_month, date__year=current_year, is_active=True)
            medical_serializer = EmployeesMedicalAllowanceSerializers(medical, many=True)

            pf = EmployeeProvidentFunds.objects.filter(employee=employee_id, is_active=True)
            pf_serializer = EmployeeProvidentFundsSerializers(pf, many=True)

            ten_days_after = current_date + datetime.timedelta(days=10)
            leaves = EmployeesLeaves.objects.filter(employee=employee_id,set_leave_duration__year=current_year,is_active=True).filter(
                Q(start_date__range=[current_date, ten_days_after]) |
                Q(end_date__range=[current_date, ten_days_after])
            ).order_by('-id')
            leaves_serializer = EmployeesLeavesSerializers(leaves, many=True)
            # next=current_year+1
            med_count = EmployeesRemainingMedicalAllowance.objects.filter(medical_allowance__isnull=False,medical_allowance__year=current_year,employee=employee_id, is_active=True)
            # print(med_count.values())
            med_remaining_leaves = med_count.values_list('remaining_allowance', flat=True).last() or 0
            med_allow_leaves = med_count.values_list('emp_yearly_limit', flat=True).last() or 0

            # Retrieve values from EmployeeLeaveCalculations
            upcoming_holiday=EmployeesOfficialHolidaysViewset().upcoming_holidays(organization_id)
            # order by leaveduration __ leave_type
            simple_count = EmployeeLeaveCalculations.objects.filter(employee=employee_id,set_leave_duration__year=current_year,is_active=True).values()
            # print(simple_count)
            result = simple_count.values('set_leave_duration__leave_types__id', 'set_leave_duration__leave_types__title','emp_yearly_leaves')
           
            leaves1=EmployeesLeaves.objects.filter(employee=employee_id,set_leave_duration__year=current_year, is_active=True,status="approved").values("leave_types_id","duration")
          
            
            leave_data_dict = {item['set_leave_duration__leave_types__id']: item for item in result}

            # Initialize a dictionary to store the final data
            leave_data_final = {}
            medical_count={}
            # Initialize a dictionary to keep track of the leaves used for each leave type
            leave_usage = {}
            # print(leave_data_dict)
    # Iterate through the 'result' queryset and calculate remaining leaves
            for leave_type_id, leave_info in leave_data_dict.items():
                # Check if the leave type ID exists in 'leaves1'
                matching_leaves = leaves1.filter(leave_types_id=leave_type_id)

                # Calculate total duration for this leave type
                total_duration = sum(matching_leave['duration'] for matching_leave in matching_leaves) or 0

                allowed_leaves = leave_info['emp_yearly_leaves'] or 0

                # Calculate remaining leaves, deducting used leaves
                remaining_leaves = allowed_leaves - total_duration

                # Check if there are additional records for the same leave type
                if remaining_leaves < 0:
                    # Use the original allowed value again
                    remaining_leaves = allowed_leaves

                # Create a dictionary entry with leave type, leave ID, remaining leaves, and total allowed leaves
                if leave_info['set_leave_duration__leave_types__title'] is not None and leave_info['set_leave_duration__leave_types__id'] is not None:
                    leave_data_final[leave_type_id] = {
                        'leave_type': leave_info['set_leave_duration__leave_types__title'],
                        'leave_id': leave_type_id,
                        'remaining_leaves': remaining_leaves,
                        'allowed_leaves': allowed_leaves,
                    }
              # Initialize a list to store the formatted leave data
            formatted_leave_data = []

            # Iterate through the leave_data_final dictionary and convert it into the desired format
            for leave_type_id, leave_data in leave_data_final.items():
                formatted_leave = {
                    "leave_type": leave_data["leave_type"],
                    "leave_id": leave_data["leave_id"],
                    "remaining_leaves": leave_data["remaining_leaves"],
                    "allowed_leaves": leave_data["allowed_leaves"],
                }
                formatted_leave_data.append(formatted_leave)

            
            # Now, formatted_result contains the desired format
            # print(formatted_leave_data)

            # print("Data:",data)
            if med_allow_leaves>0:
                medical_count = {
                    'remaining_allowance': med_remaining_leaves,
                    'emp_yearly_limit': med_allow_leaves,
                    
                }
            

            loan = EmployeesLoan.objects.filter(employee=employee_id, created_at__month=current_month, created_at__year=current_year, is_active=True)
            loan_serializer = EmployeesLoanSerializers(loan, many=True)
            # L&D module

            applicant = CourseApplicants.objects.filter(
                employee=employee_id, employee__organization=organization_id
            )          
            
            cs = CourseSessions.objects.filter(
                id__in=applicant.values('course_session'), 
                is_active=True, 
            ).filter(Q(session_status='InProgress') | Q(session_status='Not initiated'))

            cs_serializer = SessionInstructorsHomepageSerializers(cs, context = {'current_data': current_date}, many=True)

            lectures = Lectures.objects.filter(
                course_session_instructor__course_session__id__in=applicant.values('course_session'), 
                date=current_date
            )
            lectures_serializer = LecturesViewsetSerializers(lectures, many=True)

            # projects
            # employee_project = EmployeeProjects.objects.filter(
            #     employee=employee_id,
            #     employee__organization=organization_id,
            #     is_active=True,
            # )
            emp_project = EmployeeProjects.objects.filter(employee__organization=organization_id, is_active=True)
            emp_role_serializer = []
            if emp_project.exists():
                emp_role = EmployeeRoles.objects.filter(
                    employee_project__employee=employee_id,
                    is_active=True    
                )
                emp_role_serializer = EmployeeRolesViewsetSerializers(emp_role, many=True).data
                

            data = {
                'last_week_attendance': last_week_attendance_serializer.data,
                'receiver_kind_notes': receiver_kind_notes_serializer.data,
                'sender_kind_notes': sender_kind_notes_serializer.data,
                'gym': gym_serializer.data,
                'medical': medical_serializer.data,
                'provident_fund': pf_serializer.data,
                'leaves': leaves_serializer.data,
                'upcoming_holiday':upcoming_holiday,
                'loan': loan_serializer.data,
                "medical_count":medical_count,
                'Leaves_count':formatted_leave_data,
                'course_sessions': cs_serializer.data,
                'lectures': lectures_serializer.data,
                'employee_project_roles': emp_role_serializer,
            }

            return success(data)
        except Exception as e:
            return exception(e)
        
    def employee_joining_dates_dob(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            month=request.data.get("month",None)
            year=request.data.get("year",None)
            if month is None:
                date=datetime.datetime.today().date()
                # current_day = current_date.day
                month = date.month
                year=date.year
            joining_date_query = Employees.objects.filter(~Q(joining_date__year=year),joining_date__month=month,organization=organization_id, is_active=True)
            joining_date_serializer=EmployeeJDCMSerializer(joining_date_query, many=True, context={'include_joining_date': True})
            dob_query = Employees.objects.filter(dob__month=month,organization=organization_id, is_active=True)
            dob_serializer=EmployeeJDCMSerializer(dob_query, many=True, context={'include_dob': True})
            data_list={
                "joining_date_data":joining_date_serializer.data,
                "dob_data":dob_serializer.data
            }
            return success(data_list)
        except Exception as e:
            return exception(e)
    
    def pending_allowances(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pending_leaves=LeavesStatusLogsViewset().pending_leaves(organization_id)
            # print(pending_leaves)
            pending_medical=MedicalStatusLogsViewset().pending_medical(organization_id)
            pending_gym=GymStatusLogsViewset().pending_gym(organization_id)
            upcoming_holiday=EmployeesOfficialHolidaysViewset().upcoming_holidays(organization_id)
            
            data={
                "pending_leaves":pending_leaves,
                "pending_medical":pending_medical,
                "pending_gym":pending_gym,
                "upcoming_holiday":upcoming_holiday
            }

            return success(data)

            
        except Exception as e:
            return exception(e)
        
    
    def get_current_date_attendance(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            current_date=datetime.datetime.today().date()

            # all the attendance of a specific employee
            attendance_query = EmployeesAttendance.objects.filter(
                employee=employee_id,date=current_date,employee__organization=organization_id
            )

            total_time_formatted = '{:d}:{:02d}:{:02d}'.format(
                (total_seconds := sum(
                    (
                        (datetime.datetime.combine(datetime.date.fromisoformat(str(record.date)),
                                                    datetime.datetime.strptime(str(record.check_out), "%H:%M:%S").time())
                        - datetime.datetime.combine(datetime.date.fromisoformat(str(record.date)),
                                                    datetime.datetime.strptime(str(record.check_in), "%H:%M:%S").time())
                        ).seconds
                    )
                    for record in attendance_query
                    if record.check_in and record.check_out
                )) // 3600, (total_seconds % 3600) // 60, (total_seconds % 60)
            )
            

            emp_serializer = EmployeesAttendanceViewsetSerializers(attendance_query, many=True)

            data={
                "total_time":total_time_formatted,
                "data":emp_serializer.data,
            }

            return success(data)
               
        except  Exception as e:
            return exception(e)




    def today_attenadnce_leave_data(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            date=datetime.datetime.today().date()
            department=request.data.get("department",None)

            
            employee_count=Employees.objects.filter(organization=organization_id,is_active=True).count()
            employee_attendance=EmployeesAttendanceLabel.objects.filter(employee__organization=organization_id,date=date,is_active=True)
            employee_leave=EmployeeLeaveDates.objects.filter(employee_leave__employee__organization=organization_id,date=date,status='approved',is_active=True)
            if department is not None:
                employee_attendance=employee_attendance.filter(employee__department=department)
                employee_leave=employee_leave.filter(employee_leave__employee_department=department)
                
            attendance_serializer=DashboardEmployeesAttendanceLabelSerializers(employee_attendance,many=True)
            leave_serializer=DashboardEmployeesLeavesSerializers(employee_leave,many=True)
            data_list={
                "employee_count":employee_count,
                "attendance_data":attendance_serializer.data,
                "leave_data":leave_serializer.data
            }
            return success(data_list)


        except Exception as e:
            return exception(e)

    # def get_homepage(self, request, *args, **kwargs):
    #     try:
    #         token_data = decodeToken(self, self.request)
    #         organization_id = token_data['organization_id']
    #         employee_id = token_data['employee_id']

    #         # all the attendance of a specific employee
    #         attendance_query = EmployeesAttendance.objects.filter(
    #             employee=employee_id, employee__organization=organization_id
    #         )
            
    #         # Get the current date
    #         current_date = datetime.date.today()
    #         current_month = current_date.month
    #         current_year = current_date.year

    #         # Calculate the date 7 days ago
    #         seven_days_ago = current_date - datetime.timedelta(days=7)
        
    #         # Filter the attendance records for the employee in the last 7 days
    #         last_week_attendance = attendance_query.filter(date__range=[seven_days_ago, current_date]).order_by('-date')
    #         last_week_attendance_serializer = EmployeesAttendanceViewsetSerializers(last_week_attendance, many=True)


    #         kind_notes = KindNotes.objects.filter(created_at__date__range=[seven_days_ago, current_date], is_active=True)
    #         receiver_kind_notes = kind_notes.filter(receiver=employee_id).order_by('-id')
    #         sender_kind_notes =  kind_notes.filter(sender=employee_id).order_by('-id')
    #         receiver_kind_notes_serializer = KindNotesViewsetSerializers(receiver_kind_notes, many=True)
    #         sender_kind_notes_serializer = KindNotesViewsetSerializers(sender_kind_notes, many=True)

    #         gym = EmployeesGymAllowance.objects.filter(employee=employee_id, date__month=current_month, date__year=current_year, is_active=True)
    #         gym_serializer = EmployeesGymAllowanceSerializers(gym, many=True)

    #         medical = EmployeesMedicalAllowance.objects.filter(employee=employee_id, date__month=current_month, date__year=current_year, is_active=True)
    #         medical_serializer = EmployeesMedicalAllowanceSerializers(medical, many=True)

    #         pf = EmployeeProvidentFunds.objects.filter(employee=employee_id, is_active=True)
    #         pf_serializer = EmployeeProvidentFundsSerializers(pf, many=True)

    #         ten_days_after = current_date + datetime.timedelta(days=10)
    #         leaves = EmployeesLeaves.objects.filter(employee=employee_id, is_active=True).filter(
    #             Q(start_date__range=[current_date, ten_days_after]) |
    #             Q(end_date__range=[current_date, ten_days_after])
    #         ).order_by('-id')
    #         leaves_serializer = EmployeesLeavesSerializers(leaves, many=True)

    #         loan = EmployeesLoan.objects.filter(employee=employee_id, created_at__month=current_month, created_at__year=current_year, is_active=True)
    #         loan_serializer = EmployeesLoanSerializers(loan, many=True)
    #         # L&D module

    #         applicant = CourseApplicants.objects.filter(
    #             employee=employee_id, employee__organization=organization_id
    #         )          
            
    #         cs = CourseSessions.objects.filter(
    #             id__in=applicant.values('course_session'), 
    #             is_active=True, 
    #         ).filter(Q(session_status='InProgress') | Q(session_status='Not initiated'))

    #         cs_serializer = SessionInstructorsHomepageSerializers(cs, context = {'current_data': current_date}, many=True)

    #         lectures = Lectures.objects.filter(
    #             course_session_instructor__course_session__id__in=applicant.values('course_session'), 
    #             date=current_date
    #         )
    #         lectures_serializer = LecturesViewsetSerializers(lectures, many=True)

    #         # projects
    #         # employee_project = EmployeeProjects.objects.filter(
    #         #     employee=employee_id,
    #         #     employee__organization=organization_id,
    #         #     is_active=True,
    #         # )
    #         emp_project = EmployeeProjects.objects.filter(employee__organization=organization_id, is_active=True)
    #         emp_role_serializer = []
    #         if emp_project.exists():
    #             emp_role = EmployeeRoles.objects.filter(
    #                 employee_project__employee=employee_id,
    #                 is_active=True    
    #             )
    #             emp_role_serializer = EmployeeRolesViewsetSerializers(emp_role, many=True).data
                

    #         data = {
    #             'last_week_attendance': last_week_attendance_serializer.data,
    #             'receiver_kind_notes': receiver_kind_notes_serializer.data,
    #             'sender_kind_notes': sender_kind_notes_serializer.data,
    #             'gym': gym_serializer.data,
    #             'medical': medical_serializer.data,
    #             'provident_fund': pf_serializer.data,
    #             'leaves': leaves_serializer.data,
    #             'loan': loan_serializer.data,
    #             'course_sessions': cs_serializer.data,
    #             'lectures': lectures_serializer.data,
    #             'employee_project_roles': emp_role_serializer,
    #         }

    #         return success(data)
    #     except Exception as e:
    #         return exception(e)
    