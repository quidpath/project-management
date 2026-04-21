FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=projects_service.settings.prod

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc dos2unix && rm -rf /var/lib/apt/lists/*

COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

COPY . /app/

RUN dos2unix /app/start.sh && chmod +x /app/start.sh

EXPOSE 8007

CMD ["/bin/bash", "/app/start.sh"]
