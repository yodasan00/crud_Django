from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from.serializers import UserDetailsSerializer,userSerializer,OTPVerificationSerializer
from .models import UserDetails,OTPVerification
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
from rest_framework.exceptions import ValidationError,PermissionDenied,NotFound
from rest_framework.permissions import AllowAny
import logging
from django.contrib.auth import update_session_auth_hash
import json
from .permissions import IsAdminOrReadOnly,IsSuperUser



'''(note for self)perform_create()-Automatically associate the logged-in user's license_details with the license_details field in the serializer of the respective related models
 the user must have a license_details object associated with them, otherwise, a ValidationError will be raised.
if the user does not have licence_details then mgq_details   and other details will  have no meaning .
we have also used perform_create() to associate the other model objects with the user in their respective views. 
the get_queryset method overrides default and return only the queryset specific to the useri.e info relating only to that logged in user.
in the userviewset we have also checked if the user is admin or not for registering a user  and if not then we have returned a response with error message.
'''


def login_user(request):
    permission_classes = [AllowAny]
    if request.method == "POST":
        print("Raw request body:", request.body)  # Logs raw request data
        try:
            data = json.loads(request.body.decode('utf-8'))  # Decode JSON
            print("Parsed data:", data)
            username = data.get("username")
            password = data.get("password")
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
           
            return JsonResponse({"error": "Username does not exist."}, status=400)

   
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            try:
    # Access and modify user_details if it exists
                user.user_details.user_status = True
                user.user_details.save()
            except AttributeError: 
                # Handle the case where user_details does not exist
                print("UserDetails object does not exist for this user.")
    
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({"token": token.key}, status=200)
        else:
           
            return JsonResponse({"error": "Incorrect password."}, status=400)
    
    else:
        # return render(request,"registration/log.html")
        return JsonResponse({"error": "Invalid request method."}, status=405) 


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = userSerializer
    permission_classes = [IsAdminOrReadOnly]
    authentication_classes = [TokenAuthentication]
    
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()  # Admins can view all users
        return User.objects.filter(id=self.request.user.id)  # Regular users see only their data

    
class UserDetailsSerializerViewset(viewsets.ModelViewSet):
    serializer_class = UserDetailsSerializer
    queryset = UserDetails.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        
        # Admin can view all user details
        if self.request.user.is_staff:
            return UserDetails.objects.all()
        
        # Regular users can only view their own details
        return UserDetails.objects.filter(user_profile=user)




class CreateOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))  # Decode JSON
        print("Parsed data:", data)
        phone_number = data.get('phone_number')
        
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
                Wait=remaining_time.seconds
                return JsonResponse(
    {
        "message": f"Please wait {Wait} seconds before requesting a new OTP."
    },
    status=status.HTTP_429_TOO_MANY_REQUESTS
)

               
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
                print(otp_code)
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

    authentication_classes = [TokenAuthentication]

    def post(self, request):
        data = json.loads(request.body.decode('utf-8'))
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password != confirm_password: #check new and confirm pass same
            return Response({'error': 'Passwords do not match'}, status=400)

        if not request.user.check_password(old_password): #check if the old password is correct or not :-()
            return Response({'error': 'Old password is incorrect'}, status=400)

        request.user.set_password(new_password)
        request.user.save()

            # Keep the user logged in after password change
        update_session_auth_hash(request, request.user)  

        return Response({'success': 'Password changed successfully'}, status=200)
    

   
class CreateAdminView(APIView):
        permission_classes = [IsSuperUser]
        def post(self,request):
            if request.method == "POST":
                try:
                    data = json.loads(request.body)
                    username = data.get("username")
                    password = data.get("password")
                    email = data.get("email", "")
                    
                    if not username or not password:
                        return JsonResponse({"error": "Username and password are required."}, status=400)
                    
                    if User.objects.filter(username=username).exists():
                        return JsonResponse({"error": "User with this username already exists."}, status=400)

                    #we do not Create a superuser but only an admin if we wanted to create superuse create_superuser funnction is to be used
                    # Create an admin user (is_staff=True, is_superuser=False)
                    admin_user = User.objects.create_user(username=username, password=password, email=email)
                    admin_user.is_staff = True  # Set is_staff to True for admin privileges
                    admin_user.save()
                    return JsonResponse({"message": "Admin user created successfully."}, status=201)

                except json.JSONDecodeError:
                    return JsonResponse({"error": "Invalid JSON data."}, status=400)

            return JsonResponse({"error": "Only POST method is allowed."}, status=405)
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    def post(self, request):
        #request.auth.delete()
        user=self.request.user
        user.user_details.user_status = False
        user.user_details.save()
        logout(request)
        
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)        

