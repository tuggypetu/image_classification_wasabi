import os
import boto3
import numpy as np
import tensorflow as tf
from datetime import datetime
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()


ACCESS_KEY = os.getenv('WASABI_ACCESS_KEY')
SECRET_KEY = os.getenv('WASABI_SECRET_KEY')
WASABI_ENDPOINT = 'https://s3.wasabisys.com'
BUCKET_NAME = os.getenv('WASABI_BUCKET_NAME')

new_model = tf.keras.models.load_model('gallary_classification.h5')
class_names = ['Cars', 'Memes', 'Mountains', 'Selfies', 'Trees', 'Whatsapp_Screenshots']


s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    endpoint_url=WASABI_ENDPOINT
)

def preprocess_image(image_path):
    img = tf.keras.preprocessing.image.load_img(image_path, target_size=(256, 256))
    img = tf.keras.preprocessing.image.img_to_array(img)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    return img

def classify_image(file_path):
    img = preprocess_image(file_path)
    predictions = new_model.predict(img)
    predicted_class_index = np.argmax(predictions, axis=1)
    return class_names[predicted_class_index[0]]

def upload_to_wasabi(file_name, file_path, predicted_label):
    try:
        if not isinstance(predicted_label, str):
            predicted_label = str(predicted_label)

        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        s3_client.upload_file(
            file_path, BUCKET_NAME, file_name,
            ExtraArgs={
                "Metadata": {
                    "Predicted-Label": predicted_label,
                    "Upload-Date": current_date
                }
            }
        )
        print(f"File {file_name} uploaded successfully with metadata.")
        return f"{WASABI_ENDPOINT}/{BUCKET_NAME}/{file_name}"
    except NoCredentialsError:
        print("Credentials not available.")
        return None
    except s3_client.exceptions.NoSuchBucket:
        print(f"Bucket {BUCKET_NAME} does not exist.")
        return None

def download_from_wasabi(file_name, download_path):
    try:
        s3_client.download_file(BUCKET_NAME, file_name, download_path)
        print(f"File {file_name} downloaded to {download_path}.")
    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"An error occurred while downloading: {str(e)}")

def retrieve_metadata(file_name):
    try:
        response = s3_client.head_object(Bucket=BUCKET_NAME, Key=file_name)
        metadata = response['Metadata']
        print(f"Metadata for {file_name}:")
        for key, value in metadata.items():
            print(f"  {key}: {value}")
    except NoCredentialsError:
        print("Credentials not available.")
    except Exception as e:
        print(f"An error occurred while retrieving metadata: {str(e)}")


test_image_path = 'image_store/car.jpg'


predicted_class = classify_image(test_image_path)
print(f"Image classified as: {predicted_class}")


file_name = os.path.basename(test_image_path)
wasabi_url = upload_to_wasabi(file_name, test_image_path, predicted_class)

if wasabi_url:
    print(f"Image uploaded to: {wasabi_url}")

    
    retrieve_metadata(file_name)

    
    download_path = './Downloaded_' + file_name  
    download_from_wasabi(file_name, download_path)
