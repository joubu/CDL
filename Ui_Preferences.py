# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_Preferences.ui'
#
# Created: Sat Dec 20 19:45:55 2014
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Preferences(object):
    def setupUi(self, Preferences):
        Preferences.setObjectName(_fromUtf8("Preferences"))
        Preferences.resize(381, 389)
        self.formLayout_2 = QtGui.QFormLayout(Preferences)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(Preferences)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.lineEditPlayer = QtGui.QLineEdit(Preferences)
        self.lineEditPlayer.setText(_fromUtf8(""))
        self.lineEditPlayer.setObjectName(_fromUtf8("lineEditPlayer"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.lineEditPlayer)
        self.label_2 = QtGui.QLabel(Preferences)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.lineEditDirUser = QtGui.QLineEdit(Preferences)
        self.lineEditDirUser.setObjectName(_fromUtf8("lineEditDirUser"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.lineEditDirUser)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.label_4 = QtGui.QLabel(Preferences)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_2.addWidget(self.label_4)
        self.frame_2 = QtGui.QFrame(Preferences)
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.petit = QtGui.QCheckBox(self.frame_2)
        self.petit.setObjectName(_fromUtf8("petit"))
        self.gridLayout_2.addWidget(self.petit, 0, 1, 1, 1)
        self.pepites = QtGui.QCheckBox(self.frame_2)
        self.pepites.setObjectName(_fromUtf8("pepites"))
        self.gridLayout_2.addWidget(self.pepites, 2, 1, 1, 1)
        self.guignols = QtGui.QCheckBox(self.frame_2)
        self.guignols.setObjectName(_fromUtf8("guignols"))
        self.gridLayout_2.addWidget(self.guignols, 2, 0, 1, 1)
        self.grand = QtGui.QCheckBox(self.frame_2)
        self.grand.setObjectName(_fromUtf8("grand"))
        self.gridLayout_2.addWidget(self.grand, 3, 0, 1, 1)
        self.groland = QtGui.QCheckBox(self.frame_2)
        self.groland.setObjectName(_fromUtf8("groland"))
        self.gridLayout_2.addWidget(self.groland, 4, 0, 1, 1)
        self.jt = QtGui.QCheckBox(self.frame_2)
        self.jt.setObjectName(_fromUtf8("jt"))
        self.gridLayout_2.addWidget(self.jt, 1, 0, 1, 1)
        self.supplement = QtGui.QCheckBox(self.frame_2)
        self.supplement.setObjectName(_fromUtf8("supplement"))
        self.gridLayout_2.addWidget(self.supplement, 0, 0, 1, 1)
        self.salut = QtGui.QCheckBox(self.frame_2)
        self.salut.setObjectName(_fromUtf8("salut"))
        self.gridLayout_2.addWidget(self.salut, 1, 1, 1, 1)
        self.links = QtGui.QCheckBox(self.frame_2)
        self.links.setObjectName(_fromUtf8("links"))
        self.gridLayout_2.addWidget(self.links, 3, 1, 1, 1)
        self.explorateurs = QtGui.QCheckBox(self.frame_2)
        self.explorateurs.setObjectName(_fromUtf8("explorateurs"))
        self.gridLayout_2.addWidget(self.explorateurs, 5, 0, 1, 1)
        self.zapping = QtGui.QCheckBox(self.frame_2)
        self.zapping.setObjectName(_fromUtf8("zapping"))
        self.gridLayout_2.addWidget(self.zapping, 4, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.frame_2)
        self.formLayout_2.setLayout(0, QtGui.QFormLayout.LabelRole, self.verticalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(Preferences)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.formLayout_2.setLayout(1, QtGui.QFormLayout.SpanningRole, self.horizontalLayout)

        self.retranslateUi(Preferences)
        QtCore.QMetaObject.connectSlotsByName(Preferences)

    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(_translate("Preferences", "Préférences", None))
        self.label.setText(_translate("Preferences", "Player : ", None))
        self.label_2.setText(_translate("Preferences", "Emplacement : ", None))
        self.label_4.setText(_translate("Preferences", "Catégories : ", None))
        self.petit.setText(_translate("Preferences", "Petit journal", None))
        self.pepites.setText(_translate("Preferences", "Pépites du net", None))
        self.guignols.setText(_translate("Preferences", "Guignols", None))
        self.grand.setText(_translate("Preferences", "Grand Journal", None))
        self.groland.setText(_translate("Preferences", "Groland", None))
        self.jt.setText(_translate("Preferences", "Le JT", None))
        self.supplement.setText(_translate("Preferences", "Le Supplément", None))
        self.salut.setText(_translate("Preferences", "SLT", None))
        self.links.setText(_translate("Preferences", "L\'œil de Links", None))
        self.explorateurs.setText(_translate("Preferences", "Les nouveaux explorateurs", None))
        self.zapping.setText(_translate("Preferences", "ZAPPING", None))

