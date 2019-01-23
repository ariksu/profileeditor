import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QDialogButtonBox
from PyQt5 import uic
from colorpicker import Ui_SelectColor

import resources_rc


class ColorDialog(QtWidgets.QDialog, Ui_SelectColor):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.palitra = QtGui.QPixmap(":/palette/palette.png")
        self.LblColor.show()
        self.TxtColor.setAutoFillBackground(True)
        self.ColorSlider.valueChanged.connect(self.valuechange)
        self.BrightnessSlider.valueChanged.connect(self.valuechange)
        self.SuturationSlider.valueChanged.connect(self.valuechange)
        self.image = self.palitra.toImage()
        self.SuturationSlider.valueChanged['int'].connect(self.changeBrightnessLabel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.rgb = [255, 0, 0]

    def Color(self):
        return self.LblColor.text(), self.rgb

    def setcolor(self, color: str):
        self.LblColor.setText(color)
        self.mColor = color.split(",")
        self.mColor = [float(x) for x in self.mColor]

        # get max value and divide at 255 to get brightness
        s_color = (max(float(self.mColor[0]),max(self.mColor[1], self.mColor[2]))/255.0)*100.0
        self.SuturationSlider.setValue(round(s_color))
        self.mColor = [(x * 100)/s_color for x in self.mColor]

        # get min value for saturation
        b_color = min(self.mColor[0], min(self.mColor[1], self.mColor[2]))
        self.BrightnessSlider.setValue(round(b_color))

        # get max value index
        max_ind = self.mColor.index(max(self.mColor))
        # other decrease by saturation
        self.mColor = [x - b_color if i != max_ind else x for (i, x) in enumerate(self.mColor)]

        # get color
        if (round(self.mColor[1]) == 255):
            h_color = 510 - self.mColor[0] + self.mColor[2]
        elif (round(self.mColor[2]) == 255):
            h_color = 1020 + self.mColor[0] - self.mColor[1]
        else:
            h_color = (1530 + self.mColor[1] - self.mColor[2])% 1530
        self.ColorSlider.setValue(h_color)

    def valuechange(self):
        hValue = self.ColorSlider.value()
        bValue = self.BrightnessSlider.value()
        sValue = self.SuturationSlider.value()
        Color = [0, 0, 0]
        # print(hValue)
        if hValue < 255:
            Color[0] = 255
            Color[1] = hValue
        if 254  < hValue < 510:
            Color[0] = 255 - (hValue % 255)
            Color[1] = 255
        if 509 < hValue < 765:
            Color[1] = 255
            Color[2] = hValue % 255
        if 764 < hValue < 1020:
            Color[1] = 255 - (hValue % 255)
            Color[2] = 255
        if 1019 < hValue < 1275:
            Color[0] = hValue % 255
            Color[2] = 255
        if 1274 < hValue < 1530:
            Color[0] = 255
            Color[2] = 255 - hValue % 255
        if 1530 == hValue:
            Color[0] = 255

        # get text
        Color = [255 if x + bValue >= 256 else x + bValue for x in Color]
        Color = [(x*sValue)/100 for x in Color]

        # show
        c = self.image.pixel(1023 if hValue == 1530 else hValue*1024/1530, 0)
        cpix = QtGui.QColor(c).getRgbF()
        cpix = [int((x * 255 * sValue)/100) for x in cpix]
        cpix = [255 if x + bValue >= 256 else x + bValue for x in cpix]
        cpix[3] = (cpix[3] * sValue) / 100

        # for dinamic
        self.LblColor.setText('%d, %d, %d' % (Color[0],Color[1],Color[2]))
        # modified color with shifted palette
        self.TxtColor.setStyleSheet(
            "QWidget{ background-color : rgba(%d, %d, %d, %d)}" % (cpix[0], cpix[1], cpix[2], cpix[3]))
        self.rgb = [cpix[0], cpix[1], cpix[2], cpix[3]]

    def changeBrightnessLabel(self):
        """
        adds to Brightness label current brightness value
        :return:
        """
        brightness = int(self.SuturationSlider.value())
        self.LblBrightness.setText("Brightness: %i" % brightness)

    @staticmethod
    def getColor(color_main):
        dialog = ColorDialog()
        dialog.setcolor(color_main)
        result = dialog.exec_()
        color = dialog.Color()
        return (color, result == QDialog.Accepted)

    @staticmethod
    def getColornoWindow(color_main):
        dialog = ColorDialog()
        dialog.setcolor(color_main)
        color = dialog.Color()
        return color, True