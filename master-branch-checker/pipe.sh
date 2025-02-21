#!/bin/sh
set -eo pipefail

git config --global --add safe.directory /opt/atlassian/pipelines/agent/build

BRANCH_NAME=$(git symbolic-ref refs/remotes/origin/HEAD --short)
DIFF_FROM_MASTER=$(git rev-list --left-right --count HEAD...$BRANCH_NAME|awk '{print $2}')

echo "----------------------------------------------------------------------------------------------------"
echo "| SYKES BRANCH CHECKER                                                                             |"
echo "----------------------------------------------------------------------------------------------------"

if [ "$DIFF_FROM_MASTER" -gt "0" ]; then
    echo "| Your build has failed because $BRANCH_NAME has $DIFF_FROM_MASTER more changes than your current branch |"
    echo "|                                                                                                  |"
    echo "| You need to run 'git pull origin ${BRANCH_NAME#*/}' on your branch!                                         |"
    echo "----------------------------------------------------------------------------------------------------"
    exit 1
else
    echo "| Your build is up to date with $BRANCH_NAME well done!                                                   |"
    echo "----------------------------------------------------------------------------------------------------"
    exit 0
fi
