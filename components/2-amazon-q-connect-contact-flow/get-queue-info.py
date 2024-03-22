# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
# Description: (v2024.03.21) This AWS Lambda Custom Resource function will return attributes of a specified Amazon Connect Queue.
import cfnresponse
import json
import logging
import boto3

# Initialize global variables
logger = logging.getLogger()
logger.setLevel("INFO")
connect_client = boto3.client('connect')

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    request_type = event.get('RequestType')

    if request_type in ('Create', 'Update'):
        instance_arn = event['ResourceProperties']['AmazonConnectInstanceARN']
        instance_id = instance_arn.split('/')[-1]
        queue_name = event['ResourceProperties']['QueueName']

        # Search Amazon Connect Queues with exact match for name field. (https://docs.aws.amazon.com/connect/latest/APIReference/API_SearchQueues.html)
        response = connect_client.search_queues(
            InstanceId=instance_id,
            SearchCriteria={
                'StringCondition': {
                    'FieldName': 'name',
                    'Value': queue_name,
                    'ComparisonType': 'EXACT'
                },
            }
        )

        queues = response.get("Queues", [])
        if not queues:
            logger.info(f"Queue with name {queue_name} was not found.")
            return None

        # Return the first queue in the list of Queues returned by the SearchQueues API.
        queue_info = queues[0]
        logger.info("Queue Found: %s", queue_info)
        response_data = {
            "QueueName": queue_info.get("Name") or "None",
            "QueueArn": queue_info.get("QueueArn"),
            "QueueId": queue_info.get("QueueId"),
        }
    elif request_type == 'Delete':
        response_data = {}
    else:
        raise ValueError(f'Unsupported RequestType: {request_type}')

    # Send CFN Response and return ResponseData
    cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
    return response_data