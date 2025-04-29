from rest_framework import serializers
from .models import LicenseDetails, LicenseDetails, MGQDetails, AddressDetails, UnitDetails, MemberDetail,District,LicenseCategory,Application
from django.contrib.auth.models import User
from login.serializers import userSerializer

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
    class Meta:
        license_details = serializers.PrimaryKeyRelatedField(queryset=LicenseDetails.objects.all())
        model = MemberDetail
        fields = ['id','license_details','member_status', 'member_name', 'citizenship', 'gender', 'pan_number', 
                  'mobile_number', 'email_id']
   #read_only_fields = ['license_details']

'''iska api get se saara details de dega but u cant post any detail of other model via this except key details like license number etc'''

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'name']

class LicenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenseCategory
        fields = ['id', 'category']

class LicenseDetailsSerializer(serializers.ModelSerializer):
    user_profile = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  # Expect user ID
    district_name = serializers.PrimaryKeyRelatedField(queryset=District.objects.all())  # Expect District ID
    license_category = serializers.PrimaryKeyRelatedField(queryset=LicenseCategory.objects.all())  # Expect LicenseCategory ID
    mgq_details = MGQDetailsSerializer(read_only=True)  # Nested serializer for GET only
    address_details = AddressDetailsSerializer(read_only=True)  # Nested serializer for GET only
    unit_details = UnitDetailsSerializer(read_only=True)  # Nested serializer for GET only
    members = MemberDetailSerializer(many=True, read_only=True)  # Nested serializer for GET only

    class Meta:
        model = LicenseDetails
        fields = [
            'id', 'user_profile', 'license_number', 'district_name', 'licensee_name', 'establishment_name',
            'license_category', 'license_type', 'license_nature', 'yearly_license_fee', 'mgq_details',
            'address_details', 'unit_details', 'members'
        ]

    read_only_fields = ['mgq_details', 'address_details', 'unit_details', 'members']  # Make nested fields read-only
    def to_representation(self, instance):
        # Get the normal representation from the parent
        representation = super().to_representation(instance)
    
        representation['user_profile'] = userSerializer(instance.user_profile).data
        representation['district_name'] = DistrictSerializer(instance.district_name).data
        representation['license_category'] = LicenseCategorySerializer(instance.license_category).data
        
        return representation


class ApplicationSerializer(serializers.ModelSerializer):
  
    license = LicenseDetailsSerializer()  # Use nested serializer to include full license details

    class Meta:
        model = Application
        fields = [
            'application_id',
            'application_date',
            'status',
            'renewal_year',
            'license', 
        ]


    

