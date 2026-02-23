# apps/feedback/permissions.py
from django.db.models import Q
from requests import request
from employees.models import Employees, EmployeeProjects, EmployeeRoles
from projects.models import Projects
from profiles_api.models import HrmsUsers
from rest_framework.exceptions import ValidationError
import jwt


class UserDataManager:
    """
    Manages user data extraction from JWT tokens AND database
    """
    
    # High-level roles from login response
    HIGH_LEVEL_ROLES = [
        "Project Manager",
        "Associate Project Manager", 
        "Team lead",
        "Associate Team Lead",
        "HR",
        "Technical Project Manager"
    ]
    
    @staticmethod
    def extract_user_data_from_token(request):
        """
        Extract user data directly from JWT token
        """
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                decoded = jwt.decode(token, options={"verify_signature": False})
                
                # Extract data from token
                user_data = {
                    'user_id': decoded.get('user_id'),
                    'org_id': decoded.get('org_id') or decoded.get('payload', {}).get('organization_id'),
                    'is_admin': decoded.get('admin', False) or decoded.get('is_admin', False),
                    'is_employee': decoded.get('is_employee', False),
                    'employee_id': decoded.get('payload', {}).get('employee_id') if decoded.get('payload') else None,
                }
                return user_data
        except Exception:
            pass
        return {}

    @staticmethod
    def get_user_employee_record(user_id):
        """
        Get employee record for user (like login view does)
        """
        try:
            employee = Employees.objects.filter(
                Q(hrmsuser_id=user_id) | Q(hrms_user_id=user_id),
                is_active=True
            ).select_related('position', 'department').first()
            
            if employee:
                # Get position data (like login view)
                position_data = None
                if employee.position:
                    position_data = {
                        'id': employee.position.id,
                        'title': employee.position.title,
                        'code': employee.position.code
                    }
                
                # Get department data (like login view)
                department_data = None
                if employee.department:
                    department_data = {
                        'id': employee.department.id,
                        'title': employee.department.title,
                        'code': getattr(employee.department, 'code', None)
                    }
                
                return {
                    'employee': employee,
                    'position': position_data,
                    'department': department_data
                }
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_user_project_roles(user_id, employee_id=None, org_id=None):
        """
        Get user's project roles EXACTLY like login view does
        """
        project_roles = []
        
        try:
            if employee_id:
                employee_roles = EmployeeRoles.objects.filter(
                    employee_project__employee_id=employee_id,
                    is_active=True
                ).select_related(
                    'role',
                    'role__role_type',
                    'employee_project__project'
                )
                
                for er in employee_roles:
                    # Filter by organization if provided
                    if org_id and er.employee_project.project.organization_id != org_id:
                        continue
                    
                    project_roles.append({
                        'id': er.role.id,
                        'title': er.role.title,
                        'code': er.role.code,
                        'role_type': er.role.role_type.title if er.role.role_type else None,
                        'role_type_id': er.role.role_type.id if er.role.role_type else None,
                        'project': {
                            'id': er.employee_project.project.id,
                            'name': er.employee_project.project.name,
                            'code': er.employee_project.project.code
                        },
                        'start_date': er.start_date,
                        'end_date': er.end_date
                    })
        except Exception:
            pass
        
        return project_roles
    
    @staticmethod
    def get_user_high_level_project_roles(user_id, employee_id=None, org_id=None):
        """
        Get only high-level project roles for user
        """
        all_project_roles = UserDataManager.get_user_project_roles(user_id, employee_id, org_id)
        high_level_roles = []
        
        for role in all_project_roles:
            if role['title'] in UserDataManager.HIGH_LEVEL_ROLES:
                high_level_roles.append(role)
        
        return high_level_roles
    
    @staticmethod
    def get_high_level_roles(request):
        """
        Get high-level roles from database (like login view), NOT from token
        """
        # Get user data from token
        user_data = UserDataManager.extract_user_data_from_token(request)
        user_id = user_data.get('user_id')
        org_id = user_data.get('org_id')
        employee_id = user_data.get('employee_id')
        
        if not user_id and request.user.is_authenticated:
            user_id = request.user.id
        
        if not user_id:
            return []
        
        # Check if user is admin first
        try:
            hrms_user = HrmsUsers.objects.get(id=user_id)
            if getattr(hrms_user, 'is_admin', False):
                return [{'title': 'Admin', 'code': 'ADMIN'}]
        except Exception:
            pass
        
        # Get employee record if user is employee
        if not employee_id:
            employee_info = UserDataManager.get_user_employee_record(user_id)
            if employee_info:
                employee_id = employee_info['employee'].id
        
        # Get high-level project roles from database
        high_level_roles = UserDataManager.get_user_high_level_project_roles(
            user_id, 
            employee_id, 
            org_id
        )
        
        return high_level_roles
    
    @staticmethod
    def user_has_high_level_role(request):
        """Check if user has any high-level role in projects"""
        roles = UserDataManager.get_high_level_roles(request)
        
        # Also check for admin role
        if roles and roles[0].get('title') == 'Admin':
            return True
        
        return len(roles) > 0
    
    @staticmethod
    def user_is_admin(request):
        """Check if user is admin"""
        # Check database directly
        user_data = UserDataManager.extract_user_data_from_token(request)
        user_id = user_data.get('user_id')
        
        if not user_id and request.user.is_authenticated:
            user_id = request.user.id
        
        if user_id:
            try:
                hrms_user = HrmsUsers.objects.get(id=user_id)
                return getattr(hrms_user, 'is_admin', False)
            except Exception:
                pass
        
        return False
    
    @staticmethod
    def get_user_permission_details(request):
        """
        Get comprehensive permission details like login response
        """
        # Initialize with defaults FIRST
        details = {
            'user_id': None,
            'org_id': None,
            'employee_id': None,
            'is_admin': False,
            'project_roles': [],
            'all_project_roles': [],
            'employee_info': None
        }
        
        try:
            user_data = UserDataManager.extract_user_data_from_token(request)
            user_id = user_data.get('user_id')
            org_id = user_data.get('org_id')
            employee_id = user_data.get('employee_id')
            
            if not user_id and request.user.is_authenticated:
                user_id = request.user.id
            
            # Update details with actual values
            details['user_id'] = user_id
            details['org_id'] = org_id
            details['employee_id'] = employee_id
            
            if user_id:
                # Get admin status
                try:
                    hrms_user = HrmsUsers.objects.get(id=user_id)
                    details['is_admin'] = getattr(hrms_user, 'is_admin', False)
                except (HrmsUsers.DoesNotExist, Exception):
                    details['is_admin'] = False
                
                # Get employee info
                if not employee_id:
                    employee_info = UserDataManager.get_user_employee_record(user_id)
                    if employee_info and 'employee' in employee_info:
                        details['employee_info'] = {
                            'id': employee_info['employee'].id,
                            'name': employee_info['employee'].name,
                            'emp_code': employee_info['employee'].emp_code,
                            'position': employee_info.get('position'),
                            'department': employee_info.get('department')
                        }
                        employee_id = employee_info['employee'].id
                        details['employee_id'] = employee_id
                
                # Get all project roles
                if employee_id:
                    all_roles = UserDataManager.get_user_project_roles(
                        user_id, employee_id, org_id
                    )
                    if all_roles is None:
                        all_roles = []
                    details['all_project_roles'] = all_roles
                    
                    # Filter for high-level roles
                    project_roles = []
                    if isinstance(all_roles, list):
                        for role in all_roles:
                            if isinstance(role, dict) and role.get('title') in UserDataManager.HIGH_LEVEL_ROLES:
                                project_roles.append(role)
                    details['project_roles'] = project_roles
        
        except Exception:
            # Return default details even on error
            pass
        
        return details


