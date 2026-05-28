#!/usr/bin/bash

USER="ethanbarath01@gmail.com"
NAME="ebarath"

git config --global user.email ${USER}
git config --global user.name ${NAME}

git config --global --list
