FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
RUN apt-get update && apt-get install -y postgresql-client
COPY backend/ .
ENV PYTHONUNBUFFERED 1
CMD ["python", "run.py"]
