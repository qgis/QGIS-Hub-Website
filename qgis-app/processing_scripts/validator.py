import os
import ast
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

SCRIPT_MAX_SIZE = getattr(settings, "SCRIPT_MAX_SIZE", 1000000)  # 1MB

def processing_script_validator(processing_script_file) -> bool:
  """Processing Script File Validation"""
  try:
    # Check file size
    if processing_script_file.size > SCRIPT_MAX_SIZE:
      raise ValidationError(
        _("File is too big. Max size is %s Megabytes") % (SCRIPT_MAX_SIZE / 1000000)
      )
  except AttributeError:
    try:
      processing_script_file.seek(0, os.SEEK_END)
      file_size = processing_script_file.tell()
      processing_script_file.seek(0, os.SEEK_SET)
      if file_size > SCRIPT_MAX_SIZE:
        raise ValidationError(
          _("File is too big. Max size is %s Megabytes") % (SCRIPT_MAX_SIZE / 1000000)
        )
    except Exception:
      raise ValidationError(_("Cannot read this file."))

  # Read the file content
  try:
    processing_script_file.seek(0)  # Ensure the file pointer is at the start
    script_content = processing_script_file.read().decode("utf-8")
  except Exception as e:
    raise ValidationError(_("Cannot read the script content: %s") % str(e))

  # Check if the script has valid Python syntax
  if not _validate_syntax(script_content):
    raise ValidationError(_("Invalid Python syntax."))

  # Check if the script contains a class that inherits from QgsProcessingAlgorithm
  if not _validate_algorithm_class(script_content):
    raise ValidationError(_("Script must contain a class that inherits from QgsProcessingAlgorithm."))

  # Check if required methods are implemented
  required_methods = [
    "initAlgorithm",
    "processAlgorithm",
    "name",
    "displayName",
    "group",
    "groupId",
    "createInstance",
  ]
  missing_methods = []
  for method in required_methods:
    if not _validate_method_exists(script_content, method):
      missing_methods.append(method)

  if missing_methods:
    raise ValidationError(
      _("Script must implement the following methods: {}").format(", ".join(missing_methods))
    )

  # Check for malware using Bandit
  try:
    issues = _scan_for_malware(script_content)
    if issues:
      raise ValidationError(
        _(f"Script contains potential security issues:{', '.join(str(issue) for issue in issues)}")
      )
  except ImportError:
    pass  # Bandit is not installed, skip malware check

  return True

def _validate_syntax(script_content: str) -> bool:
  """
  Check if the script has valid Python syntax.
  """
  try:
    ast.parse(script_content)
    return True
  except SyntaxError:
    return False

def _validate_algorithm_class(script_content: str) -> bool:
  """
  Check if the script contains a class that inherits from QgsProcessingAlgorithm.
  """
  try:
    tree = ast.parse(script_content)
    for node in ast.walk(tree):
      if isinstance(node, ast.ClassDef):
        # Check if the class inherits from QgsProcessingAlgorithm
        for base in node.bases:
          if isinstance(base, ast.Name) and base.id == "QgsProcessingAlgorithm":
            return True
    return False
  except Exception:
    return False

def _validate_method_exists(script_content: str, method_name: str) -> bool:
  """
  Check if the specified method exists in the algorithm class.
  """
  try:
    tree = ast.parse(script_content)
    for node in ast.walk(tree):
      if isinstance(node, ast.ClassDef):
        for base in node.bases:
          if isinstance(base, ast.Name) and base.id == "QgsProcessingAlgorithm":
            # Check if the method exists in the class
            for item in node.body:
              if isinstance(item, ast.FunctionDef) and item.name == method_name:
                return True
    return False
  except Exception:
    return False

def _scan_for_malware(script_content: str):
  """
  Scan the script for potential security issues using Bandit.
  """
  import tempfile
  from bandit import config, manager
  try:

    # Create a temporary file to store the script content
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
      temp_file.write(script_content)
      temp_file_path = temp_file.name

    # Initialize Bandit configuration
    bandit_config = config.BanditConfig()
    bandit_manager = manager.BanditManager(bandit_config, "file")

    # Run Bandit on the temporary file
    bandit_manager.discover_files([temp_file_path], recursive=False)
    bandit_manager.run_tests()
    results = bandit_manager.get_issue_list()

    # Clean up the temporary file
    os.remove(temp_file_path)

    # Check if any security issues were found
    if results:
      return results
  except Exception as e:
    if "temp_file_path" in locals():
      os.remove(temp_file_path)  # Clean up the temporary file in case of an error
  return []