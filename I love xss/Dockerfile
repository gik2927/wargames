FROM python:3.11-slim

RUN apt-get update -y && apt-get install -y build-essential wget curl unzip libxml2-dev libxslt1-dev zlib1g-dev

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gnupg \
        ca-certificates \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y \
        google-chrome-stable \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN wget https://storage.googleapis.com/chrome-for-testing-public/$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE)/linux64/chromedriver-linux64.zip \
    && unzip -o chromedriver-linux64.zip \ 
    && mv chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \ 
    && rm chromedriver-linux64.zip \
    && rm -r chromedriver-linux64 

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]