import boto3
import pytest
import json
import os

from moto import mock_aws
from unittest import mock
from lambda_scripts.auto_stop_resource_script.app import lambda_function
from lambda_scripts.auto_stop_resource_script.tests import mock_ssm_ps

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
def test_get_parameter():
    mock_ssm_ps.prepare_ssm_parameters()
    ret1 = lambda_function.get_parameter("/test/param")
    ret2 = lambda_function.get_parameter("/test/secure_param")

    assert [ret1, ret2] == ["my_param", "my_secure_param"]


@mock_aws
@mock.patch.dict(os.environ, test_s3_env_dict)
def test_save(monkeypatch):
    conn = boto3.resource("s3", os.environ['REGION_NAME'])
    conn.create_bucket(Bucket="my-bucket")

    monkeypatch.setattr(lambda_function, "s3_client",
                        boto3.client('s3', region_name='us-east-1'))

    lambda_function.save("steve", "is awesome")
    body = conn.Object("my-bucket", "steve").get()["Body"].read().decode("utf-8")

    assert body == "is awesome"


# @pytest.fixture()
# def set_envs(monkeypatch):
#     monkeypatch.setenv('REGION_NAME','us-east-1')
