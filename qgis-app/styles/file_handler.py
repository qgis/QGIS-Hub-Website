"""
Validator for Style XML file.
"""
import xml.etree.ElementTree as ET

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import chardet


def _check_name_type_attribute(element):
    """
    Check if element has name and type attribute.
    """
    style_name = element.get("name")
    if not style_name:
        raise ValidationError(
            _("Undefined style name. " "Please register your style type.")
        )
    if element.tag == "symbol":
        style_type = element.get("type")
        if not style_type:
            raise ValidationError(
                _("Undefined style type. " "Please register your style type.")
            )


def validator(xmlfile):
    """
    Validate a style file for a Form.

    The file should be a valid XML file.
    The file should contains:
    - qgis_style tag in root.
    - attribute name and type in symbol tag.

    This validation will pass a style file with style types:
    - Symbol : Fill
    - Symbol : Line
    - Symbol : Marker
    - Color Ramp
    - Label Setting
    - Legend Patch
    - Text Format
    - 3D Symbol
    """

    try:
        tree = ET.parse(xmlfile)
    except ET.ParseError:
        raise ValidationError(
            _("Cannot parse the style file. " "Please ensure your file is correct.")
        )
    root = tree.getroot()
    if not root or not root.tag == "qgis_style":
        raise ValidationError(
            _("Invalid root tag of style file. " "Please ensure your file is correct.")
        )
    # find child elements
    symbol = root.find("./symbols/symbol")
    colorramp = root.find("./colorramps/colorramp")
    labelsetting = root.find("./labelsettings/labelsetting")
    legendpatchshape = root.find("./legendpatchshapes/legendpatchshape")
    symbol3d = root.find("./symbols3d/symbol3d")
    textformat = root.find("./textformats/textformat")
    if (
        not symbol
        and not colorramp
        and not labelsetting
        and not legendpatchshape
        and not symbol3d
        and not textformat
    ):
        raise ValidationError(
            _("Undefined style type. " "Please register your style type.")
        )
    if symbol:
        _check_name_type_attribute(symbol)
    elif colorramp:
        _check_name_type_attribute(colorramp)
    elif labelsetting:
        _check_name_type_attribute(labelsetting)
    elif legendpatchshape:
        _check_name_type_attribute(legendpatchshape)
    elif symbol3d:
        _check_name_type_attribute(symbol3d)
    elif textformat:
        _check_name_type_attribute(textformat)
    xmlfile.seek(0)
    return True


def detect_encoding(file):
    raw_data = file.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    file.seek(0)
    return encoding

# Validator for GPL file
def gpl_validator(gplfile):
    """
    Validate a GPL file.

    The file should be a valid GPL file.
    The file should contain:
    - Header with "GIMP Palette"
    - Name and Columns information
    - RGB values and color name
    """
    encoding = detect_encoding(gplfile)
    try:
        lines = gplfile.readlines()
    except Exception:
        raise ValidationError(_("Cannot read the GPL file. Please ensure your file is correct."))

    if len(lines) == 0:
        raise ValidationError(_("Empty file. Please ensure your file is correct."))
    if not lines[0].strip().decode(encoding) == "GIMP Palette":
        raise ValidationError(_("Invalid GPL file header. Please ensure your file is correct."))

    if not lines[1].strip().decode(encoding).startswith("Name:"):
        raise ValidationError(_("Missing 'Name' in GPL file. Please ensure your file is correct."))

    for line in lines[4:]:
        if line.strip().decode(encoding) and not line.strip().decode(encoding).startswith("#"):
            parts = line.decode(encoding).split()
            if len(parts) < 4:
                raise ValidationError(_("Invalid color definition in GPL file. Please ensure your file is correct."))
            try:
                r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
                if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
                    raise ValidationError(_("RGB values must be between 0 and 255."))
            except ValueError:
                raise ValidationError(_("RGB values must be integers."))
    gplfile.seek(0)
    return True

# Get the name from the GPL file
def get_gpl_name(gplfile):
    """
    Get the name of the GPL file.

    The file should be a valid GPL file.
    The file should contain:
    - Header with "GIMP Palette"
    - Name and Columns information
    - RGB values and color name
    """
    encoding = detect_encoding(gplfile)
    try:
        lines = gplfile.readlines()
    except Exception:
        raise ValidationError(_("Cannot read the GPL file. Please ensure your file is correct."))
    if not lines[0].strip().decode(encoding) == "GIMP Palette":
        raise ValidationError(_("Invalid GPL file header. Please ensure your file is correct."))

    if not lines[1].strip().decode(encoding).startswith("Name:"):
        raise ValidationError(_("Missing 'Name' in GPL file. Please ensure your file is correct."))

    name = lines[1].decode(encoding).split(":")[1].strip()
    gplfile.seek(0)
    return name

def read_xml_style(xmlfile):
    """
    Parse XML file.

    The file should contains:
    - qgis_style tag in root
    - One of these following elements tag:
      - symbol
      - colorramp
      - labelsetting
      - legendpatchshape
      - symbol3d
    """

    try:
        tree = ET.parse(xmlfile)
    except ET.ParseError:
        raise ValidationError(
            _("Cannot parse the style file. " "Please ensure your file is correct.")
        )
    root = tree.getroot()
    # find child elements
    symbol = root.find("./symbols/symbol")
    colorramp = root.find("./colorramps/colorramp")
    labelsetting = root.find("./labelsettings/labelsetting")
    legendpatchshape = root.find("./legendpatchshapes/legendpatchshape")
    symbol3d = root.find("./symbols3d/symbol3d")
    textformat = root.find("./textformats/textformat")

    if symbol:
        return {"name": symbol.get("name"), "type": symbol.get("type")}
    elif colorramp:
        return {"name": colorramp.get("name"), "type": "colorramp"}
    elif labelsetting:
        return {"name": labelsetting.get("name"), "type": "labelsetting"}
    elif legendpatchshape:
        return {"name": legendpatchshape.get("name"), "type": "legendpatchshape"}
    elif symbol3d:
        return {"name": symbol3d.get("name"), "type": "symbol3d"}
    elif textformat:
        return {"name": textformat.get("name"), "type": "textformat"}
    else:
        return {"name": None, "type": None}
