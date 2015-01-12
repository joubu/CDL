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
#debug = True


class DownloadProcess(QProcess):
    def __init__(self, parent=None):
        QProcess.__init__(self, parent)

        new_env = QProcess.systemEnvironment()
        self.setEnvironment(new_env)
        self.total_duration_s = 0
        self.prev_duration = None
        self.prev_time = None

        self.setReadChannel(QProcess.StandardError)

        QObject.connect(self, SIGNAL("readyRead()"),
                self.tryReadPercent)
        QObject.connect(self, SIGNAL("finished(int, QProcess::ExitStatus)"), self.finished)

    def tryReadPercent(self):
        line = self.readAll()
        # format: frame=  XXX fps= XX q=-1.0 Lsize=    XXXXkB time=00:XX:XX.XX bitrate= XXX.Xkbits/s
        percent = 0
        duration_s = self.total_duration_s;
        rate_kb_s = 0
        matches = re.findall("Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})", line)
        if len(matches) > 0:
            duration_s = int(matches[0][2]) + int(matches[0][1]) * 60 + int(matches[0][0]) * 3600
            self.total_duration_s = duration_s
        else:
            matches = re.findall("time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})\s+bitrate=\s+.*$", line)
            if len(matches) > 0:
                duration_s = int(matches[0][2]) + int(matches[0][1]) * 60 + int(matches[0][0]) * 3600
                percent = int(float(duration_s * 100 / self.total_duration_s))

        if not self.prev_duration:
            self.prev_duration = duration_s
        if not self.prev_time:
            self.prev_time = time.time()

        rate_kb_s = (duration_s - self.prev_duration) / (time.time() - self.prev_time)
        if rate_kb_s < 0:
            rate_kb_s = 0

        self.prev_duration = duration_s
        self.prev_time = time.time()

        if percent >= 0 and percent <= 100:
            self.emit(SIGNAL("majDownloadBar(PyQt_PyObject, PyQt_PyObject)"), percent, rate_kb_s)

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
        QObject.connect(self.layout.pushButton, SIGNAL("clicked()"), 
                self.stop)

        QObject.connect(self.process, SIGNAL("majDownloadBar(PyQt_PyObject, PyQt_PyObject)"),
                self.majProgressBar)
        QObject.connect(self.process, SIGNAL("stoppedByEnd()"), 
                self.stoppedByEnd)
        QObject.connect(self.process, SIGNAL("stoppedByUser()"), 
                self.stoppedByUser)
        QObject.connect(self.process, SIGNAL("stoppedByError()"),
                self.stoppedByError)

    def majProgressBar(self, percent, rate_kb_s = 0):
        rate_label = self.download.description + " %p%"
        rate_label += "(%.1f" % rate_kb_s + " kB/s)"
        self.layout.progressBar.setFormat(rate_label)
        self.layout.progressBar.setValue(percent)

    def stoppedByEnd(self):
        self.emit(SIGNAL("terminated(PyQt_PyObject, PyQt_PyObject)"), self, 0)

    def stoppedByUser(self):
        self.emit(SIGNAL("terminated(PyQt_PyObject, PyQt_PyObject)"), self, 1)

    def stoppedByError(self):
        self.emit(SIGNAL("terminated(PyQt_PyObject, PyQt_PyObject)"), self, 1)

    def start(self):
        cmd = "ffmpeg" + " -i %s -codec copy %s" % \
                (self.download.url, self.download.path)

        if debug:
            cmd = "python fake.py"

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

        return QVariant(self.datas[index.row()].description)

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
        progressBar.setFormat(download.description + " (%p%)")
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
        QObject.connect(self.ui_downloads_list, SIGNAL("activated(PyQt_PyObject)"),
                    self.download_selected)

        self.ui_downloads_list.doubleClicked.connect(self.download_selected)

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
        layout.progressBar.setToolTip(download.description)

        self.nb_downloads_in_progress += 1

        download = DownloadManager(layout, download)
        download.start()

        QObject.connect(self, SIGNAL("deleteLayout(PyQt_PyObject)"), 
                self.ui_download.deleteLayout)

        QObject.connect(download, SIGNAL("terminated(PyQt_PyObject, PyQt_PyObject)"), 
                self.downloadTerminated)

        self.downloads.append(download)
        self.ui_download.show()

    def downloadTerminated(self, download, exitCode):
        if exitCode == 0:
            self.emit(SIGNAL("download_terminated(PyQt_PyObject)"), download.download)
            self.delete_download(download.download)
        else:
            download.download.rm()
            self.downloads.remove(download)

        self.emit(SIGNAL("deleteLayout(PyQt_PyObject)"), download.layout)

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
            self.emit(SIGNAL("blacklist(PyQt_PyObject)"), d)
            self.ui_downloads_list.remove(d, delete=False)

    def killAll(self):
        for d in self.downloads:
            d.process.stop()

