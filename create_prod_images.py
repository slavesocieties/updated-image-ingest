from serialize_images import list_folders, list_object_keys
import os
import boto3
import json

def move_and_rename_s3_object(source_key, target_key, source_bucket='ssda-file-upload', target_bucket='ssda-production-jpgs', delete=False):
    """
    Move and rename an object from one S3 bucket to another.

    Args:
    source_bucket (str): The name of the source bucket.
    source_key (str): The key of the object in the source bucket.
    target_bucket (str): The name of the target bucket.
    target_key (str): The new key for the object in the target bucket.
    """
    # Create a resource service client
    s3 = boto3.resource('s3')

    # Copy the source object to the target location with the new key
    copy_source = {
        'Bucket': source_bucket,
        'Key': source_key
    }
    s3.meta.client.copy(copy_source, target_bucket, target_key)

    # Optionally, delete the original object if the copy was successful
    if delete:
        s3.Object(source_bucket, source_key).delete()

def create_prod_images(project_prefix, source_bucket='ssda-file-upload', target_bucket='ssda-production-jpgs', metadata_folder='thumbnails'):
    folders = list_folders(source_bucket, prefix=str(project_prefix) + '/')
    id_map = []

    for f, sf, files in os.walk(metadata_folder):
        for file in files:
            with open(os.path.join(f, file), 'r', encoding='utf-8') as g:
                data = json.load(g)
            id_map.append({'title': data['volumeTitle'], 'id': int(data['volumeID'])})    

    for folder in folders:
        vol_title = 'La Aurora ' + folder[folder.find('/') + 1:folder.find('/', folder.find('/') + 1)]
        vol_id = None
        print(f'Now working on {vol_title}')
        images = list_object_keys(source_bucket, prefix=folder)
        for vol in id_map:
            if vol['title'] == vol_title:
                vol_id = vol['id']
                break        
        image_id = 1
        for image in images:
            padding = '0' * (4 - len(str(image_id)))
            image_file_name = f"{vol_id}-{padding}{image_id}.jpg"            
            move_and_rename_s3_object(image, image_file_name, source_bucket='ssda-file-upload', target_bucket='ssda-production-jpgs')
            image_id += 1
        print(f'{image_id - 1} images moved from {source_bucket} to {target_bucket}.')

# create_prod_images(770)