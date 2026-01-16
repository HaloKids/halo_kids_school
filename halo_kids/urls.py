from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from school import views

urlpatterns = [
    # =========================================
    # 1. CORE & AUTHENTICATION
    # =========================================
    path('admin/', admin.site.urls),
    
    # --- CHANGED: Default page is now Landing, Home is moved to '/home' ---
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    
    # Login / Logout / Redirect Logic
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('smart-redirect/', views.smart_redirect, name='smart_redirect'),

    # =========================================
    # 2. DASHBOARDS
    # =========================================
    path('super-admin/', views.super_dashboard, name='super_dashboard'), # Super Admin Hub
    path('staff/', views.staff_dashboard, name='staff_dashboard'),       # Teacher Zone
    path('dashboard/', views.dashboard, name='dashboard'),               # Parent/Student Zone

    # =========================================
    # 3. ANALYTICS & TOOLS
    # =========================================
    path('analytics/financial/', views.financial_analytics, name='financial_analytics'),
    path('analytics/attendance/', views.attendance_analytics, name='attendance_analytics'),
    path('admissions/calculator/', views.admissions_calculator, name='admissions_calculator'), # Age Checker

    # =========================================
    # 4. REGISTRATION (ADMISSIONS)
    # =========================================
    path('register/student/', views.admin_register, name='admin_register'),
    path('register/staff/', views.staff_registration, name='staff_registration'),

    # =========================================
    # 5. MANAGEMENT LISTS (VIEW DATA)
    # =========================================
    path('manage/students/', views.manage_students, name='manage_students'),
    path('manage/staff/', views.manage_staff, name='manage_staff'),

    # =========================================
    # 6. EDIT & DELETE ACTIONS (STUDENTS/STAFF)
    # =========================================
    path('student/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('student/delete/<int:student_id>/', views.delete_student, name='delete_student'),
    
    path('staff/edit/<int:staff_id>/', views.edit_staff, name='edit_staff'),
    path('staff/delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),

    # =========================================
    # 7. ATTENDANCE MODULE
    # =========================================
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),        # For Student Attendance
    path('admin-staff-attendance/', views.admin_staff_attendance, name='admin_staff_attendance'), # For Staff Attendance

    # =========================================
    # 8. FEES & PAYMENTS MODULE
    # =========================================
    path('fees/', views.fee_dashboard_hub, name='fee_dashboard_hub'),
    path('fees/student/<int:student_id>/', views.student_fee_details, name='student_fee_details'),
    path('fees/add_structure/<int:student_id>/', views.add_fee_structure, name='add_fee_structure'),
    path('fees/add_payment/<int:fee_id>/', views.add_fee_payment, name='add_fee_payment'),
    
    # Fee Edit/Delete
    path('fees/edit/<int:fee_id>/', views.edit_fee_structure, name='edit_fee_structure'),
    path('fees/delete/<int:fee_id>/', views.delete_fee_structure, name='delete_fee_structure'),

    # =========================================
    # 9. FINANCE (FUNDS & EXPENSES)
    # =========================================
    path('funds/', views.manage_funds, name='manage_funds'),
    path('funds/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),

    # =========================================
    # 10. DOWNLOADS & REPORTS (CSV)
    # =========================================
    path('download/students/', views.download_students_csv, name='download_students_csv'),
    path('download/staff/', views.download_staff_csv, name='download_staff_csv'),
    path('download/funds/', views.download_funds_csv, name='download_funds_csv'),
    path('download/fees/', views.download_fee_data_csv, name='download_fee_data_csv'),
    
    # Attendance Downloads
    path('download/attendance/', views.download_attendance_report, name='download_attendance_report'), # Smart Date/Month Download
    path('download/my-attendance/', views.download_my_child_attendance, name='download_my_child_attendance'), # For Parents
]