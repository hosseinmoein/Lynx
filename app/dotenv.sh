#!/bin/bash
PROJECT="dependency_graph/"
PROJECT_FOLDER="$(git rev-parse --show-toplevel)/projects/$PROJECT/app"
echo -n "TZ=UTC
" > ${PROJECT_FOLDER}/.env
