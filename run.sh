# Eliminates all the previous containers & custom images and rebuilds everything.

docker container rm `docker container ls -a | grep crawler | head -c 6`
docker container rm `docker container ls -a | grep broker | head -c 6`
docker container rm `docker container ls -a | grep client | head -c 6`
docker container rm `docker container ls -a | grep redis | head -c 6`
docker container rm `docker container ls -a | grep mongo | head -c 6`
docker image rm crawler
docker image rm broker
docker image rm client
docker image rm redis
docker image rm mongo

docker-compose build
docker-compose up
