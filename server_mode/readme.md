# Documentation: Marketplace

## Kubernetes on Local Minikube Cluster Simulation

```bash
minikube start --driver=docker --cpus=2 --memory=2048 --disk-size=10g --profile=minikube-cluster-intro
# minikube delete
```

Switch back to this context if use other cluster inbetween
```bash
kubectl config use-context minikube-cluster-intro
```

Build images and Deploy
```bash
cd ./server_mode/
bash local_depl.sh
# helm uninstall kubernetes-server
```