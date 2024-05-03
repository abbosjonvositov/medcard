from django.shortcuts import render
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import random
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .models import EmailVerification
from .serializers import *
from drf_yasg import openapi
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist


# Create your views here.
class PatientSignupAPIView(APIView):
    @swagger_auto_schema(
        request_body=PatientProfileSerializer,
        responses={status.HTTP_201_CREATED: 'Signup data cached. Please verify your email.'}
    )
    def post(self, request):
        serializer = PatientProfileSerializer(data=request.data)
        if serializer.is_valid():
            # Extract validated data
            validated_data = serializer.validated_data

            # Generate a verification code
            verification_code = ''.join(random.choices('0123456789', k=4))

            # Serialize user data and patient profile data into a form suitable for caching
            user_data = validated_data.pop('user')  # separate the nested user data
            profile_data = validated_data  # remaining data is for the patient profile

            # Combine all necessary data for caching
            cache_data = {
                'user': user_data,  # user data includes username, password, and email
                'profile': profile_data,  # profile data includes all other patient details
                'code': verification_code
            }

            # Cache the data with a 30-minute timeout
            cache_key = f'verification_{user_data["email"]}'
            cache.set(cache_key, cache_data, timeout=1800)  # 1800 seconds = 30 minutes
            # Send verification email
            send_mail(
                'Verification Code',
                f'Your verification code is: {verification_code}. Use this code to complete your registration.',
                settings.EMAIL_HOST_USER,
                [user_data['email']],
                fail_silently=False,
            )

            return Response({'detail': 'Signup data cached. Please verify your email.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Verify user's email address using verification code.",
        request_body=EmailVerificationSerializer,
        responses={
            status.HTTP_200_OK: "Email verified successfully. Token and username returned.",
            status.HTTP_400_BAD_REQUEST: "Invalid verification code.",
            status.HTTP_404_NOT_FOUND: "Verification data not found."
        }
    )
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            code = serializer.validated_data['code']
            # Retrieve verification data from cache
            cached_data = cache.get(f'verification_{email}')
            # Check if the cached data exists and the code matches
            if cached_data and cached_data['code'] == code:
                try:
                    # Create the user
                    user_data = cached_data['user']
                    user = User.objects.create_user(**user_data)

                    # Create the patient profile
                    profile_data = cached_data['profile']
                    profile = PatientProfile.objects.create(patient_username=user, **profile_data)

                    # Remove verification data from cache
                    cache.delete(f'verification_{email}')

                    # Optionally record the email verification
                    EmailVerification.objects.create(user=user, code=code, verified=True)

                    # Generate or retrieve token for the user
                    token, created = Token.objects.get_or_create(user=user)

                    return Response({
                        'detail': 'Email verified successfully.',
                        'token': token.key,
                        'username': user.username
                    }, status=status.HTTP_200_OK)
                except IntegrityError as e:
                    return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'detail': 'Invalid verification code or data expired.'},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientRetrieveAPIView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Retrieve Patient Profile",
        operation_description="Retrieves a detailed patient profile along with associated user data based on the username.",
        responses={
            status.HTTP_200_OK: openapi.Response(description="Detailed patient profile data",
                                                 schema=PatientProfileRetrievalSerializer),
            status.HTTP_404_NOT_FOUND: openapi.Response(description="User not found or no associated patient profile"),
            status.HTTP_500_INTERNAL_SERVER_ERROR: openapi.Response(description="Internal Server Error")
        }
    )
    def get(self, request, username):
        # Simplify exception handling to focus on common cases
        try:
            user = User.objects.get(username=username)
            patient_profile = get_object_or_404(PatientProfile, patient_username=user)
            serializer = PatientProfileRetrievalSerializer(patient_profile)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except PatientProfile.DoesNotExist:
            return Response({"error": "No associated patient profile."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Log exception details here if needed
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
