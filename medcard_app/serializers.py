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
        fields = ['user', 'patient_fullname', 'patient_birthdate', 'patient_phone', 'patient_gender']
        extra_kwargs = {
            'patient_fullname': {'help_text': 'Full name of the patient.'},
            'patient_birthdate': {'help_text': 'Birthdate of the patient (YYYY-MM-DD).'},
            'patient_phone': {'help_text': 'Contact phone number of the patient.'},
            'patient_gender': {'help_text': 'Gender of the patient.'}
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
