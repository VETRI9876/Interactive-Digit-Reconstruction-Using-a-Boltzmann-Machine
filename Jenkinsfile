pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "my-app"
        RESOURCE_GROUP = "my-resource-group"
        ACR_NAME = "myacr"
        AKS_CLUSTER = "my-aks-cluster"
        DOCKER_REGISTRY = "myacr.azurecr.io"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/VETRI9876/Interactive-Digit-Reconstruction-Using-a-Boltzmann-Machine.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                echo "Updating System and Installing Docker..."
                echo "yourpassword" | sudo -S apt update && sudo apt install -y docker.io
                sudo usermod -aG docker jenkins
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                echo "Building Docker Image..."
                docker build -t $DOCKER_REGISTRY/$DOCKER_IMAGE:latest .
                '''
            }
        }

        stage('Azure Login') {
            steps {
                withCredentials([string(credentialsId: 'azure-service-principal', variable: 'AZURE_CREDENTIALS')]) {
                    sh '''
                    echo "Logging into Azure..."
                    az login --service-principal -u $AZURE_CREDENTIALS --tenant <TENANT_ID>
                    '''
                }
            }
        }

        stage('Create Resource Group & ACR (if not exists)') {
            steps {
                sh '''
                echo "Creating Azure Resource Group and ACR if not exists..."
                az group create --name $RESOURCE_GROUP --location eastus
                az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true || true
                '''
            }
        }

        stage('Push to Azure Container Registry') {
            steps {
                sh '''
                echo "Logging in to ACR..."
                az acr login --name $ACR_NAME
                echo "Pushing Docker image to ACR..."
                docker tag $DOCKER_IMAGE:latest $DOCKER_REGISTRY/$DOCKER_IMAGE:latest
                docker push $DOCKER_REGISTRY/$DOCKER_IMAGE:latest
                '''
            }
        }

        stage('Create AKS Cluster (if not exists)') {
            steps {
                sh '''
                echo "Creating AKS Cluster if not exists..."
                az aks show --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER || \
                az aks create --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER --node-count 1 --enable-managed-identity
                '''
            }
        }

        stage('Attach ACR to AKS') {
            steps {
                sh '''
                echo "Attaching ACR to AKS..."
                az aks update -n $AKS_CLUSTER -g $RESOURCE_GROUP --attach-acr $ACR_NAME
                '''
            }
        }

        stage('Deploy to AKS') {
            steps {
                sh '''
                echo "Deploying Application to AKS..."
                kubectl apply -f kubernetes/deployment.yaml
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh '''
                echo "Checking Deployment Status..."
                kubectl get pods -o wide
                '''
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
