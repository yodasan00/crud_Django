from rest_framework import serializers
from .models import UserDetails, LicenseDetails, LicenseDetails, MGQDetails, AddressDetails, UnitDetails, MemberDetail
from django.contrib.auth.models import User
from .models import OTPVerification




class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    '''i did this to auto hash password while registering user via  api'''
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserDetailsSerializer(serializers.ModelSerializer):

    user_profile = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = UserDetails
        fields = ['id', 'user_profile', 'date_of_birth', 'user_status', 'phone_number']
    #   read_only_fields = ['user_status','user_profile']
   


class MGQDetailsSerializer(serializers.ModelSerializer):
    license_details = serializers.PrimaryKeyRelatedField(queryset=LicenseDetails.objects.all()) 

    class Meta:
        model = MGQDetails
        fields = ['id','license_details','MGQ_in_BL', 'MGQ_in_LPL', 'MGQ_in_Quintal', 'deck_capacity']

      #read_only_fields = ['license_details']

class AddressDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        license_details = serializers.PrimaryKeyRelatedField(queryset=LicenseDetails.objects.all())
        model = AddressDetails
        fields = ['id','license_details','police_station', 'excise_sub_division', 'ward', 'site_address', 
                  'land_details', 'block', 'road']
     # read_only_fields = ['license_details']

class UnitDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        license_details = serializers.PrimaryKeyRelatedField(queryset=LicenseDetails.objects.all())
        model = UnitDetails
        fields = ['id','license_details','licensee_type', 'reg_office_address', 'pan', 'phone_number', 
                  'date_of_incorporation', 'department_office_unit', 'cin_number', 
                  'email_id', 'designation']
      #read_only_fields = ['license_details']
class MemberDetailSerializer(serializers.ModelSerializer):
    license_details = serializers.PrimaryKeyRelatedField(queryset=LicenseDetails.objects.all())
    class Meta:
        model = MemberDetail
        fields = ['id','license_details','member_status', 'member_name', 'citizenship', 'gender', 'pan_number', 
                  'mobile_number', 'email_id']
   #read_only_fields = ['license_details']

'''iska api get se saara details de dega but u cant post any detail of other model via this except key details like license number etc'''

class LicenseDetailsSerializer(serializers.ModelSerializer):
    user_profile=serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    mgq_details = MGQDetailsSerializer(read_only=True)
    address_details = AddressDetailsSerializer(read_only=True)
    unit_details = UnitDetailsSerializer(read_only=True)
    members = MemberDetailSerializer(many=True, read_only=True)

    class Meta:
        model = LicenseDetails
        fields = ['id', 'user_profile', 'license_number', 'district_name', 'licensee_name', 'establishment_name', 
                  'license_category', 'license_type', 'license_nature', 'yearly_license_fee', 
                  'mgq_details', 'address_details', 'unit_details', 'members']
    read_only_fields = [ 'mgq_details', 'address_details', 'unit_details', 'members']
   
    

class OTPVerificationSerializer(serializers.ModelSerializer):
    phone_number = serializers.StringRelatedField()  

    class Meta:
        model = OTPVerification
        fields = ['id', 'phone_number', 'otp', 'created_at', 'is_verified']
        read_only_fields = ['id', 'created_at', 'is_verified'] 

    def validate_otp(self, value):
       
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("Enter a valid 4-digit OTP.")
        return value
