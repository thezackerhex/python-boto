import sys
import boto3
from botocore.exceptions import ClientError
#instance_id = sys.argv[2]
ec2 = boto3.client('ec2')
filepath = 'instance_list.txt'
with open(filepath) as fp:
  for line in fp:
    instance_id = line.rstrip('\n')
    action = sys.argv[1].upper()
    if action == 'START':
        # Do a dryrun first to verify permissions
        try:
            #ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
            ec2.start_instances(InstanceIds=[instance_id,],)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise
    
        # Dry run succeeded, run start_instances without dryrun
        #try:
        #    response = ec2.start_instances(InstanceIds=[instance_id], DryRun=True)
        #    print(response)
        #except ClientError as e:
        #    print(e)
    if action == 'STOP':
        # Do a dryrun first to verify permissions
        try:
            ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                raise
        # Dry run succeeded, call stop_instances without dryrun
        try:
            response = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
            print(response)
        except ClientError as e:
            print(e)
    else:
        print("please pass START or STOP as argument with script")
