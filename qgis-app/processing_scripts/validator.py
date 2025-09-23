import ast
import os

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
                _("File is too big. Max size is %s Megabytes")
                % (SCRIPT_MAX_SIZE / 1000000)
            )
    except AttributeError:
        try:
            processing_script_file.seek(0, os.SEEK_END)
            file_size = processing_script_file.tell()
            processing_script_file.seek(0, os.SEEK_SET)
            if file_size > SCRIPT_MAX_SIZE:
                raise ValidationError(
                    _("File is too big. Max size is %s Megabytes")
                    % (SCRIPT_MAX_SIZE / 1000000)
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

    # Check if the script is either a class-based or decorator-based algorithm
    is_class_based = _validate_algorithm_class(script_content)
    is_decorator_based = _validate_decorator_algorithm(script_content)

    if not is_class_based and not is_decorator_based:
        raise ValidationError(
            _(
                "Script must contain either a class that inherits from QgsProcessingAlgorithm or use the @alg decorator."
            )
        )

    # Validate based on the algorithm type
    if is_class_based:
        # Check if required methods are implemented for class-based algorithms
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
                _("Script must implement the following methods: {}").format(
                    ", ".join(missing_methods)
                )
            )

    elif is_decorator_based:
        # Validate decorator-based algorithm requirements
        if not _validate_decorator_requirements(script_content):
            raise ValidationError(
                _(
                    "Decorator-based script must have @alg decorator with required parameters and a main function."
                )
            )

    # Check for malware using Bandit
    try:
        issues = _scan_for_malware(script_content)
        if issues:
            raise ValidationError(
                _(
                    f"Script contains potential security issues:{', '.join(str(issue) for issue in issues)}"
                )
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
                    if (
                        isinstance(base, ast.Name)
                        and base.id == "QgsProcessingAlgorithm"
                    ):
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
                    if (
                        isinstance(base, ast.Name)
                        and base.id == "QgsProcessingAlgorithm"
                    ):
                        # Check if the method exists in the class
                        for item in node.body:
                            if (
                                isinstance(item, ast.FunctionDef)
                                and item.name == method_name
                            ):
                                return True
        return False
    except Exception:
        return False


def _validate_decorator_algorithm(script_content: str) -> bool:
    """
    Check if the script uses @alg decorator for processing algorithms.
    """
    try:
        tree = ast.parse(script_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if the function has @alg decorator
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == "alg":
                        return True
                    elif isinstance(decorator, ast.Call):
                        if (
                            isinstance(decorator.func, ast.Name)
                            and decorator.func.id == "alg"
                        ):
                            return True
                        elif (
                            isinstance(decorator.func, ast.Attribute)
                            and decorator.func.attr == "alg"
                        ):
                            return True
        return False
    except Exception:
        return False


def _validate_decorator_requirements(script_content: str) -> bool:
    """
    Validate that decorator-based algorithm has required components.
    """
    try:
        tree = ast.parse(script_content)

        # Check for required imports
        has_alg_import = False

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "qgis.processing" and any(
                    alias.name == "alg" for alias in node.names
                ):
                    has_alg_import = True
                elif node.module == "qgis" and any(
                    alias.name == "processing" for alias in node.names
                ):
                    pass
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "qgis.processing":
                        pass

        if not has_alg_import:
            return False

        # Find the main algorithm function with @alg decorator
        algorithm_function = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == "alg":
                        algorithm_function = node
                        break
                    elif isinstance(decorator, ast.Call):
                        if (
                            isinstance(decorator.func, ast.Name)
                            and decorator.func.id == "alg"
                        ):
                            algorithm_function = node
                            break

        if not algorithm_function:
            return False

        # Check if the function has required parameters (instance, parameters, context, feedback, inputs)
        required_params = ["instance", "parameters", "context", "feedback", "inputs"]
        if len(algorithm_function.args.args) < len(required_params):
            return False

        # Check parameter names (allowing for different naming conventions)
        param_names = [arg.arg for arg in algorithm_function.args.args]
        if len(param_names) < 5:
            return False

        return True

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
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as temp_file:
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
    except Exception:
        if "temp_file_path" in locals():
            os.remove(temp_file_path)  # Clean up the temporary file in case of an error
    return []
