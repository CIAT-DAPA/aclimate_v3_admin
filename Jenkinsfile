def remote = [:]

pipeline {
    agent any

        environment {
            host = credentials('aclimate_v3_host')
        }

    stages {
        stage('Ssh to connect Melisa server') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'aclimate_v3_deploy', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                        try {
                            remote.user = USER
                            remote.password = PASS
                            remote.host = host
                            remote.name = host
                            remote.allowAnyHosts = true

                            sshCommand remote: remote, command: "echo 'Connection successful!'"
                        } catch (Exception e) {
                            echo "SSH Connection Error: ${e.message}"
                            error("Failed to establish SSH connection: ${e.message}")
                        }
                    }
                }
            }
        }
        stage('Update API code') {
            steps {
                script {
                    try {
                        sshCommand remote: remote, command: """
                            cd /var/www/aclimate/aclimate_v3_admin/aclimate_v3_admin
                            git checkout main
                            git pull origin main
                            source /opt/anaconda3/etc/profile.d/conda.sh
                            conda activate /home/scalderon/.conda/envs/aclimate_v3_admin
                            pip install -r src/requirements.txt
                        """
                    } catch (Exception e) {
                        echo "Git Pull Error: ${e.message}"
                        error("Failed to update code: ${e.message}")
                    }
                }
            }
        }
        stage('Restart API service') {
            steps {
                script {
                    try {
                        sshCommand remote: remote, command: """
                            cd /var/www/aclimate/aclimate_v3_admin/aclimate_v3_admin/src
                            source /opt/anaconda3/etc/profile.d/conda.sh
                            conda activate /home/scalderon/.conda/envs/aclimate_v3_admin
                            fuser -k 3003/tcp || true
                            nohup gunicorn -w 4 -b 0.0.0.0:3003 run:app > /var/www/aclimate/aclimate_v3_admin/aclimate_v3_admin/admin.log 2>&1 &
                        """
                    } catch (Exception e) {
                        echo "API Restart Error: ${e.message}"
                        error("Failed to restart API: ${e.message}")
                    }
                }
            }
        }
    }

    post {
        failure {
            script {
                echo "Pipeline failed"
            }
        }
        success {
            script {
                echo 'API deployed successfully!'
            }
        }
    }
}
 