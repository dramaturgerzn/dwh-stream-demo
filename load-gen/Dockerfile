# load-gen/Dockerfile
FROM python:3.9-slim

RUN pip install --no-cache-dir psycopg2-binary faker

COPY data_gen.py /app/data_gen.py
ENTRYPOINT ["python", "/load-gen/data_gen.py"]