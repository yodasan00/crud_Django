from django.urls import path,include
from . import views
from rest_framework import routers
from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from .views import   LicenseDetailsSerializerViewset, MGQDetailsViewSet, AddressDetailsViewSet,UnitDetailsViewSet,MemberDetailViewSet
from .views import LicCatListView,DistrictListView,FilterLicenseDetails


router=routers.DefaultRouter()
router.register('license-details',LicenseDetailsSerializerViewset) 
router.register('mgq-details', MGQDetailsViewSet)
router.register('address-details', AddressDetailsViewSet)
router.register('unit-details', UnitDetailsViewSet)
router.register('member-details', MemberDetailViewSet)
router.register('district', DistrictListView)
router.register('lic_cat',LicCatListView)

urlpatterns = [
   
    path('', include(router.urls)),
     path('filter-licenses/', FilterLicenseDetails.as_view(), name='filter_licenses'),

]
 