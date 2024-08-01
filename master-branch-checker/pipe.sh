#!/bin/sh
set -e

git config --global --add safe.directory /opt/atlassian/pipelines/agent/build

DIFF_FROM_MASTER=$(git rev-list --left-right --count HEAD...origin/master|awk '{print $2}')

echo "----------------------------------------------------------------------------------------------------"
echo "| SYKES BRANCH CHECKER                                                                             |"
echo "----------------------------------------------------------------------------------------------------"

if [ "$DIFF_FROM_MASTER" -gt "0" ]; then
    echo "| Your build has failed because master has $DIFF_FROM_MASTER more changes than your current branch |"
    echo "|                                                                                                  |"
    echo "| You need to run 'git pull origin master' on your branch!                                         |"
    echo "----------------------------------------------------------------------------------------------------"
    exit 1
else
    echo "| Your build is up to date with master well done!                                                   |"
    echo "----------------------------------------------------------------------------------------------------"
    exit 0
fi
