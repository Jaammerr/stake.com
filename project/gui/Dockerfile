FROM python:alpine3.19

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY .. .

#COPY wait-for-it.sh .
#RUN chmod +x wait-for-it.sh
#
#ENTRYPOINT [ "/usr/src/app/wait-for-it.sh", "-c" ]
#CMD ["/usr/src/app/wait-for-it.sh" , "api:8000" , "--strict" , "--timeout=300" , "--" , "python", "main.py"]
CMD ["python", "main.py"]