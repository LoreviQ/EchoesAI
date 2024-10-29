FROM python:3.10-slim
RUN apt-get update && apt-get install -y libpq-dev gcc
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV DETACHED_MODE=true
EXPOSE 5000
CMD ["python", "src/app.py"]