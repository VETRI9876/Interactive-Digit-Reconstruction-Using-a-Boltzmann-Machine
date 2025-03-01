pipeline {
    agent any

    environment {
        ACR_NAME = "vetri.azurecr.io"
        IMAGE_NAME = "fastapi-app"
        TAG = "latest"
        RESOURCE_GROUP = "myResourceGroup"
        AKS_CLUSTER = "devops-aks-cluster"
        GIT_REPO = "https://github.com/VETRI9876/Interactive-Digit-Reconstruction-Using-a-Boltzmann-Machine.git"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: "${GIT_REPO}"
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh """
                        echo "Building Docker Image..."
                        docker build -t $ACR_NAME/$IMAGE_NAME:$TAG .
                    """
                }
            }
        }

        stage('Push to Azure Container Registry') {
            steps {
                withCredentials([azureServicePrincipal('AZURE_CREDENTIALS')]) {
                    script {
                        sh """
                            echo "Logging into Azure..."
                            az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
                            
                            echo "Logging into Azure Container Registry..."
                            az acr login --name vetri
                            
                            echo "Tagging and pushing the Docker image..."
                            docker tag $ACR_NAME/$IMAGE_NAME:$TAG $ACR_NAME/$IMAGE_NAME:$TAG
                            docker push $ACR_NAME/$IMAGE_NAME:$TAG
                            
                            echo "Listing available repositories in ACR..."
                            az acr repository list --name vetri --output table
                            
                            echo "Showing available tags for fastapi-app..."
                            az acr repository show-tags --name vetri --repository fastapi-app --output table
                        """
                    }
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                withCredentials([azureServicePrincipal('AZURE_CREDENTIALS')]) {
                    script {
                        sh """
                            echo "Retrieving AKS credentials..."
                            az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER
                            
                            echo "Applying Kubernetes deployment..."
                            kubectl apply -f deployment.yaml
                            
                            echo "Applying Kubernetes service..."
                            kubectl apply -f service.yaml
                        """
                    }
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    sh """
                        echo "Checking running pods..."
                        kubectl get pods
                        
                        echo "Checking services..."
                        kubectl get svc fastapi-service
                    """
                }
            }
        }
    }

    post {
        failure {
            script {
                echo "Build failed! Check logs for errors."
            }
        }
        success {
            script {
                echo "Deployment successful!"
            }
        }
    }
}