class PermissionCore:
    """
    Core permission checking logic - UPDATED to use database queries
    """
    
    @staticmethod
    def get_organization_id(request):
        """Get organization ID from request"""
        # Check token
        user_data = UserDataManager.extract_user_data_from_token(request)
        org_id = user_data.get('org_id')
        
        if org_id:
            return org_id
        
        # Fallback to database if not in token
        if request.user.is_authenticated:
            try:
                # Get user permission details
                details = UserDataManager.get_user_permission_details(request)
                if details.get('employee_info'):
                    employee = Employees.objects.get(id=details['employee_info']['id'])
                    if employee.organization_id:
                        return employee.organization_id
            except Exception:
                pass
        
        return None
    
    @staticmethod
    def get_employee_id(request):
        """Get employee ID from request"""
        # Check token
        user_data = UserDataManager.extract_user_data_from_token(request)
        employee_id = user_data.get('employee_id')
        
        if employee_id:
            return employee_id
        
        # Get from permission details
        details = UserDataManager.get_user_permission_details(request)
        if details.get('employee_info'):
            return details['employee_info']['id']
        
        return None
    
    @staticmethod
    def user_has_role_in_project(user_id, employee_id, project_id, role_titles=None):
        """
        Check if user has specific role(s) in a project
        """
        try:
            query = EmployeeRoles.objects.filter(
                employee_project__employee_id=employee_id,
                employee_project__project_id=project_id,
                is_active=True
            ).select_related('role')
            
            if role_titles:
                query = query.filter(role__title__in=role_titles)
            
            has_role = query.exists()
            
            # Get role details
            if has_role:
                roles = []
                for er in query:
                    roles.append({
                        'title': er.role.title,
                        'code': er.role.code,
                        'id': er.role.id
                    })
                return True, roles
            
            return False, []
        except Exception:
            return False, []
    
    @staticmethod
    def can_assign_to_employee(request, receiver_employee, project_id=None):
        """
        Check if user can assign feedback/scores to an employee
        """
        # Check if receiver_employee is None
        if receiver_employee is None:
            return False, "Employee not specified", []
        
        try:
            org_id = PermissionCore.get_organization_id(request)
            
            # Organization validation
            if org_id and hasattr(receiver_employee, 'organization_id'):
                if receiver_employee.organization_id != org_id:
                    return False, "Employee belongs to different organization", []
            
            # Get user permission details
            user_details = UserDataManager.get_user_permission_details(request)
            
            # Ensure user_details is a dictionary
            if not isinstance(user_details, dict):
                user_details = {}
            
            user_id = user_details.get('user_id')
            is_admin = user_details.get('is_admin', False)
            project_roles = user_details.get('project_roles', [])
            
            # Check admin permission
            if is_admin:
                allowed_projects = PermissionCore._get_employee_projects(receiver_employee, org_id)
                return True, "Admin permission", list(allowed_projects)
            
            # Check if user has project roles
            if project_roles:
                # User has high-level roles in some projects
                employee_projects = PermissionCore._get_employee_projects(receiver_employee, org_id)
                user_projects_with_high_role = set()
                
                for role in project_roles:
                    if isinstance(role, dict) and 'project' in role:
                        project_info = role.get('project', {})
                        if isinstance(project_info, dict) and 'id' in project_info:
                            user_projects_with_high_role.add(project_info['id'])
                
                # Find intersection
                allowed_projects = list(set(employee_projects) & user_projects_with_high_role)
                
                if allowed_projects:
                    return True, "High-level role permission", allowed_projects
            
            # Check if user is project assigner
            if user_id:
                is_assigner = PermissionCore._is_project_assigner(user_id, receiver_employee, org_id)
                
                if is_assigner:
                    assigner_projects = PermissionCore._get_assigner_projects(user_id, receiver_employee, org_id)
                    
                    if assigner_projects:
                        return True, "Project assigner permission", list(assigner_projects)
            
            return False, "No permission to assign to this employee", []
            
        except Exception as e:
            return False, f"Permission check error: {str(e)}", []
    
    @staticmethod
    def _get_employee_projects(employee, org_id):
        """Get all projects for an employee"""
        query = EmployeeProjects.objects.filter(
            employee=employee,
            is_active=True,
            project__is_active=True
        )
        
        if org_id:
            query = query.filter(
                project__organization_id=org_id,
                employee__organization_id=org_id
            )
        
        return list(query.values_list('project_id', flat=True))
    
    @staticmethod
    def _is_project_assigner(user_id, employee, org_id):
        """Check if user is project assigner for this employee"""
        try:
            hrms_user = HrmsUsers.objects.get(id=user_id)
            query = EmployeeProjects.objects.filter(
                project_assigned_by=hrms_user,
                employee=employee,
                is_active=True
            )
            
            if org_id:
                query = query.filter(
                    project__organization_id=org_id,
                    employee__organization_id=org_id
                )
            
            return query.exists()
        except Exception:
            return False
    
    @staticmethod
    def _get_assigner_projects(user_id, employee, org_id):
        """Get projects where user is assigner for this employee"""
        try:
            hrms_user = HrmsUsers.objects.get(id=user_id)
            query = EmployeeProjects.objects.filter(
                project_assigned_by=hrms_user,
                employee=employee,
                is_active=True,
                project__is_active=True
            )
            
            if org_id:
                query = query.filter(
                    project__organization_id=org_id,
                    employee__organization_id=org_id
                )
            
            return list(query.values_list('project_id', flat=True))
        except Exception:
            return []
    
    @staticmethod
    def get_assignable_projects_for_user(request, employee_id=None):
        """Get projects user can assign to"""
        try:
            user_details = UserDataManager.get_user_permission_details(request)
            user_id = user_details.get('user_id')
            org_id = user_details.get('org_id')
            is_admin = user_details.get('is_admin')
            user_project_roles = user_details.get('project_roles', [])
            
            if not user_id:
                return []
            
            projects_list = []
            
            if is_admin:
                # Admin can assign to all projects
                query = Projects.objects.filter(is_active=True)
                if org_id:
                    query = query.filter(organization_id=org_id)
                
                if employee_id:
                    employee_projects = EmployeeProjects.objects.filter(
                        employee_id=employee_id,
                        is_active=True,
                        project__is_active=True
                    )
                    if org_id:
                        employee_projects = employee_projects.filter(
                            project__organization_id=org_id,
                            employee__organization_id=org_id
                        )
                    project_ids = employee_projects.values_list('project_id', flat=True)
                    query = query.filter(id__in=project_ids)
                
                projects = list(query.values('id', 'name', 'code'))
                for project in projects:
                    projects_list.append({
                        'id': project['id'],
                        'name': project['name'],
                        'code': project['code'],
                        'permission_type': 'admin'
                    })
            
            elif user_project_roles:
                # User has high-level project roles
                # Get projects where user has high-level roles
                user_projects_with_high_role = {}
                for role in user_project_roles:
                    project_id = role['project']['id']
                    if project_id not in user_projects_with_high_role:
                        user_projects_with_high_role[project_id] = {
                            'id': project_id,
                            'name': role['project']['name'],
                            'code': role['project']['code'],
                            'permission_type': 'high_level_role',
                            'roles': []
                        }
                    user_projects_with_high_role[project_id]['roles'].append({
                        'title': role['title'],
                        'code': role['code']
                    })
                
                # Filter by employee if specified
                if employee_id:
                    employee_project_ids = set(PermissionCore._get_employee_projects(
                        Employees.objects.get(id=employee_id), org_id
                    ))
                    
                    # Keep only projects where both user has high-level role AND employee is assigned
                    for project_id in list(user_projects_with_high_role.keys()):
                        if project_id not in employee_project_ids:
                            del user_projects_with_high_role[project_id]
                
                projects_list = list(user_projects_with_high_role.values())
            
            else:
                # Regular users can only assign to projects they're assigners for
                try:
                    hrms_user = HrmsUsers.objects.get(id=user_id)
                    query = EmployeeProjects.objects.filter(
                        project_assigned_by=hrms_user,
                        is_active=True,
                        project__is_active=True
                    )
                    
                    if org_id:
                        query = query.filter(
                            project__organization_id=org_id,
                            employee__organization_id=org_id
                        )
                    
                    if employee_id:
                        query = query.filter(employee_id=employee_id)
                    
                    for ep in query.select_related('project').distinct('project'):
                        projects_list.append({
                            'id': ep.project.id,
                            'name': ep.project.name,
                            'code': ep.project.code,
                            'permission_type': 'project_assigner'
                        })
                except HrmsUsers.DoesNotExist:
                    pass
            
            return projects_list
            
        except Exception:
            return []
    
    @staticmethod
    def get_assignable_employees_for_user(request, project_id=None):
        """Get employees user can assign to"""
        try:
            user_details = UserDataManager.get_user_permission_details(request)
            user_id = user_details.get('user_id')
            org_id = user_details.get('org_id')
            is_admin = user_details.get('is_admin')
            user_project_roles = user_details.get('project_roles', [])
            
            if not org_id:
                return Employees.objects.none()
            
            base_query = Employees.objects.filter(
                is_active=True,
                organization_id=org_id
            )
            
            if is_admin:
                # Admin can assign to all employees
                if project_id:
                    employee_ids = EmployeeProjects.objects.filter(
                        project_id=project_id,
                        is_active=True,
                        project__is_active=True,
                        project__organization_id=org_id,
                        employee__organization_id=org_id
                    ).values_list('employee_id', flat=True).distinct()
                    
                    return base_query.filter(id__in=employee_ids)
                return base_query
            
            elif user_project_roles:
                # User has high-level project roles
                # Get employees in projects where user has high-level role
                if project_id:
                    # Check if user has high-level role in this specific project
                    has_role_in_project = False
                    for role in user_project_roles:
                        if role['project']['id'] == int(project_id):
                            has_role_in_project = True
                            break
                    
                    if has_role_in_project:
                        # Get employees in this project
                        employee_ids = EmployeeProjects.objects.filter(
                            project_id=project_id,
                            is_active=True,
                            project__is_active=True,
                            project__organization_id=org_id,
                            employee__organization_id=org_id
                        ).values_list('employee_id', flat=True).distinct()
                        
                        return base_query.filter(id__in=employee_ids)
                    else:
                        return Employees.objects.none()
                else:
                    # Get all projects where user has high-level role
                    project_ids = [role['project']['id'] for role in user_project_roles]
                    employee_ids = EmployeeProjects.objects.filter(
                        project_id__in=project_ids,
                        is_active=True,
                        project__is_active=True,
                        project__organization_id=org_id,
                        employee__organization_id=org_id
                    ).values_list('employee_id', flat=True).distinct()
                    
                    return base_query.filter(id__in=employee_ids)
            
            else:
                # Regular users can only assign to employees they're assigners for
                if user_id:
                    try:
                        hrms_user = HrmsUsers.objects.get(id=user_id)
                        employee_ids = EmployeeProjects.objects.filter(
                            project_assigned_by=hrms_user,
                            is_active=True,
                            project__is_active=True,
                            project__organization_id=org_id,
                            employee__organization_id=org_id
                        ).values_list('employee_id', flat=True).distinct()
                        
                        if project_id:
                            # Filter for specific project
                            project_employee_ids = EmployeeProjects.objects.filter(
                                project_id=project_id,
                                project_assigned_by=hrms_user,
                                is_active=True,
                                project__is_active=True,
                                project__organization_id=org_id,
                                employee__organization_id=org_id
                            ).values_list('employee_id', flat=True).distinct()
                            
                            return base_query.filter(id__in=project_employee_ids)
                        
                        return base_query.filter(id__in=employee_ids)
                    except HrmsUsers.DoesNotExist:
                        return Employees.objects.none()
                
                return Employees.objects.none()
                
        except Exception:
            return Employees.objects.none()


