import logging
import os
import boto3
import requests
import zipfile
import io

from biotocore.exceptions import ClientError

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def main():
    s3 = boto3.resources("s3")
    bucket_name = "zhuje021522"
    s3.create_bucket(Bucket = bucket_name)


    list = s3.buckets.all()
    for bucket in list:
        print(bucket_name)

    # Upload Files
    filename = 'someFile'
    upload_file(filename, bucket_name)


    # Configure Access List
    bucket = s3.Bucket(bucket_name)
    bucket.Acl().put(ACL = "public-read")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

