#!/bin/bash

# Create the policy
aws iam create-policy \
  --policy-name GitHubActionsDeployPolicy \
  --policy-document file://github_actions_deploy_iam_policy.json

# Create the user
aws iam create-user --user-name github-actions-deploy

# Attach the policy to the user
aws iam attach-user-policy \
  --user-name github-actions-deploy \
  --policy-arn arn:aws:iam::YOUR-ACCOUNT-ID:policy/GitHubActionsDeployPolicy

# Create access keys
aws iam create-access-key --user-name github-actions-deploy
