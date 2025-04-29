# User microservice

This microservice is a part of larger project which can be found ....

## How to run

1. Create docker-compose.yaml file
1. Prepare env file
1. Build the image
1. Run database migrations
1. Run application

```shell
docker compose build usermicroservice
docker compose run -it usermicroservice python manage.py migrate
docker compose up
```

### Example compose file

```yaml
services:
  usermicroservice:
    build: ./users-microservice
    env_file:
      - path: ./env
        required: true
    ports:
      - "8000:8000"
    depends_on:
      - database
    volumes:
      - ./users-microservice:/code
  database:
    image: postgres
    ports:
      - "5400:5432"
    env_file:
      - path: ./env
        required: true
    volumes:
      - ./postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
      - db:/var/lib/postgresql/data

volumes:
  db:
```

### Env file variables

- RSA_PRIVATE_KEY - this key is used for creating JWT tokens and it can not be
  shared with other microservices
- RSA_PUBLIC_KEY - this key can be used to decode JWT token, each microservice
  which has to do that, must have this key
- POSTGRES_USER - username used to log in to postgresql
- POSTGRES_PASSWORD - password for user specified in *POSTGRES_USER*
- POSTGRES_HOST - name of the container holding postgres database
- POSTGRES_PORT - port at which database is running
