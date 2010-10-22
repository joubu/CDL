# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_MainWindow.ui'
#
# Created: Fri Oct 22 18:59:53 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 800)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout = QtGui.QGridLayout(self.tab)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.downloadsList = DownloadsList(self.tab)
        self.downloadsList.setObjectName("downloadsList")
        self.verticalLayout.addWidget(self.downloadsList)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonBlacklist = QtGui.QPushButton(self.tab)
        self.pushButtonBlacklist.setMinimumSize(QtCore.QSize(0, 42))
        self.pushButtonBlacklist.setStyleSheet("background-image: url(\":/*.png/resources/kblackbox.png\");\n"
"background-repeat: no-repeat;\n"
"background-position: center;")
        self.pushButtonBlacklist.setText("")
        self.pushButtonBlacklist.setObjectName("pushButtonBlacklist")
        self.horizontalLayout.addWidget(self.pushButtonBlacklist)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButtonRefresh = QtGui.QPushButton(self.tab)
        self.pushButtonRefresh.setMinimumSize(QtCore.QSize(0, 42))
        self.pushButtonRefresh.setStyleSheet("background-image: url(\":/*.png/resources/reload_all_tabs.png\");\n"
"background-repeat: no-repeat;\n"
"background-position: center;")
        self.pushButtonRefresh.setText("")
        self.pushButtonRefresh.setObjectName("pushButtonRefresh")
        self.horizontalLayout.addWidget(self.pushButtonRefresh)
        self.pushButtonDownload = QtGui.QPushButton(self.tab)
        self.pushButtonDownload.setMinimumSize(QtCore.QSize(0, 42))
        self.pushButtonDownload.setStyleSheet("background-image: url(\":/*.png/resources/download.png\");\n"
"background-repeat: no-repeat;\n"
"background-position: center;")
        self.pushButtonDownload.setText("")
        self.pushButtonDownload.setObjectName("pushButtonDownload")
        self.horizontalLayout.addWidget(self.pushButtonDownload)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.verticalLayout_3)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab1 = QtGui.QWidget()
        self.tab1.setObjectName("tab1")
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.tab1)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.scrollArea = QtGui.QScrollArea(self.tab1)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 742, 3402))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_2 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.categoriesList = CategoriesList(self.scrollAreaWidgetContents)
        self.categoriesList.setFrameShape(QtGui.QFrame.StyledPanel)
        self.categoriesList.setFrameShadow(QtGui.QFrame.Raised)
        self.categoriesList.setObjectName("categoriesList")
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.categoriesList)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.discrete = CategoryGroupBox(self.categoriesList)
        self.discrete.setFlat(True)
        self.discrete.setCheckable(True)
        self.discrete.setObjectName("discrete")
        self.gridLayout_14 = QtGui.QGridLayout(self.discrete)
        self.gridLayout_14.setObjectName("gridLayout_14")
        self.list_discrete = VideosList(self.discrete)
        self.list_discrete.setMinimumSize(QtCore.QSize(0, 200))
        self.list_discrete.setAlternatingRowColors(True)
        self.list_discrete.setGridStyle(QtCore.Qt.NoPen)
        self.list_discrete.setObjectName("list_discrete")
        self.list_discrete.horizontalHeader().setCascadingSectionResizes(True)
        self.gridLayout_14.addWidget(self.list_discrete, 0, 0, 1, 1)
        self.verticalLayout_10.addWidget(self.discrete)
        self.boite = CategoryGroupBox(self.categoriesList)
        self.boite.setFlat(True)
        self.boite.setCheckable(True)
        self.boite.setObjectName("boite")
        self.gridLayout_15 = QtGui.QGridLayout(self.boite)
        self.gridLayout_15.setObjectName("gridLayout_15")
        self.list_boite = VideosList(self.boite)
        self.list_boite.setMinimumSize(QtCore.QSize(0, 200))
        self.list_boite.setAlternatingRowColors(True)
        self.list_boite.setGridStyle(QtCore.Qt.NoPen)
        self.list_boite.setObjectName("list_boite")
        self.gridLayout_15.addWidget(self.list_boite, 0, 0, 1, 1)
        self.verticalLayout_10.addWidget(self.boite)
        self.boucan = CategoryGroupBox(self.categoriesList)
        self.boucan.setFlat(False)
        self.boucan.setCheckable(True)
        self.boucan.setObjectName("boucan")
        self.gridLayout_3 = QtGui.QGridLayout(self.boucan)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.list_boucan = VideosList(self.boucan)
        self.list_boucan.setMinimumSize(QtCore.QSize(0, 200))
        self.list_boucan.setAlternatingRowColors(True)
        self.list_boucan.setGridStyle(QtCore.Qt.NoPen)
        self.list_boucan.setObjectName("list_boucan")
        self.gridLayout_3.addWidget(self.list_boucan, 0, 0, 1, 1)
        self.verticalLayout_10.addWidget(self.boucan)
        self.grand = CategoryGroupBox(self.categoriesList)
        self.grand.setCheckable(True)
        self.grand.setObjectName("grand")
        self.gridLayout_4 = QtGui.QGridLayout(self.grand)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.list_grand = VideosList(self.grand)
        self.list_grand.setMinimumSize(QtCore.QSize(0, 200))
        self.list_grand.setAlternatingRowColors(True)
        self.list_grand.setGridStyle(QtCore.Qt.NoPen)
        self.list_grand.setObjectName("list_grand")
        self.gridLayout_4.addWidget(self.list_grand, 0, 0, 1, 1)
        self.verticalLayout_10.addWidget(self.grand)
        self.guignols = CategoryGroupBox(self.categoriesList)
        self.guignols.setFlat(True)
        self.guignols.setCheckable(True)
        self.guignols.setObjectName("guignols")
        self.gridLayout_16 = QtGui.QGridLayout(self.guignols)
        self.gridLayout_16.setObjectName("gridLayout_16")
        self.list_guignols = VideosList(self.guignols)
        self.list_guignols.setMinimumSize(QtCore.QSize(0, 200))
        self.list_guignols.setAlternatingRowColors(True)
        self.list_guignols.setGridStyle(QtCore.Qt.NoPen)
        self.list_guignols.setObjectName("list_guignols")
        self.gridLayout_16.addWidget(self.list_guignols, 0, 0, 1, 1)
        self.verticalLayout_10.addWidget(self.guignols)
        self.groland = CategoryGroupBox(self.categoriesList)
        self.groland.setFlat(True)
        self.groland.setCheckable(True)
        self.groland.setObjectName("groland")
        self.gridLayout_17 = QtGui.QGridLayout(self.groland)
        self.gridLayout_17.setObjectName("gridLayout_17")
        self.list_groland = VideosList(self.groland)
        self.list_groland.setMinimumSize(QtCore.QSize(0, 200))
        self.list_groland.setGridStyle(QtCore.Qt.NoPen)
        self.list_groland.setObjectName("list_groland")
        self.gridLayout_17.addWidget(self.list_groland, 0, 0, 1, 1)
        self.verticalLayout_10.addWidget(self.groland)
        self.matinale = CategoryGroupBox(self.categoriesList)
        self.matinale.setCheckable(True)
        self.matinale.setObjectName("matinale")
        self.gridLayout_5 = QtGui.QGridLayout(self.matinale)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.list_matinale = VideosList(self.matinale)
        self.list_matinale.setMinimumSize(QtCore.QSize(0, 200))
        self.list_matinale.setAlternatingRowColors(True)
        self.list_matinale.setGridStyle(QtCore.Qt.NoPen)
        self.list_matinale.setObjectName("list_matinale")
        self.gridLayout_5.addWidget(self.list_matinale, 0, 0, 1, 1)
        self.verticalLayout_10.addWidget(self.matinale)
        self.meteo = CategoryGroupBox(self.categoriesList)
        self.meteo.setFlat(True)
        self.meteo.setCheckable(True)
        self.meteo.setObjectName("meteo")
        self.gridLayout_18 = QtGui.QGridLayout(self.meteo)
        self.gridLayout_18.setObjectName("gridLayout_18")
        self.list_meteo = VideosList(self.meteo)
        self.list_meteo.setMinimumSize(QtCore.QSize(0, 200))
        self.list_meteo.setAlternatingRowColors(True)
        self.list_meteo.setGridStyle(QtCore.Qt.NoPen)
        self.list_meteo.setObjectName("list_meteo")
        self.gridLayout_18.addWidget(self.list_meteo, 0, 0, 1, 1)
        self.verticalLayout_10.addWidget(self.meteo)
        self.petit = CategoryGroupBox(self.categoriesList)
        self.petit.setFlat(True)
        self.petit.setCheckable(True)
        self.petit.setObjectName("petit")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.petit)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.list_petit = VideosList(self.petit)
        self.list_petit.setMinimumSize(QtCore.QSize(0, 200))
        self.list_petit.setAlternatingRowColors(True)
        self.list_petit.setGridStyle(QtCore.Qt.NoPen)
        self.list_petit.setObjectName("list_petit")
        self.verticalLayout_2.addWidget(self.list_petit)
        self.verticalLayout_10.addWidget(self.petit)
        self.petite = CategoryGroupBox(self.categoriesList)
        self.petite.setFlat(True)
        self.petite.setCheckable(True)
        self.petite.setObjectName("petite")
        self.gridLayout_20 = QtGui.QGridLayout(self.petite)
        self.gridLayout_20.setObjectName("gridLayout_20")
        self.list_petite = VideosList(self.petite)
        self.list_petite.setMinimumSize(QtCore.QSize(0, 200))
        self.list_petite.setAlternatingRowColors(True)
        self.list_petite.setGridStyle(QtCore.Qt.NoPen)
        self.list_petite.setObjectName("list_petite")
        self.gridLayout_20.addWidget(self.list_petite, 0, 0, 1, 1)
        self.verticalLayout_10.addWidget(self.petite)
        self.pepites = CategoryGroupBox(self.categoriesList)
        self.pepites.setFlat(True)
        self.pepites.setCheckable(True)
        self.pepites.setObjectName("pepites")
        self.gridLayout_21 = QtGui.QGridLayout(self.pepites)
        self.gridLayout_21.setObjectName("gridLayout_21")
        self.list_pepites = VideosList(self.pepites)
        self.list_pepites.setMinimumSize(QtCore.QSize(0, 200))
        self.list_pepites.setAlternatingRowColors(True)
        self.list_pepites.setGridStyle(QtCore.Qt.NoPen)
        self.list_pepites.setObjectName("list_pepites")
        self.gridLayout_21.addWidget(self.list_pepites, 0, 0, 1, 1)
        self.verticalLayout_10.addWidget(self.pepites)
        self.salut = CategoryGroupBox(self.categoriesList)
        self.salut.setFlat(True)
        self.salut.setCheckable(True)
        self.salut.setObjectName("salut")
        self.gridLayout_22 = QtGui.QGridLayout(self.salut)
        self.gridLayout_22.setObjectName("gridLayout_22")
        self.list_salut = VideosList(self.salut)
        self.list_salut.setMinimumSize(QtCore.QSize(0, 200))
        self.list_salut.setAlternatingRowColors(True)
        self.list_salut.setGridStyle(QtCore.Qt.NoPen)
        self.list_salut.setObjectName("list_salut")
        self.gridLayout_22.addWidget(self.list_salut, 0, 0, 1, 1)
        self.verticalLayout_10.addWidget(self.salut)
        self.sav = CategoryGroupBox(self.categoriesList)
        self.sav.setFlat(True)
        self.sav.setCheckable(True)
        self.sav.setObjectName("sav")
        self.gridLayout_23 = QtGui.QGridLayout(self.sav)
        self.gridLayout_23.setObjectName("gridLayout_23")
        self.list_sav = VideosList(self.sav)
        self.list_sav.setMinimumSize(QtCore.QSize(0, 200))
        self.list_sav.setAlternatingRowColors(True)
        self.list_sav.setGridStyle(QtCore.Qt.NoPen)
        self.list_sav.setObjectName("list_sav")
        self.gridLayout_23.addWidget(self.list_sav, 0, 0, 1, 1)
        self.verticalLayout_10.addWidget(self.sav)
        self.zapping = CategoryGroupBox(self.categoriesList)
        self.zapping.setFlat(True)
        self.zapping.setCheckable(True)
        self.zapping.setObjectName("zapping")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.zapping)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.list_zapping = VideosList(self.zapping)
        self.list_zapping.setMinimumSize(QtCore.QSize(0, 200))
        self.list_zapping.setAlternatingRowColors(True)
        self.list_zapping.setGridStyle(QtCore.Qt.NoPen)
        self.list_zapping.setObjectName("list_zapping")
        self.verticalLayout_5.addWidget(self.list_zapping)
        self.verticalLayout_10.addWidget(self.zapping)
        self.gridLayout_2.addWidget(self.categoriesList, 0, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_9.addWidget(self.scrollArea)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButtonSeen = QtGui.QPushButton(self.tab1)
        self.pushButtonSeen.setMinimumSize(QtCore.QSize(0, 42))
        self.pushButtonSeen.setStyleSheet("background-image: url(\":/*.png/resources/viewmag+.png\");\n"
"background-repeat: no-repeat;\n"
"background-position: center;")
        self.pushButtonSeen.setText("")
        self.pushButtonSeen.setObjectName("pushButtonSeen")
        self.horizontalLayout_2.addWidget(self.pushButtonSeen)
        self.pushButtonNotSeen = QtGui.QPushButton(self.tab1)
        self.pushButtonNotSeen.setMinimumSize(QtCore.QSize(0, 42))
        self.pushButtonNotSeen.setStyleSheet("background-image: url(\":/*.png/resources/viewmag-.png\");\n"
"background-repeat: no-repeat;\n"
"background-position: center;")
        self.pushButtonNotSeen.setText("")
        self.pushButtonNotSeen.setObjectName("pushButtonNotSeen")
        self.horizontalLayout_2.addWidget(self.pushButtonNotSeen)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.pushButtonRemove = QtGui.QPushButton(self.tab1)
        self.pushButtonRemove.setMinimumSize(QtCore.QSize(0, 42))
        self.pushButtonRemove.setStyleSheet("background-image: url(\":/*.png/resources/button_cancel.png\");\n"
"background-repeat: no-repeat;\n"
"background-position: center;")
        self.pushButtonRemove.setText("")
        self.pushButtonRemove.setObjectName("pushButtonRemove")
        self.horizontalLayout_2.addWidget(self.pushButtonRemove)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.pushButtonPlay = QtGui.QPushButton(self.tab1)
        self.pushButtonPlay.setMinimumSize(QtCore.QSize(0, 42))
        self.pushButtonPlay.setAutoFillBackground(False)
        self.pushButtonPlay.setStyleSheet("background-image: url(\":/*.png/resources/video.png\");\n"
"background-repeat: no-repeat;\n"
"background-position: center;")
        self.pushButtonPlay.setText("")
        self.pushButtonPlay.setObjectName("pushButtonPlay")
        self.horizontalLayout_2.addWidget(self.pushButtonPlay)
        self.verticalLayout_9.addLayout(self.horizontalLayout_2)
        self.tabWidget.addTab(self.tab1, "")
        self.verticalLayout_8.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 30))
        self.menubar.setObjectName("menubar")
        self.menuFichier = QtGui.QMenu(self.menubar)
        self.menuFichier.setObjectName("menuFichier")
        self.menu_dition = QtGui.QMenu(self.menubar)
        self.menu_dition.setObjectName("menu_dition")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")
        self.actionPreferences = QtGui.QAction(MainWindow)
        self.actionPreferences.setObjectName("actionPreferences")
        self.menuFichier.addAction(self.actionQuit)
        self.menu_dition.addAction(self.actionPreferences)
        self.menubar.addAction(self.menuFichier.menuAction())
        self.menubar.addAction(self.menu_dition.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.boite, QtCore.SIGNAL("toggled(bool)"), self.list_boite.setVisible)
        QtCore.QObject.connect(self.discrete, QtCore.SIGNAL("toggled(bool)"), self.list_discrete.setVisible)
        QtCore.QObject.connect(self.groland, QtCore.SIGNAL("toggled(bool)"), self.list_groland.setVisible)
        QtCore.QObject.connect(self.guignols, QtCore.SIGNAL("toggled(bool)"), self.list_guignols.setVisible)
        QtCore.QObject.connect(self.meteo, QtCore.SIGNAL("toggled(bool)"), self.list_meteo.setVisible)
        QtCore.QObject.connect(self.pepites, QtCore.SIGNAL("toggled(bool)"), self.list_pepites.setVisible)
        QtCore.QObject.connect(self.zapping, QtCore.SIGNAL("toggled(bool)"), self.list_zapping.setVisible)
        QtCore.QObject.connect(self.sav, QtCore.SIGNAL("toggled(bool)"), self.list_sav.setVisible)
        QtCore.QObject.connect(self.petit, QtCore.SIGNAL("toggled(bool)"), self.list_petit.setVisible)
        QtCore.QObject.connect(self.petite, QtCore.SIGNAL("toggled(bool)"), self.list_petite.setVisible)
        QtCore.QObject.connect(self.salut, QtCore.SIGNAL("toggled(bool)"), self.list_salut.setVisible)
        QtCore.QObject.connect(self.boucan, QtCore.SIGNAL("toggled(bool)"), self.list_boucan.setVisible)
        QtCore.QObject.connect(self.grand, QtCore.SIGNAL("toggled(bool)"), self.list_grand.setVisible)
        QtCore.QObject.connect(self.matinale, QtCore.SIGNAL("toggled(bool)"), self.list_matinale.setVisible)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "c+dl", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonBlacklist.setToolTip(QtGui.QApplication.translate("MainWindow", "Blacklister les vidéos sélectionnées.\n"
"Elles ne réapparaitront plus dans cette liste", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonRefresh.setToolTip(QtGui.QApplication.translate("MainWindow", "Rafraichir la liste des nouvelles vidéos disponibles", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonDownload.setToolTip(QtGui.QApplication.translate("MainWindow", "Télécharger les vidéos sélectionnées", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("MainWindow", "Télécharger", None, QtGui.QApplication.UnicodeUTF8))
        self.discrete.setTitle(QtGui.QApplication.translate("MainWindow", "Action discrète", None, QtGui.QApplication.UnicodeUTF8))
        self.boite.setTitle(QtGui.QApplication.translate("MainWindow", "Boite à questions", None, QtGui.QApplication.UnicodeUTF8))
        self.boucan.setTitle(QtGui.QApplication.translate("MainWindow", "Le Buzz du jour", None, QtGui.QApplication.UnicodeUTF8))
        self.grand.setTitle(QtGui.QApplication.translate("MainWindow", "Le Grand Journal", None, QtGui.QApplication.UnicodeUTF8))
        self.guignols.setTitle(QtGui.QApplication.translate("MainWindow", "Guignols", None, QtGui.QApplication.UnicodeUTF8))
        self.groland.setTitle(QtGui.QApplication.translate("MainWindow", "Groland", None, QtGui.QApplication.UnicodeUTF8))
        self.matinale.setTitle(QtGui.QApplication.translate("MainWindow", "La matinale", None, QtGui.QApplication.UnicodeUTF8))
        self.meteo.setTitle(QtGui.QApplication.translate("MainWindow", "meteo", None, QtGui.QApplication.UnicodeUTF8))
        self.petit.setTitle(QtGui.QApplication.translate("MainWindow", "Petit journal", None, QtGui.QApplication.UnicodeUTF8))
        self.petite.setTitle(QtGui.QApplication.translate("MainWindow", "Petite semaine", None, QtGui.QApplication.UnicodeUTF8))
        self.pepites.setTitle(QtGui.QApplication.translate("MainWindow", "Pépites du net", None, QtGui.QApplication.UnicodeUTF8))
        self.salut.setTitle(QtGui.QApplication.translate("MainWindow", "SLT", None, QtGui.QApplication.UnicodeUTF8))
        self.sav.setTitle(QtGui.QApplication.translate("MainWindow", "SAV", None, QtGui.QApplication.UnicodeUTF8))
        self.zapping.setTitle(QtGui.QApplication.translate("MainWindow", "Zapping", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonSeen.setToolTip(QtGui.QApplication.translate("MainWindow", "Marquée comme vue", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonNotSeen.setToolTip(QtGui.QApplication.translate("MainWindow", "Marquée comme non vue", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonRemove.setToolTip(QtGui.QApplication.translate("MainWindow", "Supprimer la vidéo sélectionnée", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonPlay.setToolTip(QtGui.QApplication.translate("MainWindow", "Lire la vidéo sélectionnée", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab1), QtGui.QApplication.translate("MainWindow", "Mes vidéos", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFichier.setTitle(QtGui.QApplication.translate("MainWindow", "Fichier", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_dition.setTitle(QtGui.QApplication.translate("MainWindow", "Édition", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("MainWindow", "Quitter", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPreferences.setText(QtGui.QApplication.translate("MainWindow", "Préférences", None, QtGui.QApplication.UnicodeUTF8))

from CDL import DownloadsList, CategoryGroupBox, CategoriesList
from Video import VideosList
import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

