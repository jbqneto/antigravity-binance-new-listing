FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir playwright && playwright install chromium

# Copy project files
COPY execution/ execution/
COPY directives/ directives/

# Create temp directory
RUN mkdir -p .tmp

# Set entrypoint
# Set entrypoint
CMD ["uvicorn", "execution.api:app", "--host", "0.0.0.0", "--port", "8000"]
