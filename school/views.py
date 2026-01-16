import csv
from datetime import datetime, date
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.db.models import Sum
from django.utils import timezone

# Import all models
from .models import (
    Student, Staff, StudentFee, FeeTransaction, 
    Attendance, StaffAttendance, Expense
)

# =========================================
# 1. PUBLIC PAGES
# =========================================
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def gallery(request):
    return render(request, 'gallery.html')


# =========================================
# 2. AUTHENTICATION & REDIRECTS
# =========================================
@login_required
def smart_redirect(request):
    """ Redirects users to their specific dashboard based on role """
    user = request.user
    if user.is_superuser:
        return redirect('super_dashboard')
    elif user.groups.filter(name='Staff').exists():
        return redirect('staff_dashboard')
    else:
        return redirect('dashboard')


# =========================================
# 3. DASHBOARDS
# =========================================
@login_required
def super_dashboard(request):
    return render(request, 'super_dashboard.html')

@login_required
def dashboard(request):
    """ Student / Parent Dashboard """
    if request.user.is_superuser:
        return redirect('super_dashboard')
    elif request.user.groups.filter(name='Staff').exists():
        return redirect('staff_dashboard')

    try:
        student_profile = Student.objects.get(username=request.user.username)
        fees = StudentFee.objects.filter(student=student_profile)
        attendance = Attendance.objects.filter(student=student_profile).order_by('-date')[:5]

        context = {
            'student': student_profile,
            'fees': fees,
            'attendance': attendance
        }
        return render(request, 'dashboard.html', context)
    except Student.DoesNotExist:
        return render(request, 'dashboard.html', {'error': 'No student profile found for this account.'})

@login_required
def staff_dashboard(request):
    """ Teacher Dashboard """
    # 1. Fetch Classes for Attendance Dropdown
    classes = Student.objects.values_list('class_admitted', flat=True).distinct()
    
    # 2. Logic for Marking Student Attendance
    selected_class = request.GET.get('class_selected')
    students = []
    if selected_class:
        students = Student.objects.filter(class_admitted=selected_class).order_by('student_name')

    if request.method == 'POST':
        attendance_date = request.POST.get('attendance_date')
        selected_class_post = request.POST.get('class_selected')
        if not attendance_date: attendance_date = timezone.now().date()
        
        students_to_mark = Student.objects.filter(class_admitted=selected_class_post)
        for student in students_to_mark:
            status = request.POST.get(f'status_{student.id}')
            if status:
                Attendance.objects.update_or_create(student=student, date=attendance_date, defaults={'status': status})
        messages.success(request, "Attendance marked!")
        return redirect('staff_dashboard')

    # 3. Fetch My Personal Data
    my_salary_history = []
    my_attendance_history = []
    current_staff = None

    try:
        current_staff = Staff.objects.get(username=request.user.username)
        my_salary_history = Expense.objects.filter(staff=current_staff).order_by('-date')
        my_attendance_history = StaffAttendance.objects.filter(staff=current_staff).order_by('-date')
    except Staff.DoesNotExist:
        pass 

    context = {
        'classes': classes,
        'students': students,
        'selected_class': selected_class,
        'today_date': timezone.now().date(),
        'current_staff': current_staff,
        'my_salary_history': my_salary_history,
        'my_attendance_history': my_attendance_history
    }
    return render(request, 'staff_dashboard.html', context)


# =========================================
# 4. REGISTRATION (ADMISSIONS)
# =========================================
@login_required
def admin_register(request):
    """ Register Student: Username = Mother Phone, Password = DOB """
    if request.method == 'POST':
        try:
            user_name = request.POST.get('mother_phone')
            dob_raw = request.POST.get('dob')
            
            # Generate Password DDMMYYYY
            dob_obj = datetime.strptime(dob_raw, '%Y-%m-%d')
            pass_word = dob_obj.strftime('%d%m%Y')

            if User.objects.filter(username=user_name).exists():
                messages.error(request, f"Phone Number {user_name} is already registered!")
                return redirect('admin_register')

            User.objects.create_user(username=user_name, password=pass_word)

            student = Student(
                application_number=request.POST['application_number'],
                student_name=request.POST['student_name'],
                gender=request.POST['gender'],
                dob=dob_raw,
                aadhar_number=request.POST['aadhar_number'],
                class_admitted=request.POST['class_admitted'],
                academic_year=request.POST['academic_year'],
                father_name=request.POST['father_name'],
                father_phone=request.POST['father_phone'],
                mother_name=request.POST['mother_name'],
                mother_phone=request.POST['mother_phone'],
                address=request.POST['address'],
                username=user_name,
                password=pass_word
            )
            student.save()
            messages.success(request, f"Student Registered! Login: {user_name}, Pass: {pass_word}")
            return redirect('manage_students')
            
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    return render(request, 'admin_register.html')

