# from rest_framework import viewsets
# from helpers.custom_permissions import IsAuthenticated
# from reimbursements.serializers import (
#     EmployeesGymAllowanceSerializers, EmployeesMedicalAllowanceSerializers, EmployeesLeavesSerializers
# )
# from reimbursements.models import (
#     EmployeesGymAllowance, EmployeesMedicalAllowance, EmployeesLeaves
# )
# from helpers.status_messages import exception, errorMessage, success
# from helpers.decode_token import decodeToken
# import datetime

# class GymAllowanceReportsViewset(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = EmployeesGymAllowance.objects.all()
#     serializer_class = EmployeesGymAllowanceSerializers

#     def create(self, request, *args, **kwargs):
#         try:
#             organization_id = decodeToken(self, self.request)['organization_id']
#             start_date = request.data.get('start_date', None)
#             end_date = request.data.get('end_date', datetime.date.today())
#             status = request.data.get('status', None)
#             is_active = request.data.get('is_active', True)

#             end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d').date()
#             end_month = end_date.month
#             end_year = end_date.year

#             query = self.queryset.filter(employee__organization = organization_id, is_active=is_active).order_by('date')
            
#             if start_date:
#                 start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d').date()
#                 start_month = start_date.month
#                 start_year = start_date.year
                
#                 if end_date < start_date:
#                     return errorMessage('End date should be greater than start date')
                
#                 query = query.filter(
#                         date__month__gte = start_month,
#                         date__month__lte = end_month,
#                         date__year__gte = start_year,
#                         date__year__lte = end_year, 
#                     )
#             else:
#                 query = self.queryset.filter(
#                     date__month = end_month,
#                     date__year = end_year,
#                 )

#             if status:
#                 query = query.filter(status = status) 

#             serializer = self.serializer_class(query, many=True)

#             return success(serializer.data)
#         except Exception as e:
#             return exception(e)
        

# class MedicalAllowanceReportsViewset(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = EmployeesMedicalAllowance.objects.all()
#     serializer_class = EmployeesMedicalAllowanceSerializers

#     def create(self, request, *args, **kwargs):
#         try:
#             organization_id = decodeToken(self, self.request)['organization_id']
#             start_date = request.data.get('start_date', None)
#             end_date = request.data.get('end_date', datetime.date.today())
#             status = request.data.get('status', None)
#             is_active = request.data.get('is_active', True)

#             end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d').date()
#             end_month = end_date.month
#             end_year = end_date.year

#             query = self.queryset.filter(employee__organization = organization_id, is_active=is_active).order_by('date')
            
#             if start_date:
#                 start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d').date()
#                 start_month = start_date.month
#                 start_year = start_date.year

#                 if end_date < start_date:
#                     return errorMessage('End date should be greater than start date')
                
#                 query = query.filter(
#                         date__month__gte = start_month,
#                         date__month__lte = end_month,
#                         date__year__gte = start_year,
#                         date__year__lte = end_year, 
#                     )

#             if status:
#                 query = query.filter(status = status) 

#             serializer = self.serializer_class(query, many=True)

#             return success(serializer.data)
#         except Exception as e:
#             return exception(e)
        

    
# class LeavesReportsViewset(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = EmployeesLeaves.objects.all()
#     serializer_class = EmployeesLeavesSerializers

#     def create(self, request, *args, **kwargs):
#         try:
#             organization_id = decodeToken(self, self.request)['organization_id']
#             start_date = request.data.get('start_date', None)
#             end_date = request.data.get('end_date', datetime.date.today())
#             status = request.data.get('status', None)
#             is_active = request.data.get('is_active', True)

#             end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d').date()

#             query = self.queryset.filter(employee__organization = organization_id, is_active=is_active).order_by('start_date')
            
#             if start_date:
#                 start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d').date()

#                 if end_date < start_date:
#                     return errorMessage('End date should be greater than start date')
                
#                 query = query.filter(   
#                     start_date__gte = start_date,
#                     start_date__lte = end_date,                                     
#                 )

#             if status:
#                 query = query.filter(status = status) 

#             serializer = self.serializer_class(query, many=True)

#             return success(serializer.data)
#         except Exception as e:
#             return exception(e)
        



