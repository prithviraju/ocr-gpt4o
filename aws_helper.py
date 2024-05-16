
import boto3
import io
import os
from PIL import Image, ImageDraw
import base64

aws_access_key_id = os.environ.get('aws_access_key_id', 'default_key')
aws_secret_access_key = os.environ.get('aws_secret_access_key', 'default_access_key')
REGION = 'us-east-1'
# session = boto3.Session(profile_name='profile-name')
# s3_connection = session.resource('s3')
print(aws_access_key_id)
print(aws_secret_access_key)
# client = boto3.client('textract', aws_access_key_id=aws_access_key_id , aws_secret_access_key=aws_secret_access_key, region_name=REGION)
session = boto3.session.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
client = session.client('textract', region_name=REGION)
# bucket = 'bucket'
# document = 'document'

# Takes a field as an argument and prints out the detected labels and values
def get_labels_and_values(field):
    result = []
    # Only if labels are detected and returned
    if "LabelDetection" in field:
        result.append("Summary Label Detection - Confidence: {}".format(
            str(field.get("LabelDetection")["Confidence"])) + ", "
              + "Summary Values: {}".format(str(field.get("LabelDetection")["Text"])))
        result.append(field.get("LabelDetection")["Geometry"])
    else:
        result.append("Label Detection - No labels returned.")
    if "ValueDetection" in field:
        result.append("Summary Value Detection - Confidence: {}".format(
            str(field.get("ValueDetection")["Confidence"])) + ", "
              + "Summary Values: {}".format(str(field.get("ValueDetection")["Text"])))
        result.append(field.get("ValueDetection")["Geometry"])
    else:
        result.append("Value Detection - No values returned")
    
    return result

def process_expense_analysis(s3_connection, client, image_base64, bucket = '', document = ''):
    result = []
    # Get the document from S3
    # s3_object = s3_connection.Object(bucket, document)
    # s3_response = s3_object.get()

    # opening binary stream using an in-memory bytes buffer
    # stream = io.BytesIO(s3_response['Body'].read())

    # loading stream into image
    # image = Image.open(stream)

    # Analyze document
    # process using S3 object
    response = client.analyze_expense(
        # Document={'S3Object': {'Bucket': bucket, 'Name': document}})
        Document={'Bytes': image_base64})

    print(response)

    for expense_doc in response["ExpenseDocuments"]:
        for line_item_group in expense_doc["LineItemGroups"]:
            for line_items in line_item_group["LineItems"]:
                for expense_fields in line_items["LineItemExpenseFields"]:
                    get_labels_and_values(expense_fields)

        for summary_field in expense_doc["SummaryFields"]:
            get_labels_and_values(summary_field)

        #For draw bounding boxes
        for line_item_group in expense_doc["LineItemGroups"]:
            for line_items in line_item_group["LineItems"]:
                for expense_fields in line_items["LineItemExpenseFields"]:
                    for key, val in expense_fields["ValueDetection"].items():
                        if "Geometry" in key:
                            # draw_bounding_box(key, val, width, height, draw)

        for label in expense_doc["SummaryFields"]:
            if "LabelDetection" in label:
                for key, val in label["LabelDetection"].items():
                    # draw_bounding_box(key, val, width, height, draw)

    return result

def analyze_image(image_base64: str):
    result = process_expense_analysis(None, client, image_base64)
    return result
    # with open("/home/prakhar.m/Downloads/Enterprise Restaurant Bill.jpg", "rb") as image_file:
    #     encoded_string = base64.b64encode(image_file.read())
    #     result = process_expense_analysis(None, client, encoded_string)
    #     print(result)
        

                  