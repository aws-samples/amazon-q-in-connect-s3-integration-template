# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
# Description: (v2024-03-21) Amazon Connect Integration with Amazon Q in Connect (Assistant and KnowledgeBase)

# Core Python Imports (Logging, HTTP). License: https://docs.python.org/3/license.html
import json
import logging
import urllib3

# AWS SDK (boto3) Imports. License: https://github.com/boto/boto3/blob/develop/LICENSE
import boto3
import botocore

# Initialize global variables
logger = logging.getLogger()
logger.setLevel("INFO")
http = urllib3.PoolManager()
CONNECT_CLIENT = boto3.client('connect')

def lambda_handler(event, context):
    logger.info("Event Received: %s", json.dumps(event))
    logger.info("Request Type: %s", event.get('RequestType'))
    logger.info("Resource Properties: %s", json.dumps(event.get("ResourceProperties")))

    # Handle Input Data from CloudFormation Resource Properties
    physical_resource_id = event.get('ResourceProperties').get('ServiceToken')
    instance_arn = event.get('ResourceProperties').get('INSTANCE_ARN')
    qconnect_assistant_arn = event.get('ResourceProperties').get('QCONNECT_ASSISTANT_ARN')
    qconnect_knowledge_base_arn = event.get('ResourceProperties').get('QCONNECT_KNOWLEDGE_BASE_ARN')

    # Check for existing Integrations: List Integration Association - QConnect Assistant / Knowledge Base
    connect_assistant_integration = list_integration_associations(instance_arn, "WISDOM_ASSISTANT")
    connect_knowledge_base_integration = list_integration_associations(instance_arn, "WISDOM_KNOWLEDGE_BASE")
    logger.info("Connect Integration - QConnect Assistant: %s", json.dumps(connect_assistant_integration))
    logger.info("Connect Integration - QConnect Knowledgebase: %s", json.dumps(connect_knowledge_base_integration))

    # Define ResponseData Expected by CloudFormation Response:
    response_data = {
        "QConnect_Assistant_ARN": "",
        "QConnect_Assistant_IntegrationAssociationARN": "",
        "QConnect_KnowledgeBase_ARN": "",
        "QConnect_KnowledgeBase_IntegrationAssociationARN": "",
    }

    # Case 1: CloudFormation Stack sends Create or Update Event.
    if event["RequestType"] in ["Create", "Update"]:
        # Step 1: Remove any existing QConnect Assistant/KnowledgeBase Integrations
        if connect_assistant_integration:
            logger.info("Connect Instance: %s has an existing Amazon Q in Connect - Assistant Integration", instance_arn)
            logger.info("Delete QConnect Assistant Integration: %s", connect_assistant_integration[0]["IntegrationAssociationId"])
            delete_integration_association(instance_arn, connect_assistant_integration[0]["IntegrationAssociationId"])

        if connect_knowledge_base_integration:
            logger.info("Connect Instance: %s has an existing Amazon Q in Connect - KnowledgeBase Integration", instance_arn)
            logger.info("Delete QConnect KnowledgeBase Integration: %s", connect_knowledge_base_integration[0]["IntegrationAssociationId"])
            delete_integration_association(instance_arn, connect_knowledge_base_integration[0]["IntegrationAssociationId"])

        # Step 2: Create new Integration Associations with provided QConnect Assistant and Knowledge Base
        if qconnect_assistant_arn:
            response = create_integration_association(instance_arn, qconnect_assistant_arn, 'WISDOM_ASSISTANT')
            logger.info("Connect Integration - QConnect Assistant. Create Integration Association Response: %s", response)
            if response['status'] == "SUCCESS":
                response_data["QConnect_Assistant_IntegrationAssociationARN"] = response['IntegrationAssociationArn']
                response_data["QConnect_Assistant_ARN"] = qconnect_assistant_arn
        else:
            logger.info("QConnect Assistant ARN not provided. Skipping Create Integration Association.")

        if qconnect_knowledge_base_arn:
            response = create_integration_association(instance_arn, qconnect_knowledge_base_arn, 'WISDOM_KNOWLEDGE_BASE')
            logger.info("Connect Integration - QConnect KnowledgeBase. Create Integration Association Response: %s", response)
            if response['status'] == "SUCCESS":
                response_data["QConnect_KnowledgeBase_IntegrationAssociationARN"] = response['IntegrationAssociationArn']
                response_data["QConnect_KnowledgeBase_ARN"] = qconnect_knowledge_base_arn
        else:
            logger.info("QConnect KnowledgeBase ARN not provided. Skipping Create Integration Association.")

        # Send CFN Response
        logger.info("Create/Update - QConnect Integration Handler Response: %s", json.dumps(response_data))
        send(event, context, "SUCCESS", response_data, physical_resource_id)
        return response_data

    # Case 2: CloudFormation Stack sends DELETE signal - Delete Connect Integration Associations.
    if event["RequestType"] == "Delete":
        # Delete only the Integration Association where the qconnect_assistant_arn is defined as the "IntegrationArn"
        if qconnect_assistant_arn and connect_assistant_integration:
            for integration in connect_assistant_integration:
                if integration["IntegrationArn"] == qconnect_assistant_arn:
                    logger.info("Delete QConnect Assistant Integration: %s", integration["IntegrationAssociationId"])
                    delete_integration_association(instance_arn, integration["IntegrationAssociationId"])

        # Delete only the Integration Association where the qconnect_knowledge_base_arn is defined as the "IntegrationArn"
        if qconnect_knowledge_base_arn and connect_knowledge_base_integration:
            for integration in connect_knowledge_base_integration:
                if integration["IntegrationArn"] == qconnect_knowledge_base_arn:
                    logger.info("Delete QConnect KnowledgeBase Integration: %s", integration["IntegrationAssociationId"])
                    delete_integration_association(instance_arn, integration["IntegrationAssociationId"])

        # Send CFN Response
        logger.info("Delete - QConnect Integration Response: %s", json.dumps(response_data))
        send(event, context, "SUCCESS", response_data, physical_resource_id)
        return response_data

