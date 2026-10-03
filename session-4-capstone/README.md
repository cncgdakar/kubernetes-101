# Session 4 — Full Application & Next Steps (2h)

**Slides (closing theory):** [`slides/theory.html`](slides/theory.html)

**By the end of this session you can:** deploy a 2-tier application from manifests you wrote yourself, with one service calling another by DNS name; diagnose the classic beginner failures from the events; and name what you would learn next, in order.

## Capstone hands-on (1h30)

### Mini-project: deploy a 2-tier app (60 min)
Frontend (nginx serving a page that calls the API) + backend (the Flask API). **Students write the manifests themselves**: 2 Deployments, 2 Services, 1 ConfigMap.

1. Build the images:
   ```bash
   docker build -t capstone-backend:1.0 app/backend
   docker build -t capstone-frontend:1.0 app/frontend
   kind load docker-image capstone-backend:1.0 capstone-frontend:1.0 --name k8s101
   ```
2. Write manifests for:
   - `backend`: Deployment (2 replicas, port 5000) + ClusterIP Service named `backend`
   - `frontend`: Deployment (2 replicas, port 80) + NodePort Service on 30080
   - a ConfigMap injecting `APP_ENV=training` into the backend
3. Verify: `curl http://localhost:30080` shows the page and the backend hostname.

Fill-in-the-blank manifest skeletons will be provided in `templates/` (structure given; images, ports, labels and selectors left blank) — writing 5 resources from a blank page in 60 min is too much for beginners. Fast students can ignore them.

**Staged unblocking** — the capstone is the one lab where students are meant to struggle, so the help is timed rather than withheld:

| Time | What's released |
|---|---|
| T+0 | Requirements only (the list above) |
| T+15 | `templates/` skeletons announced for anyone not started |
| T+35 | Backend reference manifest shown on screen-share and explained |
| T+50 | `solutions/` released to everyone — the point is a running app before the debugging block, not a solo victory |

No one debugs their own YAML past T+50: apply the reference manifests and join the debugging lab, which is where the real skill is.

Reference manifests are in [`solutions/`](solutions/) — instructors only until T+50!

### Guided debugging (30 min)
Apply the deliberately broken manifests one by one and diagnose with `describe` / `logs` / `events`.
📖 [Debug Pods](https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/) · [Troubleshoot applications](https://kubernetes.io/docs/tasks/debug/debug-application/)

```bash
kubectl apply -f broken-manifests/01-broken-image.yaml     # ImagePullBackOff
kubectl apply -f broken-manifests/02-broken-port.yaml      # Service selects nothing / wrong port
kubectl apply -f broken-manifests/03-broken-resources.yaml # Pending: insufficient resources
```
Fixes explained in [`broken-manifests/HINTS.md`](broken-manifests/HINTS.md).

**Checkpoint:** each broken manifest diagnosed out loud — the *symptom* (`kubectl get pods` state) and *where you found the cause* (`describe` events, `logs`) matter more than the fix.
**If stuck:** HINTS.md is open to everyone here — reading a hint after a genuine attempt is the intended flow. Students whose capstone never came up can still do this lab with the reference manifests from `solutions/`.

### Bonus — put it behind an Ingress (15 min, only if you are ahead)

Optional. Skip it without guilt: the capstone above is the session's objective, this is the
stretch. It replaces the NodePort with one entry point that routes by path — and it takes the
`/api/` proxying *out of the frontend's nginx config* and into Kubernetes, which is the real
reason Ingress exists.

```
                    ┌── /      ──► frontend Service :80
browser ──► Ingress ─┤
                    └── /api   ──► backend  Service :5000
```

**Step 1 — apply it and watch nothing happen.** Fill in
[`templates/04-ingress.yaml`](templates/04-ingress.yaml), apply it, then:

```bash
kubectl get ingress
kubectl describe ingress capstone
```

On a cluster with no controller the object is accepted, `ADDRESS` stays empty, and `curl`
gets you nothing. This is the Session 3 slide made real: **an Ingress is rules, not a router.**
Nobody made a mistake — there is simply nothing running that reads those rules.

**Step 2 — find out whether you have a controller.**

```bash
kubectl get ingressclass          # empty output = nothing is listening
kubectl get pods -A | grep -i -e ingress -e traefik
```

- **On k3d** you have one already: Traefik, class `traefik`, on ports 80/443. Put that class
  in `ingressClassName` and go to step 3.
- **On kind** there is none, and installing one is no longer a one-liner — see the note below.
  Read the manifest, keep the file, and do this on a cluster that has a controller.

**Step 3 — route through it.**

```bash
curl http://localhost:8080/            # the page, via the Ingress
curl http://localhost:8080/api/info    # the backend, without touching nginx
curl http://localhost:30080/           # the old NodePort still works — both doors are open
```

**Checkpoint:** you can say which component answered each of those three curls, and why the
first one failed before step 2.
**If stuck:** [`solutions/ingress.yaml`](solutions/ingress.yaml). If `ADDRESS` is still empty
after installing a controller, `kubectl describe ingress capstone` and read the events — a
mismatched `ingressClassName` is the usual cause and produces no error anywhere else.

> **Why there is no one-line install for kind.** `ingress-nginx` — the controller nearly every
> tutorial still tells you to `kubectl apply` — was **retired in March 2026**: no releases, no
> bugfixes, no security patches. Existing installs keep working and the artifacts are still
> downloadable, but it should not go on anything new. The project points users at **Gateway
> API** and at other maintained controllers, and the maintained ones (Traefik included) install
> via Helm rather than a raw manifest — which is why this bonus is written for k3d, where the
> controller is already running.
> 📖 [Ingress NGINX retirement](https://kubernetes.io/blog/2025/11/11/ingress-nginx-retirement/) ·
> [Gateway API](https://gateway-api.sigs.k8s.io/)

## Closing theory (20 min)
The map of the territory — what we didn't cover, in the order worth learning it:

- **Probes** — readiness vs liveness vs startup; what makes a rolling update genuinely zero-downtime
  📖 [Configure probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- **Requests and limits** — requests decide placement, limits decide enforcement (`OOMKilled`)
  📖 [Resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)
- **Security** — RBAC, ServiceAccounts, and the fact that by default *every Pod can reach every Pod*.
  **NetworkPolicy** is how you close that: default-deny the namespace, then allow one path. The catch is
  that the policy is only an object — your *CNI plugin* enforces it, and a CNI that doesn't implement
  NetworkPolicy accepts your YAML and changes nothing, silently. Verify enforcement before you trust it.
  📖 [RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) · [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- **Packaging & GitOps** — Helm/Kustomize, then Argo CD or Flux (the reconciliation loop applied to the whole platform)
  📖 [Helm docs](https://helm.sh/docs/)
- **Real clusters** — managed (EKS/AKS/GKE) vs self-hosted; same API, everything transfers
- **Storage in depth** — PVCs got a first taste in the Session 3 bonus lab

Full list with links: [`../docs/resources.md`](../docs/resources.md).

## Quiz / recap (10 min)
[`../docs/quiz.md`](../docs/quiz.md)
