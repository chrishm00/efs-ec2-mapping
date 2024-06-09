## In Memory

This project is dedicated to the memory of an amazing dad that always inspired me to continue working and never give up…

# EFS-EC2 Mapping

Automated solution for mapping EC2 instances to EFS (Elastic File System) file systems within an AWS environment.

## Overview

This project simplifies and automates the process of generating a report that shows which EC2 instances have mounted which EFS file systems. It leverages AWS CloudFormation, AWS Lambda, VPC Flow Logs, and EventBridge to provide a streamlined and efficient approach to managing your AWS infrastructure.


## Deployment

Kindly follow the [Medium Article- Automated EFS-EC2 Inventory Report](https://medium.com/@christopherhm0028/automated-efs-ec2-inventory-report-4bfa99f2a7f3)

### Prerequisites

1. **AWS Account**: An active AWS account.
2. **Basic AWS Knowledge**: Familiarity with EC2, S3, Lambda, AWS CloudFormation, and CloudWatch.
3. **EC2 Instances**: Ensure the EC2 instances have the appropriate IAM policies attached.
4. **S3 Bucket**: A bucket to store the Lambda function code and the generated reports.

### Steps

1. **Prepare the Lambda Function Code**:
   - Zip the `lambda_function.py` script.
   - Upload the zipped file to your S3 bucket.

2. **Deploy the CloudFormation Stack**:
   - Navigate to the AWS CloudFormation console.
   - Create a new stack using the provided CloudFormation template (`EFS CloudFormation.yaml`).
   - Provide the following parameters:
     - `LambdaCodeS3Bucket`: The name of the S3 bucket where the Lambda function code is stored.
     - `LambdaCodeS3Key`: The path to the zipped Lambda function code within the S3 bucket.
     - `ResultsS3Bucket`: The name of the S3 bucket where you want the results to be saved.
     - `VPCID`: The ID of the VPC where the EFS and EC2 instances are located.
     - `EFSDiscoveryOption`: Choose between `All`, `Specific`, or `FromS3` to determine how EFS file systems are discovered.
     - `SpecificEFSIds`: Comma-separated list of specific EFS IDs (only required if `EFSDiscoveryOption` is `Specific`).
     - `EFSIdsS3Path`: S3 path to a file containing EFS IDs (only required if `EFSDiscoveryOption` is `FromS3`).

### Validation and Testing

1. **Check CloudFormation Stack Status**:
   - Ensure the stack status is `CREATE_COMPLETE`.

2. **Check Lambda Function CloudWatch Logs**:
   - Verify that the Lambda function was triggered and executed correctly.

3. **Verify the Report in S3 Bucket**:
   - Check the specified S3 bucket for the generated report.
   - The report should map EFS file systems to EC2 instances.

### Security Considerations

This project adheres to the principle of least privilege by granting only the necessary permissions required for the solution to function correctly. Below are some key permissions and their purposes:

**Lambda Execution Role**:
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`: Allows the Lambda function to log its output to CloudWatch Logs.
- `logs:StartQuery`, `logs:GetQueryResults`, `logs:StopQuery`: Allows the Lambda function to query VPC Flow Logs from CloudWatch Logs.
- `ec2:DescribeInstances`, `ec2:DescribeVpcs`, `ec2:DescribeSubnets`, `ec2:DescribeNetworkInterfaces`: Allows the Lambda function to retrieve information about EC2 instances and their network interfaces.
- `ec2:CreateFlowLogs`, `ec2:DeleteFlowLogs`, `ec2:DescribeFlowLogs`, `ec2:DescribeTags`: Allows the Lambda function to manage and describe VPC Flow Logs.
- `elasticfilesystem:DescribeFileSystems`, `elasticfilesystem:DescribeMountTargets`: Allows the Lambda function to retrieve information about EFS file systems and their mount targets.
- `s3:PutObject`, `s3:GetObject`, `s3:ListBucket`: Allows the Lambda function to store and retrieve results in the specified S3 bucket.
- `events:DisableRule`: Allows the Lambda function to disable the EventBridge rule after execution.
- `iam:PassRole`: Allows the Lambda function to assume the necessary IAM roles for execution.

### Pricing and Cost Estimation

The total cost for this project depends on several AWS services: AWS Lambda, S3, EC2 instances, VPC Flow Logs, CloudWatch Logs, and EventBridge. Here's a detailed breakdown:

1. **AWS Lambda**: Costs for the number of requests and compute time.
   - **Requests**: $0.20 per 1 million requests.
   - **Compute Time**: $0.00001667 per GB-second.

2. **Amazon S3**: Costs for data storage and requests.
   - **Storage**: $0.023 per GB per month.
   - **Requests**: $0.005 per 1,000 PUT requests, $0.0004 per 1,000 GET requests.

3. **EC2 Instances**: Costs depend on the instance types and usage.

4. **VPC Flow Logs**: Costs for capturing and storing IP traffic flow information.
   - **Publishing**: $0.50 per GB.

5. **CloudWatch Logs**: Costs for storing and querying logs.
   - **Storage**: $0.03 per GB for the first 50 TB per month.
   - **Data Ingestion**: $0.50 per GB.
   - **Insights Queries**: $0.005 per GB of data scanned.

6. **EventBridge**: Costs for rule invocation.
   - **Rules**: $1.00 per 1 million events (First 1 million events per month are free).

**Total Monthly Cost**: Approximately $1.069 USD (example scenario).

### Conclusion

This automated solution simplifies the process of mapping EC2 instances to EFS file systems, providing accurate and up-to-date information efficiently. Follow the detailed steps in the accompanying Medium article to configure and deploy this solution in your AWS environment.

For more detailed instructions, refer to the accompanying Medium article [here](https://medium.com/@christopherhm0028/automated-efs-ec2-inventory-report-4bfa99f2a7f3).

## License

Apache-2.0 license
