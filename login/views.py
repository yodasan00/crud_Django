from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from.serializers import UserDetailsSerializer,LicenseDetailsSerializer,userSerializer,MGQDetailsSerializer,AddressDetailsSerializer,UnitDetailsSerializer,MemberDetailSerializer,OTPVerificationSerializer
from .models import UserDetails,LicenseDetails,MGQDetails,AddressDetails,UnitDetails,MemberDetail,OTPVerification
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
import random
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
import logging
from django.contrib.auth import update_session_auth_hash


'''(note for self)Automatically associate the logged-in user's license_details with the license_details field in the serializer of the respective related models
    the user must have a license_details object associated with them, otherwise, a ValidationError will be raised.
    if the user does not have licence_details then mgq_details   and other details will  have no meaning 

'''
class LicenseDetailsMixin:
    def perform_create(self, serializer):
        try:
            license_details = self.request.user.license_details
        except LicenseDetails.DoesNotExist:
        
            raise ValidationError("User does not have associated license details.")

       
        serializer.save(license_details=license_details)


def login_user(request):
    permission_classes = [AllowAny]
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
           
            return JsonResponse({"error": "Username does not exist."}, status=400)

   
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # render(request,"registration/sucessful.html")
            user.user_details.user_status = True
            user.user_details.save()

            token, created = Token.objects.get_or_create(user=user)
            
            return JsonResponse({"token": token.key}, status=200)
        else:
           
            return JsonResponse({"error": "Incorrect password."}, status=400)
    
    else:
        # return render(request,"registration/log.html")
        return JsonResponse({"error": "Invalid request method."}, status=405) 
@login_required

def User_page(request):
    return render(request,"registration/sucessful.html")



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = userSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
   

class UserDetailsSerializerViewset(viewsets.ModelViewSet):
    serializer_class = UserDetailsSerializer
    queryset = UserDetails.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Automatically associate the logged-in user with the user_profile field(note for self : in UserDetails model)
    def perform_create(self, serializer):
        serializer.save(user_profile=self.request.user)

class LicenseDetailsSerializerViewset( viewsets.ModelViewSet):
    serializer_class = LicenseDetailsSerializer
    queryset = LicenseDetails.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Automatically associate the logged-in user with LicenseDetails model  using user_profile field in LicenseDetails model
    def perform_create(self, serializer):
       
        serializer.save(user_profile=self.request.user)



class MGQDetailsViewSet(LicenseDetailsMixin,viewsets.ModelViewSet):
    queryset = MGQDetails.objects.all()
    serializer_class = MGQDetailsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
   

class AddressDetailsViewSet(LicenseDetailsMixin,viewsets.ModelViewSet):
    queryset = AddressDetails.objects.all()
    serializer_class = AddressDetailsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class UnitDetailsViewSet(LicenseDetailsMixin,viewsets.ModelViewSet):
    queryset = UnitDetails.objects.all()
    serializer_class = UnitDetailsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]



class MemberDetailViewSet(LicenseDetailsMixin,viewsets.ModelViewSet):
    queryset = MemberDetail.objects.all()
    serializer_class = MemberDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]





class CreateOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        
     
        try:
            user_details = UserDetails.objects.get(phone_number=phone_number)
        except UserDetails.DoesNotExist:
            return Response({"error": "Phone number not found."}, status=status.HTTP_404_NOT_FOUND)
         

        '''addition of rate limiting functionality'''
        try:
            last_otp_request =user_details.otp_verifications.latest('created_at')

            time_diff = timezone.now() - last_otp_request.created_at
            if time_diff < timedelta(minutes=1):  
                '''one otp only in a minute'''
                remaining_time = timedelta(minutes=1) - time_diff
                raise ValidationError(f"Please wait {remaining_time.seconds} seconds before requesting a new OTP.")
        except OTPVerification.DoesNotExist:
            pass  # If no OTP requests exist for this phone numbee
    
          
        otp_code = f"{random.randint(1000, 9999)}"

       
        otp_instance = OTPVerification.objects.create(phone_number=user_details, otp=otp_code)

        
        email = user_details.user_profile.email  
        
        if email:
            subject = "Your OTP Code"
            message = f"Dear  {user_details.user_profile.username},\n\nYour OTP is: {otp_code}\n\nThis code will expire in 5 minutes."
            from_email = 'pushkarraj192003l@gmail.com' 
            recipient_list = [email] 

            try:
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

       
        serializer = OTPVerificationSerializer(otp_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


logger = logging.getLogger(__name__)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')

        if not phone_number:
            logger.error("Phone number is required.")
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            logger.error("OTP is required.")
            return Response({"error": "OTP is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_details = UserDetails.objects.get(phone_number=phone_number)
            logger.info(f"User found: {user_details}")
        except UserDetails.DoesNotExist:
            logger.error(f"Phone number {phone_number} not found.")
            return Response({"error": "Phone number not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            otp_instance = OTPVerification.objects.filter(
                phone_number__phone_number=phone_number,
                otp=otp,
                is_verified=False
            ).latest('created_at')

            logger.info(f"OTP instance found: {otp_instance}")

            if timezone.now() - otp_instance.created_at > timedelta(minutes=5):
                logger.error("OTP has expired.")
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

            otp_instance.is_verified = True
            otp_instance.save()

            user_details.user_status = True
            user_details.save()

            token, created = Token.objects.get_or_create(user=user_details.user_profile)

            logger.info(f"Token created: {token.key}")

            return Response({
                "message": "OTP verified successfully.",
                "token": token.key
            }, status=status.HTTP_200_OK)

        except OTPVerification.DoesNotExist:
            logger.error("Invalid or expired OTP.")
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if new_password != confirm_password: #check new and confirm pass same
            return Response({'error': 'Passwords do not match'}, status=400)

        if not request.user.check_password(old_password): #check if the old password is correct or not :-()
            return Response({'error': 'Old password is incorrect'}, status=400)

        request.user.set_password(new_password)
        request.user.save()

            # Keep the user logged in after password change
        update_session_auth_hash(request, request.user)

        return Response({'success': 'Password changed successfully'}, status=200)
           