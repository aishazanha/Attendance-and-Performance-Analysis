from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from mainapp.models import head as HeadUser
from adminapp.models import Course, AcademicYear,Subject,ClassGroup
from teacherapp.models import Student,Attendance,ExamType, Mark,max_mark_for_exam,GRADE_SCALE,AttendanceStat
from django.utils.crypto import get_random_string
from datetime import date,datetime
from django.db.models import Count, Q
import json


@login_required
def teacher_dashboard(request):
   teacher = request.user  # Current logged-in teacher
   return render(request, 'indext.html', {'teacher': teacher})
def class_arrangements(request):
    teacher = request.user
    academic_years = AcademicYear.objects.all().order_by("-year")  
    selected_year_id = request.GET.get('academic_year')
    assigned_courses = []
    if selected_year_id:
        try:
            selected_year = AcademicYear.objects.get(id=selected_year_id)
            assigned_courses = Course.objects.filter(teacher=teacher, academic_year=selected_year)
        except AcademicYear.DoesNotExist:
            selected_year = None
    else:
        selected_year = None

    return render(request, 'class.html', {
        'academic_years': academic_years,
        'selected_year_id': selected_year_id,
        'assigned_courses': assigned_courses,
    })  
@login_required
def attendance_year_selection(request):
    teacher = request.user
    years = (
        AcademicYear.objects
        .filter(course__teacher=teacher)
        .distinct()
        .order_by('-year')
    )
    years = AcademicYear.objects.all().order_by("-year") 
    return render(request, 'year.html', {'years': years})
@login_required
def assigned_courses(request, year_id):
        teacher = request.user
        academic_year = get_object_or_404(AcademicYear, id=year_id)
        items = []
        courses = Course.objects.filter(teacher=teacher, academic_year=academic_year)
        for course in courses:
            for subj in course.subjects.all():
                items.append({
                    'class_level': course.class_level,
                    'subject_id': subj.id,
                    'subject_name': subj.name,
                    'subject_code': subj.code,
                })
        return render(
            request,
            'assigned.html',
            {
                'academic_year': academic_year,
                'items': items,
            }
        )
@login_required
def select_period_for_attendance(request):
    year_id     = request.GET.get('year_id')
    class_level = request.GET.get('class_level')
    subject_id  = request.GET.get('subject_id')
    period      = request.GET.get('period')   
    if not all([year_id, class_level, subject_id]):
        messages.error(request, "Missing academic year / class / subject data.")
        return redirect('attendance_year_selection')   
    year_obj    = get_object_or_404(AcademicYear, id=year_id)
    subject_obj = get_object_or_404(Subject, id=subject_id)
    if period:
        return redirect(
            'take_attendance',
            year_id     = int(year_id),
            class_level = int(class_level),
            subject_id  = int(subject_id),
            period      = int(period)
        )
    return render(
        request,
        'period.html',                     
        {
            'year'        : year_obj,     
            'subject'     : subject_obj,   
            'year_id'     : year_id,
            'class_level' : class_level,
            'subject_id'  : subject_id,
            'periods'     : range(1, 9),  
        }
    )
@login_required
def take_attendance(request, year_id, class_level, subject_id, period):
    today = date.today()
    class_group = get_object_or_404(ClassGroup, academic_year_id=year_id, class_level=class_level)
    subject = get_object_or_404(Subject, id=subject_id)
    students = Student.objects.filter(class_group=class_group)
    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if status in ['P', 'A']:
                Attendance.objects.get_or_create(
                    student=student,
                    subject=subject,
                    date=today,
                    period=period,
                    defaults={'status': status}
                )
        messages.success(request, "Attendance saved.")
        return redirect(select_period_for_attendance)
    return render(request, 'att.html', {
        'students': students,
        'subject': subject,
        'academic_year': class_group.academic_year,
        'class_level': class_level,
        'today': today,
        'period': period
    })
@login_required
def marks_year_selection(request):
    teacher = request.user
    years = (
        AcademicYear.objects
        .filter(course__teacher=teacher)
        .distinct()
        .order_by('-year')
    )
    years = AcademicYear.objects.all().order_by("-year")  
    return render(request, "markyear.html", {"years": years, "flow": "marks"})
@login_required
def marks_assigned_courses(request, year_id):
    teacher       = request.user
    academic_year = get_object_or_404(AcademicYear, id=year_id)
    items = []
    courses = Course.objects.filter(teacher=teacher, academic_year=academic_year)
    for course in courses:
        for subj in course.subjects.all():
            items.append({
                "class_level" : course.class_level,
                "subject_id"  : subj.id,
                "subject_name": subj.name,
                "subject_code": subj.code,
            })
    return render(
        request,
        "markassigned.html",          
        {
            "flow"         : "marks",
            "academic_year": academic_year,
            "items"        : items,
        },
    )
