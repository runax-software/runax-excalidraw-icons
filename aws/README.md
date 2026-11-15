# AWS Architecture Icons

810 icons from [AWS Architecture Icons](https://aws.amazon.com/architecture/icons/), packaged as a Miro-style Excalidraw library:
each item is a 64px icon with an editable label below it, grouped together.

<table>
<tr><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Compute/64/Arch_Amazon-EC2_64.svg" width="64" height="64"><br><sub>Amazon EC2</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Compute/64/Arch_AWS-Lambda_64.svg" width="64" height="64"><br><sub>AWS Lambda</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Storage/64/Arch_Amazon-Simple-Storage-Service_64.svg" width="64" height="64"><br><sub>Amazon Simple Storage Service</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Databases/64/Arch_Amazon-RDS_64.svg" width="64" height="64"><br><sub>Amazon RDS</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Databases/64/Arch_Amazon-Aurora_64.svg" width="64" height="64"><br><sub>Amazon Aurora</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Databases/64/Arch_Amazon-DynamoDB_64.svg" width="64" height="64"><br><sub>Amazon DynamoDB</sub></td></tr>
<tr><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Databases/64/Arch_Amazon-ElastiCache_64.svg" width="64" height="64"><br><sub>Amazon ElastiCache</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Networking-Content-Delivery/64/Arch_Amazon-CloudFront_64.svg" width="64" height="64"><br><sub>Amazon CloudFront</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Networking-Content-Delivery/64/Arch_Amazon-Virtual-Private-Cloud_64.svg" width="64" height="64"><br><sub>Amazon Virtual Private Cloud</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Networking-Content-Delivery/64/Arch_Amazon-Route-53_64.svg" width="64" height="64"><br><sub>Amazon Route 53</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Networking-Content-Delivery/64/Arch_Elastic-Load-Balancing_64.svg" width="64" height="64"><br><sub>Elastic Load Balancing</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Networking-Content-Delivery/64/Arch_Amazon-API-Gateway_64.svg" width="64" height="64"><br><sub>Amazon API Gateway</sub></td></tr>
<tr><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Application-Integration/64/Arch_Amazon-Simple-Queue-Service_64.svg" width="64" height="64"><br><sub>Amazon Simple Queue Service</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Application-Integration/64/Arch_Amazon-Simple-Notification-Service_64.svg" width="64" height="64"><br><sub>Amazon Simple Notification Service</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Application-Integration/64/Arch_Amazon-EventBridge_64.svg" width="64" height="64"><br><sub>Amazon EventBridge</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Application-Integration/64/Arch_AWS-Step-Functions_64.svg" width="64" height="64"><br><sub>AWS Step Functions</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Containers/64/Arch_Amazon-Elastic-Container-Service_64.svg" width="64" height="64"><br><sub>Amazon Elastic Container Service</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Containers/64/Arch_Amazon-Elastic-Kubernetes-Service_64.svg" width="64" height="64"><br><sub>Amazon Elastic Kubernetes Service</sub></td></tr>
<tr><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Containers/64/Arch_AWS-Fargate_64.svg" width="64" height="64"><br><sub>AWS Fargate</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Management-Tools/64/Arch_Amazon-CloudWatch_64.svg" width="64" height="64"><br><sub>Amazon CloudWatch</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Security-Identity/64/Arch_AWS-Identity-and-Access-Management_64.svg" width="64" height="64"><br><sub>AWS Identity And Access Management</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Analytics/64/Arch_Amazon-Kinesis_64.svg" width="64" height="64"><br><sub>Amazon Kinesis</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Analytics/64/Arch_Amazon-SageMaker_64.svg" width="64" height="64"><br><sub>Amazon SageMaker</sub></td><td align="center" width="120"><img src="src/Architecture-Service-Icons_07312026/Arch_Artificial-Intelligence/64/Arch_Amazon-Bedrock_64.svg" width="64" height="64"><br><sub>Amazon Bedrock</sub></td></tr>
</table>

24 of 810 shown. Every icon is in [`src/`](src/).

## Sources

Paths are relative to [`src/`](src/). Imported files are refreshed by
`uv run build.py --import aws`; the rest are kept by hand.

| Files | Source | Notes |
| ----- | ------ | ----- |
| `**` | https://d1.awsstatic.com/onedam/marketing-channels/website/public/shared/architecture-icon-release/Icon-package_07312026.5846e92413caa21490223536cc97f1269e44fa92.zip | largest size of each icon, white-only ones skipped |

## Use

Build with `uv run build.py` from the repo root, then in Excalidraw:

1. Open `runax-aws.excalidraw` (or paste icons from it into your drawing), so the images are loaded.
2. Import `runax-aws.excalidrawlib` from the library panel.

Excalidraw doesn't store images in library files, so library icons render only once the
drawing contains them. See the [main README](../README.md).

<!-- Generated by build.py; edit pack.yml instead. -->
