#!/bin/bash

read -p "Dockerhub Username: " DOCKERHUB_NAME
read -s -p "Dockerhub Password: " DOCKERHUB_PASS

[ -z "$DOCKERHUB_NAME" ] && echo "Missing required Dockerhub Username"  && exit 1
[ -z "$DOCKERHUB_PASS" ] && echo "Missing required Dockerhub Password"  && exit 1

ibmcloud ce project create -n "Bee Travels"
id=$(ibmcloud ce proj current | grep "Context:" | awk '{print $2}')
ibmcloud ce registry create -n "${DOCKERHUB_NAME}-dockerhub" -u $DOCKERHUB_NAME -p $DOCKERHUB_PASS -s https://index.docker.io/v1/

# Destination
ibmcloud ce build create -n destination-v1-build -i ${DOCKERHUB_NAME}/destination-v1:latest --src https://github.com/IBM/code-engine-microservices --rs "${DOCKERHUB_NAME}-dockerhub" --cdr src/services/destination-v1 --sz small
ibmcloud ce buildrun submit -b destination-v1-build -n destination-v1-buildrun -w
ibmcloud ce app create -n destination-v1 -i ${DOCKERHUB_NAME}/destination-v1:latest --cl -p 9001 --min 1 --cpu 0.25 -m 0.5G -e LOG_LEVEL=info

# Hotel
ibmcloud ce build create -n hotel-v1-build -i ${DOCKERHUB_NAME}/hotel-v1:latest --src https://github.com/IBM/code-engine-microservices --rs "${DOCKERHUB_NAME}-dockerhub" --cdr src/services/hotel-v1-python --sz small
ibmcloud ce buildrun submit -b hotel-v1-build -n hotel-v1-buildrun -w
ibmcloud ce app create -n hotel-v1 -i ${DOCKERHUB_NAME}/hotel-v1:latest --cl -p 9101 --min 1 --cpu 0.25 -m 0.5G -e LOG_LEVEL=info

# Car Rental
ibmcloud ce build create -n carrental-v1-build -i ${DOCKERHUB_NAME}/carrental-v1:latest --src https://github.com/IBM/code-engine-microservices --rs "${DOCKERHUB_NAME}-dockerhub" --cdr src/services/car-rental-v1 --sz small
ibmcloud ce buildrun submit -b carrental-v1-build -n carrental-v1-buildrun -w
ibmcloud ce app create -n carrental-v1 -i ${DOCKERHUB_NAME}/carrental-v1:latest --cl -p 9001 --min 1 --cpu 0.25 -m 0.5G -e LOG_LEVEL=info

# UI
ibmcloud ce build create -n ui-build -i ${DOCKERHUB_NAME}/ui:latest --src https://github.com/IBM/code-engine-microservices --rs "${DOCKERHUB_NAME}-dockerhub" --cdr src/services/ui --sz small
ibmcloud ce buildrun submit -b ui-build -n ui-buildrun -w
ibmcloud ce app create -n ui -i ${DOCKERHUB_NAME}/ui:latest -p 9000 --min 1 --cpu 0.25 -m 0.5G -e NODE_ENV=production -e DESTINATION_URL=http://destination-v1.${id}.svc.cluster.local -e HOTEL_URL=http://hotel-v1.${id}.svc.cluster.local -e CAR_URL=http://carrental-v1.${id}.svc.cluster.local
