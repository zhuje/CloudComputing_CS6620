
import boto3 
import Object 

def main():
     bucketName = 'zhujex0216220'
     session = boto3.session.Session()
     s3_client = session.client('s3')
     result = s3_client.get_bucket_location(Bucket=bucketName, )['LocationConstraint']
     print(result)
     region = result[Object.keys(result)][0].toString()
     print("region ", region)

if __name__ == '__main__':
    main()