@login_required
def staff_registration(request):
    """ Register Staff: Username = Phone, Password = DOB """
    if request.method == 'POST':
        try:
            user_name = request.POST.get('phone_number') 
            dob_raw = request.POST.get('dob')

            if not user_name:
                messages.error(request, "Error: Phone Number is required.")
                return redirect('staff_registration')

            if dob_raw:
                dob_obj = datetime.strptime(dob_raw, '%Y-%m-%d')
                pass_word = dob_obj.strftime('%d%m%Y')
            else:
                pass_word = "123456"

            if User.objects.filter(username=user_name).exists():
                messages.error(request, f"Error: Phone Number {user_name} is already registered!")
                return redirect('staff_registration')

            new_user = User.objects.create_user(username=user_name, password=pass_word)
            staff_group, _ = Group.objects.get_or_create(name='Staff')
            new_user.groups.add(staff_group)

            staff = Staff(
                full_name=request.POST['full_name'],
                gender=request.POST['gender'],
                phone_number=user_name,
                aadhar_number=request.POST.get('aadhar_number', ''),
                recruitment_date=request.POST['recruitment_date'],
                address=request.POST.get('address', ''),
                dob=dob_raw,
                designation=request.POST.get('designation'),
                username=user_name
            )
            staff.save()
            messages.success(request, f"Staff Registered! Login: {user_name}, Pass: {pass_word}")
            return redirect('manage_staff')

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'staff_register.html')


# =========================================
# 5. ADMISSIONS CALCULATOR
# =========================================
@login_required
def admissions_calculator(request):
    """ Checks age on June 1st of Academic Year """
    result = None
    selected_year = None
    dob_input = None
    
    ACADEMIC_YEARS = [('2026-27', '2026'), ('2027-28', '2027'), ('2028-29', '2028'), ('2029-30', '2029'), ('2030-31', '2030')]

    if request.method == 'POST':
        try:
            year_start = request.POST.get('academic_year')
            dob_str = request.POST.get('dob')
            
            if year_start and dob_str:
                reference_date = date(int(year_start), 6, 1) 
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                
                age_years = reference_date.year - dob.year - ((reference_date.month, reference_date.day) < (dob.month, dob.day))
                
                if reference_date.month >= dob.month:
                    age_months = reference_date.month - dob.month
                else:
                    age_months = 12 - (dob.month - reference_date.month)
                    if reference_date.day < dob.day: age_months -= 1

                # Logic: Day Care -> UKG Only
                eligible_class = "Underage"
                color = "secondary"
                
                if age_years >= 6:
                    eligible_class = "Age limit exceeded (6+ Years)"
                    color = "danger"
                elif age_years == 5:
                    eligible_class = "UKG"
                    color = "success"
                elif age_years == 4:
                    eligible_class = "LKG"
                    color = "info"
                elif age_years == 3:
                    eligible_class = "Pre-KG"
                    color = "warning"
                elif age_years == 2:
                    eligible_class = "Play Group"
                    color = "warning"
                elif age_years == 1:
                    eligible_class = "Day Care"
                    color = "primary"
                else:
                    eligible_class = "Infant (Too Young)"

                result = {
                    'age_years': age_years,
                    'age_months': age_months,
                    'eligible_class': eligible_class,
                    'color': color,
                    'reference_date_display': reference_date.strftime('%B 1st, %Y')
                }
                selected_year = year_start
                dob_input = dob_str

        except Exception as e:
            messages.error(request, f"Calculation Error: {e}")

    return render(request, 'admissions_calculator.html', {
        'academic_years': ACADEMIC_YEARS,
        'result': result,
        'selected_year': selected_year,
        'dob_input': dob_input
    })


# =========================================
# 6. MANAGEMENT & ACTIONS (Edit/Delete)
# =========================================
@login_required
def manage_students(request):
    student_list = Student.objects.all().order_by('-id')
    return render(request, 'manage_students.html', {'student_list': student_list})

