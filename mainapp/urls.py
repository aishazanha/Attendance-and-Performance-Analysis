from django.urls import path
from mainapp.views import *

urlpatterns = [
    path('', mainpage, name='home'),
    path('in/',sign),
    path('lo/',login12),
    
    ]