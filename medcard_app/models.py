from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class PatientProfile(models.Model):
    patient_username = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Username')
    patient_fullname = models.TextField(max_length=20, verbose_name='Patient Fullname')
    patient_birthdate = models.DateField(verbose_name='Date of birth')
    patient_phone = models.CharField(max_length=11, verbose_name='Contact')
    patient_gender = models.TextField(max_length=10, verbose_name='Patient Gender')

    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'


class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Email'
        verbose_name_plural = 'Emails'
