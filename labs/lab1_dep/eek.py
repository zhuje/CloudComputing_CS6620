def main(): 
    import boto3 # allows us to access AWS programmatically 

def main():
   s3 = boto3.resource('s3')
   bucketName = 'labexample210'

   # Create the bucket 
   s3.create_bucket(Bucket=bucketName)

   # list bucket -- return meta data of buckets 
   result = s3.buckets.all()
   for bkt in result: 
     print(bkt.name)

   # Copy a File to S3 
   # S3 Buckets hold Objects
   # s3.Object(<whichBucket>, <whichFile>)
   # .put(Body=open(<whichFile>, <read?>)
   # a method called upload does something similiar 
   s3.Object(bucketName, 'hello.txt').put(Body=open('hello.txt' 'rb'))

   # change the permissions of the bucket 
   bucket = s3.Bucket(bucketName) # reference bucket iin the cloud 
   bucket.Acl().put(ALC='public-read') # this makes our public publically accessible 

if __name__ == '__main__':
   main() 

