from django.urls import path, include
from . import views
from .views import *
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    # path('google/login', views.google_login, name='google_login'),
    # path('google/callback/', views.google_callback, name='google_callback'),  
    # # path('google/callback/', views.GoogleAccessView.as_view(), name='googel_access'),
    # path('google/login/finish/', views.GoogleLogin.as_view(), name='google_login_todjango'),
    # path('register2', views.register_by_access_token, name='register_access_token'),
    path('signup/', RegisterAPIView.as_view(), name='user-create'),
    path("login/", Login.as_view()),
    path("logout/", Logout.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path('password-change/', PasswordChangeView.as_view(), name='password-change'),
    path('password-change/done/', PasswordChangeView.as_view(), name='password-change-done'),


    path('register', RegisterUserFromJWT.as_view(), name='register'),
    path('bank', UserBankViewSet.as_view(), name='bank'),
    path('mypage', UserViewSet.as_view(), name='mypage'),
    path('date', UserDateViewSet.as_view(), name='date'),
    path('fishbread', UserFishbreadViewSet.as_view(), name='fishbread'),
    path('badges', UserBadgeViewSet.as_view(), name='badges'),
    path('start', UserCreateFishbreadViewSet.as_view(), name='start'),
    path('donate', UserDonateViewSet.as_view(), name='donate'),
    path('history', UserHistoryViewSet.as_view(), name='history'),
]