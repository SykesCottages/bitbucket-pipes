FROM python:3.11-slim

COPY requirements.txt /
WORKDIR /

RUN pip install --no-cache-dir -r requirements.txt
COPY pipe /
COPY pipe.yml .

CMD ["python3", "/pipe.py"]