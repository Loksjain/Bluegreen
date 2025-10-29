pipeline {
  agent any

  environment {
    DOCKERHUB_CREDS = credentials('dockerhub-creds')
    DOCKER_USER     = 'loksjain25'
    IMAGE_REPO      = "${DOCKER_USER}/bluegreen"
    KUBE_NAMESPACE  = 'bluegreen'
  }

  parameters {
    choice(name: 'ACTIVE_COLOR', choices: ['blue','green'], description: 'Currently live color')
  }

  stages {

    stage('Checkout') {
      steps {
        echo "🔄 Checking out code from GitHub..."
        git branch: 'main', url: 'https://github.com/Loksjain/Bluegreen.git'
      }
    }

    stage('Build & Push Docker Image') {
  steps {
    script {
      // ✅ Automatically build the opposite (target) color
      def TARGET_COLOR = (params.ACTIVE_COLOR == 'blue') ? 'green' : 'blue'
      def TAG = "${TARGET_COLOR}-${env.BUILD_NUMBER}"

      echo "🐳 Building and pushing Docker image: ${IMAGE_REPO}:${TAG}"

      sh """
        echo "🔐 Logging into Docker Hub..."
        docker login -u $DOCKERHUB_CREDS_USR -p $DOCKERHUB_CREDS_PSW
        echo "🏗️  Building image..."
        docker build -t $IMAGE_REPO:$TAG app
        echo "📤 Pushing image to Docker Hub..."
        docker push $IMAGE_REPO:$TAG
      """
    }
  }
}


    stage('Deploy to Kubernetes') {
  steps {
    script {
      def TARGET_COLOR = (params.ACTIVE_COLOR == 'blue') ? 'green' : 'blue'
      def TAG = "${TARGET_COLOR}-${env.BUILD_NUMBER}"
      def DEPLOY = "${TARGET_COLOR}-deploy"

      echo "🚀 Deploying ${DEPLOY} with tag ${TAG}"

      // ✅ FIXED: switched to triple double quotes so variables expand
      sh """
        echo "📦 Updating deployment..."
        kubectl -n ${KUBE_NAMESPACE} set image deployment/${DEPLOY} web=${IMAGE_REPO}:${TAG}
        kubectl -n ${KUBE_NAMESPACE} set env deployment/${DEPLOY} VERSION=${TAG}
        echo "⏳ Waiting for rollout to complete..."
        kubectl -n ${KUBE_NAMESPACE} rollout status deployment/${DEPLOY} --timeout=120s
      """
    }
  }
}


    stage('Switch Traffic (Blue ↔ Green)') {
      steps {
        script {
          def TARGET_COLOR = (params.ACTIVE_COLOR == 'blue') ? 'green' : 'blue'
          echo "🌐 Switching Service traffic to ${TARGET_COLOR}"

          writeFile file: 'patch.json', text: """{"spec":{"selector":{"app":"bluegreen","color":"${TARGET_COLOR}"}}}"""
          sh 'kubectl -n bluegreen patch service bluegreen-svc --type merge --patch-file patch.json'

          echo "✅ Traffic switched to ${TARGET_COLOR}"
        }
      }
    }

    stage('Verify Deployment') {
      steps {
        echo "🧪 Verifying active service response..."
        sh '''
          kubectl -n ${KUBE_NAMESPACE} run curl-test \
            --image=curlimages/curl:8.7.1 \
            --rm -i --restart=Never -- \
            curl -s http://bluegreen-svc
        '''
      }
    }
  }

  post {
    success {
      echo "✅ Blue-Green Deployment completed successfully!"
    }
    failure {
      echo "❌ Deployment failed — check console logs for details."
    }
  }
}
