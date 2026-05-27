from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra):
        if not email:
            raise ValueError('email이 필요합니다.')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(email, name, password, **extra)


class User(AbstractUser):
    """LionLink 사용자 — 자료 미리보기를 공유하는 동아리원."""
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = UserManager()

    def __str__(self):
        return f'{self.name} ({self.email})'


class Preview(models.Model):
    """공유된 URL의 미리보기 카드. OG 태그 + 백엔드 fetch 결과 일부 보존."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='previews'
    )
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='previews/', blank=True, null=True)
    # 디버깅 목적 — fetch 응답 일부를 그대로 보관해 미리보기 정확도 점검에 활용
    raw_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or self.url
