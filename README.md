# chat-model
This repository contains a task assessment

## How to run this project
1. Install `python 3.10`
2. Install `uv`
3. Create a `.env` file at the root of the project with following environment variables:
```sh
ENV="DEV"
OPENAI_API_KEY=""
REDIS_HOST="localhost"
REDIS_PORT="6379"
```
4. Execute the following command to run in development environment `uv run manage.py`


## Run in production
Use docker compose to run this project using docker
```sh
docker compose build
docker compose up -d
```