# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'diffusivity.ui'
##
## Created by: Qt User Interface Compiler version 6.1.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import diffusivity_resources_rc

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(373, 234)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setMaximumSize(QSize(16777215, 234))
        icon = QIcon()
        icon.addFile(u":/icons/icons/ui-slider-050.png", QSize(), QIcon.Normal, QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_8 = QLabel(Dialog)
        self.label_8.setObjectName(u"label_8")
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setMinimumSize(QSize(21, 16))
        self.label_8.setBaseSize(QSize(52, 16))
        font = QFont()
        font.setPointSize(12)
        self.label_8.setFont(font)
        self.label_8.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_8, 3, 2, 1, 1)

        self.txt_diffusive_min = QLineEdit(Dialog)
        self.txt_diffusive_min.setObjectName(u"txt_diffusive_min")
        sizePolicy.setHeightForWidth(self.txt_diffusive_min.sizePolicy().hasHeightForWidth())
        self.txt_diffusive_min.setSizePolicy(sizePolicy)
        self.txt_diffusive_min.setMinimumSize(QSize(70, 30))
        self.txt_diffusive_min.setMaximumSize(QSize(70, 30))
        font1 = QFont()
        font1.setPointSize(10)
        self.txt_diffusive_min.setFont(font1)
        self.txt_diffusive_min.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.txt_diffusive_min, 3, 1, 1, 1)

        self.lbl_diffusive = QLabel(Dialog)
        self.lbl_diffusive.setObjectName(u"lbl_diffusive")
        sizePolicy.setHeightForWidth(self.lbl_diffusive.sizePolicy().hasHeightForWidth())
        self.lbl_diffusive.setSizePolicy(sizePolicy)
        self.lbl_diffusive.setMinimumSize(QSize(120, 30))
        self.lbl_diffusive.setMaximumSize(QSize(120, 30))
        self.lbl_diffusive.setFont(font1)
        self.lbl_diffusive.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbl_diffusive, 3, 0, 1, 1)

        self.txt_immobile_min = QLineEdit(Dialog)
        self.txt_immobile_min.setObjectName(u"txt_immobile_min")
        self.txt_immobile_min.setEnabled(False)
        sizePolicy.setHeightForWidth(self.txt_immobile_min.sizePolicy().hasHeightForWidth())
        self.txt_immobile_min.setSizePolicy(sizePolicy)
        self.txt_immobile_min.setMinimumSize(QSize(70, 30))
        self.txt_immobile_min.setMaximumSize(QSize(70, 30))
        self.txt_immobile_min.setFont(font1)
        self.txt_immobile_min.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.txt_immobile_min, 1, 1, 1, 1)

        self.lbl_immobile = QLabel(Dialog)
        self.lbl_immobile.setObjectName(u"lbl_immobile")
        sizePolicy.setHeightForWidth(self.lbl_immobile.sizePolicy().hasHeightForWidth())
        self.lbl_immobile.setSizePolicy(sizePolicy)
        self.lbl_immobile.setMinimumSize(QSize(120, 30))
        self.lbl_immobile.setMaximumSize(QSize(120, 30))
        self.lbl_immobile.setFont(font1)
        self.lbl_immobile.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbl_immobile, 1, 0, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 4, 6, 1)

        self.lbl_subdiffusive = QLabel(Dialog)
        self.lbl_subdiffusive.setObjectName(u"lbl_subdiffusive")
        sizePolicy.setHeightForWidth(self.lbl_subdiffusive.sizePolicy().hasHeightForWidth())
        self.lbl_subdiffusive.setSizePolicy(sizePolicy)
        self.lbl_subdiffusive.setMinimumSize(QSize(120, 30))
        self.lbl_subdiffusive.setMaximumSize(QSize(120, 30))
        self.lbl_subdiffusive.setFont(font1)
        self.lbl_subdiffusive.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbl_subdiffusive, 2, 0, 1, 1)

        self.label_6 = QLabel(Dialog)
        self.label_6.setObjectName(u"label_6")
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QSize(21, 16))
        self.label_6.setBaseSize(QSize(52, 16))
        self.label_6.setFont(font)
        self.label_6.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_6, 1, 2, 1, 1)

        self.txt_immobile_max = QLineEdit(Dialog)
        self.txt_immobile_max.setObjectName(u"txt_immobile_max")
        self.txt_immobile_max.setEnabled(False)
        sizePolicy.setHeightForWidth(self.txt_immobile_max.sizePolicy().hasHeightForWidth())
        self.txt_immobile_max.setSizePolicy(sizePolicy)
        self.txt_immobile_max.setMinimumSize(QSize(70, 30))
        self.txt_immobile_max.setMaximumSize(QSize(70, 30))
        self.txt_immobile_max.setFont(font1)
        self.txt_immobile_max.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.txt_immobile_max, 1, 3, 1, 1)

        self.txt_active_min = QLineEdit(Dialog)
        self.txt_active_min.setObjectName(u"txt_active_min")
        sizePolicy.setHeightForWidth(self.txt_active_min.sizePolicy().hasHeightForWidth())
        self.txt_active_min.setSizePolicy(sizePolicy)
        self.txt_active_min.setMinimumSize(QSize(70, 30))
        self.txt_active_min.setMaximumSize(QSize(70, 30))
        self.txt_active_min.setFont(font1)
        self.txt_active_min.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.txt_active_min, 4, 1, 1, 1)

        self.label_7 = QLabel(Dialog)
        self.label_7.setObjectName(u"label_7")
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setMinimumSize(QSize(21, 16))
        self.label_7.setBaseSize(QSize(52, 16))
        self.label_7.setFont(font)
        self.label_7.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_7, 2, 2, 1, 1)

        self.txt_subdiffusive_max = QLineEdit(Dialog)
        self.txt_subdiffusive_max.setObjectName(u"txt_subdiffusive_max")
        self.txt_subdiffusive_max.setEnabled(False)
        sizePolicy.setHeightForWidth(self.txt_subdiffusive_max.sizePolicy().hasHeightForWidth())
        self.txt_subdiffusive_max.setSizePolicy(sizePolicy)
        self.txt_subdiffusive_max.setMinimumSize(QSize(70, 30))
        self.txt_subdiffusive_max.setMaximumSize(QSize(70, 30))
        self.txt_subdiffusive_max.setFont(font1)
        self.txt_subdiffusive_max.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.txt_subdiffusive_max, 2, 3, 1, 1)

        self.txt_subdiffusive_min = QLineEdit(Dialog)
        self.txt_subdiffusive_min.setObjectName(u"txt_subdiffusive_min")
        sizePolicy.setHeightForWidth(self.txt_subdiffusive_min.sizePolicy().hasHeightForWidth())
        self.txt_subdiffusive_min.setSizePolicy(sizePolicy)
        self.txt_subdiffusive_min.setMinimumSize(QSize(70, 30))
        self.txt_subdiffusive_min.setMaximumSize(QSize(70, 30))
        self.txt_subdiffusive_min.setFont(font1)
        self.txt_subdiffusive_min.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.txt_subdiffusive_min, 2, 1, 1, 1)

        self.lbl_active = QLabel(Dialog)
        self.lbl_active.setObjectName(u"lbl_active")
        sizePolicy.setHeightForWidth(self.lbl_active.sizePolicy().hasHeightForWidth())
        self.lbl_active.setSizePolicy(sizePolicy)
        self.lbl_active.setMinimumSize(QSize(120, 30))
        self.lbl_active.setMaximumSize(QSize(120, 30))
        self.lbl_active.setFont(font1)
        self.lbl_active.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.lbl_active, 4, 0, 1, 1)

        self.txt_diffusive_max = QLineEdit(Dialog)
        self.txt_diffusive_max.setObjectName(u"txt_diffusive_max")
        self.txt_diffusive_max.setEnabled(False)
        sizePolicy.setHeightForWidth(self.txt_diffusive_max.sizePolicy().hasHeightForWidth())
        self.txt_diffusive_max.setSizePolicy(sizePolicy)
        self.txt_diffusive_max.setMinimumSize(QSize(70, 30))
        self.txt_diffusive_max.setMaximumSize(QSize(70, 30))
        self.txt_diffusive_max.setFont(font1)
        self.txt_diffusive_max.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.txt_diffusive_max, 3, 3, 1, 1)

        self.label_9 = QLabel(Dialog)
        self.label_9.setObjectName(u"label_9")
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setMinimumSize(QSize(21, 16))
        self.label_9.setBaseSize(QSize(52, 16))
        self.label_9.setFont(font)
        self.label_9.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.label_9, 4, 2, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_3, 5, 1, 1, 3)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 0, 0, 1, 4)

        self.txt_active_max = QLineEdit(Dialog)
        self.txt_active_max.setObjectName(u"txt_active_max")
        self.txt_active_max.setEnabled(False)
        sizePolicy.setHeightForWidth(self.txt_active_max.sizePolicy().hasHeightForWidth())
        self.txt_active_max.setSizePolicy(sizePolicy)
        self.txt_active_max.setMinimumSize(QSize(70, 30))
        self.txt_active_max.setMaximumSize(QSize(70, 30))
        self.txt_active_max.setFont(font1)
        self.txt_active_max.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.txt_active_max, 4, 3, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.verticalSpacer = QSpacerItem(229, 25, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setFont(font1)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)

        self.verticalLayout.addWidget(self.buttonBox)

