#!/usr/bin/env python3


from __future__ import absolute_import
from __future__ import print_function
import re
from datetime import datetime
import csv
import argparse
import time
import os
from pprint import pprint

today = datetime.now()

try:
    import boto3
    # import botocore
except ImportError as e:
    print('This script require Boto3 to be installed and configured.')
    exit()
from botocore.exceptions import ClientError

def get_account_list():
    # generate a list of AWS accounts based on the credentials file
    local_account_list = []
    try:
        credentials = open(os.path.expanduser('~/.aws/credentials'), 'r')
        for line in credentials:
            account = re.search('\[([\w\d\-\_]*)\]', line)
            if account is not None:
                local_account_list.insert(0, account.group(1))
    except:
        print("Script expects ~/.aws/credentials. Make sure this file exists")
        exit()
    print (local_account_list)
    return local_account_list

def get_aws_accounts_in_scope():
    # read the csv file of AWS accounts into dictionary
    accounts_local = {}
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    print(__location__)
    f = (os.path.join(__location__, 'AWS-account-list.csv'))
    with open(f, 'r') as file:
        for line in file:
            data = line.split(",")
            key = data[0]
            val = data[1]
            flag = data[2]
            if flag.upper()=="Y":
                accounts_local[key] = val
    print (accounts_local)
    return accounts_local

def validate_credentials(accounts_dictionary, accounts_credentials, *profile):
    # validate that the local credentials file has an entry for each account in scope and use only
    # the credentials for the accounts in scope.
    in_scope_acct_alias_list = []
    for acct in accounts_credentials:
        if (acct in accounts_dictionary.values()):
            in_scope_acct_alias_list.append(acct)
        else:
            print("****INFORMATION: %s was not found in list of accounts in scope." % acct)
    for key, value in accounts_dictionary.items():
        if value not in in_scope_acct_alias_list:
            print("****WARNING: %s does not have a corresponding entry in the local credentials file." % value)
            print("****WARNING: The %s account will not be audited" % value)
    return in_scope_acct_alias_list

def get_client(account, local_region):
    # Sets up a boto3 session
    local_profile = account
    try:
        current_session = boto3.Session(profile_name = local_profile, region_name=local_region)
        local_client = current_session.client("rds")
        return local_client
    except:
        print(local_region)
        print('\'{}\' is not a configured account.'.format(account))
        exit()

def date_on_filename(filename, file_extension):
    from datetime import datetime
    date = str(datetime.now().date())
    return filename + "-" + date + "." + file_extension

def get_regions(lcl_account):
    #get the current list of regions to iterate through
    lcl_region = "us-east-1"
    client = get_client(lcl_account, lcl_region)
    aws_region_data = client.describe_regions()
    aws_regions = aws_region_data['Regions']
    lcl_regions = [region['RegionName'] for region in aws_regions]
    return lcl_regions


def main():
    report_filename = date_on_filename("ec2_inventory", "csv")
    # Get the List of AWS Accounts in Scope
    accounts = get_aws_accounts_in_scope()
    # Get the List of Accounts in the user's local credential file
    account_list = get_account_list()
    # Ensure the user's local credential is complete, remove out of scope accounts
    validated_accounts = validate_credentials(accounts, account_list)
    file = open(report_filename, 'w+')
    print_string_hdr = "account,Database,DbVersion,InstanceType,Retention_Period\n"
    file.write(print_string_hdr)
    #regions = get_regions(validated_accounts[0])
    regions = ['us-east-1','us-west-2']
    for account in validated_accounts:
        print("*********************************************************")
        count_total = count_old = oldest = 0
        for region in regions:
            client = get_client(account, region)
            #aws_regions = client.describe_regions()
            #print('Regions:', aws_regions['Regions'])
            #response = client.describe_instances()
            response = client.describe_db_instances()
            #print(account, " -- ", region)
            Engine = EngineVersion = status = Instance_type = Arn = Retention_Period = ""
            for key1, value1 in response.items():
                if key1 == "DBInstances":
                    for object_a in value1:
                        for key2, value2 in object_a.items():
                            if key2 == "BackupRetentionPeriod":
                                Retention_Period = str(value2)
                            if key2 == "DBInstanceArn":
                                Arn = value2
                            if key2 == "DBInstanceClass":
                                instance_type = value2
				Instance_type = str(instance_type)
                            if key2 == "DBInstanceStatus":
                                status = value2
                            if key2 == "Engine":
                                Engine = value2
                            if key2 == "EngineVersion":
                                EngineVersion = value2
                        print_string = account + "," + Engine + "," + EngineVersion + "," + Instance_type + "," + Retention_Period 
                        file.write(print_string + "\n")
                        
                        
    file.close()
    return
main()
