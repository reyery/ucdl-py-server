FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

# Use gunicorn as production server
RUN pip install gunicorn

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--log-level=debug", "app:app"]
