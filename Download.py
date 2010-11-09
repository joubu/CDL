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
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from modele import Download
from DAO import DAO

debug = False


class DownloadProcess(QProcess):
    def __init__(self, parent=None):
        QProcess.__init__(self, parent)
        
        new_env = QProcess.systemEnvironment()
        self.setEnvironment(new_env)

        self.setReadChannel(QProcess.StandardError)

        QObject.connect(self, SIGNAL("readyRead()"),
                self.tryReadPourcent)
        QObject.connect(self, SIGNAL("finished(int, QProcess::ExitStatus)"), self.finished)

    def tryReadPourcent(self):
        line = self.readAll()
        # format : 5976.281 kB / 56.36 sec (40.3%)
        r = re.findall("(\d*).{0,1}\d* kB / \d*.{0,1}\d* sec \((\d{1,3}.{0,1}\d{0,1})%\)", line)
        pourcent = None
        if len(r) > 0:
            ok = True
            (size, ok) = r[0][0].toInt()
            (pourcent, ok) = r[0][1].toFloat()
        if pourcent >= 0 and pourcent <= 100:
            self.emit(SIGNAL("majDownloadBar(float, int)"), pourcent, size)

    def finished(self, exitCode, exitStatus):
        if exitCode == 0 and exitStatus == 0: # Fin normale du process
            self.emit(SIGNAL("stoppedByEnd()"))
        elif exitCode == 0 and exitStatus == 1: # Arrêt demandé par user
            self.emit(SIGNAL("stoppedByUser()"))
        elif exitCode == 1 and exitStatus == 0: # Reprise après arrêt
            self.emit(SIGNAL("stoppedByError()"))
        else:
            self.emit(SIGNAL("stoppedByError()")) # Blocage pendant le téléchargement

    def stop(self):
        self.kill()


class DownloadHLayout(QHBoxLayout):
    def __init__(self, progressBar, pushButton, parent=None):
        QHBoxLayout.__init__(self, parent)
        self.progressBar = progressBar
        self.pushButton = pushButton

        self.progressBar.setProperty("value", 0)
        self.pushButton.setMinimumSize(QSize(0, 42))
        self.pushButton.setStyleSheet(
                "background-image: url(\":/*.png/resources/button_cancel.png\");\n"
                "background-repeat: no-repeat;\n"
                "background-position: center;")
        self.pushButton.setText("")
        self.pushButton.setFlat(True)

        self.addWidget(progressBar)
        self.addWidget(pushButton)

class DownloadManager(QObject):
    def __init__(self, layout, download):
        QObject.__init__(self)
        self.process = DownloadProcess()
        self.layout = layout
        self.download = download
        self.prev_size = None
        self.prev_time = None
        QObject.connect(self.layout.pushButton, SIGNAL("clicked()"), 
                self.stop)
    
        QObject.connect(self.process, SIGNAL("majDownloadBar(float, int)"),
                self.majProgressBar)
        QObject.connect(self.process, SIGNAL("stoppedByEnd()"), 
                self.stoppedByEnd)
        QObject.connect(self.process, SIGNAL("stoppedByUser()"), 
                self.stoppedByUser)
        QObject.connect(self.process, SIGNAL("stoppedByError()"),
                self.stoppedByError)

    def majProgressBar(self, pourcent, size):
        if not self.prev_size:
            self.prev_size = size
        if not self.prev_time:
            self.prev_time = time.time()
        
        rate = (size - self.prev_size) / (time.time() - self.prev_time)
        self.layout.progressBar.setFormat(self.download.name + " %p% (" + "%.1f" % rate + " ko/s)")
        self.layout.progressBar.setValue(pourcent)

        self.prev_size = size
        self.prev_time = time.time()

    def stoppedByEnd(self):
        self.emit(SIGNAL("terminated(DownloadProcess, int)"), self, 0)

    def stoppedByUser(self):
        self.emit(SIGNAL("terminated(DownloadProcess, int)"), self, 1)

    def stoppedByError(self):
        self.emit(SIGNAL("terminated(DownloadProcess, int)"), self, 1)

    def start(self):
        cmd = "/usr/bin/flvstreamer -er %s -o %s" % \
                (self.download.url, self.download.path)
        
        self.process.start(cmd)

    def stop(self):
        if self.process.state() != QProcess.NotRunning:
            self.process.stop()


