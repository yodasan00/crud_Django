from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from.serializers import LicenseDetailsSerializer,MGQDetailsSerializer,AddressDetailsSerializer,UnitDetailsSerializer,MemberDetailSerializer,DistrictSerializer,LicenseCategorySerializer,ApplicationSerializer
from .models import LicenseDetails,MGQDetails,AddressDetails,UnitDetails,MemberDetail,District,LicenseCategory,Application
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

# Create your views here.




class LicenseDetailsSerializerViewset( viewsets.ModelViewSet):
    serializer_class = LicenseDetailsSerializer
    queryset = LicenseDetails.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]

  
   
    def get_queryset(self):
        """
        This method ensures that:
        - Admins can access all LicenseDetails.
        - Regular users can only access their own LicenseDetails.
        - If no LicenseDetails are found for the user, a NotFound exception is raised.
        """
        user = self.request.user  # Get the logged-in user
        
        # Admins can access all LicenseDetails
        if user.is_staff:
            return LicenseDetails.objects.all()

        # Regular users can access only their own LicenseDetails
        queryset = LicenseDetails.objects.filter(user_profile=user)

        # If no LicenseDetails are found for the regular user, raise NotFound exception
        if not queryset.exists():
            raise NotFound("License details not found for this user.")

        return queryset


class MGQDetailsViewSet(viewsets.ModelViewSet):
    queryset = MGQDetails.objects.all()
    serializer_class = MGQDetailsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]
    def get_queryset(self):
        """
        This method ensures that:
        - Admins can access all MGQDetails.
        - Regular users can access MGQDetails related to their own LicenseDetails.
        - If no LicenseDetails are found for the user, a PermissionDenied exception is raised.
        """
        user = self.request.user  # Get the logged-in user
        
        # If the user is an admin, return all MGQDetails
        if user.is_staff:
            return MGQDetails.objects.all()

        # Regular users: try to fetch the LicenseDetails for the authenticated user
        try:
            license_details = LicenseDetails.objects.get(user_profile=user)
        except LicenseDetails.DoesNotExist:
            raise PermissionDenied("License details not found for the user.")
        
        # Filter MGQDetails by the related LicenseDetails for the user
        queryset = MGQDetails.objects.filter(license_details=license_details)
        
        # If no MGQDetails are found for the given LicenseDetails, raise a NotFound exception
        if not queryset.exists():
            raise NotFound("MGQ details not found for this user.")
        
        return queryset


class AddressDetailsViewSet(viewsets.ModelViewSet):
    queryset = AddressDetails.objects.all()
    serializer_class = AddressDetailsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]


    def get_queryset(self):
        user = self.request.user  # Get the logged-in user
        
        # If the user is an admin, return all AddressDetails
        if user.is_staff:
            return AddressDetails.objects.all()

        # For regular users, fetch the LicenseDetails related to the authenticated user
        try:
            license_details = LicenseDetails.objects.get(user_profile=user)
        except LicenseDetails.DoesNotExist:
            raise PermissionDenied("License details not found for the user.")
        
        # Now filter AddressDetails by the related LicenseDetails
        queryset = AddressDetails.objects.filter(license_details=license_details)
        
        # If no AddressDetails are found for the user, raise a NotFound exception
        if not queryset.exists():
            raise NotFound("Address details not found for this user.")
        
        return queryset
   

class UnitDetailsViewSet(viewsets.ModelViewSet):
    queryset = UnitDetails.objects.all()
    serializer_class = UnitDetailsSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user  # Get the currently authenticated user
        
        # If the user is an admin, return all UnitDetails
        if user.is_staff:
            return UnitDetails.objects.all()

        # Find the user's corresponding LicenseDetails
        try:
            license_details = LicenseDetails.objects.get(user_profile=user)
        except LicenseDetails.DoesNotExist:
            raise PermissionDenied("License details not found for the user.")
        
        # Return UnitDetails associated with the found LicenseDetails
        queryset = UnitDetails.objects.filter(license_details=license_details)
        
        return queryset




class MemberDetailViewSet(viewsets.ModelViewSet):
    queryset = MemberDetail.objects.all()
    serializer_class = MemberDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user  # Get the currently authenticated user
        
        # If the user is an admin, return all MemberDetails
        if user.is_staff:
            return MemberDetail.objects.all()

        # Find the user's corresponding LicenseDetails
        try:
            license_details = LicenseDetails.objects.get(user_profile=user)
        except LicenseDetails.DoesNotExist:
            raise PermissionDenied("License details not found for the user.")
        
        # Return MemberDetails associated with the found LicenseDetails
        queryset = MemberDetail.objects.filter(license_details=license_details)
        
        return queryset


class DistrictListView(viewsets.ReadOnlyModelViewSet): #populates the dropdown through Get method 
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
        

class LicCatListView(viewsets.ReadOnlyModelViewSet): #populates the dropdown through Get method 
    queryset = LicenseCategory.objects.all()
    serializer_class = LicenseCategorySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class FilterLicenseDetails(APIView):  # Filters and sorts the selected data from the dropdown
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        # Parse the incoming request data
        data = json.loads(request.body.decode('utf-8'))
        district_id = data.get('district_id')
        license_category_id = data.get('license_category_id')
        renewal_year = data.get('renewal_year')

        # Validate the inputs
        if not district_id or not license_category_id or not renewal_year:
            return Response(
                {"error": "District ID, License Category ID, and Application Year are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate the district
        try:
            district = District.objects.get(id=district_id)
        except District.DoesNotExist:
            return Response({"error": "District not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate the license category
        try:
            license_category = LicenseCategory.objects.get(id=license_category_id)
        except LicenseCategory.DoesNotExist:
            return Response({"error": "License Category not found."}, status=status.HTTP_404_NOT_FOUND)

        # Filter applications based on the provided criteria
        applications = Application.objects.filter(
            license__district_name=district,
            license__license_category=license_category,
            renewal_year=renewal_year,
        ).select_related('license')

        # Check if any applications match the filters
        if not applications.exists():
            return Response(
                {"error": "No renewal applications found "},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Serialize the filtered applications
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApplicationRenewView(APIView):
    def get(self, request):
        """
        Fetch all renewal applications.
        """
        applications = Application.objects.select_related(
            'license__district_name', 'license__license_category'
        ).all()
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)