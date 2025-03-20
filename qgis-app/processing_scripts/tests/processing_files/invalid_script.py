from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterRasterLayer, QgsProcessingOutputRasterLayer

class InvalidAlgorithm:  # Does not inherit from QgsProcessingAlgorithm
  def initAlgorithm(self, config=None):
    self.addParameter(QgsProcessingParameterRasterLayer("input", "Input Raster"))
    self.addOutput(QgsProcessingOutputRasterLayer("output", "Output Raster"))

  # Missing processAlgorithm method
  # def processAlgorithm(self, parameters, context, feedback):
  #   input_raster = self.parameterAsRasterLayer(parameters, "input", context)
  #   output_raster = "output.tif"  # Replace with actual processing logic
  #   return {"output": output_raster}

  def name(self):
    return "invalid_algorithm"

  def displayName(self):
    return "Invalid Algorithm"

  def group(self):
    return "Invalid Scripts"

  def groupId(self):
    return "invalidscripts"

  def createInstance(self):
    return InvalidAlgorithm()