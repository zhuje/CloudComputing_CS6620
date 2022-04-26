import boto3 
import gzip
import requests
import shutil
import json 
import codecs
import csv
import uuid
import pandas as pd # NOTE : Use the CLI command 'pip3 install pandas' to install pandas 

BOSTON_URL = "http://data.insideairbnb.com/united-states/ma/boston/2021-12-17/data/reviews.csv.gz"
BRISTOL_UK_URL = "http://data.insideairbnb.com/united-kingdom/england/bristol/2021-12-23/data/reviews.csv.gz"
CHICAGO_USA_URL = "http://data.insideairbnb.com/united-states/il/chicago/2021-12-15/data/reviews.csv.gz"
ASHEVILLE_USA_URL = "http://data.insideairbnb.com/united-states/nc/asheville/2021-12-15/data/reviews.csv.gz"
WASHINGTONDC_USA_URL = "http://data.insideairbnb.com/united-states/dc/washington-dc/2021-12-15/data/reviews.csv.gz"

def read_csv_from_s3(bucketName, key, column): 
    # Testing use only 
    count = 0 

    client = boto3.client("s3")
    dynamoDB = boto3.client('dynamodb', region_name='us-east-1')

    data = client.get_object(Bucket=bucketName, Key=key)
    for row in csv.DictReader(codecs.getreader("utf-8")(data["Body"])):
        if count > 5 : 
            return 
        else: 
            count += 1 
            print("COUNT :" , count)
            print(row[column])
            comprehend = boto3.client('comprehend', region_name='us-east-1') 
            sentiment_output = comprehend.detect_sentiment(Text=row[column], LanguageCode='en')
            print(sentiment_output)
            print(sentiment_output['Sentiment'])
            print("SentimentScore_Positive", sentiment_output['SentimentScore']['Positive'])
            print("___________________________")

            response = dynamoDB.put_item(
                    TableName='boston',
                    Item={
                        'id': {'S': str(uuid.uuid1())},
                        'listing_id': {'S': row['listing_id']},
                        'date': {'S': row['date']},
                        'reviewer_id': {'S' : row['reviewer_id']},
                        'reviewr_name': {'S' : row['reviewer_name']},
                        'comments': {'S' : row['comments']},
                        'sentiment': {'S' : sentiment_output['Sentiment']},
                        'sentiment_score_positive': { 'N' : str(sentiment_output['SentimentScore']['Positive']) },
                        'sentiment_score_negative': { 'N' : str(sentiment_output['SentimentScore']['Negative']) },
                        'sentiment_score_neutral': { 'N' : str(sentiment_output['SentimentScore']['Neutral']) },
                        'sentiment_score_mixed': { 'N' : str(sentiment_output['SentimentScore']['Mixed']) },
                        }
                    )

def extractAndUpload(URL, filename, bucket):
    gz_filename = filename + '.csv.gz'
    csv_filename = filename + '.csv'
    csv_mod_filename = filename + '_mod' + '.csv'
    
    # Request data, Write .gz file to local directory
    web_response = requests.get(URL)
    open(gz_filename, 'wb').write(web_response.content)

    # Extract .csv from .gz and Write to local directory 
    with gzip.open(gz_filename, 'rb') as data_input: 
        with open(csv_filename, 'wb') as data_output: 
            shutil.copyfileobj(data_input, data_output)

    # drop id column
    with open(csv_filename, "r") as source: 
        reader = csv.reader(source)
        with open(csv_mod_filename, "w") as result: 
            writer = csv.writer(result)
            for r in reader:
                writer.writerow((r[0],r[2], r[3], r[4], r[5]))


    # Upload csv to S3
    bucket.upload_file(csv_mod_filename, csv_mod_filename) 
   

def main():

    # Create Bucket
    s3 = boto3.resource('s3')
    bucketName = 'zhuje041022'
    s3.create_bucket(Bucket = bucketName)
    bucket = s3.Bucket(bucketName)

	# Configure Bucket Policy to Allow Access to Objects 
    bucket.Acl().put(ACL = 'public-read')
    client = boto3.client('s3')
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

#    # Extract Review Data from Specific Cities, Then Upload to S3
#    print("Requesting and Extracting data in progress...")
#    extractAndUpload(BRISTOL_UK_URL, 'bristol', bucket)
#    extractAndUpload(CHICAGO_USA_URL, 'chicago', bucket)
#    extractAndUpload(ASHEVILLE_USA_URL, 'ashville', bucket)
#    extractAndUpload(WASHINGTONDC_USA_URL, 'washington_dc', bucket)
#    extractAndUpload(BOSTON_URL, 'boston', bucket)

    # Read csv from S3 then put item in DynamoDB
    read_csv_from_s3(bucketName, 'bostonmod.csv', 'comments')

if __name__ == '__main__':
        main()
