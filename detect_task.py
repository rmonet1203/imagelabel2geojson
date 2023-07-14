import os, datetime
from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt, QThread, pyqtSignal, pyqtSlot
from qgis.PyQt.QtWidgets import QAction, QToolBar, QApplication, QMessageBox, QLabel, QFileDialog, QProgressBar
from qgis.gui import *
from qgis.core import *
from qgis.PyQt.QtGui import QPixmap, QPainter, QPen, QColor, QIcon, QImage, QBrush, QFont
from qgis.core import QgsVectorLayer, QgsCoordinateReferenceSystem, QgsVectorFileWriter
from io import BytesIO
# import numpy as np
# from sklearn.linear_model import LinearRegression
from PIL import Image, ImageDraw
from google.cloud import vision
apikey_path = os.path.join(os.path.dirname(__file__), 'apikey.json')
client = vision.ImageAnnotatorClient.from_service_account_json(apikey_path)


class Detect_task(QgsTask):
    taskCompleted = pyqtSignal(object)  # Signal that carries the result
    def __init__(self, description, layer, gray, affine, iface):
       super().__init__(description, QgsTask.CanCancel)
       self.layer = layer
       self.iface = iface
       self.total = 0
       self.iterations = 0
       self.exception = None
       self.affine = affine
       self.precoordinates = ""
       self.gray = gray
       self.img_index = 0
       
    
    def run(self):
        QgsMessageLog.logMessage('Started task "{}"'.format(self.description()))
        
        data_text = self.convert_image()
        
        # if self.isCanceled():
        #         return False
         # Emit the taskCompleted signal with the result
        
        self.taskCompleted.emit(data_text)
        return True
    
    def cancel(self):
        QgsMessageLog.logMessage('cancel')
        super().cancel()
        
    def detect_text(self, image):
        global client
        text = ""
        """Detects text in the file."""
        self.img_index +=1
        
        if image is None or image.size == 0:        
            return text
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        content = buffer.getvalue()        
        image = vision.Image(content=content)    

        response = client.text_detection(image=image)
        texts = response.text_annotations
        for item in texts:
            if hasattr(item, "description"):
                text = str(getattr(item, "description"))
                break

        if response.error.message:
            text = "Network error"
        return text
    
    def convert_image(self):
        
        self.total = self.layer.featureCount()
        labeling = QgsVectorLayerSimpleLabeling(QgsPalLayerSettings())
        self.layer.setLabeling(labeling)
        self.layer.setLabelsEnabled(True)

        text_format = QgsTextFormat()
        text_format.setSize(10)
        text_format.setColor(QColor('black'))
        text_format.setFont(QFont('Arial', 8))

        settings = QgsPalLayerSettings()

        settings.fieldName = 'Name'
        settings.placement = QgsPalLayerSettings.OverPoint
        settings.enabled = True
        settings.setFormat(text_format)

        #layer.setInLabelsEnabled(True)
        self.layer.setLabeling(QgsVectorLayerSimpleLabeling(settings))
        # Enable labeling for all features in the layer
        self.layer.setLabelsEnabled(True)

        # Update all features at once
        # self.layer.startEditing()
        self.pretext = ""
        id = 0
        result = []
        for feature in self.layer.getFeatures():
            if self.isCanceled():
                return False
            
            # Get the geometry of the feature (block)
            geometry = feature.geometry()
            # Check if the geometry is valid
            if geometry.isNull():
                continue
            
            id +=1
            
            # Retrieve the coordinates of the polygon
            coordinates = geometry.asPolygon()[0]

            text_recogination =""
            if coordinates == self.precoordinates:
                text_recogination = self.pretext
               
            else:        
                self.precoordinates = coordinates
                
                coor = self.affine.xy2gps(coordinates)
                polygons = []  
                
                for point in coor:
                    new_polygon = (int(point[0]), int(point[1]))
                    polygons.append(new_polygon)

                # Create a mask image with the same size as the original image
                mask = Image.new('L', self.gray.size, 0)

                # Create a draw object for the mask
                draw = ImageDraw.Draw(mask)

                # Draw the polygon on the mask
                draw.polygon(polygons, fill=255)

                # Apply the mask to the image
                cropped_image = Image.new('RGBA', self.gray.size)
                cropped_image.paste(self.gray, mask=mask)
                # Calculate the bounding box of the polygon
                x_coords, y_coords = zip(*polygons)
                min_x, min_y = min(x_coords), min(y_coords)
                max_x, max_y = max(x_coords), max(y_coords)
                width = max_x - min_x
                height = max_y - min_y
                new_image = cropped_image.crop((min_x, min_y, max_x, max_y))
                # new_image.save(f'f:/image/image_{min_x}_{min_y}_{max_x}_{max_y}.png')
                
                text_recogination = self.detect_text(new_image)               
                self.pretext = text_recogination

            result.append(text_recogination)
            self.setProgress(self.progress() + 100 /self.total)            
        
        return result
