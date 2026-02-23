from rest_framework import serializers
from .models import PFRecords,PayrollCustomisedPFProcesses,PayrollCustomisedTrainingProcesses,PayrollCustomisedCertificationsProcesses,ProcessedSalary,PayrollAttributes, PayrollBatches, PayrollBatchCompositions, EmployeePayrollConfiguration, CompositionAttributes, MonthlyDistribution, EligibleEmployees, FixedDistribution, VariableDistributions, valueTypeChoices, customisedAttributes, PayrollBatchAttributes, PayrollCustomisedGymProcesses, PayrollCustomisedMedicalProcesses, SalaryBatch, SalaryBatchAttributes, TaxSlab


class PayrollAttributesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model =  CompositionAttributes
        fields = [
            'id',
            'title',
            'organization',
            'level',
            'is_active'
        ]

class UpdatePayrollAttributesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = CompositionAttributes
        fields = [
            'id',
            'title',
            'level',
            'is_active'
        ]



class PayrollBatchesViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = PayrollBatches
        fields = [
            'id',
            'batch_no',
            'title',
            'batch_status',
            'start_date',
            'end_date',
            'organization',
            'is_lock',
            'lock_by',
            'is_active',
            'country'
        ]


class UpdatePayrollBatchsViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = PayrollBatches
        fields = [
            'id',
            'batch_status',
            'end_date'
        ]

class PayrollBatchCompositionsViewsetSerializers(serializers.ModelSerializer):
    payroll_compositions_attribute_title = serializers.SerializerMethodField()
    payroll_batch_no = serializers.SerializerMethodField()
    class Meta:
        model = PayrollBatchCompositions
        fields = [
            'id',
            'payroll_compositions_attribute',
            'payroll_compositions_attribute_title',
            'payroll_batch',
            'payroll_batch_no',
            'attribute_percentage',
            'is_active'
        ]

    def get_payroll_compositions_attribute_title(self, obj):
        try:
            return obj.payroll_compositions_attribute.title
        except Exception as e:
            print(str(e))
            return None
        
        
    def get_payroll_batch_no(self, obj):
        try:
            return obj.payroll_batch.batch_no
        except Exception as e:
            print(str(e))
            return None
        


class UpdatePayrollBatchCompositionsViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = PayrollBatchCompositions
        fields = [
            'id',
            'attribute_percentage',
            'is_active'
        ]

# serializer for Employee Payroll Configuration

# class EmployeePayrollConfigurationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = EmployeePayrollConfiguration
#         fields = '__all__'

class EmployeePayrollConfigurationSerializer(serializers.ModelSerializer):
    payroll_batch_title = serializers.SerializerMethodField()
    employee_id = serializers.ReadOnlyField(source='employee.id')
    
    # employee = serializers.IntegerField()
    employee_name = serializers.ReadOnlyField(source='employee.name')
    employee_email = serializers.ReadOnlyField(source='employee.personal_email')
    staff_classification = serializers.ReadOnlyField(source='employee.staff_classification.title')

    class Meta:
        model = EmployeePayrollConfiguration
        fields = ['employee','employee_id','organization','employee_name','employee_email', 'staff_classification','takeAway','is_salary_allowed', 'is_payslip_allowed','payroll_batch','payroll_batch_title', 'is_active','created_at','updated_at']
    
    def get_payroll_batch_title(self, obj):
        return obj.payroll_batch.title if obj.payroll_batch else None  
        
        
class PayrollAttributesSerializer(serializers.ModelSerializer):
    valueTypeChoices_title = serializers.SerializerMethodField()
    class Meta:
        model = PayrollAttributes
        fields = '__all__'
    def get_valueTypeChoices_title(self, obj):
        return obj.valueType.title if obj.valueType else None
        
        
class MonthlyDistributionSerializer(serializers.ModelSerializer):
    staff_classification_title = serializers.SerializerMethodField()
    class Meta:
        model = MonthlyDistribution
        fields = '__all__'
    def get_staff_classification_title(self, obj):
        return obj.staff_classification.title if obj.staff_classification else None
        
                
class EligibleEmployeesSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    class Meta:
        model = EligibleEmployees
        fields = '__all__'
    def get_employee_name(self, obj):
        return obj.employee.name if obj.employee else None
        
