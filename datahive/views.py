# Create your views here.
from rest_framework import viewsets

from employees.views_project_roles import EmployeeProjectsRolesViewset
from helpers.custom_permissions import IsAuthenticated
from helpers.decode_token import decodeToken
from projects.models import Projects
from .models import *
from .serializers import *
# support counts for collaboration/comments stored in enhanced models
try:
    from .model_enhanced import DocumentCollaborator, DocumentComment
except Exception:
    DocumentCollaborator = None
    DocumentComment = None
from helpers.status_messages import *
from django.db.models import Q
from functools import reduce


# Create your views here.
class CategoriesViewset(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated]
    queryset=Categories.objects.all()
    serializer_class=CategoriesSerializer

    def create(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user_id = request.user.id
            
            required_fields = ['title']
            if not all(field in request.data for field in required_fields):
                return errorMessageWithData('make sure you have added all required fields','title')
            
            check_query=self.queryset.filter(organization=organization_id,title=request.data['title'],is_active=True)

            if check_query.exists():
                    return errorMessage("This title already exists in this organization")

            
            request.data['organization']=organization_id
            request.data['created_by'] = user_id

            serializer=self.serializer_class(data = request.data)

            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)

        except Exception as e:
          return exception(e)
        
        
    def list(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            check_query=self.queryset.filter(organization=organization_id,is_active=True)
            serializer =self.serializer_class(check_query, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)
    
    def pre_data(self, request, *args, **kwargs):
        try:
            organization_id = decodeToken(self, self.request)['organization_id']
            check_query=self.queryset.filter(organization=organization_id,is_active=True)
            serializer =self.serializer_class(check_query, many=True)            
            return success(serializer.data)
        except Exception as e:
            return exception(e)
        
        

    

class Documentsviewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset=Documents.objects.all()
    serializer_class=DocumentsSerializer

    def create(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user_id = request.user.id
            required_fields = ['title','file','tags',]
            if not all(field in request.data for field in required_fields):
                return errorMessage(
                    'make sure you have added all the required fields: '
                    '[title,file,tags]')
            
            request.data._mutable = True
            
            project=request.data.get('project',None)
            category=request.data.get('category',None)

            tags_input = request.data['tags']  # Get the comma-separated tags
            tag_names = [tag.strip() for tag in tags_input.split(',')]

            if project:
                check_project_query=Projects.objects.filter(id=project,organization=organization_id,is_active=True)
                if not check_project_query.exists():
                    return errorMessage("Project not exists in this organization")
                
            if category:
                check_category_query=Categories.objects.filter(id=category,organization=organization_id,is_active=True)
                if not check_category_query.exists():
                    return errorMessage("Category not exists in this organization")
                
            if 'is_public' not in request.data:
                request.data['is_public']=True
            
            request.data['organization']=organization_id
            request.data['created_by']=user_id
            request.data['is_active']=True
            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                # if serializer.errors.get('file'):
                #     return errorMessage(serializer.errors.get('file', [''])[0])
                # print(serializer.errors)
                return serializerError(serializer.errors)
            

            document = serializer.save()  # Save the document without tags

            # Step 2: Handle tags
            for tag_name in tag_names:
                if tag_name:  # Only process non-empty tag names
                    tag, created = Tags.objects.get_or_create(
                        name=tag_name,
                        defaults={'created_by': document.created_by, 'organization': document.organization}  # Set created_by when creating a new tag
                    )
                    document.tags.add(tag)  # Add the tag to the document

            # Re-serialize the saved document to include tags and any file URL fields
            serialized = self.serializer_class(document)
            return success(serialized.data)

        except Exception as e:
            return exception(e)
        
    
    def list(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            title = request.data.get('title', None)
            tag = request.data.get('tags', None)
            project=request.data.get('project',None)
            category=request.data.get('category',None)
            created_by=request.data.get('created_by',None)



            employee_id = request.data.get('employee',None)
            if employee_id is None:
                employee_id = token_data['employee_id']

            employees_projects = EmployeeProjectsRolesViewset().pre_data(employee_id, organization_id, is_active=True)
            employee_project_ids = [emp_project['project'] for emp_project in employees_projects]
            

            
            # Start from active documents in the organization
            query = self.queryset.filter(organization=organization_id, is_active=True)

            if title is None and tag is None and project is None and category is None and created_by is None:
                return errorMessage("At least use one filter otherwise no data shown")

            if title:
                query = query.filter(title__icontains=title)

            if category:
                query = query.filter(category=category)

            if created_by:
                query = query.filter(created_by=created_by)

             # Check if project ID is provided

            # If a project filter is provided, enforce access rules:
            # - Owner or collaborator can see private files for that project
            # - Members (non-collaborator) can only see public files
            if project:
                # convert to int/str safely
                try:
                    proj_val = int(project)
                except Exception:
                    proj_val = project

                # If the requested project is one of the employee projects
                if proj_val in employee_project_ids:
                    # show files in this project but exclude private files unless owner/collaborator
                    # Build owner/collaborator filter
                    from .model_enhanced import DocumentCollaborator as UploadedDocCollaborator
                    # collaborator.user is HrmsUsers, so match against request.user.id
                    owner_or_collab_ids = UploadedDocCollaborator.objects.filter(user_id=request.user.id).values_list('document_id', flat=True)
                    # owner = created_by == current user's hrmsuser id
                    # show either public files OR files where user is owner or collaborator
                    query = query.filter(project=project).filter(Q(is_public=True) | Q(created_by=request.user.id) | Q(id__in=owner_or_collab_ids)).distinct()
                else:
                    # project not part of employee's projects — only show public files for that project
                    query = query.filter(project=project, is_public=True)
            else:
                # No project filter: show files where project is in employee_project_ids (public only) OR created_by/current user's collaborations
                from .model_enhanced import DocumentCollaborator as UploadedDocCollaborator
                owner_or_collab_ids = UploadedDocCollaborator.objects.filter(user_id=request.user.id).values_list('document_id', flat=True)
                query = query.filter(Q(project__in=employee_project_ids, is_public=True) | Q(is_public=True) | Q(created_by=request.user.id) | Q(id__in=owner_or_collab_ids)).distinct()


            # if project:
            #     query = query.filter(project=project)

            # else:
            #     # If no project specified, retrieve projects related to the employee
            #     employees_projects = EmployeeProjectsRolesViewset().pre_data(employee_id, organization_id, is_active=True)
            #     # print(employees_projects)
            #     # Collect project IDs from employee's projects
            #     employee_project_ids = [emp_project['project'] for emp_project in employees_projects]
            #     # print(employee_project_ids)

            #     # Filter files related to employee's projects or public files
            #     query = query.filter(Q(project__in=employee_project_ids) | Q(is_public=True)).distinct()


            if tag:
                tag_names = [tag.strip() for tag in tag.split(',')]
                query_filter = Q()

                for tag in tag_names:
                    query_filter |= Q(tags__name__icontains=tag)  # Using OR to match any of the tags

                query = query.filter(query_filter).distinct()


            if not query.exists():
                    return errorMessage("No data found matching the given filters.")
            
            query = query.prefetch_related('tags')

            # Serialize the data
            serializer = self.serializer_class(query, many=True)
            data = serializer.data

            # augment each document payload with collaborators_count, comments_count, and collaborators if the enhanced models exist
            if DocumentCollaborator is not None and DocumentComment is not None:
                for d in data:
                    try:
                        doc_id = d.get('id')
                        d['collaborators_count'] = DocumentCollaborator.objects.filter(document_id=doc_id).count()
                        d['comments_count'] = DocumentComment.objects.filter(document_id=doc_id).count()
                        
                        # Include collaborators data for role checking
                        collabs = DocumentCollaborator.objects.filter(document_id=doc_id).select_related('user')
                        collaborators = []
                        for c in collabs:
                            user = getattr(c, 'user', None)
                            profile_image = None
                            employee_obj = None
                            try:
                                if user:
                                    from employees.models import Employees
                                    employee_obj = Employees.objects.filter(hrmsuser=user, is_active=True).first()
                                    if employee_obj and getattr(employee_obj, 'profile_image', None):
                                        profile_image = employee_obj.profile_image.url
                            except Exception:
                                profile_image = None

                            first_name = getattr(employee_obj, 'first_name', None) if employee_obj else (getattr(user, 'first_name', None) if user else None)
                            last_name = getattr(employee_obj, 'last_name', None) if employee_obj else (getattr(user, 'last_name', None) if user else None)
                            full_name = ' '.join([n for n in [first_name, last_name] if n]) if (first_name or last_name) else None

                            collaborators.append({
                                'id': c.id,
                                'user_id': user.id if user else None,
                                'employee_id': employee_obj.id if employee_obj else None,
                                'first_name': first_name,
                                'last_name': last_name,
                                'name': full_name,
                                'email': getattr(user, 'email', None) if user else None,
                                'profile_image': profile_image,
                                'role': c.role,
                                'created_at': c.created_at
                            })
                        d['collaborators'] = collaborators
                    except Exception:
                        d['collaborators_count'] = 0
                        d['comments_count'] = 0
                        d['collaborators'] = []

            return success(data)
        except Exception as e:
            return exception(e)
        
    def get_tags(self,request,*args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            tag = request.data.get('tags', None)
            query=None
            if tag:
                query =Tags.objects.filter(name__icontains=tag,organization=organization_id,is_active=True)

            serializer=TagsSerializer(query,many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)


    def patch(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            user_id = request.user.id
            document_id = kwargs.get('pk')  # Assuming the document ID is passed in the URL

            # Retrieve the document
            document = Documents.objects.filter(id=document_id, organization_id=organization_id, is_active=True)
            if not document.exists():
                return errorMessage("Document not found or does not belong to this organization")
            elif not document.filter(created_by=user_id).exists():
                return errorMessage("Only the user who created this document can update it")
            document=document.get()
            # Update fields only if provided in the request
            project = request.data.get('project', None)
            category = request.data.get('category', None)
            tags_input = request.data.get('tags', None)  # Get the comma-separated tags

            if project:
                check_project_query = Projects.objects.filter(id=project, organization=organization_id, is_active=True)
                if not check_project_query.exists():
                    return errorMessage("Project not exists in this organization")

            if category:
                check_category_query = Categories.objects.filter(id=category, organization=organization_id, is_active=True)
                if not check_category_query.exists():
                    return errorMessage("Category not exists in this organization")
                
            serializer = self.serializer_class(document,data=request.data,partial=True)
            if not serializer.is_valid():
                # if serializer.errors.get('file'):
                #     return errorMessage(serializer.errors.get('file', [''])[0])
                # print(serializer.errors)
                return serializerError(serializer.errors)
            

            document = serializer.save() 
                
            if tags_input:
                tag_names = [tag.strip() for tag in tags_input.split(',')]  # Split and strip tags
                existing_tags = {tag.name for tag in document.tags.filter(is_active=True)}  # Get existing tags
                input_tags = set(tag_names)

                # Add new tags
                for tag_name in input_tags - existing_tags:
                    if tag_name:  # Only process non-empty tag names
                        tag, created = Tags.objects.get_or_create(
                            name=tag_name,
                            defaults={
                                'created_by': document.created_by,
                                'organization': document.organization
                            }
                        )
                        document.tags.add(tag)

                # Remove tags not in the input
                for tag_name in existing_tags - input_tags:
                    tag = Tags.objects.filter(name=tag_name, organization=document.organization).first()
                    if tag:
                        tag.is_active=False
                        tag.save()


            return success(serializer.data)

        except Exception as e:
            return exception(e) 

    def delete(self, request, *args, **kwargs):
        try:
            token_data = decodeToken(self, self.request)
            organization_id = token_data['organization_id']
            pk = self.kwargs['pk']
            user_id=request.user.id

            query = self.queryset.filter(id=pk,organization=organization_id)
            if not query.exists():
                return errorMessage('File does not exists')
            elif not query.filter(is_active=True).exists():
                return errorMessage('File is already deleted at this id')
            elif not query.filter(created_by=user_id).exists():
                return errorMessage("Only the user who created this document can delete it")
            
            obj = query.get()
 
            obj.is_active=False
            obj.save()
            return successMessage('Successfully deleted')
        except Exception as e:
            return exception(e)
        



