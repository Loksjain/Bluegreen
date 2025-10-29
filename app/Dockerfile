# --- Build (no heavy tools needed, but keep layers clean)
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# install just what we need
COPY app.py requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# runtime
EXPOSE 8080
ENV PORT=8080
CMD ["python", "app.py"]
