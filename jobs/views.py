from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from helpers.renderers import Renderer
from rest_framework.response import Response
from .models import *
from rest_framework import viewsets
from .serializers import *
from helpers.status_messages import *
from organizations.models import Organization
from departments.models import Departments
from organizations.staff_classification_views import StaffClassification
from positions.serializers import PositionsSerializers
from departments.serializers import DepartmentsSerializers
from organizations.serializers import StaffClassificationSerializers
from jd.serializers import JdDescriptionsSerializers
import json
import uuid

from logs.views import UserLoginLogsViewset

from candidates.views import CandidateStatusActionsViewset


class JobTypesViewset(viewsets.ModelViewSet):
    queryset = JobTypes.objects.filter(is_active=True)
    serializer_class = JobTypesSerializers

    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['pk']
            if JobTypes.objects.filter(id=pk).exists():
                obj = JobTypes.objects.get(id=pk)
                if obj.is_active == False:
                    msg = "Job Type is already deactivated"
                    return Response({'status': 400, 'system_status': 400, 'data': '', 'message': msg, 'system_status_message': ''})
                obj.is_active = False
                obj.save()
                serializer = JobTypesSerializers(obj)
                return success(serializer.data)
            else:
                return Response({'status': 400, 'system_status': status.HTTP_400_BAD_REQUEST, 'data': '', 'message': 'This Job type does not exists', 'system_status_message': ''})
        except Exception as e:
            return exception(e)


