# Maoto Agent Template

A maoto agent can be run with open connection to the server or without.
In most cases we recommend NOT using an open connection for communication with the platform, since an open connection can be a security risk, more error-prone and less reliable.
However, in some cases this it can be quite handy, i.e.:
- when there is a NAT / Firewall between device and Internet
- There is no static IP address available for the maoto-agent

## With Open Connection

python ./01_resolver.py

python ./02_provider.py

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
This automatically downloads or updates the server_mode dir into the working dir folder in any repository such that the latest version is used.
```bash
bash local_depl_on_template.sh
```

## See logs with:
```bash
kubectl logs -l app=apiinterfaces --namespace=maoto-agent-template --tail=-1
```
