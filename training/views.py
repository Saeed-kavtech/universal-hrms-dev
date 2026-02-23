from datetime import datetime,timedelta
from django.shortcuts import render
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from helpers.custom_permissions import IsAuthenticated, DoesOrgExists,IsEmployeeOnly,IsAdminOnly
from helpers.email_data import *
from rest_framework import viewsets
from .serializers import *
from .models import *
from helpers.status_messages import *
from employees.serializers import EmployeePreDataSerializers
from courses.models import *
from helpers.decode_token import decodeToken
import json
from courses.serializers import *
from django.utils import timezone
from employees.models import EmployeeProjects
from projects.views import PreProjectDataView
from decimal import Decimal
# Create your views here.
from email_templates.models import EmailRecipients
class  TrainingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminOnly]

    def pre_data(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            projects=PreProjectDataView().pre_data(organization_id)
            trainings=self.training_pre_data(organization_id)

            employees = Employees.objects.filter(organization=organization_id, is_active=True)
            employees_serializers = EmployeePreDataSerializers(employees, many=True)

            data = {
                'projects':projects,
                'trainings':trainings,
                'employees': employees_serializers.data,
            }

            return successMessageWithData('Success', data)

        except Exception as e:
            return exception (e)

    def create(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            current_date=datetime.today().date()
            request_data=request.data
            assignment_error=[]
            employee_error=[]

            # print(organization_id)

            # if not request.data:
            #     return errorMessage("Request data is empty")
            

            
            if isinstance(request_data, str):
                request_data = json.loads(request_data)
                req_training.append(request_data)
            else:
                req_training = request_data


            required_fields = ['title','duration']
            if not all(field in req_training for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','title,duration')
            
            course_id=request.data.get('course',None)

            if course_id is not None:

                course_query=Courses.objects.filter(id=course_id,organization=organization_id,is_active=True)
                
                if not course_query.exists():
                    return errorMessage("Course not exists in this organization")
            
            # employee_count=len(req_training["training_employees"])
            # print(employee_count)

            # cost=0

            # if 'cost' in req_training:
            #     cost=req_training['cost']

            evaluator_id = request.data.get('evaluator', None)
            if evaluator_id:
                evaluator = Employees.objects.filter(
                    id=evaluator_id, 
                    organization=organization_id, 
                    is_active=True
                )
                if not evaluator.exists():
                    return errorMessage('Evaluator does not exists at this id')

            
            req_training['created_by']=request.user.id
            req_training['organization']=organization_id
            start_date = request.data.get('start_date', None)
            end_date = request.data.get('end_date', None)

            



            # if start_date < current_date:
            #     return errorMessage("Start date must be greater or equal to current date")

            # if start_date< end_date:
            #     return errorMessage("End date must be greater or equal to start date")
            
            # print(req_training['training_employees'])
            serializer = TrainingViewSetSerializer(data = req_training)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            training_id=serializer.save()


 
            training_employee_data=req_training.get("training_employees",None)

            if training_employee_data is not None:

                for employee in req_training["training_employees"]:

                    emp=Employees.objects.filter(id=employee,organization=organization_id,is_active=True)

                    if not emp.exists():
                        employee_error.append(employee)
                        continue

                    
                    employee_data={
                            'employee':employee,
                            'training':training_id.id,
                            'start_date':start_date,
                            'end_date':end_date,
                            'training_evaluator':evaluator_id
                            } 
                    
                  
                    
                    
                    serializer =TrainingEmployeeSerializer(data = employee_data)
                    if not serializer.is_valid():
                        # return serializerError(serializer.errors)
                        employee_error.append(employee)
                        continue
                    
                    serializer.save()


            training_assignment_data=req_training.get("training_assignments",None)

            if training_assignment_data is not None:

                for assignment in req_training['training_assignments']:
                        marks=5
                        if 'marks' in assignment:
                            marks=assignment['marks']


                        assignment_data={
                            'title':assignment['title'],
                            'training':training_id.id,
                            'assignment':assignment['assignment'],
                            'marks':marks,
                            # 'submission_deadline':assignment['submission_deadline'],
                            } 
                    
                        serializer =TrainingAssignmentsSerializer(data = assignment_data)
                        if not serializer.is_valid():
                            # return serializerError(serializer.errors)
                            assignment_error.append(assignment_data)
                            continue
                        
                        serializer.save()

                        

            data={
                'employee_error':employee_error,
                'assignment_error':assignment_error
            }

                 
            if employee_error or assignment_error:
                    return successMessageWithData("some data is not created",data)


            return successMessage("Success")
        
        except Exception as e:
            return exception(e)
        

    def list(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            # print("Test1")
            # pk = self.kwargs['pk']
            # query=Training.objects.filter(course=pk,organization=organization_id,is_active=True)
            
            query=Training.objects.filter(organization=organization_id,is_active=True).order_by('-id')

            
            serializer=ListTrainingViewSetSerializer(query,many=True)

            return success(serializer.data)
        
        except Exception as e:
             return exception (e)
        

    def training_pre_data(self,organization_id):
        try:
            query=Training.objects.filter(organization=organization_id,is_active=True)
            serializer=TrainingViewSetSerializer(query,many=True)
            return serializer.data
        
        except Exception as e:
             return exception (e)
        

    def patch(self,request,*args, **kwargs):
        try:

            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            query=Training.objects.filter(id=pk,organization=organization_id,is_active=True)

            if not query.exists():
                return errorMessage("Training not exists at this id")
            
            obj=query.get()

            serializer=TrainingViewSetSerializer(obj,data=request.data,partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            serializer.save()

            return success(serializer.data)

        except Exception as e:
            return exception (e)
        


    def delete(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            error=[]
            query=Training.objects.filter(id=pk,organization=organization_id)
            
            if not query.exists():
                return errorMessage("Training not exists at this id")
            
            elif not query.filter(is_active=True).exists():
                return errorMessage('Training is deactivated at this id')
            

            assignment_query=TrainingAssignments.objects.filter(training=pk,training__organization=organization_id,is_active=True)
            
            employee_query=TrainingEmployee.objects.filter(training=pk,training__organization=organization_id,is_active=True)

            # print(assignment_query)
            # print(employee_query)


            for employee in employee_query:

                # print(employee.training_status)
                if employee.training_status>1:
                    error.append(employee.employee.id)
                    continue

                employee.is_active=False
                # print(employee)
                employee.save()


            if error:
                return errorMessageWithData("Training cannot be deleted as it is already in progress for some employees.",error)

            
            
            for assignment in assignment_query:

                assignment.is_active=False
                # print(assignment)
                assignment.save()

            
            obj=query.get()
            obj.is_active=False
            obj.save()


            return successMessage("Delete successfully")

        except Exception as e:
            return exception  (e)
        
    

    def stop_training(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            error=[]
            query=Training.objects.filter(id=pk,organization=organization_id)
            
            if not query.exists():
                return errorMessage("Training not exists at this id")
            
            if query.filter(status=2).exists():
                return errorMessage('Training is already stopped')
            
                       
            employee_query=TrainingEmployee.objects.filter(training=pk,training__organization=organization_id,is_active=True)
            # print(employee_query.values())

            for employee in employee_query:
                if employee.training_status==2:
                    error.append(employee.employee.id)
                    continue




            if error:
                return errorMessageWithData("Training cannot be stopped as it is already in progress for some employees.",error)

            obj=query.get()
            obj.status=2
            obj.save()
            return successMessage("Training stopped successfully")

        except Exception as e:
            return exception  (e)
        
    
  
  
    
    def add_training_in_project(self,request,*args, **kwargs):
        try:

            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            already_exists=[]
            does_not_exists=[]
            required_fields = ['project','training_array']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','project,training_array')

            project_id=request.data.get('project',None)
            project_query=Projects.objects.filter(id=project_id,organization=organization_id,is_active=True)

            if not project_query.exists():
                return errorMessage("Project not exists at this id")

            # if 'training_array' not in request.data:
            #     return errorMessage('trainings array does not exists')
            
            trainings = list(request.data.get('training_array'))


            # print(training_employee)

           
            for training in trainings:
                training_query=Training.objects.filter(id=training,organization=organization_id,is_active=True)

                if not training_query.exists():
                #    return errorMessage("No training exists at this id")
                    does_not_exists.append(training)
                    continue

                query=ProjectTraining.objects.filter(project=project_id,training=training,training__organization=organization_id,is_active=True)

                if query.exists():
                #    return errorMessage("No training exists at this id")
                    already_exists.append(training)
                    continue

                data={
                    'project':project_id,
                    'training':training,
                }

                serializer=ProjectTrainingSerializer(data=data)

                if not serializer.is_valid():
                    return serializerError(serializer.errors)
                
                serializer.save()


            data={
                'already_exists':already_exists,
                'does_not_exists':does_not_exists
            }

            if already_exists or does_not_exists:
                    return errorMessageWithData("Some of the data is processed successfully",data)

            return successMessage("Success")

        except Exception as e:
            return exception (e)


       
    def add_project_in_training(self,request,*args, **kwargs):
        try:

            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            already_exists=[]
            does_not_exists=[]
            # serializer_error=[]
            required_fields = ['training','project_array']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','training,project_array')

            training_id=request.data.get('training',None)
            training_query=Training.objects.filter(id=training_id,organization=organization_id,is_active=True)

            if not training_query.exists():
                return errorMessage("Training not exists at this id")

            # if 'training_array' not in request.data:
            #     return errorMessage('trainings array does not exists')

            traning_obj=training_query.get()
            
            notify=request.data.get('notify',False)
            
            projects = list(request.data.get('project_array'))


            # print(training_employee)

           
            for project in projects:
                project_query=Projects.objects.filter(id=project,organization=organization_id,is_active=True)

                if not project_query.exists():
                #    return errorMessage("No training exists at this id")
                    does_not_exists.append(project)
                    continue

                project_obj=project_query.get()

                query=ProjectTraining.objects.filter(training=training_id,project=project,training__organization=organization_id,is_active=True)

                if query.exists():
                #    return errorMessage("No training exists at this id")
                    already_exists.append(project)
                    continue

                data={
                    'training':training_id,
                    'project':project
                }

                serializer=ProjectTrainingSerializer(data=data)

                if not serializer.is_valid():
                    return serializerError(serializer.errors)
                
                serializer.save() 
                if notify==True:

                    employee=EmployeeProjects.objects.filter(project=project,is_active=True)

                    if employee.exists():
                        # official_emails = [emp.employee.official_email for emp in employee]
                        # # PojectTrainingNotificationEmail(traning_obj.title,project_obj.name,emp.employee.official_email)
                        for emp in employee:
                            PojectTrainingNotificationEmail(traning_obj.title,project_obj.name,emp.employee.official_email)

            
            data={
                'already_exists':already_exists,
                'does_not_exists':does_not_exists
            }

            if already_exists or does_not_exists:
                    return errorMessageWithData("Some of the data is processed successfully",data)


            

            return successMessage("Success")

        except Exception as e:
            return exception (e)
    
    def remove_project_from_training(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']

            training_query=ProjectTraining.objects.filter(id=pk,training__organization=organization_id)

            if not training_query.exists():
                return errorMessage("Data not exists at this id")
            
            elif not training_query.filter(is_active=True).exists():
                return errorMessage('Already deactivated')
            
            obj=training_query.get()
            obj.is_active=False
            obj.save()

            return successMessage("Deactivated Successfully")

        except Exception as e:
            return exception  (e)


  
    def get_list_project_traning(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            # print(organization_id)
            query=ProjectTraining.objects.filter(training__organization=organization_id,is_active=True)
            serializer=ProjectTrainingSerializer(query,many=True)
            return success(serializer.data)

        except Exception as e:
            return exception (e)
        

    def get_list_datewise_traning(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            required_fields = ['start_date','end_date']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','start_date,end_date')
            start_date=request.data['start_date']
            end_date=request.data['end_date']
            training_id=request.data.get('training_id',None)

            # print(organization_id)
            query=TrainingEmployee.objects.filter(training__organization=organization_id,start_date__lte=end_date,end_date__gte=start_date,is_active=True)
            
            if training_id is not None:
                query=query.filter(training=training_id)
            
            serializer=TrainingEmployeeSerializer(query,many=True)
            return success(serializer.data)

        except Exception as e:
            return exception (e)

    # Training Assignments
    def get_training_assignment(self,request,*args, **kwargs):
       try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            query=TrainingAssignments.objects.filter(training=pk,training__organization=organization_id,is_active=True)
            serializer=TrainingAssignmentsSerializer(query,many=True)

            return success(serializer.data)
           
       except Exception as e:
           return exception (e)
       

       
    def add_training_assignment(self,request,*args, **kwargs):
       try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            
            # print("Testing")
            # print(pk)
            required_fields = ['title','assignment']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','title,assignment')

            training_query=Training.objects.filter(id=pk,organization=organization_id,is_active=True)

            if not training_query.exists():
                return errorMessage("No training exists at this id")
            

            
            request.data._mutable = True
            marks=5

            if 'marks' not in request.data:
                request.data['marks']=marks
            

            request.data['training']=pk
            request.data['is_active'] = True

            serializer=TrainingAssignmentsSerializer(data=request.data)

            if not serializer.is_valid():
                if serializer.errors.get('assignment'):
                    return errorMessage(serializer.errors.get('assignment', [''])[0])
                return serializerError(serializer.errors)
            
            serializer.save()

            return success(serializer.data)
           
       except Exception as e:
           return exception (e)
       
    def update_training_assignment(self,request,*args, **kwargs):
       try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            
            # print("Testing")
            # print(pk)

            training_query=TrainingAssignments.objects.filter(id=pk,training__organization=organization_id,is_active=True)

            if not training_query.exists():
                return errorMessage("No assignment exists at this id")
            
            obj=training_query.get()
            

            serializer=TrainingAssignmentsSerializer(obj,data=request.data,partial=True)

            if not serializer.is_valid():
                if serializer.errors.get('assignment'):
                    return errorMessage(serializer.errors.get('assignment', [''])[0])
                return serializerError(serializer.errors)
            
            serializer.save()

            return success(serializer.data)
           
       except Exception as e:
           return exception (e)
       
    def remove_training_assignment(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            training_query=TrainingAssignments.objects.filter(id=pk,training__organization=organization_id)

            if not training_query.exists():
                return errorMessage("Assignment not exists at this id")
            
            elif not training_query.filter(is_active=True).exists():
                return errorMessage('Assignment is deactivated at this id')
            
            obj=training_query.get()
            obj.is_active=False
            obj.save()

            return successMessage("Delete successfully")

        except Exception as e:
            return exception  (e)
        
    def get_training_assignment_uploaded_by_emplyee(self,request,*args, **kwargs):
       try:
            
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            query=TrainingAssignments.objects.filter(training=pk,training__organization=organization_id,is_active=True)
            assignment_ids = [assignment.id for assignment in query]
            matching_assignments = EmployeeTrainingAssignment.objects.filter(employee__isnull=False,assignment_status=2,training_assignment__id__in=assignment_ids,is_active=True)
            serializer=EmployeeTrainingAssignmentSerializer(matching_assignments,many=True)
            return success(serializer.data)
           
       except Exception as e:
           return exception (e)
       


    #   Training Employees
    def remove_training_employee_single(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            training_query=TrainingEmployee.objects.filter(id=pk,training__organization=organization_id)

            if not training_query.exists():
                return errorMessage("Employee not exists at this id")
               
                             
            elif not training_query.filter(is_active=True).exists():
                return errorMessage('Employee is deactivated at this id')
            
            elif not training_query.filter(training_status=1).exists():
                return errorMessage('Employee only delete when training is in progress')

            
            obj=training_query.get()
            obj.is_active=False
            obj.save()

            return successMessage("Delete successfully")

        except Exception as e:
            return exception  (e)

    def get_training_employee(self,request,*args, **kwargs):
        try:

            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']

            query=TrainingEmployee.objects.filter(training=pk,training__organization=organization_id,is_active=True)
            
            serializer=TrainingEmployeeSerializer(query,many=True)

            return success(serializer.data)

        except Exception as e:
            return exception (e)
        
    def remove_training_employee(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            employee_error=[]
            employee_not_remove=[]
            training_query=Training.objects.filter(id=pk,organization=organization_id,is_active=True)

            already_training_employee=TrainingEmployee.objects.filter(training=pk,training__organization=organization_id,is_active=True)
            # print(already_training_employee)

            already_exists_employee = [item.employee.pk for item in already_training_employee]
            # print(already_exists_employee)
            if not training_query.exists():
                return errorMessage("No training exists at this id")

            if 'training_employees' not in request.data:
                return errorMessage('training_employee array does not exists')
            
            training_employee = list(request.data.get('training_employees'))

            # print(training_employee)

            for employee in training_employee:

                

                if not employee in already_exists_employee:
                   employee_error.append(employee)
                   continue
                
                training_emp_obj=TrainingEmployee.objects.get(employee=employee)
                training_emp_obj.is_active=False
                training_emp_obj.save()


            if employee_error :
                    return errorMessageWithData("Some employees are not in this training or have been deactivated.",employee_error)

            return successMessage("Employee remove successfully")

        except Exception as e:
            return exception (e)

    def add_training_employee(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            employee_error=[]
            employee_already_exists_error=[]
            current_date=datetime.today().date()

            required_fields = ['training_employees','training_evaluator']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','training_employees,training_evaluator')
            training_query=Training.objects.filter(id=pk,organization=organization_id,is_active=True)
            # print(request.data)
            already_training_employee=TrainingEmployee.objects.filter(training=pk,training__organization=organization_id,is_active=True)
            # print(already_training_employee)
            already_exists_employee = [item.employee.pk for item in already_training_employee]
            # print(already_exists_employee)
            if not training_query.exists():
                return errorMessage("No training exists at this id")
            
            
            evaluator_id = request.data.get('training_evaluator', None)
            if evaluator_id:
                evaluator = Employees.objects.filter(
                    id=evaluator_id, 
                    organization=organization_id, 
                    is_active=True
                )
                if not evaluator.exists():
                    return errorMessage('Evaluator does not exists at this id')
            

            start_date = request.data.get('start_date', None)
            end_date = request.data.get('end_date', None)

            # if start_date < current_date:
            #     return errorMessage("Start date must be greater or equal to current date")

            # if start_date< end_date:
            #     return errorMessage("End date must be greater or equal to start date")

            # print(start_date)
            # print(end_date)
            

            if 'training_employees' not in request.data:
                return errorMessage('training_employees array does not exists')
            
            

            training_employee = list(request.data.get('training_employees'))

            # print(training_employee)

           
            for employee in training_employee:

                emp=Employees.objects.filter(id=employee,organization=organization_id,is_active=True)

                if not emp.exists():
                    employee_error.append(employee)
                    continue

                if employee in already_exists_employee:
                   # Skip adding employees who are already part of the training
                   employee_already_exists_error.append(employee)
                   continue

                # print(emp)
                # emp_obj=emp.get()
                employee_data={
                        'employee':employee,
                        'training':pk,
                        'start_date':start_date,
                        'end_date':end_date,
                        'training_evaluator':evaluator_id
                        } 
                
                
                serializer =TrainingEmployeeSerializer(data = employee_data)
                # print(serializer)
                if not serializer.is_valid():
                    # return serializerError(serializer.errors)
                    employee_error.append(employee)
                    # continue
                
                serializer.save()


            data={
                'employee_already_exists_error':employee_already_exists_error,
                'employee_not_exists_error':employee_error
            }

            if employee_error or employee_already_exists_error:
                    return successMessageWithData("Some of the data is processed successfully",data)
            

            return successMessage("Success")

        except Exception as e:
            return exception (e)
        
    def update_training_employee(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
           
            training_employee=TrainingEmployee.objects.filter(id=pk,training__organization=organization_id,is_active=True)
            
            if not  training_employee.exists():
                return errorMessage("employee not exists in training")
            
            obj=training_employee.get()
            
            if obj.start_date is not None:
                if 'start_date' in request.data:
                    request.data.pop('start_date')


            # print(request.data)



            
            obj_training=training_employee.get()
                
            serializer =TrainingEmployeeSerializer(obj_training,data=request.data,partial=True)
                # print(serializer)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
              
                
            serializer.save()

            return successMessage("Success")

        except Exception as e:
            return exception (e)
        

    def reimbursement_approval_by_hr(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            pk = self.kwargs['pk']
            # user_id=request.user.id
            cost=request.data.get('reimbursed_cost',None)
            
            query=TrainingEmployee.objects.filter(id=pk,training__organization=organization_id,is_active=True)
            if not query.exists():
                return errorMessage('No data exists against given id')
            
            
            elif query.filter(reimbursement_status__gte=2,is_reimbursement=True):
                return errorMessage('Reimbursement is already approved by HR')
            
            obj=query.get()
            obj.reimbursed_cost=cost
            obj.reimbursement_status=2
            obj.is_reimbursement=True
            obj.save()
            return successMessage('Success')

        except Exception as e:
            return exception(e)

        
    
        
    


class EmployeeTrainingViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsEmployeeOnly]
    queryset=EmployeeTrainingAssignment.objects.all()
    serializer_class=EmployeeTrainingAssignmentSerializer

    def create(self,request,*args, **kwargs):
        try:

            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            current_date=datetime.today().date()
            # print("Test")

            required_fields=['training_assignment','submitted_assignment']

            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [training_assignment,submitted_assignment]')
            
            cc_employee=EmailRecipients.objects.filter(employee__organization=organization_id,level=3,is_active=True)

            if not cc_employee.exists():
                return errorMessage("Email recipient is not set against this module")
            
            sender_obj=cc_employee.get()

            training_assignment=request.data.get('training_assignment')

            assignment_query=TrainingAssignments.objects.filter(id=training_assignment,training__organization=organization_id,is_active=True)
            
            
            if not assignment_query.exists():
                return errorMessage("No training assignment exists at this id")
            

            obj_assignment=assignment_query.get()

            employee_query=TrainingEmployee.objects.filter(training=obj_assignment.training.id,employee=employee_id,is_active=True)

            if not employee_query.exists():
                return errorMessage("Employee not exists in given training")
            
            elif not employee_query.filter(training_status=2).exists():
                return errorMessage("To submit an assignment, the training must be in-progress")

            

            
            obj_employee=employee_query.get()

            # print(obj_employee)
            training_start_date= obj_employee.start_date
            training_end_date= obj_employee.end_date

            if training_start_date is not None and training_end_date is not None:
                # print("test")
              
                if not (training_start_date <= current_date <= training_end_date):
                    # Perform your action here
                    return errorMessage("Assignments are only accepted during the training period")


            
            
            request.data._mutable = True
            request.data['total_marks']=obj_assignment.marks
            request.data['employee']=employee_id
            request.data['created_by']=request.user.id
            request.data['assignment_file']=obj_assignment.assignment
            request.data['is_active'] = True 

            action=request.data.get('action',None)
            if action:
              action = action.lower()

            if action=="submit":
                request.data['assignment_status'] = 2

            serializer=self.serializer_class(data=request.data)

            if not serializer.is_valid():
                if serializer.errors.get('submitted_assignment'):
                    return errorMessage(serializer.errors.get('submitted_assignment', [''])[0])
                return serializerError(serializer.errors)
            
            serializer.save()
            AssignmentSubmissionNotificationEmail(obj_employee.training.title,obj_employee.employee.name,sender_obj.employee.name,sender_obj.employee.official_email)

            return success(serializer.data)

        except Exception as e:
            return exception (e)
   
    def list(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            employee_id = token_data['employee_id']

            pk = self.kwargs['pk']
            
            query=self.queryset.filter(training_assignment__training=pk,employee=employee_id,training_assignment__is_active=True,is_active=True)
            
            
            serializer=self.serializer_class(query,many=True)

            return success(serializer.data)
            
        except Exception as e:
            return exception (e)
        
    def patch(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            employee_id = token_data['employee_id']

            pk = self.kwargs['pk']
            current_date=datetime.today().date()
            emp_assignment=self.queryset.filter(id=pk,employee=employee_id,is_active=True)

            if not  emp_assignment.exists():
                return errorMessage("No employee asssignment exixts at this id")
            
            
            elif emp_assignment.filter(assignment_status=2).exists():
                return errorMessage("You cannot update an assignment after it has been submitted")
            
            obj=emp_assignment.get()
            # print(obj)

            employee_query=TrainingEmployee.objects.filter(training=obj.training_assignment.training.id,employee=employee_id,is_active=True)

            if not employee_query.exists():
                return errorMessage("Employee not exists in given training")
            
            obj_employee=employee_query.get()

            training_start_date= obj_employee.start_date
            training_end_date= obj_employee.end_date

            if training_start_date is not None and training_end_date is not None:
                # print("test")
              
                if not (training_start_date <= current_date <= training_end_date):
                    # Perform your action here
                    return errorMessage("Assignments are only accepted during the training duration")
            
            request.data._mutable = True
            
            action=request.data.get('action',None)
            if action:
              action = action.lower()

            if action=="submit":
                request.data['assignment_status'] = 2

            serializer=self.serializer_class(obj,data=request.data,partial=True)

            if not serializer.is_valid():
                if serializer.errors.get('submitted_assignment'):
                    return errorMessage(serializer.errors.get('submitted_assignment', [''])[0])
                return serializerError(serializer.errors)
            
            serializer.save()
           

            return success(serializer.data)
        
        except Exception as e:
            return exception (e)
    


    def delete(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            employee_id = token_data['employee_id']
            current_date=datetime.today().date()

            pk = self.kwargs['pk']

            emp_assignment=self.queryset.filter(id=pk,employee=employee_id,is_active=True)

            if not  emp_assignment.exists():
                return errorMessage("No employee asssignment exixts at this id")
            
            elif emp_assignment.filter(assignment_status=2).exists():
                return errorMessage("After submitting an assignment, it cannot be deleted")
            
            obj=emp_assignment.get()

            employee_query=TrainingEmployee.objects.filter(training=obj.training_assignment.training.id,employee=employee_id,is_active=True)

            if not employee_query.exists():
                return errorMessage("Employee not exists in given training")
            
            obj_employee=employee_query.get()

            training_start_date= obj_employee.start_date
            training_end_date= obj_employee.end_date

            if training_start_date is not None and training_end_date is not None:
                # print("test")
              
                if not (training_start_date <= current_date <= training_end_date):
                    # Perform your action here
                    return errorMessage("Action only preform in training duration")

            obj.is_active=False

            obj.save()

            return successMessage("Delete Successfully")
            
        except Exception as e:
            return exception (e)
    
    def get_employee_trainings(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            # permission_id=token_data['permission_id']
            # print("permission_id",permission_id)
            employee_id = token_data['employee_id']
            user_id = employee_id
            
            training_query=TrainingEmployee.objects.filter(employee=user_id,training__organization=organization_id,training__is_active=True,is_active=True).order_by('-id')
            # print(type(training_query))
            # training_instances = [item.training for item in training_query]
            # print()
            # Serialize the list of training instances
            serializer = EmployeeTrainingSerializer(training_query, many=True)

            return success(serializer.data)

        except Exception as e:
            return exception (e)
        
    
    def get_employee_project_based_traninings(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            serialized_data = []
            list_data=[]
            project_query=EmployeeProjects.objects.filter(employee=employee_id,employee__organization=organization_id,is_active=True).order_by('-id')
            # print(project_query.values())

            # project_ids = [project.id for project in project_query]
            for project in project_query:
                # print(project)
                pt_query=ProjectTraining.objects.filter(project=project.project_id,training__organization=organization_id,is_active=True).order_by('-id')
                # print(pt_query)
                training_ids = [training.training for training in pt_query]
                # print(training_ids)
                 # Serialize the list of training instances
                serialized_data.extend(training_ids)

            # print(serialized_data)

            list_data=list(set(serialized_data))
            
            
            serializer = ProjectBasedEmployeeTrainingSerializer(list_data,context={
                    "employee_id":employee_id
                }, many=True)

            return success(serializer.data)
                

        except Exception as e:
            return exception (e)
        

    def upload_training_invoice(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            pk = self.kwargs['pk']

            # required_fields = ['training_receipt']
            # if not all(field in request.data for field in required_fields):
            #     return errorMessage('make sure you have added training_receipt')

            query=TrainingEmployee.objects.filter(id=pk,employee=employee_id,training__organization=organization_id,is_active=True)

            if not query.exists():
                return errorMessage("No data exists againts given id")
            
            elif not query.filter(training_status=3).exists():
                return errorMessage("Before uploading the invoice, make sure to complete the training")
            
            elif not query.filter(is_reimbursement=False).exists():
                return errorMessage("Reimbursement already approved")
            

            obj=query.get()
            # print(obj)

            request.data._mutable = True
            request.data['reimbursement_status']=1
            request.data['is_reimbursement']=False

            # print(request.data)

            serializer=TrainingEmployeeSerializer(obj,data=request.data,partial=True)

            # print(serializer.data)

            if not serializer.is_valid():
                if serializer.errors.get('training_receipt'):
                    return errorMessage(serializer.errors.get('training_receipt', [''])[0])
                return errorMessage(serializer.errors)
            
            serializer.save()

            return successMessageWithData("Success",serializer.data)

        except exception as e:
            return exception (e)


    def training_started_by_employee(self,request,*args, **kwargs):
        try:

            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            pk = self.kwargs['pk']
            new_var=0

            emp_obj=Employees.objects.get(id=employee_id)

            training_query_result = None
            
            present_date=datetime.today().date()

            required_fields = ['training_status']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added training_status')
            

            cc_employee=EmailRecipients.objects.filter(employee__organization=organization_id,level=3,is_active=True)

            if not cc_employee.exists():
                return errorMessage("Email recipient is not set against this module")
            
            sender_obj=cc_employee.get()
            
            status_id=request.data.get('training_status',None)
            

            training_query=TrainingEmployee.objects.filter(training=pk,employee=employee_id,training__organization=organization_id,is_active=True)
            # print(training_query)
            if not training_query.exists():
                # return errorMessage("Employee not exists in this training")

                query1=Training.objects.filter(id=pk,organization=organization_id,is_active=True)

                if not query1.exists():
                    return errorMessage("Traning not exists at this id")
                
                obj1=query1.get()
                end_date = present_date + timedelta(days=obj1.duration)

                # print(emp)
                new_var=1
                # emp_obj=emp.get()
                employee_data={
                        'employee':employee_id,
                        'training':obj1.id,
                        'start_date':present_date,
                        'end_date':end_date,
                        'training_evaluator':obj1.evaluator.id
                        } 
                
                serializer =TrainingEmployeeSerializer(data = employee_data)
                # print(serializer)
                if not serializer.is_valid():
                    return serializerError(serializer.errors)
                training_query_result=serializer.save()

            
            elif training_query.filter(training_status=status_id):
                return errorMessage("Same stauts already  exists in this training")
            
            elif training_query.filter(training_status=3).exists():
                return errorMessage("After complete no action preformed")
            

            if new_var==0:
                obj_training=training_query.get()
            else:
                obj_training=training_query_result
            

            training_start_date=obj_training.start_date
            training_end_date=obj_training.end_date

            duration=obj_training.training.duration

            # print(duration)

            # print(current_date)
            end_date = present_date + timedelta(days=duration)
           
            if training_start_date is not None and training_end_date is not None:
              
                if not (training_start_date <= present_date <= training_end_date):
                    # Perform your action here
                    return errorMessage("Action only preform in training duration")
            
            # print("Month12")
            if status_id==2:
                if new_var==0:
                    obj_training.start_date=present_date
                    obj_training.end_date=end_date
              


            elif status_id==3:

                assignment=TrainingAssignments.objects.filter(training=pk,training__organization=organization_id,is_active=True)
                
                if assignment.exists():

                    # assignment_instances = [item.assignment.id for item in assignment]

                    assignment_ids = [assignment.id for assignment in assignment]

                    # print(assignment_ids)

                    for id in assignment_ids:
                        matching_assignments = EmployeeTrainingAssignment.objects.filter(employee=employee_id,assignment_status=2,training_assignment=id,is_active=True)
                        if not matching_assignments.exists():
                          return errorMessage("For completion, you must submit all assignments related to the training")


            obj_training.training_status=status_id

            obj_training.save()
            status_choices = {1: 'pending', 2: 'in progress', 3: 'completed'}
            provided_value = status_id
            status_title = status_choices[provided_value] if provided_value in status_choices else None

            TrainingStartNotificationEmail(obj_training.training.title,status_title,emp_obj.name,sender_obj.employee.name,sender_obj.employee.official_email)
            return successMessage("Success")
            
        except Exception as e:
            return exception (e)
        


    def add_assignment_marks(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            pk = self.kwargs['pk']
            employee_id = token_data['employee_id']

            if 'obtained_marks' not in request.data:
                return errorMessage("Please add obtained marks")

            emp_assignment=EmployeeTrainingAssignment.objects.filter(id=pk,assignment_status=2,is_active=True)

            if not  emp_assignment.exists():
                return errorMessage("No employee asssignment exists at this id")
            
            obj=emp_assignment.get()

            # print(obj.training_assignment.training)
            # print(obj.employee)


            training_emp=TrainingEmployee.objects.filter(training=obj.training_assignment.training,employee=obj.employee,is_active=True)

            if not  training_emp.exists():
                return errorMessage("No traning data exists")
            

            
            obj1=training_emp.get()

            user = request.user

            

            if obj1.training_evaluator.id == employee_id or user.is_admin:

                # obtained_marks = request.data['obtained_marks']
                
            
                # if obtained_marks>obj.total_marks:
                #     return errorMessage("Obtained marks should not exceed total marks")

                
                obj.obtained_marks=request.data['obtained_marks']
                obj.save()
                return successMessage("Success")
            
            else:
                return errorMessage("Only evaluator or admin have the authority to add marks")
        
        except Exception as e:
            return exception (e)
        

    def traning_evaluator_training_data(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
            # employee_id=employee_id
            ser_data=[]
            old_id=None
             # print("Test1")
            # pk = self.kwargs['pk']
            emptraining_query=TrainingEmployee.objects.filter(training_evaluator=employee_id,training__organization=organization_id,is_active=True)
            
            for emptraining in emptraining_query:
                if old_id==emptraining.training.id:
                    # print("continue")
                    continue
                    
                query=Training.objects.filter(id=emptraining.training.id,organization=organization_id,is_active=True).order_by('-id')
                # print(query)
                serializer=EvaluatorTrainingViewSetSerializer(query,context={
                    "user_id":employee_id
                },many=True)
                ser_data.extend(serializer.data)
                old_id=emptraining.training.id


            return success(ser_data)
            
        except Exception as e:
             return exception (e)
        
    def traning_evaluator_training_upload_assignment(self,request,*args, **kwargs):
        try:
            employee_id = decodeToken(self, self.request)['employee_id']
            
            pk = self.kwargs['pk']

            if 'employee' not in request.data:
                return errorMessage(
                    "employee is required field"
                )
            training_employee = request.data['employee']

            query_check_evaluator=TrainingEmployee.objects.filter(training=pk,employee=training_employee,training_evaluator=employee_id,is_active=True)
            
            if not query_check_evaluator.exists():
                return errorMessage("Training data not found")
            
            query=self.queryset.filter(training_assignment__training=pk,employee=training_employee,training_assignment__is_active=True,is_active=True)
            
            
            serializer=EvaluatorEmployeeTrainingAssignmentSerializer(query,many=True)

            return success(serializer.data)

        except Exception as e:
            return exception(e)
        
    def employee_training_counts(self,request,*args, **kwargs):
        try:
            employee_id = decodeToken(self, self.request)['employee_id']
            organization_id = decodeToken(self, self.request)['organization_id']
            pending_training_count=TrainingEmployee.objects.filter(employee=employee_id,training__organization=organization_id,training_status=1,training__is_active=True,is_active=True).count()
            in_progress_training_count=TrainingEmployee.objects.filter(employee=employee_id,training__organization=organization_id,training_status=2,training__is_active=True,is_active=True).count()
            completed_training_count=TrainingEmployee.objects.filter(employee=employee_id,training__organization=organization_id,training_status=3,training__is_active=True,is_active=True).count()
            project_query = EmployeeProjects.objects.filter(employee=employee_id, employee__organization=organization_id, is_active=True).order_by('-id')
            project_training_count = ProjectTraining.objects.filter(
                project__in=project_query.values('project_id'),
                training__organization=organization_id,
                is_active=True
            ).values('training').distinct().count()

            evaluator_query=TrainingEmployee.objects.filter(training_evaluator=employee_id,training__organization=organization_id,is_active=True)
            evaluator_training_count=Training.objects.filter(id__in=evaluator_query.values('training_id'),organization=organization_id,is_active=True).distinct().count()
            data={
                 "pending_training_count":pending_training_count,
                 "in_progress_training_count":in_progress_training_count,
                 "completed_training_count":completed_training_count,
                 "project_training_count":project_training_count,
                 "evaluator_training_count":evaluator_training_count
            }
            
            return successMessageWithData('Success',data)
        
        except Exception as e:
            return exception(e)

        
        



       
