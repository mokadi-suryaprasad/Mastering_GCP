# Cloud Run

## What is Cloud Run?

Google Cloud Run is a service that lets you run your applications in
*containers* without managing servers. You only provide your code inside
a container, and Cloud Run takes care of running it for you.

## Why Cloud Run?

-   No servers to manage\
-   Automatically scales up when traffic increases\
-   Scales down to zero when no one is using it\
-   Very fast and easy to deploy\
-   Pay only when your service is running

## How it works

1.  You create a Docker container for your app\
2.  You push the container to Google Artifact Registry\
3.  You deploy the container on Cloud Run\
4.  Cloud Run gives you a public URL

## Benefits

-   Supports any language (Python, Java, Go, Node.js, etc.)\
-   Very cheap because it scales to zero\
-   Secure by default\
-   Works well for APIs, microservices, and background tasks

## Example Use Cases

-   REST API services\
-   Webhooks\
-   Backend microservices\
-   Scheduled jobs (with Cloud Scheduler)\
-   Lightweight websites

## Simple Definition

Cloud Run is a serverless service that runs your containerized
applications automatically with no servers and no manual scaling.
