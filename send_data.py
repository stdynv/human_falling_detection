import requests

# Define the URL for the upload endpoint
url = "http://127.0.0.1:5000/api/azure/upload"

# Path to the video file you want to upload
video_path = "quedas_1.mp4"

# Open the video file in binary mode
with open(video_path, 'rb') as video_file:
    # Send the POST request with the video file
    response = requests.post(url, files={'video': video_file})

# Check if the response is successful
if response.status_code == 200:
    # Print the JSON response, which includes the SAS URL
    print("Success:", response.json())
else:
    # Print the error message if something went wrong
    print(f"Failed to upload video. Status code: {response.status_code}")
    print("Error:", response.text)






















"""from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import os

class AzureBlobStorageClient:
    def __init__(self, connection_string, container_name):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)

        # Ensure the container exists
        self._ensure_container()

    def _ensure_container(self):
        if not self.container_client.exists():
            self.container_client.create_container()

    def upload_video(self, video_path):
        video_name = os.path.basename(video_path)
        blob_client = self.container_client.get_blob_client(video_name)

        with open(video_path, "rb") as video_file:
            blob_client.upload_blob(video_file)
            print(f"Video {video_name} uploaded successfully.")

        return video_name

    def generate_sas_link(self, blob_name, expiry_hours=1):
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


# Usage example
if __name__ == "__main__":
    # Replace these with your actual values
    CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=humanfalldata;AccountKey=M1Y59oTRKPFcLi47dj99zdmKKqXuNRYirr48ujkfgXH2irTcxtMZrkIFImP8ByGmAX3ioH5yDNPc+AStRrIkrg==;EndpointSuffix=core.windows.net"
    CONTAINER_NAME = "videocontainer"
    VIDEO_PATH = "./quedas.mp4"

    azure_client = AzureBlobStorageClient(CONNECTION_STRING, CONTAINER_NAME)
    

    # Upload the video 
    try:
        uploaded_video_name = azure_client.upload_video(VIDEO_PATH)
        sas_link = azure_client.generate_sas_link(uploaded_video_name)
        print("SAS Link:", sas_link)
    except Exception as e :
        print(e)

    # Generate a SAS link valid for 1 hour

"""
    
    
