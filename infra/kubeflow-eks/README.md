https://aws.amazon.com/premiumsupport/knowledge-center/eks-cluster-connection/
https://www.youtube.com/watch?v=c4WcYjama6U

After you create your Amazon EKS cluster, you must configure your kubeconfig file

You can specify path to the kubenetes cluster configby setting the KUBECONFIG (from the Kubernetes website) environment variable, or with the following --kubeconfig option:
```
pulumi stack output kubeconfig > kubeconfig.json

kubectl get pods --kubeconfig ./kubeconfig.json
```

or 
```
KUBECONFIG=./kubeconfig.json && kubectl get pods
```
I prefer the ```--kubeconfig``` argument
```
kubectl get deployments --kubeconfig ./kubeconfig.json

kubectl get svc --kubeconfig ./kubeconfig.json

kubectl get deployments --kubeconfig ./kubeconfig.json --namespace=$(pulumi stack output namespace) 
```

To deploy an application:

```
kubectl apply -f sample_deployment.yaml --kubeconfig ./kubeconfig.json
kubectl apply -f sample_service.yaml --kubeconfig ./kubeconfig.json
```

To check nodes and pods in the cluster:

```
kubectl get nodes --kubeconfig ./kubeconfig.json
kubectl get pods -l app=my-nginx --output=wide --kubeconfig ./kubeconfig.json
```

# Cleanup
To delete the Service:
```kubectl delete services my-nginx --kubeconfig ./kubeconfig.json```

To delete the Deployment, the ReplicaSet, and the Pods that are running the Hello World application:

```kubectl delete deployment my-nginx --kubeconfig ./kubeconfig.json```

