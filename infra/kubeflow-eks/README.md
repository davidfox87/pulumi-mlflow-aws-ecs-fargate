https://aws.amazon.com/premiumsupport/knowledge-center/eks-cluster-connection/

After you create your Amazon EKS cluster, you must configure your kubeconfig file

You can specify path to the kubenetes cluster configby setting the KUBECONFIG (from the Kubernetes website) environment variable, or with the following --kubeconfig option:

pulumi stack output kubeconfig > kubeconfig.json

kubectl get pods --kubeconfig ./kubeconfig.json

or KUBECONFIG=./kubeconfig.json && kubectl get pods

I prefer the --kubeconfig argument

kubectl get deployments --kubeconfig ./kubeconfig.json

kubectl get svc --kubeconfig ./kubeconfig.json

kubectl get deployments --kubeconfig ./kubeconfig.json --namespace=$(pulumi stack output namespace) 
