from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, EmailOTP


@api_view(['POST'])
@permission_classes([AllowAny])
def request_email_otp(request):
    """
    Step 1 of Amazon-style Auth: User enters email (and optional full_name/password for signup).
    Sends a 6-digit OTP code to their email.
    """
    email = request.data.get('email', '').strip().lower()
    purpose = request.data.get('purpose', 'LOGIN').upper()  # 'SIGNUP' or 'LOGIN'

    if not email or '@' not in email:
        return Response({"error": "Please enter a valid email address."}, status=status.HTTP_400_BAD_REQUEST)

    user_exists = CustomUser.objects.filter(email=email).exists()
    if purpose == 'SIGNUP' and user_exists:
        return Response({"error": "An account with this email already exists. Please Sign In."}, status=status.HTTP_400_BAD_REQUEST)
    if purpose == 'LOGIN' and not user_exists:
        return Response({"error": "No account found with this email. Please Create an Account first."}, status=status.HTTP_404_NOT_FOUND)

    otp_obj = EmailOTP.generate_otp(email=email, purpose=purpose)

    send_mail(
        subject=f"NexCart Verification Code: {otp_obj.code}",
        message=(
            f"Hello,\n\n"
            f"Your 6-digit NexCart verification code is: {otp_obj.code}\n"
            f"This code expires in 10 minutes.\n\n"
            f"If you did not request this, please ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({
        "message": f"Verification OTP sent to {email}. Check your inbox (or server console in dev mode).",
        "email": email
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_otp(request):
    """
    Step 2 of Auth: Verifies the 6-digit OTP, creates/verifies the user, and returns JWT tokens.
    """
    email = request.data.get('email', '').strip().lower()
    code = request.data.get('code', '').strip()
    full_name = request.data.get('full_name', '').strip()
    password = request.data.get('password', '')

    otp_record = EmailOTP.objects.filter(email=email, code=code, is_used=False).order_by('-created_at').first()
    if not otp_record or not otp_record.is_valid():
        return Response({"error": "Invalid or expired OTP code."}, status=status.HTTP_400_BAD_REQUEST)

    otp_record.is_used = True
    otp_record.save(update_fields=['is_used'])

    user, created = CustomUser.objects.get_or_create(
        email=email,
        defaults={'full_name': full_name or email.split('@')[0].title(), 'is_verified': True}
    )
    if created and password:
        user.set_password(password)
    user.is_verified = True
    user.save()

    refresh = RefreshToken.for_user(user)
    return Response({
        "message": "Authentication successful!",
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "default_address": user.default_address,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_login(request):
    """
    Standard Email + Password Sign-In option alongside Passwordless OTP Sign-In.
    """
    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    user = CustomUser.objects.filter(email=email).first()
    if not user or not user.check_password(password):
        return Response({"error": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "default_address": user.default_address,
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    u = request.user
    return Response({
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "default_address": u.default_address,
    })