from django.db import models
from django.contrib.auth.models import User 
from django.core.validators import RegexValidator
from django.db import models
from datetime import timedelta
from django.utils import timezone


phone_number_validator = RegexValidator(
    regex=r'^[6-9]{1}[0-9]{9}$',  # Starts with digits 6-9 followed by 9 digits
    message="Enter a valid 10-digit phone number starting with a digit between 6 and 9."
)
validate_4_digit_otp = RegexValidator(
    regex=r'^\d{4}$',
    message="Enter a valid 4-digit OTP."
)
pan_validator = RegexValidator(
    regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$',
    message="Enter a valid PAN number (e.g., ABCDE1234F)."
)
email_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9._\-\+]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    message="Enter a valid email address."
)


class UserDetails(models.Model):
    user_profile = models.OneToOneField(User, on_delete=models.CASCADE ,related_name="user_details") 
    date_of_birth = models.DateField(default=None)
    user_status = models.BooleanField(default=False,blank=True)#login_status
    phone_number = models.CharField(max_length=10, validators=[phone_number_validator],unique=True)

    def __str__(self): 
        return self.user_profile.username


class OTPVerification(models.Model):
    phone_number = models.ForeignKey(UserDetails, on_delete=models.CASCADE, related_name="otp_verifications")
    otp = models.CharField(max_length=4, validators=[validate_4_digit_otp])
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
   

    def __str__(self):
        return f"OTP for {self.phone_number.phone_number}"
