FROM python:2.7-stretch

ADD requirements.txt /requirements.txt

# Install build deps
RUN apt-get -y update && apt-get -y install python-enchant \
    && apt-get -y install tesseract-ocr \
    && virtualenv /venv \
    && /venv/bin/pip install -U pip \
    && LIBRARY_PATH=/lib:/usr/lib /bin/sh -c "/venv/bin/pip install --no-cache-dir -r /requirements.txt"

RUN mkdir /code/
WORKDIR /code/
ADD . /code/

# uWSGI will listen on this port
EXPOSE 8000

ENV PYTHONPATH=$PYTHONPATH:/code/monthly_expenses

# Enable log creation
RUN chmod 777 /code/monthly_expenses/logs

# Add any custom, static environment variables needed by Django or your settings file here:
# ENV DJANGO_SETTINGS_MODULE=monthly_expenses.settings

# uWSGI configuration (customize as needed):
ENV UWSGI_VIRTUALENV=/venv UWSGI_WSGI_FILE=monthly_expenses/monthly_expenses/wsgi.py UWSGI_HTTP=:8000 UWSGI_MASTER=1 UWSGI_WORKERS=2 UWSGI_THREADS=8 UWSGI_UID=1000 UWSGI_GID=2000 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy

RUN /venv/bin/python /code/monthly_expenses/manage.py collectstatic --noinput

# TODO fix permissions -> should be owned by uwsgi user
RUN chmod 777 /code/monthly_expenses/apps/bills/media/

# Start uWSGI
CMD ["/venv/bin/uwsgi", "--http-auto-chunked", "--http-keepalive"]