from .serializers import KpisLogsSerializers
def kpis_logs(self, employee_kpis, requested_data, request_type, user_id):
    try:
        result = {'status': 400, 'message': '', 'data': None}
        kpis_data = {
            'request_type':request_type,
            'employees_kpi': employee_kpis.id,
            'created_by': user_id,
        }
        serializer = KpisLogsSerializers(data=kpis_data)
        if not serializer.is_valid():
            # print(serializer.errors)
            result['message'] = serializer.errors
            return result

        # print(serializer.data)
        
        kpis_obj = serializer.save()

        serializer = KpisLogsSerializers(kpis_obj, data=requested_data, partial=True)
        if not serializer.is_valid():
            result['message'] = serializer.errors
            return result
        
        serializer.save()
        result['data'] = serializer.data
        result['status'] = 200
        return result
    except Exception as e:
        print(e)
        result['data'] = e
        return result
    