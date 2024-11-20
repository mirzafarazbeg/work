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
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def hello_pubsub(event, context):
  BQMaxId=""
  tDate = datetime.datetime.today().strftime('%Y%m%d')
  # tDate = '20220310'
  Query = ""#Call SP
  bq_client = bigquery.Client()
  query_job = bq_client.query(Query)
  rows_df = query_job.result()
  output_text = '<br>'
                    # <tr style="background:rgb(53,126,189);color:white"><th></th><th>766,093</th><th>438,929</th><th></th></tr>

  # print("Chk")
  # print(os.environ.get('SENDGRID_API_KEY')) 

  # for row in rows_df:
  #   print(str(row[0]))
  children = bq_client.list_jobs(parent_job=query_job.job_id)
  i = 1
  for child in children:
    grand_total_sent = 0
    grand_total_accepted = 0
    grand_total_rejected = 0
    grand_total_late = 0

    strTableTop = ''
    strTablebody = ''
    strGrandTotal = ''' </thead>
                        <tbody>'''
    strTableBottom = '''
                                    </tbody>
                                    </table>'''

    if i == 1:
      strTableTop = '''<table cellspacing="0" style="font-family:Arial,Helvetica,sans-serif;border:1px solid rgb(53,126,189);width:680px"><thead>
                        <tr>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">FIX Interface</th>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">Total Message Count</th></tr>'''
    elif i==2:
      strTableTop = '''<table cellspacing="0" style="font-family:Arial,Helvetica,sans-serif;border:1px solid rgb(53,126,189);width:680px"><thead>
                        <tr>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">FIX Interface</th>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">Total Sent</th>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">Total Rejected</th></tr>'''
    else:
      strTableTop = '''<table cellspacing="0" style="font-family:Arial,Helvetica,sans-serif;border:1px solid rgb(53,126,189);width:680px"><thead>
                        <tr>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">FIX Interface</th>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">Total Sent</th>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">Total Accepted</th>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">Total Rejected</th></tr>'''

    print("job {}".format(child.job_id))
    # strTablebody = output_text + '<br><br>' + strTableTop
    rows = child.result()
    for row in rows:
      strAppend = ''
      ecn_name = str(row[0])
      total_sent = row[1]
      total_accepted = 0
      total_late = 0
      total_rejected = 0
      symbols_rejected = ""

      if i== 3:
        total_accepted = row[2]
        total_rejected = row[3]
        total_late = row[5]
        symbols_rejected = row[4]
      elif i== 2:
        total_rejected = row[2]
      else:
        total_rejected = 0

      txtSent = "{:,}".format(total_sent)
      if total_late != 0:
        txtSent += " (" + "{:,}".format(total_late) + " late)"
      txtAccepted = "{:,}".format(total_accepted)
      if total_accepted == 0:
        txtAccepted = "N/A"
      txtRejected = "{:,}".format(total_rejected)
      if total_rejected != 0 and symbols_rejected != "":
        txtRejected += "(" + symbols_rejected + ")"
      

      grand_total_sent += total_sent
      grand_total_accepted += total_accepted
      grand_total_rejected += total_rejected
      grand_total_late += total_late


      if i == 3:
        strAppend = '<tr style="background-color:rgb(218,237,255);border-top:2px solid rgb(218,237,255)"><td>' + ecn_name + '</td><td>'  + txtSent + '</td><td>'  + txtAccepted + '</td><td>' + txtRejected + '</td></tr>'
      elif i == 2:
        strAppend = '<tr style="background-color:rgb(218,237,255);border-top:2px solid rgb(218,237,255)"><td>' + ecn_name + '</td><td>'  + txtSent + '</td><td>'  + txtRejected + '</td></tr>'
      else:
        strAppend = '<tr style="background-color:rgb(218,237,255);border-top:2px solid rgb(218,237,255)"  ><td>' + ecn_name + '</td><td>'  + txtSent + '</td></tr>'
      strTablebody = strTablebody + strAppend  
    # print(rows)

    if i == 3:
      strGrandTotal = '''                        <tr>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">&nbsp;</th>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">'''+ "{:,}".format(grand_total_sent) + '''</th>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">'''+ "{:,}".format(grand_total_accepted) + '''</th>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">&nbsp;</th></tr>'''+strGrandTotal
    elif i == 2:
      strGrandTotal = '''                        <tr>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">&nbsp;</th>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">'''+ "{:,}".format(grand_total_sent) + '''</th>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">'''+ "{:,}".format(grand_total_rejected) + '''</th></tr>'''+strGrandTotal
    else:
      strGrandTotal = '''<tr>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">&nbsp;</th>
                        <th style="background-color:rgb(53,126,189);color:white;text-align:left">''' + "{:,}".format(grand_total_sent) + '''</th></tr>'''+strGrandTotal                      
    i += 1


    output_text = output_text + '<br>' + strTableTop + strGrandTotal + strTablebody + strTableBottom
  # output_text = output_text + '<br>' + str(i)  


  message = Mail(
    from_email='mirzafarazbeg@gmail.com',
    to_emails='mirzafarazbeg@gmail.com',
    subject='[BQ] Hourly report for ' + tDate,
    html_content=output_text)

  sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
  response = sg.send(message)
  print(response.status_code)
  print(response.body)
  print(response.headers)