class FixedDistributionSerializer(serializers.ModelSerializer):
    payroll_attribute_title = serializers.SerializerMethodField()
    class Meta:
        model = FixedDistribution
        fields = '__all__'
    def get_payroll_attribute_title(self, obj):
        return obj.payroll_attribute.title if obj.payroll_attribute else None
        
class VariableDistributionsSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    class Meta:
        model = VariableDistributions
        fields = '__all__'   
    def get_employee_name(self, obj):
        return obj.employee.name if obj.employee else None   
        
class customisedAttributesSerializer(serializers.ModelSerializer):
    class Meta:
        model = customisedAttributes
        fields = '__all__'      

class valueTypeChoicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = valueTypeChoices
        fields = '__all__' 
        
class SalaryBatchSerilaizer(serializers.ModelSerializer):
    payroll_batch_title = serializers.SerializerMethodField()
    class Meta:
        model = SalaryBatch
        fields = '__all__' 
    def get_payroll_batch_title(self, obj):
        return obj.payroll_batch.title if obj.payroll_batch else None
        
class SalaryBatchAttributeSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = SalaryBatchAttributes
        fields = '__all__' 
    
        
class PayrollBatchAttributesSerializer(serializers.ModelSerializer):
    payroll_batch_id = serializers.SerializerMethodField()
    payroll_attribute_title = serializers.SerializerMethodField()
    payroll_attribute_payroll_type = serializers.SerializerMethodField()
    payroll_attribute_is_customized = serializers.SerializerMethodField()
    payroll_attribute_valueType_title = serializers.SerializerMethodField()
    payroll_attribute_valueType_id = serializers.SerializerMethodField()
    payroll_attribute_is_organization_base = serializers.SerializerMethodField()
    payroll_attribute_is_employee_base = serializers.SerializerMethodField()
    payroll_attribute_is_customized = serializers.SerializerMethodField()
    class Meta:
        model = PayrollBatchAttributes
        fields = '__all__'  
    def get_payroll_batch_id(self, obj):
        return obj.payroll_batch.id if obj.payroll_batch else None
    def get_payroll_attribute_title(self, obj):
        return obj.payroll_attribute.title if obj.payroll_attribute else None
    def get_payroll_attribute_payroll_type(self, obj):
        return obj.payroll_attribute.payroll_type if obj.payroll_attribute else None
    def get_payroll_attribute_is_customized(self, obj):
        return obj.payroll_attribute.is_customized if obj.payroll_attribute else None
    def get_payroll_attribute_valueType_title(self, obj):
        return obj.payroll_attribute.valueType.title if obj.payroll_attribute and obj.payroll_attribute.valueType else None
    def get_payroll_attribute_valueType_id(self, obj):
        return obj.payroll_attribute.valueType.id if obj.payroll_attribute and obj.payroll_attribute.valueType else None
    def get_payroll_attribute_is_organization_base(self, obj):
        return obj.payroll_attribute.is_organization_base if obj.payroll_attribute else None
    def get_payroll_attribute_is_employee_base(self, obj):
        return obj.payroll_attribute.is_employee_base if obj.payroll_attribute else None
    def get_payroll_attribute_is_customized(self, obj):
        return obj.payroll_attribute.is_customized if obj.payroll_attribute else None
    
    
