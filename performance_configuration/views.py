from django.shortcuts import render
from rest_framework import viewsets
from helpers.status_messages import (
    errorMessageWithData, exception, errorMessage,nonexistent,success,serializerError, successMessage, successMessageWithData,successfullyCreated
)
from helpers.decode_token import decodeToken
from helpers.custom_permissions import IsAuthenticated, IsEmployeeOnly,IsAdminOnly
from employees.models import Employees
from .serializer import *
from .models import *


# Create your views here.

class  ScaleGroupsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminOnly]
    queryset = ScaleGroups.objects.all() 
    serializer_class = ScaleGroupsSerializers 
  
    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            # print(request.data)
           
            # print(organization_id)
            required_fields = ['title','have_aspects','is_default_group']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','title,have_aspects')
            
            query = self.queryset.filter(organization=organization_id,title=request.data['title'],is_active=True)
            request.data['created_by'] = request.user.id
            request.data['organization'] = organization_id
            if not query.exists():
                serializer=self.serializer_class(data = request.data)
                if not serializer.is_valid():
                    return serializerError(serializer.errors)
                serializer.save()
                return successfullyCreated(serializer.data)
            
            else:
                return errorMessage('Title is already exists in this organization')
            
        except Exception as e:
            return exception(e)
        

  
    
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            query = self.queryset.filter(organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def pre_data(self, organization_id):
        try:        
            queryset = ScaleGroups.objects.filter(organization=organization_id, is_active=True)
            query=queryset.values("id","title")
            return query
        except Exception as e:
            return None     
        
    

        
    # def patch(self, request, *args, **kwargs):
    #     try:
    #         sg_id = self.kwargs['pk']
    #         organization_id = decodeToken(request, self.request)['organization_id']
    #         query = ScaleGroups.filter(id=sg_id,organization= organization_id)
    #         if not query.exists():
    #            return nonexistent(var = 'id')
            
    #         obj = query.get()

    #     except Exception as e:
    #         return exception(e)



class ScaleRatingViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ScaleRating.objects.all() 
    serializer_class = ScaleRatingSerializers 

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            required_fields = ['title', 'level']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [title,level]')
            
            level_query = self.queryset.filter(level=request.data['level'],organization=organization_id,is_active=True)
            if level_query.exists():
                return errorMessage('Level is already exists in current organization')
            

            title_query = self.queryset.filter(organization=organization_id,title=request.data['title'],is_active=True)
            
            if  title_query.exists():
                return errorMessage('Title is already exists in this organization')
            
            request.data['created_by'] = request.user.id
            request.data['organization'] = organization_id
            
            serializer=self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
            
        except Exception as e:
            return exception(e)
        
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            query = self.queryset.filter(organization=organization_id,is_active=True).order_by('-id')
            
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
    def pre_data(self, organization_id):
        try:        
            queryset = self.queryset.filter(organization=organization_id, is_active=True)
            query=queryset.values("id","title",'level').order_by('level')
            return query
        except Exception as e:
            return None 
        
class GroupAspectsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminOnly]
    queryset = GroupAspects.objects.all() 
    serializer_class = GroupAspectsSerializers

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
             
            # print(scalegroups)
            required_fields = ['title', 'scale_group']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [title,scale_group]')
            
            query = self.queryset.filter(scale_group=request.data['scale_group'],scale_group__organization=organization_id,title=request.data['title'],is_active=True)
            
            if not query.exists():

                scalegroups_query = ScaleGroups.objects.filter(id=request.data['scale_group'], organization=organization_id)
                if not scalegroups_query.exists():
                    return errorMessage("Scale Group does not exists")
                elif scalegroups_query.filter(is_active=False).exists():
                    return errorMessage("Scale Group is deactivated at this id")
                
                request.data['created_by'] = request.user.id

                serializer=self.serializer_class(data = request.data)

                if not serializer.is_valid():
                    return serializerError(serializer.errors)
                serializer.save()
                return successfullyCreated(serializer.data)
            
            else:
                return errorMessage('Title is already exists in this organization')
            
        except Exception as e:
            return exception(e)
    
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            query = self.queryset.filter(scale_group__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
class AspectsParametersViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated,IsAdminOnly]
    queryset =AspectsParameters.objects.all() 
    serializer_class = AspectsParametersSerializers

    def create(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            required_fields = ['title', 'aspects','is_required']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [title,aspects,is_required]')
            request.data['created_by'] = request.user.id
            
            query = self.queryset.filter(aspects=request.data['aspects'],aspects__scale_group__organization=organization_id,title=request.data['title'],is_active=True)
            if not query.exists():

                aspects_query = GroupAspects.objects.filter(id=request.data['aspects'],scale_group__organization=organization_id)
                if not aspects_query.exists():
                    return errorMessage("Aspects does not exists")
                elif aspects_query.filter(is_active=False).exists():
                    return errorMessage("Aspects is deactivated at this id")

                serializer=self.serializer_class(data = request.data)
                if not serializer.is_valid():
                    return serializerError(serializer.errors)
                serializer.save()
                return successfullyCreated(serializer.data)
            
            else:
                return errorMessage('Title is already exists in this organization')
            
        except Exception as e:
            return exception(e)
        
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(request, self.request)['organization_id']
            query = self.queryset.filter(aspects__scale_group__organization=organization_id,is_active=True).order_by('-id')
            serializer = self.serializer_class(query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)