from rest_framework import viewsets
from helpers.custom_permissions import IsAuthenticated
from employees.models import Employees, EmployeeTypes
from reimbursements.serializers import (
    EmployeesGymAllowanceSerializers, EmployeesMedicalAllowanceSerializers, EmployeesLeavesSerializers, ListEmployeeLeaveDateSerializers
)
from reimbursements.models import (
    EmployeeLeaveCalculations, EmployeesGymAllowance, EmployeesMedicalAllowance, EmployeesLeaves, LeaveTypes, SetLeavesDuration
)
from helpers.status_messages import exception, errorMessage, success
from helpers.decode_token import decodeToken
import datetime
from django.db.models import Count, Sum

class GymAllowanceReportsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EmployeesGymAllowance.objects.all()
    serializer_class = EmployeesGymAllowanceSerializers

    def create(self, request, *args, **kwargs):
        try:
            # print("DEBUG: Received request data:", request.data)
            
            organization_id = decodeToken(self, self.request)['organization_id']
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date', str(datetime.date.today()))
            status_val = request.data.get('status')  # Changed variable name
            employee_id = request.data.get('employee_id')
            is_active = request.data.get('is_active', True)

            # print(f"DEBUG: employee_id received: {employee_id}, type: {type(employee_id)}")
            
            # Parse end_date
            end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d').date()
            end_month = end_date.month
            end_year = end_date.year

            # Start with base query
            query = EmployeesGymAllowance.objects.filter(
                employee__organization=organization_id, 
                is_active=is_active
            )
            
            # CRITICAL: Filter by employee_id if provided
            if employee_id and employee_id != '' and employee_id != 'undefined':
                try:
                    employee_id_int = int(employee_id)
                    query = query.filter(employee_id=employee_id_int)
                    # print(f"DEBUG: Filtering by employee_id: {employee_id_int}")
                except (ValueError, TypeError) as e:
                    # print(f"DEBUG: Invalid employee_id: {employee_id}, error: {e}")
                    return errorMessage('Invalid employee_id format')
            
            # Date filtering
            if start_date and start_date != '':
                start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d').date()
                start_month = start_date.month
                start_year = start_date.year
                
                if end_date < start_date:
                    return errorMessage('End date should be greater than start date')
                
                query = query.filter(
                    date__month__gte=start_month,
                    date__month__lte=end_month,
                    date__year__gte=start_year,
                    date__year__lte=end_year,
                )
                # print(f"DEBUG: Date range filter applied: {start_date} to {end_date}")
            else:
                query = query.filter(
                    date__month=end_month,
                    date__year=end_year,
                )
                # print(f"DEBUG: Single month filter applied: {end_month}/{end_year}")

            # Status filtering
            if status_val and status_val != '':
                query = query.filter(status=status_val)
                # print(f"DEBUG: Status filter applied: {status_val}")
                
            # Order the results
            query = query.order_by('date')
            
            # print(f"DEBUG: Final query count: {query.count()}")

            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            # print(f"DEBUG: Exception occurred: {str(e)}")
            return exception(e)

class MedicalAllowanceReportsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EmployeesMedicalAllowance.objects.all()
    serializer_class = EmployeesMedicalAllowanceSerializers

    def create(self, request, *args, **kwargs):
        try:
            # print("DEBUG: Received request data:", request.data)
            
            organization_id = decodeToken(self, self.request)['organization_id']
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date', str(datetime.date.today()))
            status_val = request.data.get('status')  # Changed variable name
            employee_id = request.data.get('employee_id')
            is_active = request.data.get('is_active', True)

            # print(f"DEBUG: employee_id received: {employee_id}, type: {type(employee_id)}")
            
            end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d').date()
            end_month = end_date.month
            end_year = end_date.year

            # Start with base query
            query = EmployeesMedicalAllowance.objects.filter(
                employee__organization=organization_id, 
                is_active=is_active
            )
            
            # CRITICAL: Filter by employee_id
            if employee_id and employee_id != '' and employee_id != 'undefined':
                try:
                    employee_id_int = int(employee_id)
                    query = query.filter(employee_id=employee_id_int)
                    # print(f"DEBUG: Filtering by employee_id: {employee_id_int}")
                except (ValueError, TypeError) as e:
                    # print(f"DEBUG: Invalid employee_id: {employee_id}, error: {e}")
                    return errorMessage('Invalid employee_id format')
            
            # Date filtering
            if start_date and start_date != '':
                start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d').date()
                start_month = start_date.month
                start_year = start_date.year

                if end_date < start_date:
                    return errorMessage('End date should be greater than start date')
                
                query = query.filter(
                    date__month__gte=start_month,
                    date__month__lte=end_month,
                    date__year__gte=start_year,
                    date__year__lte=end_year, 
                )
                # print(f"DEBUG: Date range filter applied: {start_date} to {end_date}")
            else:
                query = query.filter(
                    date__month=end_month,
                    date__year=end_year,
                )
                # print(f"DEBUG: Single month filter applied: {end_month}/{end_year}")

            # Status filtering
            if status_val and status_val != '':
                query = query.filter(status=status_val)
                # print(f"DEBUG: Status filter applied: {status_val}")
            
            # Ordering
            query = query.order_by('date')
            
            # print(f"DEBUG: Final query count: {query.count()}")

            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            # print(f"DEBUG: Exception occurred: {str(e)}")
            return exception(e)

class LeavesReportsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EmployeesLeaves.objects.all()
    serializer_class = EmployeesLeavesSerializers

    def create(self, request, *args, **kwargs):

        try:
            # print("DEBUG: Received request data:", request.data)
            
            organization_id = decodeToken(self, self.request)['organization_id']
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date', str(datetime.date.today()))
            status_val = request.data.get('status')  # Changed variable name
            employee_id = request.data.get('employee_id')
            is_active = request.data.get('is_active', True)

            # print(f"DEBUG: employee_id received: {employee_id}, type: {type(employee_id)}")
            
            end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d').date()

            # Start with base query
            query = EmployeesLeaves.objects.filter(
                employee__organization=organization_id, 
                is_active=is_active
            )
            
            # CRITICAL: Filter by employee_id
            if employee_id and employee_id != '' and employee_id != 'undefined':
                try:
                    employee_id_int = int(employee_id)
                    query = query.filter(employee_id=employee_id_int)
                    # print(f"DEBUG: Filtering by employee_id: {employee_id_int}")
                except (ValueError, TypeError) as e:
                    # print(f"DEBUG: Invalid employee_id: {employee_id}, error: {e}")
                    return errorMessage('Invalid employee_id format')
            
            # Date filtering
            if start_date and start_date != '':
                start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d').date()

                if end_date < start_date:
                    return errorMessage('End date should be greater than start date')
                
                query = query.filter(   
                    start_date__gte=start_date,
                    start_date__lte=end_date,                                     
                )
                print(f"DEBUG: Date range filter applied: {start_date} to {end_date}")
            else:
                query = query.filter(start_date__lte=end_date)
                # print(f"DEBUG: Filter by end_date only: {end_date}")

            # Status filtering
            if status_val and status_val != '':
                query = query.filter(status=status_val)
                # print(f"DEBUG: Status filter applied: {status_val}")
            
            # Ordering
            query = query.order_by('start_date')

            # query = query.values(
            #     'employee_id',
            #     'status'
            # ).annotate(
            #     total_leaves=Count('id')
            # ).order_by(
            #     'employee_id',
            #     'status'
            # )
            
            # print(f"DEBUG: Final query count: {query}")
            # returnssss

            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            # print(f"DEBUG: Exception occurred: {str(e)}")
            return exception(e)
        