class FeedbackPermissions:
    """
    Public interface for feedback permissions
    """
    
    @staticmethod
    def get_user_organization(request):
        return PermissionCore.get_organization_id(request)
    
    @staticmethod
    def get_permission_status(request):
        """Get comprehensive permission status"""
        try:
            # Get user data
            user_data = UserDataManager.extract_user_data_from_token(request)
            user_id = user_data.get('user_id')
            
            if not user_id and request.user.is_authenticated:
                user_id = request.user.id
            
            # Check permissions
            is_admin = UserDataManager.user_is_admin(request)
            has_high_level_role = UserDataManager.user_has_high_level_role(request)
            
            # Check if user has assigned projects
            has_assigned_projects = False
            if user_id:
                try:
                    hrms_user = HrmsUsers.objects.get(id=user_id)
                    has_assigned_projects = EmployeeProjects.objects.filter(
                        project_assigned_by=hrms_user,
                        is_active=True
                    ).exists()
                except Exception:
                    pass
            
            # Determine if user can assign
            can_assign = is_admin or has_high_level_role or has_assigned_projects
            
            # Get high-level role details
            high_level_roles = UserDataManager.get_high_level_roles(request)
            specific_role_details = high_level_roles[0] if high_level_roles else None
            
            # Check if user is employee
            is_employee = user_data.get('is_employee', False)
            employee_id = PermissionCore.get_employee_id(request)
            
            # Get employee record if exists
            employee_record = None
            if employee_id:
                try:
                    employee = Employees.objects.get(id=employee_id, is_active=True)
                    employee_record = {
                        'id': employee.id,
                        'name': employee.name,
                        'emp_code': employee.emp_code,
                        'department': employee.department.title if employee.department else None,
                        'official_email': employee.official_email
                    }
                except Employees.DoesNotExist:
                    pass
            
            permission_status = {
                "can_assign": can_assign,
                "is_admin": is_admin,
                "has_assigned_projects": has_assigned_projects,
                "is_project_assigner": has_assigned_projects,
                "has_high_level_role": has_high_level_role,
                "has_active_role": is_employee or has_high_level_role or has_assigned_projects,
                "organization_id": PermissionCore.get_organization_id(request),
                "message": "Permission check successful",
                "specific_role_details": specific_role_details,
                "permission_breakdown": {
                    'is_admin': is_admin,
                    'is_employee': is_employee,
                    'has_high_level_role': has_high_level_role,
                    'has_assigned_projects': has_assigned_projects,
                    'high_level_roles_count': len(high_level_roles),
                    'employee_record': employee_record is not None,
                    'user_id': user_id
                },
                "all_roles": [role.get('title') for role in high_level_roles],
                "project_roles": high_level_roles,
                "employee_record": employee_record
            }
            
            return permission_status
            
        except Exception as e:
            return {
                "can_assign": False,
                "is_admin": False,
                "has_assigned_projects": False,
                "is_project_assigner": False,
                "has_high_level_role": False,
                "has_active_role": False,
                "organization_id": None,
                "message": f"Permission check error: {str(e)}",
                "specific_role_details": None
            }
    
    @staticmethod
    def can_assign_feedback(request, receiver_employee, project_id=None):
        return PermissionCore.can_assign_to_employee(request, receiver_employee, project_id)
    
    @staticmethod
    def get_assignable_projects(request, employee_id=None):
        return PermissionCore.get_assignable_projects_for_user(request, employee_id)
    
    @staticmethod
    def get_assignable_employees(request, project_id=None):
        return PermissionCore.get_assignable_employees_for_user(request, project_id)
    
    @staticmethod
    def validate_feedback_assignment(request, receiver_employee_id, project_id):
        """Validate feedback assignment"""
        try:
            org_id = PermissionCore.get_organization_id(request)
            employee_filter = Q(id=receiver_employee_id, is_active=True)
            if org_id:
                employee_filter &= Q(organization_id=org_id)
            
            receiver_employee = Employees.objects.get(employee_filter)
        except Employees.DoesNotExist:
            raise ValidationError({
                "receiver": "Employee not found, inactive, or not in your organization"
            })
        
        can_assign, reason, allowed_projects = FeedbackPermissions.can_assign_feedback(
            request, receiver_employee, project_id
        )
        
        if not can_assign:
            try:
                Projects.objects.get(id=project_id, is_active=True)
                error_msg = "Project is not assigned to this employee under your supervision"
            except Projects.DoesNotExist:
                error_msg = reason
            
            raise ValidationError({
                "project": [error_msg]
            })
        
        return True
    # Add this method to FeedbackPermissions class in permissions.py
    @staticmethod
    def get_initial_employees(request):
        """
        Get employees to show initially (when no project is selected).
        - Admins: All employees in organization
        - Non-admins with roles: Only employees in shared projects
        """
        # Get permission status
        permission_status = FeedbackPermissions.get_permission_status(request)
        is_admin = permission_status.get('is_admin', False)
    
        if is_admin:
            return PermissionCore.get_assignable_employees_for_user(request)
        else:
            return PermissionCore.get_assignable_employees_for_user(request, project_id=None)


