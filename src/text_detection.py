# text_detection.py

from google.cloud import vision
import pandas as pd

# text_detection.py

from google.cloud import vision
import pandas as pd
import os 

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "GCP_keys3.json"

class TextDetector:
    def __init__(self):
        """
        Initializes the Google Cloud Vision client. 
        The environment variable GOOGLE_APPLICATION_CREDENTIALS should be set.
        """
        self.client = vision.ImageAnnotatorClient()

    # ... rest of your class methods ...

    def analyze_image_for_text(self, image_data):
        """
        Analyzes the given image for text.
        :param image_data: Image data in bytes.
        :return: Detected text in the image.
        """
        image = vision.Image(content=image_data)
        response = self.client.text_detection(image=image)
        texts = response.text_annotations

        return texts



