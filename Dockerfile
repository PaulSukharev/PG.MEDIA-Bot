
FROM python:3.11-slim AS bot

RUN apt-get update
RUN apt-get install -y python3 python3-pip python-dev build-essential python3-venv
RUN apt-get -y install eog ffmpeg

WORKDIR /bot/app/

COPY . /bot/

RUN pip3 install -r ../requirements.txt

RUN chmod +x bot.py

ENTRYPOINT ["python", "-u"]

CMD ["bot.py"]