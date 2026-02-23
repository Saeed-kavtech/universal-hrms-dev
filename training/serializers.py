from rest_framework import serializers
from .models import *
from courses.serializers import *
from courses.models import Courses
class TrainingViewSetSerializer(serializers.ModelSerializer):
    number_of_employee=serializers.SerializerMethodField()
    status_title=serializers.SerializerMethodField()
    mode_of_training_title=serializers.SerializerMethodField()
    evaluator_name=serializers.SerializerMethodField()
    class Meta:
        model = Training
        fields = [
            'id',
            'title',
            'course',
            'description',
            'duration',
            'mode_of_training',
            'mode_of_training_title',
            'cost',
            'status',
            'status_title',
            'number_of_employee',
            'organization',
            'evaluator',
            'evaluator_name',
            'created_by',
            'is_active',
            'created_at',
            'updated_at',
        ]


    def get_evaluator_name(self, obj):
        try:
            return obj.evaluator.name
        except Exception as e:
            return None
        

    def get_number_of_employee(self,obj):
        try:
            count=0
            query=TrainingEmployee.objects.filter(training=obj.id,is_active=True)
            
            if query.exists():
                count=len(query)
                return count
            
            return None

        except Exception as e:
            return None
        
    def get_status_title(self,obj):
        try:
            if obj.status in [1,2]:
                return choices_for_training[obj.status-1][1]
            
            return None

        except Exception as e:
            return None
    

    def get_mode_of_training_title(self,obj):
        try:
            if obj.mode_of_training in [1,2]:
                return mode_of_training_choices[obj.mode_of_training-1][1]
            
            return None

        except Exception as e:
            return None
        





class ListTrainingViewSetSerializer(serializers.ModelSerializer):
    training_employees=serializers.SerializerMethodField()
    training_assignments=serializers.SerializerMethodField()
    training_projects=serializers.SerializerMethodField()
    number_of_employee=serializers.SerializerMethodField()
    mode_of_training_title=serializers.SerializerMethodField()
    status_title=serializers.SerializerMethodField()
    evaluator_name=serializers.SerializerMethodField()

    
    class Meta:
        model = Training
        fields = [
            'id',
            'title',
            'course',
            'description',
            'duration',
            'mode_of_training',
            'mode_of_training_title',
            'status',
            'status_title',
            'cost',
            'number_of_employee',
            'training_employees',
            'training_assignments',
            'training_projects',
            'organization',
            'evaluator',
            'evaluator_name',
            'created_by',
            'is_active',
            'created_at',
            'updated_at',
        ]


    def get_evaluator_name(self, obj):
        try:
            return obj.evaluator.name
        except Exception as e:
            return None
    

    def get_number_of_employee(self,obj):
        try:
            count=0
            query=TrainingEmployee.objects.filter(training=obj.id,is_active=True)
            
            if query.exists():
                count=len(query)
                return count
            
            return None
        
        except Exception as e:
            return None
        

    def get_status_title(self,obj):
        try:
            if obj.status in [1,2]:
                return choices_for_training[obj.status-1][1]
            
            return None

        except Exception as e:
            return None

        
    def get_training_employees(self,obj):
       try:
           query=TrainingEmployee.objects.filter(training=obj.id,is_active=True)
           query1=TrainingAssignments.objects.filter(training=obj.id,is_active=True)
           
           if not query.exists():
               return None
               
           data=ListTrainingEmployeeSerializer(query,context={'assignment': query1},many=True).data
        
           return data

       except Exception as e:
           return None
       
    def get_training_projects(self,obj):
       try:
           query=ProjectTraining.objects.filter(training=obj.id,is_active=True)
           
           
           if not query.exists():
               return None
               
           data=ListProjectTrainingSerializer(query,many=True).data
        
           return data

       except Exception as e:
           return None
       

    def get_mode_of_training_title(self,obj):
        try:
            if obj.mode_of_training in [1,2]:
                return mode_of_training_choices[obj.mode_of_training-1][1]
            
            return None

        except Exception as e:
            return None
          
    
    def get_training_assignments(self,obj):
       try:
           query=TrainingAssignments.objects.filter(training=obj.id,is_active=True)
           
           if not query.exists():
               return None
               
           data=TrainingAssignmentsSerializer(query,many=True).data
        
           return data

       except Exception as e:
           return None





