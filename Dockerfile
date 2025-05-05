FROM python:3.12

ENV PYTHONUNBUFFERED 1

WORKDIR /opt/app

COPY requirements.txt /opt/app/

RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY backend /opt/app/

CMD ["python", "/opt/app/run.py"]
