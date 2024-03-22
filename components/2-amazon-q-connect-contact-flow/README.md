# Amazon Q in Connect Contact Flow Export Steps (README.md)

Describe Contact Flow 
### Description:
1. Export Contact Flow from Connect UI, 
2. Describe (from Connect API 'describe-contact-flow')
3. Copy Exported Flow into CloudFormation Template to deploy the Contact Flows

### Reference:
- CloudFormation - AWS::Connect::ContactFlow: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-connect-contactflow.html
- Describe Contact Flow (AWS CLI): https://awscli.amazonaws.com/v2/documentation/api/latest/reference/connect/describe-contact-flow.html

Regex Match for ARN is:
`arn:aws:wisdom:[a-z-\d]+:[\d]+:[a-z\d]+\/[a-z-\d]+`

**Contact Flow Operations:**
Step 1: Export the Template Contact Flow, store it in this folder.
Step 2: Run 'describe-contact-flow' operation using the AWS CLI

**TEMPLATE**
aws connect describe-contact-flow --instance-id INSTANCE_ID --contact-flow-id CONTACT_FLOW_ID > OUTPUT_FILE_NAME.json

****
* Describe Contact Flow Steps (Modify Template Flow)
1. Run `aws connect describe-contact-flow --instance-id INSTANCE_ID --contact-flow-id CONTACT_FLOW_ID --query ContactFlow.Content > OUTPUT_FLOW.json`
2. Open the JSON file 'OUTPUT_FLOW.json'
3. Perform a RegEx search to FIND `arn:aws:wisdom:[a-z-\d]+:[\d]+:[a-z\d]+\/[a-z-\d]+`, REPLACE with `${QConnectAssistantARN}`
4. Copy the modified JSON string into the "Content" section of the Contact Flow Definition below.
****