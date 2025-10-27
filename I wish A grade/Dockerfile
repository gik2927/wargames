# 1. 베이스 이미지 지정
FROM python:3.11-slim

# 2. 작업 디렉토리 생성 및 설정
WORKDIR /app

# 3. 시스템 패키지 설치 (SQLite, 빌드 도구 등)
RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Python 패키지 설치 (requirements.txt 없이 Flask만 설치)
RUN pip install --no-cache-dir flask click

# 5. 애플리케이션 소스코드 복사
COPY . .

# 6. 업로드 디렉토리 생성
RUN mkdir -p uploads

# 7. 환경 변수 설정
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000
ENV FLASK_ENV=development

# 8. Flask 실행
CMD ["flask", "run"]
