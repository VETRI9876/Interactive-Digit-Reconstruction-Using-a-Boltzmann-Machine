pipeline {
    agent any
    environment {
        ACR_NAME = "vetri.azurecr.io"
        IMAGE_NAME = "fastapi-app"
        TAG = "latest"
        RESOURCE_GROUP = "myResourceGroup"
        AKS_CLUSTER = "devops-aks-cluster"
        LOCATION = "eastus"
    }
    stages {
        stage('Checkout Code') {
            steps {
                git 'https://github.com/VETRI9876/Interactive-Digit-Reconstruction-Using-a-Boltzmann-Machine.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t $ACR_NAME/$IMAGE_NAME:$TAG ."
            }
        }

        stage('Azure Login') {
            steps {
                withCredentials([string(credentialsId: 'AZURE_CREDENTIALS', variable: 'AZURE_CREDENTIALS')]) {
                    sh "az login --service-principal -u <client-id> -p <client-secret> --tenant <tenant-id>"
                }
            }
        }

        stage('Create Resource Group & ACR') {
            steps {
                sh """
                    az group create --name $RESOURCE_GROUP --location $LOCATION
                    az acr create --resource-group $RESOURCE_GROUP --name vetri --sku Basic --admin-enabled true
                """
            }
        }

        stage('Push to Azure Container Registry') {
            steps {
                withCredentials([string(credentialsId: 'AZURE_CREDENTIALS', variable: 'AZURE_CREDENTIALS')]) {
                    sh """
                        az acr login --name vetri
                        docker tag $ACR_NAME/$IMAGE_NAME:$TAG vetri.azurecr.io/$IMAGE_NAME:$TAG
                        docker push vetri.azurecr.io/$IMAGE_NAME:$TAG
                    """
                }
            }
        }

        stage('Create AKS Cluster') {
            steps {
                sh """
                    az aks create --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --node-count 2 \
                    --enable-addons monitoring --enable-managed-identity --network-plugin azure \
                    --generate-ssh-keys
                """
            }
        }

        stage('Attach ACR to AKS') {
            steps {
                sh "az aks update --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --attach-acr vetri"
            }
        }

        stage('Deploy to AKS') {
            steps {
                withCredentials([string(credentialsId: 'AZURE_CREDENTIALS', variable: 'AZURE_CREDENTIALS')]) {
                    sh """
                        az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER
                        kubectl apply -f deployment.yaml
                        kubectl apply -f service.yaml
                    """
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                sh """
                    kubectl get pods
                    kubectl get svc fastapi-service
                """
            }
        }
    }
}
