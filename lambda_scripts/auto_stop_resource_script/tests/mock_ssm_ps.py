import boto3

PARAM_DATA_FILE = "../parameter_data/parameter_list.tsv"


def prepare_ssm_parameters():
    ssm = boto3.client("ssm", "ap-northeast-1")

    with open(PARAM_DATA_FILE, encoding="utf-8", newline="") as f:
        for line in f:
            cols = [x.strip() for x in line.split("\t")]
            ssm.put_parameter(Name=cols[0], Value=cols[2], Type=cols[1])