@login_required
def manage_staff(request):
    staff_list = Staff.objects.all().order_by('-id')
    return render(request, 'manage_staff.html', {'staff_list': staff_list})

@login_required
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        try:
            student.student_name = request.POST.get('student_name')
            student.class_admitted = request.POST.get('class_admitted')
            student.father_name = request.POST.get('father_name')
            student.father_phone = request.POST.get('father_phone')
            student.save()
            messages.success(request, "Updated successfully!")
            return redirect('manage_students')
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, 'edit_student.html', {'student': student})

@login_required
def delete_student(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id)
        if student.username:
            try:
                user = User.objects.get(username=student.username)
                user.delete()
            except User.DoesNotExist: pass
        student.delete()
        messages.success(request, "Deleted successfully.")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect('manage_students')

@login_required
def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    if request.method == 'POST':
        try:
            staff.full_name = request.POST.get('full_name')
            staff.phone_number = request.POST.get('phone_number')
            staff.gender = request.POST.get('gender')
            staff.address = request.POST.get('address')
            staff.save()
            messages.success(request, "Updated successfully!")
            return redirect('manage_staff')
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, 'edit_staff.html', {'staff': staff})

@login_required
def delete_staff(request, staff_id):
    try:
        staff = get_object_or_404(Staff, id=staff_id)
        staff.delete()
        messages.success(request, "Removed successfully.")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return redirect('manage_staff')


# =========================================
# 7. ATTENDANCE MODULE
# =========================================
@login_required
def mark_attendance(request):
    classes = Student.objects.values_list('class_admitted', flat=True).distinct()
    selected_class = request.GET.get('class_selected')
    students = []
    
    if selected_class:
        students = Student.objects.filter(class_admitted=selected_class).order_by('student_name')

    if request.method == 'POST':
        attendance_date = request.POST.get('attendance_date')
        selected_class = request.POST.get('class_selected')
        students_to_mark = Student.objects.filter(class_admitted=selected_class)
        
        for student in students_to_mark:
            status = request.POST.get(f'status_{student.id}') 
            if status:
                Attendance.objects.update_or_create(
                    student=student,
                    date=attendance_date,
                    defaults={'status': status}
                )
        messages.success(request, f"Attendance marked for {selected_class} on {attendance_date}")
        return redirect('attendance_analytics')

    return render(request, 'mark_attendance.html', {
        'classes': classes,
        'students': students,
        'selected_class': selected_class,
        'today_date': timezone.now().date()
    })

@login_required
def admin_staff_attendance(request):
    staff_list = Staff.objects.all().order_by('full_name')
    if request.method == 'POST':
        attendance_date = request.POST.get('attendance_date') or timezone.now().date()
        for staff in staff_list:
            status = request.POST.get(f'status_{staff.id}')
            if status:
                StaffAttendance.objects.update_or_create(
                    staff=staff,
                    date=attendance_date,
                    defaults={'status': status}
                )
        messages.success(request, f"Staff Attendance marked successfully for {attendance_date}!")
        return redirect('super_dashboard')

    return render(request, 'admin_staff_attendance.html', {
        'staff_list': staff_list,
        'today_date': timezone.now().date()
    })

@login_required
def attendance_analytics(request):
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    else:
        selected_date = timezone.now().date()

    classes = Student.objects.values_list('class_admitted', flat=True).distinct()
    class_data = []
    total_school_students = 0
    total_present_count = 0

    for class_name in classes:
        students_in_class = Student.objects.filter(class_admitted=class_name)
        total_students = students_in_class.count()

        if total_students > 0:
            present = Attendance.objects.filter(student__in=students_in_class, date=selected_date, status='Present').count()
            absent = Attendance.objects.filter(student__in=students_in_class, date=selected_date, status='Absent').count()
            leave = Attendance.objects.filter(student__in=students_in_class, date=selected_date, status='Leave').count()

            records_exist = (present + absent + leave) > 0
            percentage = round((present / total_students) * 100, 1) if records_exist else 0

            total_school_students += total_students
            total_present_count += present

            class_data.append({
                'class_name': class_name,
                'total_students': total_students,
                'present': present,
                'absent': absent,
                'leave': leave,
                'percentage': percentage,
                'status': 'Taken' if records_exist else 'Pending'
            })

    school_percentage = round((total_present_count / total_school_students) * 100, 1) if total_school_students > 0 else 0

    context = {
        'selected_date': selected_date,
        'class_data': class_data,
        'school_percentage': school_percentage,
        'total_school_students': total_school_students,
        'present_today': total_present_count,
        'absent_today': total_school_students - total_present_count
    }
    return render(request, 'attendance_analytics.html', context)


