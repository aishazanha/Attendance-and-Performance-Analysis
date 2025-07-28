from django.db import models
from mainapp.models import head  # only head is imported from mainapp

class AcademicYear(models.Model):
    year = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.year

class Class(models.Model):
    class_name = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 11)])

    def __str__(self):
        return f"Class {self.class_name}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, null=True, blank=True)

   

    def __str__(self):
        return f"{self.name} ({self.code})"


    
class ClassGroup(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    class_level = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)])
    
    class Meta:
        unique_together = ('academic_year', 'class_level')

    def __str__(self):
        return f"Class {self.class_level} - {self.academic_year.year}"

class Course(models.Model):
    teacher = models.ForeignKey(
        head,
        on_delete=models.SET_NULL,          # keep Course if teacher deleted
        null=True, blank=True,
        limit_choices_to={'activation': 1, 'is_staff': 1}
    )
    subjects = models.ManyToManyField(Subject)
    class_level = models.IntegerField(choices=[(i, str(i)) for i in range(1, 11)], default=1)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, default=1)

    # ✅ Add this field:
    max_strength = models.PositiveIntegerField(null=True, blank=True)  # null initially

    def __str__(self):
        return f"Course for {self.teacher} in Class {self.class_level} - {self.academic_year.year}"