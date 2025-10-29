pipeline {
  agent any

  environment {
    DOCKERHUB_CREDS = credentials('dockerhub-creds')    // create in Jenkins
    DOCKER_USER     = 'loksjain25'                       // <— change if needed
    IMAGE_REPO      = "${DOCKER_USER}/bluegreen"
    KUBE_NAMESPACE  = 'bluegreen'
    APP_NAME        = 'bluegreen'                         // common app label
  }

  parameters {
    choice(name: 'ACTIVE_COLOR', choices: ['blue','green'], description: 'Current live color (what Service points to now)')
    booleanParam(name: 'SWITCH_TRAFFIC', defaultValue: true, description: 'Switch traffic to the newly deployed color after health check')
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Docker Build & Push (blue/green)') {
      steps {
        script {
          sh """
            docker login -u ${DOCKERHUB_CREDS_USR} -p ${DOCKERHUB_CREDS_PSW}
            # Build blue (tagged with BUILD_NUMBER)
            docker build -t ${IMAGE_REPO}:blue-${BUILD_NUMBER} app
            # Rebuild green with a tiny label change to avoid cache (optional)
            docker build --build-arg CACHE_BUSTER=${BUILD_NUMBER} -t ${IMAGE_REPO}:green-${BUILD_NUMBER} app

            docker push ${IMAGE_REPO}:blue-${BUILD_NUMBER}
            docker push ${IMAGE_REPO}:green-${BUILD_NUMBER}
          """
        }
      }
    }

    stage('K8s Apply Base Manifests (once)') {
      when { expression { return params.BUILD_NUMBER == '1' } }  // first run only (or remove the when to always apply)
      steps {
        sh """
          kubectl apply -f k8s/namespace.yaml
          kubectl -n ${KUBE_NAMESPACE} apply -f k8s/service.yaml
          kubectl -n ${KUBE_NAMESPACE} apply -f k8s/deploy-blue.yaml
          kubectl -n ${KUBE_NAMESPACE} apply -f k8s/deploy-green.yaml
        """
      }
    }

    stage('Decide Target Color') {
      steps {
        script {
          // if active is blue, we deploy green; if active is green, we deploy blue
          TARGET_COLOR = (params.ACTIVE_COLOR == 'blue') ? 'green' : 'blue'
          echo "ACTIVE_COLOR=${params.ACTIVE_COLOR} -> TARGET_COLOR=${TARGET_COLOR}"
        }
      }
    }

    stage('Update Target Deployment Image & Version Env') {
      steps {
        script {
          def tag = "${TARGET_COLOR}-${BUILD_NUMBER}"
          def deploy = "${TARGET_COLOR}-deploy"
          sh """
            # set container image
            kubectl -n ${KUBE_NAMESPACE} set image deployment/${deploy} web=${IMAGE_REPO}:${tag}
            # update VERSION env (purely cosmetic on page)
            kubectl -n ${KUBE_NAMESPACE} set env deployment/${deploy} VERSION='${tag}'
            # wait for rollout
            kubectl -n ${KUBE_NAMESPACE} rollout status deployment/${deploy} --timeout=120s
          """
        }
      }
    }

    stage('Smoke Test Target Color') {
      steps {
        script {
          // simple in-cluster test via temporary pod curl
          def deploy = "${TARGET_COLOR}-deploy"
          sh """
            kubectl -n ${KUBE_NAMESPACE} run curl-test --image=curlimages/curl:8.7.1 --rm -i --restart=Never -- \
              sh -c 'sleep 2; echo -n "Health: "; curl -s http://$(kubectl -n ${KUBE_NAMESPACE} get pod -l color=${TARGET_COLOR},app=${APP_NAME} -o jsonpath="{.items[0].status.podIP}"):8080/healthz'
          """
        }
      }
    }

    stage('Switch Traffic (Service selector)') {
      when { expression { return params.SWITCH_TRAFFIC } }
      steps {
        script {
          sh """
            echo "Switching Service selector to color=${TARGET_COLOR}"
            kubectl -n ${KUBE_NAMESPACE} patch service bluegreen-svc -p '{ "spec": { "selector": { "app": "${APP_NAME}", "color": "${TARGET_COLOR}" } } }'
            kubectl -n ${KUBE_NAMESPACE} get svc bluegreen-svc -o wide
          """
        }
      }
    }
  }

  post {
    success {
      script {
        def old = (params.ACTIVE_COLOR == 'blue') ? 'blue' : 'green'
        def newColor = (params.ACTIVE_COLOR == 'blue') ? 'green' : 'blue'
        echo "Traffic now on: ${newColor}"
        // Optional: scale down the old color to save resources
        sh "kubectl -n ${KUBE_NAMESPACE} scale deploy/${old}-deploy --replicas=1 || true"
      }
    }
    failure {
      echo "Build failed. No traffic switch performed."
    }
  }
}
