# Azure Architecture Icons

645 icons from [Azure Architecture Icons](https://learn.microsoft.com/azure/architecture/icons/), packaged as a Miro-style Excalidraw library:
each item is a 64px icon with an editable label below it, grouped together.

<table>
<tr><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/compute/10021-icon-service-Virtual-Machine.svg" width="64" height="64"><br><sub>Virtual Machine</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/app%20services/10035-icon-service-App-Services.svg" width="64" height="64"><br><sub>App Services</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/compute/10029-icon-service-Function-Apps.svg" width="64" height="64"><br><sub>Function Apps</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/compute/10023-icon-service-Kubernetes-Services.svg" width="64" height="64"><br><sub>Kubernetes Services</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/compute/10104-icon-service-Container-Instances.svg" width="64" height="64"><br><sub>Container Instances</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/containers/10105-icon-service-Container-Registries.svg" width="64" height="64"><br><sub>Container Registries</sub></td></tr>
<tr><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/storage/10086-icon-service-Storage-Accounts.svg" width="64" height="64"><br><sub>Storage Accounts</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/databases/10130-icon-service-SQL-Database.svg" width="64" height="64"><br><sub>SQL Database</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/databases/10121-icon-service-Azure-Cosmos-DB.svg" width="64" height="64"><br><sub>Azure Cosmos DB</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/databases/10137-icon-service-Cache-Redis.svg" width="64" height="64"><br><sub>Cache Redis</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/databases/10131-icon-service-Azure-Database-PostgreSQL-Server.svg" width="64" height="64"><br><sub>Azure Database PostgreSQL Server</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/networking/10061-icon-service-Virtual-Networks.svg" width="64" height="64"><br><sub>Virtual Networks</sub></td></tr>
<tr><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/networking/10062-icon-service-Load-Balancers.svg" width="64" height="64"><br><sub>Load Balancers</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/networking/10076-icon-service-Application-Gateways.svg" width="64" height="64"><br><sub>Application Gateways</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/networking/10073-icon-service-Front-Door-and-CDN-Profiles.svg" width="64" height="64"><br><sub>Front Door And CDN Profiles</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/networking/10064-icon-service-DNS-Zones.svg" width="64" height="64"><br><sub>DNS Zones</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/security/10245-icon-service-Key-Vaults.svg" width="64" height="64"><br><sub>Key Vaults</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/identity/10227-icon-service-Managed-Identities.svg" width="64" height="64"><br><sub>Managed Identities</sub></td></tr>
<tr><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/management%20%2B%20governance/00001-icon-service-Monitor.svg" width="64" height="64"><br><sub>Monitor</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/analytics/00009-icon-service-Log-Analytics-Workspaces.svg" width="64" height="64"><br><sub>Log Analytics Workspaces</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/devops/10042-icon-service-API-Management-Services.svg" width="64" height="64"><br><sub>API Management Services</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/integration/10836-icon-service-Azure-Service-Bus.svg" width="64" height="64"><br><sub>Azure Service Bus</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/analytics/00039-icon-service-Event-Hubs.svg" width="64" height="64"><br><sub>Event Hubs</sub></td><td align="center" width="120"><img src="src/Azure_Public_Service_Icons/Icons/ai%20%2B%20machine%20learning/03438-icon-service-Azure-OpenAI.svg" width="64" height="64"><br><sub>Azure OpenAI</sub></td></tr>
</table>

24 of 645 shown. Every icon is in [`src/`](src/). Changes are in [`CHANGELOG.md`](CHANGELOG.md).

## License

The icons are from Microsoft's [Azure Architecture Icons](https://learn.microsoft.com/azure/architecture/icons/). Microsoft permits their use in architectural diagrams, training materials or documentation, and does not allow modifying them; see Microsoft's icon terms. Azure and the Azure product names are trademarks of Microsoft.

## Sources

Paths are relative to [`src/`](src/). Imported files are refreshed by
`uv run runax-icons import azure`; the rest are kept by hand.

| Files | Source | Notes |
| ----- | ------ | ----- |
| `**` | https://arch-center.azureedge.net/icons/Azure_Public_Service_Icons_V25.zip | largest size of each icon, white-only ones skipped |

## Use

Build with `uv run runax-icons build` from the repo root, then in Excalidraw:

1. Open `runax-azure.excalidraw` (or paste icons from it into your drawing), so the images are loaded.
2. Import `runax-azure.excalidrawlib` from the library panel.

Excalidraw doesn't store images in library files, so library icons render only once the
drawing contains them. See the [main README](../README.md).

<!-- Generated by runax-icons build; edit pack.yml instead. -->
