from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q,Avg
from django.contrib import messages
from mainapp.models import head
from adminapp.models import AcademicYear, Course,Subject,ClassGroup
from teacherapp.models import Student,Attendance,Mark,GRADE_SCALE

def admin12(request):
    return render(request, 'adminindex.html')
def tlist(request):
   
    if 'id' not in request.session:
        messages.error(request, "Session expired, please login again.")
        return redirect('login')

    try:
        data = head.objects.get(id=request.session['id'])
    except head.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('login')

    pending_teachers  = head.objects.filter(is_superuser=0, is_staff=1, activation=0)
    approved_teachers = head.objects.filter(is_superuser=0, is_staff=1, activation=1)
    academic_years    = AcademicYear.objects.all()
    class_range       = range(1, 11)

    if request.method == 'POST':
       
        subject_name      = request.POST.get('name', '').strip()
        subject_code      = request.POST.get('code', '').strip()
        class_level       = request.POST.get('class_level')
        teacher_id        = request.POST.get('teacher')
        academic_year_id  = request.POST.get('academic_year')

      
        if not all([subject_name, subject_code, class_level, teacher_id, academic_year_id]):
            messages.error(request, "All fields are required.")
            return redirect('teacher_list')

       
        teacher       = get_object_or_404(head, id=teacher_id)
        academic_year = get_object_or_404(AcademicYear, id=academic_year_id)

       
        subject, _ = Subject.objects.get_or_create(
        code=subject_code,               
        defaults={
            'name': subject_name,
            'academic_year': academic_year
    }
)


      
        course, _ = Course.objects.get_or_create(
            teacher       = teacher,
            academic_year = academic_year,
            class_level   = class_level
        )
        course.subjects.add(subject)

        messages.success(request, "Subject created and assigned successfully.")
        return redirect('teacher_list')

    
    return render(request, 'approve.html', {
        'data': data,
        'det': pending_teachers,
        'approved_teachers': approved_teachers,
        'academic_years': academic_years,
        'class_range': class_range,
    })
def delete_teacher(request, user_id):
    user = head.objects.filter(id=user_id).first()
    if user:
        user.delete()
        messages.success(request, "Teacher deleted successfully.")
    else:
        messages.error(request, "User not found.")
    return redirect(tlist)

def approve_teacher(request, id):
    user = head.objects.filter(id=id).first()
    if user:
        user.activation = 1
        user.save()
        messages.success(request, "Teacher approved successfully.")
    else:
        messages.error(request, "Teacher not found.")
    return redirect(tlist)


def add_academic_year(request):
    if request.method == 'POST':
        year = request.POST.get('year')
        if not year:
            messages.error(request, "Please enter a year.")
        elif AcademicYear.objects.filter(year=year).exists():
            messages.warning(request, "This academic year already exists.")
        else:
            AcademicYear.objects.create(year=year)
            messages.success(request, f"Academic year {year} added successfully.")
            return redirect('add_academic_year')  

    years = AcademicYear.objects.all().order_by('-id')
    return render(request, 'addacademic.html', {'years': years})


def uplst(request):
    academic_years = AcademicYear.objects.all()
    selected_year_id = request.GET.get('year')

    courses_by_year = {}

    if selected_year_id:
        selected_year = get_object_or_404(AcademicYear, id=selected_year_id)
        courses = Course.objects.filter(academic_year=selected_year)

        course_data = []
        seen = set()
        for course in courses:
            for subj in course.subjects.all():
                key = (subj.code, course.class_level, course.teacher_id)
                if key in seen:          
                    continue
                seen.add(key)

                course_data.append({
                    "subject_name": subj.name,
                    "subject_code": subj.code,
                    "class_level":  course.class_level,
                    "teacher":      f"{course.teacher.get_full_name()} ({course.teacher.username})",
                })

        if course_data:
            courses_by_year[selected_year.year] = course_data

    return render(request, 'list.html', {
        'subject_data': courses_by_year,
        'academic_years': academic_years,
        'selected_year_id': int(selected_year_id) if selected_year_id else None,
    })
@login_required
def select_class_view(request):
    academic_years = AcademicYear.objects.all()
    selected_year_id = request.GET.get('year')
    class_levels = range(1, 11)

    return render(request, 'select.html', {
        'academic_years': academic_years,
        'selected_year_id': int(selected_year_id) if selected_year_id else None,
        'class_levels': class_levels,
    })


@login_required
def register_students_by_class(request, year_id, class_level):
    academic_year = get_object_or_404(AcademicYear, id=year_id)
    
    class_group, created = ClassGroup.objects.get_or_create(
        academic_year=academic_year,
        class_level=class_level
    )

    if request.method == 'POST':
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')

        if not name or not roll_number:
            messages.error(request, "Name and Roll number are required.")
        elif Student.objects.filter(class_group=class_group, roll_number=roll_number).exists():
            messages.warning(request, "Roll-number already exists in this class.")
        else:
            Student.objects.create(
                class_group=class_group,
                name=name,
                roll_number=roll_number,
                is_approved=True
            )
            messages.success(request, f"{name} registered successfully.")

        return redirect('admin_register_students_by_class', year_id=year_id, class_level=class_level)

    students = Student.objects.filter(class_group=class_group).order_by('roll_number')

    return render(request, 'register.html', {
        'class_group': class_group,
        'students': students
    })

