# load-gen/Dockerfile
FROM python:3.9-slim
WORKDIR /app
RUN pip install --no-cache-dir psycopg2-binary faker
COPY data_gen.py .
ENTRYPOINT ["python", "data_gen.py"]