from .models import ContactForm
from rest_framework import serializers

class ContactFormSerializers(serializers.ModelSerializer):
    class Meta:
        model = ContactForm
        fields = [
            'name', 
            'email',
            'message',
            'company',
        ]
