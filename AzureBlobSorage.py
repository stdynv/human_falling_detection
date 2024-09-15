import os
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from datetime import datetime, timedelta
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class AzureBlobUploader:
    def __init__(self, connection_string, container_name):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
    
    def ensure_container_exists(self):
        """Ensure that the container exists in Azure Blob Storage."""
        try:
            if not self.container_client.exists():
                logging.info(f"Container '{self.container_name}' does not exist. Creating container...")
                self.container_client.create_container()
                logging.info(f"Container '{self.container_name}' created successfully.")
            else:
                logging.info(f"Container '{self.container_name}' exists.")
        except Exception as e:
            logging.error(f"Error ensuring container exists: {str(e)}")
            sys.exit(1)

    def upload_video(self, file_path):
        """Upload video to Azure Blob Storage."""
        try:
            filename = os.path.basename(file_path)
            blob_client = self.container_client.get_blob_client(filename)

            logging.info(f"Uploading {filename} to Azure Blob Storage...")
            content_settings = ContentSettings(content_type='video/mp4')

            # Upload the file
            with open(file_path, "rb") as video_file:
                blob_client.upload_blob(video_file, overwrite=True, content_settings=content_settings)

            logging.info(f"Video {filename} uploaded successfully.")

            # After uploading the video, generate the SAS URL and log it
            sas_url = self.generate_sas_link(filename)
            logging.info(f"SAS URL for {filename}: {sas_url}")
            return sas_url
        except Exception as e:
            logging.error(f"Error uploading video {filename}: {str(e)}")
            sys.exit(1)

    def generate_sas_link(self, blob_name, expiry_hours=1):
        """Generate a SAS link for the uploaded video."""
        try:
            sas_token = generate_blob_sas(
                account_name=self.blob_service_client.account_name,
                container_name=self.container_name,
                blob_name=blob_name,
                account_key=self.blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
            )

            sas_url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"
            return sas_url
        except Exception as e:
            logging.error(f"Error generating SAS link for {blob_name}: {str(e)}")
            sys.exit(1)
