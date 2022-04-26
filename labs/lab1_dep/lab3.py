
# Name : Jenny Zhu 
# Lab : Lab 1 -- S3
# Purpose : Purpose of this is lab is to programmatically upload and configure a static website on S3. 

import boto3
import requests
import zipfile
import io
import os
import json
import mimetypes


def getSiteFiles(s3, bucketName):
    bucket = s3.Bucket(bucketName)
    zip_file_url='https://github.com/AVS1508/My-Alternate-Portfolio-Website/archive/refs/heads/master.zip'
    r = requests.get(zip_file_url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall()
    for file in z.namelist():
        f = file.split('/', 1)[1]
        content_type = mimetypes.guess_type(file)[0]
        # print(f, content_type )
        if os.path.isdir(file):
            continue
        if content_type == None:
            s3.Object(bucketName, f).put(Body=open(file, 'rb'))
        else: 
            bucket.upload_file(file, f, ExtraArgs={'ACL': 'public-read', 'ContentType': content_type})


def printURL(bucketName): 
    key = "index.html"
    url =  f'https://{bucketName}.s3.amazonaws.com/{key}'
    print(url)


def main():
    # create bucket
    s3 = boto3.resource('s3')
    bucketName = 'zhujex21522'
    s3.create_bucket(Bucket = bucketName)

    # Download Static Website from Git and Upload to S3 Bucket
    getSiteFiles(s3, bucketName)

    # Configure Access Control List Policies
    bucket = s3.Bucket(bucketName)
    bucket.Acl().put(ACL = 'public-read')
    web_config = {
            'IndexDocument': {'Suffix': 'index.html'},
            }

    # Configure S3 for static website hosting
    client = boto3.client('s3')
    client.put_bucket_website(
            Bucket=bucketName,
            WebsiteConfiguration=web_config
            )
    bucket_website = s3.BucketWebsite(bucketName)


    # Configure Bucket Policy 
    bucket_policy = {
            'Version': '2012-10-17',
            'Statement': [{
                'Sid': 'AddPerm',
                'Effect': 'Allow',
                'Principal':'*',
                'Action':['s3:GetObject'],
                'Resource':f'arn:aws:s3:::{bucketName}/*'
                }]
            }
    bucket_policy = json.dumps(bucket_policy)
    client.put_bucket_policy(Bucket=bucketName, Policy=bucket_policy)

    # Print URL 
    printURL(bucketName)

if __name__ == '__main__':
    main()
    

