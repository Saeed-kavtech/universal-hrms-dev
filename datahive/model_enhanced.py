from django.db import models

from helpers.image_uploads import upload_datahive_files
from organizations.models import Organization
from profiles_api.models import HrmsUsers
from projects.models import Projects
from .models import Categories, Tags, Documents


class RichDocuments(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    is_template = models.BooleanField(default=False)
    word_count = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tags, blank=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Enhanced collaboration features
    allow_comments = models.BooleanField(default=True)
    allow_editing = models.BooleanField(default=True)
    allow_download = models.BooleanField(default=True)
    allow_sharing = models.BooleanField(default=True)
    workspace = models.CharField(max_length=100, blank=True, null=True)
    folder_path = models.CharField(max_length=500, blank=True, null=True)
    is_archived = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rich Document'
        verbose_name_plural = 'Rich Documents'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.organization.name})"


class RichDocumentVersion(models.Model):
    """Immutable snapshot of a rich document content for version history."""
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(RichDocuments, on_delete=models.CASCADE, related_name='versions')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    word_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']


class RichDocumentCollaborator(models.Model):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    )

    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(RichDocuments, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default='viewer')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('document', 'user')
        ordering = ['-created_at']


class RichDocumentComment(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(RichDocuments, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class RichDocumentChecklistItem(models.Model):
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(RichDocuments, on_delete=models.CASCADE, related_name='checklist_items')
    text = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)
    assignee = models.ForeignKey(HrmsUsers, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class RichDocumentMention(models.Model):
    """Track mentions of users in documents"""
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(RichDocuments, on_delete=models.CASCADE, related_name='mentions')
    mentioned_user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    mentioned_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, related_name='mentions_created')
    position = models.IntegerField()  # Character position in document
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class RichDocumentShare(models.Model):
    """Track document sharing with external users"""
    SHARE_TYPES = (
        ('link', 'Public Link'),
        ('email', 'Email Invite'),
        ('workspace', 'Workspace Share'),
    )
    
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(RichDocuments, on_delete=models.CASCADE, related_name='shares')
    share_type = models.CharField(max_length=20, choices=SHARE_TYPES, default='link')
    shared_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    shared_with_email = models.EmailField(blank=True, null=True)
    shared_with_user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE, blank=True, null=True, related_name='shared_documents')
    share_token = models.CharField(max_length=100, unique=True, blank=True, null=True)
    permissions = models.JSONField(default=dict)  # {'view': True, 'edit': False, 'comment': True}
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class RichDocumentActivity(models.Model):
    """Track all activities on documents"""
    ACTIVITY_TYPES = (
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('viewed', 'Viewed'),
        ('commented', 'Commented'),
        ('shared', 'Shared'),
        ('archived', 'Archived'),
        ('restored', 'Restored'),
        ('deleted', 'Deleted'),
    )
    
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(RichDocuments, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict)  # Additional data about the activity
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class RichDocumentWorkspace(models.Model):
    """Workspace management for documents"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    members = models.ManyToManyField(HrmsUsers, related_name='workspaces', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class RichDocumentEditingSession(models.Model):
    """Track who is currently editing a document"""
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(RichDocuments, on_delete=models.CASCADE, related_name='editing_sessions')
    user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    session_start = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        # unique_together should not include is_active boolean in modern Django; use index instead
        unique_together = ('document', 'user')
        ordering = ['-last_activity']

    def __str__(self):
        return f"EditingSession: {self.user.email} -> {self.document.title}"


class DocumentCollaborator(models.Model):
    """Collaborators for uploaded files (Documents model)"""
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    )

    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Documents, on_delete=models.CASCADE, related_name='collaborators')
    user = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default='viewer')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('document', 'user')
        ordering = ['-created_at']


class DocumentComment(models.Model):
    """Comments for uploaded files (Documents model)"""
    id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Documents, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(HrmsUsers, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
