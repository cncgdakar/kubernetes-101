# Capstone templates — fill in the blanks

These skeletons exist so a YAML typo doesn't cost you the session. The **structure** is given;
everything that matters — images, ports, labels, selectors, names — is left as `TODO`.

Use them if you want. Ignore them and write from scratch if you'd rather.

## What you are building

```
browser ──► NodePort 30080 ──► frontend (nginx, 2 replicas)
                                   │  proxies /api/ ──► backend Service (ClusterIP, port 5000)
                                   ▼
                               backend (Flask, 2 replicas) + ConfigMap (APP_ENV=training)
```

## Constraints that are NOT negotiable

The frontend's nginx config proxies to `http://backend:5000`, so:

- the backend Service **must be named `backend`** and listen on **port 5000**
- the frontend Service is **NodePort 30080** (that's the port mapped by the cluster)
- both images use `imagePullPolicy: IfNotPresent` and must be loaded into the cluster:
  `kind load docker-image capstone-backend:1.0 capstone-frontend:1.0 --name k8s101`

## Order that works

1. `03-configmap.yaml` → `kubectl apply -f`
2. `01-backend.yaml` → check `kubectl get pods -l app=backend`
3. `02-frontend.yaml` → `curl http://localhost:30080`

4. *(bonus, optional)* `04-ingress.yaml` → see the Ingress section of the session README

Validate before applying: `kubectl apply --dry-run=client -f 01-backend.yaml`

Stuck on a field? `kubectl explain deployment.spec.template.spec.containers`
