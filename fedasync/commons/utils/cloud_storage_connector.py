from abc import ABC
import logging
import boto3
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class AWSConnector(ABC):
    """Class for connecting to AWS S3"""

    def __init__(self, access_key, secret_key) -> None:
        self.s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
        logging.info(f'Connected to AWS server')

    def upload(self, local_file_path: str, remote_file_path: str, bucket_name: str):
        """Uploads new global model to AWS"""
        filename = local_file_path.split('/')[-1]

        try:
            self.s3.upload_file(local_file_path, bucket_name, remote_file_path)
            logging.info(f'Successfully uploaded {filename} to {remote_file_path}')
        except Exception as e:
            logging.error(e)
    
    def download(self, bucket_name, remote_file_path, local_file_path):
        """Downloads a file from AWS"""

        filename = remote_file_path.split('/')[-1]
        try:
            self.s3.download_file(bucket_name, remote_file_path, local_file_path)
            logging.info(f'Downloaded {filename}')
        except Exception as e:
            logging.error(e)

