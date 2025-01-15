from PyQt5.QtWidgets import (
    QWidget
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QColor, QPainter, QPen
import math


class LoadingSpinner(QWidget):
    def __init__(self, parent=None, centerOnParent=True, disableParentWhenSpinning=True):
        super().__init__(parent)
        
        self.centerOnParent = centerOnParent
        self.disableParentWhenSpinning = disableParentWhenSpinning
        
        # Remove window modality as we're using an overlay
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Adjusted parameters for better visibility
        self.angleOffset = 30
        self.timerId = -1
        self.angle = 0
        self.delay = 80  # Slower rotation
        self.displayedWhenStopped = False
        self.color = QColor("#2196F3")  # Bright blue color
        
        self.roundness = 100.0
        self.minimumTrailOpacity = 40  # Higher minimum opacity
        self.trailFadePercentage = 90  # Less fade for better visibility
        self.numberOfLines = 12
        self.lineLength = 25  # Even longer lines
        self.lineWidth = 6    # Even thicker lines
        self.innerRadius = 25 # Even larger radius
        
        self.isSpinning = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.updateSize()
        self.updateTimer()
        self.hide()
        
        # Force a minimum size
        self.setMinimumSize(QSize(100, 100))

    def paintEvent(self, QPaintEvent):
        self.updatePosition()
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.transparent)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        if self.isSpinning:
            for i in range(0, self.numberOfLines):
                painter.save()
                painter.translate(self.innerRadius + self.lineLength, self.innerRadius + self.lineLength)
                rotateAngle = float(360 * i) / float(self.numberOfLines)
                painter.rotate(rotateAngle + self.angle)
                painter.translate(self.innerRadius, 0)
                distance = self.lineCountDistanceFromPrimary(i, self.numberOfLines, self.trailFadePercentage, 
                                                           self.minimumTrailOpacity, self.angle)
                color = self.currentLineColor(distance, self.minimumTrailOpacity, self.color)
                painter.setPen(QPen(color, self.lineWidth, Qt.SolidLine))
                painter.drawLine(0, 0, self.lineLength, 0)
                painter.restore()

    def start(self):
        self.isSpinning = True
        self.show()
        
        if self.parentWidget and self.disableParentWhenSpinning:
            self.parentWidget().setEnabled(False)
            
        if not self.timer.isActive():
            self.timer.start()
            self.angle = 0

    def stop(self):
        self.isSpinning = False
        self.hide()
        
        if self.parentWidget() and self.disableParentWhenSpinning:
            self.parentWidget().setEnabled(True)
            
        if self.timer.isActive():
            self.timer.stop()

    def rotate(self):
        self.angle = (self.angle + self.angleOffset) % 360
        self.update()

    def updateSize(self):
        size = (self.innerRadius + self.lineLength) * 2
        self.setFixedSize(size, size)

    def updateTimer(self):
        self.timer.setInterval(self.delay)

    def updatePosition(self):
        if self.parentWidget() and self.centerOnParent:
            parentRect = self.parentWidget().rect()
            self.move(
                parentRect.center().x() - self.width() / 2,
                parentRect.center().y() - self.height() / 2
            )

    def lineCountDistanceFromPrimary(self, current, primary, fadePerc, minOpacity, angleCurrent):
        distance = (primary - current) % primary
        if distance > primary / 2:
            distance = primary - distance
        return math.pow(distance / (primary / 2), fadePerc) * (1 - minOpacity / 100) + minOpacity / 100

    def currentLineColor(self, countDistance, minOpacity, colorinput):
        color = QColor(colorinput)
        color.setAlpha(round(minOpacity + ((255 - minOpacity) * countDistance)))
        return color
