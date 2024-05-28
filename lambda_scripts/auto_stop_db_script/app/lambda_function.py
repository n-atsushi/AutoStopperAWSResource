import os
import sys
import boto3
import sqlite3
from datetime import datetime, timezone, timedelta



region_name = os.environ.get('REGION_NAME', 'ap-northeast-1')
ec2_client = boto3.client('ec2', region_name=region_name)
s3_client = boto3.client('s3', region_name=region_name)

yml_bucket_name = os.environ.get('S3_AUTO_RESOURCE_YML_BUCKET'
                                 , 's3-auto-resource-yml-atsushi')

db_bucket_name = os.environ.get('S3_AUTO_RESOURCE_DB_BUCKET'
                                , 's3-auto-resource-db-atsushi')

db_bucket_path = os.environ.get('S3_AUTO_RESOURCE_DB_PATH'
                                , 'db-resources')

db_bucket_obj = os.environ.get('S3_AUTO_RESOURCE_DB_OBJ'
                                , 'aws_resources.db')

#sqlite3
def initialize_db_connection():
    pass


def get_records():
    pass


def insert_record():
    pass


def delete_record():
    pass


def save(name, value):
    s3_client.put_object(Bucket="my-bucket", Key=name, Body=value)


def stop_ec2_instance(instance_id):
    #e = boto3.client('ec2', region_name="ap-northeast-1")
    ec2_client.stop_instances(
        InstanceIds=[
            instance_id
        ]
    )


def get_ec2_instance_status(instance_id):
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    state = response['Reservations'][0]['Instances'][0]['State']['Name']

    return state


def get_parameter(param_key, WithDecryption=True):
    ssm_client = boto3.client("ssm", region_name="ap-northeast-1")

    response = ssm_client.get_parameters(
        Names=[
            param_key,
        ],
        WithDecryption=WithDecryption,
    )
    if len(response["Parameters"]) > 0:
        return response["Parameters"][0]["Value"]
    else:
        return None


def main():
    # eventから、S3で連携されたファイルについて、パスを取得する

    # S3からaws_resources.dbをダウンロードしてくる
    region_name = os.environ['REGION_NAME']
    pass


def handler(event, context):
    main()
    return 'Hello from AWS Lambda using Python' + sys.version + '!'
