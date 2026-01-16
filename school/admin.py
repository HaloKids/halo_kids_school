from django.contrib import admin
from .models import Student, Staff, StudentFee, FeeTransaction, Attendance

# 1. Register Student Table
class StudentAdmin(admin.ModelAdmin):
    # 'status' removed to prevent errors. We stick to fields we know exist.
    list_display = ('student_name', 'class_admitted', 'father_name', 'father_phone')
    search_fields = ('student_name', 'application_number')

admin.site.register(Student, StudentAdmin)

# 2. Register Staff Table
class StaffAdmin(admin.ModelAdmin):
    # 'designation' removed. We show recruitment date instead.
    list_display = ('full_name', 'phone_number', 'recruitment_date')
    search_fields = ('full_name', 'phone_number')

admin.site.register(Staff, StaffAdmin)

# 3. Register Other Tables
admin.site.register(StudentFee)
admin.site.register(FeeTransaction)
admin.site.register(Attendance)