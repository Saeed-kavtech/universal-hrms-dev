from rest_framework import serializers

from .model_enhanced import (
    RichDocuments,
    RichDocumentCollaborator,
    RichDocumentVersion,
    RichDocumentComment,
    RichDocumentChecklistItem,
    RichDocumentMention,
    RichDocumentShare,
    RichDocumentActivity,
    RichDocumentWorkspace
)
from .models import Tags
from employees.models import Employees


class TagSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ['id', 'name']


class RichDocumentsSerializer(serializers.ModelSerializer):
    tags = TagSimpleSerializer(many=True, read_only=True)
    collaborators = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    created_by_profile_image = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    collaborators_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    versions_count = serializers.SerializerMethodField()
    # permission flags for current request user
    can_view = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    can_manage_collaborators = serializers.SerializerMethodField()

    class Meta:
        model = RichDocuments
        fields = [
            'id', 'title', 'content', 'project', 'category', 'is_public', 'is_template', 
            'word_count', 'created_by', 'organization', 'tags', 'created_at', 'updated_at', 
            'created_by_profile_image', 'created_by_name', 'allow_comments', 'allow_editing', 
            'allow_download', 'allow_sharing', 'workspace', 'folder_path', 'is_archived', 
            'last_accessed', 'collaborators_count', 'comments_count', 'versions_count', 'collaborators', 'comments',
            # permission flags
            'can_view', 'can_edit', 'can_delete', 'can_manage_collaborators'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'organization', 'last_accessed']

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()

    def validate_content(self, value):
        if value is not None and len(value) > 1000000:  # 1MB limit
            raise serializers.ValidationError("Content is too large")
        return value

    def validate_project(self, value):
        if value and not value.is_active:
            raise serializers.ValidationError("Project is not active")
        return value

    def validate_category(self, value):
        if value and not value.is_active:
            raise serializers.ValidationError("Category is not active")
        return value

    def get_created_by_profile_image(self, obj):
        try:
            employee = Employees.objects.filter(hrmsuser=obj.created_by_id, is_active=True).first()
            if employee and employee.profile_image:
                return employee.profile_image.url
            return None
        except Exception:
            return None

    def get_created_by_name(self, obj):
        try:
            if obj.created_by:
                return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
            return None
        except Exception:
            return None

    def get_collaborators_count(self, obj):
        try:
            return obj.collaborators.count()
        except Exception:
            return 0

    def _current_user_id(self):
        req = self.context.get('request') if self.context else None
        try:
            return getattr(req.user, 'id', None)
        except Exception:
            return None

    def get_can_view(self, obj):
        # Owner or collaborator or public+member rules
        try:
            user_id = self._current_user_id()
            if obj.created_by_id == user_id:
                return True
            from .model_enhanced import RichDocumentCollaborator
            if RichDocumentCollaborator.objects.filter(document=obj, user_id=user_id).exists():
                return True
            if obj.is_public:
                # if not project-scoped, public link allows view
                if not obj.project_id:
                    return True
                # project-scoped -> user must be project member
                from employees.models import EmployeeProjects
                return EmployeeProjects.objects.filter(project_id=obj.project_id, employee__hrmsuser_id=user_id, employee__organization_id=obj.organization_id, is_active=True).exists()
            return False
        except Exception:
            return False

    def get_can_edit(self, obj):
        try:
            user_id = self._current_user_id()
            # only owner or collaborator with editor role
            if obj.created_by_id == user_id:
                return True
            from .model_enhanced import RichDocumentCollaborator
            collab = RichDocumentCollaborator.objects.filter(document=obj, user_id=user_id).first()
            return bool(collab and collab.role in ('editor', 'owner'))
        except Exception:
            return False

    def get_can_delete(self, obj):
        try:
            user_id = self._current_user_id()
            return obj.created_by_id == user_id
        except Exception:
            return False

    def get_can_manage_collaborators(self, obj):
        try:
            user_id = self._current_user_id()
            return obj.created_by_id == user_id
        except Exception:
            return False

    def get_comments_count(self, obj):
        try:
            return obj.comments.count()
        except Exception:
            return 0

    def get_versions_count(self, obj):
        try:
            return obj.versions.count()
        except Exception:
            return 0

    def get_collaborators(self, obj):
        try:
            collabs = obj.collaborators.select_related('user').all()
            result = []
            for c in collabs:
                user = getattr(c, 'user', None)
                # try to resolve profile image and employee id from Employees if available
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
            return result
        except Exception:
            return []

    def get_comments(self, obj):
        try:
            comms = obj.comments.select_related('author').all()
            result = []
            for c in comms:
                author = getattr(c, 'author', None)
                result.append({
                    'id': c.id,
                    'author': author.id if author else None,
                    'author_name': f"{getattr(author, 'first_name', '')} {getattr(author, 'last_name', '')}".strip() if author else None,
                    'content': c.content,
                    'created_at': c.created_at
                })
            return result
        except Exception:
            return []


class RichDocumentCollaboratorSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = RichDocumentCollaborator
        fields = ['id', 'document', 'user', 'role', 'first_name', 'last_name', 'name', 'email', 'profile_image', 'created_at']


    def get_name(self, obj):
        """Return a best-effort display name for the collaborator.

        Prefer employee record name when available, otherwise fall back to the HrmsUsers name.
        """
        try:
            user = getattr(obj, 'user', None)
            if not user:
                return None
            # prefer Employees record for display name
            try:
                emp = Employees.objects.filter(hrmsuser=user, is_active=True).first()
            except Exception:
                emp = None
            if emp:
                return f"{emp.first_name or ''} {emp.last_name or ''}".strip()
            return f"{getattr(user, 'first_name', '') or ''} {getattr(user, 'last_name', '') or ''}".strip() or None
        except Exception:
            return None

    def get_profile_image(self, obj):
        """Return profile image url from Employees record or HrmsUsers if available."""
        try:
            user = getattr(obj, 'user', None)
            if not user:
                return None
            try:
                emp = Employees.objects.filter(hrmsuser=user, is_active=True).first()
            except Exception:
                emp = None
            if emp and getattr(emp, 'profile_image', None):
                return emp.profile_image.url
            # fallback to user profile image if present
            if getattr(user, 'profile_image', None):
                return user.profile_image.url
            return None
        except Exception:
            return None


class RichDocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RichDocumentVersion
        fields = ['id', 'document', 'title', 'content', 'word_count', 'created_at', 'created_by']
        read_only_fields = ['id', 'created_at', 'created_by']


class RichDocumentCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = RichDocumentComment
        fields = ['id', 'document', 'author', 'author_name', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_name(self, obj):
        try:
            user = getattr(obj, 'user', None)
            if not user:
                return None
            return f"{user.first_name or ''} {user.last_name or ''}".strip()
        except Exception:
            return None

    def get_profile_image(self, obj):
        try:
            user = getattr(obj, 'user', None)
            if not user:
                return None
            emp = Employees.objects.filter(hrmsuser=user).first()
            if emp and getattr(emp, 'profile_image', None):
                return emp.profile_image.url
            return None
        except Exception:
            return None

    def get_author_name(self, obj):
        try:
            return f"{obj.author.first_name} {obj.author.last_name}".strip()
        except Exception:
            return None


class RichDocumentChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RichDocumentChecklistItem
        fields = ['id', 'document', 'text', 'is_completed', 'assignee', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RichDocumentMentionSerializer(serializers.ModelSerializer):
    mentioned_user_name = serializers.SerializerMethodField()
    mentioned_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RichDocumentMention
        fields = ['id', 'document', 'mentioned_user', 'mentioned_by', 'position', 'mentioned_user_name', 'mentioned_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_mentioned_user_name(self, obj):
        try:
            return f"{obj.mentioned_user.first_name} {obj.mentioned_user.last_name}".strip()
        except Exception:
            return None

    def get_mentioned_by_name(self, obj):
        try:
            return f"{obj.mentioned_by.first_name} {obj.mentioned_by.last_name}".strip()
        except Exception:
            return None


class RichDocumentShareSerializer(serializers.ModelSerializer):
    shared_by_name = serializers.SerializerMethodField()
    shared_with_name = serializers.SerializerMethodField()

    class Meta:
        model = RichDocumentShare
        fields = ['id', 'document', 'share_type', 'shared_by', 'shared_with_email', 'shared_with_user', 'share_token', 'permissions', 'expires_at', 'is_active', 'shared_by_name', 'shared_with_name', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_shared_by_name(self, obj):
        try:
            return f"{obj.shared_by.first_name} {obj.shared_by.last_name}".strip()
        except Exception:
            return None

    def get_shared_with_name(self, obj):
        try:
            if obj.shared_with_user:
                return f"{obj.shared_with_user.first_name} {obj.shared_with_user.last_name}".strip()
            return obj.shared_with_email
        except Exception:
            return None


class RichDocumentActivitySerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = RichDocumentActivity
        fields = ['id', 'document', 'user', 'activity_type', 'description', 'metadata', 'user_name', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_user_name(self, obj):
        try:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        except Exception:
            return None


class RichDocumentWorkspaceSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = RichDocumentWorkspace
        fields = ['id', 'name', 'description', 'organization', 'created_by', 'members', 'is_active', 'members_count', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_members_count(self, obj):
        try:
            return obj.members.count()
        except Exception:
            return 0

    def get_created_by_name(self, obj):
        try:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        except Exception:
            return None
