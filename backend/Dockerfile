FROM python:3.7.2-stretch
# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
RUN apt install tzdata -y
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime
COPY backend/app /app/app
RUN pip install --no-cache -r requirements.txt
WORKDIR /app/app
CMD ["uvicorn", "main:app", "--port", "2090"]
