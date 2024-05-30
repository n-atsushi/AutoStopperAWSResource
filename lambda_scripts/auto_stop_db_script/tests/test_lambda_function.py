import boto3
import pytest
import os
import json
import shutil
import sqlite3
from moto import mock_aws
from unittest import mock
from ..app import lambda_function


test_s3_env_dict = json.loads(open("env/lambda_function_env.json", "r").read())


@mock_aws
@mock.patch.dict(os.environ, test_s3_env_dict)
def test_download_s3_db_file(monkeypatch):
    conn = boto3.client("s3", os.environ['REGION_NAME'])
    conn.create_bucket(Bucket=os.environ['S3_AUTO_RESOURCE_DB_BUCKET'])

    db_s3_file = os.path.join(os.environ['S3_AUTO_RESOURCE_DB_PATH'],
                              os.environ['S3_AUTO_RESOURCE_DB_OBJ'])

    conn.upload_file('../tmp/' + os.environ['S3_AUTO_RESOURCE_DB_OBJ'],
                     os.environ['S3_AUTO_RESOURCE_DB_BUCKET'], db_s3_file)

    monkeypatch.setattr(lambda_function, "s3_client",
                        boto3.client('s3',
                                     region_name=os.environ['REGION_NAME']))

    lambda_function.download_s3_db_file()

    if os.path.exists('/tmp/' + os.environ['S3_AUTO_RESOURCE_DB_OBJ']):
        os.remove('/tmp/' + os.environ['S3_AUTO_RESOURCE_DB_OBJ'])
        assert True
    else:
        assert False

@mock_aws
@mock.patch.dict(os.environ, test_s3_env_dict)
def test_upload_s3_db_file(monkeypatch):
    shutil.copy('../tmp/aws_resources.db',
                '/tmp/aws_resources.db')

    conn = boto3.client("s3", os.environ['REGION_NAME'])
    conn.create_bucket(Bucket=os.environ['S3_AUTO_RESOURCE_DB_BUCKET'])

    db_s3_file = os.path.join(os.environ['S3_AUTO_RESOURCE_DB_PATH'],
                              os.environ['S3_AUTO_RESOURCE_DB_OBJ'])


    monkeypatch.setattr(lambda_function, "s3_client",
                        boto3.client('s3',
                                     region_name=os.environ['REGION_NAME']))
    lambda_function.upload_file_db_to_s3()

    if os.path.exists('/tmp/' + os.environ['S3_AUTO_RESOURCE_DB_OBJ']):
        os.remove('/tmp/' + os.environ['S3_AUTO_RESOURCE_DB_OBJ'])
        assert True
    else:
        assert False

@mock_aws
@mock.patch.dict(os.environ, test_s3_env_dict)
def test_download_s3_yml_file(monkeypatch):
    conn = boto3.client("s3", os.environ['REGION_NAME'])
    conn.create_bucket(Bucket=os.environ['S3_AUTO_RESOURCE_YML_BUCKET'])

    yml_s3_file_path = 'ec2/i-0fb61b1ac0e16ba3f.yml'
    yml_file = str.split(yml_s3_file_path, "/")[1]

    conn.upload_file('../tmp/i-0fb61b1ac0e16ba3f.yml',
                     os.environ['S3_AUTO_RESOURCE_YML_BUCKET'],
                     yml_s3_file_path)

    monkeypatch.setattr(lambda_function, "s3_client",
                        boto3.client('s3',
                                     region_name=os.environ['REGION_NAME']))

    lambda_function.download_s3_yml_file(yml_s3_file_path)

    if os.path.exists('/tmp/' + yml_file):
        os.remove('/tmp/' + yml_file)
        assert True
    else:
        assert False


