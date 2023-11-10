pipeline {
    agent any
    stages {
        stage('Giving Permissions') {
            steps {
                sh '''
                chmod +x permission.sh
                ./permission.sh
                '''
            }
        }
        stage('Setup Python Virtual ENV for dependencies') {
            steps {
                sh '''
                chmod +x env-setup.sh
                ./env-setup.sh
                '''
            }
        }
        stage('Setup Supervisor Setup') {
            steps {
                sh '''
                chmod +x supervisor.sh
                ./supervisor.sh
                '''
            }
        }
        stage('Setup NGINX') {
            steps {
                sh '''
                chmod +x nginx.sh
                ./nginx.sh
                '''
            }
        }
    }
}
