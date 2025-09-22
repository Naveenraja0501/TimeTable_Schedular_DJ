from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import User, Timetable, TimetableEntry
from .forms import TimetableForm

import json

# ------------------ SIGNUP ------------------
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
            password=make_password(password)  # hash password
        )
        user.save()
        messages.success(request, "Account created! Please login.")
        return redirect("login")

    return render(request, "signup.html")


# ------------------ LOGIN ------------------
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                request.session["user_id"] = user.user_id
                request.session["user_name"] = user.name
                return redirect("details")
            else:
                messages.error(request, "Invalid password")
        except User.DoesNotExist:
            messages.error(request, "User not found")

    return render(request, "login.html")


# ------------------ DETAILS ------------------
def details_view(request):
    if "user_id" not in request.session:
        return redirect("login")

    user = User.objects.get(user_id=request.session["user_id"])

    if request.method == "POST":
        form = TimetableForm(request.POST)
        if form.is_valid():
            timetable = form.save(commit=False)
            timetable.user = user
            timetable.save()
            return redirect("main_table")
    else:
        form = TimetableForm()
    return render(request, "details.html", {"form": form})


# ------------------ GENERATE TIMETABLE ------------------
def generate_timetable(request):
    if request.method == 'POST':
        class_name = request.POST.get('class')
        days_count = int(request.POST.get('days'))
        periods_count = int(request.POST.get('periods'))
        start_time = request.POST.get('start_time')
        period_duration = int(request.POST.get('duration'))
        breaks_count = int(request.POST.get('breaks'))
        break_positions = request.POST.getlist('break_positions[]')
        break_durations = request.POST.getlist('break_durations[]')

        # Get custom break positions
        if break_positions:
            break_positions = sorted(set(map(int, break_positions)))
        else:
            break_positions = []

        # Assign break fields
        break1 = break_positions[0] if len(break_positions) > 0 else None
        break2 = break_positions[1] if len(break_positions) > 1 else None
        break3 = break_positions[2] if len(break_positions) > 2 else None

        # Parse start time
        start_hour, start_minute = map(int, start_time.split(':'))

        # Generate periods and breaks
        time_slots = []
        current_hour, current_minute = start_hour, start_minute
        period_counter, break_index = 1, 0

        while period_counter <= periods_count:
            period_start = f"{current_hour:02d}:{current_minute:02d}"
            current_minute += period_duration
            if current_minute >= 60:
                current_hour += current_minute // 60
                current_minute %= 60
            period_end = f"{current_hour:02d}:{current_minute:02d}"

            time_slots.append({
                'type': 'period',
                'number': period_counter,
                'start': period_start,
                'end': period_end
            })

            # Insert break
            if break_index < len(break_positions) and period_counter == break_positions[break_index]:
                print(break_index)
                break_start = f"{current_hour:02d}:{current_minute:02d}"
                current_minute += int(break_durations[break_index]) if break_index < len(break_durations) else 20
                if current_minute >= 60:
                    current_hour += current_minute // 60
                    current_minute %= 60
                break_end = f"{current_hour:02d}:{current_minute:02d}"

                time_slots.append({
                    'type': 'break',
                    'number': break_index + 1,
                    'start': break_start,
                    'end': break_end
                })
                break_index += 1

            period_counter += 1

        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        selected_days = weekdays[:days_count]

        # Save to DB
        try:
            user = User.objects.get(user_id=request.session["user_id"])
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
            context = {
                'class_name': class_name,
                'days': selected_days,
                'time_slots': time_slots,
                'timetable_id': timetable.id,
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

    # ------------------ GET existing timetable ------------------
    elif request.method == 'GET':
        class_name = request.GET.get('class_name')
        print(type(class_name))
        if not class_name:
            return render(request, 'view_timetable.html', {
                'error': 'Please select a class first.'
            })

        try:
            user = User.objects.get(user_id=request.session["user_id"])
            print(user,">>>>>>>>>>>>>>>>")
            timetable = Timetable.objects.get(user=user, class_name=class_name)
            print(timetable,"<<<<<<<<<<<<<")

            #e=TimetableEntry.objects.get(user=user,timetable=cn)
            #print(e,"eeeeeeeeeeeeeeeeeee")

            entries = TimetableEntry.objects.filter(timetable=class_name, user=user) #user__user_id=user.user_id
            #entries = TimetableEntry.objects.filter(timetable=int(class_name))
            print(entries,"..................................")
            
            
            for entry in entries:
                print(entry)

            timetable_data = {}
            for entry in entries:
                if entry.day not in timetable_data:
                    timetable_data[entry.day] = []
                timetable_data[entry.day].append({
                    'period': entry.period_number,
                    'subject': entry.subject or '',
                    'teacher': entry.teacher or '',
                    'start_time': entry.start_time.strftime('%H:%M'),
                    'end_time': entry.end_time.strftime('%H:%M'),
                    'is_break': entry.is_break
                })
            print(timetable_data,'????????+++?????????')

            # Breaks
            break_positions = []
            if timetable.break1_after_period:
                break_positions.append(timetable.break1_after_period)
            if timetable.break2_after_period:
                break_positions.append(timetable.break2_after_period)
            if timetable.break3_after_period:
                break_positions.append(timetable.break3_after_period)

            # Generate slots
            start_hour, start_minute, *_ = map(int, str(timetable.start_time).split(':'))
            time_slots = []
            current_hour, current_minute = start_hour, start_minute
            period_counter, break_index = 1, 0

            while period_counter <= timetable.no_of_periods:
                period_start = f"{current_hour:02d}:{current_minute:02d}"
                current_minute += timetable.duration_minutes
                if current_minute >= 60:
                    current_hour += current_minute // 60
                    current_minute %= 60
                period_end = f"{current_hour:02d}:{current_minute:02d}"

                time_slots.append({
                    'type': 'period',
                    'number': period_counter,
                    'start': period_start,
                    'end': period_end
                })

                if break_index < len(break_positions) and period_counter == break_positions[break_index]:
                    break_start = f"{current_hour:02d}:{current_minute:02d}"
                    current_minute += 20
                    if current_minute >= 60:
                        current_hour += current_minute // 60
                        current_minute %= 60
                    break_end = f"{current_hour:02d}:{current_minute:02d}"

                    time_slots.append({
                        'type': 'break',
                        'number': break_index + 1,
                        'start': break_start,
                        'end': break_end
                    })
                    break_index += 1

                period_counter += 1

            weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            selected_days = weekdays[:timetable.no_of_days]
            print(time_slots,'*******************', selected_days)
            context = {
                'class_name': class_name,
                'days': selected_days,
                'time_slots': time_slots,
                'timetable_id': timetable.id,
                'timetable_data': timetable_data
            }
            print(context,"c ---------- c")
            return render(request, 'view_timetable.html', context)

        except Timetable.DoesNotExist:
            print(f"Does Not Erorr-----------")
            return render(request, 'view_timetable.html', {
                'class_name': class_name,
                'error': f'Timetable for class {class_name} not found.'
            })
        except Exception as e:
            return render(request, 'view_timetable.html', {
                'class_name': class_name,
                'error': f'Error retrieving timetable: {str(e)}'
            })


# ------------------ SAVE TIMETABLE ENTRY ------------------
@csrf_exempt
@require_POST
def save_timetable_entry(request):
    try:
        data = json.loads(request.body)
        timetable_id = data.get('timetable_id')
        day = data.get('day')
        period_number = data.get('period_number')
        subject = data.get('subject')
        teacher = data.get('teacher')
        startTime = data.get('startTime')
        endTime = data.get('endTime')
        
        # create = TimetableEntry.objects.create(
        #     day=day,
        #     period_number=period_number,
        #     subject=subject,
        #     teacher_name=teacher,
        #     # timetable_id=timetable_id,
        #     start_time=startTime,
        #     end_time=endTime,
        # )

        if not timetable_id:
            return JsonResponse({'status': 'error', 'message': 'Timetable ID is missing'})

        try:
            timetable = Timetable.objects.get(id=int(timetable_id))
        except (ValueError, Timetable.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Invalid timetable ID'})
        user = User.objects.get(user_id=request.session["user_id"])
        entry, created = TimetableEntry.objects.update_or_create(
            user=user,
            timetable=timetable,
            day=day,
            period_number=period_number,
            start_time=startTime,
            end_time=endTime,
            defaults={'subject': subject, 'teacher': teacher}
        )
        return JsonResponse({'status': 'success', 'message': 'Entry saved successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


# ------------------ GET TIMETABLE CONTENT ------------------
def get_timetable_content(request, timetable_id):
    try:
        timetable = Timetable.objects.get(id=timetable_id)
        entries = TimetableEntry.objects.filter(timetable=timetable)
            

        timetable_data = {}
        for entry in entries:
            if entry.day not in timetable_data:
                timetable_data[entry.day] = []
            timetable_data[entry.day].append({
                'period': entry.period_number,
                'subject': entry.subject or '',
                'teacher': entry.teacher or '',
                'start_time': entry.start_time.strftime('%H:%M'),
                'end_time': entry.end_time.strftime('%H:%M'),
                'is_break': entry.is_break
            })
        print(timetable_data,'>>>>>>>>>>>>>')
        return JsonResponse({'success': True, 'data': timetable_data})

    except Timetable.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Timetable not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


