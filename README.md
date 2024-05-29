# AutoStopperAWSResource

AutoStopperAWSResource

> **注意**
このプロジェクトはまだ作成中です。

AutoStopperAWSResourceはサーバーレス環境におけるAWSリソースの管理を効率化し、コストを削減するソリューションを提供します。Terraformを使用してAWSインフラストラクチャをコード化し、Lambda関数を定期的に起動してリソースの状態を監視し、必要に応じて停止します。さらに、S3を使用してログを保存し、イベントブリッジを使用してタスクをスケジュールします。

## 使用技術

- Python 3.12
- AWS
- Terraform
- S3
- Lambda
- EventBridge
- SQLite3(リソースの操作用)
- yml(主にリソースの構成管理用)

# 構成図
![構成](https://github.com/n-atsushi/AutoStopperAWSResource/structure.png)
