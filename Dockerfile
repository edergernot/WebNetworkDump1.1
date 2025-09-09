FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/  

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN uv venv /opt/venv                 
ENV VIRTUAL_ENV=/opt/venv             
ENV PATH="/opt/venv/bin:$PATH"        
RUN uv pip install -r requirements.txt 

RUN mkdir output
RUN mkdir dump
RUN mkdir quickcommand

COPY  *.py ./
COPY  templates ./templates/
COPY  static ./static

EXPOSE 5000
EXPOSE 8888

CMD [ "uv", "run", "./webnetworkdump.py" ]
