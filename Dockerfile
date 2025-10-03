# Sử dụng Python base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy file requirements và cài
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào
COPY . .

# Command mặc định
CMD ["python", "run.py"]