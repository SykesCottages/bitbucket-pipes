FROM python:3.12-slim

ENV OTEL_SDK_DISABLED "true"
ENV ANONYMIZED_TELEMETRY "false"

COPY requirements.txt /
WORKDIR /

RUN pip install --no-cache-dir -r requirements.txt
COPY pipe /
COPY pipe.yml .

CMD ["python3", "/pipe.py"]