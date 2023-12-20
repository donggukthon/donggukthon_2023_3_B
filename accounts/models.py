from django.db import models
from badge.models import Badge
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=email,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

def create_superuser(self, email=None, password=None, **extra_fields):
    """
    주어진 이메일, 비밀번호 등 개인정보로 User 인스턴스 생성
    단, 최상위 사용자이므로 권한을 부여
    """
    superuser = self.create_user(
        email=email,
        password=password,
    )
    
    superuser.is_staff = True
    superuser.is_superuser = True
    superuser.is_active = True
    
    superuser.save(using=self._db)
    return superuser
    
class User(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(max_length=30, unique=True, null=False, blank=False)
    # name = models.CharField(max_length=100, null=False, blank=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    # holder = models.CharField(max_length=20, null=True)
    # bankname = models.CharField(max_length=20, null=True)
    # account_num = models.CharField(max_length=100, null=True)
#     # date_list = ArrayField(models.CharField(max_length=20), blank=True)
#     # date_list = models.CharField(max_length=30)
    # date = models.CharField(max_length=30, null=True)
    # badge = models.ManyToManyField(Badge, blank=True)
    # fishbread = models.ManyToManyField(Fishbread, blank=True)

	# 헬퍼 클래스 사용
    objects = UserManager()

	# 사용자의 username field는 email으로 설정 (이메일로 로그인)
    USERNAME_FIELD = 'email'
