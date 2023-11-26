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

ENV USER=ChristopherKlix
ENV REPO=haw_ipj1_datacrunch
ENV BRANCH=public

ADD https://api.github.com/repos/$USER/$REPO/git/refs/heads/$BRANCH version.json
RUN git clone -b $BRANCH https://github.com/$USER/$REPO.git

RUN mv haw_ipj1_datacrunch/* .

RUN pip3 install -r requirements.txt

EXPOSE 8080

# HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "run.py", "--server.port=8080", "--server.address=0.0.0.0", "--theme.base=light"]