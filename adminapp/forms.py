from django import forms
from adminapp.models import Course
from mainapp.models import head, Subject

class AssignSubjectsForm(forms.ModelForm):
    class Meta:
        model = head
        fields = ['assigned_subjects']
        widgets = {
            'assigned_subjects': forms.CheckboxSelectMultiple()
        }

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['teacher', 'subjects', 'class_level']  # Renamed academic_year to class
        widgets = {
            'subjects': forms.CheckboxSelectMultiple(),  # Multiple subjects can be selected
            'class': forms.Select()  # Dropdown for class selection
        }

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        # Only show approved teachers (activation=1 and is_staff=True)
        self.fields['teacher'].queryset = head.objects.filter(activation=1, is_staff=True)
        
        # Filter subjects to show all available subjects
        self.fields['subjects'].queryset = Subject.objects.all()
        
        # Dropdown list for classes (1 to 10)
        self.fields['class_level'].choices = [(i, str(i)) for i in range(1, 9)]  # Class choices from 1 to 10
