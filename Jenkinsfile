pipeline {
    agent any

    environment {
        IMAGE_NAME = "DOCKER"
        RESOURCE_GROUP = "myResourceGroup"
        ACR_NAME = "vetri"
        AKS_CLUSTER = "devops-aks-cluster"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', 
                    url: 'https://github.com/VETRI9876/Interactive-Digit-Reconstruction-Using-a-Boltzmann-Machine.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    try {
                        sh '''
                        echo "Installing necessary dependencies..."
                        sudo apt update -y
                        sudo apt install -y docker.io
                        sudo usermod -aG docker jenkins
                        '''
                    } catch (Exception e) {
                        error "Dependency installation failed. Please check system permissions."
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh '''
                    echo "Building Docker image..."
                    docker build -t $IMAGE_NAME .
                    '''
                }
            }
        }

        stage('Azure Login') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'AZURE_SERVICE_PRINCIPAL', variable: 'AZURE_CREDENTIALS')]) {
                        sh '''
                        echo "Logging into Azure..."
                        az login --service-principal -u $AZURE_CREDENTIALS --tenant YOUR_TENANT_ID
                        '''
                    }
                }
            }
        }

        stage('Create Resource Group & ACR (if not exists)') {
            steps {
                script {
                    sh '''
                    az group create --name $RESOURCE_GROUP --location eastus || echo "Resource group exists"
                    az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic || echo "ACR exists"
                    az acr login --name $ACR_NAME
                    '''
                }
            }
        }

        stage('Push to Azure Container Registry') {
            steps {
                script {
                    sh '''
                    docker tag $IMAGE_NAME $ACR_NAME.azurecr.io/$IMAGE_NAME:v1
                    docker push $ACR_NAME.azurecr.io/$IMAGE_NAME:v1
                    '''
                }
            }
        }

        stage('Create AKS Cluster (if not exists)') {
            steps {
                script {
                    sh '''
                    az aks create --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --node-count 1 --generate-ssh-keys || echo "AKS cluster exists"
                    az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER
                    '''
                }
            }
        }

        stage('Attach ACR to AKS') {
            steps {
                script {
                    sh '''
                    az aks update --name $AKS_CLUSTER --resource-group $RESOURCE_GROUP --attach-acr $ACR_NAME
                    '''
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                script {
                    sh '''
                    kubectl apply -f deployment.yaml
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    sh '''
                    kubectl get pods
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline executed successfully! ✅"
        }
        failure {
            echo "Pipeline failed! Please check the logs. ❌"
        }
    }
}
