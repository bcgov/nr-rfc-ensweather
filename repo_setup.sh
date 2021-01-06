#!/bin/zsh

conda env create --file environment.yaml
ln pre-commit.sh .git/hooks/pre-commit
ln pre-push.sh .git/hooks/pre-push
