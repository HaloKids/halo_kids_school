from django import forms
from django.contrib.auth.models import User
# Note: Ensure these models exist in your models.py
from .models import Student, Attendance, Fee, StaffAttendance

# =========================================
# 1. ATTENDANCE FORMS
# =========================================

class AttendanceForm(forms.ModelForm):
    """ Used for marking Student Attendance """
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}), 
        }

class StaffAttendanceForm(forms.ModelForm):
    """ Used for marking Staff Attendance """
    class Meta:
        model = StaffAttendance
        fields = ['staff', 'status', 'date']
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }


# =========================================
# 2. FINANCE FORMS
# =========================================

class FeeForm(forms.ModelForm):
    """ Used for adding Fee structures/records """
    class Meta:
        model = Fee
        fields = ['student', 'title', 'amount', 'date', 'payment_status', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Term 1 Fee'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


# =========================================
# 3. STAFF AUTHENTICATION FORMS
# =========================================

class StaffSignUpForm(forms.ModelForm):
    """ Used for registering new Staff members manually """
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


# =========================================
# 4. STUDENT / PARENT PLACEHOLDERS
# =========================================
# Note: Most logic for these is now handled directly in views.py 
# using manual HTML forms to support custom logic (like DOB passwords).

class ParentSignUpForm(forms.Form):
    pass 

class StudentRegistrationForm(forms.Form):
    pass

class StudentProfileForm(forms.ModelForm):
    """ Simple form for editing basic student details """
    class Meta:
        model = Student
        fields = ['student_name', 'class_admitted', 'academic_year']
        widgets = {
            'student_name': forms.TextInput(attrs={'class': 'form-control'}),
            'class_admitted': forms.Select(attrs={'class': 'form-select'}),
            'academic_year': forms.Select(attrs={'class': 'form-select'}),
        }