class EvaluatorTrainingViewSetSerializer(serializers.ModelSerializer):
    training_employees=serializers.SerializerMethodField()
    training_assignments=serializers.SerializerMethodField()
    training_projects=serializers.SerializerMethodField()
    number_of_employee=serializers.SerializerMethodField()
    mode_of_training_title=serializers.SerializerMethodField()
    status_title=serializers.SerializerMethodField()
    evaluator_name=serializers.SerializerMethodField()

    
    class Meta:
        model = Training
        fields = [
            'id',
            'title',
            'course',
            'description',
            'duration',
            'mode_of_training',
            'mode_of_training_title',
            'status',
            'status_title',
            'cost',
            'number_of_employee',
            'training_employees',
            'training_assignments',
            'training_projects',
            'organization',
            'evaluator',
            'evaluator_name',
            'created_by',
            'is_active',
            'created_at',
            'updated_at',
        ]


    def get_evaluator_name(self, obj):
        try:
            return obj.evaluator.name
        except Exception as e:
            return None
    

    def get_number_of_employee(self,obj):
        try:
            emp_id=self.context.get('user_id')
            count=0
            query=TrainingEmployee.objects.filter(training=obj.id,training_evaluator=emp_id,is_active=True)
            
            if query.exists():
                count=len(query)
                return count
            
            return None
        
        except Exception as e:
            return None
        

    def get_status_title(self,obj):
        try:
            if obj.status in [1,2]:
                return choices_for_training[obj.status-1][1]
            
            return None

        except Exception as e:
            return None

        
    def get_training_employees(self,obj):
       try:
           emp_id=self.context.get('user_id')
           query=TrainingEmployee.objects.filter(training=obj.id,training_evaluator=emp_id,is_active=True)
           
           
           if not query.exists():
               return None
               
           data=EvaluatorListTrainingEmployeeSerializer(query,many=True).data
        
           return data

       except Exception as e:
           return None
       
    def get_training_projects(self,obj):
       try:
           query=ProjectTraining.objects.filter(training=obj.id,is_active=True)
           
           
           if not query.exists():
               return None
               
           data=ListProjectTrainingSerializer(query,many=True).data
        
           return data

       except Exception as e:
           return None
       

    def get_mode_of_training_title(self,obj):
        try:
            if obj.mode_of_training in [1,2]:
                return mode_of_training_choices[obj.mode_of_training-1][1]
            
            return None

        except Exception as e:
            return None
          
    
    def get_training_assignments(self,obj):
       try:
           query=TrainingAssignments.objects.filter(training=obj.id,is_active=True)
           
           if not query.exists():
               return None
               
           data=TrainingAssignmentsSerializer(query,many=True).data
        
           return data

       except Exception as e:
           return None


