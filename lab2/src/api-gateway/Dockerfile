FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only=main --no-root

# Copy source code
COPY api_gateway/ ./api_gateway/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"] 