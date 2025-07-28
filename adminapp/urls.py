from django.urls import path

from adminapp.views import *

urlpatterns = [
   
    path('approve/',admin12),
    
    path('del/<int:user_id>/',delete_teacher),
   
    path('approve-teacher/<int:id>/', approve_teacher, name='approve_teacher'),
path('teacher-list/', tlist, name='teacher_list'),

    path('up/',uplst,name="lst"),
    path('sc/', select_class_view),
    path('reg/<int:year_id>/<int:class_level>/', register_students_by_class, name='admin_register_students_by_class'),
    path(
        "attendance1/",
        year_and_class_selector,       # ↓ new view
        name="attendance_select_year_class",
    ),

    # STEP‑2  per‑student attendance grid
    path(
        "attendance1/overview/<int:year_id>/<int:class_level>/",
        attendance_student_overview,   # ↓ new view
        name="attendance_student_overview"),
    path("marks12/",mark_year_class_selector, name="marks_select_year_class"),
    path("marks12/overview/<int:year_id>/<int:class_level>/",
     mark_student_overview,
     name="mark_student_overview"),
     path('add-academic-year/', add_academic_year, name='add_academic_year')



  
    ]
