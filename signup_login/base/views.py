from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password,check_password
from .models import User,Timetable
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

from django.contrib.auth import authenticate, login
'''
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('details')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')
'''
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                request.session["user_id"] = user.user_id
               #request.session["user_id"] = user.id  # ✅ Manually store ID
                request.session["user_name"] = user.name
                return redirect("details")
            else:
                messages.error(request, "Invalid password")
        except User.DoesNotExist:
            messages.error(request, "User not found")

    return render(request, "login.html")


'''
def details_view(request):
    if request.user.is_authenticated:
        # Get only this user's timetables
        user_timetables = Timetable.objects.filter(user=request.user)
        return render(request, 'details.html', {'timetables': user_timetables})
    else:
        return redirect('login')   
'''
def details_view(request):
    if "user_id" not in request.session:
        return redirect("login")

    #user = User.objects.get(id=request.session["user_id"])
    user = User.objects.get(user_id=request.session["user_id"])
    
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



def timetable(request):
    return render(request,"timetable.html")


# views.py


from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
#from django.contrib.auth.decorators import login_required

#@login_required
def generate_timetable(request):
    if request.method == 'POST':
        # Get form data
        class_name = request.POST.get('class')
        days_count = int(request.POST.get('days'))
        periods_count = int(request.POST.get('periods'))
        start_time = request.POST.get('start_time')
        period_duration = int(request.POST.get('duration'))
        breaks_count = int(request.POST.get('breaks'))
        break_positions = request.POST.getlist('break_positions[]')

        # Get custom break positions from form and convert to integers
        if break_positions:
            break_positions = sorted(set(map(int, break_positions)))  # unique & sorted
        else:
            break_positions = []

        # Set individual break fields
        break1 = break_positions[0] if len(break_positions) > 0 else None
        break2 = break_positions[1] if len(break_positions) > 1 else None
        break3 = break_positions[2] if len(break_positions) > 2 else None

        # Parse start time
        start_hour, start_minute = map(int, start_time.split(':'))

        # Generate time slots
        time_slots = []
        current_hour = start_hour
        current_minute = start_minute

        period_counter = 1  # Tracks periods
        break_index = 0     # Tracks which break we're at

        while period_counter <= periods_count:
            # Add a regular period
            period_start = f"{current_hour:02d}:{current_minute:02d}"

            current_minute += period_duration
            if current_minute >= 60:
                current_hour += current_minute // 60
                current_minute = current_minute % 60

            period_end = f"{current_hour:02d}:{current_minute:02d}"

            time_slots.append({
                'type': 'period',
                'number': period_counter,
                'start': period_start,
                'end': period_end
            })

            # After adding this period, check if a break is needed
            if break_index < len(break_positions) and period_counter == break_positions[break_index]:
                # Insert break right after this period
                break_start = f"{current_hour:02d}:{current_minute:02d}"

                current_minute += 20  # Fixed break duration of 20 minutes
                if current_minute >= 60:
                    current_hour += current_minute // 60
                    current_minute = current_minute % 60

                break_end = f"{current_hour:02d}:{current_minute:02d}"

                time_slots.append({
                    'type': 'break',
                    'number': break_index + 1,
                    'start': break_start,
                    'end': break_end
                })

                break_index += 1  # Move to next break

            # Increment period counter
            period_counter += 1

        # Weekday names
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        selected_days = weekdays[:days_count]

        # Save to database
        try:
            user = User.objects.get(user_id=request.session["user_id"])
            # Get the current user (replace with actual user retrieval)
            #user = User.objects.first()  # Replace with actual user from session/request
            #user = request.user
    
            #if not user.is_authenticated:
                #return redirect('login')
            
            # Create Timetable entry with individual break fields
            timetable = Timetable.objects.create(
                user=user,
                class_name=class_name,
                no_of_days=days_count,
                no_of_periods=periods_count,
                start_time=start_time,
                duration_minutes=period_duration,
                no_of_breaks=breaks_count,
               
                break1_after_period=break1,
                break2_after_period=break2,
                break3_after_period=break3
            )
            
            # Add timetable ID to context for reference
            context = {
                'class_name': class_name,
                'days': selected_days,
                'time_slots': time_slots,
                'timetable_id': timetable.id,  # For reference
                'success': True,
                'message': 'Timetable configuration saved successfully!'
            }
            
        except Exception as e:
            context = {
                'class_name': class_name,
                'days': selected_days,
                'time_slots': time_slots,
                'error': True,
                'message': f'Error saving to database: {str(e)}'
            }

        return render(request, 'timetable.html', context)
    
    # Handle GET request - View existing timetable
    elif request.method == 'GET':
        class_name = request.GET.get('class_name')
        
        print(f"DEBUG: Class name from GET: {class_name}")
        
        if not class_name:
            return render(request, 'view_timetable.html', {
                'error': 'Please select a class first.'
            })
        
        try:
            #user = request.user  # This is the key change!
            
            #if not user.is_authenticated:
                #return redirect('login')  # Redirect to login if not authenticated
            
            #user = User.objects.first()
            user = User.objects.get(user_id=request.session["user_id"])
            print(f"DEBUG: User: {user}")
            
            timetable = Timetable.objects.get(user=user, class_name=class_name)
            print(f"DEBUG: Found timetable: {timetable}")
            print(f"DEBUG: Timetable data - Days: {timetable.no_of_days}, Periods: {timetable.no_of_periods}, Start: {timetable.start_time}")
            
            # Get break positions
            break_positions = []
            if timetable.break1_after_period:
                break_positions.append(timetable.break1_after_period)
                print(f"DEBUG: Break 1 after period: {timetable.break1_after_period}")
            if timetable.break2_after_period:
                break_positions.append(timetable.break2_after_period)
                print(f"DEBUG: Break 2 after period: {timetable.break2_after_period}")
            if timetable.break3_after_period:
                break_positions.append(timetable.break3_after_period)
                print(f"DEBUG: Break 3 after period: {timetable.break3_after_period}")
            
            print(f"DEBUG: All break positions: {break_positions}")

            # Generate time slots
            start_time_str = str(timetable.start_time)
            print(f"DEBUG: Start time string: {start_time_str}")

            # Fix the time parsing - handle HH:MM:SS format
            time_parts = start_time_str.split(':')
            start_hour = int(time_parts[0])
            start_minute = int(time_parts[1])
            # Ignore seconds (time_parts[2]) if present

            print(f"DEBUG: Start hour: {start_hour}, Start minute: {start_minute}")
            
    
            
            
            time_slots = []
            current_hour = start_hour
            current_minute = start_minute
            period_counter = 1
            break_index = 0

            print(f"DEBUG: Generating {timetable.no_of_periods} periods...")
            
            while period_counter <= timetable.no_of_periods:
                period_start = f"{current_hour:02d}:{current_minute:02d}"
                current_minute += timetable.duration_minutes
                if current_minute >= 60:
                    current_hour += current_minute // 60
                    current_minute = current_minute % 60
                period_end = f"{current_hour:02d}:{current_minute:02d}"

                time_slots.append({
                    'type': 'period',
                    'number': period_counter,
                    'start': period_start,
                    'end': period_end
                })
                print(f"DEBUG: Added period {period_counter} - {period_start} to {period_end}")

                if break_index < len(break_positions) and period_counter == break_positions[break_index]:
                    break_start = f"{current_hour:02d}:{current_minute:02d}"
                    current_minute += 20
                    if current_minute >= 60:
                        current_hour += current_minute // 60
                        current_minute = current_minute % 60
                    break_end = f"{current_hour:02d}:{current_minute:02d}"

                    time_slots.append({
                        'type': 'break',
                        'number': break_index + 1,
                        'start': break_start,
                        'end': break_end
                    })
                    print(f"DEBUG: Added break {break_index + 1} - {break_start} to {break_end}")
                    break_index += 1

                period_counter += 1

            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            selected_days = weekdays[:timetable.no_of_days]
            
            print(f"DEBUG: Selected days: {selected_days}")
            print(f"DEBUG: Time slots generated: {len(time_slots)}")
            
            context = {
                'class_name': class_name,
                'days': selected_days,
                'time_slots': time_slots,
                'timetable_id': timetable.id,
            }
            
            return render(request, 'view_timetable.html', context)
            
        except Timetable.DoesNotExist:
            print(f"DEBUG: Timetable for class {class_name} not found")
            return render(request, 'view_timetable.html', {
                'class_name': class_name,
                'error': f'Timetable for class {class_name} not found.'
            })
        except Exception as e:
            print(f"DEBUG: Error: {str(e)}")
            return render(request, 'view_timetable.html', {
                'class_name': class_name,
                'error': f'Error retrieving timetable: {str(e)}'
            })