import base64
from PIL import Image
from io import BytesIO
import json

with open('master-covers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# This is your base64 string
base64_string = data['serializedCovers'][1]['ThumbnailArray']

# Decode the base64 string to bytes
image_data = base64.b64decode(base64_string)

# Convert bytes data to an image
image = Image.open(BytesIO(image_data))

# Display the image (if you are using a Jupyter notebook or similar environment)
image.show()

# Optionally, save the image to a file
image.save('cover_1.png')