class SalaryBatchAttributesSerializer(serializers.ModelSerializer):
    # payroll_batch_id = serializers.SerializerMethodField()
    payroll_attribute = serializers.SerializerMethodField()
    payroll_batch = serializers.SerializerMethodField()
    payroll_attribute_title = serializers.SerializerMethodField()
    payroll_attribute_payroll_type = serializers.SerializerMethodField()
    payroll_attribute_is_customized = serializers.SerializerMethodField()
    payroll_attribute_valueType_title = serializers.SerializerMethodField()
    payroll_attribute_valueType_id = serializers.SerializerMethodField()
    payroll_attribute_is_organization_base = serializers.SerializerMethodField()
    payroll_attribute_is_employee_base = serializers.SerializerMethodField()
    # payroll_attribute_is_customized = serializers.SerializerMethodField()
    class Meta:
        model = SalaryBatchAttributes
        fields = '__all__'  
    def get_payroll_attribute(self, obj):
        return obj.payroll_batch_attribute.payroll_attribute.id if obj.payroll_batch_attribute else None
    def get_payroll_batch(self, obj):
        return obj.salary_batch.payroll_batch.id if obj.salary_batch else None
    def get_payroll_attribute_title(self, obj):
        return obj.payroll_batch_attribute.payroll_attribute.title if obj.payroll_batch_attribute else None
    def get_payroll_attribute_payroll_type(self, obj):
        return obj.payroll_batch_attribute.payroll_attribute.payroll_type if obj.payroll_batch_attribute else None
    def get_payroll_attribute_is_customized(self, obj):
        return obj.payroll_batch_attribute.payroll_attribute.is_customized if obj.payroll_batch_attribute else None
    def get_payroll_attribute_valueType_title(self, obj):
        return obj.payroll_batch_attribute.payroll_attribute.valueType.title if obj.payroll_batch_attribute and obj.payroll_batch_attribute.payroll_attribute.valueType  else None
    def get_payroll_attribute_valueType_id(self, obj):
        return obj.payroll_batch_attribute.payroll_attribute.valueType.id if obj.payroll_batch_attribute and obj.payroll_batch_attribute.payroll_attribute.valueType else None
    def get_payroll_attribute_is_organization_base(self, obj):
        return obj.payroll_batch_attribute.payroll_attribute.is_organization_base if obj.payroll_batch_attribute else None
    def get_payroll_attribute_is_employee_base(self, obj):
        return obj.payroll_batch_attribute.payroll_attribute.is_employee_base if obj.payroll_batch_attribute else None
    # def get_payroll_attribute_is_customized(self, obj):
    #     return obj.payroll_attribute.is_customized if obj.payroll_attribute else None
    
class ProcessedSalarySerilaizer(serializers.ModelSerializer):
    employee_id = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    jobtitle = serializers.SerializerMethodField()
    joining_date = serializers.SerializerMethodField()
    employee_type = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    cnic = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    class Meta:
        model = ProcessedSalary
        fields= '__all__'
    def get_employee_id(self, obj):
        return obj.employee.id if obj.employee else None
    def get_employee_name(self, obj):
        return obj.employee.name if obj.employee else None
    def get_jobtitle(self, obj):
        return obj.employee.staff_classification.title if obj.employee and obj.employee.staff_classification else None
    def get_joining_date(self, obj):
        return obj.employee.joining_date if obj.employee else None
    def get_employee_type(self, obj):
        return obj.employee.employee_type.title if obj.employee and obj.employee.employee_type  else None
    def get_email(self, obj):
        return obj.employee.official_email if obj.employee  else None
    def get_cnic(self, obj):
        return obj.employee.cnic_no if obj.employee  else None
    def get_department(self, obj):
        return obj.employee.department.title if obj.employee and obj.employee.department  else None
    
    
    
    
class PayrollCustomisedGymSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollCustomisedGymProcesses
        fields = '__all__' 
        
class PayrollCustomisedMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollCustomisedMedicalProcesses
        fields = '__all__' 
        
class PayrollCustomisedCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollCustomisedCertificationsProcesses
        fields = '__all__' 
        
        
class PayrollCustomisedTrainingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollCustomisedTrainingProcesses
        fields = '__all__' 
        
class PayrollCustomisedPFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollCustomisedPFProcesses
        fields = '__all__' 
        
class PFSerializer(serializers.ModelSerializer):
    employee_id = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    class Meta:
        model = PFRecords
        fields = '__all__' 
    def get_employee_id(self, obj):
        return obj.employee.id if obj.employee else None
    def get_employee_name(self, obj):
        return obj.employee.name if obj.employee else None
        
        
class TaxSlabSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxSlab
        fields = '__all__'
        
        
class EmployeeProcessedSalarySerializer(serializers.ModelSerializer):
    salary_batch_details = SalaryBatchSerilaizer(source='salary_batch', read_only=True)
    employee_id = serializers.SerializerMethodField()
    employee_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcessedSalary
        fields = '__all__'
    def get_employee_id(self, obj):
        return obj.employee.id if obj.employee else None
    def get_employee_name(self, obj):
        return obj.employee.name if obj.employee else None 
        

    
        