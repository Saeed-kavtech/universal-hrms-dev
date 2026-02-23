from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from profiles_api.models import HrmsUsers
from organizations.models import Organization,SubadminOrganization
from .serializers import *
from .models import *
from employees.models import Employees

# Create your views here.

class UserLoginLogsViewset(viewsets.ModelViewSet):
	permission_classes = [IsAuthenticated]
	
	def userLogin(self, user_id):
		try:
			user_return = {
				'status': 200, 
				'data': '', 
				'message': 'Successfully get the user organization.'
			}
			
			user = HrmsUsers.objects.get(id=user_id)		
			if user is None:
				return None
			
			user_return['current_hrmsuser'] = user
			login_logs = UserLoginLogs.objects.filter(user=user.id, is_active=True)
			if login_logs.exists():
				for log in login_logs:
					log.is_active=False
					log.save()
			
			if user.is_admin == True:
				organizations = Organization.objects.filter(user = user.id, is_active = True)
				if user.is_subadmin==True:
					subadminorg = SubadminOrganization.objects.filter(user = user.id, is_active = True)
					if not subadminorg.exists():
						#TODO has no organization or active organization
						user_return['message'] = "Sub admin not exists"
						user_return['status'] = 202
						return user_return
					
					obj=subadminorg.get()
					organizations = Organization.objects.filter(id=obj.organization.id, is_active = True)



				#TODO check if user has multi active organization
				
				if not organizations.exists():
					#TODO has no organization or active organization
					user_return['message'] = "User has no or active organization."
					user_return['status'] = 202
					return user_return
				
				count_organizations = organizations.count()
				if count_organizations > 1:
					#TODO user has multi active organizations
					# print(count_organizations)
					# for org in organizations:
					# 	if org.id == 38:
					# 		continue
					# 	org.is_active = False
					# 	org.save()
					
					user_return['message'] = "User has multi active organizations."
					user_return['status'] = 400
					return user_return 
			
				organization = organizations.get()
				user_return['data'] = organization
				log_array = {'user': user.id, 'organization': organization.id, 'is_active': True}
				serializer = UserLoginLogsSerializers(data=log_array)
				if not serializer.is_valid():
					user_return['message'] = serializer.errors
					user_return['status'] = 400
					return user_return
				serializer.save()
				
				return user_return
			
			elif user.is_employee==True:
				#TODO check if employee belongs to multi organizations
				employees = Employees.objects.filter(hrmsuser = user.id, is_active = True)
				if not employees.exists():
					#TODO has no organization or active organization
					user_return['message'] = "Employee does not belong to any organization"
					user_return['status'] = 202
					return user_return
				
				count_emp_organizations = employees.count()
				if count_emp_organizations > 1:
					#TODO employee has multi active organizations
					# print(count_organizations)
					# for org in organizations:
					# 	if org.id == 38:
					# 		continue
					# 	org.is_active = False
					# 	org.save()
					
					user_return['message'] = 'Employee has multi active organizations.'
					user_return['status'] = 400
					return user_return 
				
				employee = employees.get()
				user_return['current_employee'] = employee
				# employee organization
				organization = employee.organization
				user_return['data'] = organization
				log_array = {'user': user.id, 'organization': organization.id, 'is_active': True}
				serializer = UserLoginLogsSerializers(data=log_array)
				if not serializer.is_valid():
					user_return['message'] = serializer.errors
					user_return['status'] = 400
					return user_return
				serializer.save()
				
				return user_return
					
			else:
				user_return['message']= 'User is not an admin user'
				user_return['status'] = 400
				return user_return
			
		except Exception as e:
			user_return['status'] = 400
			user_return['message'] = str(e)
			return user_return



	def getUserOrganization(self, user_id):
		try:
			user_organization = UserLoginLogs.objects.filter(user=user_id, is_active=True)
			if user_organization.exists():
				user_organization = user_organization.first()
				return user_organization.organization
			else:
				return None
		except Exception as e:
			print(str(e))
			return None

	def userOrganization(self, user):
		try:
			user_organization = UserLoginLogs.objects.filter(user=user.id, is_active=True)

			if user_organization.exists():
				user_organization = user_organization.first()
				# print(user_organization.organization)
				return user_organization.organization
			else:
				return None
		except Exception as e:
			# print(str(e))
			return None
