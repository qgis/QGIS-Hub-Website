"""
Validator for Map Image file
"""
from PIL import Image
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import xml.etree.ElementTree as ET

# Check if the image is valid
def is_valid_image(image_filename):
  """
  Check if the image file is valid.
  param image_filename: The image file to check
  """
  try:
    print("Checking image file...", image_filename)
    img = Image.open(image_filename)
    img.verify()
  except Exception as e:
    raise ValidationError(
      _("Invalid image file. Please ensure your file is correct.")
    )


def is_valid_svg(svg_filename):
    """
    Check if the svg file is valid.
    param svg_filename: The svg file to check
    return: True if the svg is valid, False otherwise
    """
    try:
        ET.parse(svg_filename)  # Try to parse the XML
        return True  # No error means it's valid
    except ET.ParseError:
        return False  # If parsing fails, it's invalid