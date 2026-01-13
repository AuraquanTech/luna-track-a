FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Railway sets PORT
# Use OpenAPI wrapper for ChatGPT integration
CMD ["sh", "-c", "uvicorn openapi_wrapper:app --host 0.0.0.0 --port ${PORT:-8000}"]