def test_get_s3_event_object_record():
    # put yml file to s3 bucket
    event_response_put = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3',
                          'awsRegion': 'ap-northeast-1',
                          'eventTime': '2024-05-28T20:35:20.766Z',
                          'eventName': 'ObjectCreated:Put',
                          'userIdentity': {'principalId': 'AC78JVZ7116OV'},
                          'requestParameters': {
                              'sourceIPAddress': '14.9.218.0'},
                          'responseElements': {
                              'x-amz-request-id': 'DY92R8AB5XCRZH74',
                              'x-amz-id-2': '/dE2AWq/wW4GKsgJCIvAU8bPO1e'
                                            '/FO5HpQFEmGg4S'
                                            '+nupIE8OtqHts9Tt25pdu'
                                            '/Sfqamb6fMk30VQw/wCsuGGQK9v2EJ//vF'},
                          's3': {'s3SchemaVersion': '1.0',
                                 'configurationId': 'CREATE_YML',
                                 'bucket': {
                                     'name': 's3-auto-resource-yml-atsushi',
                                     'ownerIdentity': {
                                         'principalId': 'AC78JVZ7116OV'},
                                     'arn': 'arn:aws:s3:::s3-auto-resource'
                                            '-yml-atsushi'},
                                 'object': {
                                     'key': 'ec2/i-0fb61b1ac0e16ba3f.yml',
                                     'size': 407,
                                     'eTag': '7571e51ee1ab12eee3c852cb9ba34452',
                                     'sequencer': '0066564008B89FDF39'}}}]}
    event_put, object_info = lambda_function.get_s3_event_object_record(event_response_put)


    if (object_info[0]['key'] == 'ec2/i-0fb61b1ac0e16ba3f.yml'
            and event_put == 'Put'):
        assert True
    else:
        assert False

    # delete yml file from s3 bucket
    event_data_delete = {'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'ap-northeast-1', 'eventTime': '2024-05-28T20:39:31.868Z', 'eventName': 'ObjectRemoved:Delete', 'userIdentity': {'principalId': 'AC78JVZ7116OV'}, 'requestParameters': {'sourceIPAddress': '172.16.160.128'}, 'responseElements': {'x-amz-request-id': 'G7TWV6NBB8XDMJRS', 'x-amz-id-2': 'bq1PazWtGussL+zWu4AVAjURauYlj1vJTihwYey1BkV6ozp99pt40sFydVGEpVhG6yRcYxdW1Ozk/7HSAi+zSzp6pFg5p1FIgPohyraBo7g='}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'CREATE_YML', 'bucket': {'name': 's3-auto-resource-yml-atsushi', 'ownerIdentity': {'principalId': 'AC78JVZ7116OV'}, 'arn': 'arn:aws:s3:::s3-auto-resource-yml-atsushi'}, 'object': {'key': 'ec2/i-0fb61b1ac0e16ba3f.yml', 'sequencer': '0066564103D64F2856'}}}]}

    event_delete, object_info = lambda_function.get_s3_event_object_record(
        event_data_delete)

    if (object_info[0]['key'] == 'ec2/i-0fb61b1ac0e16ba3f.yml'
            and event_delete == 'Delete'):
        assert True
    else:
        assert False


def test_read_yaml_file():
    shutil.copy('../tmp/i-0fb61b1ac0e16ba3f.yml','/tmp/i-0fb61b1ac0e16ba3f.yml')
    yml_file = 'i-0fb61b1ac0e16ba3f.yml'
    data = lambda_function.read_yaml_file(yml_file)
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'
                 , 'Saturday', 'Sunday']

    if os.path.isfile('/tmp/' + yml_file):
        os.remove('/tmp/' + yml_file)
    instance_data = data['ec2_instance'][0]
    print(instance_data)
    instance_id = instance_data['instance_id']
    for key, value in instance_data['start_time'].items():
        if key in week_days:
            if key in instance_data['end_time']:
                assert True


def test_insert_ec2_instance():

    # insert
    aws_resource_db_file = '../tmp/aws_resources.db'

    lambda_function.insert_ec2_instance(
        aws_resource_db_file,
        instance_id='i-0fb61b1ac0e16ba3f',
        instance_type='t2.micro',
        state='running',
        region='ap-northeast-1'
    )

    # select
    conn = sqlite3.connect(aws_resource_db_file)
    select_query = """
                 SELECT instance_id, instance_type, state, region
                 FROM ec2
                 WHERE instance_id = ?;
                 """
    cursor = conn.cursor()
    cursor.execute(select_query, ('i-0fb61b1ac0e16ba3f',))
    rows = cursor.fetchall()
    conn.close()
    assert True if rows[0][0] == 'i-0fb61b1ac0e16ba3f' else False
    # delete
    conn = sqlite3.connect(aws_resource_db_file)
    delete_query = "DELETE FROM ec2 WHERE instance_id = ?"
    cursor = conn.cursor()
    cursor.execute(delete_query, ('i-0fb61b1ac0e16ba3f',))
    conn.commit()


