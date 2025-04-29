FROM python
WORKDIR /code
COPY . .
RUN pip install -U pip
RUN pip install -r requirements.txt
CMD python manage.py runserver 0.0.0.0:8000
