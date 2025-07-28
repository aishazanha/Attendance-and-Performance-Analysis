from django.urls import path
from  teacherapp.views import  * 

urlpatterns = [
   
path('dashboard/',teacher_dashboard, name='teacher_dashboard'),
path('class/',class_arrangements),
path('attendance/',attendance_year_selection, name='attendance_year_selection'),
path('attendance/<int:year_id>/',assigned_courses, name='assigned_courses'),
path(
    'attendance/select/',
    select_period_for_attendance,
    name='select_class_subject_period'
),
 path(
        'attendance/mark/<int:year_id>/<int:class_level>/<int:subject_id>/<int:period>/',
        take_attendance,
        name='take_attendance'
    ),
path("marks/year/", marks_year_selection, name="marks_year_selection"),
    path("marks/<int:year_id>/", marks_assigned_courses, name="marks_assigned_courses"),
    path("marks/select-exam/", select_exam_type, name="select_exam_type"),
    path(
        "marks/enter/<int:year_id>/<int:class_level>/<int:subject_id>/<str:exam_type>/",
        enter_marks,
        name="enter_marks",
    ),
 path("attendance/summary/year/",
        attendance_year_summary,
         name="attendance_year_summary"),
    path("attendance/summary/<int:year_id>/",
        attendance_assigned_courses,
         name="attendance_assigned_courses"),
    path("attendance/summary/view/",
        attendance_overview,
         name="attendance_overview"),
path("ranking/year/", ranking_year_selection,
         name="ranking_year_selection"),

    path("ranking/<int:year_id>/", ranking_assigned_courses,
         name="ranking_assigned_courses"),

    # new step – pick exam‑set
    path("ranking/select-exam/",ranking_select_exam,
         name="ranking_select_exam"),

    # final table
    path("ranking/results/<int:year_id>/<int:class_level>/<int:subject_id>/<str:exam_set>/",
         ranking_results,
         name="ranking_results"),
]