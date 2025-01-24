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

class District(models.Model): #Master table for District
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class LicenseCategory(models.Model): #Master table for Licensecat
    category = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.category


class LicenseDetails(models.Model):
    user_profile = models.OneToOneField(User, on_delete=models.CASCADE, related_name='license_details')  
    license_number = models.CharField(max_length=50, unique=True)
    district_name = models.ForeignKey(District, on_delete=models.CASCADE, related_name='licenses')
    licensee_name = models.CharField(max_length=100)
    establishment_name = models.CharField(max_length=100)
    license_category = models.ForeignKey(LicenseCategory, on_delete=models.CASCADE , related_name='licenses')
    license_type = models.CharField(max_length=50)
    license_nature = models.CharField(max_length=50)
    yearly_license_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"License {self.license_number} for {self.user_profile.username}"
    


class MGQDetails(models.Model):
    license_details = models.OneToOneField(LicenseDetails, on_delete=models.CASCADE, related_name='mgq_details') 
    MGQ_in_BL = models.DecimalField(max_digits=10, decimal_places=2)
    MGQ_in_LPL = models.DecimalField(max_digits=10, decimal_places=2)
    MGQ_in_Quintal = models.DecimalField(max_digits=10, decimal_places=2)
    deck_capacity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"MGQ Details for {self.license_details.license_number}"


class AddressDetails(models.Model):
    license_details = models.OneToOneField(LicenseDetails, on_delete=models.CASCADE, related_name='address_details')  
    police_station = models.CharField(max_length=100)
    excise_sub_division = models.CharField(max_length=100)
    ward = models.CharField(max_length=100, blank=True, null=True)
    site_address = models.TextField()
    land_details = models.TextField(blank=True, null=True)
    block = models.CharField(max_length=100, blank=True, null=True)
    road = models.CharField(max_length=100, blank=True, null=True)
    '''pin_code = models.CharField(max_length=6)'''

    def __str__(self):
        return f"Address for {self.license_details.license_number}"


class UnitDetails(models.Model):
    license_details = models.OneToOneField(LicenseDetails, on_delete=models.CASCADE, related_name='unit_details')  # Link to LicenseDetails
    licensee_type = models.CharField(max_length=50)
    reg_office_address = models.TextField(blank=True, null=True)
    pan = models.CharField(max_length=10, blank=True, null=True,validators=[pan_validator])
    phone_number = models.CharField(max_length=15, blank=True, null=True,validators=[phone_number_validator])
    date_of_incorporation = models.DateField(blank=True, null=True)
    department_office_unit = models.CharField(max_length=100, blank=True, null=True)
    cin_number = models.CharField(max_length=50, blank=True, null=True)
    email_id = models.EmailField(blank=True, null=True,validators=[email_validator])
    designation = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Unit Details for {self.license_details.license_number}"
    
class MemberDetail(models.Model):
    
    MEMBER_STATUS_CHOICES = [
        ('Partner', 'Partner'),
        ('Member', 'Member'),
    ]
    
    
    CITIZENSHIP_CHOICES = [
        ('Indian', 'Indian'),
        ('Non-Indian', 'Non-Indian'),
    ]
    
    license_details = models.ForeignKey(LicenseDetails, on_delete=models.CASCADE, related_name="members")
    member_status = models.CharField(max_length=50, choices=MEMBER_STATUS_CHOICES)
    member_name = models.CharField(max_length=100)
    citizenship = models.CharField(max_length=50, choices=CITIZENSHIP_CHOICES, default='Indian')
    gender = models.CharField(max_length=10)
    pan_number = models.CharField(max_length=50,validators=[pan_validator])
    mobile_number = models.CharField(max_length=15)
    email_id = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.member_name} ({self.member_status})"

class OTPVerification(models.Model):
    phone_number = models.ForeignKey(UserDetails, on_delete=models.CASCADE, related_name="otp_verifications")
    otp = models.CharField(max_length=4, validators=[validate_4_digit_otp])
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    last_requested_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"OTP for {self.phone_number.phone_number}"



    @staticmethod
    def verify_otp(phone_number, otp):
  
        try:
            otp_record = OTPVerification.objects.filter(
                phone_number__phone_number=phone_number,
                otp=otp,
                is_verified=False,  
            ).latest('created_at')

            
            if timezone.now() - otp_record.created_at > timedelta(minutes=5):
                return False
            

      
            otp_record.is_verified = True
            otp_record.save()
            return True
        except OTPVerification.DoesNotExist:
            return False

