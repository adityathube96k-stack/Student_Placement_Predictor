FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=5000 APP_ENV=production

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN useradd --create-home appuser && mkdir -p instance logs dataset/uploads \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s \
  CMD python -c "import urllib.request,os;urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','5000')+'/health')"

# --preload creates the app (and initialises the database) once, before workers fork.
CMD ["sh", "-c", "gunicorn --preload -w 2 --threads 4 -b 0.0.0.0:${PORT} run:app"]
