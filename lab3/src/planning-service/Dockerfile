FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml ./

RUN poetry config virtualenvs.create false

RUN poetry install --only=main --no-root

COPY planning_service/ ./planning_service/

EXPOSE 8080

CMD ["uvicorn", "planning_service.main:app", "--host", "0.0.0.0", "--port", "8080"]