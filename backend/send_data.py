# send data to data lake

from azure.storage.blob import BlobServiceClient, BlobCLientm ContainerClient
from config import Config
import pyodbc
import datetime

blobsotage_client = BlobServiceClient.from_connection_string('')
container_name = ''
blob_client = blob_service_client.get_blob_client(container=container_name,blob='fall.mp4')

try : 
    with open('fall.mp4','rb') as data : 
        blob_client.upload_blob(data)
    video_url = blob_client.url
    upload_status = 'data uploaded'

except Exception as e :
    print('error iploading data to blob')


conn = Config.get_db_connection()
cursor = conn.cursor()
rasberry_id = 'ras-123'
incident_date = datetime.datetime.now()
description = 'chute personne'

if video_url: 
    cursor.execute("""INSERT INTO incidents (rasberry_id,incident_date,description,video_url,status)
                   
                   VALUES (?, ?, ?, ?, ?)
                   
                   """,rasberry_id,incident_date,description,video_url,upload_status)



# sp=r&st=2024-08-27T16:37:07Z&se=2024-08-28T00:37:07Z&sv=2022-11-02&sr=c&sig=wDfwy%2FNlDMVv%2BqM%2Bn859Mz%2FCOKSQ1msbm4dvVzrIteQ%3D
# sp=r&st=2024-08-27T16:49:07Z&se=2024-08-28T00:49:07Z&spr=https&sv=2022-11-02&sr=b&sig=Re4gcMTPhckBelxs8FEUDE9hBPcdTOkMM86763AOE2Y%3D
