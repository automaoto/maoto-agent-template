# Maoto Agent Template

A maoto agent can be run with open connection to the server or without.
In most cases we recommend NOT using an open connection for communication with the platform.
However, in some cases this is necessary, i.e.:
- when there is a NAT / Firewall between device and Internet
- There is no static IP address available for the maoto-agent

Usually, only the functionality for personal assistants is suitable deployment as extension for locally run personal assistants on mobile devices.

## With Open Connection

python ./01_resolver.py

python ./02_provider.py

python ./03_provider_pa.py

`.secrets_resolver`:
```bash
MAOTO_API_KEY=<test_apikey_resolver>
```

`.secrets_provider`:
```bash
MAOTO_API_KEY=<test_apikey_provider>
```

# Server Mode

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
