FROM python:3.10
WORKDIR /app
COPY . /app
RUN pip install uvicorn fastapi
RUN pip install -r /app/svstl/requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
