import boto3
import requests 
import zipfile 
import io
import os 

def getSiteFiles():
    zip_file_url='https://github.com/AVS1508/My-Alternate-Portfolio-Website/archive/refs/heads/master.zip'
    r = requests.get(zip_file_url, stream=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall()

def main(): 
    s3 = boto3.resource('s3')
    bucketName = 'zhujex21522'

    s3.create_bucket(Bucket = bucketName)

    s3.Object(bucketName, 'hello.txt').put(Body=open('hello.txt', 'rb'))
    
    getSiteFiles()

if __name__ == '__main__':
    main()
