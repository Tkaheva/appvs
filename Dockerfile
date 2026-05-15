# Использовать alpine вместо slim (меньше размер, быстрее скачивается)
FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache ffmpeg

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads

EXPOSE 7000

CMD ["python", "run.py"]