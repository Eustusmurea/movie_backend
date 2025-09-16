FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "movie_backend.wsgi:application", "--bind", "0.0.0.0:8000"]