def test_insert_ec2_instance_launch_times():

    aws_resource_db_file = '../tmp/aws_resources.db'

    shutil.copy('../tmp/i-0fb61b1ac0e16ba3f.yml',
                '/tmp/i-0fb61b1ac0e16ba3f.yml')
    yml_file = 'i-0fb61b1ac0e16ba3f.yml'
    data = lambda_function.read_yaml_file(yml_file)
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'
        , 'Saturday', 'Sunday']

    if os.path.isfile('/tmp/' + yml_file):
        os.remove('/tmp/' + yml_file)
    instance_data = data['ec2_instance'][0]
    instance_id = instance_data['instance_id']

    lambda_function.insert_ec2_instance_launch_times(
        aws_resource_db_file,
        instance_id,
        instance_data['start_time'],
        instance_data['end_time'])

    lambda_function.delete_instance_by_id(aws_resource_db_file,'i-0fb61b1ac0e16ba3f')

    assert True


def test_delete_instance_by_id():
    # insert
    aws_resource_db_file = '../tmp/aws_resources.db'
    lambda_function.insert_ec2_instance(
        aws_resource_db_file,
        instance_id='i-0fb61b1ac0e16ba3f',
        instance_type='t2.micro',
        state='running',
        region='ap-northeast-1'
    )
    shutil.copy('../tmp/i-0fb61b1ac0e16ba3f.yml',
                '/tmp/i-0fb61b1ac0e16ba3f.yml')
    yml_file = 'i-0fb61b1ac0e16ba3f.yml'
    data = lambda_function.read_yaml_file(yml_file)
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'
        , 'Saturday', 'Sunday']

    if os.path.isfile('/tmp/' + yml_file):
        os.remove('/tmp/' + yml_file)
    instance_data = data['ec2_instance'][0]
    instance_id = instance_data['instance_id']

    lambda_function.insert_ec2_instance_launch_times(
        aws_resource_db_file,
        instance_id,
        instance_data['start_time'],
        instance_data['end_time'])

    # delete
    lambda_function.delete_instance_by_id(aws_resource_db_file,
                                          'i-0fb61b1ac0e16ba3f')
    if lambda_function.check_instance_existence(aws_resource_db_file,
                                                'i-0fb61b1ac0e16ba3f'):
        assert False
    else:
        assert True


def test_check_instance_existence():
    # insert
    aws_resource_db_file = '../tmp/aws_resources.db'
    lambda_function.insert_ec2_instance(
        aws_resource_db_file,
        instance_id='i-0fb61b1ac0e16ba3f',
        instance_type='t2.micro',
        state='running',
        region='ap-northeast-1'
    )
    shutil.copy('../tmp/i-0fb61b1ac0e16ba3f.yml',
                '/tmp/i-0fb61b1ac0e16ba3f.yml')
    yml_file = 'i-0fb61b1ac0e16ba3f.yml'
    data = lambda_function.read_yaml_file(yml_file)
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'
        , 'Saturday', 'Sunday']

    if os.path.isfile('/tmp/' + yml_file):
        os.remove('/tmp/' + yml_file)
    instance_data = data['ec2_instance'][0]
    instance_id = instance_data['instance_id']

    lambda_function.insert_ec2_instance_launch_times(
        aws_resource_db_file,
        instance_id,
        instance_data['start_time'],
        instance_data['end_time'])

    # check
    if lambda_function.check_instance_existence(aws_resource_db_file,
                                                'i-0fb61b1ac0e16ba3f'):
        assert True
    else:
        assert False

    # delete
    lambda_function.delete_instance_by_id(aws_resource_db_file,'i-0fb61b1ac0e16ba3f')

    #check
    if lambda_function.check_instance_existence(aws_resource_db_file,
                                                'i-0fb61b1ac0e16ba3f'):
        assert False
    else:
        assert True

# def test_select_ec2_instance_start():
#
#     aws_resource_db_file = '../tmp/aws_resources.db'
#
#     rows = lambda_function.select_ec2_instance_start(
#         aws_resource_db_file,
#         day='Monday',
#         time='08:00'
#     )
#     print(rows[0][0])
#     assert len(rows) == 1
#
#
# def test_select_ec2_instance_stop():
#
#     aws_resource_db_file = '../tmp/aws_resources.db'
#
#     rows = lambda_function.select_ec2_instance_stop(
#         aws_resource_db_file,
#         day='Monday',
#         time='20:00'
#     )
#
#     print(rows)
#
#     assert len(rows) == 1

# @pytest.fixture()
# def set_envs(monkeypatch):
#     monkeypatch.setenv('REGION_NAME','us-east-1')
