FROM python:3.10-slim

# install build deps for manylinux wheels (if needed)
RUN apt-get update  \
    && apt-get install -y gcc libpq-dev  \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# copy poetry and project files
COPY pyproject.toml poetry.lock README.md ./
COPY app/ ./app/

RUN pip install "poetry==2.1.2" \
 && poetry config virtualenvs.create false \
 && poetry install

# copy source
COPY .env-docker ./.env

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]