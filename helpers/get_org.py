from organizations.models import Organization

def userOrganizationChecks(self, request):
    try:
        user_id = request.user.id
        is_admin = request.user.is_admin
        is_superuser = request.user.is_superuser
        # user_level = request.user.user_level
        if is_superuser==True:
            return {'status': 200, 'type': 'superuser'}
        
        organization = Organization.objects.filter(is_active=True)
        
        if is_admin == True:
            if not organization.filter(user__id=user_id).exists():
                message = 'Admin does not belong to any active organization'
                return {'status': 400, 'system_status': 400, 'message': message, 'data': '', 'system_status_message': ''}
            
                
            organization = organization.filter(user__id=user_id).first()
            return {'status': 202, 'type': 'admin', 'organization': organization, 'org_id': organization.id, 'org_name': organization.name, 'user_id': user_id}
        
        # todo
        elif request.user.is_employee == True:
            return {'status': 400, 'system_status': 400, 'message': "Employee Don't have any assign roles right now", 'data': '', 'system_status_message': ''}
            
        return {'status': 400, 'message': 'Not allowed right now', 'type': 'other users'}
    except Exception as e:
        return {'status': 400, 'system_status': 400, 'message': '', 'data': '', 'system_status_message': str(e)}
