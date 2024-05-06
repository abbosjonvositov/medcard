from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class PatientProfile(models.Model):
    patient_username = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Username')
    patient_fullname = models.TextField(max_length=20, verbose_name='Patient Fullname')
    patient_birthdate = models.DateField(verbose_name='Date of birth')
    patient_phone = models.CharField(max_length=11, verbose_name='Patient Contact')
    patient_gender = models.TextField(max_length=10, verbose_name='Patient Gender')
    patient_address = models.CharField(max_length=200, verbose_name='Patient Addresss')

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


class DoctorSpeciality(models.Model):
    speciality_name = models.CharField(max_length=200, verbose_name='Specialty Name')

    class Meta:
        verbose_name = "Doctor Specialty"
        verbose_name_plural = "Doctor Specialties"
        ordering = ['speciality_name']

    def __str__(self):
        return self.speciality_name


class Clinics(models.Model):
    clinic_name = models.CharField(max_length=200, verbose_name='Clinic Name')
    contacts = models.CharField(max_length=200, verbose_name='Contacts')
    address = models.CharField(max_length=200, verbose_name='Address')
    clinic_location = models.CharField(max_length=200, verbose_name='Clinic Location')

    class Meta:
        verbose_name = "Clinic"
        verbose_name_plural = "Clinics"
        ordering = ['clinic_name']

    def __str__(self):
        return self.clinic_name


class Doctors(models.Model):
    clinic = models.ForeignKey(Clinics, on_delete=models.CASCADE, verbose_name='Clinic')
    doctor_username = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Username')
    doctor_fullname = models.CharField(max_length=200, verbose_name='Full Name')
    doctor_birthdate = models.DateField(verbose_name='Date of Birth')
    doctor_phone = models.CharField(max_length=11, verbose_name='Contact Phone')
    doctor_license_no = models.CharField(max_length=200, verbose_name='License Number')
    speciality_name = models.ForeignKey(DoctorSpeciality, on_delete=models.CASCADE, verbose_name='Specialty')

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
        ordering = ['doctor_fullname', 'speciality_name']

    def __str__(self):
        return f"{self.doctor_fullname} ({self.speciality_name})"


class DoctorReview(models.Model):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE, verbose_name='Doctor')
    rating = models.IntegerField(verbose_name='Rating of Doctor')
    review = models.CharField(max_length=300, verbose_name='Review')

    class Meta:
        verbose_name = "Doctor Review"
        verbose_name_plural = "Doctor Reviews"
        ordering = ['doctor']

    def __str__(self):
        return f"{self.doctor.doctor_fullname} - Review"


class DoctorWorkExperience(models.Model):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE, verbose_name='Doctor')
    place_of_experience = models.CharField(max_length=200, verbose_name='Place of experience')
    start_year = models.DateField(verbose_name='Start Date')
    end_year = models.DateField(verbose_name='End Date')
    position = models.CharField(max_length=200, verbose_name='Position Held')
    description = models.TextField(blank=True, verbose_name='Description of Duties')

    class Meta:
        verbose_name = "Doctor Work Experience"
        verbose_name_plural = "Doctor Work Experiences"
        ordering = ['-start_year', '-end_year', 'doctor']

    def __str__(self):
        return f"{self.position} ({self.start_year.year} to {self.end_year.year})"


class DoctorQualification(models.Model):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE, verbose_name='Doctor')
    qualification = models.CharField(max_length=300, verbose_name='Qualification')
    institution = models.CharField(max_length=300, verbose_name='Institution')
    year_obtained = models.DateField(verbose_name='Year Obtained')

    class Meta:
        verbose_name = "Doctor Qualification"
        verbose_name_plural = "Doctor Qualifications"
        ordering = ['year_obtained']

    def __str__(self):
        return f"{self.qualification} ({self.year_obtained.year})"


class DoctorAvailability(models.Model):
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE, related_name='availabilities', verbose_name='Doctor')
    day_of_week = models.IntegerField(choices=[(i, day) for i, day in enumerate(
        ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], start=1)],
                                      verbose_name='Day of the Week')
    start_time = models.TimeField(verbose_name='Start Time')
    end_time = models.TimeField(verbose_name='End Time')

    class Meta:
        verbose_name = "Doctor Availability"
        verbose_name_plural = "Doctor Availabilities"
        ordering = ['doctor', 'day_of_week', 'start_time']
        constraints = [
            models.UniqueConstraint(fields=['doctor', 'day_of_week', 'start_time'], name='unique_doctor_availability')
        ]

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')} to {self.end_time.strftime('%H:%M')}"


class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments', verbose_name='Patient')
    doctor = models.ForeignKey(Doctors, on_delete=models.CASCADE, related_name='appointments', verbose_name='Doctor')
    date = models.DateField(verbose_name='Date of Appointment')
    start_time = models.TimeField(verbose_name='Start Time')
    end_time = models.TimeField(verbose_name='End Time')
    status = models.CharField(max_length=100, choices=[('scheduled', 'Scheduled'), ('cancelled', 'Cancelled'),
                                                       ('completed', 'Completed')], default='scheduled',
                              verbose_name='Status')

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ['date', 'start_time', 'doctor']
        constraints = [
            models.CheckConstraint(check=models.Q(end_time__gt=models.F('start_time')),
                                   name='appointment_end_time_must_be_after_start_time')
        ]

    def __str__(self):
        return f"{self.date} at {self.start_time.strftime('%H:%M')}"
