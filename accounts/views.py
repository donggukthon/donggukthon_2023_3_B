import requests
from json.decoder import JSONDecodeError

from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

from rest_framework import viewsets, mixins, generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount

from .models import User
from .serializers import UserBankSerializer, UserSeriazlier, UserDateSerializer, UserFishbreadSerializer

state = getattr(settings, 'STATE')

BASE_URL = 'http://localhost:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'accounts/google/callback/'

def google_login(request):
    """
    Code Request
    """
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")

def google_callback(request):
    client_id = getattr(settings, "SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = getattr(settings, "SOCIAL_AUTH_GOOGLE_SECRET")
    print(client_id, client_secret)
    code = request.GET.get('code')
    """
    Access Token Request
    """
    token_req = requests.post(f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    token_req_json = token_req.json()
    error = token_req_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    access_token = token_req_json.get('access_token')
    """
    Email Request
    """
    # access_token = request.data.get("access_token")
    email_req = requests.get(
    f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code

    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)

    email_req_json = email_req.json()
    email = email_req_json.get('email')
    """
    Signup or Signin Request
    """
    try:
        user = User.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)

        # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
        # 다른 SNS로 가입된 유저
        if social_user is None:
            return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
        if social_user.provider != 'google':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
        # 기존에 Google로 가입된 유저
        data = {'access_token': access_token, 'code': code}
        print(data)
        accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        print(accept)
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

    except User.DoesNotExist:
        # 기존에 가입된 유저가 없으면 새로 가입
        data = {'access_token': access_token, 'code': code}

        accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)

        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        accept_json = accept.json()
        accept_json.pop('user', None)
        return JsonResponse(accept_json)

class GoogleAccessView(APIView):
    def post(self, request):
        access_token = request.data.get("access_token")
        email_req = requests.get(
        f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
        email_req_status = email_req.status_code

        if email_req_status != 200:
            return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)

        email_req_json = email_req.json()
        email = email_req_json.get('email')
        """
        Signup or Signin Request
        """
        try:
            user = User.objects.get(email=email)
            social_user = SocialAccount.objects.get(user=user)

            # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생, 맞으면 로그인
            # 다른 SNS로 가입된 유저
            if social_user is None:
                return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
            if social_user.provider != 'google':
                return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

            data = {'access_token': access_token}
            print(data)
            accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
            accept_status = accept.status_code

            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

            accept_json = accept.json()
            # accept_json.pop('user', None)
            return JsonResponse(accept_json)

        except User.DoesNotExist:
            # 기존에 가입된 유저가 없으면 새로 가입
            # data = {'access_token': access_token, 'code': code}
            data = {'access_token': access_token}
            accept = requests.post(f"{BASE_URL}accounts/google/login/finish/", data=data)
            accept_status = accept.status_code

            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
            accept_json = accept.json()
            # accept_json.pop('user', None)
            return JsonResponse(accept_json)


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    permission_classes = [AllowAny]
    client_class = OAuth2Client


############################
####### 사용자 Views ########
############################
        
class UserViewSet(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSeriazlier
    
    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)
    
class UserBankViewSet(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserBankSerializer
    
    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)
    
class UserDateViewSet(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserDateSerializer
    
    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)


class UserFishbreadViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserFishbreadSerializer

    def get_qureryset(self):
        return get_object_or_404(User, id=self.request.user.id)
    


# from rest_framework.response import Response
# from rest_framework.decorators import api_view

# from .models import User
# from fishbread.models import Fishbread
# # from .serializers import UserSerializer
# from fishbread.serializers import FishbreadSerializer

# from django.shortcuts import get_object_or_404

# # Create your views here.
# @api_view(['GET', 'POST'])
# def fishbread_info(request):

#     if request.method == 'GET':
#         fishbreads = Fishbread.objects.all()
#         serializer = FishbreadSerializer(fishbreads, many=True)
#         return Response(data=serializer.data)
    
#     if request.method == 'POST':
#         serializer = FishbreadSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             serializer.save()
#             return Response(data=serializer.data)

# @api_view(['GET', 'POST'])
# def fishbread_detail(request, id):
#     user = get_object_or_404(User, user_id=id)

#     if request.method == 'GET':
#         fishbreads = Fishbread.objects.filter(user_id=user)
#         serializer = FishbreadSerializer(fishbreads, many=True)
#         return Response(data=serializer.data)
    
#     elif request.method == 'POST':
#         serializer = FishbreadSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#         return Response(serializer.data)
