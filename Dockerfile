FROM python:3.8
LABEL MAINTAINER="Mohammad Nazemi Ardakani| ossa7899@gmail.com"

ENV PYTHONUNBUFFERED 1

# Set working directory
RUN mkdir /charsooghe_ir
WORKDIR /charsooghe_ir
COPY . /charsooghe_ir

# Installing requirements
ADD requirements.txt /charsooghe_ir
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --no-input

CMD ["gunicorn", "--chdir", "charsooghe_ir", "--bind", ":8000", "charsooghe_ir.wsgi:application"]