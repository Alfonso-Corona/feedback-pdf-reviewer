import json
import boto3
import base64
import os
from datetime import datetime
import uuid

TABLE_NAME = os.environ.get('TABLE_NAME', 'feedback-pdf-kaori')
BUCKET_NAME = os.environ.get('BUCKET_NAME', 'feedback-pdf-kaori')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@gmail.com')
REGION = os.environ.get('REGION', 'us-east-1')

dynamodb = boto3.resource('dynamodb', region_name=REGION)
s3 = boto3.client('s3', region_name=REGION)
ses = boto3.client('ses', region_name=REGION)

def lambda_handler(event, context):
    print('Event received: ', json.dumps(event))
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
        }
    
    try: 
        if 'body' in event:
            body = json.loads(event['body'])
        elif 'name' in event and 'email' in event:
            body = event
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'Invalid request format'})
            }

        feedback_id = str(uuid.uuid4())
        name = body.get('name', '')
        email = body.get('email', '')
        message = body.get('message', '')
        file_base64 = body.get('file_base64', '')

        file_url = None
        if file_base64:
            key = f"{feedback_id}.pdf"
            pdf_data = base64.b64decode(file_base64.split(',')[-1])
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=key,
                Body=pdf_data,
                ContentType='application/pdf'
            )

            file_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': key},
                ExpiresIn=86400
            )

        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item={
            'feedback_id': feedback_id,
            'name': name,
            'email': email,
            'message': message,
            'file_url': file_url,
            'timestamp': datetime.utcnow().isoformat()
        })

        response = ses.send_email(
            Source=ADMIN_EMAIL,  # Sender email address
            Destination={'ToAddresses': [ADMIN_EMAIL]},  # Recipient email address
            Message={
                'Subject': {'Data': 'New Feedback Received'},  # Subject of the email
                'Body': {
                    'Html': {
                        'Data': f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                          <style>
                            body {{
                              font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                              background-color: #f1f5f9;
                              padding: 40px 0;
                            }}
                            .container {{
                              max-width: 600px;
                              margin: auto;
                              background-color: #ffffff;
                              border-radius: 10px;
                              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                              padding: 30px;
                            }}
                            h2 {{
                              color: #1d4ed8;
                              border-bottom: 2px solid #e2e8f0;
                              padding-bottom: 10px;
                              margin-bottom: 20px;
                            }}
                            table {{
                              width: 100%;
                              border-collapse: collapse;
                              margin-bottom: 20px;
                            }}
                            td {{
                              padding: 12px 10px;
                              vertical-align: top;
                              border-bottom: 1px solid #e2e8f0;
                            }}
                            td.label {{
                              font-weight: bold;
                              background-color: #f8fafc;
                              width: 30%;
                              color: #475569;
                            }}
                            .message {{
                              white-space: pre-wrap;
                            }}
                            .image-link {{
                              margin-top: 20px;
                              display: block;
                              color: #2563eb;
                              font-weight: bold;
                              text-decoration: none;
                            }}
                            .image-link:hover {{
                              text-decoration: underline;
                            }}
                            .footer {{
                              margin-top: 30px;
                              font-size: 12px;
                              color: #94a3b8;
                              text-align: center;
                            }}
                          </style>
                        </head>
                        <body>
                          <div class="container">
                            <h2>📩 New Feedback Received</h2>
                            <table>
                              <tr>
                                <td class="label">Name</td>
                                <td>{name}</td>
                              </tr>
                              <tr>
                                <td class="label">Email</td>
                                <td>{email}</td>
                              </tr>
                              <tr>
                                <td class="label">Message</td>
                                <td class="message">{message.replace('\n', '<br>')}</td>
                              </tr>
                              {f'''
                                <tr>
                                  <td class="label">Attachment</td>
                                  <td><a href="{file_url}" target="_blank" class="image-link">📎 View PDF Attachment</a></td>
                                </tr>
                                ''' if file_url else ''}

                            </table>
                            <div class="footer">
                              This email was automatically sent from your feedback form.
                            </div>
                          </div>
                        </body>
                        </html>
                        """
                    }
                }
            }
        )

        print(f"SES Email sent. Message ID: {response['MessageId']}")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'message': 'Feedback submitted successfully!'})
        }
    
    except Exception as e:
        print(f"Error ocurred: ", str(e))
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Headers': '*',
            },
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }