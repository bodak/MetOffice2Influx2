FROM python:3.10-slim-bullseye
WORKDIR /app
COPY . .
RUN pip install -U pip
RUN pip install -r requirements.txt && rm requirements.txt
CMD ["python3", "main.py"]
