FROM python:3.10-slim

WORKDIR /usr/src/app

RUN pip install --upgrade pip

COPY requirements.txt ./

RUN pip install -r requirements.txt

RUN mkdir output
RUN mkdir dump

COPY  *.py ./
COPY  templates ./templates/
COPY  static ./static

EXPOSE 5000

CMD [ "python", "./webnetworkdump.py" ]