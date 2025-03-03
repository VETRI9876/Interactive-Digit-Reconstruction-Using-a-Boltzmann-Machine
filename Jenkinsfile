pipeline {
    agent any

    environment {
        ACR_NAME = 'myACR'
        IMAGE_NAME = 'myapp'
        AKS_CLUSTER = 'myAKSCluster'
        RESOURCE_GROUP = 'myResourceGroup'
        ACR_LOGIN_SERVER = "${ACR_NAME}.azurecr.io"
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t $IMAGE_NAME:latest .'
                }
            }
        }

        stage('Tag & Push to ACR') {
            steps {
                script {
                    sh 'docker tag $IMAGE_NAME:latest $ACR_LOGIN_SERVER/$IMAGE_NAME:latest'
                    sh 'az acr login --name $ACR_NAME'
                    sh 'docker push $ACR_LOGIN_SERVER/$IMAGE_NAME:latest'
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                script {
                    sh 'az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_CLUSTER'
                    sh 'kubectl apply -f deployment.yaml'
                }
            }
        }
    }
}
