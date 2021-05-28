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

ibmcloud ce project create -n "Bee Travels"
id=$(ibmcloud ce proj current | grep "Kubectl Context:" | awk '{print $3}')
ibmcloud ce app create -n destination-v1 -i ${DOCKERHUB_NAME}/destination-v1:latest --cl -p 9001 --min 1 --cpu 0.25 -m 0.5G -e LOG_LEVEL=info
ibmcloud ce app create -n hotel-v1 -i ${DOCKERHUB_NAME}/hotel-v1:latest --cl -p 9101 --min 1 --cpu 0.25 -m 0.5G -e LOG_LEVEL=info
ibmcloud ce app create -n carrental-v1 -i ${DOCKERHUB_NAME}/carrental-v1:latest --cl -p 9102 --min 1 --cpu 0.25 -m 0.5G -e LOG_LEVEL=info
ibmcloud ce app create -n ui -i ${DOCKERHUB_NAME}/ui:latest -p 9000 --min 1 --cpu 0.25 -m 0.5G -e NODE_ENV=production -e DESTINATION_URL=http://destination-v1.${id}.svc.cluster.local -e HOTEL_URL=http://hotel-v1.${id}.svc.cluster.local -e CAR_URL=http://carrental-v1.${id}.svc.cluster.local
