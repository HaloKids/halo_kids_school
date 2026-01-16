from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# =========================================
# 1. STUDENT MODEL
# =========================================
class Student(models.Model):
    # Personal Details
    application_number = models.CharField(max_length=20, unique=True)
    student_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    dob = models.DateField()
    aadhar_number = models.CharField(max_length=20, null=True, blank=True)
    
    # Academic Details
    class_admitted = models.CharField(max_length=50)
    academic_year = models.CharField(max_length=20)
    
    # Parent Details
    father_name = models.CharField(max_length=100)
    father_phone = models.CharField(max_length=15)
    mother_name = models.CharField(max_length=100)
    mother_phone = models.CharField(max_length=15)
    address = models.TextField()
    
    # Login Credentials (Stored for reference)
    username = models.CharField(max_length=100, null=True, blank=True) # Usually Mother's Phone
    password = models.CharField(max_length=100, null=True, blank=True) # Usually DOB (DDMMYYYY)

    def __str__(self):
        return self.student_name


# =========================================
# 2. STAFF MODEL
# =========================================
class Staff(models.Model):
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    phone_number = models.CharField(max_length=15)
    aadhar_number = models.CharField(max_length=20, null=True, blank=True)
    recruitment_date = models.DateField()
    address = models.TextField()
    
    # New Fields for Auth & Designation
    dob = models.DateField(null=True, blank=True)
    designation = models.CharField(max_length=100, default="Teacher")
    username = models.CharField(max_length=100, null=True, blank=True) # Usually Phone Number

    def __str__(self):
        return self.full_name


# =========================================
# 3. FEE MODELS (Structure & Transactions)
# =========================================
class StudentFee(models.Model):
    """
    Defines the 'Total Fee' a student is expected to pay.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    fee_name = models.CharField(max_length=100) # e.g. "Term 1 Fee"
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_paid(self):
        # Calculate sum of all transactions for this fee
        paid = self.feetransaction_set.aggregate(total=models.Sum('amount_paid'))['total']
        return paid if paid else 0

    def get_balance(self):
        return self.total_amount - self.get_total_paid()

    def get_payment_percentage(self):
        if self.total_amount == 0: return 0
        return (self.get_total_paid() / self.total_amount) * 100

    def __str__(self):
        return f"{self.fee_name} - {self.student.student_name}"

class FeeTransaction(models.Model):
    """
    Records individual payments made against a StudentFee.
    """
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    remarks = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.amount_paid} paid for {self.student_fee}"


# =========================================
# 4. ATTENDANCE MODELS
# =========================================
class Attendance(models.Model):
    """ Student Attendance """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Leave', 'Leave')])

    class Meta:
        unique_together = ('student', 'date') # Prevent duplicate attendance for same student on same day

    def __str__(self):
        return f"{self.student.student_name} - {self.date} - {self.status}"

class StaffAttendance(models.Model):
    """ Staff Attendance """
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Leave', 'Leave')
    ])

    def __str__(self):
        return f"{self.staff.full_name} - {self.date} - {self.status}"


# =========================================
# 5. EXPENSE MODEL (Finance)
# =========================================
class Expense(models.Model):
    """ Records all money going OUT (Salaries, Rent, etc.) """
    CATEGORY_CHOICES = [
        ('Salary', 'Salary'),
        ('Rent', 'Rent'),
        ('Stationery', 'Stationery'),
        ('Garments', 'Garments'),
        ('Trip', 'Trip/Events'),
        ('School Day', 'School Day'),
        ('Maintenance', 'Maintenance'),
        ('Other', 'Other'),
    ]

    date = models.DateField(default=timezone.now)
    purpose = models.CharField(max_length=200) # Description
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=50, choices=[('Cash', 'Cash'), ('UPI', 'UPI'), ('Bank Transfer', 'Bank Transfer')])
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    # Optional Link to Staff (Used if category is 'Salary')
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.purpose} - ₹{self.amount}"