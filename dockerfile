# Use Python 3.12 slim image
FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install system dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Download SpaCy model
RUN python -m spacy download en_core_web_sm

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false"]
