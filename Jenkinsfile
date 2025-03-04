pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/VETRI9876/Interactive-Digit-Reconstruction-Using-a-Boltzmann-Machine.git'
        IMAGE_NAME = 'interactivedigitreconstruction'
        ACR_NAME = 'vetri.azurecr.io' 
        AKS_CLUSTER = 'devops-aks-cluster'
        AKS_RESOURCE_GROUP = 'myResourceGroup'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: "$REPO_URL"
            }
        }

        stage('Verify Git Branch') {
            steps {
                sh 'git branch -a'
                sh 'git status'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("$ACR_NAME/$IMAGE_NAME")
                }
            }
        }

        stage('Push to Azure ACR') {
            steps {
                sh 'docker login $ACR_NAME'
                sh 'docker push $ACR_NAME/$IMAGE_NAME'
            }
        }

        stage('Deploy to AKS') {
            steps {
                script {
                    sh 'az aks get-credentials --resource-group $AKS_RESOURCE_GROUP --name $AKS_CLUSTER'
                    sh 'kubectl apply -f deployment.yaml'
                }
            }
        }
    }

    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
