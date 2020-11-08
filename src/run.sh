# Eliminate all the previous containers & custom images  and rebuilds everything.

# For now we assume to have only one container.
docker container rm `docker container ls -a | grep crawler | head -c 6`
docker container rm `docker container ls -a | grep broker | head -c 6`
docker container rm `docker container ls -a | grep client | head -c 6`
docker image rm crawler
docker image rm broker
docker image rm client

docker-compose up
