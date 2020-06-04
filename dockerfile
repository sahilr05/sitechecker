FROM python:3.8

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.0.5

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

COPY . /app
EXPOSE 8000

# CMD ['python','manage.py','runserver','localhost:8000']
