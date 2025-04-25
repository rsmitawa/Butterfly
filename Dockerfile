FROM python:3.9.17-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1-mesa-glx \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

RUN mkdir -p data/raw data/processed

ENV OLLAMA_HOST=host.docker.internal

EXPOSE 5002

CMD ["python", "src/butterfly/web/app.py"]