class UserScorePermissions:
    """Alias for score permissions"""
    
    @staticmethod
    def get_user_organization(request):
        return PermissionCore.get_organization_id(request)
    
    @staticmethod
    def get_permission_status(request):
        return FeedbackPermissions.get_permission_status(request)
    
    @staticmethod
    def can_award_score(request, receiver_employee, project_id=None):
        return PermissionCore.can_assign_to_employee(request, receiver_employee, project_id)
    
    @staticmethod
    def get_assignable_projects(request, employee_id=None):
        return PermissionCore.get_assignable_projects_for_user(request, employee_id)
    
    @staticmethod
    def get_assignable_employees(request, project_id=None):
        return PermissionCore.get_assignable_employees_for_user(request, project_id)
    
    @staticmethod
    def validate_score_assignment(request, receiver_employee_id, project_id):
        """Validate score assignment"""
        try:
            org_id = PermissionCore.get_organization_id(request)
            employee_filter = Q(id=receiver_employee_id, is_active=True)
            if org_id:
                employee_filter &= Q(organization_id=org_id)
            
            receiver_employee = Employees.objects.get(employee_filter)
        except Employees.DoesNotExist:
            raise ValidationError({
                "receiver": "Employee not found, inactive, or not in your organization"
            })
        
        can_award, reason, _ = UserScorePermissions.can_award_score(
            request, receiver_employee, project_id
        )
        
        if not can_award:
            try:
                Projects.objects.get(id=project_id, is_active=True)
                error_msg = "Project is not assigned to this employee under your supervision"
            except Projects.DoesNotExist:
                error_msg = reason
            
            raise ValidationError({
                "project": [error_msg]
            })
        
        return True
    
    # Add this method to UserScorePermissions class in permissions.py
    @staticmethod
    def get_initial_employees_for_scores(request):
        """
        Get employees to show initially for scores (when no project is selected).
        - Admins: All employees in organization
        - Non-admins with roles: Only employees in shared projects
        """
    # Get permission status
        permission_status = UserScorePermissions.get_permission_status(request)
        is_admin = permission_status.get('is_admin', False)
    
        if is_admin:
            # Admin sees all employees
            return PermissionCore.get_assignable_employees_for_user(request)
        else:
            # Non-admin users see only employees in projects where they have permission
            return PermissionCore.get_assignable_employees_for_user(request, project_id=None)