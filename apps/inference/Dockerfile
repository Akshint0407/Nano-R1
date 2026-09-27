FROM python:3.10-slim

WORKDIR /app

# Install system build dependencies required for compiling C++ extensions like llama-cpp-python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to leverage Docker layer caching
COPY requirements.txt .

ARG INSTALL_GPU_DEPS=false

# Install base Python packages
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" pydantic llama-cpp-python==0.3.4 huggingface_hub && \
    if [ "$INSTALL_GPU_DEPS" = "true" ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy application files
COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]