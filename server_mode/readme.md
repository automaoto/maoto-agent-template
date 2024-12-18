# Documentation: Marketplace

## Kubernetes on Local Minikube Cluster Simulation

```bash
minikube start --driver=docker --cpus=2 --memory=2048 --disk-size=10g --profile=cluster-server
# minikube delete
```

Switch back to this context if use other cluster inbetween
```bash
kubectl config use-context cluster-server
kubectl profile cluster-server
```

Build images and Deploy
```bash
cd ./server_mode/
bash local_depl.sh
# helm uninstall kubernetes-server
```

## Debug with:
```bash
kubectl logs -l app=apiinterfaces --namespace=agent-namespace --tail=-1
```
