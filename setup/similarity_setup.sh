#!/bin/bash -e

# This script installs and configures depedencies for the similarity feature
# The similarity feature is optional, so this script is not run by default on
# setup. You will have to run this after setup to enable the similarity feature.
set -e
PROJECT_ROOT=$PWD
RUN_DIR=$PROJECT_ROOT/run
BATCH_LOG=$RUN_DIR/batch.log

# Install python libraries
pip install numpy
pip install scipy
pip install pyyaml
pip install nltk
