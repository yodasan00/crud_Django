from django.contrib import admin
from .models import UserDetails, LicenseDetails,OTPVerification, MGQDetails, AddressDetails, UnitDetails, MemberDetail


@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
   
    list_display = ['user_profile', 'date_of_birth', 'user_status', 'phone_number']
    
    search_fields = ['user_profile__username', 'phone_number']
    
    list_filter = ['user_status']

    fields = ['user_profile', 'date_of_birth', 'user_status', 'phone_number']




@admin.register(LicenseDetails)
class LicenseDetailsAdmin(admin.ModelAdmin):
    
    list_display = ['user_profile', 'license_number', 'district_name', 'licensee_name', 'establishment_name', 
                    'license_category', 'license_type', 'license_nature', 'yearly_license_fee']
    
    search_fields = ['user_profile__username', 'license_number', 'district_name']
    
    list_filter = ['license_category', 'license_type']
    
    fields = ['user_profile', 'license_number', 'district_name', 'licensee_name', 'establishment_name', 
              'license_category', 'license_type', 'license_nature', 'yearly_license_fee']
    





@admin.register(MGQDetails)
class MGQDetailsAdmin(admin.ModelAdmin):
    
    list_display = ['license_details', 'MGQ_in_BL', 'MGQ_in_LPL', 'MGQ_in_Quintal', 'deck_capacity']
    
    search_fields = ['license_details__license_number']
   
    fields = ['license_details', 'MGQ_in_BL', 'MGQ_in_LPL', 'MGQ_in_Quintal', 'deck_capacity']



@admin.register(AddressDetails)
class AddressDetailsAdmin(admin.ModelAdmin):
    
    list_display = ['license_details', 'police_station', 'excise_sub_division', 'ward', 'site_address','land_details', 'block', 'road']
    
    search_fields = ['license_details__license_number']
    
    fields = ['license_details', 'police_station', 'excise_sub_division', 'ward', 'site_address', 'land_details', 'block', 'road']



@admin.register(UnitDetails)
class UnitDetailsAdmin(admin.ModelAdmin):
   
    list_display = ['license_details', 'licensee_type', 'reg_office_address', 'pan', 'phone_number', 'date_of_incorporation', 'department_office_unit', 'cin_number', 'email_id', 'designation']
    
    search_fields = ['license_details__license_number', 'phone_number', 'pan']
   
    fields = ['license_details', 'licensee_type', 'reg_office_address', 'pan', 'phone_number', 'date_of_incorporation', 'department_office_unit', 'cin_number', 'email_id', 'designation']



@admin.register(MemberDetail)
class MemberDetailAdmin(admin.ModelAdmin):
  
    list_display = ['license_details', 'member_status', 'member_name', 'citizenship', 'gender', 'pan_number', 'mobile_number','email_id']
    
    search_fields = ['license_details__license_number', 'member_name', 'mobile_number', 'pan_number']
   
    list_filter = ['citizenship', 'member_status']
   
    fields = ['license_details', 'member_status', 'member_name', 'citizenship', 'gender', 'pan_number', 'mobile_number', 'email_id']

@admin.register(OTPVerification)

class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp', 'created_at', 'is_verified')
    search_fields = ('phone_number__phone_number', 'otp')
    list_filter = ('is_verified', 'created_at')
    ordering = ('-created_at',)
    fields = ('phone_number', 'otp', 'created_at', 'is_verified')