# Added this new view for Leaves Types details on admin site List Report 25_12_2025
class LeavesSummaryReportsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            employee_id = request.data.get('employee_id')
            year = request.data.get('year', datetime.date.today().year)
            
            if not employee_id:
                return errorMessage('Employee ID is required')
            
            try:
                employee = Employees.objects.get(
                    id=int(employee_id),
                    organization=organization_id,
                    is_active=True
                )
            except Employees.DoesNotExist:
                return errorMessage('Employee not found')
            
            year_int = int(year)
            summary_data = []
            processed_leave_types = set()
            
            # First, try to get data from EmployeeLeaveCalculations
            calculations = EmployeeLeaveCalculations.objects.filter(
                employee=employee,
                set_leave_duration__year=year_int,
                is_active=True
            ).select_related('set_leave_duration', 'set_leave_duration__leave_types')
            
            for calc in calculations:
                if not calc.set_leave_duration or not calc.set_leave_duration.leave_types:
                    continue
                    
                leave_type = calc.set_leave_duration.leave_types
                leave_type_id = leave_type.id
                
                if leave_type_id in processed_leave_types:
                    continue
                
                # Check staff classification
                if leave_type.is_staff_classification:
                    if not calc.set_leave_duration.staff_classification or calc.set_leave_duration.staff_classification != employee.staff_classification:
                        continue
                
                # Get approved leaves for date ranges
                approved_leaves_query = EmployeesLeaves.objects.filter(
                    employee=employee,
                    leave_types=leave_type,
                    start_date__year=year_int,
                    status='approved',
                    is_active=True
                )
                
                # Get date ranges - FIXED HERE
                date_ranges = []
                for leave in approved_leaves_query.order_by('start_date'):
                    if leave.start_date == leave.end_date:
                        date_ranges.append(leave.start_date.strftime('%Y-%m-%d'))
                    else:
                        date_ranges.append(f"{leave.start_date.strftime('%Y-%m-%d')} to {leave.end_date.strftime('%Y-%m-%d')}")
                
                # Use calculation data
                allocated_leaves = calc.emp_yearly_leaves or 0
                consumed_leaves = calc.approved_leaves or 0
                remaining_leaves = calc.remaining_leaves or 0
                
                summary_data.append({
                    'leave_type_id': leave_type_id,
                    'leave_type_title': leave_type.title,
                    'allocated_leaves': allocated_leaves,
                    'consumed_leaves': consumed_leaves,
                    'remaining_leaves': remaining_leaves,
                    'date_ranges': date_ranges[:6],  # First 5 for display
                    'total_date_ranges': len(date_ranges),  # Total count
                    'employee_name': employee.name,
                    'employee_id': employee.id
                })
                
                processed_leave_types.add(leave_type_id)
            
            # If no calculations found, fall back to SetLeavesDuration
            if not summary_data:
                set_leaves = SetLeavesDuration.objects.filter(
                    year=year_int,
                    is_active=True
                ).select_related('leave_types')
                
                for sl in set_leaves:
                    if not sl.leave_types:
                        continue
                    
                    leave_type = sl.leave_types
                    leave_type_id = leave_type.id
                    
                    if leave_type_id in processed_leave_types:
                        continue
                    
                    # Check staff classification
                    if leave_type.is_staff_classification:
                        if not sl.staff_classification or sl.staff_classification != employee.staff_classification:
                            continue
                    
                    # Get approved leaves
                    approved_leaves_query = EmployeesLeaves.objects.filter(
                        employee=employee,
                        leave_types=leave_type,
                        start_date__year=year_int,
                        status='approved',
                        is_active=True
                    )
                    
                    consumed_leaves = approved_leaves_query.aggregate(
                        total=Sum('duration')
                    )['total'] or 0
                    
                    # Get date ranges
                    date_ranges = []
                    for leave in approved_leaves_query.order_by('start_date'):
                        if leave.start_date == leave.end_date:
                            date_ranges.append(leave.start_date.strftime('%Y-%m-%d'))
                        else:
                            date_ranges.append(f"{leave.start_date.strftime('%Y-%m-%d')} to {leave.end_date.strftime('%Y-%m-%d')}")
                    
                    summary_data.append({
                        'leave_type_id': leave_type_id,
                        'leave_type_title': leave_type.title,
                        'allocated_leaves': sl.allowed_leaves,
                        'consumed_leaves': consumed_leaves,
                        'remaining_leaves': sl.allowed_leaves - consumed_leaves,
                        'date_ranges': date_ranges[:5],
                        'total_date_ranges': len(date_ranges),
                        'employee_name': employee.name,
                        'employee_id': employee.id
                    })
                    
                    processed_leave_types.add(leave_type_id)
            
            # Remove any potential duplicates
            unique_data = {}
            for item in summary_data:
                key = item['leave_type_id']
                if key not in unique_data:
                    unique_data[key] = item
            
            final_data = list(unique_data.values())
            final_data.sort(key=lambda x: x['leave_type_title'])
            
            return success(final_data)
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return exception(e)








   