pipeline {
    agent any

    environment {
        DATABASE_URL = credentials('DATABASE_URL')
    }

    stages {

        stage('Clone Repository') {
            steps {
                git branch: 'main',
                url: 'https://github.com/Nikk434/Yaml-Yamaly.git'
            }
        }

        stage('Build Images') {
            steps {
                sh '''
                docker build -t fastapi-backend ./backend
                docker build -t next-frontend ./frontend
                '''
            }
        }

        stage('Stop Old Containers') {
            steps {
                sh '''
                docker stop fastapi-backend || true
                docker rm fastapi-backend || true

                docker stop next-frontend || true
                docker rm next-frontend || true
                '''
            }
        }

        stage('Run Backend Container') {
            steps {
                withCredentials([
                    string(credentialsId: 'DATABASE_URL', variable: 'DATABASE_URL')
                ]) {
                    sh '''
                    docker rm -f fastapi-backend || true

                    docker run -d \
                    --name fastapi-backend \
                    -p 8000:8000 \
                    -e DATABASE_URL=$DATABASE_URL \
                    fastapi-backend
                    '''
                }
            }
        }

        stage('Run Frontend Container') {
            steps {
                sh '''
                docker run -d \
                --name next-frontend \
                -p 3000:3000 \
                -e BACKEND_URL=http://3.7.30.50:8000 \
                next-frontend
                '''
            }
        }

        stage('Cleanup') {
            steps {
                sh 'docker image prune -f'
            }
        }
    }
}