from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from .models import User,Timetable, TimetableSlot
from .forms import TimetableForm
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login

from django.http import HttpResponse
import math

from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from .models import Timetable, User

def signup_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # check password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "signup.html")

        # check duplicate email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return render(request, "signup.html")

        # save user with hashed password
        user = User(
            name=name,
            email=email,
            phone=phone,
            password=make_password(password)  # 🔐 hash
        )
        user.save()
        messages.success(request, "Account created! Please login.")
        return redirect("login")

    return render(request, "signup.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                request.session["user_id"] = user.id  # ✅ Manually store ID
                request.session["user_name"] = user.name
                return redirect("details")
            else:
                messages.error(request, "Invalid password")
        except User.DoesNotExist:
            messages.error(request, "User not found")

    return render(request, "login.html")

def details_view(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = User.objects.get(id=request.session["user_id"])
    
    if request.method == "POST":
        form = TimetableForm(request.POST)
        if form.is_valid():
            timetable = form.save(commit=False)
            timetable.user = user
            timetable.save()
            return redirect("main_table")  # go to main timetable page
    else:
        form = TimetableForm()


    return render(request,"details.html")

def home(request):
    return render(request,"home.html")

def timetable(request):
    return render(request,"timetable.html")


# views.py



from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Timetable, TimetableSlot, User

def generate_timetable(request):
    if request.method == 'POST':
        # 1. Fetch logged-in user from session
        user_id = request.session.get("user_id")
        if not user_id:
            messages.error(request, "You must be logged in to create a timetable.")
            return redirect("login")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, "User not found. Please log in again.")
            return redirect("login")

        # 2. Get form data
        class_name = request.POST.get('class')
        days_count = int(request.POST.get('days'))
        periods_count = int(request.POST.get('periods'))
        start_time = request.POST.get('start_time')
        period_duration = int(request.POST.get('duration'))
        breaks_count = int(request.POST.get('breaks'))

        # 3. Get custom break positions (e.g., ['2', '4'] → [2, 4])
        break_positions = request.POST.getlist('break_positions[]')
        if break_positions:
            break_positions = sorted(set(map(int, break_positions)))
        else:
            break_positions = []

        # 4. Parse start time into hours and minutes
        start_hour, start_minute = map(int, start_time.split(':'))

        # 5. Get selected days
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        selected_days = weekdays[:days_count]

        # ---------- 6. Save main Timetable ----------
        timetable = Timetable.objects.create(
            user=user,  # ✅ Correctly linked with logged-in user
            class_name=class_name,
            no_of_days=days_count,
            no_of_periods=periods_count,
            start_time=datetime.strptime(start_time, "%H:%M").time(),
            duration_minutes=period_duration,
            no_of_breaks=breaks_count,
        )

        # ---------- 7. Generate and save time slots ----------
        for day in selected_days:
            current_hour = start_hour
            current_minute = start_minute
            period_counter = 1
            break_index = 0

            while period_counter <= periods_count:
                # Period start time
                period_start = datetime.strptime(f"{current_hour:02d}:{current_minute:02d}", "%H:%M")
                period_end = period_start + timedelta(minutes=period_duration)

                # Save period slot
                TimetableSlot.objects.create(
                    timetable=timetable,
                    day=day,
                    type='period',
                    number=period_counter,
                    start_time=period_start.time(),
                    end_time=period_end.time(),
                )

                # Update current time
                current_hour = period_end.hour
                current_minute = period_end.minute

                # Add break after this period if needed
                if break_index < len(break_positions) and period_counter == break_positions[break_index]:
                    break_start = datetime.strptime(f"{current_hour:02d}:{current_minute:02d}", "%H:%M")
                    break_end = break_start + timedelta(minutes=20)  # Fixed 20-minute break

                    TimetableSlot.objects.create(
                        timetable=timetable,
                        day=day,
                        type='break',
                        number=break_index + 1,
                        start_time=break_start.time(),
                        end_time=break_end.time(),
                    )

                    # Update time to break end
                    current_hour = break_end.hour
                    current_minute = break_end.minute
                    break_index += 1

                # Move to next period
                period_counter += 1

        # ---------- 8. Redirect after saving ----------
        messages.success(request, "Timetable generated successfully!")
        #return redirect('generate_timetable', timetable_id=timetable.id)
        return render(request,"timetable.html")


    return HttpResponse("Invalid request")



