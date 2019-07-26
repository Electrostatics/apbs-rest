#!/bin/sh
minikube start --memory 4096
minikube addons enable ingress


kubectl create serviceaccount tiller --namespace kube-system
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
helm init --service-account=tiller --wait

helm install charts/apbs-rest -n apbs-rest --set ingress.enabled=true,ingress.hosts[0]=apbs.$(minikube ip).xip.io