class JobsViewset(viewsets.ModelViewSet):
    queryset = Jobs.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    serializer_class = JobsSerializers

    def list(self, request):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            obj = JobPosts.objects.filter(job__staff_classification__organization=user_organization)
            serializer = JobListPostSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def create(self, request):
        try:
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            #TODO check the department, staff classification and position co-relation with organization. 


            # generating unique job code
            unique_code = str(uuid.uuid4())[:6]
            if Jobs.objects.filter(job_code=unique_code, staff_classification__organization=user_organization.id).exists():
                return errorMessage('This job code already exists. Please contact the administrator or try again')
            request.data['job_code'] = unique_code
            
            serializer = CreateUpdateJobsSerializers(data=request.data)
            if serializer.is_valid():
                serializer.is_active = True
                job = serializer.save(created_by=self.request.user)
                job_post_data = []
                post_data = self.makePostJobArray(request.data, request.user.id)
                
                job_post_data.append(post_data)
                
                job_post_result = self.createUpdateJobPosts(request.user.id, job, job_post_data)
                
                message = f"Job successfully added and {job_post_result['message']}".format(
                    job_post_result) 
                job = Jobs.objects.get(pk=job.id)
                job_data = JobsSerializers(job, many=False)
                
                return success(serializer.data)
            else:
                return serializerError(serializer.errors)

        except Exception as e:
            return exception(e)


    def retrieve(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['uuid']
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            if Jobs.objects.filter(uuid=pk, staff_classification__organization=user_organization).exists():
                job = Jobs.objects.get(uuid=pk)
                serializer = JobsSerializers(job, many=False)
                return Response({'status': 200, 'system_status': status.HTTP_200_OK,'data': serializer.data, 'message': 'Successfully get the job detail', 'system_status_message': ''})
            else:
                return nonexistent(var = 'Job')
        except Exception as e:
            raise exception(e)


    def partial_update(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['uuid']
            message = ''
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            if Jobs.objects.filter(uuid=pk, staff_classification__organization=user_organization).exists():
                job = Jobs.objects.get(uuid=pk)
                
                serializer = CreateUpdateJobsSerializers(job, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    if 'job_is_active' in request.data:
                        job.is_active = request.data.get('job_is_active')
                        job.save()
                        print(request.data)
                    
                    job_post_data = []
                    if 'job_post_id' in request.data:
                        if request.data.get('job_post_id') is not None:
                            post_data = self.makePostJobArray(request.data, request.user.id)
                            job_post_data.append(post_data)
                            job_post_result = self.createUpdateJobPosts(request.user.id, job, job_post_data)

                            message = f"Job successfully updated and {job_post_result['message']}".format(job_post_result)

                    # job = Jobs.objects.get(pk=job.id)
                    
                    job_data = JobsSerializers(job, many=False)
                    

                    return Response({'status': 200, 'system_status': status.HTTP_200_OK, 'data': job_data.data, 'message': message, 'system_status_message': ''})
                
                else:
                    return serializerError(serializer.errors)
            else:
                return Response({'status': 400, 'system_status': status.HTTP_200_OK, 'data': '', 'message': 'does not exist', 'system_status_message': ''})

        except Exception as e:
            return Response({'status': 400, 'system_status': 400, 'data': '', 'message': str(e), 'system_status_message': str(e)})


    def activate_job(self, request, *args, **kwargs):
        try:
            job_post_uuid = self.kwargs['uuid']
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            if not JobPosts.objects.filter(uuid=job_post_uuid, job__staff_classification__organization=user_organization).exists():
                return errorMessage("Job post does not exists")

            job_post = JobPosts.objects.get(uuid=job_post_uuid)
            if job_post.is_active:
                return errorMessage("Job post is already in active state.")

            # Now get the job
            job = Jobs.objects.get(pk=job_post.job.id)
            job.is_active = True
            job.save()

            #TODO job log for this action

            #TODO does we change the job details like department, position and staff_classification

            # serializer = CreateUpdateJobsSerializers(job, data=request.data)
            # if serializer.is_valid():
            #     serializer.save()
            #     job = Jobs.objects.get(pk=job.id)
            # else:
            #     return serializerError(serializer.errors)

            #Now process the job post 
            message = "Job activate successfully."
            job_post_data = []
            post_data = self.makePostJobArray(request.data, request.user.id)
            post_data['job_post_id'] = job_post.id
            post_data['action'] = 'activate'
            post_data['is_active'] = True
            job_post_data.append(post_data)
            job_post.is_active=True
            job_post.save()
            job_post_result = self.createUpdateJobPosts(request.user.id, job, job_post_data)
            
            

            
            message = f"Job activate successfully and {job_post_result['message']}".format(job_post_result)

            # if 'job_post_id' in request.data:
            #     if request.data.get('job_post_id') is not None:
            #         post_data = self.makePostJobArray(request.data, request.user.id)
            #         job_post_data.append(post_data)
            #         job_post_result = self.createUpdateJobPosts(request.user.id, job, job_post_data)

            #         message = f"Job activate successfully and {job_post_result['message']}".format(job_post_result)

            serializer = JobsSerializers(job)
            return successMessageWithData(message, serializer.data)

        except Exception as e:
            return exception(e)


    def destroy(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['uuid']
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})

            if Jobs.objects.filter(uuid=pk, staff_classification__organization=user_organization).exists():
                obj = Jobs.objects.get(uuid=pk)
                if obj.is_active == False:
                    msg = "Job is already deactivated"
                    return Response({'status': 200, 'message': msg})
                obj.is_active = False
                obj.save()
                job_posts = JobPosts.objects.filter(job=obj, is_active=True)
                for job_post in job_posts:
                    job_post.is_active = False
                    job_post.save()

                serializer = JobsSerializers(obj)
                return successfullyDeleted(serializer.data)
            else:
                return Response({'status': 400, 'system_status': 400, 'data': '', 'message': 'This Job type does not exists', 'system_status_message': ''})
        except Exception as e:
            return exception(e)
                

    def deactivate_job_post(self, request, *args, **kwargs):
        try:
            job_post_uuid = self.kwargs['uuid']
            user_organization = UserLoginLogsViewset().userOrganization(request.user)
            if user_organization is None:
                return Response({'status':400, 'system_status':400, 'data': '', 'message': 'User has no organization in logs', 'system_error_message': ''})
            
            if not JobPosts.objects.filter(uuid=job_post_uuid, job__staff_classification__organization=user_organization).exists():
                return errorMessage("Job post does not exists")

            job_post = JobPosts.objects.get(uuid=job_post_uuid)
            if not job_post.is_active:
                return errorMessage("Job post is already have inactive state.")

            job_post.is_active = False
            job_post.save()

            # Now get the job
            job = Jobs.objects.get(pk=job_post.job.id)
            if not JobPosts.objects.filter(job=job_post.job.id).exists():
                job.is_active = False
                job.save()

                #Now in-active all the candidates who applied for this job
                candidate_list_update = CandidateStatusActionsViewset().candidate_status_on_job_update(job_post)
                print(candidate_list_update)
                
            serializer = JobsSerializers(job)
            return successfullyDeleted(serializer.data)
            
        except Exception as e:
            return exception(e)

    
    def makePostJobArray(self, job_data, user_id):
        post_job = {
            "job_post_id": None, "job": "", "action":"patch",
            "jd_selection": "", "project": "", "job_type": "", "job_post_code": "", "purpose": "",
            "jp_reports_to": "", "no_of_individuals": "", "post_date": None, "expiry_date": None,
            "jp_iterations": "1", "revised_by": None, "revised_date": None, "status": None
        }

        for key in post_job:
            if job_data.get(key):
                if job_data.get(key) != '':
                    post_job[key] = job_data.get(key, None)
        if post_job['revised_by'] == '' or post_job['revised_by'] is None:
            post_job['revised_by'] = user_id
        return post_job

    def createUpdateJobPosts(self, user_id, job, post_job_data):
        jp_errors = []
        job_posts = []
        response = {'message': '', 'job_post_errors': ''}
        job_post_id = None
        if isinstance(post_job_data, str):
            post_job_data = json.loads(post_job_data)
            job_posts.append(post_job_data)
        else:
            job_posts = post_job_data

        try:

            if job_posts is not None:
                for jobPost in job_posts:
                    jobPost['job'] = job.id

                    if 'job_post_code' in jobPost:
                        if jobPost['job_post_code'] is None or jobPost['job_post_code'] == '':
                            jobPost['job_post_code'] = job.job_code
                    else:
                        jobPost['job_post_code'] = job.job_code

                    if 'job_post_id' in jobPost:
                        if jobPost['job_post_id'] is not None:
                            job_post_id = jobPost['job_post_id']

                    if 'revised_by' in jobPost:
                        if jobPost['revised_by'] is None:
                            jobPost['revised_by'] = user_id
                    else:
                        jobPost['revised_by'] = user_id

                    # if JobPosts.objects.filter(job_post_code=jobPost['job_post_code'], job=job.id).exists():
                    # 	jp_obj = JobPosts.objects.filter(job_post_code=jobPost['job_post_code'], job=job.id).last()
                    # 	jobPost['jp_iterations'] = jp_obj.jp_iterations
                    # else:
                    # 	jp_obj = None
                    # 	jobPost['jp_iterations'] = 0

                    if JobPosts.objects.filter(job=job.id).exists():
                        jp_obj = JobPosts.objects.filter(job=job.id).last()
                        jobPost['jp_iterations'] = jp_obj.jp_iterations
                        # update the job_post_id
                        if jobPost['action']!='active':
                            job_post_id = jp_obj.id
                    else:
                        jp_obj = None
                        jobPost['jp_iterations'] = 0

                    # TODO check if job post code already exist in other jobs posts.
                    # to check this we ignore the codes of that jobs.

                    if job_post_id is None:
                        jobPost['jp_iterations'] = jobPost['jp_iterations']+1
                        job_post_serializer = JobPostsSerializers(data=jobPost)
                    elif JobPosts.objects.filter(id=job_post_id, job=job.id).exists():
                        jp_data = JobPosts.objects.get(id=job_post_id)

                        if jp_data.is_active:
                            job_post_serializer = JobPostsSerializers(jp_data, data=jobPost, partial=True)
                        else:
                            jobPost['jp_iterations'] = jobPost['jp_iterations']+1
                            job_post_serializer = JobPostsSerializers(jp_data, data=jobPost, partial=True)
                            # job_post_serializer = JobPostsSerializers(data=jobPost)
                    else:
                        jp_errors.append("Job Post does not exist to update, please try again.")
                        response['message'] = "Job Post does not exist to update, please try again."
                        response['job_post_errors'] = jp_errors
                        return response

                    if job_post_serializer.is_valid():
                        job_post_serializer.save()
                    else:
                        jp_errors.append(job_post_serializer.errors)

                if (len(job_posts) == len(jp_errors)):
                    response['message'] = "No job posts data processed, please update it again!"
                elif len(jp_errors) > 0:
                    response['message'] = "Some of the job posts are not processed, please update it again!"
                else:
                    response['message'] = "All Job posts data processed Successfully."

            else:
                response["message"] = "No job_posts found."
                jp_errors.append("No job_posts found.")

        except Exception as e:
            response['message'] = "Job posts process through error, please update it again!"
            jp_errors.append("job_posts process has error({})".format(str(e)))

        response['job_post_errors'] = jp_errors
        return response
    


class GetDataViewset(viewsets.ModelViewSet):
    # This API retrieve the JD against the job post uuid
    def get_jd_data(self, request, *args, **kwargs):
        try:
            pk = self.kwargs['uuid']
            
            job_post = JobPosts.objects.filter(uuid=pk)
            if not job_post.exists():
                return errorMessage("Job post does not exists")
            elif not job_post.filter(is_active=True).exists():
                return errorMessage("job post is deactivated against this uuid")
            job_post = job_post.get()
            
            jd_description = JdDescriptions.objects.filter(id=job_post.jd_selection.id)
            serializer = JdDescriptionsSerializers(jd_description, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)



class PreJobDataView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):		
        try:
            org_id = self.kwargs['org_id']
            if org_id is not None:
                if Organization.objects.filter(id=org_id).exists():
                    org = Organization.objects.get(id=org_id)
                    if org.is_active == False:
                        return Response({'status':400, 'system_status': 400, 'data': '', 'message': "Activate the Organization first", 'system_error_message':''})

                    position_obj = Positions.objects.filter(is_active=True, staff_classification__organization__id=org_id)
                    if not position_obj.exists():
                        return Response({'status':400, 'system_status': 400, 'data': '', 'message': "No active Position exists", 'system_error_message':''})
                    position_serializer = PositionsSerializers(position_obj, many=True)
                    department_obj = Departments.objects.filter(grouphead__organization__id=org_id, is_active=True)
                    if not department_obj.exists():
                        return Response({'status':400, 'system_status': 400, 'data': '', 'message': "No active Department exists", 'system_error_message':''})
                    department_serializer = DepartmentsSerializers(department_obj, many=True)

                    staff_obj = StaffClassification.objects.filter(organization__id=org_id, is_active=True)
                    if not staff_obj.exists():
                        return Response({'status':400, 'system_status': 400, 'data': '', 'message': "No active Staff Classification exists", 'system_error_message':''})
                    staff_serializer = StaffClassificationSerializers(staff_obj, many=True)

                    job_types_obj = JobTypes.objects.filter(is_active=True)
                    job_types_serializer = JobTypesSerializers(job_types_obj, many=True)

                    jd_obj = JdDescriptions.objects.filter(is_active=True, staff_classification__organization__id=org_id)
                    jd_serializer = JdDescriptionsSerializers(jd_obj, many=True)

                    data = {'staff_classification': staff_serializer.data, 'department': department_serializer.data, 'position': position_serializer.data, 'job_types': job_types_serializer.data, 'jd': jd_serializer.data}
                    return Response({'status': 200, 'system_status': 200, 'data': data, 'message': "Success", 'system_error_message': ''})
            else:
                return Response({'status': 400, 'system_status': 404, 'data': '', 'message': "Organization does not exist at this index", 'system_error_message': ''})

        except Exception as e:
            return exception(e)
                

class JobsForKavtechWebsiteViewSet(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        try:
            query = JobPosts.objects.filter(
                job__staff_classification__organization=4,
                job__is_active=True,
                is_active=True,

            )
            serializer = JobsForKavtechWebsiteSerializers(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

