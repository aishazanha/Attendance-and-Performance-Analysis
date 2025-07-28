from django.conf import settings
from django.db import models
from django.dispatch import receiver
from adminapp.models import Subject,AcademicYear
from django.db.models.signals import post_save
from django.db.models import Count, Q

class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True
    )

    # ✅  ForeignKey written as a string to avoid circular import problems
    class_group = models.ForeignKey(
        'adminapp.ClassGroup',            # ← quoted app.Model
        on_delete=models.CASCADE,
        null=True, blank=True             # nullable for existing rows
    )

    name        = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20)
    is_approved = models.BooleanField(default=True)

    class Meta:
        unique_together = ('class_group', 'roll_number')


   

    def __str__(self):
        return f"{self.name} ({self.roll_number})"
# teacherapp/models.py
class Attendance(models.Model):
    """
    One record = one student, one subject, one period, one date
    """
    date    = models.DateField()
    period  = models.PositiveSmallIntegerField()            # e.g. 1-8
    student = models.ForeignKey(Student,  on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    status  = models.CharField(
        max_length=1,
        choices=[('P', 'Present'), ('A', 'Absent')],
        default='P'
    )

    class Meta:
        unique_together = ('date', 'period', 'student', 'subject')
        ordering = ['date', 'period', 'student_id']

    def __str__(self):
        return (
            f"{self.date} | Period {self.period} | "
            f"{self.student.name} | {self.subject.code} | {self.status}"
        )


class ExamType(models.TextChoices):
    SERIES_1   = 'S1', 'Series 1'
    SERIES_2   = 'S2', 'Series 2'
    SERIES_3   = 'S3', 'Series 3'
    INTERNAL_1 = 'I1', 'Internal 1'
    INTERNAL_2 = 'I2', 'Internal 2'
    INTERNAL_3 = 'I3', 'Internal 3'          # NEW

class Mark(models.Model):
    student       = models.ForeignKey('teacherapp.Student', on_delete=models.CASCADE)
    subject       = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_type     = models.CharField(max_length=2, choices=ExamType.choices)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    class_level   = models.PositiveSmallIntegerField()
    grade         = models.CharField(max_length=2)
    mark          = models.PositiveSmallIntegerField()
    date_recorded = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'subject', 'exam_type', 'academic_year')

    def __str__(self):
        return f"{self.student} {self.subject} {self.exam_type} {self.grade}"
    
GRADE_SCALE = [
    ('A+', 90, 100),
    ('A',  80,  89),
    ('B+', 70,  79),
    ('B',  60,  69),
    ('C',  50,  59),
    ('D',  40,  49),
    ('F',   0,  39),
]

def max_mark_for_exam(code: str) -> int:
    """
    Return 50 for any Internal exam (code starts with 'I'),
    else 100 for Series exams.
    """
    return 50 if code.startswith('I') else 100


# ───────────────── cached stats for instant % ────────────────── #
class AttendanceStat(models.Model):
    """
    Cached totals so the overview page renders instantly.
    One row = student × subject × academic year.
    """
    student       = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject       = models.ForeignKey(Subject, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    total_classes = models.PositiveIntegerField(default=0)
    total_present = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('student', 'subject', 'academic_year')

    @property
    def percentage(self) -> float:
        return round(self.total_present / self.total_classes * 100, 2) \
               if self.total_classes else 0.0

    def __str__(self):
        return f"{self.student.name} – {self.subject.code} – {self.percentage}%"

# ───────── signal: keep AttendanceStat in sync automatically ─── #
@receiver(post_save, sender=Attendance)
def update_attendance_stat(sender, instance, created, **kwargs):
    stat, _ = AttendanceStat.objects.get_or_create(
        student=instance.student,
        subject=instance.subject,
        academic_year=instance.student.class_group.academic_year
    )

    if created:
        stat.total_classes += 1
        if instance.status == 'P':
            stat.total_present += 1
    else:
        # Re‑compute on edit (rare). Simpler than diffing.
        totals = Attendance.objects.filter(
            student=instance.student,
            subject=instance.subject
        ).aggregate(
            tot=Count('id'),
            pres=Count('id', filter=Q(status='P'))
        )
        stat.total_classes = totals['tot']
        stat.total_present = totals['pres']

    stat.save()

    