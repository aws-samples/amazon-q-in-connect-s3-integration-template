# CHANGELOG.md

## 2024-MM-DD - ROADMAP
- Develop and Integrate Amazon Q in Connect Quick Responses Integration

## 2024-05-02 - Update QConnectIntegrationRole
- Added `kms:CreateGrant` permission to `QConnectIntegrationRole` IAM Role. 
  - This is to allow for the Integration Association of the Amazon Connect Instance with a QConnect Assistant and KnowledgeBase.
- Updated `amazon-q-in-connect-s3-integration-template.yaml` to use ${AWS::Partition} instead of 'aws' in ARN definitions.

## 2024-03-22 - Open Source Release
- Project Name: `amazon-q-in-connect-s3-integration-template`
- GitHub URL: https://github.com/aws-samples/amazon-q-in-connect-s3-integration-template 

## 2024-03-21 - Project Refinements, Documentation
- Clean up amazon-q-in-connect-s3-sync.yaml
  - Removed KMS Key Alias Resource
- Review all Documentation sections for clarity, including `README.md`
- Remove all Account Information, Author Information from Templates and code
- Remove option to deploy Contact Flow (Y/N), since it interferes with the Custom Resource deployment
  - Issue: Custom Resources cannot have Conditional Properties attached, meaning if the underlying Lambda Function is not deployed, then the Custom Resource Fails.
  - Option 1: Automatically deploy Contact Flow with Stack Deployment (Set to BasicQueue)
  - Option 2: Have customers provide a BasicQueueARN, which would remove the need for Custom Resource
  - Option 3: Keep Contact Flow deployment as a separate stack.

## 2024-03-19 - Improved Integration Handling
amazon-q-in-connect-s3-sync.yaml Updates:
- Update Main Template to specify Queue Name instead of Queue ARN
  - This will involve retrieving the specified Queue ARN for a specified QueueName using a Lambda Custom Resource (Conditional)
- Integrate and Test `0-get-queue-info` module into Main Template
  - NOTE: allow customers to select "Deploy Contact Flow" conditionally deploying helper functions and Contact Flow

amazon-q-connect-integration.py Updates
- Optimize `amazon-q-connect-integration.py` codebase
- Improve handling of CloudFormation "Delete" Events
  - On Delete, only remove Integrations where the Assistant ARN and KnowledgeBase ARN match the values from the current deployment.
  - This should eliminate the possibility of an improper removal of an integration from a separate deployment.
- Integrate `amazon-q-connect-integration-logging.py` into main `amazon-q-connect-integration.py` code.

## 2024-03-19 - Updated Q in Connect Main Template
- Main Template now successfully deploys Amazon Q in Connect, 
- Updated `amazon-q-connect-integration.py`
- Created `amazon-q-connect-integration-logging.py`
  - [x] Added logging using Python logger function to `amazon-q-connect-integration-logging.py`
  - https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html
  - Make sure to use String Formatting logger.info('Attempts: {}'.format(attempts)) 
- Created separate integration file that uses `cfnresponse` module instead of manually defined `send()` in `amazon-q-connect-integration-cfnresponse.py`
- Updated Architecture Diagram (draw.io) and exports
- Develop `0-get-queue-info` component 
  - [x] Test and Validate Deployment

## 2024-03-15 - Refactor Project Structure, Refine QiC Template
- Updated Project structure
- Added Architecture Diagram for Main Q in Connect Template
- Added Amazon QiC Contact Flow to main Template
- Updating Documentation (README.md) to reflect Amazon Q in Connect

## 2024-02-27 - Amazon Q in Connect Template
- Created amazon-connect-qic-sync-template.yml
- Removed Tagging from QIC Resources, Connect Resources

## 2023-10-04 - Wisdom S3 Sync Template Final
- Created Release Branch in Git to prepare for V1 launch.
- Updated Documentation, README.md with deployment instructions.