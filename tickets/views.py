from django.shortcuts import render
from employees.models import EmployeeProjects
from employees.serializers import EmployeeJDCMSerializer, PreEmployeesDataSerializers
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists,IsEmployeeOnly,IsAdminOnly
from projects.models import Projects
from rest_framework import viewsets
from .serializers import *
from .models import *
from helpers.status_messages import *
from helpers.decode_token import decodeToken
from django.db.models import Q
from departments.models import Departments
from departments.serializers import DepartmentsOrgSerializer
# Create your views here.

      
class TicketCategoryViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    queryset=TicketCategory.objects.all()
    serializer_class=TicketCategorySerializer
    
    
    def create(self, request, *args, **kwargs):
        try:
            
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id=token_data['employee_id']

            required_fields = ['title']
            if not all(field in request.data for field in required_fields):
                        return errorMessageWithData('make sure you have added all required field','title')
            
            check_query=self.queryset.filter(title=request.data['title'],organization=organization_id,is_active=True)

            if check_query.exists():
                    return errorMessage("This title already exists")
            
            request.data['created_by'] = request.user.id
            request.data['organization'] = organization_id
            
            serializer=self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
            
        except Exception as e:
            return exception(e)
  
    
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            query = self.queryset.filter(organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def patch(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            if not request.data:
                return errorMessage("Request Data is empty")
            

            query=self.queryset.filter(id=pk,created_by=request.user.id,organization=organization_id,is_active=True)

            if not query.exists():
                    return errorMessage("Data not exists in current organization")
            
            if 'title' in request.data:
                check_query=self.queryset.filter(title=request.data['title'],organization=organization_id,is_active=True)
                if check_query.exists():
                        return errorMessage("This title already exists")
                
                
            obj=query.get()
            
            serializer=self.serializer_class(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()

            return successfullyUpdated(serializer.data)
            
        except Exception as e:
            return exception(e)
        

    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            
            query = self.queryset.filter(id=pk,created_by=request.user.id)
            if not query.exists():
                return errorMessage('Category does not exists')
            if not query.filter(is_active=True).exists():
                return errorMessage('Category is already deactivated at this id')
            
            obj = query.get()
            obj.is_active=False
            obj.save()
            
            return successMessage('Category is deactivated successfully')
        except Exception as e:
            return exception(e)



class TicketCategoryDepartmentViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    queryset=TicketCategoryDepartment.objects.all()
    serializer_class=TicketCategoryDepartmentSerializer
    
    
    def create(self, request, *args, **kwargs):
        try:
            
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            required_fields = ['ticket_category','department']
            if not all(field in request.data for field in required_fields):
                        return errorMessageWithData('make sure you have added all required field','ticket_category,department')
            
            ticket_category_query=TicketCategory.objects.filter(id=request.data['ticket_category'],organization=organization_id,is_active=True)

            if not ticket_category_query.exists():
                    return errorMessage("This ticket category does not exists")
                
            
            department_query=Departments.objects.filter(id=request.data['department'],grouphead__organization=organization_id,is_active=True)

            if not department_query.exists():
                    return errorMessage("This department does not exists")
                
            already_exixts=self.queryset.filter(ticket_category=request.data['ticket_category'],department=request.data['department'],is_active=True)
                
            if already_exixts.exists():
                    return errorMessage("Same data already exists")
            
            request.data['created_by'] = request.user.id
            
            serializer=self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
            
        except Exception as e:
            return exception(e)
  
    
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            query = self.queryset.filter(ticket_category__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def patch(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            if not request.data:
                return errorMessage("Request Data is empty")
            

            query=self.queryset.filter(id=pk,created_by=request.user.id,organization=organization_id,is_active=True)

            if not query.exists():
                    return errorMessage("Data not exists in current organization")
                
                
            ticket_category=request.data.get('ticket_category',None)
            department=request.data.get('department',None)
            if ticket_category is not None:
                ticket_category_query=TicketCategory.objects.filter(id=ticket_category,organization=organization_id,is_active=True)

                if not ticket_category_query.exists():
                        return errorMessage("This ticket category does not exists")
                
            if department is not None:
                department_query=Departments.objects.filter(id=department,grouphead__organization=organization_id,is_active=True)

                if not department_query.exists():
                        return errorMessage("This department does not exists")
            
            if department is not None and ticket_category is not None:
                
                already_exixts=self.queryset.filter(ticket_category=ticket_category,department=department,is_active=True)
                    
                if already_exixts.exists():
                        return errorMessage("Same data already exists")
                
                
            obj=query.get()
            
            serializer=self.serializer_class(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()

            return successfullyUpdated(serializer.data)
            
        except Exception as e:
            return exception(e)

    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            
            query = self.queryset.filter(id=pk,created_by=request.user.id)
            if not query.exists():
                return errorMessage('Date does not exists')
            if not query.filter(is_active=True).exists():
                return errorMessage('Data is already deactivated at this id')
            
            obj = query.get()
            obj.is_active=False
            obj.save()
            
            return successMessage('Data is deactivated successfully')
        except Exception as e:
            return exception(e)


class TicketDepartmentEmployeeViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    queryset=TicketDepartmentEmployee.objects.all()
    serializer_class=TicketDepartmentEmployeeSerializer
    
    
    def create(self, request, *args, **kwargs):
        try:
            
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            required_fields = ['ticket_category_department','employee']
            if not all(field in request.data for field in required_fields):
                        return errorMessageWithData('make sure you have added all required field','ticket_category_department,employee')
            
            ticket_category_department_query=TicketCategoryDepartment.objects.filter(id=request.data['ticket_category_department'],ticket_category__organization=organization_id,is_active=True)

            if not ticket_category_department_query.exists():
                    return errorMessage("This ticket category department does not exists")
                
            obj=ticket_category_department_query.get()
                
            
            employee_query=Employees.objects.filter(id=request.data['employee'],organization=organization_id,is_active=True)

            if not employee_query.exists():
                return errorMessage("This employee does not exists")
            
            elif not employee_query.filter(department=obj.department.id).exists():
                return errorMessage("This employee is not part of the selected department")
                    
            already_exixts=self.queryset.filter(ticket_category_department =request.data['ticket_category_department'],employee=request.data['employee'],is_active=True)
                
            if already_exixts.exists():
                    return errorMessage("Same data already exists")
            
            request.data['created_by'] = request.user.id
            
            serializer=self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
            
        except Exception as e:
            return exception(e)
  
    
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            department_id=self.kwargs['department_id']
            query = self.queryset.filter(ticket_category_department__department=department_id,ticket_category_department__ticket_category__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def patch(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            if not request.data:
                return errorMessage("Request Data is empty")
            

            query=self.queryset.filter(id=pk,created_by=request.user.id,organization=organization_id,is_active=True)

            if not query.exists():
                    return errorMessage("Data not exists in current organization")
                
            ticket_category_department=request.data.get('ticket_category_department',None)
            employee=request.data.get('employee',None)
            
            if ticket_category_department is not None and employee is not None:
                    
                already_exixts=self.queryset.filter(ticket_category_department =request.data['ticket_category_department '],employee=request.data['employee'],is_active=True)
                    
                if already_exixts.exists():
                        return errorMessage("Same data already exists")
                
                
            obj1=query.get()
            
            serializer=self.serializer_class(obj1, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()

            return successfullyUpdated(serializer.data)
            
        except Exception as e:
            return exception(e)
        


    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            
            query = self.queryset.filter(id=pk,created_by=request.user.id)
            if not query.exists():
                return errorMessage('Date does not exists')
            if not query.filter(is_active=True).exists():
                return errorMessage('Data is already deactivated at this id')
            
            obj = query.get()
            obj.is_active=False
            obj.save()
            
            return successMessage('Data is deactivated successfully')
        except Exception as e:
            return exception(e)





class TicketViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]

    def create(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            user_id = request.user.id
            
            required_fields = ['subject','description','category','ticket_department']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','subject,description,category,ticket_department')
            
            employee_query=Employees.objects.filter(id=employee_id,organization=organization_id,is_active=True)

            if not employee_query.exists():
                return errorMessage("Employee not exists in current organization")
            
            category=request.data['category']
            ticket_department=request.data.get('ticket_department',None)

            
            
            ticket_category_query=TicketCategory.objects.filter(id=category,organization=organization_id,is_active=True)

            if not ticket_category_query.exists():
                    return errorMessage("This ticket category does not exists")
                
            if 'send_to_admin' in request.data and request.data['send_to_admin']==True and ticket_category_query.filter(is_main_admin=False).exists():
                        return errorMessage("Can't send this ticket to main admin")
                
            if ticket_department is not None:
                department_query=Departments.objects.filter(id=ticket_department,grouphead__organization=organization_id,is_active=True)
                if not department_query.exists():
                    return errorMessage("This department does not exists")
            
            if ticket_department is not None and category is not None:
                ticket_department_category_query=TicketCategoryDepartment.objects.filter(department=ticket_department,ticket_category=category,ticket_category__organization=organization_id,is_active=True)
                if not ticket_department_category_query.exists():
                    return errorMessage("The department and category are not correctly associated")
                 
            
            ticket_handler=request.data.get('assign_to',None)
            if ticket_handler is not None:
                ticket_handler_query=Employees.objects.filter(id=ticket_handler,organization=organization_id,is_active=True)

                if not ticket_handler_query.exists():
                    return errorMessage("Assign to employee not exists in current organization")
                
                check_department_employee=TicketDepartmentEmployee.objects.filter(employee=ticket_handler,ticket_category_department__department=ticket_department,is_active=True)
                if not check_department_employee.exists():
                    return errorMessage("The ticket department and employee are not correctly associated")
                
                
                
            team_lead=request.data.get('team_lead',None)
            if team_lead is not None:
                team_lead_query=Employees.objects.filter(id=team_lead,organization=organization_id,is_active=True)

                if not team_lead_query.exists():
                    return errorMessage("Team lead not exists in current organization")
                
                # if team_lead==employee_id:
                #   return errorMessage('Employee cannot set themselves as their own team lead')
            
            request.data['created_by'] = user_id
            request.data['employee']=employee_id

            serializer=TicketSerializer(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)

        except Exception as e:
          return exception(e)
        
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            query = Ticket.objects.filter(employee=employee_id,employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = TicketSerializer(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def patch(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            # user_id = request.user.id
            # print(pk)
            if not request.data:
                return errorMessage("Request Data is empty")
            
                
            query = Ticket.objects.filter(id=pk,is_active=True)
            
            if not query.exists():
                return errorMessage('No ticket exists at this id')
            
            category=request.data.get('category',None)
            ticket_department=request.data.get('ticket_department',None)
            
            if category is not None:
                
                ticket_category_query=TicketCategory.objects.filter(id=category,organization=organization_id,is_active=True)

                if not ticket_category_query.exists():
                        return errorMessage("This ticket category does not exists")
                    
            if 'send_to_admin' in request.data and request.data['send_to_admin']==True and query.filter(category__ticket_category__is_main_admin=False).exists():
                        return errorMessage("Can't send this ticket to main admin")

                
            if ticket_department is not None:
                department_query=Departments.objects.filter(id=ticket_department,grouphead__organization=organization_id,is_active=True)
                if not department_query.exists():
                    return errorMessage("This department does not exists")
            
            
            
            assign_to=request.data.get('assign_to',None)
            

            if assign_to is not None:
                assign_to_query=Employees.objects.filter(id=assign_to,organization=organization_id,is_active=True)

                if not assign_to_query.exists():
                    return errorMessage("Assign to employee not exists in current organization")
                check_department_employee=TicketDepartmentEmployee.objects.filter(employee=assign_to,ticket_category_department__department=ticket_department,is_active=True)
                if not check_department_employee.exists():
                    return errorMessage("The ticket department and employee are not correctly associated")
            
            team_lead=request.data.get('team_lead',None)   
            if team_lead is not None:
                team_lead_query=Employees.objects.filter(id=team_lead,organization=organization_id,is_active=True)

                if not team_lead_query.exists():
                    return errorMessage("Team lead not exists in current organization")
            
            if not query.filter(ticket_status=1):
                return errorMessage('For update ticket must be in pending state')
            
            obj=query.get()
            
            
            serializer=TicketSerializer(obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()

            return successfullyUpdated(serializer.data)
            
        except Exception as e:
            return exception(e)
        
    def delete(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            
            query = Ticket.objects.filter(id=pk)
            if not query.exists():
                return errorMessage('Ticket does not exists')
            if not query.filter(is_active=True).exists():
                return errorMessage('Ticket is already deactivated at this id')
            obj = query.get()
            
            if obj.ticket_status != 1:
                return errorMessage('Ticket can only be deactivated when it is pending state')
            
            obj.is_active=False
            obj.save()

            return successMessage('Ticket is deactivated successfully')
        except Exception as e:
            return exception(e)
        
    #HR actions
    def get_hr_ticket_data(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']

            if not request.user.is_admin:
                return errorMessage('User is not an admin user')
            
            query = Ticket.objects.filter(employee__organization=organization_id,send_to_admin=False,ticket_status__gt=1,is_active=True).order_by('-id')
            serializer = TicketSerializer(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def get_hr_services_ticket_data(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            if not request.user.is_admin:
                return errorMessage('User is not an admin user')
            
            query = Ticket.objects.filter(employee__organization=organization_id,send_to_admin=True,team_lead__isnull=True,assign_to__isnull=True,transfer_to__isnull=True,is_active=True).order_by('-id')
            serializer = TicketSerializer(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def action_by_hr(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            
            if not request.user.is_admin:
                return errorMessage('User is not an admin user')
            user_id=request.user.id
            required_fields = ['ticket_status', 'decision_reason']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all the required fields','ticket_status,decision_reason')
            
            query = Ticket.objects.filter(id=pk,send_to_admin=True,employee__organization=organization_id,team_lead__isnull=True,assign_to__isnull=True,transfer_to__isnull=True,is_active=True)
            if not query.exists():
                return errorMessage('No ticket exists at given id')
            obj = query.get()
            reason = request.data['decision_reason']
            status=request.data['ticket_status']
            output=None
            if reason:
                # print(status)
                output = self.ticket_reason(pk, reason,status,user_id)
                # print(output)
                if output['status'] == 400:
                        return errorMessage(output['message'])
                
            obj.ticket_status=status
            obj.save()

            return successMessageWithData('Status changed successfully',output['data'])
    
        except Exception as e:
            return exception(e)
        

        
        
    #Team Lead actions
    def get_team_lead_ticket(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            query = Ticket.objects.filter(team_lead=employee_id,employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = TicketSerializer(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def action_by_team_lead(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            user_id=request.user.id
            required_fields = ['ticket_status', 'decision_reason']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all the required fields','ticket_status,decision_reason')
            
            query = Ticket.objects.filter(id=pk,team_lead=employee_id,employee__organization=organization_id,is_active=True)
            if not query.exists():
                return errorMessage('No ticket exists at given id')
            
            elif not query.filter(ticket_status__in=[1,2,3,4]).exists():
                return errorMessage('The team lead only acts when the ticket is at an initial phase')

            obj = query.get()
            
            reason = request.data['decision_reason']
            status=request.data['ticket_status']
            output=None
            if reason:
                # print(status)
                output = self.ticket_reason(pk, reason,status,user_id)
                # print(output)
                if output['status'] == 400:
                        return errorMessage(output['message'])
                
            obj.ticket_status=status
            obj.save()

            return successMessageWithData('Status changed successfully',output['data'])
    
        except Exception as e:
            return exception(e)
        

        
        
    # Transfer to employee actions
    def get_transfer_to(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            query = Ticket.objects.filter(transfer_to=employee_id,ticket_status__in=[8,9,10],employee__organization=organization_id,is_active=True).order_by('-id')
            serializer = TicketSerializer(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def action_by_transfer_to(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            user_id=request.user.id
            required_fields = ['ticket_status', 'decision_reason']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all the required fields','ticket_status,decision_reason')
            
            query = Ticket.objects.filter(id=pk,transfer_to=employee_id,employee__organization=organization_id,is_active=True)
            # print(query.values())
            if not query.exists():
                return errorMessage('No ticket exists at this id')
            
            if query.filter(ticket_status=request.data['ticket_status']).exists():
                return successMessage('Status changed successfully')
            
            
            elif query.filter(ticket_status=10).exists():
                return errorMessage('Once a ticket is marked as solved, its status cannot be changed')

            
            elif not query.filter(ticket_status__in=[8,9]).exists():
                return errorMessage('You can only acts when the ticket is at an final phase')
            
            obj = query.get()
            
            reason = request.data['decision_reason']
            status=request.data['ticket_status']
            output=None
            if reason:
                # print(status)
                output = self.ticket_reason(pk, reason,status,user_id)
                # print(output)
                if output['status'] == 400:
                        return errorMessage(output['message'])
                

            # obj.ticket_status=status
            
            obj.ticket_status=status
            obj.save()
            
            return successMessageWithData('Status changed successfully',output['data'])
    
        except Exception as e:
            return exception(e)


    # Assign to employee actions
        
    def get_assign_to_procurement(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id=decodeToken(request,self.request)['employee_id']
            # team_lead__isnull=False
            query = Ticket.objects.filter(assign_to=employee_id,employee__organization=organization_id,team_lead__isnull=False,send_to_admin=False,ticket_status__in=[4, 5, 6, 7, 8, 9, 10],is_active=True).order_by('-id')
            serializer = TicketSerializer(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    # def get_assign_to_general(self, request, *args, **kwargs):
    #     try:
    #         organization_id = decodeToken(request, self.request)['organization_id']
    #         employee_id=decodeToken(request,self.request)['employee_id']
    #         # team_lead__isnull=True
    #         query = Ticket.objects.filter(assign_to=employee_id,employee__organization=organization_id,team_lead__isnull=True,category=2,is_active=True).order_by('-id')
    #         serializer = TicketSerializer(query, many=True)
    #         return success(serializer.data)
    #     except Exception as e:
    #         return exception(e)
        
    def action_by_assign_to(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            user_id=request.user.id
            required_fields = ['ticket_status', 'decision_reason']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all the required fields','ticket_status,decision_reason')
            
            query = Ticket.objects.filter(id=pk,send_to_admin=False,assign_to=employee_id,employee__organization=organization_id,is_active=True)
            if not query.exists():
                return errorMessage('No ticket  exists at this id')
            
            if not query.filter(team_lead__isnull=True).exists():
                if not query.filter(ticket_status__in=[4,5,6,7,8,9,10]).exists():
                    return errorMessage('You can only acts when the ticket is at an final phase')
            
            
            if query.filter(ticket_status=request.data['ticket_status']).exists():
                return successMessage('Status changed successfully')

            
            obj = query.get()
            
            reason = request.data.get('decision_reason', None)
            status=request.data.get('ticket_status',None)
            output=None
            if reason:
                # print(status)
                output = self.ticket_reason(pk, reason,status,user_id)
                # print(output)
                if output['status'] == 400:
                        return errorMessage(output['message'])

            obj.ticket_status=status
            obj.save()

            return successMessageWithData('Status changed successfully',output['data'])
    
        except Exception as e:
            return exception(e)
        
    def ticket_transfer_to(self, request, *args, **kwargs):
        try:
            # print("Test")
            pk = self.kwargs['pk']
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id = decodeToken(request, self.request)['employee_id']
            user_id=request.user.id
            if not request.data:
                return errorMessage("Request Data is empty")
            transfer_to=request.data.get('transfer_to',None)
            query = Ticket.objects.filter(id=pk,employee__organization=organization_id,is_active=True)
            if not query.exists():
                    return errorMessage('No ticket request  exists')
            if not query.filter(assign_to=employee_id).exists() or not request.user.is_admin:
                    return errorMessage('Only ticket assignee and main admin transfer tickets to another employee')
            
            if query.filter(transfer_to=transfer_to):
                return errorMessage('Ticket already trnasfer to this')
            
            if not query.filter(team_lead__isnull=True).exists():
                if not query.filter(ticket_status__in=[4,5,6,7,8,9,10]).exists():
                    return errorMessage('Please note that the ticket cannot be transferred until it reaches the final phase')
            # emp_name=None
            employee_query=None
            
            
            if transfer_to:
                employee_query=Employees.objects.filter(id=transfer_to,organization=organization_id,is_active=True)

                if not employee_query.exists():
                    return errorMessage("Transfer to employee not exists in current organization")
                
                check_department_employee=TicketDepartmentEmployee.objects.filter(employee=transfer_to,is_active=True)
                if not check_department_employee.exists():
                    return errorMessage("This employee have no role in ticket processing")
                   
                
            employee_obj=employee_query.get()
                   

            reason = f"Your ticket has been forwarded to {employee_obj.name} for handling"
            status=8
            output=None
            output = self.ticket_reason(pk, reason,status,user_id)
            if output['status'] == 400:
                    return errorMessage(output['message'])
            
                
            obj = query.get()
            obj.transfer_to=employee_obj
            obj.ticket_status=status
            obj.save()
                

            return successMessageWithData('Tickket transfered successfully ',output['data'])
        except Exception as e:
            return exception(e)
     
        
    def get_ticket_department_category(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            department_id=self.kwargs['department_id']
            data=[]
            query =TicketCategoryDepartment.objects.filter(department=department_id,ticket_category__organization=organization_id,is_active=True).order_by('-id')
            for q in query:
                category=TicketCategorySerializer(id=q.ticket_category.id,is_active=True)
                serializer=TicketCategorySerializer(category,many=True).data
                data.extend(serializer)
                
            return success(data)
        except Exception as e:
            return exception(e)
    # descicion data 
        
        
    def get_descicion_data(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            pk=self.kwargs['pk']
            query = TicketLogs.objects.filter(ticket=pk,is_active=True).order_by('-id')
            serializer = TicketLogsSerializer(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def ticket_counts(self,request,*args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            employee_id=decodeToken(request,self.request)['employee_id']
            team_lead_count = Ticket.objects.filter(team_lead=employee_id,employee__organization=organization_id,is_active=True).count()
            transfer_to_count = Ticket.objects.filter(transfer_to=employee_id,ticket_status__in=[8,9,10],employee__organization=organization_id,is_active=True).count()
            procurement_ticket_count= Ticket.objects.filter(assign_to=employee_id,employee__organization=organization_id,team_lead__isnull=False,ticket_status__in=[4, 5, 6, 7, 8, 9, 10],is_active=True).count()
            general_ticket_count = Ticket.objects.filter(assign_to=employee_id,employee__organization=organization_id,team_lead__isnull=True,is_active=True).count()
            data={
                'team_lead_count':team_lead_count,
                'transfer_to_count':transfer_to_count,
                'procurement_ticket_count':procurement_ticket_count,
                'general_ticket_count':general_ticket_count
            }
            return successMessageWithData('Success', data)
        except Exception as e:
            return exception(e)

            
    def ticket_reason(self,id,reason,status,user_id):
        try:
            result = {
                'status': 400, 
                'data':[],
                'message': '', 
                'system_error_message': ''
            }
            
            data={
                "ticket":id,
                "decision_reason":reason,
                "ticket_status":status,
                "decision_by":user_id,
            }
            

            serializer = TicketLogsSerializer(data=data)
            if not serializer.is_valid():
                # print(serializer.errors)
                result['message'] = serializer.errors
                return result
            
            serializer.save()

            result['status'] = 200
            result['data']=serializer.data

            return result

        except Exception as e:
            return exception(e)


    #get predata

    def get_ticket_departement(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            query = TicketCategoryDepartment.objects.filter(ticket_category__organization=organization_id,is_active=True).order_by('-id')
            data=[]
            for q in query:
                department=Departments.objects.filter(id=q.department.id,is_active=True)
                serializer = DepartmentsOrgSerializer(department, many=True).data
                data.extend(serializer)
            return success(data)
        except Exception as e:
            return exception(e)
        

    # def get_departement_category(self, request, *args, **kwargs):
    #     try:
    #         organization_id = decodeToken(request, self.request)['organization_id']
    #         department_id=self.kwargs['department_id']
    #         query = TicketCategoryDepartment.objects.filter(department=department_id,ticket_category__organization=organization_id,is_active=True).order_by('-id')
    #         data=[]
    #         for q in query:
    #             department=TicketCategory.objects.filter(id=q.ticket_category.id,is_active=True)
    #             serializer =TicketCategorySerializer(department, many=True).data
    #             data.extend(serializer)
    #         return success(data)
    #     except Exception as e:
    #         return exception(e)
        

    # def get_departement_employee(self, request, *args, **kwargs):
    #     try:
    #         organization_id = decodeToken(request, self.request)['organization_id']
    #         department_id=self.kwargs['department_id']
    #         query = TicketDepartmentEmployee.objects.filter(ticket_category_department__department=department_id,ticket_category_department__ticket_category__organization=organization_id,is_active=True).order_by('-id')
    #         data=[]
    #         for q in query:
    #             employee=Employees.objects.filter(id=q.employee.id,is_active=True)
    #             serializer =EmployeeJDCMSerializer(employee, many=True).data
    #             data.extend(serializer)
    #         return success(data)
    #     except Exception as e:
    #         return exception(e)
    
    def get_department_details(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            department_id = self.kwargs['department_id']
            
            # Fetching department categories
            category_query = TicketCategoryDepartment.objects.filter(
                department=department_id,
                ticket_category__organization=organization_id,
                is_active=True
            ).order_by('-id')
            category_data = []
            for q in category_query:
                department = TicketCategory.objects.filter(id=q.ticket_category.id, is_active=True)
                category_serializer = TicketCategorySerializer(department, many=True).data
                category_data.extend(category_serializer)
            
            # Fetching department employees
            employee_query = TicketDepartmentEmployee.objects.filter(
                ticket_category_department__department=department_id,
                ticket_category_department__ticket_category__organization=organization_id,
                is_active=True
            ).order_by('-id')
            employee_data = []
            for q in employee_query:
                employee = Employees.objects.filter(id=q.employee.id, is_active=True)
                employee_serializer = EmployeeJDCMSerializer(employee, many=True).data
                employee_data.extend(employee_serializer)
            
            # Combining both results into a single response
            response_data = {
                'categories': category_data,
                'employees': employee_data
            }
            
            return success(response_data)
        except Exception as e:
            return exception(e)


        

    

        
