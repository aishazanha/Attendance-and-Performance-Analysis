from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from adminapp.models import Course, Subject
from teacherapp.models import Student,Attendance ,Mark  ,GRADE_SCALE

@login_required
def student_dashboard(request):
    # fetch the Student object linked to the logged‑in user
    student = get_object_or_404(Student, user=request.user)
    return render(request, "studindexs.html", {"student": student})



@login_required
def my_attendance(request):
    student = get_object_or_404(Student, user=request.user)

    # subject‑wise aggregation
    qs = (Attendance.objects
          .filter(student=student)
          .values("subject__name", "subject__code")
          .annotate(total=Count("id"),
                    present=Count("id", filter=Q(status="P")))
          .order_by("subject__code"))

    records = []
    grand_total = grand_present = 0

    for row in qs:
        pct = round(row["present"] / row["total"] * 100, 2) if row["total"] else 0
        records.append({
            "name": row["subject__name"],
            "code": row["subject__code"],
            "total": row["total"],
            "present": row["present"],
            "pct": pct,
        })
        grand_total   += row["total"]
        grand_present += row["present"]

    overall_pct = round(grand_present / grand_total * 100, 2) if grand_total else 0

    context = {
        "student": student,
        "records": records,
        "grand_total": grand_total,
        "grand_present": grand_present,
        "overall_pct": overall_pct,
    }
    return render(request, "stud12.html", context)

def grade_for_percent(p):
    for g, lo, hi in GRADE_SCALE:
        if lo <= p <= hi:
            return g
    return "F"


@login_required
def my_marks(request):
    student = get_object_or_404(Student, user=request.user)

    # 🔹 1.  Get **all** courses for this class_level‑year combo
    courses_qs = Course.objects.filter(
        class_level=student.class_group.class_level,
        academic_year=student.class_group.academic_year
    )

    # 🔹 2.  Collect unique subjects from those courses
    subjects = Subject.objects.filter(course__in=courses_qs).distinct()

    if not subjects:
        return render(request, "student/marks.html", {
            "student": student,
            "records": [],
            "msg": "No subjects assigned.",
        })

    # 3. Fetch all marks for those subjects in one query
    ms = (Mark.objects
          .filter(student=student, subject__in=subjects)
          .values("subject_id", "exam_type", "mark"))

    mark_dict = {(m["subject_id"], m["exam_type"]): m["mark"] for m in ms}

    pair_info = [("S1", "I1"), ("S2", "I2"), ("S3", "I3")]
    pair_max = 150  # 100 (series) + 50 (internal)

    records = []
    for subj in subjects:
        row = {
            "name": subj.name,
            "code": subj.code,
            "pairs": [],
            "overall_pct": 0,
            "overall_grade": "F",
        }
        overall_tot = overall_max = 0

        for s_code, i_code in pair_info:
            s_mark = mark_dict.get((subj.id, s_code))
            i_mark = mark_dict.get((subj.id, i_code))

            total = (s_mark or 0) + (i_mark or 0)
            pct = round(total / pair_max * 100, 2) if (s_mark or i_mark) else None
            grade = grade_for_percent(pct) if pct is not None else "–"

            row["pairs"].append({
                "series": s_mark if s_mark is not None else "–",
                "internal": i_mark if i_mark is not None else "–",
                "total": total if (s_mark or i_mark) else "–",
                "grade": grade,
            })

            if pct is not None:
                overall_tot += total
                overall_max += pair_max

        if overall_max:
            row["overall_pct"] = round(overall_tot / overall_max * 100, 2)
            row["overall_grade"] = grade_for_percent(row["overall_pct"])

        records.append(row)

    return render(request, "mimarks.html", {
        "student": student,
        "records": records,
    })
@login_required
def my_profile(request):
    student = get_object_or_404(Student, user=request.user)

    context = {
        "name": student.name,
        "roll_number": student.roll_number,
        "class_level": student.class_group.class_level,
        "academic_year": student.class_group.academic_year.year
    }

    return render(request, "profile.html", context)

