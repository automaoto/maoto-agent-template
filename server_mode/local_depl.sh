#!/bin/bash

# Ensure we have the Docker environment from Minikube
MINIKUBE_PROFILE="minikube-cluster-intro"
eval $(minikube docker-env --profile $MINIKUBE_PROFILE)

# Define variables
PROJECT_DIR="$(dirname "$0")/src"

# Generate BUILD_NUMBER and GIT_COMMIT
BUILD_NUMBER=$(date +%Y%m%d%H%M%S)  # Example: use timestamp as build number
GIT_COMMIT=$(git rev-parse --short HEAD)  # Get the short commit hash

TARGET_DIR=./src/apiinterfaces/maoto-agent
DEV="false" # TODO: load env variable from env var file

# Build and push images for all Dockerfiles in subdirectories
export DOCKER_CLI_HINTS=false
for DOCKERFILE in $(find $PROJECT_DIR -type f -name Dockerfile); do
    echo "Building image for $DOCKERFILE..."
    DIR=$(dirname $DOCKERFILE)
    IMAGE_NAME=$(basename $DIR)
    IMAGE_TAG="local_$BUILD_NUMBER-$GIT_COMMIT"
    
    # Check if the directory name is "apiinterfaces" and DEV is set to true
    if [ "$IMAGE_NAME" = "apiinterfaces" ]; then
        mkdir -p "$TARGET_DIR"
    fi
    if [ "$IMAGE_NAME" = "apiinterfaces" ] && [ "$DEV" = "true" ]; then
        echo "Copying maoto-agent..."
        rsync -a --delete ~/Developer/maoto-agent/ "$TARGET_DIR"
        docker build --build-arg USE_LOCAL_PACKAGE_VERSION=true -q -t "$IMAGE_NAME:$IMAGE_TAG" $DIR
    else
        docker build -q -t "$IMAGE_NAME:$IMAGE_TAG" $DIR
    fi
done

# Upgrade and install Helm chart with the image tag
helm upgrade --install kubernetes-server ./kubernetes \
    --set image.tag="$IMAGE_TAG"
