pipeline {
    agent any

    environment {
        DATABASE_URL = credentials('DATABASE_URL')
    }

    stages {

        stage('Clone Repository') {
            steps {
                git branch: 'main',
                url: 'YOUR_GITHUB_REPO_URL'
            }
        }

        stage('Build Backend Image') {
            steps {
                dir('backend') {
                    sh 'docker build -t fastapi-backend .'
                }
            }
        }

        stage('Build Frontend Image') {
            steps {
                dir('frontend') {
                    sh 'docker build -t next-frontend .'
                }
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
                sh '''
                docker run -d \
                  --name fastapi-backend \
                  -p 8000:8000 \
                  -e DATABASE_URL="$DATABASE_URL" \
                  fastapi-backend
                '''
            }
        }

        stage('Run Frontend Container') {
            steps {
                sh '''
                docker run -d \
                  --name next-frontend \
                  -p 3000:3000 \
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