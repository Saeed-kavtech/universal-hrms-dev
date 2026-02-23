from .models import ContactForm
from rest_framework import viewsets
from helpers.status_messages import (
    exception, errorMessage, success, successMessage, successfullyCreated, 
    successfullyUpdated, serializerError, successMessageWithData
)
from .serializers import ContactFormSerializers
from django.core.mail import EmailMessage

# Create your views here.

class ContactFormViewset(viewsets.ModelViewSet):
    queryset = ContactForm.objects.all()
    serializer_class = ContactFormSerializers
    
    def create(self, request, *args, **kwargs):
        try:
            required_fields = ['name', 'email', 'message','company']
            if not all(field in request.data for field in required_fields):
                return errorMessage('make sure you have added all the required fields: [name, email, message,company]')

            email = request.data['email']
            message = request.data['message']
            name = request.data['name']
            company = request.data['company']

            serializer = self.serializer_class(data = request.data)
            if not serializer.is_valid():
                return serializerError(serializer.errors)
            serializer.save()
            
            subject = "kavtech website contact form"
            body = f"\
                Name: {name} \n\
                Email: {email} \n\
                Company:{company} \n\
                Message: {message} \n\
            "
            to = "muhammad.junaid@kavmails.net"

            
            self.send_email(subject, body, to)

            return successfullyCreated(serializer.data)
        except Exception as e:
            return exception(e)
        
    
    def send_email(self, subject, message, to):
        try:
            email = EmailMessage(
                subject=subject,
                body=message, 
                to=[to],
                from_email = "noreply@kavmails.net",
            )
            email.send()
            print('email send successfully')
        except Exception as e:
            print(e)
            return None