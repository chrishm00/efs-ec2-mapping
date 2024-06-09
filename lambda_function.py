import boto3
import os
import json
from datetime import datetime, timedelta
import time

# Initialize AWS clients
efs_client = boto3.client('efs')
logs_client = boto3.client('logs')
ec2_client = boto3.client('ec2')
s3_client = boto3.client('s3')
events_client = boto3.client('events')

# Environment variables
RESULTS_S3_BUCKET = os.environ['RESULTS_S3_BUCKET']
CLOUDWATCH_LOG_GROUP = os.environ['CLOUDWATCH_LOG_GROUP']
EFS_DISCOVERY_OPTION = os.environ['EFS_DISCOVERY_OPTION']
SPECIFIC_EFS_IDS = os.environ['SPECIFIC_EFS_IDS']
EFS_IDS_S3_PATH = os.environ['EFS_IDS_S3_PATH']
EVENTBRIDGE_RULE_NAME = os.environ['EVENTBRIDGE_RULE_NAME']

def list_all_efs_file_systems():
    response = efs_client.describe_file_systems()
    return [fs['FileSystemId'] for fs in response['FileSystems']]

def list_specific_efs_file_systems():
    return SPECIFIC_EFS_IDS.split(',')

def list_efs_file_systems_from_s3():
    content_object = s3_client.get_object(Bucket=RESULTS_S3_BUCKET, Key=EFS_IDS_S3_PATH)
    file_content = content_object['Body'].read().decode('utf-8')
    return file_content.splitlines()

def get_efs_file_systems():
    if EFS_DISCOVERY_OPTION == 'All':
        return list_all_efs_file_systems()
    elif EFS_DISCOVERY_OPTION == 'Specific':
        return list_specific_efs_file_systems()
    elif EFS_DISCOVERY_OPTION == 'S3':
        return list_efs_file_systems_from_s3()
    else:
        raise ValueError("Invalid EFS discovery option")

def list_mount_targets(efs_id):
    response = efs_client.describe_mount_targets(FileSystemId=efs_id)
    return [mt['IpAddress'] for mt in response['MountTargets']]

def analyze_vpc_flow_logs(mount_targets, retries=3, wait_time=20):
    query = """
    fields @timestamp, srcAddr, dstAddr
    | filter dstPort == 2049 and dstAddr in {}
    """.format(json.dumps(mount_targets))
    
    start_query_response = logs_client.start_query(
        logGroupName=CLOUDWATCH_LOG_GROUP,
        startTime=int((datetime.now() - timedelta(minutes=10)).timestamp()),
        endTime=int(datetime.now().timestamp()),
        queryString=query,
        limit=1000
    )
    query_id = start_query_response['queryId']
    
    attempts = 0
    response = None
    while attempts < retries:
        attempts += 1
        response = logs_client.get_query_results(queryId=query_id)
        if response['status'] == 'Complete':
            return response['results']
        print(f"Retrying... {attempts}/{retries}")
        time.sleep(wait_time)
    return []

def get_ec2_instance(ip):
    response = ec2_client.describe_instances(
        Filters=[{'Name': 'private-ip-address', 'Values': [ip]}]
    )
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if instance['PrivateIpAddress'] == ip:
                return instance['InstanceId']
    return None

def generate_report(efs_to_instances):
    report = []
    for efs, instances in efs_to_instances.items():
        efs_entry = {"EFS": efs, "EC2Instances": list(instances)}
        report.append(efs_entry)
    return json.dumps(report, indent=2)

def lambda_handler(event, context):
    try:
        # Disable the EventBridge rule at the beginning
        disable_eventbridge_rule(EVENTBRIDGE_RULE_NAME)
        
        efs_file_systems = get_efs_file_systems()
        print("EFS file systems:", efs_file_systems)
        efs_to_instances = {}
        for efs_id in efs_file_systems:
            mount_targets = list_mount_targets(efs_id)
            print(f"Mount targets for EFS {efs_id}:", mount_targets)
            flow_logs = analyze_vpc_flow_logs(mount_targets)
            print("Flow logs:", flow_logs)
            instances = set()
            for log in flow_logs:
                src_addr = None
                for field in log:
                    if field['field'] == 'srcAddr':
                        src_addr = field['value']
                if src_addr:
                    instance_id = get_ec2_instance(src_addr)
                    if instance_id:
                        instances.add(instance_id)
                    elif src_addr == '127.0.0.1':  # Handle localhost IP address
                        instance_id = get_ec2_instance(log[1]['value']['dstaddr'])
                        if instance_id:
                            instances.add(instance_id)
            efs_to_instances[efs_id] = instances
            print(f"Instances for EFS {efs_id}:", instances)
        
        report = generate_report(efs_to_instances)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        report_key = f'efs_to_ec2_report_{timestamp}.json'
        print("Generated report:", report)
        s3_client.put_object(
            Bucket=RESULTS_S3_BUCKET,
            Key=report_key,
            Body=report
        )
    except Exception as e:
        print("Error:", str(e))
        raise e

def disable_eventbridge_rule(rule_name):
    events_client.disable_rule(Name=rule_name)
