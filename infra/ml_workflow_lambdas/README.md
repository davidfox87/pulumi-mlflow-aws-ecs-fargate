AWS Lambda Containers QuickStart
Ready to get up and running quickly right away?

Bootstrap a project $ pulumi new https://github.com/pulumi/apps/lambda-containers.
Add your Lambda’s logic to ./app/Dockerfile and ./app/index.js.
Deploy with $ pulumi up.
Test with $ curl $(pulumi stack output invokeUrl).