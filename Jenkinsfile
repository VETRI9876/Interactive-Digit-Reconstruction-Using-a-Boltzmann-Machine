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
        stage('Install Dependencies') {
            steps {
                script {
                    sh """
                        echo 'Installing Docker...'
                        sudo apt update
                        command -v docker || (echo 'yourpassword' | sudo -S apt install -y docker.io)
                        sudo systemctl start docker
                        sudo systemctl enable docker
                    """
                }
            }
        }

        stage('Checkout Code') {
            steps {
                script {
                    checkout scm
                }
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
                    sh "echo $AZURE_CREDENTIALS | az login --service-principal --username <appId> --password <password> --tenant <tenantId>"
                }
            }
        }

        stage('Create Resource Group & ACR (if not exists)') {
            steps {
                script {
                    def acr_exists = sh(script: "az acr show --name vetri --query 'name' --output tsv || echo ''", returnStdout: true).trim()
                    if (acr_exists == "") {
                        sh """
                            az group create --name $RESOURCE_GROUP --location $LOCATION
                            az acr create --resource-group $RESOURCE_GROUP --name vetri --sku Basic --admin-enabled true
                        """
                    } else {
                        echo "ACR already exists, skipping creation."
                    }
                }
            }
        }

        stage('Push to Azure Container Registry') {
            steps {
                withCredentials([string(credentialsId: 'AZURE_CREDENTIALS', variable: 'AZURE_CREDENTIALS')]) {
                    sh """
                        az acr login --name vetri
                        docker tag $IMAGE_NAME:$TAG vetri.azurecr.io/$IMAGE_NAME:$TAG
                        docker push vetri.azurecr.io/$IMAGE_NAME:$TAG
                    """
                }
            }
        }

        stage('Create AKS Cluster (if not exists)') {
            steps {
                script {
                    def aks_exists = sh(script: "az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --query 'name' --output tsv || echo ''", returnStdout: true).trim()
                    if (aks_exists == "") {
                        sh """
                            az aks create --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --node-count 2 \
                            --enable-addons monitoring --enable-managed-identity --network-plugin azure \
                            --generate-ssh-keys
                        """
                    } else {
                        echo "AKS cluster already exists, skipping creation."
                    }
                }
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

    post {
        failure {
            echo "Pipeline failed! Please check the logs."
        }
    }
}
