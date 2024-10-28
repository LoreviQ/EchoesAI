FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV DETACHED_MODE=true
EXPOSE 5000
CMD ["python", "src/app.py"]