class ProjectBasedEmployeeTrainingSerializer(serializers.ModelSerializer):
    training_assignments=serializers.SerializerMethodField()
    mode_of_training_title=serializers.SerializerMethodField()
    course_data=serializers.SerializerMethodField()
    training=serializers.SerializerMethodField()
    training_status=serializers.SerializerMethodField()
    training_status_title=serializers.SerializerMethodField()
    status_title=serializers.SerializerMethodField()
  
    class Meta:
        model = Training
        fields = [
            'id',
            'training',
            'title',
            'course',
            'course_data',
            'description',
            'duration',
            'status',
            'status_title',
            'training_status',
            'training_status_title',
            'mode_of_training',
            'mode_of_training_title',
            'cost',
            'training_assignments',
            'organization',
            'created_by',
            'is_active',
            'created_at',
            'updated_at',
        ]
    

    # def get_number_of_employee(self,obj):
    #     try:
    #         count=0
    #         query=TrainingEmployee.objects.filter(training=obj.id,is_active=True)
            
    #         if query.exists():
    #             count=len(query)
    #             # print("test")
    #             return count
            
    #         return None
        
    #     except Exception as e:
    #         return None

        
    def get_status_title(self,obj):
        try:
    
            if obj.status in [1,2]:
                return choices_for_training[obj.status-1][1]
            
            return None

        except Exception as e:
            return None


    def get_course_data(self,obj):
       try:
           query=Courses.objects.filter(id=obj.course.id,is_active=True)
           
           if not query.exists():
               return None
               
           data=ListCoursesViewsetSerializers(query,many=True).data
        
           return data

       except Exception as e:
           return None
        
           
    def get_mode_of_training_title(self,obj):
        try:
            if obj.mode_of_training in [1,2]:
                return mode_of_training_choices[obj.mode_of_training-1][1]
            
            return None

        except Exception as e:
            return None
        

    def get_training(self,obj):
        try:
            
            return obj.id
            

        except Exception as e:
            return None
        

    def get_training_status_title(self,obj):
        try:
            emp_id=self.context.get('employee_id')
            # print("Test",emp_id)
            query=TrainingEmployee.objects.filter(training=obj.id,employee=emp_id,is_active=True)
            if query.exists():
                obj1=query.get()
                if obj1.training_status in [1,2,3]:
                     return status_choices[obj1.training_status-1][1]
            return None

        except Exception as e:
            return None
        
    def get_training_status(self,obj):
        try:
            emp_id=self.context.get('employee_id')
            # print("Test",emp_id)
            # print(obj.id)
            query=TrainingEmployee.objects.filter(training=obj.id,employee=emp_id,is_active=True)
            # print(query.values())
            if query.exists():
                obj1=query.get()
                return obj1.training_status
               
            return None

        except Exception as e:
            return None
        
    
    def get_training_assignments(self,obj):
       try:
           query=TrainingAssignments.objects.filter(training=obj.id,is_active=True)
           
           if not query.exists():
               return None
               
           data=TrainingAssignmentsSerializer(query,many=True).data
        
           return data

       except Exception as e:
           return None



class EmployeeTrainingSerializer(serializers.ModelSerializer):
    training_assignments=serializers.SerializerMethodField()
    training_status_title=serializers.SerializerMethodField()
    training_title=serializers.SerializerMethodField()
    description=serializers.SerializerMethodField()
    duration=serializers.SerializerMethodField()
    mode_of_training=serializers.SerializerMethodField()
    mode_of_training_title=serializers.SerializerMethodField()
    cost=serializers.SerializerMethodField()
    course=serializers.SerializerMethodField()
    organization=serializers.SerializerMethodField()
    course_data=serializers.SerializerMethodField()
    evaluator=serializers.SerializerMethodField()
    evaluator_name=serializers.SerializerMethodField()
    training_evaluator_name=serializers.SerializerMethodField()
    created_by=serializers.SerializerMethodField()
    reimbursement_status_title=serializers.SerializerMethodField()
    status=serializers.SerializerMethodField()
    status_title=serializers.SerializerMethodField()

    class Meta:
        model = TrainingEmployee
        fields = [
            'id',
            'training',
            'training_title',
            'status',
            'status_title',
            'training_status',
            'training_status_title',
            'start_date',
            'end_date',
            'reimbursed_cost',
            'reimbursement_status',
            'reimbursement_status_title',
            'training_cost',
            'training_receipt',
            'description',
            'duration',
            'mode_of_training',
            'mode_of_training_title',
            'cost',
            'course',
            'course_data',
            'training_assignments',
            'organization',
            'evaluator',
            'evaluator_name',
            'training_evaluator',
            'training_evaluator_name',
            'created_by',
            'is_active',
            'created_at',
            'updated_at',
        ]
    
    def get_evaluator_name(self, obj):
        try:
            return obj.training.evaluator.name
        except Exception as e:
            return None
        
    def get_evaluator(self, obj):
        try:
            return obj.training.evaluator.id
        except Exception as e:
            return None
        

    def get_training_evaluator_name(self, obj):
        try:
            # print(obj.training)
            return obj.training_evaluator.name
        except Exception as e:
            return None
        
    
    def get_created_by(self, obj):
        try:
            return obj.training.created_by.id
        except Exception as e:
            return None


    def get_course_data(self,obj):
       try:
           query=Courses.objects.filter(id=obj.training.course.id,is_active=True)
           
           if not query.exists():
               return None
               
           data=ListCoursesViewsetSerializers(query,many=True).data
        
           return data

       except Exception as e:
           return None
        

    def get_training_status_title(self,obj):
        try:
    
            if obj.training_status in [1,2,3]:
                return status_choices[obj.training_status-1][1]
            
            return None

        except Exception as e:
            return None
        

    def get_status(self,obj):
        try:
            
            return obj.training.status

        except Exception as e:
            return None
        
    def get_status_title(self,obj):
        try:
    
            if obj.training.status in [1,2]:
                return choices_for_training[obj.training.status-1][1]
            
            return None

        except Exception as e:
            return None

    def get_training_title(self,obj):
        try:
    
            if obj.training:
                return obj.training.title
            
            return None

        except Exception as e:
            return None
        

    def get_description(self,obj):
        try:
    
            if obj.training.description:
                return obj.training.description
            
            return None

        except Exception as e:
            return None
        

    def get_duration(self,obj):
        try:
    
            if obj.training.duration:
                return obj.training.duration
            
            return None

        except Exception as e:
            return None
        

    def get_cost(self,obj):
        try:
    
            if obj.training.cost:
                return obj.training.cost
            
            return None

        except Exception as e:
            return None
        

    def get_organization(self,obj):
        try:
    
            if obj.training.organization:
                return obj.training.organization.id
            
            return None

        except Exception as e:
            return None
        


    def get_course(self,obj):
        try:
            # print(obj.training.course)
            if obj.training.course:
                return obj.training.course.id
            
            return None

        except Exception as e:
            return None
        



    def get_mode_of_training(self,obj):
        try:
            if obj.training.mode_of_training:
                return obj.training.mode_of_training
            
            return None

        except Exception as e:
            return None

    def get_reimbursement_status_title(self,obj):
        try:
            if obj.reimbursement_status in [1,2,3,4]:
                return reimbursement_status_choices[obj.reimbursement_status-1][1]
            
            return None

        except Exception as e:
            return None
        

    def get_mode_of_training_title(self,obj):
        try:
            if obj.training.mode_of_training in [1,2]:
                return mode_of_training_choices[obj.training.mode_of_training-1][1]
            
            return None

        except Exception as e:
            return None
        
    
    def get_training_assignments(self,obj):
       try:
           query=TrainingAssignments.objects.filter(training=obj.training.id,is_active=True)
        #    print(query.values())
           
           if not query.exists():
               return None
               
           data=TrainingAssignmentsSerializer(query,many=True).data
        
           return data

       except Exception as e:
           return None


