#!/bin/python
# -*- coding: utf-8 -*-

import urllib
import sys
import os
import re
import traceback
import select
import shlex
import fcntl
import time
import subprocess
import threading
import signal

from operator import attrgetter
import pygst
pygst.require("0.10")
import gst

import datetime

from elixir import setup_all, create_all
from elixir import metadata, session
from elixir import Entity, Field
from elixir import Integer, Unicode, Boolean, DateTime
from elixir import ManyToMany, ManyToOne, OneToMany
from elixir import using_options

# Emplacement du fichier
WORKING_DIR = os.path.dirname(__file__)

DB_FILE = os.path.join(WORKING_DIR, 'database.db')
metadata.bind = 'sqlite:///%s' % DB_FILE
metadata.bind.echo = False

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Ui_MainWindow import Ui_MainWindow
from Ui_Preferences import Ui_Preferences
import resources_rc
from modele import Video, Category, Config
from DAO import DAO
from Download import *
from Video import *

debug = False
#debug = True

# Quit sur CTRL-C
signal.signal(signal.SIGINT, signal.SIG_DFL)

if not os.path.exists('/usr/bin/flvstreamer'):
    print "flvstreamer must be installed"
    exit(1)


config = DAO.init()
config.categories




class Ui_Wait(QProgressDialog):
    def __init__(self, parent=None):
        QProgressDialog.__init__(self, u"Recherche des nouvelles vidéos en cours ...",
                "Fermer", 0, 0)
        self.setModal(True)
        self.setWindowTitle(u"Recherche ...")
        self.setCancelButton(None)

    def open(self):
        self.show()

    def close(self):
        self.hide()


class Preferences(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        self.ui.lineEditPlayer.setText(config.player)
        self.ui.lineEditDirUser.setText(config.dir_user)

        for c in config.categories:
            cb = self.findChild(QCheckBox, c.name)
            if cb:
                cb.setCheckState(Qt.Checked)

    def tr(self):
        self.ui.retranslateUi(self)

    @pyqtSlot()
    def on_buttonBox_accepted(self):
        new_dir_user = unicode(self.ui.lineEditDirUser.text())
        if config.dir_user != new_dir_user:
            try:
                os.renames(config.dir_user, new_dir_user)
                config.dir_user = new_dir_user
            except Exception, e:
                r = QMessageBox.critical(self, "Path", "Le chemin %s n'existe pas"%new_dir_user)
                print e
                return
                
        config.player = unicode(self.ui.lineEditPlayer.text())
        config.categories = []
        for cb in self.findChildren(QCheckBox):
            if cb.isChecked():
                cat = DAO.category(unicode(cb.objectName()))
                config.categories.append(cat)
        DAO.commit()
        self.emit(SIGNAL("configChanged(list)"), config.categories)
        self.close()

    @pyqtSlot()
    def on_buttonBox_rejected(self):
        self.close()


class CDL(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.wait = Ui_Wait(self)
        self.downloadsManager = DownloadsManager(self, self.ui.downloadsList)

        global config
        self.videosManager = VideosManager(self.ui.downloadsList,
                self.ui.categoriesList)

        QObject.connect(self.downloadsManager,
                SIGNAL("download_terminated(Download)"),
                self.add_video)

        QObject.connect(self, SIGNAL("refresh(PyQt_PyObject)"),
                self.downloadsManager.refresh_downloads_list)

        QObject.connect(self.ui.downloadsList, SIGNAL("download(Video)"),
                self.downloadsManager.download)

        QObject.connect(self, SIGNAL("construct_downloads(PyQt_PyObject)"),
                self.generate_downloads)

        QObject.connect(self.downloadsManager, SIGNAL("blacklist(Download)"), 
                self.blacklist)

    	QObject.connect(self.ui.wait, SIGNAL("open()"), self.ui.wait.open)
    	QObject.connect(self.ui.wait, SIGNAL("close()"), self.ui.wait.close)

    def showPreferences(self):
        self.pref = Preferences(self)
    	QObject.connect(self.pref, SIGNAL("configChanged(list)"),
                self.videosManager.refresh_categoriesList)
        self.pref.show()

    def blacklist(self, download):
        config.blacklist.append(download)
        DAO.commit()

    def generate_downloads(self, list_data):
        downloads = []
        for d in list_data:
            download = DAO.download(d['url'], d['category'], d['date'])
            downloads.append(download)
        self.emit(SIGNAL("refresh(PyQt_PyObject)"), downloads)

    def add_video(self, download):
        new_video = Video(download.url, download.category, download.name,
                download.date)
        self.videosManager.add_new_video(new_video)


    def refresh_downloads_list(self):
        def threadListNewVideos(self):
            self.ui.wait.emit(SIGNAL("open()"))
            list_data = []
            for c in config.categories:
                list_data.extend(c.find_new_videos_availables(config.blacklist))
            self.emit(SIGNAL("construct_downloads(PyQt_PyObject)"), list_data)
            self.ui.wait.emit(SIGNAL("close()"))

        if self.downloadsManager.nb_downloads_in_progress != 0:
            r = QMessageBox.critical(self, "Veuillez patienter !", 
                    u"Tous les téléchargements ne sont pas terminés, veuillez patienter quelques instants avant de raffraichir cette liste")
            return

        config.blacklist
        config.categories = [DAO.merge(x) for x in config.categories]

        threading.Thread(target=threadListNewVideos, args=[self]).start()

    def quit(self):
        if hasattr(self, 'pref'):
            self.pref.close()
        if hasattr(self, 'downloadsManager'):
            self.downloadsManager.ui_download.close()
        self.close()

    def closeEvent(self, closeEvent):
        self.quit()

    @pyqtSlot()
    def on_pushButtonRefresh_clicked(self):
        self.refresh_downloads_list()

    @pyqtSlot()
    def on_pushButtonDownload_clicked(self):
        self.downloadsManager.download_selected()

    @pyqtSlot()
    def on_pushButtonPlay_clicked(self):
        self.videosManager.play_selected()

    @pyqtSlot()
    def on_pushButtonBlacklist_clicked(self):
        try:
            self.downloadsManager.blacklist_selected()
        except Exception, e:
            print "error while blacklisting video"
            print traceback.format_exc(e)

    @pyqtSlot()
    def on_pushButtonSeen_clicked(self):
        self.videosManager.marked_as_seen(True)

    @pyqtSlot()
    def on_pushButtonNotSeen_clicked(self):
        self.videosManager.marked_as_seen(False)

    @pyqtSignature("")
    def on_pushButtonRemove_clicked(self):
        self.videosManager.remove_selected()

    @pyqtSignature("")
    def on_actionQuit_activated(self):
        self.quit()
    
    @pyqtSignature("")
    def on_actionPreferences_activated(self):
        self.showPreferences()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CDL()
    window.show()
    ret = app.exec_()
    app.closeAllWindows()
    window = None # FIX Segmentation Fault
    sys.exit(ret)

