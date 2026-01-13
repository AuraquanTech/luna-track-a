FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

# Railway sets PORT
CMD ["sh", "-c", "fastmcp run server.py --transport http --host 0.0.0.0 --port ${PORT:-8000}"]
