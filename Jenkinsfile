pipeline {
    agent any

    environment {
        REPO_URL = 'https://github.com/VETRI9876/Interactive-Digit-Reconstruction-Using-a-Boltzmann-Machine.git'
        IMAGE_NAME = 'interactivedigitreconstruction'
        ACR_NAME = 'youracrname.azurecr.io' // Replace with your ACR name
        AKS_CLUSTER = 'youraksclustername'  // Replace with your AKS cluster name
        AKS_RESOURCE_GROUP = 'yourresourcegroup' // Replace with your resource group
        DOCKER_CREDENTIAL_ID = 'acr-docker-credentials' // Jenkins credentials ID for ACR
    }

    stages {
        stage('Clone Repository') {
            steps {
                git url: "$REPO_URL"
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
                withCredentials([usernamePassword(credentialsId: "$DOCKER_CREDENTIAL_ID", 
                                usernameVariable: 'ACR_USERNAME', 
                                passwordVariable: 'ACR_PASSWORD')]) {
                    sh 'echo $ACR_PASSWORD | docker login $ACR_NAME --username $ACR_USERNAME --password-stdin'
                    sh 'docker push $ACR_NAME/$IMAGE_NAME'
                }
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
