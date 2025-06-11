# Use official Python runtime as a parent image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Install OpenCV, Tesseract OCR, and required system dependencies (before pip install!)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    tesseract-ocr \
    tesseract-ocr-eng && \
    rm -rf /var/lib/apt/lists/*

# Copy your app code into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set default command to run your main bot file
CMD ["python", "main.py"]

