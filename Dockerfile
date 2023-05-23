FROM python:3.11-slim AS bot

RUN apt-get update
RUN apt-get install -y python3 python3-pip python-dev build-essential python3-venv
RUN apt-get -y install eog ffmpeg

WORKDIR /bot/app/

COPY . /bot/

RUN pip3 install -r ../requirements.txt

RUN sed -i 's/var_regex = re.compile(r"^\w+\W")*/var_regex = re.compile(r"^\$*\w+\W")/g' /usr/local/lib/python3.11/site-packages/pytube/cipher.py

RUN chmod +x bot.py

ENTRYPOINT ["python", "-u"]

CMD ["bot.py"]