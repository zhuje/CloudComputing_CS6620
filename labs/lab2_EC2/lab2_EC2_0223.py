import boto3
from botocore.exceptions import ClientError

REGION_NAME = 'us-east-1'
RESOURCE = 'ec2'
IMAGE_ID = 'ami-033b95fb8079dc481'
INSTANCE_TYPE = 't2.nano'
KEYNAME = "zhujekeypair"
LOCAL_IP = '75.69.182.36/32'
SECURITY_GROUP_NAME = 'jz-security-group'


# DeviceName is dependent on the type of AMI (Amazon Machine Image)
def getDeviceName():
    client = boto3.client('ec2')
    response = client.describe_images(ImageIds=[IMAGE_ID])
    device_name = response['Images'][0]['RootDeviceName']
    return device_name


def securityGroupNameAlreadyExists():
    ec2 = boto3.client('ec2')
    group_name = SECURITY_GROUP_NAME
    response = ec2.describe_security_groups()
    for i in response['SecurityGroups']:
        if i['GroupName'] == SECURITY_GROUP_NAME:
            return True 
    return False 


def setSecurityGroup():
    ec2 = boto3.client('ec2')
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

    try: 
        response = ec2.create_security_group(GroupName = 'jz-security-group', Description = 'jz security group', VpcId=vpc_id)
        security_group_id = response['GroupId']

        ec2.authorize_security_group_ingress(
                GroupId=security_group_id, 
                IpPermissions = [
                    {
                        'FromPort': 80, 
                        'IpProtocol': 'tcp', 
                        'IpRanges': [
                            {
                                'CidrIp': '0.0.0.0/0',
                                'Description': 'HTTPForAll'
                            }, 
                        ],
                        'ToPort':80, 
                    },
					{
						'FromPort': 22, 
						'IpProtocol': 'tcp', 
						'IpRanges': [
							{
								'CidrIp': LOCAL_IP,
								'Description': 'sshFromMyIP'
							},
						],
						'ToPort': 22,
					},
                    
                ],
            )
    except ClientError as e: 
        if e.response['Error']['Code'] == "InvalidGroup.Duplicate":
            print('This Security Group Name  Already exists')
        print(e)

    return security_group_id


def getSecurityGroupID():
    ec2 = boto3.client('ec2')
    group_name = SECURITY_GROUP_NAME
    response = ec2.describe_security_groups(
                Filters=[
                            dict(Name='group-name', Values=[group_name])
                                ]
                )
    group_id = response['SecurityGroups'][0]['GroupId']
    return group_id


def main():

    if securityGroupNameAlreadyExists() :
        sg_id = getSecurityGroupID()
    else : 
        sg_id = setSecurityGroup()

    ec2 = boto3.resource(RESOURCE)
    instance = ec2.create_instances(
            ImageId = IMAGE_ID,
            MinCount = 1, 
            MaxCount = 1,
            InstanceType = INSTANCE_TYPE,
            KeyName = KEYNAME, 
            TagSpecifications = [ 
                {
                    'ResourceType': 'instance',
                    'Tags' : [
                        {
                            'Key' : 'Name', 
                            'Value': 'cs6620-ec2-lab2'
                        },
                    ]
                },
            ],
            BlockDeviceMappings=[
                {
                    'DeviceName': getDeviceName(), 
                    'Ebs': {
                        'VolumeSize' : 10,
                    },
                },
            ],
            SecurityGroupIds=[sg_id]
        ) 
    print("Success. Instance id is : ", instance[0].id)


if __name__ == '__main__':
     main()