class DownloadsModel(QAbstractListModel):
    def __init__(self, parent, data):
        QAbstractListModel.__init__(self, parent)
        self.hHeaderData = []
        self.vHeaderData = []

        self.datas = []
        for d in data:
            self.add(d)

    def rowCount(self, parent):
        return len(self.datas)

    def columnCount(self, parent):
        return 1

    def clear(self):
        DAO.commit()
        for i in xrange(len(self.datas)):
            self.remove(self.datas[-1])
        DAO.commit()

    def data(self, index, role):
        if not index.isValid(): 
            return QVariant()
        elif role == Qt.ToolTipRole:
            return QString(self.datas[index.row()].url)
        elif role != Qt.DisplayRole: 
            return QVariant()

        return QVariant(self.datas[index.row()].name)

    def headerData(self, section, orientation, role):
        return QVariant()

    def add(self, download, parent=QModelIndex()):
        if not DAO.already_downloaded(download.url):
            self.beginInsertRows(parent, 0, 0)
            download = DAO.merge(download)
            self.datas.append(download)
            self.endInsertRows()
            return True

    def remove(self, download, delete=True, parent=QModelIndex()):
        self.beginRemoveRows(parent, 0, len(self.datas))
        self.datas.pop(self.datas.index(download))
        self.endRemoveRows()
        if delete:
            download.delete()
        return True



class Ui_DownloadManager(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.setObjectName("Download")
        self.resize(466, 88)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

    def new_layout(self, download):
        progressBar = QProgressBar(self)
        progressBar.setFormat(download.name + " (%p%)")
        pushButton = QPushButton(self)
        downloadLayout = DownloadHLayout(progressBar, pushButton)
        self.verticalLayout.addLayout(downloadLayout)
        return downloadLayout

    def deleteLayout(self, layout):
        lo = layout.layout()
        while True:
            i=lo.takeAt(0)
            if i is None : break
            i.widget().deleteLater()
            del i

        del lo
        self.verticalLayout.removeItem(layout)
        del layout


class Ui_DownloadManager(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.setObjectName("Download")
        self.resize(466, 88)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

    def new_layout(self, download):
        progressBar = QProgressBar(self)
        progressBar.setFormat(download.name + " (%p%)")
        pushButton = QPushButton(self)
        downloadLayout = DownloadHLayout(progressBar, pushButton)
        self.verticalLayout.addLayout(downloadLayout)
        return downloadLayout

    def deleteLayout(self, layout):
        lo = layout.layout()
        while True:
            i=lo.takeAt(0)
            if i is None : break
            i.widget().deleteLater()
            del i

        del lo
        self.verticalLayout.removeItem(layout)
        del layout

class DownloadsList(QListView):
    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.model = DownloadsModel(parent, DAO.downloads())
        self.setModel(self.model)
        
    def get(self, row):
        return self.model.datas[row]

    def remove(self, download, delete=True):
        self.model.remove(download, delete)

    def selectedDownloads(self):
        indexes = self.selectedIndexes()
        downloads = []
        for i in indexes:
            d = self.get(i.row())
            downloads.append(d)
        return downloads

    def refresh(self, downloads):
        self.model.clear()
        for download in downloads:
            self.model.add(download)
        DAO.commit()



class DownloadsManager(QObject):
    def __init__(self, parent, ui_downloads_list):
        QObject.__init__(self)
        self.nb_downloads_in_progress = 0
        self.ui_download = Ui_DownloadManager(parent)
        self.ui_downloads_list = ui_downloads_list
        self.downloads = []

        QObject.connect(self.ui_download, SIGNAL("killAll()"), self.killAll)
        QObject.connect(self.ui_downloads_list, SIGNAL("activated(QModelIndex)"),
                    self.download_selected)

    def download_selected(self, index=None):
        if index and isinstance(index, QModelIndex):
            d = self.ui_downloads_list.get(index.row())
            self.download(d)
        else:
            for d in self.ui_downloads_list.selectedDownloads():
                self.download(d)

    def download(self, download):
        if download in self.downloads:
            return

        layout = self.ui_download.new_layout(download)
        layout.progressBar.setToolTip(download.name)

        self.nb_downloads_in_progress += 1

        download = DownloadManager(layout, download)
        download.start()
        
        QObject.connect(self, SIGNAL("deleteLayout(object)"), 
                self.ui_download.deleteLayout)

        QObject.connect(download, SIGNAL("terminated(DownloadProcess, int)"), 
                self.downloadTerminated)

        self.downloads.append(download)
        self.ui_download.show()

    def downloadTerminated(self, download, exitCode):
        if exitCode == 0:
            self.emit(SIGNAL("download_terminated(Download)"), download.download)
            self.delete_download(download.download)
        else:
            download.download.rm()
            self.downloads.remove(download)

        self.emit(SIGNAL("deleteLayout(object)"), download.layout)

        self.nb_downloads_in_progress -= 1

        if self.nb_downloads_in_progress < 1:
            self.ui_download.close()

    def refresh_downloads_list(self, downloads):
        self.ui_downloads_list.refresh(downloads)

    def delete_download(self, download):
        self.ui_downloads_list.remove(download)
        DAO.commit()

    def blacklist_selected(self):
        for d in self.ui_downloads_list.selectedDownloads():
            self.emit(SIGNAL("blacklist(Download)"), d)
            self.ui_downloads_list.remove(d, delete=False)

    def killAll(self):
        for d in self.downloads:
            d.process.stop()