# =========================================
# 8. FINANCIAL MODULE (Funds & Fees)
# =========================================
@login_required
def manage_funds(request):
    staff_members = Staff.objects.all()

    if request.method == 'POST':
        staff_id = request.POST.get('staff_id') 
        selected_staff = Staff.objects.get(id=staff_id) if staff_id else None

        Expense.objects.create(
            date=request.POST.get('date'),
            purpose=request.POST.get('purpose'),
            category=request.POST.get('category'),
            amount=request.POST.get('amount'),
            payment_type=request.POST.get('payment_type'),
            added_by=request.user,
            staff=selected_staff
        )
        messages.success(request, "Expense/Salary recorded successfully!")
        return redirect('manage_funds')

    total_target = StudentFee.objects.aggregate(sum=Sum('total_amount'))['sum'] or 0
    total_collected = FeeTransaction.objects.aggregate(sum=Sum('amount_paid'))['sum'] or 0
    total_utilized = Expense.objects.aggregate(sum=Sum('amount'))['sum'] or 0
    current_available = total_collected - total_utilized
    recent_expenses = Expense.objects.all().order_by('-date')

    context = {
        'total_target': total_target,
        'total_collected': total_collected,
        'total_utilized': total_utilized,
        'current_available': current_available,
        'recent_expenses': recent_expenses,
        'today_date': timezone.now().date(),
        'staff_members': staff_members
    }
    return render(request, 'manage_funds.html', context)

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    messages.success(request, "Expense record deleted.")
    return redirect('manage_funds')

@login_required
def financial_analytics(request):
    total_expected = StudentFee.objects.aggregate(sum=Sum('total_amount'))['sum'] or 0
    total_collected = FeeTransaction.objects.aggregate(sum=Sum('amount_paid'))['sum'] or 0
    total_pending = total_expected - total_collected

    collection_percentage = round((total_collected / total_expected) * 100, 1) if total_expected > 0 else 0

    all_fees = StudentFee.objects.all()
    total_invoices = all_fees.count()
    fully_paid_count = sum(1 for fee in all_fees if fee.get_balance() <= 0)
    unpaid_count = total_invoices - fully_paid_count

    context = {
        'total_expected': total_expected,
        'total_collected': total_collected,
        'total_pending': total_pending,
        'collection_percentage': collection_percentage,
        'total_invoices': total_invoices,
        'fully_paid_count': fully_paid_count,
        'unpaid_count': unpaid_count,
    }
    return render(request, 'financial_analytics.html', context)


# =========================================
# 9. FEE ACTIONS
# =========================================
@login_required
def fee_dashboard_hub(request):
    students = Student.objects.all().order_by('class_admitted', 'student_name')
    return render(request, 'fees/fee_hub.html', {'students': students})

