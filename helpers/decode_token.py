from rest_framework_simplejwt.tokens import AccessToken

def decodeToken(self, request, *args, **kwargs):
    try:
        token = request.META.get('HTTP_AUTHORIZATION')
        # print(token)
        if token is not None:
            if ' ' in token:
                # print(token)
                token = token.split(' ')[1]
        
        decoded_token = AccessToken(token)
        
        payload = decoded_token.payload.get('payload', {})
        role_id = payload.get('role_id', None)
        organization_id = payload.get('organization_id')
        employee_id = payload.get('employee_id')
        # permission_id=payload.get('permission_id')
        return {'organization_id': organization_id, 'role_id': role_id, 'employee_id': employee_id}
    except Exception as e:
        print(str(e))
        return None