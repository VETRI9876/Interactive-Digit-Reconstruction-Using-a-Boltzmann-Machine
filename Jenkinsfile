pipeline {
    agent any
    environment {
        ACR_NAME = "vetri.azurecr.io"
        IMAGE_NAME = "fastapi-app"
        TAG = "latest"
        RESOURCE_GROUP = "myResourceGroup"
        AKS_CLUSTER = "myAKSCluster"
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

        stage('Push to Azure Container Registry') {
            steps {
                withCredentials([string(credentialsId: 'AZURE_CREDENTIALS', variable: 'AZURE_CREDENTIALS')]) {
                    sh "az login --service-principal -u <client-id> -p <client-secret> --tenant <tenant-id>"
                    sh "az acr login --name vetri"
                    sh "docker push $ACR_NAME/$IMAGE_NAME:$TAG"
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                withCredentials([string(credentialsId: 'AZURE_CREDENTIALS', variable: 'AZURE_CREDENTIALS')]) {
                    sh "az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER"
                    sh "kubectl apply -f deployment.yaml"
                    sh "kubectl apply -f service.yaml"
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                sh "kubectl get pods"
                sh "kubectl get svc fastapi-service"
            }
        }
    }
}
