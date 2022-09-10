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

To deploy kubernetes dashboard, follow these steps
1. Apply the dashboard manifest to your cluster
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.4.0/aio/deploy/recommended.yaml --kubeconfig ./kubeconfig.json
```

2. Create an eks-admin service account and cluster role binding that you can use to securely connect to the dashboard with admin-level permissions
```
kubectl apply -f eks-admin-service-account.yaml --kubeconfig ./kubeconfig.json
```

3. Now that the Kubernetes Dashboard is deployed to your cluster, and you have an administrator service account that you can use to view and control your cluster, you can connect to the dashboard with that service account.
Retrieve an authentication token for the eks-admin service account.

```
kubectl -n kube-system describe secret $(kubectl -n kube-system get secret --kubeconfig ./kubeconfig.json | grep eks-admin | awk '{print $1}')
```
Copy the token, which you will use to connect to the dashboard

4. Start the kubectl proxy
```
kubectl proxy --kubeconfig ./kubeconfig.json
```
5. To access the dashboard endpoint, open the following link with a web browser:
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#!/login

6. Choose Token, paste the authentication-token output from the previous command into the Token field, and choose SIGN IN.



# Cleanup
To delete the Service:
```kubectl delete services my-nginx --kubeconfig ./kubeconfig.json```

To delete the Deployment, the ReplicaSet, and the Pods that are running the Hello World application:

```kubectl delete deployment my-nginx --kubeconfig ./kubeconfig.json```

To destroy the EKS cluster
``` pulumi destroy ```

