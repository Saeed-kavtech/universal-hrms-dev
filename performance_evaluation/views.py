
from rest_framework import viewsets
from helpers.status_messages import (
    exception,success,errorMessage, serializerError, successMessage
)
from helpers.decode_token import decodeToken
from helpers.custom_permissions import IsAuthenticated, IsEmployeeOnly,IsAdminOnly
from kpis.models import EmployeesKpis
# from kpis.views import KpisEvaluationViewset
from kpis.kpislogs import kpis_logs
from performance_configuration.models import ScaleGroups
from performance_configuration.serializer import ListScaleGroupSerializers
from.serializers import *
from .models import *
import json
from django.db.models import Q

# Create your views here.
class KIPScaleGroupsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminOnly|IsEmployeeOnly]
    queryset = KPIScaleGroups.objects.all() 
    serializer_class = KPIScaleGroupsSerializers
    

    def retrieve(self, request, *args, **kwargs):
        try:
            # print("Test")
            pk = self.kwargs['pk']
            # print(pk)
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            query = EmployeesKpis.objects.filter(employee=pk,employee__organization=organization_id,is_active=True)
            if not query.exists():
                return errorMessage("No kpis exists against this employee")
            # print(query.values())
            # serializer = ListEmployeesKpisSerializers(query, many=True)
            # return success(serializer.data)
            # return "Test"
        except Exception as e:
            return exception(e)

    # def list(self, request, *args, **kwargs):
    #     try:
    #         token_data = decodeToken(self, self.request)
    #         organization_id = token_data['organization_id']
    #         query = EmployeesKpis.objects.filter(employee__organization=organization_id,is_active=True)
    #         # print(query.values())
    #         # serializer=ListEmployeesKpisSerializers(query, many=True)
    #         # print("Test1")
    #         # return success(serializer.data)
    #     except Exception as e:
    #         return exception(e)


    def create(self, request, *args, **kwargs):
        try:
            # pk = self.kwargs['pk']
            # print("Test")
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user_id = request.user.id
            # print(request.data['kpi_id'])
            required_fields = ['kpi_id', 'scale_group']
            if not all(field in request.data for field in required_fields):
                return errorMessage(
                    'make sure you have added all the required fields: '
                    '[kpi_id, scale_group]'
                )
            
            emp_kapi=EmployeesKpis.objects.filter(id=request.data['kpi_id'],employee__organization=organization_id,is_active=True)
            

            if  not emp_kapi.exists():
                return errorMessage("Kpi not exists at this id")
            
            kpi_sg_group_query = KPIScaleGroups.objects.filter(kpi_id=request.data['kpi_id'],is_active=True)
            # print(kpi_sg_group_query.values())

            if kpi_sg_group_query.exists():
                return errorMessage("Scale Group already assigned against this kpi id")
            
            
            
            scalegroups_query = ScaleGroups.objects.filter(id=request.data['scale_group'], organization=organization_id)
            if not scalegroups_query.exists():
                    return errorMessage("Scale Group does not exists")
            elif scalegroups_query.filter(is_active=False).exists():
                    return errorMessage("Scale Group is deactivated at this id")
            
           
            
            request.data['assign_by'] = user_id

            serializer=self.serializer_class(data = request.data)

            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            instance=serializer.save()
            kpi_sg_id = instance.id

            # print(kpi_sg_id)
            
            aspects_query = GroupAspects.objects.filter(scale_group=request.data['scale_group'],is_active=True)
            # print(aspects_query.values())

            if aspects_query.exists():

                for aspect in aspects_query:
                    try:
                        
                        aspect_data={
                        'kpi_sg':kpi_sg_id,
                        'ep_aspects':aspect.id,
                        'comment':request.data['comment'],
                        'result':request.data['result'],
                        'score':request.data['score'],
                        } 

                        serializer=KPIAspectsSerializers(data = aspect_data)

                        if not serializer.is_valid():
                            continue
                            # return serializerError(serializer.errors)
                        aspect_instance=serializer.save()
                        kpi_aspect_id = aspect_instance.id

                        aspects_parameters_query=AspectsParameters.objects.filter(id=aspect.id,is_active=True)

                        if not aspects_parameters_query.exists():
                            continue
                        
                        for parameters in aspects_parameters_query:
                        
                            
                            parameters_data={
                            'kpi_aspects':kpi_aspect_id,
                            'parameters':parameters.id,
                            'comment':request.data['comment'],
                            'result':request.data['result'],
                            'score':request.data['score'],
                            } 

                            serializer=KPIAspectsParametersSerializers(data =parameters_data)

                            if not serializer.is_valid():
                                # return serializerError(serializer.errors)
                                print(serializer.errors)
                                continue
                            serializer.save()

                    except Exception as e:
                        return exception(e)
                    
            return successMessage("Success")
            
        except Exception as e:
            return exception(e)

    def lead_update_scale_group(self,kpi_id,scale_group,employee_id,organization_id):
        try:
            # print("Test")
            result = {
                'status': 400, 
                'message': '', 
                'system_error_message': '',   
            }

            kpi_id= kpi_id
            scale_group=scale_group
            employee_id = employee_id
            
            
            kpi_id_scale_group=KPIScaleGroups.objects.filter(kpi_id=kpi_id,scale_group__organization=organization_id,is_active=True) 
            
            if not kpi_id_scale_group.exists():
                # return errorMessage("No scale group assigned against this kpi")
                output=self.lead_scale_group_assign(kpi_id,scale_group,employee_id)
                if output['status'] == 400:
                        # print("IF")
                        result['message'] = output['message']
                        return result
            
            
            else:  
                kpi_scale_group=KPIScaleGroups.objects.filter(kpi_id=kpi_id,scale_group=scale_group,scale_group__organization=organization_id,is_active=True) 
                
                if not kpi_scale_group.exists():
                    # return errorMessage("Same scale group is already assign at this kpi id")
            
                    obj=kpi_id_scale_group.get()

                    obj.is_active = False
                    obj.save()

                    aspects_query = KPIAspects.objects.filter(kpi_sg=obj.id,is_active=True)
                    
                    if aspects_query.exists():
                        for aspect in aspects_query:
                            try:
                                aspect.is_active = False
                                aspect.save()

                                aspects_parameters_query=KPIAspectsParameterRating.objects.filter(kpi_aspects=aspect.id,is_active=True)

                                if not aspects_parameters_query.exists():
                                    continue

                                for parameters in aspects_parameters_query:
                                    parameters.is_active = False
                                    parameters.save()

                            except Exception as e:

                                return exception(e)
                    
                    output=self.lead_scale_group_assign(kpi_id,scale_group,employee_id)
                    if output['status'] == 400:
                            # print("IF")
                            result['message'] = output['message']
                            return result
            
              

            result['message'] = 'Success'      
            result['status'] = 200
            return result
        
        
        except Exception as e:
            return exception(e)

    def lead_scale_group_assign(self,kpi_id,scale_group,emp_id):
        try:
           
            result = {
                'status': 400, 
                'message': '', 
                'system_error_message': '',   
            }
            
            data={
                'kpi_id':kpi_id,
                'scale_group':scale_group,
                'assign_by':emp_id,
            }

            serializer=self.serializer_class(data =  data)

            if not serializer.is_valid():
                return serializerError(serializer.errors)
            
            instance=serializer.save()
            kpi_sg_id = instance.id

            # print(kpi_sg_id)
            
            aspects_query = GroupAspects.objects.filter(scale_group=scale_group,is_active=True)
            # print(aspects_query.values())

            if aspects_query.exists():

                for aspect in aspects_query:
                    try:
                        
                        aspect_data={
                        'kpi_sg':kpi_sg_id,
                        'ep_aspects':aspect.id,
                      
                        } 

                        serializer=KPIAspectsSerializers(data = aspect_data)

                        if not serializer.is_valid():
                            continue
                            # return serializerError(serializer.errors)
                        aspect_instance=serializer.save()
                        kpi_aspect_id = aspect_instance.id

                        aspects_parameters_query=AspectsParameters.objects.filter(aspects=aspect.id,is_active=True)

                        if not aspects_parameters_query.exists():
                            continue
                        
                        for parameters in aspects_parameters_query:
                        
                            
                            parameters_data={
                            'kpi_aspects':kpi_aspect_id,
                            'parameters':parameters.id,
                          
                            } 

                            serializer=KPIAspectsParametersSerializers(data =parameters_data)

                            if not serializer.is_valid():
                                # return serializerError(serializer.errors)
                                # print(serializer.errors)
                                continue
                            serializer.save()

                    except Exception as e:
                        return exception(e)
            result['message'] = 'Success'      
            result['status'] = 200
            return result
            
        except Exception as e:
            return exception(e)
    

class EmployeeKIPScaleGroupsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsEmployeeOnly]
    queryset = KPIScaleGroups.objects.all() 
    serializer_class = KPIScaleGroupsSerializers

    # def evaluator_employee_kpis(self, request, *args, **kwargs):
    #     try:
    #         token_data = decodeToken(self, self.request)
    #         organization_id = token_data['organization_id']
    #         # pk = self.kwargs['pk']
    #         # print(pk)
    #         # query=Employees.objects.filter(evaluator=request.user.id,employee__organization=organization_id,is_active=True)
    #         # query = EmployeesKpis.objects.filter(evaluator=request.user.id,employee__organization=organization_id,is_active=True)
    #         # serializer=ListEmployeesKpisSerializers(query, many=True)
    #         # return success(serializer.data)
    #     except Exception as e:
    #         return exception(e)
        
    def scale_group_data(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            query = ScaleGroups.objects.filter(organization=organization_id,is_active=True)
            serializer=ListScaleGroupSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def evaluation(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            employee_id = token_data['employee_id']
           
            request_type = request.method
            user_id = request.user.id
           
           
            
           
            if pk != str(request.data['kpi_id']):
                 return errorMessage(
                    'Kpi id is not matched'
                )
            

            query_submit = EmployeesKpis.objects.filter(
                kpis_status__level=6,
                id=pk,
                employee__organization=organization_id,
                is_active=True
            )

            if query_submit.exists():
                return errorMessage("KPI evaluation has already been submitted")

            query = EmployeesKpis.objects.filter(
                Q(kpis_status__level=4) | Q(kpis_status__level=5) | Q(kpis_status__level=7)| Q(kpis_status__level=8),
                id=pk,
                employee__organization=organization_id,
                is_active=True
            )

         

           
            if not query.exists():
                return errorMessage("For evaluation Kpi must be approved by HR")
            
            kpi_obj=query.get()
            
            # if kpi_obj.evaluator is None:
            #     return errorMessage('You are not the evaluator')
            
            if kpi_obj.evaluator.id != employee_id:
                return errorMessage('You are not the evaluator')
            
            ep_score=5
            ep_score_queryset = query.values_list("ep_complexity__score", flat=True)
            if ep_score_queryset.exists():
                ep_score = ep_score_queryset.first()
            # print(ep_score)
            scalerating={}
            scale_rating_query=ScaleRating.objects.filter(organization=organization_id,is_active=True)
            if len(scale_rating_query)<=0:
                return errorMessage("Scale Rating is not set againts this organization")


            max_sr = 1
          
            for sr in scale_rating_query:
                
                scalerating[sr.id]=sr
                
                if max_sr < sr.level:
                    max_sr = sr.level

           
            count=0
            countrp=0
            param_count=0
            parameters_required=0
            request_data=request.data
            # req_kpi_sg=[]
            if isinstance(request_data, str):
                request_data = json.loads(request_data)
                req_kpi_sg.append(request_data)
            else:
                req_kpi_sg = request_data
            
            action=req_kpi_sg.get('action',None)
            if action:
              action = action.lower()

            evaluation_status=req_kpi_sg.get('evaluation_status',None)


            if action =="submit":
                if evaluation_status is None:
                    return errorMessage('Please make sure to include  evaluation status when submitting evaluation.')
           
            query_kpi_scale_group=KPIScaleGroups.objects.filter(kpi_id=pk,scale_group=req_kpi_sg['scale_group'],is_active=True)
          
            if query_kpi_scale_group.exists():
                obj=query_kpi_scale_group.get()
                req_kpi_sg_aspects = req_kpi_sg["kpi_aspects"]
                scalegroupresult=0.0
                for aspect in req_kpi_sg_aspects:
                    try:
                        
                        aspects_query=KPIAspects.objects.filter(id=aspect['id'],kpi_sg=obj.id,is_active=True)
                        
                        if not aspects_query.exists():
                            continue
                        parameters_data = aspect["parameters"]
                        obj1=aspects_query.get()
                        aspect_result=0.0
                        
                        parameters_required=KPIAspectsParameterRating.objects.filter(kpi_aspects=aspect['id'],parameters__is_required=True,is_active=True).count()
                        for parameters in parameters_data:
                            
                            parameters_query=KPIAspectsParameterRating.objects.filter(id=parameters['id'],kpi_aspects=aspect['id'],is_active=True)
                           
                            if not parameters_query.exists():
                               continue
                            
                            obj2=parameters_query.get()
                            paramter_result=0.0
                            has_checked=parameters.get('has_checked',False)
                            # print(parameters['scale_rating'])
                            if 'scale_rating' in parameters and has_checked==True:
                                 
                            #    print(parameters['scale_rating']) 
                               scale_rating_id = parameters['scale_rating']

                               if obj2.parameters.is_required==True:
                                  countrp+=1

                               if not scale_rating_id in scalerating :
                                   count+=1
                                   continue
                               
                               param_count+=1

                               obj2_scale_rating=scalerating[parameters['scale_rating']]
                               
                            # print(obj2_scale_rating)
                               obj2.scale_rating = obj2_scale_rating
                               sr_level=obj2_scale_rating.level 
                            #    print("SR_level",sr_level)
                               result=(ep_score*sr_level)/(ep_score*max_sr)*100
                            #    print(result)
                               paramter_result =round(result, 2)
                               obj2.result=paramter_result
                               obj2.is_required=True
                               obj2.save()
                            else:
                               obj2.scale_rating=None
                               obj2.is_required=False
                               paramter_result= 0.0
                               obj2.result=paramter_result
                               obj2.save()
                               
                            aspect_result += paramter_result
                            
                        # print("Test")
                        # print(aspect_result)
                        aspectresult = round(aspect_result/param_count,2)
                        # print(aspectresult)
                        obj1.result=aspectresult
                        obj1.save()  

                        scalegroupresult +=aspectresult

                    except Exception as e:
                        return exception(e)
                
                sgresult=round(scalegroupresult/len(req_kpi_sg_aspects),2)
                # print("Test1")
                # print(sgresult)
                obj.result=sgresult
                obj.save()
            message=''
            status_id=0


            


            if action =="submit":
                if count > 0:
                  return errorMessage('To submit your evaluation, please rate each required parameter')
                
                if countrp<parameters_required:
                    return errorMessage('To submit your evaluation, please checked and rate each parameter')

                # print("Test")
                if kpi_obj.kpis_status.level==7 or kpi_obj.kpis_status.level==8:
                    
                    recheck_status = KpisStatus.objects.get(level=9, organization=organization_id, is_active=True)
                    kpi_obj.kpis_status=recheck_status
                    kpi_obj.evaluation_status=evaluation_status
                    kpi_obj.save() 
                    status_id=kpi_obj.kpis_status.id
                    message='Recheck Evaluation is  completed'

                else:
                    status = KpisStatus.objects.get(level=6, organization=organization_id, is_active=True)
                    kpi_obj.kpis_status=status
                    kpi_obj.evaluation_status=evaluation_status
                    kpi_obj.save()
                    status_id=kpi_obj.kpis_status.id
                    message='Evaluation is  completed'
            

            else:

                if kpi_obj.kpis_status.level==7 or kpi_obj.kpis_status.level==8:
                    recheck_status = KpisStatus.objects.get(level=8, organization=organization_id, is_active=True)
                    kpi_obj.kpis_status=recheck_status
                    kpi_obj.evaluation_status=evaluation_status
                    kpi_obj.save() 

                    status_id=kpi_obj.kpis_status.id
                    message='Recheck Evaluation is save but not completed'
                
                else: 
                    kpis_status = KpisStatus.objects.get(level=5, organization=organization_id, is_active=True)
                    kpi_obj.kpis_status=kpis_status
                    kpi_obj.evaluation_status=evaluation_status
                    kpi_obj.save() 
                    status_id=kpi_obj.kpis_status.id
                    message='Evaluation is save but not completed'
            
            requested_data = {
                        'kpis_status': status_id
                    }

            kpis_logs(self,kpi_obj, requested_data, request_type, user_id)

            return successMessage(message)
            
        except Exception as e:
            return exception(e)

    def submit(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']

            # emp_query = Employees.objects.filter(id=pk,organization=organization_id,is_active=True)
            # if not emp_query.exists():
            #    return errorMessage("Employee not exists in this organization")
            
            kpi_query = EmployeesKpis.objects.filter(id=pk,employee__organization=organization_id,is_active=True)

            if not kpi_query.exists():
               return errorMessage("Kpi not exists in this organization")
            
            if not kpi_query.filter(kpis_status__level=5).exists():
                return errorMessage("Kpi is not evaluated by team lead")
            
            status = KpisStatus.objects.get(level=6, organization=organization_id, is_active=True)

            obj=kpi_query.get()
            obj.kpis_status=status
            obj.save() 

            # kpis_array = list(request.data.get('kpis_array'))
            

            # if not kpis_array:
            #     return errorMessage("kpis array is not passed")
            
            # kpis_status_not_set = []
            # kpis_status = KpisStatus.objects.get(level=6, organization=organization_id, is_active=True)
            # count=0
            # for kpis in kpis_array:
            #     query = EmployeesKpis.objects.filter(id=kpis,kpis_status__level=5,evaluator=request.user.id, employee__organization=organization_id)
            #     if not query.exists():
            #         kpis_status_not_set .append(kpis)
            #         continue
            #     obj = query.get()
            #     obj.kpis_status = kpis_status
            #     obj.save()

            #     count +=1

            # if count == len(kpis_array):
            #     return successMessage('All kpis status is changed successfuly')
            # elif count == 0:
            #     return errorMessageWithData('No status is changed Successfully', kpis_status_not_set) 
            # elif count > 0:
            #     return successMessageWithData('Some of the data is processed successfully',kpis_status_not_set)

            
            
            # kpi_query_hr = EmployeesKpis.objects.filter(employee=pk,kpis_status__status_key="Approved-By-HR",employee__organization=organization_id,is_active=True)
            # kpi_query_evaluated = EmployeesKpis.objects.filter(employee=pk,kpis_status__status_key="Evaluate-By-team-lead",employee__organization=organization_id,is_active=True)
            # # print(kpi_query)
            # kpi_query_length = len(kpi_query_hr)

            # # print(kpi_query_length)

            # # stauts_query=kpi_query.filter(kpis_status__status_key="Evaluate-By-team-lead")
            # kpi_stauts_query_length = len(kpi_query_evaluated )

            # if kpi_query_length!=kpi_stauts_query_length:
            #     return errorMessage("Kpis is not evaluated,please make sure all kpis is evaluated before submit")
            
            # kpis_status = KpisStatus.objects.get(status_key="Sumbitted-by-team-lead", organization=organization_id, is_active=True)


            # for kpi in kpi_query :
            #     # print(kpi)
            #     kpi.kpis_status=kpis_status
            #     kpi.save()

            return successMessage('Status changed successfully') 
            
        except Exception as e:
            return exception(e)
    def update_scale_group(self,kpi_id,scale_group,employee_id,organization_id):
        try:
            # print("Test1")
            result = {
                'status': 400, 
                'message': '', 
                'system_error_message': '',   
            }

            kpi_id= kpi_id
            scale_group=scale_group
            employee_id = employee_id
            
            
            kpi_id_scale_group=KPIScaleGroups.objects.filter(kpi_id=kpi_id,scale_group__organization=organization_id,is_active=True) 
            
            
            if not kpi_id_scale_group.exists():
                # return errorMessage("No scale group assigned against this kpi")
                output=self.assign_scale_group(kpi_id,scale_group,employee_id)
                if output['status'] == 400:
                        # print("IF")
                        result['message'] = output['message']
                        return result
                
            else:  
                kpi_scale_group=KPIScaleGroups.objects.filter(kpi_id=kpi_id,scale_group=scale_group,scale_group__organization=organization_id,is_active=True) 
                
                if not kpi_scale_group.exists():
                    # return errorMessage("Same scale group is already assign at this kpi id")
            
                    obj=kpi_id_scale_group.get()

                    obj.is_active = False
                    obj.save()

                    aspects_query = KPIAspects.objects.filter(kpi_sg=obj.id,is_active=True)
                    
                    if aspects_query.exists():
                        for aspect in aspects_query:
                            try:
                                aspect.is_active = False
                                aspect.save()

                                aspects_parameters_query=KPIAspectsParameterRating.objects.filter(kpi_aspects=aspect.id,is_active=True)

                                if not aspects_parameters_query.exists():
                                    continue

                                for parameters in aspects_parameters_query:
                                    parameters.is_active = False
                                    parameters.save()

                            except Exception as e:
                                result['message'] = e
                                return result
                    
                    output=self.assign_scale_group(kpi_id,scale_group,employee_id)
                    if output['status'] == 400:
                            # print("IF")
                            result['message'] = output['message']
                            return result
                
            # scale_group_instance = ScaleGroups.objects.get(id=request.data['scale_group'])
            # kpi_query = EmployeesKpis.objects.get(id=pk,employee__organization=organization_id,is_active=True)
            # kpi_query.scale_group=scale_group_instance
            # kpi_query.save()

            result['message'] = 'Success'      
            result['status'] = 200
            return result
        
        except Exception as e:
            result['message'] = e
            return result

    def assign_scale_group(self,kpi_id,scale_group,employee_id):
        try:
           
            result = {
                'status': 400, 
                'message': '', 
                'system_error_message': '',   
            }

            
            data={
                'kpi_id':kpi_id,
                'scale_group':scale_group,
                'assign_by':employee_id,
            }

            serializer=self.serializer_class(data =  data)

            if not serializer.is_valid():
                result['message'] = serializer.errors
                return result
                
            
            instance=serializer.save()
            kpi_sg_id = instance.id

            # print(kpi_sg_id)
            
            aspects_query = GroupAspects.objects.filter(scale_group=scale_group,is_active=True)
            # print(aspects_query.values())

            if aspects_query.exists():

                for aspect in aspects_query:
                    try:
                        
                        aspect_data={
                        'kpi_sg':kpi_sg_id,
                        'ep_aspects':aspect.id,
                      
                        } 

                        serializer=KPIAspectsSerializers(data = aspect_data)

                        if not serializer.is_valid():
                            continue
                            # return serializerError(serializer.errors)
                        aspect_instance=serializer.save()
                        kpi_aspect_id = aspect_instance.id

                        aspects_parameters_query=AspectsParameters.objects.filter(aspects=aspect.id,is_active=True)

                        if not aspects_parameters_query.exists():
                            continue
                        
                        for parameters in aspects_parameters_query:
                        
                            
                            parameters_data={
                            'kpi_aspects':kpi_aspect_id,
                            'parameters':parameters.id,
                          
                            } 

                            serializer=KPIAspectsParametersSerializers(data =parameters_data)

                            if not serializer.is_valid():
                                # return serializerError(serializer.errors)
                                # print(serializer.errors)
                                continue
                            serializer.save()

                    except Exception as e:
                        result['message'] = e
                        return result
            result['message'] = 'Success'      
            result['status'] = 200
            return result
            
        except Exception as e:
            result['message'] = e
            return result
    
    