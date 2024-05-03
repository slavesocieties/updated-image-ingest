import boto3
from PIL import Image
import io
import base64
import json

def list_folders(bucket_name, prefix=''):
    # Initialize a boto3 client
    s3_client = boto3.client('s3')

    # Use the list_objects_v2 API to list objects with a specific prefix and delimiter
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')

    # Extract the 'CommonPrefixes' from the response to get the folder-like prefixes
    folders = [cp['Prefix'] for cp in response.get('CommonPrefixes', [])]

    return folders

def list_object_keys(bucket_name, prefix=''):
    # Initialize a boto3 client
    s3_client = boto3.client('s3')

    # Initialize a list to hold all the object keys
    object_keys = []

    # Initialize the paginator
    paginator = s3_client.get_paginator('list_objects_v2')

    # Create a page iterator from the paginator
    page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

    # Loop through each page of results
    for page in page_iterator:
        # Check if 'Contents' is in the page (it might not be if the page is empty)
        if 'Contents' in page:
            # Extend the list of object keys with the keys found in this page
            object_keys.extend([item['Key'] for item in page['Contents']])

    return object_keys

def download_and_resize_image(bucket_name, key, output_size):
    # Initialize a boto3 client
    s3_client = boto3.client('s3')
    
    # Download the image data from S3
    response = s3_client.get_object(Bucket=bucket_name, Key=key)
    image_data = response['Body'].read()

    # Calculate the size of the original image data in bytes
    original_size_bytes = len(image_data)

    # Create a PIL Image from the binary data
    image = Image.open(io.BytesIO(image_data))

    # Resize the image
    resized_image = image.resize(output_size)    

    return resized_image, original_size_bytes

def image_to_base64(image, format='JPEG'):
    # Convert the PIL Image to bytes
    buffered = io.BytesIO()
    image.save(buffered, format=format)

    # Encode this bytes to base64 string
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return img_str

def ingest_images(bucket_name, project_prefix, first_vol=1):
    folders = list_folders(bucket_name, prefix=str(project_prefix) + '/')
    vol_id = str(project_prefix) + ('0' * (3 - len(str(first_vol)))) + str(first_vol)    
    covers = []
    total_images = 0    

    for folder in folders:
        vol_title = folder[folder.find('/') + 1:folder.find('/', folder.find('/') + 1)]
        print(f'Now working on {vol_title}')        
        images = list_object_keys(bucket_name, prefix=folder)
        images.sort()
        thumbnails = {"volumeID": vol_id, "volumeTitle": vol_title, "thumbnailCount": 0, "serializedThumbnails": []}
        image_id = 1
        for image in images:            
            padding = '0' * (4 - len(str(image_id)))
            image_file_name = f"{vol_id}-{padding}{image_id}.jpg"
            if image_id == 1:
                cover_image, size = download_and_resize_image(bucket_name, image, (265, 400))
                cover_image_string = image_to_base64(cover_image, format='JPEG')
                covers.append({'ContainerName': 'ssda-production-jpgs', 'BlobName': image_file_name, 'Blobpath': image_file_name, 'BlobSize': size, 'ThumbnailArray': cover_image_string})
            thumbnail, size = download_and_resize_image(bucket_name, image, (90, 120))
            thumbnail_string = image_to_base64(thumbnail, format='JPEG')
            thumbnails['serializedThumbnails'].append({'ContainerName': 'ssda-production-jpgs', 'BlobName': image_file_name, 'Blobpath': image_file_name, 'BlobSize': size, 'ThumbnailArray': thumbnail_string})
            thumbnails['thumbnailCount'] += 1
            image_id += 1
            total_images += 1

        with open(f'thumbnails/{vol_id}-thumbnails.json', 'w', encoding='utf-8') as f:
            json.dump(thumbnails, f)

        vol_id = str(int(vol_id) + 1)

    with open('master-covers.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for cover in covers:
        data['serializedCovers'].append(cover)
        data['coverCount'] += 1

    with open('master-covers.json', 'w', encoding='utf-8') as f:
        json.dump(data, f)

    print(f'{total_images} images from {len(folders)} volumes serialized.')

# ingest_images('ssda-file-upload', 770)