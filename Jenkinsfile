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
                sh '''
                # Install Docker if not installed
                if ! command -v docker &> /dev/null; then
                    echo "Installing Docker..."
                    sudo apt update
                    sudo apt install -y docker.io
                    sudo systemctl start docker
                    sudo systemctl enable docker
                    sudo usermod -aG docker jenkins
                else
                    echo "Docker is already installed."
                fi

                # Install Azure CLI if not installed
                if ! command -v az &> /dev/null; then
                    echo "Installing Azure CLI..."
                    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
                else
                    echo "Azure CLI is already installed."
                fi
                '''
            }
        }

        stage('Checkout Code') {
            steps {
                script {
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: '*/main']],
                        userRemoteConfigs: [[url: 'https://github.com/VETRI9876/Interactive-Digit-Reconstruction-Using-a-Boltzmann-Machine.git']]
                    ])
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
                withCredentials([usernamePassword(credentialsId: 'AZURE_CREDENTIALS', usernameVariable: 'AZURE_USER', passwordVariable: 'AZURE_PASS')]) {
                    sh "az login --service-principal -u $AZURE_USER -p $AZURE_PASS --tenant <your-tenant-id>"
                }
            }
        }

        stage('Create Resource Group & ACR (if not exists)') {
            steps {
                sh '''
                if ! az group show --name $RESOURCE_GROUP &>/dev/null; then
                    az group create --name $RESOURCE_GROUP --location $LOCATION
                else
                    echo "Resource group $RESOURCE_GROUP already exists."
                fi

                if ! az acr show --name vetri &>/dev/null; then
                    az acr create --resource-group $RESOURCE_GROUP --name vetri --sku Basic --admin-enabled true
                else
                    echo "ACR vetri already exists."
                fi
                '''
            }
        }

        stage('Push to Azure Container Registry') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'AZURE_CREDENTIALS', usernameVariable: 'AZURE_USER', passwordVariable: 'AZURE_PASS')]) {
                    sh '''
                    az acr login --name vetri
                    docker tag $IMAGE_NAME:$TAG $ACR_NAME/$IMAGE_NAME:$TAG
                    docker push $ACR_NAME/$IMAGE_NAME:$TAG
                    '''
                }
            }
        }

        stage('Create AKS Cluster (if not exists)') {
            steps {
                sh '''
                if ! az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER &>/dev/null; then
                    az aks create --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --node-count 2 \
                    --enable-addons monitoring --enable-managed-identity --network-plugin azure \
                    --generate-ssh-keys
                else
                    echo "AKS Cluster $AKS_CLUSTER already exists."
                fi
                '''
            }
        }

        stage('Attach ACR to AKS') {
            steps {
                sh "az aks update --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --attach-acr vetri"
            }
        }

        stage('Deploy to AKS') {
            steps {
                sh '''
                az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER
                kubectl apply -f deployment.yaml
                kubectl apply -f service.yaml
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                kubectl get pods
                kubectl get svc fastapi-service
                '''
            }
        }
    }

    post {
        failure {
            echo "Pipeline failed! Please check the logs."
        }
    }
}
