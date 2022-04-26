import boto3
from botocore.exceptions import ClientError

REGION_NAME = 'us-east-1'
RESOURCE = 'ec2'
IMAGE_ID = 'ami-033b95fb8079dc481'
INSTANCE_TYPE = 't2.nano'
KEYNAME = "zhujekeypair"


def getDeviceName():
    client = boto3.client('ec2')
    response = client.describe_images(ImageIds=[IMAGE_ID])
    device_name = response['Images'][0]['RootDeviceName']
    return device_name


def setSecurityGroup():
    ec2 = boto3.client('ec2')
    response = ec2.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

    try: 
        response = ec2.create_security_group(GroupName = 'jz-security-group', Description = 'jz security group', VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

        data = ec2.authorize_security_group_ingress(
                GroupId=security_group_id, 
                IpPermission=[
                    {'IpProtocol' : 'tcp', 
                     'FromPort': 80, 
                     'ToPort': 80, 
                     'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                     },
                ])
        print('Ingress Successfully Set %s' % data)


    except ClientError as e: 
        print(e)


def getGroupID():
    ec2 = boto3.client('ec2')
    group_name = 'jz-security-group'
    response = ec2.describe_security_groups(
                Filters=[
                            dict(Name='group-name', Values=[group_name])
                                ]
                )
    group_id = response['SecurityGroups'][0]['GroupId']
    print(group_id)

def AH():
    ec2 = boto3.resource('ec2')
    security_group = ec2.SecurityGroup('id')
    print(security_group)


def main():

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
                    'DeviceName': getDeviceName(), # how to dynamically generate this? can you hard code?
                    'Ebs': {
                        'VolumeSize' : 10,
                    },
                },
            ],
            SecurityGroupIds=['sg-0591f04eec0203f02'],
        ) 
    print(instance[0].id)



if __name__ == '__main__':
    main()