@login_required
def select_exam_type(request):
    year_id     = request.GET.get("year_id")
    class_level = request.GET.get("class_level")
    subject_id  = request.GET.get("subject_id")
    exam_type   = request.GET.get("exam_type")   
    if not all([year_id, class_level, subject_id]):
        messages.error(request, "Missing academic year / class / subject data.")
        return redirect("marks_year_selection")
    year_obj    = get_object_or_404(AcademicYear, id=year_id)
    subject_obj = get_object_or_404(Subject,       id=subject_id)
    if exam_type:
        return redirect(
            "enter_marks",
            year_id     = int(year_id),
            class_level = int(class_level),
            subject_id  = int(subject_id),
            exam_type   = exam_type,      
        )
    return render(
        request,
        "extype.html",        
        {
            "year_id"     : year_id,
            "class_level" : class_level,
            "subject_id"  : subject_id,
            "exam_types"  : ExamType.choices,
            "year"        : year_obj,
            "subject"     : subject_obj,
        },
    )
def grade_for_mark(mark: int) -> str:
    """Return A+, A, … based on GRADE_SCALE."""
    for g, low, high in GRADE_SCALE:
        if low <= mark <= high:
            return g
    return "F"
@login_required
def enter_marks(request, year_id, class_level, subject_id, exam_type):
    year_obj    = get_object_or_404(AcademicYear, id=year_id)
    subject_obj = get_object_or_404(Subject,       id=subject_id)
    class_group = get_object_or_404(
        ClassGroup, academic_year_id=year_id, class_level=class_level
    )
    students           = Student.objects.filter(class_group=class_group).order_by("roll_number")
    max_mark_allowed   = max_mark_for_exam(exam_type)
    exam_type_readable = dict(ExamType.choices).get(exam_type, exam_type)
    if request.method == "POST":
        for stu in students:
           
            mark_str = request.POST.get(f"mark_{stu.id}", "").strip()
            if not mark_str:
                continue
            try:
                mark = int(mark_str)
            except ValueError:
                messages.error(request, f"{stu.name}: invalid mark '{mark_str}'.")
                return redirect(request.path)

            if mark > max_mark_allowed:
                messages.error(request,
                               f"{stu.name}: mark {mark} exceeds max {max_mark_allowed}.")
                return redirect(request.path)

            grade = grade_for_mark(mark)

            Mark.objects.update_or_create(
                student       = stu,
                subject       = subject_obj,
                exam_type     = exam_type,
                academic_year = year_obj,
                defaults={
                    "class_level": class_level,
                    "grade": grade,
                    "mark": mark,
                },
            )
        messages.success(request, "Marks saved successfully.")
        return redirect("select_exam_type")

   
    return render(request, "marks.html", {
    "students": students,
    "subject": subject_obj,
    "academic_year": year_obj,
    "class_level": class_level,
    "exam_type_code": exam_type,
    "exam_type": exam_type_readable,
    "max_mark": max_mark_allowed,
    "grade_scale": GRADE_SCALE,                     
    "grade_scale_json": json.dumps(GRADE_SCALE),    
})
@login_required
def attendance_year_summary(request):
    teacher = request.user
    years = (AcademicYear.objects
             .filter(course__teacher=teacher)
             .distinct()
             .order_by('-year'))
    years = AcademicYear.objects.all().order_by("-year") 
    return render(request, 'overyear.html', {"years": years, "flow": "overview"})
@login_required
def attendance_assigned_courses(request, year_id):
    teacher       = request.user
    academic_year = get_object_or_404(AcademicYear, id=year_id)

    items = []
    for course in Course.objects.filter(teacher=teacher, academic_year=academic_year):
        for subj in course.subjects.all():
            items.append({
                "class_level" : course.class_level,
                "subject_id"  : subj.id,
                "subject_name": subj.name,
                "subject_code": subj.code,
            })

    return render(request, 'overass.html', {
        "academic_year": academic_year,
        "items"        : items,
        "flow"         : "overview",
    })
@login_required
def attendance_overview(request):
    year_id     = request.GET.get('year_id')
    class_level = request.GET.get('class_level')
    subject_id  = request.GET.get('subject_id')
    date_str    = request.GET.get('date')
    view_mode   = request.GET.get('view', 'list')

    if not all([year_id, class_level, subject_id]):
        messages.error(request, "Missing parameters.")
        return redirect('attendance_year_summary')

    year_obj    = get_object_or_404(AcademicYear, id=year_id)
    subject_obj = get_object_or_404(Subject,       id=subject_id)
    class_grp   = get_object_or_404(
        ClassGroup, academic_year_id=year_id, class_level=class_level
    )
    students = Student.objects.filter(class_group=class_grp)

    # daily list (same as before) .............................................
    selected_date, day_records = None, []
    if view_mode == 'list' and date_str:
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            day_records = (Attendance.objects
                           .filter(subject=subject_obj,
                                   student__in=students,
                                   date=selected_date)
                           .order_by('period', 'student__roll_number'))
        except ValueError:
            messages.error(request, "Invalid date format (yyyy-mm-dd).")

    # on‑the‑fly per‑student percentage .......................................
    agg = (Attendance.objects
           .filter(subject=subject_obj, student__in=students)
           .values('student__id', 'student__roll_number', 'student__name')
           .annotate(
               total=Count('id'),
               present=Count('id', filter=Q(status='P')),
           )
           .order_by('student__roll_number'))

    student_stats = [
        {
            "roll": a['student__roll_number'],
            "name": a['student__name'],
            "present": a['present'],
            "total": a['total'],
            "pct": round(a['present'] / a['total'] * 100, 2) if a['total'] else 0,
        }
        for a in agg
    ]

    return render(request, 'overview.html', {
        "academic_year": year_obj,
        "class_level": class_level,
        "subject": subject_obj,
        "view_mode": view_mode,
        "student_stats": student_stats,
        "day_records": day_records,
        "selected_date": selected_date,
    })
