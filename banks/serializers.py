from rest_framework import serializers
from .models import *


class BanksViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = Banks
        fields = [
            'id',
            'name',
            'short_form',
            'code',
            'is_active',
        ]

class EmployeeBankDetailsViewsetSerializers(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    bank_name = serializers.SerializerMethodField()
    bank_short_form = serializers.SerializerMethodField()
    class Meta:
        model = EmployeeBankDetails
        fields = [
            'id',
            'employee',
            'employee_name',
            'bank',
            'bank_name',
            'bank_short_form',
            'branch_name',
            'account_no',
            'account_title',
            'iban',
            'is_active'
        ]
    def get_bank_name(self, obj):
        try:
            if obj.bank is not None: 
                return obj.bank.name
            return None
        except:
            return None

    def get_employee_name(self, obj):
        try:
            if obj.employee is not None:
                return obj.employee.name
            return None
        except:
            return None

    def get_bank_short_form(self, obj):
        try:
            if obj.bank is not None:
                return obj.bank.short_form
            return None
        except:
            return None
        
class OrganizationBankDetailViewsetSerializers(serializers.ModelSerializer):
    class Meta:
        model = OrganizationBankDetail
        fields = '__all__'