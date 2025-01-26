from django.urls import path,include
from . import views
from rest_framework import routers
from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from .views import CreateOTPView, VerifyOTPView
from .views import ChangePasswordView,CreateAdminView




router=routers.DefaultRouter()
router.register('users',views.UserViewSet)
router.register('user-details',views.UserDetailsSerializerViewset)

urlpatterns = [
    path('login/',views.login_user,name='login'),
    path('otp/create/', CreateOTPView.as_view(), name='create-otp'),
    path('otp/verify/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('', include(router.urls)),
    path('create-admin/', CreateAdminView.as_view(), name='create_admin'),
     

]
 