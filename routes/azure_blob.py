from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, ContentSettings
from datetime import datetime, timedelta
import logging
from flask import Blueprint, jsonify, request

azure_bp = Blueprint('azure_bp', __name__)

# Initialize Azure Blob Storage Client
CONNECTION_STRING = "your_connection_string"
CONTAINER_NAME = "videocontainer"

blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

def ensure_container_exists():
    try:
        if not container_client.exists():
            container_client.create_container()
        logging.info("Container exists or created successfully.")
    except Exception as e:
        logging.error(f"Error ensuring container exists: {str(e)}")
        raise

def upload_video_to_blob(file_stream, filename):
    try:
        logging.info(f"Uploading {filename} to Azure Blob Storage...")
        content_settings = ContentSettings(content_type='video/mp4')
        blob_client = container_client.get_blob_client(filename)
        blob_client.upload_blob(file_stream, overwrite=True, content_settings=content_settings)
        logging.info(f"Video {filename} uploaded successfully.")
    except Exception as e:
        logging.error(f"Error uploading video {filename}: {str(e)}")
        raise

def generate_sas_link(blob_name, expiry_hours=1):
    try:
        sas_token = generate_blob_sas(
            account_name=blob_service_client.account_name,
            container_name=CONTAINER_NAME,
            blob_name=blob_name,
            account_key=blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )
        
        sas_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{blob_name}?{sas_token}"
        return sas_url
    except Exception as e:
        logging.error(f"Error generating SAS link for {blob_name}: {str(e)}")
        raise

@azure_bp.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    video_file = request.files['video']
    video_filename = video_file.filename
    
    try:
        # Ensure the container exists
        ensure_container_exists()
        
        # Upload the video to Azure Blob Storage
        upload_video_to_blob(video_file.stream, video_filename)
        
        # Generate a SAS link for the uploaded video
        sas_link = generate_sas_link(video_filename)
        
        return jsonify({"sas_url": sas_link}), 200
    
    except KeyError as e:
        logging.error(f"KeyError during video upload: {str(e)}")
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    
    except ValueError as e:
        logging.error(f"ValueError during video upload: {str(e)}")
        return jsonify({"error": f"Invalid value: {str(e)}"}), 400

    except PermissionError as e:
        logging.error(f"PermissionError during video upload: {str(e)}")
        return jsonify({"error": "Permission denied"}), 403

    except FileNotFoundError as e:
        logging.error(f"FileNotFoundError during video upload: {str(e)}")
        return jsonify({"error": f"File not found: {str(e)}"}), 404

    except Exception as e:
        logging.error(f"Error during upload: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@azure_bp.route('/', methods=['GET'])
def hello():
    return 'Hi Azure'
