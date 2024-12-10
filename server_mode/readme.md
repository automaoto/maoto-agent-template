# Documentation: Marketplace

## Kubernetes on Local Minikube Cluster Simulation

```bash
minikube start --driver=docker --cpus=2 --memory=2048 --disk-size=10g --profile=minikube-cluster-intro
# minikube delete
```

Switch back to this context if use other cluster inbetween
```bash
kubectl config use-context minikube-cluster-intro
kubectl profile minikube-cluster-intro
```

Build images and Deploy
```bash
cd ./server_mode/
bash local_depl.sh
# helm uninstall kubernetes-server
```

### Commands for Bug Fixing and Security Checks

Locally build images to check images security with docker scout
```bash
bash build_for_docker_scout.sh
```
Check the status of the deployment and ensure the pods are running.
```bash
kubectl get pods -w
kubectl get all
kubectl describe pod <podname>
```
Verify the pod is running correctly by checking the logs.
```bash
kubectl logs -l app=<deploymentname> --tail=-1
```
See logs of pod that was recreated due to an error.
```bash
kubectl logs <api> --previous
```
Download Logs
```bash
kubectl logs -l app=<deploymentname> --tail=-1 > ./logs.txt
```