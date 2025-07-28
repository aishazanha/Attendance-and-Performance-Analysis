from django.urls import path
from studentapp.views import *

urlpatterns = [
    path('std/', student_dashboard, name='student_dashboard'),
    path('my-attendance/', my_attendance, name='my_attendance'),
    path('my-marks/', my_marks, name='my_marks'),
    path("student/profile/", my_profile, name="my_profile")
]
