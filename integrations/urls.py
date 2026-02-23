from django.urls import path
from .views import *

urlpatterns = [
    path('add/mail/credentials/',MailCredentialsviewset.as_view({'post':'create','get':'list'})),
    path('add/mail/credentials/<pk>/',MailCredentialsviewset.as_view({'patch':'patch','delete':'delete'})),
    path('mail/inbox/data/',MailInboxviewset.as_view({'post':'get_inbox'})),
    path('get/mail/data/<pk>/',MailInboxviewset.as_view({'post':'mail_data'})),
    path('download/attachment/data/<pk>/',MailInboxviewset.as_view({'post':'download_attachments_data'})),
    path('send/mail/',MailInboxviewset.as_view({'post':'send_message'}))
]