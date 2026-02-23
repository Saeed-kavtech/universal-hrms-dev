from .serializers import ScriptStatusLogsSerializers
from .models import ScriptStatusLogs
def script_logs(emp_id,staff_classification,script_title,script_type,year,status,user_id):
        try:
            result = {
                'status': 400, 
                'data':[],
                'message': '', 
                'system_error_message': '',   
            }
            
            record_exists=False
            query=ScriptStatusLogs.objects.filter(employee=emp_id,year=year,script_type=script_type,is_completed=True,action_by=user_id,is_active=True)
            
            if query.exists():
                if script_type==2:
                    record_exists=True
                    
                else:
                    query1=query.filter(staff_classification=staff_classification)
                    if query1.exists():
                        record_exists=True

                    else:
                        query.update(is_completed=False)



                 
                           
            if record_exists:
                result['status'] = 400
                result['message'] = "Script already run for this employee"
                return result
                 
            data={
                "employee":emp_id,
                'staff_classification':staff_classification,
                "script_type":script_type,
                "script_title":script_title,
                'year':year,
                "is_completed":status,
                "action_by":user_id,
            }
            

            serializer = ScriptStatusLogsSerializers(data=data)
            if not serializer.is_valid():
                print(serializer.errors)
                result['message'] = serializer.errors
                return result
            
            serializer.save()
            
            result['status'] = 200
            result['data'] = serializer.data

            return result

        except Exception as e:
            print(e)
            result['data'] = e
            return result

