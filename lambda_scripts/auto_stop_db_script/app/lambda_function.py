import os
import boto3
import sqlite3
import yaml

"""
auto_stop_db_script
"""

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

# auto_stop_resource_script
db_s3_file = os.path.join(db_bucket_path, db_bucket_obj)


def download_s3_db_file():
    try:
        s3_client.download_file(db_bucket_name, db_s3_file,
            '/tmp/' + db_bucket_obj)
        print('S3 download Success')
    except Exception as e:
        print('S3 download error')


def upload_file_db_to_s3():
    try:
        s3_client.upload_file('/tmp/' + db_bucket_obj, db_bucket_name
                              , db_s3_file)
        print('S3 upload Success')
    except Exception as e:
        print(f'S3 upload error: {e}')


def download_s3_db_file():
    try:
        s3_client.download_file(db_bucket_name, db_s3_file,
            '/tmp/' + db_bucket_obj)
        print('S3 download Success')
    except Exception as e:
        print('S3 download error')

def download_s3_yml_file(yml_s3_file_path):
    yml_file = str.split(yml_s3_file_path,"/")[1]

    try:
        s3_client.download_file(yml_bucket_name, yml_s3_file_path,
                                '/tmp/' + yml_file)
        print('S3 download Success')
    except Exception as e:
        print('S3 download error')


# Recordsの中からobject情報を取り出す関数
def get_s3_event_object_record(event_data):
    records = event_data.get('Records', [])
    object_info = []
    event_name = ''
    for record in records:
        s3_info = record.get('s3', {})
        event_name = str.split(record['eventName'],':')[1]
        object_info.append(s3_info.get('object', {}))
    return event_name, object_info


def read_yaml_file(yml_file):
    """
    指定されたパスのYAMLファイルを読み込み、辞書として返す関数。

    :param yml_file: 読み込むYAMLファイルのパス
    :return: 読み込んだデータを含む辞書
    """
    try:
        with open('/tmp/' + yml_file, 'r') as file:
            yml_data = yaml.safe_load(file)
            return yml_data
    except Exception as e:
        print(f"Error reading {yml_file}: {e}")
        return None


#sqlite3
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
def check_instance_existence(conn, instance_id):
    try:
        cursor = conn.cursor()

        select_query = """
            SELECT COUNT(*) FROM ec2
            WHERE instance_id = ?;
        """
        cursor.execute(select_query, (instance_id,))
        result = cursor.fetchone()[0]

        if result > 0:
            print(
                f"Instance with ID {instance_id} already exists in the database.")
            return True
        else:
            print(
                f"Instance with ID {instance_id} does not exist in the database.")
            return False
    except sqlite3.Error as e:
        print(f"Error checking instance existence: {e}")
        return False


@initialize_db_connection
def insert_ec2_instance(conn, instance_id, instance_type, state, region):
    try:
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO ec2 (instance_id, instance_type, state, region)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(insert_query, (instance_id, instance_type, state, region))
        conn.commit()
        print(f"Successfully inserted instance_id {instance_id}")
    except sqlite3.Error as e:
        print(f"Error inserting instance: {e}")

@initialize_db_connection
def insert_ec2_instance_launch_times(conn, instance_id, start_times, end_times):
    try:
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO launch_times (instance_id, launch_day, start_time, end_time)
        VALUES (?, ?, ?, ?)
        """
        for week_day, start_time in start_times.items():
            end_time = end_times[week_day]
            print(f'{instance_id}, {week_day} , {start_time}, {end_time}')
            cursor.execute(insert_query, (instance_id, week_day, start_time,
                                          end_time))
        conn.commit()
        print(f"Successfully inserted instance_id {instance_id} launch times")
    except sqlite3.Error as e:
        print(f"Error inserting instance: {e} launch times")


@initialize_db_connection
def delete_instance_by_id(conn, instance_id):
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                 'Saturday', 'Sunday']
    try:
        cursor = conn.cursor()
        delete_query_ec2 = """
            DELETE FROM ec2
            WHERE instance_id = ?;
        """
        delete_query_ec2_launch_times = """
            DELETE FROM launch_times
            WHERE instance_id= ? AND launch_day= ?;
        """
        cursor.execute(delete_query_ec2, (instance_id,))
        for day in week_days:
            cursor.execute(delete_query_ec2_launch_times,
                           (instance_id, day))
        conn.commit()
        print(f"Successfully deleted instance with ID {instance_id}")
    except sqlite3.Error as e:
        print(f"Error deleting instance: {e}")

def main(event):
    # S3からaws_resources.dbをダウンロードしてくる
    download_s3_db_file()
    aws_resource_db_file = '/tmp/' + db_bucket_obj

    # eventから、S3で連携されたファイルについて、パスを取得する
    event_name, object_info = get_s3_event_object_record(event)
    yml_s3_file_path = object_info[0]['key']
    yml_s3_file = str.split(yml_s3_file_path,'/')[1]
    instance_id = str.split(yml_s3_file,".")[0]

    # eventで処理を分ける
    if event_name == 'Put':
        download_s3_yml_file(yml_s3_file_path)
        yml_data = read_yaml_file(yml_s3_file)
        instance_data = yml_data['ec2_instance'][0]

        if check_instance_existence(aws_resource_db_file, instance_id):
            delete_instance_by_id(aws_resource_db_file, instance_id)

        insert_ec2_instance(
            aws_resource_db_file,
            instance_id=instance_data['instance_id'],
            instance_type=instance_data['instance_type'],
            state=instance_data['state'],
            region=instance_data['region']
        )
        insert_ec2_instance_launch_times(
            aws_resource_db_file,
            instance_id=instance_data['instance_id'],
            start_times=instance_data['start_time'],
            end_times=instance_data['end_time']
        )
    elif event_name == 'Delete':
        delete_instance_by_id(aws_resource_db_file, instance_id)

    # dbに登録して完了
    upload_file_db_to_s3()

    # ダウンロード後にそのファイルの内容を元にdbに登録する
    upload_file_db_to_s3()

def handler(event, context):
    print('処理を開始しました')
    main(event)
    print('処理を終了します')
