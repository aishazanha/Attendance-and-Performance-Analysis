from django.shortcuts import render,redirect
from django.contrib import messages
from mainapp.models import head
from django.contrib.auth import authenticate,login,get_user_model
from adminapp.views import admin12
from teacherapp.views import Student
# from studentapp.views import *

User = get_user_model()  

def mainpage(request):
    return render(request,'index.html')
def sign(request):
    if request.method == 'POST':
        Name = request.POST['uname']
        Email = request.POST['ename']
        Username = request.POST['usename']
        Password = request.POST['pass']
        ConfirmPassword = request.POST.get('conpass')
        usertype = request.POST['type']
        if Password != ConfirmPassword:
           messages.error(request, "Passwords do not match!")
           return render(request, 'signup.html')
        if head.objects.filter(username=Username).exists():
            messages.error(request, "Username already taken. Please choose another one.")
            return render(request, 'signup.html')

        # ✅ Check if email already exists (optional)
        if head.objects.filter(email=Email).exists():
            messages.error(request, "Email already registered. Try logging in instead.")
            return render(request, 'signup.html')
        is_staff_value = 1 if usertype.lower() == "teacher" else 0
        data = head.objects.create_user(first_name=Name,email=Email,username=Username,password=Password,user_type=usertype,is_staff=is_staff_value )
        data.save()
        messages.success(request, "Account created successfully.")
        return render(request, 'signup.html')
    return render(request, 'signup.html')

                       # ⬅️ import
                # only if you auto‑create users

def login12(request):
    if request.method == "POST":
        uname = request.POST.get("usename")      # HTML field: <input name="usename">
        passw = request.POST.get("password")

        # 1️⃣ Try normal authentication (admin / teacher)
        user = authenticate(username=uname, password=passw)

        if user:
            # Admin
            if user.is_superuser:
                login(request, user)
                request.session["id"] = user.id
                return redirect(admin12)               # admin dashboard URL‑name

            # Teacher
            if user.is_staff and getattr(user, "activation", 0) == 1:
                login(request, user)
                return redirect("teacher_dashboard")      # teacher dashboard URL‑name

            # Staff but not approved
            messages.error(request, "Your account is not approved by admin.")
            return render(request, "login.html")

        # 2️⃣ Student login: name + roll‑number
        try:
            stu = Student.objects.get(name=uname, roll_number=passw, is_approved=True)
        except Student.DoesNotExist:
            messages.error(request, "Invalid username or password.")
            return render(request, "login.html")

        # student row found — ensure he/she has an auth.User account
        if stu.user:
            login(request, stu.user)
            return redirect('student_dashboard')          # student dashboard URL‑name

        # optional: auto‑create a User if missing
        new_user = User.objects.create_user(
            username=f"stu{stu.roll_number}",
            password=passw,
            first_name=stu.name.split()[0],
            last_name=" ".join(stu.name.split()[1:]),
        )
        stu.user = new_user
        stu.save()
        login(request, new_user)
        return redirect('student_dashboard')

    return render(request, "login.html")
