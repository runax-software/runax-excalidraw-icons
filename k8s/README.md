# Kubernetes Icons

43 icons from [kubernetes/community `icons/svg`](https://github.com/kubernetes/community/tree/main/icons/svg) plus the Kubernetes, Argo CD, Helm and K3s logos, packaged as a Miro-style Excalidraw library:
each item is a 64px icon with an editable label below it, grouped together.

<table>
<tr><td align="center" width="120"><img src="src/cncf/kubernetes.svg" width="64" height="62"><br><sub>Kubernetes</sub></td><td align="center" width="120"><img src="src/cncf/helm.svg" width="64" height="64"><br><sub>Helm</sub></td><td align="center" width="120"><img src="src/cncf/argo.svg" width="50" height="64"><br><sub>Argo CD</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/pod.svg" width="64" height="62"><br><sub>Pod</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/deploy.svg" width="64" height="62"><br><sub>Deployment</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/rs.svg" width="64" height="62"><br><sub>ReplicaSet</sub></td></tr>
<tr><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/sts.svg" width="64" height="62"><br><sub>StatefulSet</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/ds.svg" width="64" height="62"><br><sub>DaemonSet</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/job.svg" width="64" height="62"><br><sub>Job</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/cronjob.svg" width="64" height="62"><br><sub>CronJob</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/svc.svg" width="64" height="62"><br><sub>Service</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/ing.svg" width="64" height="62"><br><sub>Ingress</sub></td></tr>
<tr><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/netpol.svg" width="64" height="62"><br><sub>NetworkPolicy</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/cm.svg" width="64" height="62"><br><sub>ConfigMap</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/secret.svg" width="64" height="62"><br><sub>Secret</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/pv.svg" width="64" height="62"><br><sub>PersistentVolume</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/pvc.svg" width="64" height="62"><br><sub>PersistentVolumeClaim</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/sc.svg" width="64" height="62"><br><sub>StorageClass</sub></td></tr>
<tr><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/ns.svg" width="64" height="62"><br><sub>Namespace</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/sa.svg" width="64" height="62"><br><sub>ServiceAccount</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/role.svg" width="64" height="62"><br><sub>Role</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/rb.svg" width="64" height="62"><br><sub>RoleBinding</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/resources/unlabeled/hpa.svg" width="64" height="62"><br><sub>HorizontalPodAutoscaler</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/infrastructure_components/unlabeled/node.svg" width="64" height="62"><br><sub>Node</sub></td></tr>
<tr><td align="center" width="120"><img src="src/kubernetes/svg/infrastructure_components/unlabeled/control-plane.svg" width="64" height="62"><br><sub>Control Plane</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/control_plane_components/labeled/api.svg" width="64" height="62"><br><sub>API Server</sub></td><td align="center" width="120"><img src="src/kubernetes/svg/infrastructure_components/unlabeled/etcd.svg" width="64" height="62"><br><sub>etcd</sub></td></tr>
</table>

27 of 43 shown. Every icon is in [`src/`](src/). Changes are in [`CHANGELOG.md`](CHANGELOG.md).

## License

The Kubernetes resource and component icons are from [kubernetes/community](https://github.com/kubernetes/community) (Apache-2.0). The Kubernetes, Helm, Argo, K3s and K3OS logos are trademarks of The Linux Foundation or their owners, used under the [Linux Foundation trademark guidelines](https://www.linuxfoundation.org/legal/trademark-usage). Product names and logos are trademarks of their owners and are used here only to refer to their products; no endorsement is implied.

## Sources

Imports last fetched 2026-11-15. Paths are relative to [`src/`](src/). Imported files are refreshed by
`uv run runax-icons import k8s`; the rest are kept by hand.

| Files | Source | Notes |
| ----- | ------ | ----- |
| `kubernetes/**` | https://github.com/kubernetes/community/archive/c8b1af836bc44adbafe45653ceb1a4a54ab14d9a.zip | largest size of each icon, white-only ones skipped; from `community-*/icons` in the archive |
| `cncf/*.svg` | https://raw.githubusercontent.com/cncf/artwork/main/projects/{name}/icon/color/{name}-icon-color.svg | argo is Argo CD; forbids `edit`; 4 files |

## Use

Build with `uv run runax-icons build` from the repo root, then in Excalidraw:

1. Open `runax-k8s.excalidraw` (or paste icons from it into your drawing), so the images are loaded.
2. Import `runax-k8s.excalidrawlib` from the library panel.

Excalidraw doesn't store images in library files, so library icons render only once the
drawing contains them. See the [main README](../README.md).

<!-- Generated by runax-icons build; edit pack.yml instead. -->
