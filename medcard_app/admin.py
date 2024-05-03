from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['patient_fullname', 'patient_birthdate', 'patient_phone', 'patient_gender']


@admin.register(EmailVerification)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'verified']
