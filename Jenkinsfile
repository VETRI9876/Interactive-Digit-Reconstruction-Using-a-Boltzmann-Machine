pipeline {
    agent any
    
    environment {
        IMAGE_NAME = 'digit-reconstruction-app'
        DOCKER_REGISTRY = 'docker.io/vetri20' // Replace with your Docker registry
        GIT_REPO = 'https://github.com/VETRI9876/Interactive-Digit-Reconstruction-Using-a-Boltzmann-Machine.git'
    }
    
    stages {
        stage('Clone Repository') {
            steps {
                echo 'Cloning repository...'
                git url: "${GIT_REPO}", branch: 'main'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    docker.build("${IMAGE_NAME}")
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                sh 'docker run --rm ${IMAGE_NAME} pytest'
            }
        }

        stage('Push to Docker Registry') {
            steps {
                echo 'Pushing image to Docker registry...'
                script {
                    docker.withRegistry("${DOCKER_REGISTRY}", 'docker-credentials-id') {
                        docker.image("${IMAGE_NAME}").push('latest')
                    }
                }
            }
        }

        stage('Deploy Application') {
            steps {
                echo 'Deploying application...'
                sh 'kubectl apply -f deployment.yaml'
                sh 'kubectl apply -f service.yaml'
            }
        }
    }
    
    post {
        success {
            echo 'Deployment completed successfully!'
        }
        failure {
            echo 'Deployment failed!'
        }
    }
}