@login_required
def student_fee_details(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    fees = StudentFee.objects.filter(student=student)
    return render(request, 'fees/student_fee_details.html', {'student': student, 'fees': fees})

@login_required
def add_fee_structure(request, student_id):
    if request.method == "POST":
        student = get_object_or_404(Student, id=student_id)
        StudentFee.objects.create(
            student=student,
            fee_name=request.POST.get('fee_name'),
            total_amount=request.POST.get('total_amount')
        )
        messages.success(request, "Fee Structure Added Successfully!")
        return redirect('student_fee_details', student_id=student_id)

@login_required
def add_fee_payment(request, fee_id):
    if request.method == "POST":
        fee_record = get_object_or_404(StudentFee, id=fee_id)
        FeeTransaction.objects.create(
            student_fee=fee_record,
            amount_paid=request.POST.get('amount_paid'),
            payment_date=request.POST.get('payment_date'),
            remarks=request.POST.get('remarks')
        )
        messages.success(request, "Payment Recorded Successfully!")
        return redirect('student_fee_details', student_id=fee_record.student.id)

@login_required
def edit_fee_structure(request, fee_id):
    fee = get_object_or_404(StudentFee, id=fee_id)
    if request.method == 'POST':
        fee.fee_name = request.POST.get('fee_name')
        fee.total_amount = request.POST.get('total_amount')
        fee.save()
        messages.success(request, "Fee Record Updated Successfully!")
        return redirect('student_fee_details', student_id=fee.student.id)
    return render(request, 'fees/edit_fee.html', {'fee': fee})

@login_required
def delete_fee_structure(request, fee_id):
    fee = get_object_or_404(StudentFee, id=fee_id)
    student_id = fee.student.id
    fee.delete()
    messages.success(request, "Fee Record Deleted Successfully.")
    return redirect('student_fee_details', student_id=student_id)


# =========================================
# 10. DOWNLOADS & CSV REPORTS
# =========================================
@login_required
def download_students_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_list.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Class', 'Parent Phone', 'DOB', 'Gender', 'Address'])
    for student in Student.objects.all():
        writer.writerow([
            student.application_number, student.student_name, student.class_admitted,
            student.mother_phone, student.dob, student.gender, student.address
        ])
    return response

@login_required
def download_staff_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="staff_list.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Designation', 'Phone', 'Recruited On', 'Gender'])
    for staff in Staff.objects.all():
        writer.writerow([
            staff.full_name, staff.designation, staff.phone_number,
            staff.recruitment_date, staff.gender
        ])
    return response

@login_required
def download_funds_csv(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Purpose', 'Type', 'Amount', 'Payment Mode', 'Staff Linked'])

    mode = request.GET.get('mode')
    expenses = []
    filename = "Financial_Report.csv"

    if mode == 'date':
        date_param = request.GET.get('date')
        if date_param:
            expenses = Expense.objects.filter(date=date_param).order_by('category')
            filename = f"Financial_Report_Daily_{date_param}.csv"
    elif mode == 'month':
        month_param = request.GET.get('month')
        if month_param:
            year, month = month_param.split('-')
            expenses = Expense.objects.filter(date__year=year, date__month=month).order_by('date')
            filename = f"Financial_Report_Monthly_{month_param}.csv"
    else:
        expenses = Expense.objects.all().order_by('-date')
        filename = "Financial_Report_Full_History.csv"

    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    if expenses:
        for expense in expenses:
            type_label = "Salary" if expense.category == 'Salary' else "Expense"
            staff_name = expense.staff.full_name if expense.staff else "-"
            writer.writerow([
                expense.date, expense.category, expense.purpose, type_label,
                expense.amount, expense.payment_type, staff_name
            ])
    else:
        writer.writerow(["No records found."])
    return response

@login_required
def download_fee_data_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fee_collection_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Student Name', 'Fee Type', 'Amount Paid', 'Mode/Remarks'])
    for txn in FeeTransaction.objects.all().order_by('-payment_date'):
        writer.writerow([
            txn.payment_date, txn.student_fee.student.student_name,
            txn.student_fee.fee_name, txn.amount_paid, txn.remarks
        ])
    return response

@login_required
def download_attendance_report(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Date', 'Class', 'Student Name', 'Status'])

    mode = request.GET.get('mode')
    logs = []
    filename = "attendance_report.csv"

    if mode == 'date':
        date_param = request.GET.get('date')
        if date_param:
            logs = Attendance.objects.filter(date=date_param).order_by('student__class_admitted', 'student__student_name')
            filename = f"Attendance_Daily_{date_param}.csv"
    elif mode == 'month':
        month_param = request.GET.get('month')
        if month_param:
            year, month = month_param.split('-')
            logs = Attendance.objects.filter(date__year=year, date__month=month).order_by('date', 'student__class_admitted')
            filename = f"Attendance_Monthly_{month_param}.csv"
    else:
        logs = Attendance.objects.all().order_by('-date')

    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    if logs:
        for log in logs:
            writer.writerow([log.date, log.student.class_admitted, log.student.student_name, log.status])
    else:
        writer.writerow(["No records found."])
    return response

@login_required
def download_all_attendance_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="school_attendance_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Class', 'Student Name', 'Status'])
    logs = Attendance.objects.all().order_by('-date', 'student__class_admitted', 'student__student_name')
    for log in logs:
        writer.writerow([log.date, log.student.class_admitted, log.student.student_name, log.status])
    return response

@login_required
def download_my_child_attendance(request):
    try:
        student = Student.objects.get(username=request.user.username)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{student.student_name}_attendance.csv"'
        writer = csv.writer(response)
        writer.writerow(['Date', 'Status'])
        logs = Attendance.objects.filter(student=student).order_by('-date')
        for log in logs:
            writer.writerow([log.date, log.status])
        return response
    except:
        return redirect('dashboard')