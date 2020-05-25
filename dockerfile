FROM python:3.8
ENV PYTHONUNBUFFERED 1
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8000
# CMD ['python','manage.py','runserver','localhost:8000']