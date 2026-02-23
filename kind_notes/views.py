from rest_framework import viewsets
from .serializers import KindNotesViewsetSerializers, kindNotesPreDataViewSerializers
from .models import KindNotes
from helpers.status_messages import errorMessage, success, exception, serializerError, successfullyCreated, successfullyUpdated, successMessage
from rest_framework import generics
from helpers.custom_permissions import IsAuthenticated, TokenDataPermissions
from employees.models import Employees
from django.db.models import Q

# Create your views here.
class KindNotesViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, TokenDataPermissions]
    serializer_class = KindNotesViewsetSerializers

    def list(self, request, *args, **kwargs):
        try:
            organization_id = request.data.get('current_organization')
            sender_id = request.user.id
            notes = KindNotes.objects.filter(sender__hrmsuser=sender_id, sender__organization=organization_id, is_active=True)
            serializer = KindNotesViewsetSerializers(notes, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)  

    def retrieve(self, request, *args, **kwargs):
        try:
            # sent or recieved notes
            organization_id = request.data.get('current_organization')
            note_id = self.kwargs['note_id']
            user_id = request.user.id

            notes = KindNotes.objects.filter(id=note_id, sender__organization=organization_id, is_active=True)
            if not notes.exists():
                return errorMessage('No notes exists at this id')
            elif not notes.filter(is_active=True).exists():
                return errorMessage('No active notes exists at this id')
            elif not notes.filter(Q(sender__hrmsuser=user_id) | Q(receiver__hrmsuser=user_id)).exists():
                return errorMessage("You can only view your own notes")

            obj = notes.get()
            serializer = KindNotesViewsetSerializers(obj, many=False)
            return success(serializer.data)
        except Exception as e:
            return exception(e)  
 
    def create(self, request, *args, **kwargs):
        try:
            organization_id = request.data.get('current_organization')

            hrmsuser_id = request.user.id
            emp = Employees.objects.filter(hrmsuser=hrmsuser_id)
            if not emp.exists():
                return errorMessage("user is not an employee")
            emp = emp.get()
            sender_id = emp.id
            request.data['sender'] = sender_id
            
            # receiver checks
            if 'receiver' in request.data:
                receiver_id = request.data['receiver']
                emp_query = Employees.objects.filter(id=receiver_id, organization=organization_id).exclude(id=sender_id)
                if not emp_query.exists():
                    return errorMessage('Receiver does not exists at this id')
                elif not emp_query.filter(is_active=True).exists():
                    return errorMessage('Receiver is deactivated')
            else:
                return errorMessage('Receiver is the required field')
            
            if sender_id == receiver_id:
                return errorMessage("You cannot sent kind notes to yourself")

            serializer = KindNotesViewsetSerializers(data = request.data)
            if not serializer.is_valid():
                if serializer.errors.get('notes'):
                    return errorMessage(serializer.errors.get('notes', [''])[0])
                else:
                    return serializerError(serializer.errors)
            serializer.save()
            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)
        
    def patch(self, request, *args, **kwargs):
        try:
            organization_id = request.data.get('current_organization')
            note_id = self.kwargs['note_id']
            
            hrmsuser_id = request.user.id
            emp = Employees.objects.filter(hrmsuser=hrmsuser_id)
            if not emp.exists():
                return errorMessage("user is not an employee")
            emp = emp.get()
            sender_id = emp.id
            request.data['sender'] = sender_id

            notes = KindNotes.objects.filter(id=note_id, sender__organization=organization_id)
            if not notes.exists():
                return errorMessage('No notes exists at this id')
            elif not notes.filter(sender=sender_id).exists():
                return errorMessage("You cannot edit someone's else notes")
            notes_obj = notes.first()
            
            # receiver checks
            receiver_id = notes_obj.receiver.id
            if 'receiver' in request.data:
                receiver_id = request.data['receiver']
                if sender_id == receiver_id:
                    return errorMessage("You cannot sent kind notes to yourself")
                
                emp_query = Employees.objects.filter(id=receiver_id, organization=organization_id)
                if not emp_query.exists():
                    return errorMessage('Receiver does not exists at this id')
                elif not emp_query.filter(is_active=True).exists():
                    return errorMessage('Receiver is deactivated')        
                
            serializer = KindNotesViewsetSerializers(notes_obj, data = request.data, partial=True)
            if not serializer.is_valid():
                return serializerError(serializer.errors)                
            serializer.save()
            return successfullyUpdated(serializer.data)
        except Exception as e:
            return exception(e) 
        
    def delete(self, request, *args, **kwargs):
        try:
            organization_id = request.data.get('current_organization')
            note_id = self.kwargs['note_id']
            user_id = request.user.id

            notes = KindNotes.objects.filter(id=note_id, sender__organization=organization_id)
            if not notes.exists():
                return errorMessage('No notes exists at this id')
            elif not notes.filter(Q(sender__hrmsuser=user_id) | Q(receiver__hrmsuser=user_id)).exists():
                return errorMessage("You cannot delete someone else kind notes")
            notes_obj = notes.get()

            if notes_obj.is_active==False:
                return successMessage('This kindnote is already deactivated')
            notes_obj.is_active=False
            notes_obj.save()
            return successMessage('Deleted Successfully')
        except Exception as e:
            return exception(e)

    def received_notes(self, request, *args, **kwargs):
        try: 
            organization_id = request.data.get('current_organization')
            
            notes = KindNotes.objects.filter(receiver__hrmsuser=request.user.id, receiver__organization=organization_id)
            if not notes.exists():
                return errorMessage('This employee has no kind notes')
            notes = notes.filter(is_active=True)
            if not notes.exists():
                return errorMessage('This employee has no active notes')

            serializer = KindNotesViewsetSerializers(notes, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)  

    def pre_data(self, request, *args, **kwargs):
        try: 
            organization_id = request.data.get('current_organization')
            obj = Employees.objects.filter(organization=organization_id, is_active=True)
            serializer = kindNotesPreDataViewSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e)  


class kindNotesUniversalViewset(viewsets.ModelViewSet):
    serializer_class = KindNotesViewsetSerializers

    def list(self, request, *args, **kwargs):
        try: 
            organization_id = self.kwargs['organization_id']
            
            notes = KindNotes.objects.filter(sender__organization=organization_id, is_active=True)
            if not notes.exists():
                return errorMessage('Kind notes does not exists')
            
            serializer = KindNotesViewsetSerializers(notes, many=True)
            return success(serializer.data)

        except Exception as e:
            return exception(e)  



class kindNotesPreDataView(generics.ListAPIView):

    def get(self, request, *args, **kwargs):
        try:
            organization_id = self.kwargs['organization_id']
            obj = Employees.objects.filter(organization=organization_id, is_active=True)
            serializer = kindNotesPreDataViewSerializers(obj, many=True)
            return success(serializer.data)
        except Exception as e:
            return exception(e) 