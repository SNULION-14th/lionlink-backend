import requests
from bs4 import BeautifulSoup
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Preview
from .serializers import (
    UserSerializer,
    SignupSerializer,
    PreviewSerializer,
    PreviewCreateSerializer,
)


def _issue_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'user': UserSerializer(user).data,
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def _og(soup, prop):
    """OG 태그 또는 일반 메타 태그에서 값 추출."""
    tag = soup.find('meta', attrs={'property': prop})
    if tag and tag.get('content'):
        return tag['content']
    if prop == 'og:title':
        if soup.title and soup.title.string:
            return soup.title.string.strip()
    if prop == 'og:description':
        tag = soup.find('meta', attrs={'name': 'description'})
        if tag and tag.get('content'):
            return tag['content']
    return ''


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(_issue_tokens(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {'detail': '이메일 또는 비밀번호가 잘못되었습니다.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(_issue_tokens(user))


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class PreviewView(APIView):
    """
    GET — 전체 미리보기 보드 (모든 사용자 공유)
    POST — 사용자가 입력한 URL을 받아 미리보기 카드를 만든다. 일반 외부 블로그·
    기사 URL을 입력하면 정상적으로 OG 태그가 추출되어 카드가 생성된다.

    백엔드가 URL을 fetch해서 응답 일부를 raw_text로 함께 보관하는데, 미리보기
    정확도 점검(디버깅) 목적이다.
    """

    def get(self, request):
        qs = Preview.objects.all()[:100]
        return Response(
            PreviewSerializer(qs, many=True, context={'request': request}).data
        )

    def post(self, request):
        serializer = PreviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.validated_data['url']

        # URL을 그대로 fetch.
        response = requests.get(url, timeout=5)
        raw_text = response.text[:500]

        soup = BeautifulSoup(response.text, 'html.parser')
        title = _og(soup, 'og:title')
        description = _og(soup, 'og:description')

        preview = Preview.objects.create(
            user=request.user,
            url=url,
            title=title,
            description=description,
            raw_text=raw_text,
        )

        # og:image도 fetch해서 디스크에 저장
        image_url = _og(soup, 'og:image')
        if image_url:
            try:
                img_response = requests.get(image_url, timeout=5)
                preview.image.save(
                    f'{preview.id}.jpg',
                    ContentFile(img_response.content),
                )
            except Exception:
                pass

        return Response(
            PreviewSerializer(preview, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class PreviewDetailView(APIView):
    def get(self, request, pk):
        try:
            preview = Preview.objects.get(pk=pk)
        except Preview.DoesNotExist:
            return Response(
                {'detail': '미리보기를 찾을 수 없습니다.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            PreviewSerializer(preview, context={'request': request}).data
        )
