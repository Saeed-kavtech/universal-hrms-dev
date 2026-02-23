from django.urls import path
from .views import ContactFormViewset

urlpatterns = [    
    path('kav_apis/contact/form/', ContactFormViewset.as_view({'post': 'create'})),   
]