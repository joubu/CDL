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
from modele import Video, Category
from DAO import DAO



class VideosList(QTableView):
    def __init__(self, category, parent=None):
        QTableView.__init__(self, parent)

        self.model = VideosModel(self)
        self.setModel(self.model)

        vh = self.verticalHeader()
        vh.setVisible(False)
        hh = self.horizontalHeader()
        hh.setMovable(True)
        hh.setResizeMode(QHeaderView.ResizeToContents)
        hh.setVisible(True)
        self.resizeColumnsToContents() 

        self.player = None

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSortingEnabled(True)

    def clear(self):
        self.model.clear()

    def add(self, video):
        self.model.add(video)
        self.resizeColumnsToContents() 

    def remove(self, video):
        self.model.remove(video)
        self.resizeColumnsToContents() 

    def currentVideo(self):
        indexes = self.selectedIndexes()
        index = indexes[0]
        return self.model.datas[index.row()]

    def refresh(self, videos):
        self.clear()
        for video in videos:
            self.add(video)

    def marked_as_seen(self, seen):
        indexes = self.selectedIndexes()
        index = indexes[0]
        v = self.model.datas[index.row()]
        v.marked_as_seen(seen)
        
        index = self.model.createIndex(index.row(), 3)
        self.model.emit(SIGNAL("dataChanged(PyQt_PyObject, PyQt_PyObject)"),index, index) 

    def currentChanged(self, i, j):
        self.emit(SIGNAL("selectionChanged(PyQt_PyObject)"), self)
        

