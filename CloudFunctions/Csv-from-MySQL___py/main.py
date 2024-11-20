from google.cloud import bigquery
import requests
import google
import google.oauth2
import google.oauth2.id_token
import googleapiclient
from googleapiclient import discovery
import oauth2client
import oauth2client.client
from oauth2client.client import GoogleCredentials
import datetime
from google.cloud import storage

def hello_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    BQMaxId=""
    Query = ""
    tDate = datetime.datetime.today().strftime('%Y%m%d')
    yDate = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y%m%d')
    bq_client = bigquery.Client()
    query_job = bq_client.query(Query)
    rows_df = query_job.result()
    for row in rows_df:
         BQMaxId = str(row.MaxId)
         
    print(BQMaxId)
    print(tDate)
    sqlQuery = ""
    print(sqlQuery)
    shortfilename = "workload/CF_SQL_"+tDate+"_after_"+BQMaxId+".csv"
    filename = "gs://[bucket]/"+shortfilename
    print(filename)

    storage_client = storage.Client()
    bucket_name = '[bucket]'
    bucket = storage_client.bucket(bucket_name)
    #blob = storage.Blob(bucket=bucket, name=shortfilename)
    blob = bucket.get_blob(blob_name = shortfilename)
    stats = storage.Blob(bucket=bucket, name=shortfilename).exists(storage_client)
    size = 0

    try:
     size = blob.size
    except:
     if stats == False:
          size = 0     

    print(str(size) + " bytes")

    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('sqladmin', 'v1beta4', credentials=credentials)
    project = # TODO: Update placeholder value.
    instance = # TODO: Update placeholder value.
    instances_export_request_body = {
        "exportContext": {
			"fileType": "CSV","uri": filename,
			"csvExportOptions": {
                    "selectQuery": sqlQuery
                    }
               }
        }
    request = service.instances().export(project=project, instance=instance, body=instances_export_request_body)
    if stats == False or size == 0:
         response = request.execute()
    else:
         print("File " + filename + " already exists!") 
    