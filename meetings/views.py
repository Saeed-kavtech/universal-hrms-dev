import pytz
import requests
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from helpers.decode_token import decodeToken
from helpers.email_data import SendMeetingMails,SendMeetMails
from organizations.models import *
from .serializers import *
from helpers.status_messages import *
from .models import *
import json



# class MeetingCategoryViewset(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]  # Requires authentication and admin permission
#     queryset = MeetingCategory.objects.all()  # Retrieves all instances of EngagementSchedule model
#     serializer_class = MeetingCategorySerializer  # Serializer class for serializing data

#     def list(self, request, *args, **kwargs):
#         try:
#             organization_id = decodeToken(request, self.request)['organization_id']
#             queryset = self.queryset.filter(organization=organization_id, is_active=True)
#             serializer = self.get_serializer(queryset, many=True)
#             serialized_data = serializer.data
#             return successMessageWithData('success', serialized_data)
#         except Exception as e:
#             return errorMessage(str(e))

#     def create(self, request, *args, **kwargs):
#         try:
#             organization_id = decodeToken(request, self.request)['organization_id']
#             request.data['organization'] = organization_id
#             title = request.data.get('title', None)
#             if title is not None and self.queryset.filter(title=title).exists():
#                 return errorMessage('A record with the same title already exists.')
#             serializer = self.get_serializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return successMessageWithData('Created successfully', serializer.data)
#         except Exception as e:
#             return errorMessage(str(e))

#     def update(self, request, *args, **kwargs):
#         try:
#             partial = kwargs.pop('partial', False)
#             instance = self.get_object()
#             title = request.data.get('title', None)
#             if title is not None and self.queryset.exclude(pk=instance.pk).filter(title=title).exists():
#                 return errorMessage('A record with the same title already exists.')
#             serializer = self.get_serializer(instance, data=request.data, partial=partial)
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return successMessageWithData('Updated successfully', serializer.data)
#         except Exception as e:
#             return errorMessage(str(e))

#     def destroy(self, request, *args, **kwargs):
#         try:
#             pk = self.kwargs['pk']
#             if MeetingCategory.objects.filter(id=pk).exists():
#                 obj = MeetingCategory.objects.get(id=pk)
#                 if obj.is_active == False:
#                     msg = "Meeting Category is already deactivated"
#                     return errorMessage(msg)
#                 obj.is_active = False
#                 obj.save()
#                 return successMessage('successfully deactivated')
#             else:
#                 return errorMessage('Bad Request')
#         except Exception as e:
#             return exception(e)
        
#     def update(self, request, *args, **kwargs):
#         message = 'Update function is not offered in this path.'
#         return errorMessage(message)

class Meetingsviewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def create_meetings(self,request,*args, **kwargs):
        try:    
                token_data = decodeToken(self, self.request)
                organization_id = token_data['organization_id']
                user_id=request.user.id
                user_not_exists=[]
                user_serializer_errors=[]
                other_serializer_errors=[]
                api_url = "https://api.zoom.us/v2/users/me/meetings"
                required_fields = ['topic','start_time']
                if not all(field in request.data for field in required_fields):
                        return errorMessageWithData('make sure you have added all required fields','start_time,topic')

                existing_data =ThirdPartyTokens.objects.filter(organization=organization_id,is_active=True).last()
                if existing_data is None:
                    return errorMessage("Data not exists")
                
                bearer_token=f"bearer {existing_data.access_token}"
                
                headers = {
                    "Authorization": bearer_token,
                    "Content-Type": "application/json",
                }

                # JSON data for the POST request
                body = {
                    "topic": request.data['topic'],
                    "start_time":request.data['start_time'],
                    "timezone": 'Asia/Tashkent',
                    "settings":{
                    "host_video":True,
                    "participant_video":True,
                    "join_before_host":True,},
                }
                
                response = requests.post(api_url, headers=headers, json=body)  # Use 'json', not 'body'
                
                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    dt = datetime.fromisoformat(data['start_time'].rstrip('Z'))
                    date= dt.date() 
                    time= dt.time()
                    # print(data)
                    new_meeting_dict={
                        "meeting_uuid":data['uuid'],
                        "meeting_id":data['id'],
                        "host_id":data['host_id'],
                        "topic":data['topic'],
                        "meeting_type":int(data['type']),
                        "start_time":time,
                        "date":date,
                        "timezone":data['timezone'],
                        "organization":organization_id,
                        "join_url":data['join_url'],
                        "start_url":data['start_url'],
                        "password":data['password'],
                        "status":data['status'],
                        "duration":int(data['duration']),
                        "meeting_category" : request.data['meeting_category'],
                        "meeting_medium" : request.data["meeting_medium"]
                    }
                    serializer=MeetingSerializer(data=new_meeting_dict)
                    
                    if not serializer.is_valid():
                         return errorMessage(serializer.error_messages)
                    
                    meeting=serializer.save()
                    # print("Test",meeting.id)
                    
                    user_data={
                         "hrms_user":user_id,
                         "is_host":True
                    }
                    user_list_data= list(request.data.get('hrms_user_list',[]))
                    other_user_data=list(request.data.get('other_user_list',[]))
                    user_list_data.append(user_data)
                    for id in user_list_data:
                            query=HrmsUsers.objects.filter(id=id['hrms_user'],is_active=True)
                            if not query.exists():
                                user_not_exists.append(id['hrms_user'])
                                continue
                            
                            new_data={
                                "hrms_user":id['hrms_user'],
                                "meeting":meeting.id,
                                "is_host":id['is_host']
                            }

                            serializer=InternalMeetingParticipantSerializer(data=new_data)

                            if not serializer.is_valid():
                                user_serializer_errors.append(serializer.errors)
                                continue
                            serializer.save()


                                 
                                 

                    for other in other_user_data:

                        new_data={
                            "name":other['name'],
                            "email":other['email'],
                            "is_host":id['is_host'],
                            "meeting":meeting.id
                        }
                         
                        serializer=ExternalMeetingParticipantSerializer(data=new_data)

                        if not serializer.is_valid():
                                other_serializer_errors.append(serializer.errors)
                                continue

                        serializer.save()

                        SendMeetingMails(other['name'],other['email'],time,date,data['topic'],data['join_url'],data['id'],data['password'])

                    result={
                         "data":data,
                         "user_not_exists":user_not_exists,
                         "user_serializer_errors":user_serializer_errors,
                         "other_serializer_errors":other_serializer_errors
                    }

                    if len(user_not_exists)==0 and len(user_serializer_errors)==0 and len(other_serializer_errors)==0:
                        return successMessageWithData('All data added successfuly',data)
                    elif len(user_not_exists)>0 or len(user_serializer_errors)>0 or len(other_serializer_errors)>0:
                        return successMessageWithData('Some data added', result) 
                    # else:
                    #     return errorMessageWithData('Failed to add data', result) 
                else:
                    return errorMessageWithData("Failed to retrieve data",response.text)
        except  Exception as e:
            return exception(e)
        
        
    def create_meet(self,request,*args, **kwargs):
        try:    
                token_data = decodeToken(self, self.request)
                organization_id = token_data['organization_id']
                user_id=request.user.id
                user_not_exists=[]
                user_serializer_errors=[]
                other_serializer_errors=[]
                required_fields = ['topic','start_time']
                
                if not all(field in request.data for field in required_fields):
                        return errorMessageWithData('make sure you have added all required fields','start_time,topic')                
                else : 
                    dt = datetime.fromisoformat(request.data.get('start_time').rstrip('Z'))
                    date= dt.date() 
                    time= dt.time()
                    new_meeting_dict = {
                                "meeting_uuid": None,
                                "meeting_id": None,
                                "host_id": None,
                                "topic": request.data['topic'],
                                "meeting_type": None,
                                "start_time": time,
                                "date": date,
                                "timezone":request.data['timezone'],
                                "organization": organization_id,  # Use the updated value
                                "join_url": request.data['join_url'],
                                "start_url": request.data['start_url'],
                                "password": None,
                                "status": request.data['status'],
                                "duration": None,
                                "meeting_category" : request.data['meeting_category'],
                                "meeting_medium" : request.data["meeting_medium"]
                            }
                    serializer = MeetingSerializer(data=new_meeting_dict)
    
                    if not serializer.is_valid():
                         return errorMessage(serializer.error_messages)
                    
                    print('at serializer')
                    meeting=serializer.save()
                    # print("Test",meeting.id)
                    
                    user_data={
                         "hrms_user":user_id,
                         "is_host":True
                    }
                    user_list_data= list(request.data.get('hrms_user_list',[]))
                    other_user_data=list(request.data.get('other_user_list',[]))
                    user_list_data.append(user_data)
                    for id in user_list_data:
                            query=HrmsUsers.objects.filter(id=id['hrms_user'],is_active=True)
                            if not query.exists():
                                user_not_exists.append(id['hrms_user'])
                                continue
                            
                            new_data={
                                "hrms_user":id['hrms_user'],
                                "meeting":meeting.id,
                                "is_host":id['is_host']
                            }

                            serializer=InternalMeetingParticipantSerializer(data=new_data)

                            if not serializer.is_valid():
                                user_serializer_errors.append(serializer.errors)
                                continue
                            serializer.save()


                                 
                                 

                    for other in other_user_data:

                        new_data={
                            "name":other['name'],
                            "email":other['email'],
                            "is_host":id['is_host'],
                            "meeting":meeting.id
                        }
                         
                        serializer=ExternalMeetingParticipantSerializer(data=new_data)

                        if not serializer.is_valid():
                                other_serializer_errors.append(serializer.errors)
                                continue

                        serializer.save()
                       

                        SendMeetMails(other['name'],other['email'],time,date,request.data.get('topic'),request.data.get('join_url'),request.data.get('meeting_id'))
                    print(meeting)
                    result={
                         "data": new_meeting_dict,
                         "user_not_exists":user_not_exists,
                         "user_serializer_errors":user_serializer_errors,
                         "other_serializer_errors":other_serializer_errors
                    }

                    if len(user_not_exists)==0 and len(user_serializer_errors)==0 and len(other_serializer_errors)==0:
                        return successMessageWithData('All data added successfuly',result)
                    elif len(user_not_exists)>0 or len(user_serializer_errors)>0 or len(other_serializer_errors)>0:
                        return successMessageWithData('Some data added', result) 
                    # else:
                    #     return errorMessageWithData('Failed to add data', result) 
        except  Exception as e:
            return exception(e)
    

    
    def meetings_list(self,request,*args, **kwargs):
        try:    
                token_data = decodeToken(self, self.request)
                organization_id = token_data['organization_id']
                query=Meetings.objects.filter(organization=organization_id,is_active=True)

                serializer=MeetingSerializer(query,many=True)

                return success(serializer.data)

        except Exception as e:
          return exception(e)
        
    def meeting_detalis(self,request,*args, **kwargs):
        try:    
                token_data = decodeToken(self, self.request)
                organization_id = token_data['organization_id']
                pk=self.kwargs['pk']
                
                api_url = f"https://api.zoom.us/v2/meetings/{pk}"
                existing_data =ThirdPartyTokens.objects.filter(organization=organization_id,is_active=True).last()
                if existing_data is None:
                    return errorMessage("Data not exists")
                
                bearer_token=f"bearer {existing_data.access_token}"
                headers = {
                    "Authorization": bearer_token,
                    "Content-Type": "application/json",
                }

                response = requests.get(api_url, headers=headers)

                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    return success(data)
                else:
                    return errorMessageWithData("Failed to retrieve data",response.text)

        except Exception as e:
          return exception(e)
        
    def get_zak_token(self,request,*args, **kwargs):
        try:
                token_data = decodeToken(self, self.request)
                organization_id = token_data['organization_id']
                
                api_url ="https://api.zoom.us/v2/users/me/token?type=zak"
                existing_data =ThirdPartyTokens.objects.filter(organization=organization_id,is_active=True).last()
                if existing_data is None:
                    return errorMessage("Data not exists")
                
                bearer_token=f"bearer {existing_data.access_token}"
                headers = {
                    "Authorization": bearer_token,
                    "Content-Type": "application/json",
                }

                response = requests.get(api_url, headers=headers)

                if response.status_code == 200 or response.status_code == 201:
                    data = response.json()
                    return success(data)
                else:
                    return errorMessageWithData("Failed to retrieve data",response.text)

        except Exception as e:
          return exception(e)
              

    def get_upcoming_meetings(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            current_date=datetime.today().date()
            query=InternalMeetingParticipant.objects.filter(meeting__organization=organization_id,meeting__date__gte=current_date,hrms_user=request.user.id,is_active=True)
            serializer=ListMeetingSerializer(query,many=True)
            return success(serializer.data)
        except Exception as e:
          return exception(e)
        

    def get_meeting_participants(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk=self.kwargs['pk']
            # print("Test")
            user_query=InternalMeetingParticipant.objects.filter(meeting=pk,meeting__organization=organization_id,is_active=True)
            user_serializer=InternalMeetingParticipantSerializer(user_query,many=True).data
            other_user_query=ExternalMeetingParticipant.objects.filter(meeting=pk,meeting__organization=organization_id,is_active=True)
            other_user_serializer=ExternalMeetingParticipantSerializer(other_user_query,many=True).data
            
            data={
                 "hrms_users":user_serializer,
                 "other_users":other_user_serializer
            }

            return success(data)
              
        except Exception as e:
          return exception(e)