class EvaluatorListTrainingEmployeeSerializer(serializers.ModelSerializer):
    training_status_title=serializers.SerializerMethodField()
    employee_name=serializers.SerializerMethodField()
    reimbursement_status_title=serializers.SerializerMethodField()
    training_evaluator_name=serializers.SerializerMethodField()

    class Meta:
        model = TrainingEmployee
        fields = [
            'id',
            'training',
            'start_date',
            'end_date',
            'training_status',
            'training_status_title',
            'training_cost',
            'reimbursed_cost',
            'reimbursement_status',
            'reimbursement_status_title',
            'is_reimbursement',
            'training_receipt',
            'employee',
            'employee_name',
            'training_evaluator',
            'training_evaluator_name',
            'is_active',
            'created_at',
            'updated_at',
        ]


    def get_reimbursement_status_title(self,obj):
        try:

            if obj.reimbursement_status:
                return reimbursement_status_choices[obj.reimbursement_status-1][1]
            
            return None

        except Exception as e:
            return None

    
    def get_training_status_title(self,obj):
        try:
            if obj.training_status in [1,2,3]:
                return status_choices[obj.training_status-1][1]
            
            return None

        except Exception as e:
            return None
        
    def get_employee_name(self,obj):
        try:
            if obj.employee:
                return obj.employee.name
            
            return None
        except Exception as e:
            return None
        

    def get_training_evaluator_name(self,obj):
        try:
            if obj.training_evaluator:
                return obj.training_evaluator.name
            
            return None
        except Exception as e:
            return None

        


