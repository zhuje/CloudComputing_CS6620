import boto3 
import os
from botocore.exceptions import ClientError


def create_key_pair():
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    key_pair = ec2_client.create_key_pair(KeyName="ec2-key-pair")

    private_key = key_pair["KeyMaterial"]

    # write private key to file with 400 permissions
    with os.fdopen(os.open("/tmp/aws_ec2_key.pem", os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
        handle.write(private_key)


def describe_key_pair():
    ec2 = boto3.client('ec2')
    response = ec2.describe_key_pairs()
    print(response)


def print_instance(ec2_instance):
    print(ec2_instance["Instances"][0]["InstanceId"])


def create_ec2_instance():
    RESOURCE = "ec2" 
    REGION = "us-east-1"
    LINUX_AMI = "ami-033b95fb8079dc481"
    INSTANCE_TYPE = "t2.nano"

    try: 
        create_key_pair()
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidKeyPair.Duplicate' :
            print('key already exists')
        else:
            print(e)

    print('continued to create ec2')
    ec2_client = boto3.client(RESOURCE, region_name=REGION)
    ec2_instance = ec2_client.run_instances(
            ImageId = LINUX_AMI, 
            MinCount = 1, 
            MaxCount = 1, 
            InstanceType = INSTANCE_TYPE,
            KeyName = "ec2-key-pair"
            )
    print_instance(ec2_instance)

def main():
    create_ec2_instance() 

main()
