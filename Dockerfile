FROM python:3.13-slim

WORKDIR /app

# pipenv
RUN pip install --no-cache-dir pipenv

# kopiujemy tylko pliki zależności (lepszy cache)
COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

# kopiujemy kod
COPY app/ /app/app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