class ListTrainingEmployeeSerializer(serializers.ModelSerializer):
    training_status_title=serializers.SerializerMethodField()
    employee_training_assignment=serializers.SerializerMethodField()
    employee_name=serializers.SerializerMethodField()
    reimbursement_status_title=serializers.SerializerMethodField()
    training_evaluator_name=serializers.SerializerMethodField()

    class Meta:
        model = TrainingEmployee
        fields = [
            'id',
            'training',
            'start_date',
            'end_date',
            'training_status',
            'training_status_title',
            'training_cost',
            'reimbursed_cost',
            'reimbursement_status',
            'reimbursement_status_title',
            'is_reimbursement',
            'training_receipt',
            'employee',
            'employee_name',
            'employee_training_assignment',
            'training_evaluator',
            'training_evaluator_name',
            'is_active',
            'created_at',
            'updated_at',
        ]


    def get_reimbursement_status_title(self,obj):
        try:

            if obj.reimbursement_status:
                return reimbursement_status_choices[obj.reimbursement_status-1][1]
            
            return None

        except Exception as e:
            return None

    
    def get_training_status_title(self,obj):
        try:
            if obj.training_status in [1,2,3]:
                return status_choices[obj.training_status-1][1]
            
            return None

        except Exception as e:
            return None
        
    def get_employee_name(self,obj):
        try:
            if obj.employee:
                return obj.employee.name
            
            return None
        except Exception as e:
            return None
        

    def get_training_evaluator_name(self,obj):
        try:
            if obj.training_evaluator:
                return obj.training_evaluator.name
            
            return None
        except Exception as e:
            return None

        
    def get_employee_training_assignment(self,obj):
        try:
            assignmnet_data = self.context.get('assignment')

            # print()
            

            if assignmnet_data is None:
                return None
            
            
            # for assignment in assignmnet_data:
                
            query=EmployeeTrainingAssignment.objects.filter(employee=obj.employee,training_assignment__training=obj.training,training_assignment__id__in=assignmnet_data,assignment_status=2,is_active=True)
                # print("test")
            # print(query.values())
            if not query.exists():
                   return None
                
            serializer=EmployeeTrainingAssignmentSerializer(query,many=True).data

            return serializer


        except Exception as e:
            return None


class TrainingEmployeeSerializer(serializers.ModelSerializer):
    training_status_title=serializers.SerializerMethodField()
    employee_name=serializers.SerializerMethodField()
    reimbursement_status_title=serializers.SerializerMethodField()
    training_evaluator_name=serializers.SerializerMethodField()
    class Meta:
        model = TrainingEmployee
        fields = [
            'id',
            'training',
            'start_date',
            'end_date',
            'training_status',
            'training_cost',
            'reimbursed_cost',
            'reimbursement_status',
            'reimbursement_status_title',
            'is_reimbursement',
            'training_status_title',
            'training_receipt',
            'employee',
            'employee_name',
            'training_evaluator',
            'training_evaluator_name',
            'is_active',
            'created_at',
            'updated_at',
        ]



    def validate_training_receipt(self, value):
        try:
            if value:
                max_size = 5 * 1024 * 1024
                # print("Certificate:",max_size)
                if value.size > max_size:
                    raise serializers.ValidationError
                
                # print("Test:",value)
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError("File size cannot be greater than 5MB")
        except Exception as e:
            print(str(e))
            return None

    def get_reimbursement_status_title(self,obj):
        try:

            if obj.reimbursement_status:
                return reimbursement_status_choices[obj.reimbursement_status-1][1]
            
            return None

        except Exception as e:
            return None


    def get_employee_name(self,obj):
        try:
            if obj.employee:
                return obj.employee.name
            
            return None
        except Exception as e:
            return None
        

    def get_training_evaluator_name(self,obj):
        try:
            if obj.training_evaluator:
                return obj.training_evaluator.name
            
            return None
        except Exception as e:
            return None
    
    def get_training_status_title(self,obj):
        try:
            if obj.training_status in [1,2,3]:
                return status_choices[obj.training_status-1][1]
            
            return None

        except Exception as e:
            return None

class TrainingAssignmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingAssignments
        fields = [
            'id',
            'title',
            'training',
            'assignment',
            'marks',
            # 'submission_deadline',
            'is_active',
            'created_at',
            'updated_at',
        ]

    def validate_assignment(self, value):
        try:
            if value:
                max_size = 5 * 1024 * 1024
                # print(max_size)
                if value.size > max_size:
                    raise serializers.ValidationError
                
                # print("Test:",value)
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError("File size cannot be greater than 5MB")
        except Exception as e:
            print(str(e))
            return None


