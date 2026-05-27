# LionLink Backend

멋사 동아리원들이 좋은 자료(블로그·깃헙·튜토리얼) URL을 공유하는 미리보기 보드의
백엔드.

## 기술 스택

- Backend: Django 5 + DRF + simplejwt
- HTML 파싱: BeautifulSoup4
- HTTP 클라이언트: requests
- 이미지: Pillow + Django ImageField (EC2 디스크 `MEDIA_ROOT`에 저장)
- Project name: `seminar` (작년 가이드와 동일)
- DB: SQLite (로컬) / MySQL (배포)
- WSGI: gunicorn

## 환경변수

- `SECRET_KEY` — Django 시크릿 키

## 로컬 실행

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# SECRET_KEY를 임의의 긴 문자열로 교체
python manage.py migrate
python manage.py runserver
```

미디어 파일은 `media/` 디렉터리에 저장.

## AWS 배포

**AWS 배포 가이드**를 그대로 따라가면 됩니다.
차이점:

- 가이드의 `11th-week-back` → `lionlink-backend`
- 추가 환경변수: 없음
- 추가 requirements 패키지: `beautifulsoup4`, `requests`, `Pillow` (이미
  `requirements.txt`에 포함)
- nginx 설정에 `/media/` 경로 static 서빙 추가 (가이드의 `/static/` 옆에 한 줄):
  ```
  location /media/ {
      root /home/ubuntu/lionlink-backend;
  }
  ```

## API 요약

| Method | Path | 인증 | 설명 |
|---|---|---|---|
| POST | `/api/auth/signup/` | X | 회원가입 |
| POST | `/api/auth/login/` | X | JWT 발급 |
| GET | `/api/users/me/` | O | 본인 정보 |
| GET | `/api/previews/` | O | 전체 미리보기 보드 |
| POST | `/api/previews/` | O | URL 입력 → 미리보기 생성. `{ url }` |
| GET | `/api/previews/<id>/` | O | 특정 미리보기 |
