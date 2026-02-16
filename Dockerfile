FROM python:3.12-slim
WORKDIR /usr/src
COPY requirements.txt /usr/src
RUN pip install -r requirements.txt
COPY app.py /usr/src
EXPOSE 5000
CMD ["python3", "/usr/src/app.py"]

