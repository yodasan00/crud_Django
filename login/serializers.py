from rest_framework import serializers
from .models import UserDetails
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
    
