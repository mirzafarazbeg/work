def chkFile(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    import requests
    import google
    import google.oauth2
    import google.oauth2.id_token
    import googleapiclient
    import googleapiclient.discovery
    import oauth2client
    import oauth2client.client
    from oauth2client.client import GoogleCredentials
   
    file = event

    filename = event['name']
    folder = filename.split("/")[0]
    
    jobName = "CSV2BQ_"+filename.split(".")[0].split("/")[1]
    inputFilePattern="gs://[bucket]/"+event['name']
    URL='https://dataflow.googleapis.com/v1b3/projects/[project_name]/templates:launch?gcsPath=gs://dataflow-templates/latest/GCS_Text_to_BigQuery'
    data = {
     "jobName": jobName,
     "parameters": {
          "javascriptTextTransformFunctionName": "transform",
          "JSONPath": "gs://omex_etl_scripts/OmexLogs.json",
          "javascriptTextTransformGcsPath": "gs://etl_scripts/Logs.js",
          "inputFilePattern":inputFilePattern,
          "outputTable":"enduring-signal-279816:[Database].Logs",
          "bigQueryLoadingTemporaryDirectory": "gs://etl_scripts/temp"
      }     
     }

    project = "" # Project Name
    location = "us-central1"

    if folder == "workload" and filename.split(".")[1] == "csv":
     print("Yahan tak to aa gaye")
     #response = requests.post(url = URL, data = data)
     credentials = GoogleCredentials.get_application_default()

     dataflow = googleapiclient.discovery.build('dataflow', 'v1b3', credentials=credentials)
     result = dataflow.projects().templates().launch(
         projectId=project,
         body=data,
         gcsPath = "gs://dataflow-templates/latest/GCS_Text_to_BigQuery"
     ).execute()

     print(result)
     print("Did we do something in between?")
    else:
     print("Something else")