def year_and_class_selector(request):
    years = AcademicYear.objects.order_by("-year")
    year_id = request.GET.get("year_id") or (years[0].id if years else None)

    if not year_id:
        return render(request, "attendance/no_years.html")

    year = get_object_or_404(AcademicYear, id=year_id)
    class_levels = range(1, 11)   # always 1‑10

    return render(request, "attensel.html", {
        "years": years,
        "selected_year_id": int(year_id),
        "year": year,
        "class_levels": class_levels,
    })



def attendance_student_overview(request, year_id, class_level):
    year = get_object_or_404(AcademicYear, id=year_id)
    class_grp = get_object_or_404(ClassGroup,
                                  academic_year=year,
                                  class_level=class_level)

    students = list(Student.objects.filter(class_group=class_grp)
                                 .order_by("roll_number"))
    subjects = list(Subject.objects
                    .filter(course__class_level=class_level,
                            course__academic_year=year)
                    .distinct()
                    .order_by("code"))

   
    qs = (Attendance.objects
                    .filter(student__in=students, subject__in=subjects)
                    .values("student_id", "subject_id")
                    .annotate(
                        total=Count("id"),
                        present=Count("id", filter=Q(status="P")),
                    ))

   
    lookup = {
        (row["student_id"], row["subject_id"]): (row["present"], row["total"])
        for row in qs
    }

   
    table_rows = []
    for stu in students:
        row = {
            "roll": stu.roll_number,
            "name": stu.name,
            "subjects": [],
            "overall_pct": 0,
        }
        overall_present = overall_total = 0

        for subj in subjects:
            present, total = lookup.get((stu.id, subj.id), (0, 0))
            pct = round(present / total * 100, 2) if total else 0
            row["subjects"].append({"present": present, "total": total, "pct": pct})
            overall_present += present
            overall_total   += total

        row["overall_pct"] = round(overall_present / overall_total * 100, 2) \
                             if overall_total else 0
        table_rows.append(row)

    return render(request, "attenover.html", {
        "year": year,
        "class_level": class_level,
        "subjects": subjects,
        "rows": table_rows,
    })




def grade_for_percent(pct: float) -> str:
    for g, lo, hi in GRADE_SCALE:
        if lo <= pct <= hi:
            return g
    return "F"



@login_required
def mark_year_class_selector(request):
    years = AcademicYear.objects.order_by("-year")
    if not years:
        return render(request, "marks/no_years.html")

   
    try:
        year_id = int(request.GET.get("year_id", years[0].id))
    except ValueError:
        year_id = years[0].id

    year = get_object_or_404(AcademicYear, id=year_id)
    class_levels = range(1, 11)  

    return render(request, "marksyear.html", {
        "years": years,
        "selected_year_id": year_id,
        "year": year,
        "class_levels": class_levels,
    })



@login_required
def mark_student_overview(request, year_id: int, class_level: int):
    year = get_object_or_404(AcademicYear, id=year_id)
    class_grp = get_object_or_404(
        ClassGroup, academic_year=year, class_level=class_level
    )

   
    students = list(Student.objects.filter(class_group=class_grp)
                                 .order_by("roll_number"))
    subjects = list(Subject.objects
                    .filter(course__academic_year=year,
                            course__class_level=class_level)
                    .distinct()
                    .order_by("code"))

    
    qs = (Mark.objects
          .filter(academic_year=year,
                  student__in=students,
                  subject__in=subjects)
          .values("student_id", "subject_id")
          .annotate(avg=Avg("mark")))

    mark_lookup = {
        (row["student_id"], row["subject_id"]): row["avg"]
        for row in qs
    }

   
    rows = []
    for stu in students:
        total_pct = counted = 0
        subj_entries = []

        for subj in subjects:
            pct = mark_lookup.get((stu.id, subj.id))
            pct_val = float(pct) if pct is not None else 0
            grade   = grade_for_percent(pct_val) if pct is not None else "—"
            subj_entries.append({"pct": pct_val, "grade": grade})

            if pct is not None:
                total_pct += pct_val
                counted   += 1

        overall_pct   = round(total_pct / counted, 2) if counted else 0
        overall_grade = grade_for_percent(overall_pct) if counted else "F"

        rows.append({
            "roll"          : stu.roll_number,
            "name"          : stu.name,
            "subjects"      : subj_entries,
            "overall_pct"   : overall_pct,
            "overall_grade" : overall_grade,
        })

    return render(request, "marksover.html", {
        "year"       : year,
        "class_level": class_level,
        "subjects"   : subjects,
        "rows"       : rows,
    })
