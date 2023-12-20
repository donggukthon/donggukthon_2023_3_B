import requests
import jwt
import random
from json.decoder import JSONDecodeError

from django.shortcuts import redirect, get_object_or_404
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from boonglunteer.settings import SECRET_KEY
from django.contrib.auth import authenticate

from rest_framework import viewsets, mixins, generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount

from .models import User
from badge.models import Badge
from fishbread.models import *
from fishbread.serializers import *
from .serializers import *

from social_django.utils import psa
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST'])
@psa('social:complete')
def register_by_access_token(request, backend):
    token = request.data.get('token')
    print(token)
    user = request.backend.do_auth(token)

    if user:
        # 사용자가 이미 존재하는 경우 로그인 처리
        # 여기서 JWT 토큰 발행 등의 추가 로직을 구현할 수 있습니다.
        return Response({'success': 'User authenticated', 'user': user.username})
    else:
        # 사용자가…
        return Response({'error': 'Authentication Failed'})

class RegisterUserFromJWT(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        jwt_token = request.data.get('token')  # 프론트에서 전달한 JWT 토큰

        try:
            decoded_token = jwt.decode(jwt_token,'317787650438-melnlpu3vcr53d2l4oc2e22f7jg8ra98.apps.googleusercontent.com', algorithms=['RS256'])  # 토큰 디코딩)
            email = decoded_token.get('email')
            print(email)
            name = decoded_token.get('name')
            print()

            # JWT에서 추출한 정보로 새로운 사용자 생성
            new_user = User.objects.create(email=email, name=name)
            serializer = UserSerializer(new_user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except jwt.ExpiredSignatureError:
            return Response({'error': 'Expired token'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
    print(access_token)
    """
    Email Request
    """
    print("함수호출")
    # print(request.data)
    # code = request.data.get("code")
    # access_token = request.data.get("access_token")
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
        # data = {'code': code}
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
        # data = {'code': code}

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
    client_class = OAuth2Client

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "user": serializer.data,
                    "message": "register successs",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            
            # jwt 토큰 => 쿠키에 저장
            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)
            
            return res
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    # 유저 정보 확인
    def get(self, request):
        try:
            # access token을 decode 해서 유저 id 추출 => 유저 식별
            access = request.COOKIES['access']
        except KeyError:
            # 'access' 키가 존재하지 않을 때의 처리
            return Response({'error': 'Access token not provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
        #     # access token을 decode 해서 유저 id 추출 => 유저 식별
        #     access = request.COOKIES['access']
            payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
            pk = payload.get('user_id')
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(instance=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except(jwt.exceptions.ExpiredSignatureError):
            # 토큰 만료 시 토큰 갱신
            data = {'refresh': request.COOKIES.get('refresh', None)}
            serializer = TokenRefreshSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                access = serializer.data.get('access', None)
                refresh = serializer.data.get('refresh', None)
                payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
                pk = payload.get('user_id')
                user = get_object_or_404(User, pk=pk)
                serializer = UserSerializer(instance=user)
                res = Response(serializer.data, status=status.HTTP_200_OK)
                res.set_cookie('access', access)
                res.set_cookie('refresh', refresh)
                return res
            raise jwt.exceptions.InvalidTokenError

        except(jwt.exceptions.InvalidTokenError):
            # 사용 불가능한 토큰일 때
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # 로그인
    def post(self, request):
    	# 유저 인증
        user = authenticate(
            email=request.data.get("email"), password=request.data.get("password")
        )
        # 이미 회원가입 된 유저일 때
        if user is not None:
            serializer = UserSerializer(user)
            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "user": serializer.data,
                    "message": "login success",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_200_OK,
            )
            # jwt 토큰 => 쿠키에 저장
            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)
            return res
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class Logout(APIView):
    def get(self, request):
        try:
            # access token을 decode 해서 유저 id 추출 => 유저 식별
            access = request.COOKIES['access']
        except KeyError:
            # 'access' 키가 존재하지 않을 때의 처리
            return Response({'error': 'Access token not provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
        #     # access token을 decode 해서 유저 id 추출 => 유저 식별
        #     access = request.COOKIES['access']
            payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
            pk = payload.get('user_id')
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(instance=user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except(jwt.exceptions.ExpiredSignatureError):
            # 토큰 만료 시 토큰 갱신
            data = {'refresh': request.COOKIES.get('refresh', None)}
            serializer = TokenRefreshSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                access = serializer.data.get('access', None)
                refresh = serializer.data.get('refresh', None)
                payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
                pk = payload.get('user_id')
                user = get_object_or_404(User, pk=pk)
                serializer = UserSerializer(instance=user)
                res = Response(serializer.data, status=status.HTTP_200_OK)
                res.set_cookie('access', access)
                res.set_cookie('refresh', refresh)
                return res
            raise jwt.exceptions.InvalidTokenError

        except(jwt.exceptions.InvalidTokenError):
            # 사용 불가능한 토큰일 때
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        # 쿠키에 저장된 토큰 삭제 => 로그아웃 처리
        response = Response({
            "message": "Logout success"
            }, status=status.HTTP_202_ACCEPTED)
        response.delete_cookie("access")
        response.delete_cookie("refresh")
        return response


############################
####### 사용자 Views ########
############################
        
class UserViewSet(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
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

# 유저 붕어빵 정보 조회
class UserFishbreadViewSet(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserFishbreadSerializer

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)
    
class UserCreateFishbreadViewSet(generics.CreateAPIView):
    serializer_class = FishbreadCreateSerializer
    
    def perform_create(self, serializer):
        fishbreadtype_id = random.randrange(1,5)
        fishbreadtype = FishbreadType.objects.get(id=fishbreadtype_id)  # 해당 id의 FishbreadType 가져오기
        serializer.save(user=self.request.user, fishbreadtype=fishbreadtype)
        return Response(data={
            "status" : 201
        },status=status.HTTP_201_CREATED)

class UserBadgeViewSet(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserBadgeSerializer

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

# 기부하기
class UserDonateViewSet(APIView):
    def post(self, request):
        charity_id = request.data.get('charity_id')
        charity = get_object_or_404(Charity, id=charity_id)
        charity.count += 1
        charity.save()

        fishbread_id = request.data.get('fishbread_id')
        fishbread = get_object_or_404(Fishbread, id=fishbread_id)

        fishbread.charity.add(charity)
        fishbread.isDonated = True
        fishbread.save()

        badge_id = random.randrange(1,10)
        badge = Badge.objects.get(id=badge_id)

        user = get_object_or_404(User, id=self.request.user.id)
        user.badge.add(badge)
        user.save()

        return Response({'message': '기부 업데이트 완료'})        
    

class UserHistoryViewSet(APIView):
    def get(self, request):
        user_fishbreads = Fishbread.objects.filter(user=request.user, isDonated=True)
        serializer  = FishbreadHistorySerializer(user_fishbreads, many=True)
        return Response(serializer.data)

