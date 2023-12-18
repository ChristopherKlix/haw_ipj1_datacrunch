# app/Dockerfile

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Europe/Berlin
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./public/* .

RUN pip3 install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["streamlit", "run", "run.py", "--server.port=8080", "--server.address=0.0.0.0", "--theme.base=light"]