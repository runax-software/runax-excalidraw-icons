# Networking

35 icons from service mesh, ingress, CNI, DNS, VPN and API protocol logos: CNCF projects from [cncf/artwork](https://github.com/cncf/artwork) plus NGINX, Traefik, Kong, HAProxy, Caddy, Calico, Consul, Tailscale, WireGuard, NetBird, GraphQL, REST, OpenAPI, Swagger and Socket.IO, packaged as a Miro-style Excalidraw library:
each item is a 64px icon with an editable label below it, grouped together.

<table>
<tr><td align="center" width="120"><img src="src/cncf/istio.svg" width="64" height="64"><br><sub>Istio</sub></td><td align="center" width="120"><img src="src/cncf/linkerd.svg" width="64" height="64"><br><sub>Linkerd</sub></td><td align="center" width="120"><img src="src/cncf/cilium.svg" width="64" height="64"><br><sub>Cilium</sub></td><td align="center" width="120"><img src="src/cncf/envoy.svg" width="64" height="64"><br><sub>Envoy</sub></td><td align="center" width="120"><img src="src/other/nginx.svg" width="64" height="64"><br><sub>NGINX</sub></td><td align="center" width="120"><img src="src/other/traefik.svg" width="64" height="64"><br><sub>Traefik</sub></td></tr>
<tr><td align="center" width="120"><img src="src/other/kong.svg" width="64" height="64"><br><sub>Kong</sub></td><td align="center" width="120"><img src="src/other/haproxy.svg" width="64" height="64"><br><sub>HAProxy</sub></td><td align="center" width="120"><img src="src/other/caddy.svg" width="64" height="64"><br><sub>Caddy</sub></td><td align="center" width="120"><img src="src/cncf/contour.svg" width="64" height="64"><br><sub>Contour</sub></td><td align="center" width="120"><img src="src/cncf/emissary-ingress.svg" width="64" height="64"><br><sub>Emissary-ingress</sub></td><td align="center" width="120"><img src="src/cncf/kgateway.svg" width="64" height="64"><br><sub>kgateway</sub></td></tr>
<tr><td align="center" width="120"><img src="src/cncf/kuma.svg" width="64" height="64"><br><sub>Kuma</sub></td><td align="center" width="120"><img src="src/other/consul.svg" width="64" height="64"><br><sub>HashiCorp Consul</sub></td><td align="center" width="120"><img src="src/other/calico.svg" width="64" height="64"><br><sub>Calico</sub></td><td align="center" width="120"><img src="src/cncf/antrea.svg" width="64" height="64"><br><sub>Antrea</sub></td><td align="center" width="120"><img src="src/cncf/metallb.svg" width="64" height="64"><br><sub>MetalLB</sub></td><td align="center" width="120"><img src="src/cncf/coredns.svg" width="64" height="64"><br><sub>CoreDNS</sub></td></tr>
<tr><td align="center" width="120"><img src="src/cncf/cert-manager.svg" width="64" height="64"><br><sub>cert-manager</sub></td><td align="center" width="120"><img src="src/cncf/spiffe.svg" width="64" height="64"><br><sub>SPIFFE</sub></td><td align="center" width="120"><img src="src/cncf/spire.svg" width="64" height="64"><br><sub>SPIRE</sub></td><td align="center" width="120"><img src="src/cncf/grpc.svg" width="64" height="64"><br><sub>gRPC</sub></td><td align="center" width="120"><img src="src/other/graphql.svg" width="64" height="64"><br><sub>GraphQL</sub></td><td align="center" width="120"><img src="src/other/rest.svg" width="64" height="64"><br><sub>REST API</sub></td></tr>
<tr><td align="center" width="120"><img src="src/other/openapi.svg" width="64" height="64"><br><sub>OpenAPI</sub></td><td align="center" width="120"><img src="src/other/swagger.svg" width="64" height="64"><br><sub>Swagger</sub></td><td align="center" width="120"><img src="src/other/socket.io.svg" width="64" height="64"><br><sub>Socket.IO</sub></td><td align="center" width="120"><img src="src/other/tailscale.svg" width="64" height="64"><br><sub>Tailscale</sub></td><td align="center" width="120"><img src="src/other/wireguard.svg" width="64" height="64"><br><sub>WireGuard</sub></td><td align="center" width="120"><img src="src/other/netbird.svg" width="64" height="64"><br><sub>NetBird</sub></td></tr>
</table>

30 of 35 shown. Every icon is in [`src/`](src/). Changes are in [`CHANGELOG.md`](CHANGELOG.md).

## License

The CNCF project logos are from [cncf/artwork](https://github.com/cncf/artwork), used under the [Linux Foundation trademark guidelines](https://www.linuxfoundation.org/legal/trademark-usage); other logos come from [gilbarbara/logos](https://github.com/gilbarbara/logos) (CC0-1.0), [simple-icons](https://github.com/simple-icons/simple-icons) (CC0-1.0) or the projects themselves. Product names and logos are trademarks of their owners and are used here only to refer to their products; no endorsement is implied.

## Sources

Imports last fetched 2026-11-15. Paths are relative to [`src/`](src/). Imported files are refreshed by
`uv run runax-icons import networking`; the rest are kept by hand.

| Files | Source | Notes |
| ----- | ------ | ----- |
| `cncf/*.svg` | https://raw.githubusercontent.com/cncf/artwork/main/projects/{name}/icon/color/{name}-icon-color.svg | 17 files |
| `cncf/cilium.svg` | https://raw.githubusercontent.com/cncf/artwork/main/projects/cilium/icon/color/cilium_icon-color.svg |  |
| `cncf/kmesh.svg` | https://raw.githubusercontent.com/cncf/artwork/main/projects/kmesh/icon/color/KMESH-icon-color.svg |  |
| `cncf/grpc.svg` | https://raw.githubusercontent.com/cncf/artwork/main/projects/grpc/pancake/color/grpc-pancake-color.svg | the gRPC mascot; its icon/ file is the wordmark |
| `other/*.svg` | https://raw.githubusercontent.com/gilbarbara/logos/main/logos/{src}.svg | CC0-1.0; 5 files |
| `other/haproxy.svg` | https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/haproxy.svg | HAProxy brand color; filled #169BD6 |
| `other/caddy.svg` | https://caddyserver.com/resources/images/logo-light.svg | mark only; viewBox cropped |
| `other/calico.svg` | https://www.tigera.io/app/uploads/2026/01/Calico-logo-2026-black-text.svg | mark only; viewBox cropped |
| `other/wireguard.svg` | https://www.wireguard.com/img/wireguard.svg | mark only; viewBox cropped |
| `other/netbird.svg` | https://raw.githubusercontent.com/netbirdio/netbird/main/client/ui/frontend/src/assets/logos/netbird.svg |  |
| `other/rest.svg` |  | drawn for this pack; REST has no logo |
| `other/*` |  | moved from the techno pack (originally from techno's svg.zip) (GraphQL, OpenAPI, Swagger, Socket.IO) |

## Use

Build with `uv run runax-icons build` from the repo root, then in Excalidraw:

1. Open `runax-networking.excalidraw` (or paste icons from it into your drawing), so the images are loaded.
2. Import `runax-networking.excalidrawlib` from the library panel.

Excalidraw doesn't store images in library files, so library icons render only once the
drawing contains them. See the [main README](../README.md).

<!-- Generated by runax-icons build; edit pack.yml instead. -->