# --- helper --------------------------------------------------------------
def grade_for_score(score: float) -> str:
    """Return A+, A, B+ … from your GRADE_SCALE list."""
    for g, low, high in GRADE_SCALE:
        if low <= score <= high:
            return g
    return "F"
EXAM_SETS = {
    "S1I1": {"label": "Series 1 + Internal 1", "codes": ["S1", "I1"], "max_total": 150},
    "S2I2": {"label": "Series 2 + Internal 2", "codes": ["S2", "I2"], "max_total": 150},
    "S3I3": {"label": "Series 3 + Internal 3", "codes": ["S3", "I3"], "max_total": 150},
}
def grade_for_score(percent: float) -> str:
    for g, lo, hi in GRADE_SCALE:
        if lo <= percent <= hi:
            return g
    return "F"
@login_required
def ranking_year_selection(request):
    teacher = request.user
    years = (AcademicYear.objects
             .filter(course__teacher=teacher)
             .distinct()
             .order_by("-year"))
    years = AcademicYear.objects.all().order_by("-year") 
    return render(request, "rankyear.html", {"years": years, "flow": "ranking"})
@login_required
def ranking_assigned_courses(request, year_id):
    teacher       = request.user
    academic_year = get_object_or_404(AcademicYear, id=year_id)

    items = []
    for course in Course.objects.filter(teacher=teacher, academic_year=academic_year):
        for subj in course.subjects.all():
            items.append({
                "class_level": course.class_level,
                "subject_id" : subj.id,
                "subject_name": subj.name,
                "subject_code": subj.code,
            })

    return render(request, "rankass.html", {
        "academic_year": academic_year,
        "items": items,
        "flow": "ranking",
    })
@login_required
def ranking_select_exam(request):
    year_id     = request.GET.get("year_id")
    class_level = request.GET.get("class_level")
    subject_id  = request.GET.get("subject_id")
    exam_set    = request.GET.get("exam_set")

    if not all([year_id, class_level, subject_id]):
        messages.error(request, "Missing parameters.")
        return redirect("ranking_year_selection")

    if exam_set in EXAM_SETS:
        return redirect("ranking_results",
                        year_id=year_id,
                        class_level=class_level,
                        subject_id=subject_id,
                        exam_set=exam_set)

    return render(request, "ranksel.html", {
        "year_id": year_id,
        "class_level": class_level,
        "subject_id": subject_id,
        "exam_sets": EXAM_SETS,
    })

@login_required
def ranking_results(request, year_id, class_level, subject_id, exam_set):
    if exam_set not in EXAM_SETS:
        messages.error(request, "Invalid exam‑set.")
        return redirect("ranking_year_selection")

    meta = EXAM_SETS[exam_set]
    year_obj    = get_object_or_404(AcademicYear, id=year_id)
    subject_obj = get_object_or_404(Subject,       id=subject_id)
    class_grp   = get_object_or_404(
        ClassGroup, academic_year_id=year_id, class_level=class_level
    )
    students = Student.objects.filter(class_group=class_grp).order_by("roll_number")

    # gather marks ----------------------------------------------------------
    marks_qs = (Mark.objects
                .filter(academic_year=year_obj,
                        subject=subject_obj,
                        exam_type__in=meta["codes"],
                        student__in=students)
                .values("student_id", "exam_type", "mark"))

    mark_lookup = {(m["student_id"], m["exam_type"]): m["mark"] for m in marks_qs}

    rows = []
    for stu in students:
        partials = {code: mark_lookup.get((stu.id, code), 0) for code in meta["codes"]}
        total = sum(partials.values())
        pct   = round(total / meta["max_total"] * 100, 2) if meta["max_total"] else 0
        grade = grade_for_score(pct)

        rows.append({
            "student": stu,
            "partials": partials,
            "total": total,
            "pct": pct,
            "grade": grade,
        })

    rows.sort(key=lambda r: (-r["total"], r["student"].roll_number))
    for idx, r in enumerate(rows, 1):
        r["rank"] = idx

    return render(request, "ranking.html", {
        "academic_year": year_obj,
        "class_level": class_level,
        "subject": subject_obj,
        "exam_meta": meta,
        "rows": rows,
    })
