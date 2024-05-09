from datetime import datetime, timedelta

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {
            'username': {'help_text': 'Unique username for the user.'},
            'password': {'help_text': 'Secure password for the user.', 'write_only': True},
            'email': {'help_text': 'Valid email address of the user.'}
        }


class PatientProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(help_text="User's account related information")  # Nested Serializer for User

    class Meta:
        model = PatientProfile
        fields = ['user', 'patient_fullname', 'patient_birthdate', 'patient_phone', 'patient_gender', 'patient_address']
        extra_kwargs = {
            'patient_fullname': {'help_text': 'Full name of the patient.'},
            'patient_birthdate': {'help_text': 'Birthdate of the patient (YYYY-MM-DD).'},
            'patient_phone': {'help_text': 'Contact phone number of the patient.'},
            'patient_gender': {'help_text': 'Gender of the patient.'},
            'patient_address': {'help_text': 'Patient address.'}
        }


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text="Email address of the user."
    )
    code = serializers.CharField(
        max_length=4,
        help_text="Verification code sent to the user's email."
    )


class UserRetrievalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class PatientProfileRetrievalSerializer(serializers.ModelSerializer):
    user = UserRetrievalSerializer(source='patient_username', read_only=True)  # Ensure this points to the correct field

    class Meta:
        model = PatientProfile
        fields = ['user', 'patient_fullname', 'patient_birthdate', 'patient_phone', 'patient_gender']
        extra_kwargs = {
            'patient_fullname': {'help_text': 'Full name of the patient.'},
            'patient_birthdate': {'help_text': 'Birthdate of the patient (YYYY-MM-DD).'},
            'patient_phone': {'help_text': 'Contact phone number of the patient.'},
            'patient_gender': {'help_text': 'Gender of the patient.'}
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']  # Email is the only field to update for User
        extra_kwargs = {
            'email': {'required': False, 'help_text': 'Valid email address of the user.'}
        }


class PatientProfileUpdateSerializer(serializers.ModelSerializer):
    patient_username = UserUpdateSerializer(required=False)  # Correctly remove the 'source' as it is redundant

    class Meta:
        model = PatientProfile
        fields = ['patient_username', 'patient_phone', 'patient_address']
        extra_kwargs = {
            'patient_phone': {'required': False, 'help_text': 'Contact phone number of the patient.'},
            'patient_address': {'required': False, 'help_text': 'Address of the patient'}
        }

    def update(self, instance, validated_data):
        user_data = validated_data.pop('patient_username', {})
        if user_data:
            user_serializer = UserUpdateSerializer(instance.patient_username, data=user_data, partial=True)
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class DoctorUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']  # Excluding password for security and relevance in read operations


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinics
        fields = ['clinic_name', 'contacts', 'address']


class DoctorSpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSpeciality
        fields = ['speciality_name']


class DoctorReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorReview
        fields = ['rating', 'review']


class DoctorWorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorWorkExperience
        fields = ['place_of_experience', 'start_year', 'end_year', 'position', 'description']


class DoctorQualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorQualification
        fields = ['qualification', 'institution', 'year_obtained']


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    day_of_week = serializers.SerializerMethodField()

    class Meta:
        model = DoctorAvailability
        fields = ['day_of_week', 'start_time', 'end_time']

    def get_day_of_week(self, obj):
        days = {
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            7: "Sunday"
        }
        # Return the day name by looking up the dictionary with the day number
        return days.get(obj.day_of_week, "")


class DoctorSerializer(serializers.ModelSerializer):
    doctor_username = DoctorUserSerializer()  # Use the customized serializer without password
    clinic = ClinicSerializer()
    speciality_name = DoctorSpecialitySerializer()
    reviews = DoctorReviewSerializer(many=True, source='doctorreview_set', read_only=True)  # Default related name
    experiences = DoctorWorkExperienceSerializer(many=True, source='doctorworkexperience_set',
                                                 read_only=True)  # Default related name
    qualifications = DoctorQualificationSerializer(many=True, source='doctorqualification_set',
                                                   read_only=True)  # Default related name

    availabilities = DoctorAvailabilitySerializer(many=True, read_only=True)

    class Meta:
        model = Doctors
        fields = ['doctor_username', 'doctor_fullname', 'doctor_birthdate', 'doctor_phone', 'doctor_license_no',
                  'clinic', 'speciality_name', 'reviews', 'experiences', 'qualifications', 'availabilities']


class ClinicListSerializer(serializers.ModelSerializer):
    doctors = DoctorSerializer(many=True,
                               source='doctors_set')  # Adjust 'doctors_set' based on related_name if specified

    class Meta:
        model = Clinics
        fields = ['clinic_name', 'contacts', 'address', 'doctors']


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'date', 'start_time', 'end_time', 'status']
        read_only_fields = ['patient']
        extra_kwargs = {
            'doctor': {'help_text': 'ID of the doctor associated with the appointment.'},
            'date': {'help_text': 'Date of the appointment (YYYY-MM-DD).'},
            'start_time': {
                'help_text': 'Start time of the appointment (formatted as HH:MM, 24-hour clock).'
            },
            'end_time': {
                'help_text': 'End time of the appointment (formatted as HH:MM, 24-hour clock).'
            },
            'status': {'help_text': 'Status of the appointment (scheduled, cancelled, completed).'}
        }

    def validate(self, data):
        # Validate appointment time slots (30-minute intervals)
        start_time = datetime.combine(data['date'], data['start_time'])
        end_time = datetime.combine(data['date'], data['end_time'])
        if (end_time - start_time) != timedelta(minutes=30):
            raise serializers.ValidationError("Appointments must be exactly 30 minutes long.")

        # Check doctor's availability
        day_of_week = data['date'].weekday() + 1  # Monday is 1, Sunday is 7
        availabilities = DoctorAvailability.objects.filter(
            doctor=data['doctor'],
            day_of_week=day_of_week,
            start_time__lte=data['start_time'],
            end_time__gte=data['end_time']
        )
        if not availabilities.exists():
            raise serializers.ValidationError("No matching doctor availability for the selected time slot.")

        return data


class AppointmentDetailSerializer(serializers.ModelSerializer):
    patient = UserSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'doctor', 'date', 'start_time', 'end_time', 'status']
        extra_kwargs = {
            'date': {'help_text': 'Date of the appointment (YYYY-MM-DD).'},
            'start_time': {'help_text': 'Start time of the appointment (formatted as HH:MM, 24-hour clock).'},
            'end_time': {'help_text': 'End time of the appointment (formatted as HH:MM, 24-hour clock).'},
            'status': {'help_text': 'Status of the appointment (scheduled, cancelled, completed).'}
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        help_text="Username of the user."
    )
    password = serializers.CharField(
        max_length=128,
        help_text="Password of the user."
    )
