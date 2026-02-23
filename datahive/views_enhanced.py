from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.http import HttpResponse
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import os
import uuid
from datetime import datetime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from helpers.custom_permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from helpers.decode_token import decodeToken
from .model_enhanced import (
    RichDocuments,
    RichDocumentCollaborator,
    RichDocumentVersion,
    RichDocumentComment,
    RichDocumentChecklistItem,
    RichDocumentMention,
    RichDocumentShare,
    RichDocumentActivity,
    RichDocumentWorkspace,
    RichDocumentEditingSession
)
from .model_enhanced import DocumentCollaborator, DocumentComment
from .models import Documents
from .serializers_enhanced import (
    RichDocumentsSerializer,
    RichDocumentCollaboratorSerializer,
    RichDocumentVersionSerializer,
    RichDocumentCommentSerializer,
    RichDocumentChecklistItemSerializer,
    RichDocumentMentionSerializer,
    RichDocumentShareSerializer,
    RichDocumentActivitySerializer,
    RichDocumentWorkspaceSerializer
)
from .serializers import DocumentsSerializer
from projects.models import Projects
from .models import Categories, Tags
from employees.models import Employees
from helpers.notification_helper import send_collaboration_notification, send_comment_notification, send_mention_notification


class RichDocumentsViewset(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _check_document_permission(self, document, user_id, required_permission='view'):
        """
        Check if user has required permission on document
        required_permission: 'view', 'edit', 'delete', 'manage'
        """
        # Document creator always has full permissions
        if getattr(document, 'created_by_id', None) == user_id:
            return True

        # Check if this is an uploaded document (Documents model)
        is_uploaded_document = hasattr(document, 'file')  # Documents model has file field
        
        # Look for explicit collaborator entry
        try:
            if is_uploaded_document:
                from .model_enhanced import DocumentCollaborator
                collab = DocumentCollaborator.objects.filter(document=document, user_id=user_id).first()
            else:
                collab = RichDocumentCollaborator.objects.filter(document=document, user_id=user_id).first()
                
            if not collab:
                return False

            # Different permission sets for uploaded vs rich documents
            if is_uploaded_document:
                # Uploaded documents: no editing, only view and manage for owners
                role_permissions = {
                    'owner': ['view', 'manage'],  # Removed 'edit'
                    'editor': ['view'],  # Editor can only view for uploaded docs
                    'viewer': ['view']
                }
            else:
                # Rich documents: full permissions
                role_permissions = {
                    'owner': ['view', 'edit', 'manage'],
                    'editor': ['view', 'edit'],
                    'viewer': ['view']
                }

            # 'delete' is intentionally not granted to collaborator 'owner' — only creator can delete
            return required_permission in role_permissions.get(collab.role, [])
        except Exception:
            return False

    def _wants_json(self, request):
        # Robust detection for API/XHR callers: check Accept header and X-Requested-With
        try:
            accept = request.META.get('HTTP_ACCEPT', '') or ''
            xrw = request.META.get('HTTP_X_REQUESTED_WITH') or request.headers.get('X-Requested-With') if hasattr(request, 'headers') else request.META.get('HTTP_X_REQUESTED_WITH')
            return ('application/json' in accept) or (xrw == 'XMLHttpRequest')
        except Exception:
            return False

    def get_permissions(self):
        # Allow unauthenticated GET /view/ for public documents
        if getattr(self, 'action', None) == 'view':
            return [AllowAny()]
        return [permission() if isinstance(permission, type) else permission for permission in self.permission_classes]

    def _get_org_user(self, request):
        token = decodeToken(self, request)
        return token['organization_id'], request.user.id

    @action(methods=['post'], detail=False, url_path='upload_image')
    def upload_image(self, request):
        """Handle image uploads for rich documents"""
        try:
            organization_id, user_id = self._get_org_user(request)
            
            if 'image' not in request.FILES:
                return Response({'status': 400, 'message': 'No image file provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            image_file = request.FILES['image']
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if image_file.content_type not in allowed_types:
                return Response({'status': 400, 'message': 'Invalid image format. Allowed: JPEG, PNG, GIF, WebP'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate file size (5MB max)
            if image_file.size > 5 * 1024 * 1024:
                return Response({'status': 400, 'message': 'Image size too large. Maximum 5MB allowed'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate unique filename
            file_extension = os.path.splitext(image_file.name)[1]
            unique_filename = f"rich_docs/images/{datetime.now().strftime('%Y/%m')}/{uuid.uuid4()}{file_extension}"
            
            # Save file
            saved_path = default_storage.save(unique_filename, ContentFile(image_file.read()))
            file_url = default_storage.url(saved_path)
            
            # Make URL absolute if needed
            if not file_url.startswith(('http://', 'https://')):
                file_url = request.build_absolute_uri(file_url)
            
            return Response({
                'status': 200, 
                'data': {
                    'url': file_url,
                    'filename': image_file.name,
                    'size': image_file.size
                }
            })
            
        except Exception as e:
            return Response({'status': 500, 'message': f'Image upload failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """Used by editor auto-save and manual save. If `id` present, update."""
        try:
            organization_id, user_id = self._get_org_user(request)

            data = request.data.copy()
            data['organization'] = organization_id
            data['created_by'] = user_id

            # Validate project and category if provided
            project = data.get('project', None)
            category = data.get('category', None)
            if project:
                if not Projects.objects.filter(id=project, organization=organization_id, is_active=True).exists():
                    return Response({'message': 'Project not exists in this organization'}, status=status.HTTP_400_BAD_REQUEST)
            if category:
                if not Categories.objects.filter(id=category, organization=organization_id, is_active=True).exists():
                    return Response({'message': 'Category not exists in this organization'}, status=status.HTTP_400_BAD_REQUEST)

            tags_input = data.get('tags', '')
            tag_names = [t.strip().lower() for t in tags_input.split(',')] if tags_input else []

            serializer = RichDocumentsSerializer(data=data)
            if serializer.is_valid():
                with transaction.atomic():
                    obj = serializer.save(created_by_id=user_id, organization_id=organization_id)

                    # handle tags in bulk
                    new_tag_names = [t for t in tag_names if t]
                    if new_tag_names:
                        existing_tags = list(Tags.objects.filter(name__in=new_tag_names, organization_id=organization_id))
                        existing_names = {t.name for t in existing_tags}
                        to_create = [Tags(name=name, created_by_id=user_id, organization_id=organization_id) for name in new_tag_names if name not in existing_names]
                        if to_create:
                            Tags.objects.bulk_create(to_create, ignore_conflicts=True)
                        all_tags = list(Tags.objects.filter(name__in=new_tag_names, organization_id=organization_id))
                        obj.tags.add(*all_tags)

                    # create a version snapshot
                    RichDocumentVersion.objects.create(
                        document=obj,
                        title=obj.title,
                        content=obj.content,
                        word_count=obj.word_count or 0,
                        created_by_id=user_id
                    )

                    # CREATE ACTIVITY ENTRY FOR DOCUMENT CREATION
                    RichDocumentActivity.objects.create(
                        document=obj,
                        user_id=user_id,
                        activity_type='created',
                        description=f'Document created by {request.user.first_name} {request.user.last_name}',
                        metadata={
                            'title': obj.title,
                            'word_count': obj.word_count or 0
                        }
                    )

                return Response({'status': 200, 'data': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'status': 400, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=False, url_path='create_rich_document')
    def create_rich_document(self, request):
        # Finalize creation of document (frontend calls this after manual save)
        return self.create(request)

    def list(self, request):
        try:
            organization_id, user_id = self._get_org_user(request)
            
            # Get query parameters with proper defaults
            search = request.query_params.get('search', '')
            project_id = request.query_params.get('project')
            category_id = request.query_params.get('category')
            is_template = request.query_params.get('is_template')
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            show_archived = request.query_params.get('show_archived', 'false').lower() == 'true'
            
            # Build query following access rules:
            # - Owner: can see all documents in the organization
            # - Collaborator: can see documents they're invited to
            # - Member: can see documents where is_public=True and (project is None OR they are member of project)
            collaborator_docs = RichDocumentCollaborator.objects.filter(user_id=user_id).values_list('document_id', flat=True)

            # documents where user is owner or explicit collaborator
            owner_or_collab_q = Q(created_by=user_id) | Q(id__in=collaborator_docs)

            # public documents: either not project-scoped (public link) or project-scoped and user is project member
            from employees.models import EmployeeProjects
            member_project_ids = EmployeeProjects.objects.filter(employee__hrmsuser_id=user_id, employee__organization_id=organization_id, is_active=True).values_list('project_id', flat=True)
            public_q = Q(is_public=True) & (Q(project__isnull=True) | Q(project_id__in=member_project_ids))

            query = RichDocuments.objects.filter(organization=organization_id).filter(owner_or_collab_q | public_q)
            
            if not show_archived:
                query = query.filter(is_archived=False)
            
            # Apply filters
            if search:
                query = query.filter(
                    Q(title__icontains=search) | 
                    Q(content__icontains=search) |
                    Q(tags__name__icontains=search)
                ).distinct()
                
            if project_id:
                query = query.filter(project_id=project_id)
            if category_id:
                query = query.filter(category_id=category_id)
            if is_template is not None:
                query = query.filter(is_template=is_template.lower() == 'true')
            
            # Apply ordering
            query = query.order_by('-created_at')
            
            # Apply pagination
            start = (page - 1) * page_size
            end = start + page_size
            total_count = query.count()
            documents = query[start:end]
            
            serializer = RichDocumentsSerializer(documents, many=True, context={'request': request})
            return Response({
                'status': 200, 
                'data': serializer.data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
            })
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """Retrieve a single rich document (JSON)"""
        try:
            organization_id, user_id = self._get_org_user(request)
            try:
                document = RichDocuments.objects.get(id=pk, organization=organization_id)
            except RichDocuments.DoesNotExist:
                return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = RichDocumentsSerializer(document, context={'request': request})
            data = serializer.data
            # augment with simple counts
            try:
                collabs = RichDocumentCollaborator.objects.filter(document=document).count()
                comms = RichDocumentComment.objects.filter(document=document).count()
                versions = RichDocumentVersion.objects.filter(document=document).count()
            except Exception:
                collabs = comms = versions = 0
            data['collaborators_count'] = collabs
            data['comments_count'] = comms
            data['versions_count'] = versions
            data['_type'] = 'rich_document'

            return Response({'status': 200, 'data': data})
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        """Update a document (full update)"""
        try:
            organization_id, user_id = self._get_org_user(request)
            try:
                document = RichDocuments.objects.get(id=pk, organization=organization_id)
            except RichDocuments.DoesNotExist:
                return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
            # Permission check: owner or editors may edit
            if not self._check_document_permission(document, user_id, 'edit'):
                return Response({'status': 403, 'message': 'You do not have permission to edit this document'}, status=status.HTTP_403_FORBIDDEN)
            
            data = request.data.copy()
            data['organization'] = organization_id
            data['created_by'] = user_id
            
            serializer = RichDocumentsSerializer(document, data=data, context={'request': request})
            if serializer.is_valid():
                with transaction.atomic():
                    obj = serializer.save()
                    
                    # Update tags
                    tags_input = data.get('tags', '')
                    tag_names = [t.strip() for t in tags_input.split(',')] if tags_input else []
                    obj.tags.clear()
                    
                    for tag_name in tag_names:
                        if tag_name:
                            tag, created = Tags.objects.get_or_create(
                                name=tag_name,
                                defaults={'created_by_id': user_id, 'organization_id': organization_id}
                            )
                            obj.tags.add(tag)
                
                    # create a version snapshot on update
                    RichDocumentVersion.objects.create(
                        document=obj,
                        title=obj.title,
                        content=obj.content,
                        word_count=obj.word_count or 0,
                        created_by_id=user_id
                    )

                    # CREATE ACTIVITY ENTRY FOR DOCUMENT UPDATE
                    updated_fields = list(request.data.keys())
                    RichDocumentActivity.objects.create(
                        document=obj,
                        user_id=user_id,
                        activity_type='updated',
                        description=f'Document updated by {request.user.first_name} {request.user.last_name}',
                        metadata={
                            'updated_fields': updated_fields,
                            'word_count': obj.word_count or 0
                        }
                    )

                return Response({'status': 200, 'data': serializer.data})
            return Response({'status': 400, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk=None):
        """Update a document (partial update)"""
        try:
            organization_id, user_id = self._get_org_user(request)
            try:
                document = RichDocuments.objects.get(id=pk, organization=organization_id)
            except RichDocuments.DoesNotExist:
                return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

            # Permission check: owner or editors may partial update
            if not self._check_document_permission(document, user_id, 'edit'):
                return Response({'status': 403, 'message': 'You do not have permission to edit this document'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = RichDocumentsSerializer(document, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                with transaction.atomic():
                    obj = serializer.save()
                    
                    # Update tags if provided
                    if 'tags' in request.data:
                        tags_input = request.data.get('tags', '')
                        tag_names = [t.strip() for t in tags_input.split(',')] if tags_input else []
                        obj.tags.clear()
                        
                        for tag_name in tag_names:
                            if tag_name:
                                tag, created = Tags.objects.get_or_create(
                                    name=tag_name,
                                    defaults={'created_by_id': user_id, 'organization_id': organization_id}
                                )
                                obj.tags.add(tag)
                
                    # optional version snapshot if content/title changed
                    if any(field in request.data for field in ['title', 'content', 'word_count']):
                        RichDocumentVersion.objects.create(
                            document=obj,
                            title=obj.title,
                            content=obj.content,
                            word_count=obj.word_count or 0,
                            created_by_id=user_id
                        )

                    # CREATE ACTIVITY ENTRY FOR DOCUMENT UPDATE
                    updated_fields = list(request.data.keys())
                    RichDocumentActivity.objects.create(
                        document=obj,
                        user_id=user_id,
                        activity_type='updated',
                        description=f'Document updated by {request.user.first_name} {request.user.last_name}',
                        metadata={
                            'updated_fields': updated_fields,
                            'word_count': obj.word_count or 0
                        }
                    )

                return Response({'status': 200, 'data': serializer.data})
            return Response({'status': 400, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        """Delete a document"""
        try:
            organization_id, user_id = self._get_org_user(request)
            try:
                document = RichDocuments.objects.get(id=pk, organization=organization_id)
            except RichDocuments.DoesNotExist:
                return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

            # Permission check: only owner may delete
            if not self._check_document_permission(document, user_id, 'delete'):
                return Response({'status': 403, 'message': 'You do not have permission to delete this document'}, status=status.HTTP_403_FORBIDDEN)

            # Log activity before deletion
            RichDocumentActivity.objects.create(
                document=document,
                user_id=user_id,
                activity_type='deleted',
                description=f'Document deleted by {request.user.first_name} {request.user.last_name}'
            )

            document.delete()
            return Response({'status': 200, 'message': 'Document deleted successfully'})
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def view(self, request, pk=None):
        """Render a read-only HTML view of a rich document for opening in a new tab"""
        try:
            document = RichDocuments.objects.filter(id=pk).first()
            wants_json = self._wants_json(request)
            if not document:
                if wants_json:
                    return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
                return HttpResponse('<h3>Document not found</h3>', status=404)

            # Visibility rules:
            # - Private document: only owner or explicit collaborators may view
            # - Public document with project: only users who are part of that project OR collaborators/owner can view
            # - Public document without project: allow anonymous (public link)

            # Private documents require authentication and collaborator/owner check
            if not document.is_public:
                if not request.user or not request.user.is_authenticated:
                    if wants_json:
                        return Response({'status': 401, 'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
                    return HttpResponse('<h3>Authentication required</h3>', status=401)
                org_id, user_id = self._get_org_user(request)
                if document.organization_id != org_id:
                    if wants_json:
                        return Response({'status': 403, 'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
                    return HttpResponse('<h3>Forbidden</h3>', status=403)

                # allowed if owner or collaborator
                if document.created_by_id != user_id and not RichDocumentCollaborator.objects.filter(document=document, user_id=user_id).exists():
                    if wants_json:
                        return Response({'status': 403, 'message': 'You do not have access to this private document'}, status=status.HTTP_403_FORBIDDEN)
                    return HttpResponse('<h3>Forbidden</h3>', status=403)

            else:
                # public document
                if document.project_id:
                    # project-scoped public document: user must be authenticated and member of project OR collaborator/owner
                    if not request.user or not request.user.is_authenticated:
                        if wants_json:
                            return Response({'status': 401, 'message': 'Authentication required for project-scoped public document'}, status=status.HTTP_401_UNAUTHORIZED)
                        return HttpResponse('<h3>Authentication required</h3>', status=401)
                    org_id, user_id = self._get_org_user(request)
                    if document.organization_id != org_id:
                        if wants_json:
                            return Response({'status': 403, 'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
                        return HttpResponse('<h3>Forbidden</h3>', status=403)

                    # check project membership
                    from employees.models import EmployeeProjects
                    member = EmployeeProjects.objects.filter(project_id=document.project_id, employee__hrmsuser_id=user_id, employee__organization_id=org_id, is_active=True).exists()
                    collab = RichDocumentCollaborator.objects.filter(document=document, user_id=user_id).exists()
                    if not (member or collab or document.created_by_id == user_id):
                        if wants_json:
                            return Response({'status': 403, 'message': 'You are not a member of this project or collaborator'}, status=status.HTTP_403_FORBIDDEN)
                        return HttpResponse('<h3>Forbidden</h3>', status=403)
                else:
                    # public and not tied to a project -> allow anonymous access (public link)
                    pass

            # Log view activity for authenticated users
            if request.user and request.user.is_authenticated:
                try:
                    RichDocumentActivity.objects.create(
                        document=document,
                        user_id=request.user.id,
                        activity_type='viewed',
                        description=f'Document viewed by {request.user.first_name} {request.user.last_name}'
                    )
                except Exception:
                    pass

            # Prepare collaborators and comments HTML snippets
            collaborators_html = ''
            try:
                collabs = RichDocumentCollaborator.objects.filter(document=document)
                if collabs.exists():
                    collaborators_html = '<h3>Collaborators</h3><ul>' + ''.join([f"<li>{c.user.first_name} {c.user.last_name} ({c.user.email}) - {c.role}</li>" for c in collabs]) + '</ul>'
            except Exception:
                collaborators_html = ''

            comments_html = ''
            try:
                comms = RichDocumentComment.objects.filter(document=document)
                if comms.exists():
                    comments_html = '<h3>Comments</h3><ul>' + ''.join([f"<li><strong>{(c.author.first_name + ' ' + c.author.last_name).strip()}</strong>: {c.content}</li>" for c in comms]) + '</ul>'
            except Exception:
                comments_html = ''

            html = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{document.title}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; margin: 24px; color: #222; }}
    .container {{ max-width: 900px; margin: 0 auto; }}
    h1,h2,h3 {{ margin: 0 0 12px; }}
    .meta {{ color:#666; font-size: 13px; margin-bottom: 16px; }}
    .content {{ line-height: 1.6; }}
    .content img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 16px 0; }}
  </style>
  </head>
            <body>
        <div class=\"container\"> 
            <h2>{document.title}</h2>
            <div class=\"meta\">Created: {document.created_at.strftime('%Y-%m-%d %H:%M')}</div>
            <div class=\"content\">{document.content or ''}</div>
            <div class=\"collaboration\">{collaborators_html}{comments_html}</div>
        </div>
    </body>
</html>
"""
            # Return JSON for API/XHR clients, HTML for browsers
            if wants_json:
                serializer = RichDocumentsSerializer(document, context={'request': request})
                return Response({'status': 200, 'data': serializer.data})
            return HttpResponse(html)
        except Exception as e:
            wants_json = self._wants_json(request)
            if wants_json:
                return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return HttpResponse(f"<h3>Error rendering document</h3><pre>{str(e)}</pre>", status=500)

    @action(methods=['post'], detail=True, url_path='start_edit')
    def start_edit(self, request, pk=None):
        """Start an editing session - Enhanced with immediate lock acquisition"""
        try:
            organization_id, user_id = self._get_org_user(request)
            try:
                document = RichDocuments.objects.get(id=pk, organization=organization_id)
            except RichDocuments.DoesNotExist:
                return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

            # Check edit permission
            if not self._check_document_permission(document, user_id, 'edit'):
                return Response({'status': 403, 'message': 'No edit permission'}, status=status.HTTP_403_FORBIDDEN)

            # Enhanced lock checking - more aggressive cleanup of stale sessions
            stale_time = timezone.now() - timedelta(minutes=2)  # Reduced from 5 to 2 minutes
            RichDocumentEditingSession.objects.filter(
                document=document,
                last_activity__lt=stale_time
            ).update(is_active=False)

            # Check if document is already being edited by someone else
            active_sessions = RichDocumentEditingSession.objects.filter(
                document=document,
                is_active=True
            ).exclude(user_id=user_id).first()

            if active_sessions:
                return Response({
                    'status': 409,
                    'message': f'Document is currently being edited by {active_sessions.user.first_name} {active_sessions.user.last_name}'
                }, status=status.HTTP_409_CONFLICT)

            # Create or update editing session with immediate activity update
            session, created = RichDocumentEditingSession.objects.update_or_create(
                document=document,
                user_id=user_id,
                defaults={
                    'last_activity': timezone.now(), 
                    'is_active': True,
                    'session_start': timezone.now()
                }
            )

            # Log editing session start
            RichDocumentActivity.objects.create(
                document=document,
                user_id=user_id,
                activity_type='updated',
                description=f'Started editing session',
                metadata={
                    'session_id': session.id,
                    'session_start': session.session_start.isoformat()
                }
            )

            return Response({'status': 200, 'message': 'Editing session started'})
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=True, url_path='end_edit')
    def end_edit(self, request, pk=None):
        """End an editing session"""
        try:
            organization_id, user_id = self._get_org_user(request)

            # End all active sessions for this user and document
            sessions = RichDocumentEditingSession.objects.filter(
                document_id=pk,
                user_id=user_id,
                is_active=True
            )
            
            for session in sessions:
                # Log editing session end
                RichDocumentActivity.objects.create(
                    document_id=pk,
                    user_id=user_id,
                    activity_type='updated',
                    description=f'Ended editing session',
                    metadata={
                        'session_id': session.id,
                        'session_duration': str(timezone.now() - session.session_start)
                    }
                )

            sessions.update(is_active=False)

            return Response({'status': 200, 'message': 'Editing session ended'})
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=True, url_path='update_activity')
    def update_activity(self, request, pk=None):
        """Update editing session activity timestamp"""
        try:
            organization_id, user_id = self._get_org_user(request)
            
            # Update the last_activity timestamp for active sessions
            sessions_updated = RichDocumentEditingSession.objects.filter(
                document_id=pk,
                user_id=user_id,
                is_active=True
            ).update(last_activity=timezone.now())
            
            if sessions_updated > 0:
                return Response({'status': 200, 'message': 'Activity updated'})
            else:
                return Response({'status': 404, 'message': 'No active session found'}, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['get'], detail=True, url_path='active_editors')
    def active_editors(self, request, pk=None):
        """Get currently active editors"""
        try:
            organization_id, user_id = self._get_org_user(request)

            # Clean up stale sessions first
            stale_time = timezone.now() - timedelta(minutes=2)
            RichDocumentEditingSession.objects.filter(
                document_id=pk,
                last_activity__lt=stale_time
            ).update(is_active=False)

            active_sessions = RichDocumentEditingSession.objects.filter(
                document_id=pk,
                is_active=True
            ).select_related('user')

            editors = []
            for session in active_sessions:
                editors.append({
                    'id': session.user_id,
                    'name': f"{session.user.first_name} {session.user.last_name}",
                    'session_start': session.session_start,
                    'last_activity': session.last_activity
                })

            return Response({'status': 200, 'data': editors})
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['get'], detail=True, url_path='check_edit_lock')
    def check_edit_lock(self, request, pk=None):
        """Check if document is currently locked for editing - Enhanced with immediate stale session cleanup"""
        try:
            organization_id, user_id = self._get_org_user(request)
            try:
                document = RichDocuments.objects.get(id=pk, organization=organization_id)
            except RichDocuments.DoesNotExist:
                return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

            # Clean up stale sessions first (sessions older than 2 minutes)
            stale_time = timezone.now() - timedelta(minutes=2)
            stale_sessions = RichDocumentEditingSession.objects.filter(
                document=document,
                last_activity__lt=stale_time,
                is_active=True
            )
            if stale_sessions.exists():
                stale_sessions.update(is_active=False)

            # Check for active editing sessions
            active_sessions = RichDocumentEditingSession.objects.filter(
                document=document,
                is_active=True
            ).select_related('user').first()

            if active_sessions:
                return Response({
                    'status': 200,
                    'data': {
                        'is_locked': True,
                        'current_editor': {
                            'id': active_sessions.user.id,
                            'name': f"{active_sessions.user.first_name} {active_sessions.user.last_name}",
                            'session_start': active_sessions.session_start,
                            'last_activity': active_sessions.last_activity
                        }
                    }
                })
            else:
                return Response({
                    'status': 200,
                    'data': {
                        'is_locked': False,
                        'current_editor': None
                    }
                })
                
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=True, url_path='archive')
    def archive(self, request, pk=None):
        """Archive a document"""
        try:
            organization_id, user_id = self._get_org_user(request)
            try:
                document = RichDocuments.objects.get(id=pk, organization=organization_id)
            except RichDocuments.DoesNotExist:
                return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
            
            document.is_archived = True
            document.save()
            
            # Log activity
            RichDocumentActivity.objects.create(
                document=document,
                user_id=user_id,
                activity_type='archived',
                description=f'Document archived by {request.user.first_name} {request.user.last_name}'
            )
            
            return Response({'status': 200, 'message': 'Document archived successfully'})
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=True, url_path='restore')
    def restore(self, request, pk=None):
        """Restore an archived document"""
        try:
            organization_id, user_id = self._get_org_user(request)
            try:
                document = RichDocuments.objects.get(id=pk, organization=organization_id)
            except RichDocuments.DoesNotExist:
                return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
            
            document.is_archived = False
            document.save()
            
            # Log activity
            RichDocumentActivity.objects.create(
                document=document,
                user_id=user_id,
                activity_type='restored',
                description=f'Document restored by {request.user.first_name} {request.user.last_name}'
            )
            
            return Response({'status': 200, 'message': 'Document restored successfully'})
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['get'], detail=True, url_path='activities')
    def activities(self, request, pk=None):
        """Get document activities"""
        try:
            organization_id, user_id = self._get_org_user(request)
            try:
                document = RichDocuments.objects.get(id=pk, organization=organization_id)
            except RichDocuments.DoesNotExist:
                return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
            
            activities = RichDocumentActivity.objects.filter(document=document).select_related('user').order_by('-created_at')
            serializer = RichDocumentActivitySerializer(activities, many=True)
            return Response({'status': 200, 'data': serializer.data})
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=True, url_path='share')
    def share(self, request, pk=None):
        """Share document with external users"""
        try:
            organization_id, user_id = self._get_org_user(request)
            try:
                document = RichDocuments.objects.get(id=pk, organization=organization_id)
            except RichDocuments.DoesNotExist:
                return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
            
            data = request.data.copy()
            data['document'] = pk
            data['shared_by'] = user_id
            
            serializer = RichDocumentShareSerializer(data=data)
            if serializer.is_valid():
                share_obj = serializer.save()
                
                # Log sharing activity
                RichDocumentActivity.objects.create(
                    document=document,
                    user_id=user_id,
                    activity_type='shared',
                    description=f'Document shared by {request.user.first_name} {request.user.last_name}',
                    metadata={
                        'share_type': share_obj.share_type,
                        'shared_with': share_obj.shared_with_email or (share_obj.shared_with_user.email if share_obj.shared_with_user else None)
                    }
                )
                
                return Response({'status': 200, 'data': serializer.data})
            return Response({'status': 400, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CollaboratorsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _get_org_user(self, request):
        token = decodeToken(self, request)
        return token['organization_id'], request.user.id

    def list(self, request):
        try:
            organization_id, user_id = self._get_org_user(request)
            document_id = request.query_params.get('document')
            if not document_id:
                return Response({'status': 400, 'message': 'document is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Try rich document first, then fallback to regular uploaded Documents
            document = None
            is_rich = False
            try:
                document = RichDocuments.objects.get(id=document_id, organization_id=organization_id)
                is_rich = True
            except RichDocuments.DoesNotExist:
                # try regular uploaded Documents
                try:
                    document = Documents.objects.get(id=document_id, organization_id=organization_id)
                    is_rich = False
                except Documents.DoesNotExist:
                    return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

            if is_rich:
                collaborators = RichDocumentCollaborator.objects.filter(document=document)
                serializer = RichDocumentCollaboratorSerializer(collaborators, many=True)
                # indicate whether current user can manage collaborators (document creator OR collaborator with owner role)
                can_manage = (document.created_by_id == user_id) or RichDocumentCollaborator.objects.filter(document=document, user_id=user_id, role='owner').exists()
                return Response({'status': 200, 'data': {'collaborators': serializer.data, 'can_manage': can_manage, 'document': RichDocumentsSerializer(document, context={"request": request}).data}})
            else:
                collabs = DocumentCollaborator.objects.filter(document=document).select_related('user')
                result = []
                for c in collabs:
                    user = getattr(c, 'user', None)
                    profile_image = None
                    employee_obj = None
                    try:
                        if user:
                            employee_obj = Employees.objects.filter(hrmsuser=user, is_active=True).first()
                            if employee_obj and getattr(employee_obj, 'profile_image', None):
                                profile_image = employee_obj.profile_image.url
                    except Exception:
                        profile_image = None

                    first_name = getattr(employee_obj, 'first_name', None) if employee_obj else (getattr(user, 'first_name', None) if user else None)
                    last_name = getattr(employee_obj, 'last_name', None) if employee_obj else (getattr(user, 'last_name', None) if user else None)
                    full_name = ' '.join([n for n in [first_name, last_name] if n]) if (first_name or last_name) else None

                    result.append({
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
                # for regular uploaded Documents, include can_manage flag too (document creator OR collaborator with owner role)
                can_manage = (document.created_by_id == user_id) or DocumentCollaborator.objects.filter(document=document, user_id=user_id, role='owner').exists()
                return Response({'status': 200, 'data': {'collaborators': result, 'can_manage': can_manage, 'document': DocumentsSerializer(document).data}})
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        try:
            # Allow creation via user id (internal) but validate ownership and organization
            organization_id, user_id = self._get_org_user(request)
            data = request.data.copy()

            document_id = data.get('document')
            user_id_field = data.get('user')
            if not document_id or not user_id_field:
                return Response({'status': 400, 'message': 'document and user are required'}, status=status.HTTP_400_BAD_REQUEST)

            # validate document belongs to org - support both rich and regular Documents
            document = None
            is_rich = False
            try:
                document = RichDocuments.objects.get(id=document_id, organization_id=organization_id)
                is_rich = True
            except RichDocuments.DoesNotExist:
                try:
                    document = Documents.objects.get(id=document_id, organization_id=organization_id)
                    is_rich = False
                except Documents.DoesNotExist:
                    return Response({'status': 404, 'message': 'Document not found in your organization'}, status=status.HTTP_404_NOT_FOUND)

            # validate user exists. The frontend may send either a HrmsUsers id, an Employees id,
            # or an object containing an id/email. Normalize and resolve accordingly.
            from profiles_api.models import HrmsUsers
            from employees.models import Employees

            def _normalize_identifier(val):
                # Return an int if the value is numeric, otherwise return a non-empty string id (eg. uuid)
                if val is None:
                    return None
                if isinstance(val, dict):
                    for k in ('id', 'user_id', 'employee_id', 'pk'):
                        if k in val and val[k] is not None:
                            return _normalize_identifier(val[k])
                    return None
                if isinstance(val, (list, tuple)) and val:
                    return _normalize_identifier(val[0])
                if isinstance(val, int):
                    return val
                if isinstance(val, str):
                    s = val.strip()
                    if not s:
                        return None
                    if s.isdigit():
                        try:
                            return int(s)
                        except Exception:
                            return s
                    # non-numeric string (possibly uuid) - return as-is
                    return s
                # fallback: try converting to int, otherwise string repr
                try:
                    return int(val)
                except Exception:
                    try:
                        return str(val)
                    except Exception:
                        return None

            normalized_id = _normalize_identifier(user_id_field)
            user_obj = None
            emp = None

            # Prefer resolving an Employees record first (frontend commonly sends Employees.id)
            if normalized_id is not None:
                # try employee by numeric id or uuid
                try:
                    emp = Employees.objects.filter(Q(id=normalized_id) | Q(uuid=normalized_id)).first()
                except Exception:
                    emp = Employees.objects.filter(id=normalized_id).first()

                if emp and getattr(emp, 'hrmsuser', None):
                    user_obj = emp.hrmsuser
                else:
                    # fall back to HrmsUsers lookup (numeric or string id)
                    try:
                        user_obj = HrmsUsers.objects.filter(id=normalized_id).first()
                    except Exception:
                        user_obj = None

            # If payload was an object without numeric id, try email match
            if not user_obj and isinstance(user_id_field, dict):
                email = user_id_field.get('email')
                if email:
                    user_obj = HrmsUsers.objects.filter(email__iexact=email).first()

            if not user_obj:
                return Response({'status': 404, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            # Prevent adding yourself as collaborator
            if user_obj.id == user_id:
                return Response({
                    'status': 400,
                    'message': 'You cannot add yourself as a collaborator'
                }, status=status.HTTP_400_BAD_REQUEST)


            # Ensure we have the Employees record for the organization
            try:
                if not emp:
                    emp = Employees.objects.filter(hrmsuser=user_obj, organization_id=organization_id).first()
                else:
                    # emp resolved earlier, make sure it belongs to the same organization
                    if emp.organization_id != organization_id:
                        emp = None
            except Exception:
                emp = None

            if not emp:
                return Response({'status': 400, 'message': 'User is not part of this organization'}, status=status.HTTP_400_BAD_REQUEST)

            # Allow creation by the document creator OR a collaborator who has role 'owner'
            is_actor_owner = (document.created_by_id == user_id)
            if not is_actor_owner:
                try:
                    if is_rich:
                        is_actor_owner = RichDocumentCollaborator.objects.filter(document=document, user_id=user_id, role='owner').exists()
                    else:
                        is_actor_owner = DocumentCollaborator.objects.filter(document=document, user_id=user_id, role='owner').exists()
                except Exception:
                    is_actor_owner = False

            if not is_actor_owner:
                return Response({'status': 403, 'message': 'Only the document owner or collaborators with owner role can add collaborators'}, status=status.HTTP_403_FORBIDDEN)

            # prevent duplicate
            if is_rich:
                exists = RichDocumentCollaborator.objects.filter(document_id=document_id, user_id=user_obj.id).exists()
            else:
                exists = DocumentCollaborator.objects.filter(document_id=document_id, user_id=user_obj.id).exists()
            if exists:
                return Response({'status': 400, 'message': 'User is already a collaborator'}, status=status.HTTP_400_BAD_REQUEST)

            # validate role (use the correct model's ROLE_CHOICES)
            role = data.get('role', 'viewer')
            
            # Check if this is an uploaded document and prevent editor role
            if not is_rich and role == 'editor':
                return Response({
                    'status': 400, 
                    'message': 'Editor role is not available for uploaded documents'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            valid_roles = dict(RichDocumentCollaborator.ROLE_CHOICES) if is_rich else dict(DocumentCollaborator.ROLE_CHOICES)
            if role not in valid_roles:
                return Response({'status': 400, 'message': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)

            if is_rich:
                collab = RichDocumentCollaborator.objects.create(document_id=document_id, user_id=user_obj.id, role=role)
                
                
                
                try:
                    send_collaboration_notification(
                        user_id=user_obj.id,
                        document_id=document_id,  # Pass document ID
                        document_title=document.title,
                        action_type='added',
                        role=role
                    )
                except Exception as e:
                    print(f"Failed to send collaboration notification: {str(e)}")
                
                
                # LOG ACTIVITY FOR COLLABORATOR ADDED
                RichDocumentActivity.objects.create(
                    document=document,
                    user_id=user_id,
                    activity_type='shared',
                    description=f'Added {user_obj.first_name} {user_obj.last_name} as {role}',
                    metadata={
                        'added_user_id': user_obj.id,
                        'added_user_name': f"{user_obj.first_name} {user_obj.last_name}",
                        'role': role
                    }
                )
            else:
                collab = DocumentCollaborator.objects.create(document_id=document_id, user_id=user_obj.id, role=role)
            
            # send notification to collaborator (best-effort)
            try:
                import importlib
                notif_mod = importlib.import_module('notification_engine.views')
                send_notification = getattr(notif_mod, 'send_notification', None)
                if send_notification:
                    send_notification(
                        user_id=user_obj.id,
                        title="You've been added as collaborator",
                        message=f"You've been added as {role} to document: {document.title}",
                        notification_type="collaboration"
                    )
            except Exception:
                pass
            
            # prepare collaborator payload for response
            if is_rich:
                serializer = RichDocumentCollaboratorSerializer(collab)
                collab_payload = serializer.data
            else:
                user = getattr(collab, 'user', None)
                employee_obj = None
                profile_image = None
                try:
                    if user:
                        employee_obj = Employees.objects.filter(hrmsuser=user, is_active=True).first()
                        if employee_obj and getattr(employee_obj, 'profile_image', None):
                            profile_image = employee_obj.profile_image.url
                except Exception:
                    profile_image = None
                collab_payload = {
                    'id': collab.id,
                    'document': collab.document_id,
                    'user': user.id if user else None,
                    'role': collab.role,
                    'first_name': getattr(employee_obj, 'first_name', None) or (getattr(user, 'first_name', None) if user else None),
                    'last_name': getattr(employee_obj, 'last_name', None) or (getattr(user, 'last_name', None) if user else None),
                    'name': (getattr(employee_obj, 'first_name', '') + ' ' + getattr(employee_obj, 'last_name', '')).strip() or (getattr(user, 'first_name', '') + ' ' + getattr(user, 'last_name', '')).strip(),
                    'email': getattr(user, 'email', None) if user else None,
                    'profile_image': profile_image,
                    'created_at': collab.created_at
                }

            # return updated document payload so frontend can refresh counts
            try:
                if is_rich:
                    doc_serializer = RichDocumentsSerializer(document)
                    return Response({'status': 201, 'collaborator': collab_payload, 'document': doc_serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    # minimal document payload for uploaded Documents
                    doc_payload = {
                        'id': document.id,
                        'title': document.title,
                        'collaborators_count': DocumentCollaborator.objects.filter(document=document).count(),
                        'comments_count': DocumentComment.objects.filter(document=document).count()
                    }
                    return Response({'status': 201, 'collaborator': collab_payload, 'document': doc_payload}, status=status.HTTP_201_CREATED)
            except Exception:
                return Response({'status': 201, 'collaborator': collab_payload}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk=None):
        """Update collaborator role (owner only)"""
        try:
            organization_id, user_id = self._get_org_user(request)
            collab = RichDocumentCollaborator.objects.filter(id=pk).first()
            collab_model = 'rich'
            if not collab:
                collab = DocumentCollaborator.objects.filter(id=pk).first()
                collab_model = 'document'

            if not collab:
                return Response({'status': 404, 'message': f'Collaborator not found for id {pk}'}, status=status.HTTP_404_NOT_FOUND)

            document = getattr(collab, 'document', None)
            if not document:
                return Response({'status': 400, 'message': 'Collaborator has no associated document'}, status=status.HTTP_400_BAD_REQUEST)

            # confirm document belongs to user's organization
            doc_org_id = getattr(document, 'organization_id', None)
            if doc_org_id != organization_id:
                return Response({'status': 403, 'message': 'You do not have permission to modify collaborators for this document'}, status=status.HTTP_403_FORBIDDEN)

            # Allow role changes by the document creator OR a collaborator with owner role
            is_actor_owner = (getattr(document, 'created_by_id', None) == user_id)
            if not is_actor_owner:
                try:
                    is_actor_owner = RichDocumentCollaborator.objects.filter(document=document, user_id=user_id, role='owner').exists()
                except Exception:
                    try:
                        is_actor_owner = DocumentCollaborator.objects.filter(document=document, user_id=user_id, role='owner').exists()
                    except Exception:
                        is_actor_owner = False

            if not is_actor_owner:
                return Response({'status': 403, 'message': 'Only the document owner or collaborators with owner role can modify collaborator roles'}, status=status.HTTP_403_FORBIDDEN)

            role = request.data.get('role')
            if not role:
                return Response({'status': 400, 'message': 'role is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if this is an uploaded document and prevent editor role
            if collab_model == 'document' and role == 'editor':
                return Response({
                    'status': 400, 
                    'message': 'Editor role is not available for uploaded documents'
                }, status=status.HTTP_400_BAD_REQUEST)

            # validate role against model choices
            valid_roles = dict(RichDocumentCollaborator.ROLE_CHOICES) if collab_model == 'rich' else dict(DocumentCollaborator.ROLE_CHOICES)
            if role not in valid_roles:
                return Response({'status': 400, 'message': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)

            old_role = collab.role
            collab.role = role
            collab.save()

            # Log role change activity for rich documents
            if collab_model == 'rich':
                RichDocumentActivity.objects.create(
                    document=document,
                    user_id=user_id,
                    activity_type='updated',
                    description=f'Changed {collab.user.first_name} {collab.user.last_name}\'s role from {old_role} to {role}',
                    metadata={
                        'collaborator_id': collab.id,
                        'collaborator_name': f"{collab.user.first_name} {collab.user.last_name}",
                        'old_role': old_role,
                        'new_role': role
                    }
                )

            if collab_model == 'rich':
                serializer = RichDocumentCollaboratorSerializer(collab)
                return Response({'status': 200, 'data': serializer.data})
            else:
                return Response({'status': 200, 'data': {'id': collab.id, 'role': collab.role}})
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        try:
            organization_id, user_id = self._get_org_user(request)

            # Find collaborator in either rich or regular collaborator tables
            collab = RichDocumentCollaborator.objects.filter(id=pk).first()
            collab_model = 'rich'
            if not collab:
                collab = DocumentCollaborator.objects.filter(id=pk).first()
                collab_model = 'document'

            if not collab:
                return Response(
                    {'status': 404, 'message': f'Collaborator not found for id {pk}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            document = getattr(collab, 'document', None)
            if not document:
                return Response(
                    {'status': 400, 'message': 'Collaborator has no associated document'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get document ID from the document object
            document_id = getattr(document, 'id', None)  # ADD THIS LINE
            if not document_id:
                print(f"[DEBUG] Could not get document ID from document object")
            
            # print(f"[DEBUG] Document ID: {document_id}")  # ADD FOR DEBUG

            # Confirm document belongs to user's organization
            doc_org_id = getattr(document, 'organization_id', None)
            if doc_org_id != organization_id:
                return Response(
                    {'status': 403, 'message': 'You do not have permission to remove collaborators from this document'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Allow removal by document creator OR collaborator with owner role
            is_actor_owner = (getattr(document, 'created_by_id', None) == user_id)
            if not is_actor_owner:
                is_actor_owner = (
                    RichDocumentCollaborator.objects.filter(
                        document=document, user_id=user_id, role='owner'
                    ).exists()
                    or
                    DocumentCollaborator.objects.filter(
                        document=document, user_id=user_id, role='owner'
                    ).exists()
                )

            if not is_actor_owner:
                return Response(
                    {'status': 403, 'message': 'Only the document owner or collaborators with owner role can remove collaborators'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # -----------------------------
            # NEW: Email notification + activity log (rich documents only)
            # -----------------------------
            if collab_model == 'rich':
                # Send email notification BEFORE deletion
                try:
                    # print(f"[DEBUG] Sending removal notification to user_id={collab.user.id}")
                    result = send_collaboration_notification(
                        user_id=collab.user.id,
                        document_id=document_id,  # Now this is defined
                        document_title=document.title,
                        action_type='removed'
                    )
                    # print(f"[DEBUG] Removal notification result: {result}")
                except Exception as e:
                    # Do not fail API if email fails
                    # print(f"[ERROR] Failed to send removal notification: {str(e)}")
                    import traceback
                    traceback.print_exc()

                # Log removal activity
                RichDocumentActivity.objects.create(
                    document=document,
                    user_id=user_id,
                    activity_type='updated',
                    description=f'Removed {collab.user.first_name} {collab.user.last_name} as collaborator',
                    metadata={
                        'removed_user_id': collab.user.id,
                        'removed_user_name': f"{collab.user.first_name} {collab.user.last_name}",
                        'role': collab.role
                    }
                )

            # Delete collaborator
            collab.delete()

            # Return updated document payload
            try:
                if collab_model == 'rich':
                    doc_serializer = RichDocumentsSerializer(document)
                    return Response(
                        {'status': 200, 'message': 'Removed', 'document': doc_serializer.data}
                    )
                else:
                    doc_payload = {
                        'id': document.id,
                        'title': document.title,
                        'collaborators_count': DocumentCollaborator.objects.filter(document=document).count(),
                        'comments_count': DocumentComment.objects.filter(document=document).count()
                    }
                    return Response(
                        {'status': 200, 'message': 'Removed', 'document': doc_payload}
                    )
            except Exception:
                return Response({'status': 200, 'message': 'Removed'})

        except Exception as e:
            print(f"[ERROR] Destroy method error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'status': 500, 'message': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(methods=['post'], detail=False, url_path='invite')
    def invite(self, request):
        try:
            organization_id, actor_user_id = self._get_org_user(request)

            email = request.data.get('email')
            user_id_field = request.data.get('user')
            document_id = request.data.get('document')
            role = request.data.get('role', 'viewer')

            if not email and not user_id_field:
                return Response({'status': 400, 'message': 'email or user is required'}, status=status.HTTP_400_BAD_REQUEST)
            if not document_id:
                return Response({'status': 400, 'message': 'document is required'}, status=status.HTTP_400_BAD_REQUEST)

            # validate document
            try:
                document = RichDocuments.objects.get(id=document_id, organization_id=organization_id)
            except RichDocuments.DoesNotExist:
                return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

            # resolve user by id/object or email robustly (same logic as create)
            from profiles_api.models import HrmsUsers
            from employees.models import Employees

            def _normalize_identifier(val):
                if val is None:
                    return None
                if isinstance(val, dict):
                    for k in ('id', 'user_id', 'employee_id', 'pk'):
                        if k in val and val[k] is not None:
                            return _normalize_identifier(val[k])
                    return None
                if isinstance(val, (list, tuple)) and val:
                    return _normalize_identifier(val[0])
                if isinstance(val, int):
                    return val
                if isinstance(val, str):
                    s = val.strip()
                    if not s:
                        return None
                    if s.isdigit():
                        try:
                            return int(s)
                        except Exception:
                            return s
                    return s
                try:
                    return int(val)
                except Exception:
                    try:
                        return str(val)
                    except Exception:
                        return None

            normalized_id = _normalize_identifier(user_id_field)
            user = None
            emp = None

            if normalized_id is not None:
                # prefer Employees lookup first (frontend typically sends Employees.id)
                try:
                    emp = Employees.objects.filter(Q(id=normalized_id) | Q(uuid=normalized_id)).first()
                except Exception:
                    emp = Employees.objects.filter(id=normalized_id).first()

                if emp and getattr(emp, 'hrmsuser', None):
                    user = emp.hrmsuser
                else:
                    try:
                        user = HrmsUsers.objects.filter(id=normalized_id).first()
                    except Exception:
                        user = None

            if not user and isinstance(user_id_field, dict):
                email = user_id_field.get('email')
                if email:
                    user = HrmsUsers.objects.filter(email__iexact=email).first()

            if not user:
                return Response({'status': 404, 'message': 'No user with that email or id'}, status=status.HTTP_404_NOT_FOUND)

            # ensure employee belongs to same organization (document.organization)
            emp = Employees.objects.filter(hrmsuser=user, organization=document.organization).first()
            if not emp:
                return Response({'status': 400, 'message': 'User is not part of this organization'}, status=status.HTTP_400_BAD_REQUEST)

            # validate role
            if role not in dict(RichDocumentCollaborator.ROLE_CHOICES):
                return Response({'status': 400, 'message': 'Invalid role'}, status=status.HTTP_400_BAD_REQUEST)

            # prevent duplicate
            if RichDocumentCollaborator.objects.filter(document=document, user=user).exists():
                return Response({'status': 400, 'message': 'User already a collaborator'}, status=status.HTTP_400_BAD_REQUEST)

            collab = RichDocumentCollaborator.objects.create(document=document, user=user, role=role)

            # log activity
            RichDocumentActivity.objects.create(
                document=document,
                user_id=actor_user_id,
                activity_type='shared',
                description=f'Invited {user.email} as {role}',
                metadata={'invited_user': user.id, 'role': role}
            )

            serializer = RichDocumentCollaboratorSerializer(collab)
            # best-effort notification
            try:
                import importlib
                notif_mod = importlib.import_module('notification_engine.views')
                send_notification = getattr(notif_mod, 'send_notification', None)
                if send_notification:
                    send_notification(
                        user_id=user.id,
                        title="You've been invited as collaborator",
                        message=f"You've been invited as {role} to document: {document.title}",
                        notification_type="collaboration"
                    )
            except Exception:
                pass
            # return collaborator and updated document payload
            try:
                doc_serializer = RichDocumentsSerializer(document)
                return Response({'status': 201, 'collaborator': serializer.data, 'document': doc_serializer.data}, status=status.HTTP_201_CREATED)
            except Exception:
                return Response({'status': 201, 'collaborator': serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VersionsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, document_pk=None):
        versions = RichDocumentVersion.objects.filter(document_id=document_pk)
        serializer = RichDocumentVersionSerializer(versions, many=True)
        return Response({'status': 200, 'data': serializer.data})

    def retrieve(self, request, pk=None, document_pk=None):
        version = RichDocumentVersion.objects.filter(id=pk, document_id=document_pk).first()
        if not version:
            return Response({'status': 404, 'message': 'Version not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RichDocumentVersionSerializer(version)
        return Response({'status': 200, 'data': serializer.data})


class CommentsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        document_id = request.query_params.get('document')
        if not document_id:
            return Response({'status': 200, 'data': []})

        # try rich document comments first, then fallback to uploaded Documents comments
        try:
            if RichDocuments.objects.filter(id=document_id).exists():
                qs = RichDocumentComment.objects.filter(document_id=document_id)
                serializer = RichDocumentCommentSerializer(qs, many=True)
                return Response({'status': 200, 'data': serializer.data})
        except Exception:
            pass

        # fallback to DocumentComment
        qs = DocumentComment.objects.filter(document_id=document_id)
        # build response shape similar to RichDocumentCommentSerializer
        result = []
        for c in qs:
            result.append({
                'id': c.id,
                'document': c.document_id,
                'author': c.author_id,
                'author_name': f"{getattr(c.author, 'first_name', '')} {getattr(c.author, 'last_name', '')}".strip(),
                'content': c.content,
                'created_at': c.created_at
            })
        return Response({'status': 200, 'data': result})

    def create(self, request):
        org_id, user_id = decodeToken(self, request)['organization_id'], request.user.id
        data = request.data.copy()
        data['author'] = user_id
        document_id = data.get('document')
        if not document_id:
            return Response({'status': 400, 'message': 'document is required'}, status=status.HTTP_400_BAD_REQUEST)

        # If rich document exists, use RichDocumentCommentSerializer, otherwise use DocumentComment
        try:
            rd = RichDocuments.objects.filter(id=document_id).first()
            if rd:
                # permission: owner or collaborator or public (project-members handled in serializer/view logic)
                try:
                    # owner
                    if rd.created_by_id != user_id:
                        collab_ok = RichDocumentCollaborator.objects.filter(document=rd, user_id=user_id).exists()
                        if not collab_ok:
                            # if public and project-scoped, allow project members
                            if rd.is_public and rd.project_id:
                                from employees.models import EmployeeProjects
                                member_ok = EmployeeProjects.objects.filter(project_id=rd.project_id, employee__hrmsuser_id=user_id, employee__organization_id=rd.organization_id, is_active=True).exists()
                                if not member_ok:
                                    return Response({'status': 403, 'message': 'You do not have permission to comment on this document'}, status=status.HTTP_403_FORBIDDEN)
                            else:
                                return Response({'status': 403, 'message': 'You do not have permission to comment on this document'}, status=status.HTTP_403_FORBIDDEN)

                    # allow comments only if document allows comments
                    if not getattr(rd, 'allow_comments', True):
                        return Response({'status': 403, 'message': 'Comments are disabled for this document'}, status=status.HTTP_403_FORBIDDEN)

                    serializer = RichDocumentCommentSerializer(data=data)
                    if serializer.is_valid():
                        comment_obj = serializer.save()
                        
                        
                        # print(f"[DEBUG] Comment created. Checking if notification needed...")
                        # print(f"[DEBUG] Document owner ID: {rd.created_by_id}, Commenter ID: {user_id}")
                        
                        # Send email notification to document owner (if not the commenter)
                        if rd.created_by_id != user_id:
                            # print(f"[DEBUG] Sending comment notification (different users)...")
                            try:
                                result = send_comment_notification(
                                    document_owner_id=rd.created_by_id,
                                    commenter_id=user_id,
                                    document_id=document_id,  # Pass document ID
                                    document_title=rd.title,
                                    comment_preview=comment_obj.content
                                )
                                # print(f"[DEBUG] Comment notification result: {result}")
                            except Exception as e:
                                print(f"[ERROR] Failed to send comment notification: {str(e)}")
                                import traceback
                                traceback.print_exc()
                        else:
                            print(f"[DEBUG] Skipping notification (commenter is document owner)")
                        # Log comment activity
                        RichDocumentActivity.objects.create(
                            document=rd,
                            user_id=user_id,
                            activity_type='commented',
                            description=f'Added a comment',
                            metadata={
                                'comment_id': comment_obj.id,
                                'comment_preview': comment_obj.content[:100] + ('...' if len(comment_obj.content) > 100 else '')
                            }
                        )
                        
                        return Response({'status': 200, 'data': serializer.data})
                    return Response({'status': 400, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception:
            pass

        # fallback: create DocumentComment
        try:
            # ensure document exists and belongs to organization
            doc = Documents.objects.filter(id=document_id, organization_id=org_id).first()
            if not doc:
                return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
            # permission check for uploaded documents: owner or collaborator or project member (if project-scoped public)
            try:
                if doc.created_by_id != user_id:
                    collab_ok = DocumentCollaborator.objects.filter(document=doc, user_id=user_id).exists() if DocumentCollaborator is not None else False
                    if not collab_ok:
                        if doc.is_public and doc.project_id:
                            from employees.models import EmployeeProjects
                            member_ok = EmployeeProjects.objects.filter(project_id=doc.project_id, employee__hrmsuser_id=user_id, employee__organization_id=doc.organization_id, is_active=True).exists()
                            if not member_ok:
                                return Response({'status': 403, 'message': 'You do not have permission to comment on this document'}, status=status.HTTP_403_FORBIDDEN)
                        else:
                            return Response({'status': 403, 'message': 'You do not have permission to comment on this document'}, status=status.HTTP_403_FORBIDDEN)
            except Exception:
                return Response({'status': 500, 'message': 'Permission check failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            comment = DocumentComment.objects.create(document_id=document_id, author_id=user_id, content=data.get('content', ''))
            return Response({'status': 200, 'data': {
                'id': comment.id,
                'document': comment.document_id,
                'author': comment.author_id,
                'author_name': f"{getattr(comment.author, 'first_name', '')} {getattr(comment.author, 'last_name', '')}".strip(),
                'content': comment.content,
                'created_at': comment.created_at
            }})
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        obj = RichDocumentComment.objects.filter(id=pk).first()
        model_used = 'rich'
        if not obj:
            obj = DocumentComment.objects.filter(id=pk).first()
            model_used = 'document'
        if not obj:
            return Response({'status': 404, 'message': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Log comment deletion activity for rich documents
        if model_used == 'rich':
            RichDocumentActivity.objects.create(
                document=obj.document,
                user_id=request.user.id,
                activity_type='updated',
                description=f'Deleted a comment',
                metadata={
                    'comment_id': obj.id,
                    'comment_preview': obj.content[:100] + ('...' if len(obj.content) > 100 else '')
                }
            )
        
        obj.delete()
        return Response({'status': 200, 'message': 'Deleted', 'model': model_used})


class ChecklistViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        document_id = request.query_params.get('document')
        qs = RichDocumentChecklistItem.objects.filter(document_id=document_id)
        serializer = RichDocumentChecklistItemSerializer(qs, many=True)
        return Response({'status': 200, 'data': serializer.data})

    def create(self, request):
        serializer = RichDocumentChecklistItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 200, 'data': serializer.data})
        return Response({'status': 400, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        item = RichDocumentChecklistItem.objects.filter(id=pk).first()
        if not item:
            return Response({'status': 404, 'message': 'Checklist item not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RichDocumentChecklistItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 200, 'data': serializer.data})
        return Response({'status': 400, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        item = RichDocumentChecklistItem.objects.filter(id=pk).first()
        if not item:
            return Response({'status': 404, 'message': 'Checklist item not found'}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({'status': 200, 'message': 'Deleted'})


class MentionsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        document_id = request.query_params.get('document')
        qs = RichDocumentMention.objects.filter(document_id=document_id) if document_id else RichDocumentMention.objects.none()
        serializer = RichDocumentMentionSerializer(qs, many=True)
        return Response({'status': 200, 'data': serializer.data})

    def create(self, request):
        serializer = RichDocumentMentionSerializer(data=request.data)
        if serializer.is_valid():
            mention_obj = serializer.save()
            
            
            # Send email notification to mentioned user
            try:
                send_mention_notification(
                    mentioned_user_id=mention_obj.mentioned_user_id,
                    mentioned_by_id=mention_obj.mentioned_by_id,
                    document_title=mention_obj.document.title if mention_obj.document else "Document",
                    document_id=mention_obj.document_id
                )
            except Exception as e:
                print(f"Failed to send mention notification: {str(e)}")
            
            
            return Response({'status': 200, 'data': serializer.data})
        return Response({'status': 400, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class SharesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        document_id = request.query_params.get('document')
        qs = RichDocumentShare.objects.filter(document_id=document_id) if document_id else RichDocumentShare.objects.none()
        serializer = RichDocumentShareSerializer(qs, many=True)
        return Response({'status': 200, 'data': serializer.data})

    def create(self, request):
        serializer = RichDocumentShareSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 200, 'data': serializer.data})
        return Response({'status': 400, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        share = RichDocumentShare.objects.filter(id=pk).first()
        if not share:
            return Response({'status': 404, 'message': 'Share not found'}, status=status.HTTP_404_NOT_FOUND)
        share.delete()
        return Response({'status': 200, 'message': 'Share removed'})


class ActivitiesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        document_id = request.query_params.get('document')
        if not document_id:
            return Response({'status': 400, 'message': 'document parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get all activities for the document
            qs = RichDocumentActivity.objects.filter(document_id=document_id).select_related('user').order_by('-created_at')
            serializer = RichDocumentActivitySerializer(qs, many=True)
            data = serializer.data or []

            # If no activities exist, create a default "created" activity from document metadata
            if not data:
                try:
                    document = RichDocuments.objects.filter(id=document_id).select_related('created_by').first()
                    if document:
                        # Create a synthetic creation activity
                        created_activity = {
                            'id': f"created-{document.id}",
                            'document': document_id,
                            'user': document.created_by_id,
                            'activity_type': 'created',
                            'description': f'Document created by {document.created_by.first_name} {document.created_by.last_name}',
                            'metadata': {},
                            'user_name': f"{document.created_by.first_name} {document.created_by.last_name}".strip(),
                            'created_at': document.created_at
                        }
                        data.append(created_activity)
                except Exception as e:
                    print(f"Error creating default activity: {e}")

            # Add editing session information as activities
            try:
                editing_sessions = RichDocumentEditingSession.objects.filter(
                    document_id=document_id
                ).select_related('user').order_by('-last_activity')
                
                for session in editing_sessions:
                    # Check if we already have an activity for this editing session
                    existing_edit = next((item for item in data if item.get('metadata', {}).get('session_id') == session.id), None)
                    
                    if not existing_edit:
                        edit_activity = {
                            'id': f"edit-session-{session.id}",
                            'document': int(document_id),
                            'user': session.user_id,
                            'activity_type': 'updated',
                            'description': f'Document edited by {session.user.first_name} {session.user.last_name}',
                            'metadata': {
                                'session_id': session.id,
                                'last_activity': session.last_activity.isoformat(),
                                'session_start': session.session_start.isoformat()
                            },
                            'user_name': f"{session.user.first_name} {session.user.last_name}".strip(),
                            'created_at': session.last_activity
                        }
                        data.append(edit_activity)
            except Exception as e:
                print(f"Error processing editing sessions: {e}")

            # Sort all activities by creation date (newest first)
            data.sort(key=lambda x: x['created_at'], reverse=True)

            return Response({'status': 200, 'data': data})
            
        except Exception as e:
            return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorkspacesViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        organization_id, user_id = self._get_org_user(request)
        workspaces = RichDocumentWorkspace.objects.filter(organization=organization_id, is_active=True)
        serializer = RichDocumentWorkspaceSerializer(workspaces, many=True)
        return Response({'status': 200, 'data': serializer.data})

    def create(self, request):
        organization_id, user_id = self._get_org_user(request)
        data = request.data.copy()
        data['organization'] = organization_id
        data['created_by'] = user_id
        
        serializer = RichDocumentWorkspaceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 200, 'data': serializer.data})
        return Response({'status': 400, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        organization_id, user_id = self._get_org_user(request)
        try:
            workspace = RichDocumentWorkspace.objects.get(id=pk, organization=organization_id)
        except RichDocumentWorkspace.DoesNotExist:
            return Response({'status': 404, 'message': 'Workspace not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RichDocumentWorkspaceSerializer(workspace)
        return Response({'status': 200, 'data': serializer.data})

    def _get_org_user(self, request):
        token = decodeToken(self, request)
        return token['organization_id'], request.user.id


class DocumentsEnhancedViewset(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        organization_id, user_id = self._get_org_user(request)
        try:
            doc = Documents.objects.get(id=pk, organization_id=organization_id)
        except Documents.DoesNotExist:
            return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentsSerializer(doc)
        # augment with counts
        try:
            collabs = DocumentCollaborator.objects.filter(document=doc).count() if DocumentCollaborator is not None else 0
            comms = DocumentComment.objects.filter(document=doc).count() if DocumentComment is not None else 0
        except Exception:
            collabs = 0
            comms = 0
        data = serializer.data
        data['collaborators_count'] = collabs
        data['comments_count'] = comms
        data['_type'] = 'document'
        return Response({'status': 200, 'data': data})

    def view(self, request, pk=None):
        # provide a simple HTML view for uploaded files similar to rich document view
        try:
            doc = Documents.objects.filter(id=pk).first()
            # use same robust detection used by RichDocumentsViewset
            wants_json = False
            try:
                wants_json = RichDocumentsViewset()._wants_json(request)
            except Exception:
                wants_json = ('application/json' in request.META.get('HTTP_ACCEPT', '')) or (request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest')
            if not doc:
                if wants_json:
                    return Response({'status': 404, 'message': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
                return HttpResponse('<h3>Document not found</h3>', status=404)

            # Basic visibility check (public or org match)
            if not doc.is_public:
                if not request.user or not request.user.is_authenticated:
                    if wants_json:
                        return Response({'status': 401, 'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
                    return HttpResponse('<h3>Authentication required</h3>', status=401)
                token = decodeToken(self, request)
                if token['organization_id'] != doc.organization_id:
                    if wants_json:
                        return Response({'status': 403, 'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
                    return HttpResponse('<h3>Forbidden</h3>', status=403)

            # If doc is public but project scoped, ensure user is project member or collaborator
            if doc.is_public and doc.project_id:
                if not request.user or not request.user.is_authenticated:
                    if wants_json:
                        return Response({'status': 401, 'message': 'Authentication required for project document'}, status=status.HTTP_401_UNAUTHORIZED)
                    return HttpResponse('<h3>Authentication required</h3>', status=401)
                token = decodeToken(self, request)
                org_id, user_id = token['organization_id'], request.user.id
                if doc.organization_id != org_id:
                    if wants_json:
                        return Response({'status': 403, 'message': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
                    return HttpResponse('<h3>Forbidden</h3>', status=403)
                from employees.models import EmployeeProjects
                member = EmployeeProjects.objects.filter(project_id=doc.project_id, employee__hrmsuser_id=user_id, employee__organization_id=org_id, is_active=True).exists()
                collab = DocumentCollaborator.objects.filter(document=doc, user_id=user_id).exists() if DocumentCollaborator is not None else False
                if not (member or collab or doc.created_by_id == user_id):
                    if wants_json:
                        return Response({'status': 403, 'message': 'You do not have access to this project document'}, status=status.HTTP_403_FORBIDDEN)
                    return HttpResponse('<h3>Forbidden</h3>', status=403)

            content_html = f"<h2>{doc.title}</h2>" + (f"<p>{doc.description}</p>" if doc.description else '')
            if doc.file:
                # link to file
                content_html += f"<p><a href='{doc.file.url}'>Download file</a></p>"

            if wants_json:
                serializer = DocumentsSerializer(doc)
                data = serializer.data
                data['collaborators_count'] = DocumentCollaborator.objects.filter(document=doc).count() if DocumentCollaborator is not None else 0
                data['comments_count'] = DocumentComment.objects.filter(document=doc).count() if DocumentComment is not None else 0
                return Response({'status': 200, 'data': data})

            return HttpResponse(f"<html><body>{content_html}</body></html>")
        except Exception as e:
            wants_json = False
            try:
                wants_json = RichDocumentsViewset()._wants_json(request)
            except Exception:
                wants_json = ('application/json' in request.META.get('HTTP_ACCEPT', '')) or (request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest')
            if wants_json:
                return Response({'status': 500, 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return HttpResponse(f"<h3>Error rendering document</h3><pre>{str(e)}</pre>", status=500)