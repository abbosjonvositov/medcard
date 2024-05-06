from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['patient_fullname', 'patient_birthdate', 'patient_phone', 'patient_gender']


@admin.register(EmailVerification)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'verified']


@admin.register(Clinics)
class ClinicsAdmin(admin.ModelAdmin):
    list_display = ['clinic_name', 'contacts', 'address', 'clinic_location']


@admin.register(Doctors)
class DoctorsAdmin(admin.ModelAdmin):
    list_display = ['doctor_fullname', 'clinic', 'speciality_name', 'doctor_username', 'doctor_birthdate',
                    'doctor_phone', 'doctor_license_no']


@admin.register(DoctorQualification)
class DoctorsAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'qualification', 'institution', 'year_obtained']


@admin.register(DoctorWorkExperience)
class DoctorsAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'place_of_experience', 'start_year', 'end_year', 'position', 'description']


@admin.register(DoctorAvailability)
class DoctorsAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time']


@admin.register(DoctorSpeciality)
class DoctorsAdmin(admin.ModelAdmin):
    list_display = ['speciality_name']


@admin.register(Appointment)
class DoctorsAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date', 'start_time', 'end_time', 'status']


@admin.register(DoctorReview)
class DoctorsAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'rating', 'review']
