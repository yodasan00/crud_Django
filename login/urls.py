from django.urls import path,include
from . import views
from rest_framework import routers
from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from .views import CreateOTPView, VerifyOTPView,  LicenseDetailsSerializerViewset, MGQDetailsViewSet, AddressDetailsViewSet,UnitDetailsViewSet,MemberDetailViewSet
from .views import ChangePasswordView,CreateAdminView,LicCatListView,DistrictListView,FilterLicenseDetails




router=routers.DefaultRouter()
router.register('users',views.UserViewSet)
router.register('user-details',views.UserDetailsSerializerViewset)
router.register('license-details',LicenseDetailsSerializerViewset) 
router.register('mgq-details', MGQDetailsViewSet)
router.register('address-details', AddressDetailsViewSet)
router.register('unit-details', UnitDetailsViewSet)
router.register('member-details', MemberDetailViewSet)
router.register('district', DistrictListView)
router.register('lic_Cat',LicCatListView)

urlpatterns = [
    path('login/',views.login_user,name='login'),
    path('otp/create/', CreateOTPView.as_view(), name='create-otp'),
    path('otp/verify/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('', include(router.urls)),
    path('create-admin/', CreateAdminView.as_view(), name='create_admin'),
     path('api/filter-licenses/', FilterLicenseDetails.as_view(), name='filter_licenses'),

]
 