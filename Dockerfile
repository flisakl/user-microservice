FROM python
WORKDIR /code
COPY . .
RUN pip install -U pip
RUN pip install -r requirements.txt
RUN python manage.py migrate
CMD python manage.py runserver 0.0.0.0:8000