# Name : Jenny Zhu 
# Lab : Lab2 EC2
# Description : The purpose of this lab is to create and configure an EC2 instance programmatically. 

import boto3
from botocore.exceptions import ClientError

IMAGE_ID = 'ami-033b95fb8079dc481'
INSTANCE_TYPE = 't2.nano'
KEYNAME = "zhujekeypair"
LOCAL_IP = '75.69.182.36/32'

# DeviceName is dependent on the type of AMI (Amazon Machine Image)
def getDeviceName():
    client = boto3.client('ec2')
    response = client.describe_images(ImageIds=[IMAGE_ID])
    device_name = response['Images'][0]['RootDeviceName']
    return device_name


def setSecurityGroup(vpc):
    ec2 = boto3.resource('ec2')   
    security_group = ec2.create_security_group(VpcId = vpc.id, GroupName='Lab2SG', Description='only my IP allowed to SSH at port 22, allow all  HTTP at port 80')
    security_group.authorize_ingress(FromPort = 22, ToPort = 22, CidrIp = LOCAL_IP, IpProtocol='tcp')
    security_group.authorize_ingress(FromPort = 80, ToPort = 80, CidrIp = '0.0.0.0/0', IpProtocol='tcp')
    security_group.create_tags(Tags=[{"Key": "Name", "Value": "lab2_security_group"}])
    return security_group


def main():

    print("Creating VPC ... ")

    try: 
        # create vpc 
        ec2 = boto3.resource('ec2')
        vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
        vpc.wait_until_available()
        vpc.create_tags(Tags=[{"Key": "Name", "Value": "lab2_vpc"}])

        # enable dns name hosting 
        client = boto3.client('ec2')
        client.modify_vpc_attribute( EnableDnsSupport = { 'Value': True }, VpcId = vpc.id )
        client.modify_vpc_attribute( EnableDnsHostnames = { 'Value': True }, VpcId = vpc.id )

        # attach a gateway to our vpc 
        gateway = ec2.create_internet_gateway()
        vpc.attach_internet_gateway(InternetGatewayId = gateway.id)
        gateway.create_tags(Tags=[{"Key": "Name", "Value": "lab2_gateway"}])

        # create a routetable 
        route_table = vpc.create_route_table()
        route_table.create_tags(Tags=[{"Key": "Name", "Value": "lab2_route_table"}])

        # create a public route 
        route = route_table.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId= gateway.id)

        # create subnet 
        subnet = ec2.create_subnet(CidrBlock='10.0.1.0/24', VpcId=vpc.id)
        route_table.associate_with_subnet(SubnetId=subnet.id)
        subnet.create_tags(Tags=[{"Key": "Name", "Value": "lab2_subnet"}])

    except ClientError as e: 
        print('A problem was encountered while creating the vpc')
        print(e)
        return 


    print("Creating EC2 instance ... ")

    try: 
        # create the security group  
        security_group = setSecurityGroup(vpc)
        
        # create the EC2 instance
        instance = ec2.create_instances(
                ImageId = IMAGE_ID,
                InstanceType = INSTANCE_TYPE, 
                MaxCount = 1 , 
                MinCount = 1 , 
                NetworkInterfaces = [ 
                    {
                        'SubnetId' :  subnet.id, 
                        'DeviceIndex': 0,
                        'AssociatePublicIpAddress': True, 
                        'Groups': [security_group.group_id]
                    }
                ],
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
            )
        print("EC2 instance id is : ", instance[0].id)
    except ClientError as e:
        print('A problem was encountered while creating the EC2 instance')
        print(e)
        


if __name__ == '__main__':
    main()
