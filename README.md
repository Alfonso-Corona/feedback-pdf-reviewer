# Feedback PDF Reviewer

This project is a simple web form that allows users to submit feedback along with an optional PDF file. The form sends the submitted data to a backend API endpoint and shows a confirmation message to the user.

## Project Purpose

The main goal of this application is to collect user feedback and optionally attach a PDF document for review. It is designed as a lightweight front-end demo that can be opened directly in a browser.

## Files

### index.html

This is the main application file.

It contains:
- The feedback form UI
- Input fields for name, email, message, and an optional PDF upload
- Styling for the layout and modal dialog
- JavaScript logic to submit the form data to the API
- A success/error modal shown after submission

The form sends a POST request to the configured API endpoint defined in the script section.

### README.md

This file documents the project, its purpose, and the files included in the repository.

### lambda.py

This file contains the AWS Lambda handler that processes feedback submissions received from the web form.

It performs the following actions:
- Receives the incoming event payload from API Gateway
- Handles preflight OPTIONS requests for CORS support
- Parses the submitted form data from the request body
- Stores the submission in DynamoDB
- Uploads an attached PDF to S3 when a file is provided
- Sends an email notification through Amazon SES to the configured administrator address
- Returns a JSON response to the client

The Lambda function uses environment variables such as:
- TABLE_NAME for the DynamoDB table
- BUCKET_NAME for the S3 bucket
- ADMIN_EMAIL for the recipient of notification emails
- REGION for the AWS region

## How It Works

1. The user fills in the form fields.
2. The user may optionally choose a PDF file.
3. When the form is submitted, the browser reads the selected file as Base64 data.
4. The data is sent to the feedback API endpoint as JSON.
5. A modal is displayed with the server response or an error message.

## Usage

Open index.html in a browser to use the form.

If you want to connect this project to a different backend, update the API URL in the script section of index.html.

## Notes

- The project currently contains a front-end only implementation.
- The form depends on an active API endpoint for successful submissions.
- The uploaded file is optional.
