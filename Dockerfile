FROM python:3.6

ENV HMM_PORT=8888
ENV HMM_BASEDIR=/var/www

EXPOSE 8888

VOLUME [ "/var/www" ]

ADD requirements.txt requirements.txt
ADD main.py main.py

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "main.py" ]