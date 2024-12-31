# Documentation

Kubernetes on Local Minikube Cluster Simulation
```bash
minikube start --driver=docker --cpus=2 --memory=2048 --disk-size=10g --profile=cluster-server
```

Build images and Deploy
```bash
bash ./server_mode/local_depl.sh
```

## See logs with:
```bash
kubectl logs -l app=apiinterfaces --namespace="$NAMESPACE" --tail=-1
```
