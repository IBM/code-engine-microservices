#!/bin/bash
# -d = dockerhub name

DOCKERHUB_NAME=""
while getopts d: option
	do
		case "${option}"
		in
			d) DOCKERHUB_NAME=${OPTARG};;
		esac
done

[ -z "$DOCKERHUB_NAME" ] && echo "Missing required -d flag for Dockerhub Username"  && exit 1

cd src
yarn
cd ..

docker build -t ${DOCKERHUB_NAME}/node-base:v1 src

sed "s/\${DOCKERHUB_NAME}/${DOCKERHUB_NAME}/" src/services/destination-v1/Dockerfile_template > src/services/destination-v1/Dockerfile
docker build -t ${DOCKERHUB_NAME}/destination-v1:latest src/services/destination-v1
rm -rf src/services/destination-v1/Dockerfile

sed "s/\${DOCKERHUB_NAME}/${DOCKERHUB_NAME}/" src/services/car-rental-v1/Dockerfile_template > src/services/car-rental-v1/Dockerfile
docker build -t ${DOCKERHUB_NAME}/carrental-v1:latest src/services/car-rental-v1
rm -rf src/services/car-rental-v1/Dockerfile

sed "s/\${DOCKERHUB_NAME}/${DOCKERHUB_NAME}/" src/services/currency-exchange/Dockerfile_template > src/services/currency-exchange/Dockerfile
docker build -t ${DOCKERHUB_NAME}/currencyexchange:latest src/services/currency-exchange
rm -rf src/services/currency-exchange/Dockerfile

docker build -t ${DOCKERHUB_NAME}/python-hotel-v1:latest src/services/hotel-v1-python

sed "s/\${DOCKERHUB_NAME}/${DOCKERHUB_NAME}/" src/services/ui/Dockerfile_template > src/services/ui/Dockerfile
docker build -t ${DOCKERHUB_NAME}/ui:latest src/services/ui
rm -rf src/services/ui/Dockerfile

docker login

docker push ${DOCKERHUB_NAME}/destination-v1:latest
docker push ${DOCKERHUB_NAME}/carrental-v1:latest
docker push ${DOCKERHUB_NAME}/currencyexchange:latest
docker push ${DOCKERHUB_NAME}/python-hotel-v1:latest
docker push ${DOCKERHUB_NAME}/ui:latest