class VideosModel(QAbstractTableModel):
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self.hHeaderData = ["Name", "Date", "Length", "Seen"]
        self.vHeaderData = []
        self.scroll = parent.verticalScrollBar()
        self.sort_map = {
                0: 'name',
                1: 'date',
                2: 'length',
                3: 'seen'}
        self.sorting_column = 0
        self.datas = []

    def rowCount(self, parent):
        return len(self.datas)

    def columnCount(self, parent):
        return len(self.hHeaderData)

    def data(self, index, role):
        if not index.isValid(): 
            return QVariant()
        elif role == Qt.ToolTipRole:
            return QString(self.datas[index.row()].description)
        elif role == Qt.DisplayRole:
            if index.column() == 0:
                return QString(self.datas[index.row()].name)
            elif index.column() == 1:
                return QString(self.datas[index.row()].date)
            elif index.column() == 2:
                return QString(unicode(self.datas[index.row()].length))
            elif index.column() == 3:
                seen = "non"
                if self.datas[index.row()].seen == True:
                    seen = "oui"
                return QString(seen)
        else:
            return QVariant()

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            return QVariant(self.hHeaderData[section])
        elif orientation == Qt.Vertical:
            return QVariant()

        return QVariant()

    def clear(self):
        self.removeRows(0, len(self.datas))
        self.datas = []

    def removeRows(self, position, rows, parent=QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        self.vHeaderData[position:position+rows] = []
        self.endRemoveRows()
        return True

    def insertRows(self, position, rows, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        self.vHeaderData.append(len(self.datas))
        self.endInsertRows()
        return True

    def sort(self, column, order = Qt.AscendingOrder):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.datas = sorted(self.datas, key=attrgetter(self.sort_map[column]))
        if order == Qt.DescendingOrder:
            self.datas.reverse()
        self.emit(SIGNAL("layoutChanged()"))

    def add(self, video):
        self.insertRows(0, 1)
        self.datas.append(video)
        self.sort(self.sorting_column)
        DAO.commit()

    def remove(self, video):
        i = self.datas.index(video)
        self.removeRows(i, 1)
        self.datas.remove(video)
        video.delete()
        DAO.commit()


class CategoryGroupBox(QGroupBox):
    def __init__(self, parent=None):
        QGroupBox.__init__(self, parent)
        self.setCheckable(True)
        self.setChecked(True)

class CategoriesList(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.categoriesGB = []
        self.listTVChildren = []
        self.listTVActives = []
        self.currentSelection = None
        self.first = True

    def refresh_all(self, categories):
        if self.first:
            self.categoriesGB = self.findChildren(CategoryGroupBox)
            self.first = False

        self.listTVChildren = []
        self.listTVActives = []
        for c in self.categoriesGB:
            listCategory = c.findChildren(VideosList)
            if len(listCategory) == 0:
                continue
            listCategory = listCategory[0]

            QObject.disconnect(listCategory, SIGNAL("selectionChanged(PyQt_PyObject)"), 
                    self.selectionChanged)
            QObject.connect(listCategory, SIGNAL("selectionChanged(PyQt_PyObject)"), 
                    self.selectionChanged)

            QObject.disconnect(listCategory, SIGNAL("activated(PyQt_PyObject)"),
                    self.play_requested)
            QObject.connect(listCategory, SIGNAL("activated(PyQt_PyObject)"),
                    self.play_requested)

            try: listCategory.doubleClicked.disconnect()
            except Exception: pass
            listCategory.doubleClicked.connect(self.play_requested)

            c.setVisible(False)
            for cat in categories:
                if c.objectName() == cat.name:
                    c.setVisible(True)
                    self.listTVActives.append(listCategory)
                    listCategory.clear()
                    for v in cat.videos:
                        listCategory.add(v)

    def play_requested(self, index):
        v = self.videoSelected()
        self.emit(SIGNAL("play(PyQt_PyObject)"), v)

    def add(self, video):
        categoryGB = self.findChild(CategoryGroupBox, video.category.name)
        catTV = categoryGB.findChildren(VideosList)
        if len(catTV) == 0:
            return
        catTV[0].add(video)

    def remove(self, video):
        categoryGB = self.findChild(CategoryGroupBox, video.category.name)
        catTV = categoryGB.findChildren(VideosList)
        if len(catTV) == 0:
            return
        catTV[0].remove(video)

    def videoSelected(self):
        if self.currentSelection == None:
            return None
        return self.currentSelection.currentVideo()


    def selectionChanged(self, listCategory):
        if id(self.currentSelection) == id(listCategory):
            return
        self.currentSelection = listCategory
        for c in self.listTVActives:
            if id(c) != id(self.currentSelection):
                c.clearSelection()

    def marked_as_seen_selected(self, seen):
        self.currentSelection.marked_as_seen(seen)


class VideosManager(QObject):
    def __init__(self, listAvailables_ui, categoriesList_ui):
        QObject.__init__(self)
        self.ui_categoriesList = categoriesList_ui
        self.refresh_categoriesList(DAO.categories())

        QObject.connect(self.ui_categoriesList, SIGNAL("play(PyQt_PyObject)"), 
                self.play)

    def add_new_video(self, video):
        video.length = self.calcul_length(video)
        self.ui_categoriesList.add(video)

    def calcul_length(self, video):
        try:
            d = gst.parse_launch("filesrc name=source ! decodebin2 ! fakesink")
            source = d.get_by_name("source")
            source.set_property("location", video.path)
            d.set_state(gst.STATE_PLAYING)
            d.get_state()
            format = gst.Format(gst.FORMAT_TIME)
            duration = d.query_duration(format)[0]
            d.set_state(gst.STATE_NULL)
            length = datetime.timedelta(seconds=(duration / gst.SECOND))
            return unicode(length)
        except Exception, e:
            return unicode('-1')

    def refresh_categoriesList(self, categories):
        self.ui_categoriesList.refresh_all(categories)

    def play_selected(self, index=None):
        v = self.ui_categoriesList.videoSelected()
        self.play(v)

    def play(self, video):
        if not video:
            return
        playerProcess = PlayerProcess(DAO.player(), video)
        playerProcess.start()
        video.marked_as_seen(True)

    def remove_selected(self):
        v = self.ui_categoriesList.videoSelected()
        if v:
            v.rm()
            self.ui_categoriesList.remove(v)

    def marked_as_seen(self, seen=True):
        video = self.ui_categoriesList.videoSelected()
        video.marked_as_seen(seen)
        self.ui_categoriesList.marked_as_seen_selected(seen)
        DAO.commit()



class PlayerProcess(QProcess):
    def __init__(self, player, video, parent=None):
        QProcess.__init__(self, parent)
        self.cmd = "%s %s" % (player, video.path)

    def start(self):
        self.startDetached(self.cmd)
