#!/bin/bash

# Permanent link to the `server_mode` directory in the repository
REPO_NAME="maoto-agent-template"
REPO_URL="https://github.com/automaoto/$REPO_NAME"
WORK_DIR="workdir"
REPO_DIR="$WORK_DIR/$REPO_NAME"
SERVER_TEMPLATE="server_mode"
SRC_DIR="src"

# if repo directory does not exist, clone the repository, otherwise pull the latest changes
if [ ! -d "$REPO_DIR" ]; then
    git clone --depth 1 --branch main "$REPO_URL" "./$WORK_DIR/$REPO_NAME"
else
    cd "$REPO_DIR" || exit
    git pull
    cd ../..
fi

# copy and overwrite the server_mode directory under workdir with cintent from repo_dir/server_mode
rsync -a --delete "./$REPO_DIR/$SERVER_TEMPLATE/" "./$WORK_DIR/$SERVER_TEMPLATE/"

# Copy the src folder to the target directory
rsync -a --delete "./$SRC_DIR/" "./$WORK_DIR/$SERVER_TEMPLATE/$SRC_DIR/"

# Copy the .env and .secrets files to the target directory only if they exist
if [ -f "./.env" ]; then
  rsync -a --delete "./.env" "./$WORK_DIR/"
fi
if [ -f "./.secrets" ]; then
  rsync -a --delete "./.secrets" "./$WORK_DIR/"
fi

# Run the local_depl.sh script in the target directory
bash "./$WORK_DIR/$SERVER_TEMPLATE/local_depl.sh"