#if QT_CONFIG(shortcut)
        self.lbl_diffusive.setBuddy(self.txt_diffusive_min)
        self.lbl_immobile.setBuddy(self.txt_immobile_min)
        self.lbl_subdiffusive.setBuddy(self.txt_subdiffusive_min)
        self.lbl_active.setBuddy(self.txt_active_min)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.txt_immobile_min, self.txt_subdiffusive_min)
        QWidget.setTabOrder(self.txt_subdiffusive_min, self.txt_diffusive_min)
        QWidget.setTabOrder(self.txt_diffusive_min, self.txt_active_min)
        QWidget.setTabOrder(self.txt_active_min, self.txt_immobile_max)
        QWidget.setTabOrder(self.txt_immobile_max, self.txt_subdiffusive_max)
        QWidget.setTabOrder(self.txt_subdiffusive_max, self.txt_diffusive_max)
        QWidget.setTabOrder(self.txt_diffusive_max, self.txt_active_max)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.txt_subdiffusive_min.textChanged.connect(self.txt_immobile_max.setText)
        self.txt_diffusive_min.textChanged.connect(self.txt_subdiffusive_max.setText)
        self.txt_active_min.textChanged.connect(self.txt_diffusive_max.setText)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Diffusivity configuration", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", u"-", None))
        self.txt_diffusive_min.setInputMask(QCoreApplication.translate("Dialog", u"#.0", None))
        self.txt_diffusive_min.setText(QCoreApplication.translate("Dialog", u"0.0", None))
        self.lbl_diffusive.setText(QCoreApplication.translate("Dialog", u"Diffusive", None))
        self.txt_immobile_min.setInputMask(QCoreApplication.translate("Dialog", u"#.0", None))
        self.txt_immobile_min.setText(QCoreApplication.translate("Dialog", u"0.0", None))
        self.lbl_immobile.setText(QCoreApplication.translate("Dialog", u"Immobile", None))
        self.lbl_subdiffusive.setText(QCoreApplication.translate("Dialog", u"Subdiffusive", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"-", None))
        self.txt_immobile_max.setInputMask(QCoreApplication.translate("Dialog", u"#.000", None))
        self.txt_immobile_max.setText(QCoreApplication.translate("Dialog", u"0.000", None))
        self.txt_active_min.setInputMask(QCoreApplication.translate("Dialog", u"#.0", None))
        self.txt_active_min.setText(QCoreApplication.translate("Dialog", u"0.0", None))
        self.label_7.setText(QCoreApplication.translate("Dialog", u"-", None))
        self.txt_subdiffusive_max.setInputMask(QCoreApplication.translate("Dialog", u"#.000", None))
        self.txt_subdiffusive_max.setText(QCoreApplication.translate("Dialog", u"0.000", None))
        self.txt_subdiffusive_min.setInputMask(QCoreApplication.translate("Dialog", u"#.0", None))
        self.txt_subdiffusive_min.setText(QCoreApplication.translate("Dialog", u"0.0", None))
        self.lbl_active.setText(QCoreApplication.translate("Dialog", u"Active", None))
        self.txt_diffusive_max.setInputMask(QCoreApplication.translate("Dialog", u"#.000", None))
        self.txt_diffusive_max.setText(QCoreApplication.translate("Dialog", u"0.000", None))
        self.label_9.setText(QCoreApplication.translate("Dialog", u"-", None))
        self.txt_active_max.setInputMask("")
        self.txt_active_max.setText(QCoreApplication.translate("Dialog", u"\u221e", None))
    # retranslateUi

