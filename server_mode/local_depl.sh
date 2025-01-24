#!/bin/bash

# Get the name of the current repository and include it into the namespace
REPO_URL="$(git config --get remote.origin.url)"
REPO_NAME="$(basename -s .git "$REPO_URL")"
NAMESPACE="${REPO_NAME}-namespace"

# Path variables
ABS_SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$ABS_SCRIPT_DIR/src"

# Configuration variables defaults
BETA_MAOTO_PACKAGE="false"
LOCAL_MAOTO_PACKAGE="false"
MAOTO_PACKAGE_PATH=""
APIINTERFACES_LOADBALANCER=false

# Load environment variables from .env and .secrets files
if [ -f "$ABS_SCRIPT_DIR/.env_server" ]; then
  set -a
  source "$ABS_SCRIPT_DIR/.env_server"
  set +a
fi

if [ -f "$ABS_SCRIPT_DIR/.secrets_server" ]; then
  set -a
  source "$ABS_SCRIPT_DIR/.secrets_server"
  set +a
fi

# Check if LOCAL_MAOTO_PACKAGE is set to true,
# then ensure that MAOTO_PACKAGE_PATH is set
if [ "$LOCAL_MAOTO_PACKAGE" = "true" ]; then
  if [ -z "$MAOTO_PACKAGE_PATH" ]; then
    echo "ERROR: LOCAL_MAOTO_PACKAGE is set to 'true' but MAOTO_PACKAGE_PATH is not defined."
    echo "Please define MAOTO_PACKAGE_PATH in your .env_server file."
    exit 1
  fi
fi

# Ensure we have the Docker environment from Minikube
eval $(minikube docker-env --profile cluster-server)

# Generate BUILD_NUMBER and GIT_COMMIT
BUILD_NUMBER=$(date +%Y%m%d%H%M%S)  # Example: use timestamp as build number
GIT_COMMIT=$(git rev-parse --short HEAD)  # Get the short commit hash

# Build and push images for all Dockerfiles in subdirectories
COPY_PACKAGE_TARGET_DIR="$ABS_SCRIPT_DIR/src/apiinterfaces/maoto-agent"
mkdir -p "$COPY_PACKAGE_TARGET_DIR" # Critical, since Dockerfile cant't reference non existing directories
export DOCKER_CLI_HINTS=false
for DOCKERFILE in $(find $PROJECT_DIR -type f -name Dockerfile); do
    echo "Building image for $DOCKERFILE..."
    DIR=$(dirname $DOCKERFILE)
    IMAGE_NAME=$(basename $DIR)
    IMAGE_TAG="local_$BUILD_NUMBER-$GIT_COMMIT"
    
    # Check if the directory name is "apiinterfaces" and local maoto-package is selected
    if [ "$IMAGE_NAME" = "apiinterfaces" ] && [ "$LOCAL_MAOTO_PACKAGE" = "true" ]; then
        echo "Copying maoto-agent..."
        rsync -a --delete $MAOTO_PACKAGE_PATH $COPY_PACKAGE_TARGET_DIR
        docker build --build-arg USE_LOCAL_PACKAGE_VERSION=true -t "$IMAGE_NAME:$IMAGE_TAG" $DIR
    else
        docker build --build-arg USE_BETA_PACKAGE_VERSION=$BETA_MAOTO_PACKAGE -t "$IMAGE_NAME:$IMAGE_TAG" $DIR
    fi
done

# Ensure the namespace exists
kubectl get namespace $NAMESPACE || kubectl create namespace $NAMESPACE

# Upgrade and install Helm chart with the image tag
helm upgrade --install kubernetes-server "$ABS_SCRIPT_DIR/kubernetes" \
    --namespace "$NAMESPACE" \
    --set image.tag="$IMAGE_TAG" \
    --set apiinterfaces.loadbalancer=$APIINTERFACES_LOADBALANCER
