# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ai2x.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QDir,
    QSize,
    QTime,
    QUrl,
    Qt,
    Slot,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QWidget,
    QStyle,
    QFileDialog,
)


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(400, 245)
        self.start_button = QPushButton(Form)
        self.start_button.setObjectName("start_button")
        self.start_button.setGeometry(QRect(90, 190, 75, 23))
        self.abort_button = QPushButton(Form)
        self.abort_button.setObjectName("abort_button")
        self.abort_button.setGeometry(QRect(220, 190, 75, 23))
        self.progress_bar = QProgressBar(Form)
        self.progress_bar.setObjectName("progress_bar")
        self.progress_bar.setGeometry(QRect(170, 150, 201, 23))
        self.progress_bar.setValue(0)
        self.input_lineEdit = QLineEdit(Form)
        self.input_lineEdit.setObjectName("input_lineEdit")
        self.input_lineEdit.setGeometry(QRect(90, 30, 271, 20))
        self._read_input_action = self.input_lineEdit.addAction(
            qApp.style().standardIcon(QStyle.SP_DirOpenIcon), QLineEdit.TrailingPosition
        )
        self._read_input_action.triggered.connect(self.slot_read_input)
        self.input_label = QLabel(Form)
        self.input_label.setObjectName("input_label")
        self.input_label.setGeometry(QRect(30, 30, 61, 20))
        self.output_label = QLabel(Form)
        self.output_label.setObjectName("output_label")
        self.output_label.setGeometry(QRect(20, 70, 71, 20))
        self.output_lineEdit = QLineEdit(Form)
        self.output_lineEdit.setObjectName("output_lineEdit")
        self.output_lineEdit.setGeometry(QRect(90, 70, 271, 20))
        self._set_output_action = self.output_lineEdit.addAction(
            qApp.style().standardIcon(QStyle.SP_DirOpenIcon), QLineEdit.TrailingPosition
        )
        self._set_output_action.triggered.connect(self.slot_set_output)
        self.scale_comboBox = QComboBox(Form)
        self.scale_comboBox.addItem("")
        self.scale_comboBox.addItem("")
        self.scale_comboBox.addItem("")
        self.scale_comboBox.setObjectName("scale_comboBox")
        self.scale_comboBox.setGeometry(QRect(80, 110, 51, 22))
        self.scale_label = QLabel(Form)
        self.scale_label.setObjectName("scale_label")
        self.scale_label.setGeometry(QRect(40, 110, 31, 20))
        self.tta_checkBox = QCheckBox(Form)
        self.tta_checkBox.setObjectName("tta_checkBox")
        self.tta_checkBox.setGeometry(QRect(40, 150, 73, 21))
        self.model_comboBox = QComboBox(Form)
        self.model_comboBox.addItem("")
        self.model_comboBox.addItem("")
        self.model_comboBox.addItem("")
        self.model_comboBox.addItem("")
        self.model_comboBox.setObjectName("model_comboBox")
        self.model_comboBox.setGeometry(QRect(200, 110, 161, 22))
        self.model_label = QLabel(Form)
        self.model_label.setObjectName("model_label")
        self.model_label.setGeometry(QRect(150, 110, 41, 20))

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", "Form", None))
        self.start_button.setText(QCoreApplication.translate("Form", "Start", None))
        self.abort_button.setText(QCoreApplication.translate("Form", "Abort", None))
        self.input_label.setText(QCoreApplication.translate("Form", "Input File", None))
        self.output_label.setText(
            QCoreApplication.translate("Form", "Output Path", None)
        )
        self.scale_comboBox.setItemText(
            0, QCoreApplication.translate("Form", "2x", None)
        )
        self.scale_comboBox.setItemText(
            1, QCoreApplication.translate("Form", "3x", None)
        )
        self.scale_comboBox.setItemText(
            2, QCoreApplication.translate("Form", "4x", None)
        )

        self.scale_comboBox.setCurrentText(
            QCoreApplication.translate("Form", "2x", None)
        )
        self.scale_label.setText(QCoreApplication.translate("Form", "Scale", None))
        self.tta_checkBox.setText(QCoreApplication.translate("Form", "TTA mode", None))
        self.model_comboBox.setItemText(
            0, QCoreApplication.translate("Form", "realesrgan-x4plus", None)
        )
        self.model_comboBox.setItemText(
            1, QCoreApplication.translate("Form", "realesr-animevideov3", None)
        )
        self.model_comboBox.setItemText(
            2, QCoreApplication.translate("Form", "realesrgan-x4plus-anime", None)
        )
        self.model_comboBox.setItemText(
            3, QCoreApplication.translate("Form", "realesrnet-x4plus", None)
        )

        self.model_comboBox.setCurrentText(
            QCoreApplication.translate("Form", "realesrgan-x4plus", None)
        )
        self.model_label.setText(QCoreApplication.translate("Form", "Model", None))

    # retranslateUi

    @Slot()
    def slot_read_input(self):
        input_fpath = QFileDialog.getOpenFileName(
            self, "Open File", QDir.homePath(), "Video (*.mp4 *.mkv *.flv)"
        )[0]

        if input_fpath:
            self.input_lineEdit.setText(input_fpath)

    @Slot()
    def slot_set_output(self):
        output_path = QFileDialog.getExistingDirectory(
            self, "Open Directory", QDir.homePath(), QFileDialog.ShowDirsOnly
        )

        if output_path:
            output_dir = QDir(output_path)
            self.output_lineEdit.setText(QDir.fromNativeSeparators(output_dir.path()))
