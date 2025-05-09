FROM python:3.12
RUN pip install poetry==1.4.2
WORKDIR /app
COPY . .
ENV PYTHONUNBUFFERED=1
RUN poetry install --no-root
ENTRYPOINT ["./woodchipper.sh"]