# List Amazon Connect Instance Integration Associations (Accepts either Instance ID or ARN)
# https://docs.aws.amazon.com/connect/latest/APIReference/API_ListIntegrationAssociations.html
def list_integration_associations(instance_id, integration_type):
    try:
        response = CONNECT_CLIENT.list_integration_associations(InstanceId=instance_id, IntegrationType=integration_type)
        return response["IntegrationAssociationSummaryList"]
    except botocore.exceptions.ClientError as e:
        logger.error("Client Error: %s", e)
        return []
    except Exception as e:
        logger.error("Exception: %s", e)
        return []

# Integrates a WISDOM_KNOWLEDGE_BASE or WISDOM_ASSISTANT with an Amazon Connect Instance
# https://docs.aws.amazon.com/connect/latest/APIReference/API_CreateIntegrationAssociation.html
def create_integration_association(instance_id, integration_arn, integration_type):
    logger.info("Creating Integration Association between Connect Instance: %s and the QConnect Resource: %s with Integration Type: %s", instance_id, integration_arn, integration_type)
    try:
        response = CONNECT_CLIENT.create_integration_association(InstanceId=instance_id, IntegrationArn=integration_arn, IntegrationType=integration_type)
        response["status"] = "SUCCESS"
        return response
    except botocore.exceptions.ClientError as e:
        logger.error("Client Error: %s", e)
        return {'status': "CLIENT_ERROR", 'Message': str(e)}
    except Exception as e:
        logger.error("Exception: %s", e)
        return {'status': "EXCEPTION", 'Message': str(e)}

# Delete a Connect - Wisdom Integration Association (Assistant or KnowledgeBase)
# https://docs.aws.amazon.com/connect/latest/APIReference/API_DeleteIntegrationAssociation.html
def delete_integration_association(instance_id, integration_association_id):
    logger.info("Deleting Integration Association between Connect Instance: %s and the QConnect Integration: %s", instance_id, integration_association_id)
    try:
        CONNECT_CLIENT.delete_integration_association(InstanceId=instance_id, IntegrationAssociationId=integration_association_id)
        return {'status': "SUCCESS", 'Message': f"Integration Association {integration_association_id} deleted successfully"}
    except botocore.exceptions.ClientError as e:
        logger.error("Client Error: %s", e)
        return {'status': "CLIENT_ERROR", 'Message': str(e)}
    except Exception as e:
        logger.error("Exception: %s", e)
        return {'status': "EXCEPTION", 'Message': str(e)}

# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
# CloudFormation Response Helper Function: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cfn-lambda-function-code-cfnresponsemodule.html
def send(event, context, response_status, response_data, physical_resource_id=None, no_echo=False, reason=None):
    response_url = event['ResponseURL']
    logger.info("Response URL: %s", response_url)

    response_body = {
        'Status': response_status,
        'Reason': reason or f"See the details in CloudWatch Log Stream: {context.log_stream_name}",
        'PhysicalResourceId': physical_resource_id or context.log_stream_name,
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'NoEcho': no_echo,
        'Data': response_data
    }
    json_response_body = json.dumps(response_body)
    logger.info("Response body: %s", json_response_body)

    headers = {
        'content-type': '',
        'content-length': str(len(json_response_body))
    }

    try:
        response = http.request('PUT', response_url, headers=headers, body=json_response_body)
        logger.info("Status code: %s", response.status)
    except Exception as e:
        logger.error("send(..) failed executing http.request(..):%s", e)
