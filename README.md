# LionLink Backend

멋사 동아리원들이 좋은 자료(블로그·깃헙·튜토리얼) URL을 공유하는 미리보기 보드의
백엔드.

> 이 레포에는 4단계 챌린지를 위한 결함이 의도적으로 내장되어 있습니다.

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

**작년 AWS 배포 가이드** ("4. 배포해보자!" 페이지)를 그대로 따라가면 됩니다.
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

## 프로덕션 환경의 추가 방어 (학습 자료)

코드 수준의 URL 검증은 첫 번째 방어선이지만 충분하지 않을 수 있다. 다음
인프라 수준의 layered defense를 함께 고려하라. **본 챌린지의 채점에 강제되지는
않지만, 실무에서는 표준 권고**:

- **IMDSv2 enforcement** — EC2 instance metadata service v2를 강제하면
  `PUT /latest/api/token`을 통한 토큰 발급 없이는 metadata에 접근 불가.
  AWS 콘솔 또는 CLI(`aws ec2 modify-instance-metadata-options --http-tokens required`)로 활성화.
- **Security Group egress 제한** — EC2 instance의 egress에서 `169.254.0.0/16`
  대역 송신 차단. private CIDR 외부로의 outbound도 최소화.
- **VPC private subnet + NAT Gateway** — backend를 private subnet에 두고 NAT
  Gateway로만 인터넷 접근. internal endpoint로의 직접 라우팅 자체가 불가.
- **IAM 최소 권한** — backend EC2의 IAM role에서 불필요한 권한 제거 (혹시 모를
  탈취 대비).
