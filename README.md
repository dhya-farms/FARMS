# Run Django with Docker Compose

This repo contains Fishery(FARMS) project.

It will be hosted locally using Gunicorn and Nginx containers.


# Usage

Run services in the background:
`docker-compose -f docker-compose.prod.yml up -d`

Run services in the foreground:
`docker-compose docker-compose.prod.yml up --build`

Inspect volume:
`docker volume ls`
and
`docker volume inspect <volume name>`

Prune unused volumes:
`docker volume prune`

View networks:
`docker network ls`

Bring services down:
`docker-compose -f docker-compose.prod.yml down -v`

Run migration:
`docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput`

Collect statis files:
`docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear`

Open a bash session in a running container:
`docker exec -it <container ID> /bin/bash`