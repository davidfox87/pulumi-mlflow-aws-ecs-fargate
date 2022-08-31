# AWS base images for Lambda

You can use one of the AWS base images for Lambda to build the container image for your function code. The base images are preloaded with a language runtime and other components required to run a container image on Lambda. You add your function code and dependencies to the base image and then package it as a container image.

AWS will maintain and regularly update these images. In addition, AWS will release AWS base images when any new managed runtime becomes available. 


Lambda provides a runtime interface emulator (RIE) for you to test your function locally.
https://docs.aws.amazon.com/lambda/latest/dg/images-test.html#images-test-limitations