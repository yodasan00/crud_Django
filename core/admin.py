from django.contrib import admin
from .models import  LicenseDetails, MGQDetails, AddressDetails, UnitDetails, MemberDetail,District,LicenseCategory,Application
# Register your models here.


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  
    search_fields = ('name',) 


@admin.register(LicenseCategory)
class LicenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'category')  
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

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('application_id','application_date','license','status','renewal_year')  
    search_fields = ('application_id','application_date','license','status','renewal_year')