class EmployeeTrainingAssignmentSerializer(serializers.ModelSerializer):
    training_assignment_title=serializers.SerializerMethodField()
    assignment_status_title=serializers.SerializerMethodField()
   
    class Meta:
        model = EmployeeTrainingAssignment
        fields = [
            'id',
            'employee',
            'training_assignment',
            'training_assignment_title',
            'assignment_file',
            'submitted_assignment',
            'assignment_status',
            'assignment_status_title',
            'total_marks',
            'obtained_marks',
            'created_by',
            'is_active',
            'created_at',
            'updated_at',
        ]

    def validate_submitted_assignment(self, value):
        try:
            if value:
                max_size = 5 * 1024 * 1024
                # print(max_size)
                if value.size > max_size:
                    raise serializers.ValidationError
                
                # print("Test:",value)
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError("File size cannot be greater than 5MB")
        except Exception as e:
            print(str(e))
            return None
        
    def get_training_assignment_title(self,obj):
        try:
            if obj.training_assignment:
                return obj.training_assignment.title
            
            return None

        except Exception as e:
            return None
        
    def get_assignment_status_title(self,obj):
        try:
            if obj.assignment_status in [1,2]:
               return assignment_status_choices[obj.assignment_status-1][1]
            
            return None
        except Exception as e:
            return None
        
    def get_training(self,obj):
        try:
            if obj.training_assignment is not None and obj.training_assignment.training is not None:
                 return obj.training_assignment.training.id
                 
            return None
        except Exception as e:
            return None
        

    def get_training_title(self,obj):
        try:
            if obj.training_assignment is not None and obj.training_assignment.training is not None:
                 return obj.training_assignment.training.title
                 
            return None
        except Exception as e:
            return None


class EvaluatorEmployeeTrainingAssignmentSerializer(serializers.ModelSerializer):
    training_assignment_title=serializers.SerializerMethodField()
    assignment_status_title=serializers.SerializerMethodField()
    employee_name=serializers.SerializerMethodField()
    training=serializers.SerializerMethodField()
    training_title=serializers.SerializerMethodField()
   
    class Meta:
        model = EmployeeTrainingAssignment
        fields = [
            'id',
            'employee',
            'employee_name',
            'training',
            'training_title',
            'training_assignment',
            'training_assignment_title',
            'assignment_file',
            'submitted_assignment',
            'assignment_status',
            'assignment_status_title',
            'total_marks',
            'obtained_marks',
            'created_by',
            'is_active',
            'created_at',
            'updated_at',
        ]

    def get_training_assignment_title(self,obj):
        try:
            if obj.training_assignment:
                return obj.training_assignment.title
            
            return None

        except Exception as e:
            return None
        
    def get_assignment_status_title(self,obj):
        try:
            if obj.assignment_status in [1,2]:
               return assignment_status_choices[obj.assignment_status-1][1]
            
            return None
        except Exception as e:
            return None
        
    def get_training(self,obj):
        try:
            if obj.training_assignment is not None and obj.training_assignment.training is not None:
                 return obj.training_assignment.training.id
                 
            return None
        except Exception as e:
            return None
        

    def get_training_title(self,obj):
        try:
            if obj.training_assignment is not None and obj.training_assignment.training is not None:
                 return obj.training_assignment.training.title
                 
            return None
        except Exception as e:
            return None
        
    def get_employee_name(self, obj):
        try:
            return obj.employee.name
        except Exception as e:
            return None


class ProjectTrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTraining
        fields = [
            'id',
            'project',
            'training',
            'is_active',
            'created_at',
            'updated_at',
        ]

class ListProjectTrainingSerializer(serializers.ModelSerializer):
    project_title=serializers.SerializerMethodField()
    class Meta:
        model = ProjectTraining
        fields = [
            'id',
            'project',
            'project_title',
        ]

    def get_project_title(self,obj):
        try:
           
            if obj.project is not None:
               
                return obj.project.name
                 
            return None
        except Exception as e:
            return None