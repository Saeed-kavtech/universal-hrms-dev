from django.urls import path
from .views_enhanced import (
    RichDocumentsViewset,
    CollaboratorsViewSet,
    VersionsViewSet,
    CommentsViewSet,
    ChecklistViewSet,
    MentionsViewSet,
    SharesViewSet,
    ActivitiesViewSet,
    WorkspacesViewSet
    , DocumentsEnhancedViewset
)

urlpatterns = [
    path('rich-documents/', RichDocumentsViewset.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('rich-documents/<int:pk>/', RichDocumentsViewset.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
    path('rich-documents/<int:pk>/view/', RichDocumentsViewset.as_view({
        'get': 'view'
    })),
    path('rich-documents/create_rich_document/', RichDocumentsViewset.as_view({'post':'create_rich_document'})),
    path('rich-documents/<int:pk>/archive/', RichDocumentsViewset.as_view({'post':'archive'})),
    path('rich-documents/<int:pk>/restore/', RichDocumentsViewset.as_view({'post':'restore'})),
    path('rich-documents/<int:pk>/activities/', RichDocumentsViewset.as_view({'get':'activities'})),
    path('rich-documents/<int:pk>/share/', RichDocumentsViewset.as_view({'post':'share'})),
    # Collaboration
    path('collaborators/', CollaboratorsViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('collaborators/<int:pk>/', CollaboratorsViewSet.as_view({
        'delete': 'destroy',
        'patch': 'partial_update'
    })),
    path('collaborators/invite/', CollaboratorsViewSet.as_view({
        'post': 'invite'
    })),
    # Versions
    path('rich-documents/<int:document_pk>/versions/', VersionsViewSet.as_view({
        'get': 'list'
    })),
    path('rich-documents/<int:document_pk>/versions/<int:pk>/', VersionsViewSet.as_view({
        'get': 'retrieve'
    })),
    # Comments
    path('comments/', CommentsViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('comments/<int:pk>/', CommentsViewSet.as_view({
        'delete': 'destroy'
    })),
    # Checklist / tasks
    path('checklist/', ChecklistViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('checklist/<int:pk>/', ChecklistViewSet.as_view({
        'patch': 'partial_update',
        'delete': 'destroy'
    })),
    # Mentions
    path('mentions/', MentionsViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    # Shares
    path('shares/', SharesViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('shares/<int:pk>/', SharesViewSet.as_view({
        'delete': 'destroy'
    })),
    # Activities
    path('activities/', ActivitiesViewSet.as_view({
        'get': 'list'
    })),
    # Workspaces
    path('workspaces/', WorkspacesViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('workspaces/<int:pk>/', WorkspacesViewSet.as_view({
        'get': 'retrieve'
    })),
    # Uploaded documents detail + public view
    path('documents/<int:pk>/', DocumentsEnhancedViewset.as_view({
        'get': 'retrieve'
    })),
    path('documents/<int:pk>/view/', DocumentsEnhancedViewset.as_view({
        'get': 'view'
    })),
    # Add this to urlpatterns
path('rich-documents/upload_image/', RichDocumentsViewset.as_view({'post': 'upload_image'})),

path('rich-documents/<int:pk>/start_edit/', RichDocumentsViewset.as_view({'post': 'start_edit'})),
    path('rich-documents/<int:pk>/end_edit/', RichDocumentsViewset.as_view({'post': 'end_edit'})),
    path('rich-documents/<int:pk>/active_editors/', RichDocumentsViewset.as_view({'get': 'active_editors'})),
    path('rich-documents/<int:pk>/check_edit_lock/', RichDocumentsViewset.as_view({'get': 'check_edit_lock'})),

    path('rich-documents/<int:pk>/update_activity/', RichDocumentsViewset.as_view({'post': 'update_activity'})),
]
