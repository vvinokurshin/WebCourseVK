#!/bin/bash

has_docker_img=$(docker images | awk '{print $1}' | grep helpme_docker)

if [[ ${has_docker_img} != "helpme_docker" ]]
then
    echo 'Building docker image'
    docker build -t helpme_docker .
else
    echo 'Docker image is already exists'
fi

has_docker_container=$(docker ps --filter ancestor=helpme_docker | awk '{print $12}' | grep helpme_db)

if [[ ${has_docker_container} != "helpme_db" ]]
then
    echo 'Creating container'
    docker run --name helpme_db -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d helpme_docker
    exit 0
else
    echo 'Container is already created'
fi

port1=$(docker ps --filter ancestor=helpme_docker --filter name=helpme_db | awk '{print $10}' | grep "0.0.0.0:5432->5432/tcp,")
port2=$(docker ps --filter ancestor=helpme_docker --filter name=helpme_db | awk '{print $11}' | grep ":::5432->5432/tcp")

if [[ ${port1} == "0.0.0.0:5432->5432/tcp," && ${port2} == ":::5432->5432/tcp" ]]
then
    echo 'Container is already run'
    exit 0
fi

echo 'Running container'
docker start helpme
