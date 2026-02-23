from rest_framework import serializers
from .models import *

class LNDCertificationsSerializers(serializers.ModelSerializer):
    mode_of_course_title=serializers.SerializerMethodField()
    relevance_title=serializers.SerializerMethodField()
    certification_status_title=serializers.SerializerMethodField()
    decision=serializers.SerializerMethodField()
    department=serializers.SerializerMethodField()
    department_title=serializers.SerializerMethodField()
    employee_name=serializers.SerializerMethodField()
    team_lead_name=serializers.SerializerMethodField()
    position=serializers.SerializerMethodField()
    position_title=serializers.SerializerMethodField()
    reimbursement_status_title=serializers.SerializerMethodField()


    class Meta:
        model = LNDCertifications
        fields = [
            'id',
            'employee',
            'employee_name',
            'position',
            'position_title',
            'department',
            'department_title',
            'title',
            'duration',
            'mode_of_course',
            'mode_of_course_title',
            'relevance',
            'relevance_title',
            'cost',
            'certification_status',
            'certification_status_title',
            'course_url',
            'team_lead',
            'team_lead_name',
            'approved_by',
            'course_reason',
            'start_date',
            'end_date',
            'decision',
            'certificate',
            'certification_receipt',
            'feedback_comment',
            'reimbursement_status',
            'reimbursement_status_title',
            'is_reimbursement',
            'created_by',
            'created_at',
            'updated_at',
            'is_active',
        ]

    def get_mode_of_course_title(self,obj):
        try:
            if obj.mode_of_course:
                return course_type[obj.mode_of_course-1][1]
            
            return None
           
        except Exception as e:
            return None
        

    # def validate_certificate(self, value):
    #     try:
    #         if value:
    #             max_size = 5 * 1024 * 1024
    #             # print(max_size)
    #             if value.size > max_size:
    #                 raise serializers.ValidationError
                
    #             # print("Test:",value)
    #         return value
    #     except serializers.ValidationError:
    #         raise serializers.ValidationError("File size cannot be greater than 5MB")
    #     except Exception as e:
    #         print(str(e))
    #         return None
        

    # def validate_certification_receipt(self, value):
    #     try:
    #         if value:
    #             max_size = 5 * 1024 * 1024
    #             # print("Certificate:",max_size)
    #             if value.size > max_size:
    #                 raise serializers.ValidationError
                
    #             # print("Test:",value)
    #         return value
    #     except serializers.ValidationError:
    #         raise serializers.ValidationError("File size cannot be greater than 5MB")
    #     except Exception as e:
    #         print(str(e))
    #         return None
        
    def get_relevance_title(self,obj):
        try:
            if obj.relevance:
                return relevance_choices[obj.relevance-1][1]
            
            return None
           
        except Exception as e:
            return None

    def get_certification_status_title(self,obj):
        try:
            if obj.certification_status:
                return status_choices[obj.certification_status-1][1]
            
            return None
           
        except Exception as e:
            return None
        
    def get_decision(self,obj):
        try:
            query=LNDCertificationLogs.objects.filter(certification=obj.id,is_active=True)
            serializer=LNDCertificationLogsSerializers(query,many=True)
            return serializer.data
        except  Exception as e:
            return None
        
    def get_department(self,obj):
        try:
            if obj.employee:
               return obj.employee.department.id
            return None
        except Exception as e:
            return None
        

    def get_reimbursement_status_title(self,obj):
        try:

            if obj.reimbursement_status:
                return reimbursement_status_choices[obj.reimbursement_status-1][1]
            
            return None

        except Exception as e:
            return None
    
        
    def get_department_title(self,obj):
        try:
            if obj.employee is not None and obj.employee.department is not None:
               return obj.employee.department.title
            return None
        except Exception as e:
            return None
        

    def get_position(self,obj):
        try:
            if obj.employee:
               return obj.employee.position.id
            return None
        except Exception as e:
            return None
        
    
        
    def get_position_title(self,obj):
        try:
            if obj.employee is not None and obj.employee.position is not None:
               return obj.employee.position.title
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
        

    def get_team_lead_name(self,obj):
        try:
            if obj.team_lead:
                return obj.team_lead.name
            
            return None
        except Exception as e:
            return None
        
    
        



class LNDCertificationLogsSerializers(serializers.ModelSerializer):
    certification_status_title=serializers.SerializerMethodField()
    class Meta:
        model = LNDCertificationLogs
        fields = [
            'id',
            'certification',
            'decision_reason',
            'certification_status',
            'certification_status_title',
            'created_by',
            'created_at',
            'updated_at',
            'is_active',
        ]

    def get_certification_status_title(self,obj):
        try:
            if obj.certification_status:
                return status_choices[obj.certification_status-1][1]
            
            return None
           
        except Exception as e:
            return None
        
class SubmissionLNDCertificationsSerializers(serializers.ModelSerializer):
    reimbursement_status_title=serializers.SerializerMethodField()
    team_lead_name=serializers.SerializerMethodField()
    employee_name=serializers.SerializerMethodField()
    class Meta:
        model = LNDCertifications
        fields = [
            'id',
            'employee',
            'employee_name',
            'title',
            'certificate',
            'certification_receipt',
            'feedback_comment',
            'reimbursement_status',
            'reimbursement_status_title',
            'is_reimbursement',
            'team_lead',
            'team_lead_name',
            'created_by',
            'created_at',
            'updated_at',
            'is_active',
        ]

    
    def validate_certificate(self, value):
        try:
            if value:
                max_size = 5 * 1024 * 1024
                # print(max_size)
                if value.size > max_size:
                    raise serializers.ValidationError
                
                # print("Test:",value)
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError("Certificate file size cannot be greater than 5MB")
        except Exception as e:
            print(str(e))
            return None
        

    def validate_certification_receipt(self, value):
        try:
            if value:
                max_size = 5 * 1024 * 1024
                # print("Certificate:",max_size)
                if value.size > max_size:
                    raise serializers.ValidationError
                
                # print("Test:",value)
            return value
        except serializers.ValidationError:
            raise serializers.ValidationError("Certification receipt file size cannot be greater than 5MB")
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
        

    def get_team_lead_name(self,obj):
        try:

            if obj.team_lead:
                return obj.team_lead.name
            
            return None

        except Exception as e:
            return None
