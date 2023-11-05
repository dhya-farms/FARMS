FROM python:3.11.4-slim-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV ENV_PATH=.env.prod
ENV PATH="/py/bin:$PATH"
ENV PATH="/scripts:/py/bin:$PATH"
# set work directory
WORKDIR /usr/src/FARMS

# install system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/* && apt-get clean

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./scripts /scripts
RUN chmod -R +x /scripts

# copy project
COPY . .

EXPOSE 80

CMD ["/scripts/run.sh"]
