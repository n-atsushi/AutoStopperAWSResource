import boto3
import pytest
import os
import json
import re
from moto import mock_aws
from unittest import mock

from ..app import lambda_function
from . import mock_ssm_ps

test_s3_env_dict = json.loads(open("env/lambda_function_env.json", "r").read())

@pytest.fixture
@mock_aws
def setup_ec2_instance():
    def _setup_ec2_instance(min_count, max_count):
        ec2 = boto3.client('ec2', region_name='ap-northeast-1')

        ec2_response = ec2.run_instances(
                ImageId='ami-12345678',
                MinCount=min_count,
                MaxCount=max_count,
                InstanceType="t2.micro"
        )
        return ec2_response

    return _setup_ec2_instance

@mock_aws
def test_start_ec2_instance(setup_ec2_instance, monkeypatch):
    ec2_response = setup_ec2_instance(1, 1)

    instance_id = ec2_response['Instances'][0]['InstanceId']

    instance_count = len(ec2_response['Instances'])
    assert instance_count == 1

    monkeypatch.setattr(lambda_function, "ec2_client",
                        boto3.client('ec2', region_name='ap-northeast-1'))

    # Stop Instance
    lambda_function.stop_ec2_instance(instance_id)

    # Start Instance
    lambda_function.start_ec2_instance(instance_id)

    assert lambda_function.get_ec2_instance_status(instance_id) == 'running'



@mock_aws
def test_stop_ec2_instance(setup_ec2_instance, monkeypatch):
    ec2_response = setup_ec2_instance(1, 1)

    instance_id = ec2_response['Instances'][0]['InstanceId']

    instance_count = len(ec2_response['Instances'])
    assert instance_count == 1

    monkeypatch.setattr(lambda_function, "ec2_client",
                        boto3.client('ec2', region_name='ap-northeast-1'))

    # Stop Instance
    lambda_function.stop_ec2_instance(instance_id)
    assert lambda_function.get_ec2_instance_status(instance_id) == 'stopped'


@mock_aws
def test_get_ec2_instance_status(setup_ec2_instance, monkeypatch):
    ec2_response = setup_ec2_instance(1, 1)

    monkeypatch.setattr(lambda_function, "ec2_client",
                        boto3.client('ec2', region_name='ap-northeast-1'))

    instance_id = ec2_response['Instances'][0]['InstanceId']

    assert lambda_function.get_ec2_instance_status(instance_id) == 'running'


@mock_aws
@mock.patch.dict(os.environ, test_s3_env_dict)
def test_download_s3_db_file(monkeypatch):
    conn = boto3.client("s3", os.environ['REGION_NAME'])
    conn.create_bucket(Bucket=os.environ['S3_AUTO_RESOURCE_DB_BUCKET'])

    db_s3_file = os.path.join(os.environ['S3_AUTO_RESOURCE_DB_PATH'],
                              os.environ['S3_AUTO_RESOURCE_DB_OBJ'])

    conn.upload_file('../tmp/' + os.environ['S3_AUTO_RESOURCE_DB_OBJ'],
                      os.environ['S3_AUTO_RESOURCE_DB_BUCKET'],db_s3_file)

    monkeypatch.setattr(lambda_function, "s3_client",
                        boto3.client('s3', region_name=os.environ['REGION_NAME']))

    lambda_function.download_s3_db_file()

    if os.path.exists('/tmp/' + os.environ['S3_AUTO_RESOURCE_DB_OBJ']):
        os.remove('/tmp/' + os.environ['S3_AUTO_RESOURCE_DB_OBJ'])
        assert True
    else:
        assert False


def test_get_test_hour_minute_now():

    time_pattern = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d|24:00$")
    time = lambda_function.get_tokyo_hour_minute_now()
    assert True if time_pattern.match(time) else False


def test_get_week_today():
    weekday_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                    'Saturday', 'Sunday']
    weekday_name = lambda_function.get_week_today()
    print(weekday_name)
    assert True if weekday_name in weekday_list else False


def test_select_ec2_instance_start():

    aws_resource_db_file = '../tmp/aws_resources.db'

    rows = lambda_function.select_ec2_instance_start(
        aws_resource_db_file,
        day='Monday',
        time='08:00'
    )
    print(rows[0][0])
    assert len(rows) == 1


def test_select_ec2_instance_stop():

    aws_resource_db_file = '../tmp/aws_resources.db'

    rows = lambda_function.select_ec2_instance_stop(
        aws_resource_db_file,
        day='Monday',
        time='20:00'
    )

    print(rows)

    assert len(rows) == 1

# @pytest.fixture()
# def set_envs(monkeypatch):
#     monkeypatch.setenv('REGION_NAME','us-east-1')
