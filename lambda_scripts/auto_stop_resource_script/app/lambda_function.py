import os
import sys
import boto3
import sqlite3
from datetime import datetime, timezone, timedelta


region_name = os.environ.get('REGION_NAME', 'ap-northeast-1')
ec2_client = boto3.client('ec2', region_name=region_name)
s3_client = boto3.client('s3', region_name=region_name)

db_bucket_name = os.environ.get('S3_AUTO_RESOURCE_DB_BUCKET'
                                , 's3-auto-resource-db-atsushi')

db_bucket_path = os.environ.get('S3_AUTO_RESOURCE_DB_PATH'
                                , 'db-resources')

db_bucket_obj = os.environ.get('S3_AUTO_RESOURCE_DB_OBJ'
                                , 'aws_resources.db')
# auto_stop_resource_script
db_s3_file = os.path.join(db_bucket_path, db_bucket_obj)


def get_tokyo_hour_minute_now():
    # 現在のUTC時刻を取得
    utc_now = datetime.now(timezone.utc)
    print(f"UTC now: {utc_now}")

    # 東京のタイムゾーン（UTC+9時間）
    tokyo_tz = timezone(timedelta(hours=9))

    # UTC時刻を東京の時刻に変換
    tokyo_time = utc_now.astimezone(tokyo_tz)

    return f"{str(tokyo_time.hour).zfill(2)}:{str(tokyo_time.minute).zfill(2)}"


def get_week_today():
    #現在の曜日を取得
    return datetime.today().strftime('%A')


def initialize_db_connection(func):
    def _wrapper(aws_resource_db_file, *args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect(aws_resource_db_file)
            return func(conn, *args, **kwargs)
        except Exception as e:
            print('Connection Error sqlite3:', e)
        finally:
            conn.close() if conn else None

    return _wrapper

@initialize_db_connection
def select_ec2_instance_start(conn, day='', time=''):
    select_query = """
             SELECT ec2.instance_id, lt.launch_day, lt.start_time
             FROM ec2
             JOIN launch_times lt ON ec2.instance_id = lt.instance_id
             WHERE lt.launch_day = ? and lt.start_time = ?;
             """
    cursor = conn.cursor()
    cursor.execute(select_query, (day, time))
    rows = cursor.fetchall()

    return rows

@initialize_db_connection
def select_ec2_instance_stop(conn, day='', time=''):
    select_query = """
             SELECT ec2.instance_id, lt.launch_day, lt.end_time
             FROM ec2
             JOIN launch_times lt ON ec2.instance_id = lt.instance_id
             WHERE lt.launch_day = ? and lt.end_time = ?;
             """
    cursor = conn.cursor()
    cursor.execute(select_query, (day, time))
    rows = cursor.fetchall()

    return rows

def download_s3_db_file():
    try:
        s3_client.download_file(db_bucket_name, db_s3_file,
            '/tmp/' + db_bucket_obj)
    except Exception as e:
        print('S3 download error')


def start_ec2_instance(instance_id):
    ec2_client.start_instances(
        InstanceIds=[
            instance_id
        ]
    )
    print(f'{instance_id} を開始しました')


def stop_ec2_instance(instance_id):
    ec2_client.stop_instances(
        InstanceIds=[
            instance_id
        ]
    )
    print(f'{instance_id} を停止しました')


def get_ec2_instance_status(instance_id):
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    state = response['Reservations'][0]['Instances'][0]['State']['Name']

    return state


def main():

    # 曜日,現在時刻を取得
    week_day = get_week_today()
    now_time = get_tokyo_hour_minute_now()

    # S3からaws_resources.dbをダウンロードしてくる
    download_s3_db_file()

    # DBのテーブルから起動するインスタンスを抽出する
    aws_resource_db_file = '/tmp/' + db_bucket_obj

    start_instance_rows = select_ec2_instance_start(
        aws_resource_db_file,
        day=week_day,
        time=now_time
    )

    for start_instance in start_instance_rows:
        start_ec2_instance(start_instance[0])

    # DBのテーブルから起動するインスタンスを抽出する
    stop_instance_rows = select_ec2_instance_stop(
        aws_resource_db_file,
        day=week_day,
        time=now_time
    )

    for stop_instance in stop_instance_rows:
        stop_ec2_instance(stop_instance[0])


def handler(event, context):
    print('処理を開始しました')
    main()
    print('処理を終了しました')
