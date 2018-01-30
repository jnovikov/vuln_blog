FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY requirements.txt /tmp/

# upgrade pip and install required python packages
RUN pip install -U pip
RUN pip install -r /tmp/requirements.txt


COPY ./app /app

WORKDIR /app

RUN python init_db.py
