from django.contrib import admin
from .models import UserDetails,OTPVerification


@admin.register(UserDetails)
class UserDetailsAdmin(admin.ModelAdmin):
   
    list_display = ['user_profile', 'date_of_birth', 'user_status', 'phone_number']
    
    search_fields = ['user_profile__username', 'phone_number']
    
    list_filter = ['user_status']

    fields = ['user_profile', 'date_of_birth', 'user_status', 'phone_number']



@admin.register(OTPVerification)

class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'otp', 'created_at', 'is_verified')
    search_fields = ('phone_number__phone_number', 'otp')
    list_filter = ('is_verified', 'created_at')
    ordering = ('-created_at',)
    fields = ('phone_number', 'otp', 'created_at', 'is_verified')

