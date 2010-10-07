#!/bin/python
# -*- coding: utf-8 -*-



from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Ui_MainWindow import Ui_MainWindow
from Ui_Preferences import Ui_Preferences
import resources_rc
from xml.dom import minidom
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

import pygst
pygst.require("0.10")
import gst

import datetime

try:
    import sqlite3
except Exception, e:
    print e
    exit(1)

debug = False
#debug = True

VLC_PATH = "/usr/bin/vlc"

# Quit sur CTRL-C
signal.signal(signal.SIGINT, signal.SIG_DFL)

if not os.path.exists('/usr/bin/flvstreamer'):
    print "flvstreamer must be installed"
    exit(1)

class DbConnect:
    def __init__(self):
        self.con = sqlite3.connect('database.db')
        self.cur = self.con.cursor()

    def execute(self, cmd, args=()):
        commit=False 
        try:
            if len(args) == 0:
                r = self.cur.execute(cmd)
            else:
                r = self.cur.execute(cmd, args)
            if commit:
                self.commit()
        except Exception, e:
             print "== ERREUR SQL =="
             print e
             print cmd, args
             print "================"
       
    def executemany(self, cmd, args, commit=False):
        try:
            self.cur.executemany(cmd, args)
            if commit:
                self.commit()
        except Exception, e:
            print e

    def query(self, cmd, args=[]):
        self.execute(cmd, args)
        return self.cur.fetchall()


    def commit(self):
        self.con.commit()

    def quote(self, s):
        return s.replace("'", "''").replace('\\', '\\\\')

    def close(self):
        self.cur.close()

class Category:
    def __init__(self, url, dir_user, name, keywords, create_path=False):
        self.name = str(name)
        self.keywords = str(keywords)
        self.path = os.path.join(str(dir_user), self.name)
        self.url = os.path.join(str(url), self.keywords)

        self.new_videos = []
        self.videos = []
        if create_path and not os.path.exists(self.path):
            try:
                os.makedirs(self.path)
            except Exception, e:
                print "%s ne peut être créé" % self.path
                exit(2)
 
    def __repr__(self):
        return self.name

    def list_new_videos_availables(self, blacklist=list()):
        list_videos = []
        dom = minidom.parse(urllib.urlopen(self.url))
        video_node = dom.getElementsByTagName('VIDEO')
        for vn in video_node:
            date_node_list = vn.getElementsByTagName('DATE')
            rubrique_node_list = vn.getElementsByTagName('RUBRIQUE')
            
            try:
                rubrique = str(rubrique_node_list[0].firstChild.nodeValue.replace(' ', '_'))
            except:
                continue

            debit_node_list = vn.getElementsByTagName('HAUT_DEBIT')

            """
            for dn in date_node_list:
                try:
                    url = str(debit_node_list[0].firstChild.nodeValue)
                    print url
                except:
                    continue
            """

            if date_node_list.length == debit_node_list.length and \
                    rubrique.lower().find(self.name.lower()) > -1:
                for dn in date_node_list:
                    url = str(debit_node_list[0].firstChild.nodeValue)
                    if url in blacklist:
                        continue
                    if url.find('rtmp') > -1:
                        date = str(dn.firstChild.nodeValue)
                        list_videos.append(Video(url, self, date=date))
        return list_videos

class Config:
    def __init__(self):
        global db
        tables = db.query("SELECT name FROM SQLite_Master")
        if len(tables) == 0:
            self.reset()

        self.init_from_DAO()

    def init_from_DAO(self):
        self.dir_user = DAO.dir_user()
        self.url_dl = DAO.url_dl()
        self.player = DAO.player()
        self.categories_availables = DAO.categories_availables(self.url_dl, 
                self.dir_user)
        self.categories = DAO.categories(self.url_dl, self.dir_user)
        for c in self.categories:
            c.videos = DAO.videos(c)
        self.blacklist = DAO.blacklist()

    def save(self):
        DAO.save_config(self)
    
    def reset(self):
        DAO.reset_config()

class DAO:

    @classmethod
    def reset_config(cls):
        global db
        db.execute("CREATE TABLE config(id INTEGER PRIMARY KEY AUTOINCREMENT, dir_user, url, player)")
        db.execute("CREATE TABLE category_available(name, keywords)")
        db.execute("CREATE TABLE category(name)")
        db.execute("CREATE TABLE video(url, category, name, date,\
                length, seen, PRIMARY KEY(url))") #FIXME : if not exist  
        db.execute("CREATE TABLE blacklist(url)")

        db.execute("INSERT INTO config(dir_user, url, player) VALUES (?, ?, ?)",
                (os.path.join(os.path.expanduser("~"), 'Canal+DL'),
                    'http://www.canalplus.fr/rest/bootstrap.php?/bigplayer/search/',
                    'vlc'))
        db.executemany("INSERT INTO category_available(name, keywords) VALUES (?, ?)",
                (("discrete", "action+discrete"),
                 ("boite", "boite+question"), 
                 ("boucan", "boucan"),
                 ("guignols", "les+guignols"), 
                 ("grand", "grand+journal"),
                 ("groland", "groland"), 
                 ("petit", "petit+journal"),
                 ("petite", "petite+semaine"), 
                 ("matinale", "la+matinale"),
                 ("meteo", "la+meteo"), 
                 ("pepites", "pepites+net"),
                 ("sav", "sav"), 
                 ("salut", "salut+les+terriens"), 
                 ("zapping", "zapping")
                 ))

        db.executemany("INSERT INTO category(name) VALUES (?)",
                (("petit",),
            ("zapping", )))
        db.commit()
    @classmethod
    def save_config(cls, config):
        global db
        db.execute("INSERT INTO config(dir_user, url, player) VALUES (?, ?, ?)",
                (str(config.dir_user), str(config.url_dl), str(config.player)))
        db.execute("DELETE FROM category")
        for c in config.categories:
            db.execute("INSERT INTO category(name) VALUES (?)", (str(c.name), ))

        db.commit()

    @classmethod
    def add_video(cls, video):
        global db

        seen = 0
        if video.seen == True:
            seen = 1
            
        db.execute("INSERT INTO video(url, category, name, date, length, seen) \
                VALUES(?, ?, ?, ?, ?, ?)", 
                (video.url, video.category.name, video.name,
                    video.date, video.length, seen))
        db.commit()

    @classmethod
    def update_video(cls, video):
        global db

        seen = 0
        if video.seen == True:
            seen = 1

        db.execute("UPDATE video SET category=?, name=?, date=?, \
                length=?, seen=? WHERE url=?", 
                (video.category.name, video.name,
                    video.date, video.length, seen, video.url))
        db.commit()

    @classmethod
    def remove_video(cls, video):
        global db

        db.execute("DELETE FROM video WHERE url=?", (video.url,))
        db.commit()

    @classmethod
    def blacklist_video(cls, video):
        global db
        db.execute("INSERT INTO blacklist(url) VALUES(?)", (video.url,))
        db.commit()

    @classmethod
    def videos(cls, category):
        global db
        result = db.query("SELECT url, name, date, length, seen FROM \
                video WHERE category=? AND url NOT IN (SELECT url FROM blacklist)",
                (category.name, ))
        videos = []
        for r in result:
            url = r[0]
            name = r[1]
            date = r[2]
            length = r[3]
            seen = r[4]
            v = Video(url, category, name=name,
                date=date, length=length, seen=seen)
            videos.append(v)

        return videos

    @classmethod
    def video_exist(cls, video):
        global db
        result = db.query("SELECT count(url) FROM video WHERE url=?",
                (video.url, ))
        
        if result[0][0] > 0:
            return True

        return False

    @classmethod
    def blacklist(cls):
        global db
        result = db.query("SELECT url FROM blacklist")
        urls = []
        for r in result:
            urls.append(r[0])

        return urls

    @classmethod
    def dir_user(cls):
        global db
        r = db.query("SELECT dir_user FROM config ORDER BY id DESC LIMIT 1")
        return r[0][0]

    @classmethod
    def url_dl(cls):
        global db
        r = db.query("SELECT url FROM config ORDER BY id DESC LIMIT 1")
        return r[0][0]

    @classmethod
    def player(cls):
        global db
        r = db.query("SELECT player FROM config ORDER BY id DESC LIMIT 1")
        return r[0][0]
        
    @classmethod
    def category(cls, url_dl, dir_user, name):
        global db
        result = db.query("SELECT keywords FROM category_available \
                    WHERE name=?", (str(name), ))

        if not len(result) > 0:
            return None
        
        return Category(url_dl, dir_user, name, keywords=result[0][0],
                create_path=True)

    @classmethod
    def categories_availables(cls, url_dl, dir_user):
        global db
        result = db.query("SELECT name, keywords FROM \
            category_available")
        categories = []
        for r in result:
            name = r[0]
            keywords = r[1]
            c = Category(url_dl, dir_user, name, keywords)
            categories.append(c)

        return categories

    @classmethod
    def categories(cls, url_dl, dir_user):
        global db
        result = db.query("SELECT c.name, ca.keywords FROM category c, \
                    category_available ca WHERE c.name=ca.name")
        categories = []
        for r in result:
            name = r[0]
            keywords = str(r[1])
            c = Category(url_dl, dir_user, name, keywords, create_path=True)
            categories.append(c)

        return categories


class Video():
    def __init__(self, url, category, name=None, date=None,
                    length=None, seen=False):

        self.url = url
        self.category = category
        self.date = date
        
        if name == None:
            filename = url.split('/')[-1]
            try:
                matches = re.compile("(.*)_CAN_([0-9]*)_video_H\.flv").findall(filename)
                if len(matches) > 0:
                    self.name = "%s_%s.flv" % (matches[0][0], matches[0][1])
                else:
                    matches = re.compile("(.*)_([0-9]*)_AUTO_.*_video_H\.flv").findall(filename)
                    self.name = "%s_%s.flv" % (matches[0][0], matches[0][1])
                    
            except:
                self.name = filename
        else:
            self.name = name

        self.path = os.path.join(self.category.path, self.name)

        if length == None:
            self.length = 0
        else:
            self.length = length

        self.seen = seen


    def get_length(self):
        try:
            d = gst.parse_launch("filesrc name=source ! decodebin2 ! fakesink")
            source = d.get_by_name("source")
            source.set_property("location", self.path)
            d.set_state(gst.STATE_PLAYING)
            d.get_state()
            format = gst.Format(gst.FORMAT_TIME)
            duration = d.query_duration(format)[0]
            d.set_state(gst.STATE_NULL)
            length = datetime.timedelta(seconds=(duration / gst.SECOND))
            return str(length)
        except Exception, e:
            return str(-1)


    def __repr__(self):
        return u"Video [%s] %s\t%s" % (self.category, self.url, self.date)

    def save(self):
        self.length = self.get_length()
        DAO.add_video(self)

    def rm(self):
        try:
            os.remove(self.path)
        except:
            pass
        finally:
            DAO.remove_video(self)

    def blacklist(self):
        DAO.blacklist_video(self)

    def marked_as_seen(self, seen):
        self.seen = seen
        DAO.update_video(self)

#       SUBPROCESS AVEC RECUP DE LA SORTIE
#        self.bla = QObject()
#        QObject.connect(self.bla, SIGNAL("pourcentageFichier(int)"), self.bid)
#
#        cmd = "/usr/bin/flvstreamer -er %s -o %s" % \
#                (self.url, self.path)
#        cmd = str(cmd)
#
#        arguments = shlex.split( cmd )
#
#        try:
#            self.process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#            stdout = self.process.stdout
#            stdout_fd = stdout.fileno()
#            stdout_flags = fcntl.fcntl(stdout_fd, fcntl.F_GETFL)
#            fcntl.fcntl(stdout_fd, fcntl.F_SETFL, stdout_flags | os.O_NDELAY)
#            while(self.process.poll() == None):
#                if (stdout_fd in select.select([stdout_fd], [], [])[0]):
#                    ligne = stdout.read()
#                    if ligne:
#                        pourcent = re.findall("(\d{1,3}\.{0,1}\d{0,1})%", ligne)
#                        print "pourcent=%s"%pourcent
#                        if len(pourcent) > 0:
#                            pourcent = int(float(pourcent[-1]))
#                            self.process.emit(QtCore.SIGNAL("pourcentageFichier(int)"), pourcent)
#                time.sleep(1)
#
#        except Exception, e:
#            traceback.format_exc(e)
#            exit(2)
#        

def get_list_new_videos(config):
    videos = []
    for c in config.categories:
        if debug:
            print u"categorie %s trouvée"%c
        try:
            list_videos = c.list_new_videos_availables(config.blacklist)
            c.new_videos = list_videos
            videos.extend(list_videos)
        except Exception, e:
            print traceback.format_exc(e)
            exit(1)

    return videos
    
class TableViewCategory(QTableView):
    def __init__(self, parent=None):
        QTableView.__init__(self, parent)

        self.model = ListMyVideosModel(self)
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
        return self.model.tabData[index.row()]

    def refresh(self, liste):
        self.clear()
        for video in liste:
            self.add(video)

    def marked_as_seen(self, seen):
        indexes = self.selectedIndexes()
        index = indexes[0]
        v = self.model.tabData[index.row()]
        v.marked_as_seen(seen)
        
        index = self.model.createIndex(index.row(), 3) # FIXME BURK !
        self.model.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index, index) 

    def currentChanged(self, i, j):
        self.emit(SIGNAL("selectionChanged(TableViewCategory)"), self)
        

class ListMyVideosModel(QAbstractTableModel):
    def __init__(self, parent):
        QAbstractTableModel.__init__(self, parent)
        self.hHeaderData = ["Name", "Date", "Length", "Seen"]
        self.vHeaderData = []
        self.tabData = []
        self.scroll = parent.verticalScrollBar()

    def rowCount(self, parent):
        return len(self.tabData)

    def columnCount(self, parent):
        return len(self.hHeaderData)

    def data(self, index, role):
        if not index.isValid(): 
            return QVariant()
        elif role == Qt.ToolTipRole:
            return QVariant()
        elif role == Qt.DisplayRole:
            if index.column() == 0:
                return QString(self.tabData[index.row()].name)
            elif index.column() == 1:
                return QString(self.tabData[index.row()].date)
            elif index.column() == 2:
                return QString(self.tabData[index.row()].length)
            elif index.column() == 3:
                seen = "non"
                if self.tabData[index.row()].seen == True:
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
        self.removeRows(0, len(self.tabData))
        self.tabData = []

    def removeRows(self, position, rows, parent=QModelIndex()):
        self.beginRemoveRows(parent, position, position + rows - 1)
        self.vHeaderData[position:position+rows] = []
        self.endRemoveRows()
        return True

    def insertRows(self, position, rows, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        self.vHeaderData.append(len(self.tabData))
        self.endInsertRows()
        return True

    def add(self, video):
        self.insertRows(0, 1)
        self.tabData.append(video)
        self.sort(0)

    def remove(self, video):
        i = self.tabData.index(video)
        self.removeRows(i, 1)
        self.tabData.remove(video)


class CategoryGroupBox(QGroupBox):
    def __init__(self, parent=None):
        QGroupBox.__init__(self, parent)
        #self.setFlat(False)
        self.setCheckable(True)
        self.setChecked(True)


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
        r = re.findall("(\d{1,3}\.{0,1}\d{0,1})%", line)
        pourcent = None
        if len(r) > 0:
            pourcent = int(float(r[-1]))
        if pourcent >= 0 and pourcent <= 100:
            self.emit(SIGNAL("majDownloadBar(int)"), pourcent)

    def finished(self, exitCode, exitStatus):
        if exitCode == 0 and exitStatus == 0: # Fin normale du process
            self.emit(SIGNAL("stoppedByEnd()"))
        elif exitCode == 0 and exitStatus == 1: # Arrêt demandé par user
            self.emit(SIGNAL("stoppedByUser()"))
        elif exitCode == 1 and exitStatus == 0: # Reprise après arrêt
            self.emit(SIGNAL("stoppedByError()"))
        else:
            self.emit(SIGNAL("stoppedByError()"))
            print "?????????????????"
            print "exit code=%s exitStatus=%s" % (exitCode, exitStatus)
            print "?????????????????"

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

    def setValue(self, value):
        self.progressBar.setValue(value)


class Download(QObject):
    def __init__(self, process, layout):
        QObject.__init__(self)
        self.process = process
        self.layout = layout

        QObject.connect(self.layout.pushButton, SIGNAL("clicked()"), 
                self.stop)
    
        QObject.connect(self.process, SIGNAL("majDownloadBar(int)"),
                self.majProgressBar)
        QObject.connect(self.process, SIGNAL("stoppedByEnd()"), 
                self.stoppedByEnd)
        QObject.connect(self.process, SIGNAL("stoppedByUser()"), 
                self.stoppedByUser)
        QObject.connect(self.process, SIGNAL("stoppedByError()"),
                self.stoppedByError)

    def majProgressBar(self, pourcent):
        self.layout.progressBar.setValue(pourcent)

    def stoppedByEnd(self):
        self.emit(SIGNAL("terminated(DownloadProcess, int)"), self, 0)

    def stoppedByUser(self):
        self.emit(SIGNAL("terminated(DownloadProcess, int)"), self, 1)

    def stoppedByError(self):
        self.emit(SIGNAL("terminated(DownloadProcess, int)"), self, 1)

    def stop(self):
        if self.process.state() != QProcess.NotRunning:
            self.process.stop()

class ListAvailablesVideosModel(QAbstractListModel):
    def __init__(self, parent):
        QAbstractListModel.__init__(self, parent)
        self.hHeaderData = []
        self.vHeaderData = []
        self.tabData = []

    def rowCount(self, parent):
        return len(self.tabData)

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid(): 
            return QVariant()
        elif role == Qt.ToolTipRole:
            return QString(self.tabData[index.row()].url)
        elif role != Qt.DisplayRole: 
            return QVariant()

        return QVariant(self.tabData[index.row()].name)

    def headerData(self, section, orientation, role):
        return QVariant()

    def add(self, video, parent=QModelIndex()):
        self.beginInsertRows(parent, 0, 0)
        self.tabData.append(video)
        self.endInsertRows()
        #self.tabData = sorted(self.tabData, key=lambda video: video.name)
        #self.sort(0)
        return True

    def remove(self, video, parent=QModelIndex()):
        self.beginRemoveRows(parent, 0, len(self.tabData))
        self.tabData.pop(self.tabData.index(video))
        self.endRemoveRows()
        return True

class PlayerProcess(QProcess):
    def __init__(self, player, video, parent=None):
        QProcess.__init__(self, parent)
        self.cmd = "%s %s" % (player, video.path)

    def start(self):
        self.startDetached(self.cmd)


class Ui_DownloadManager(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.setObjectName("Download")
        self.resize(466, 88)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

    def new_layout(self):
        progressBar = QProgressBar(self)
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


    # FIXME Comment dissocier un widget.close() d'une fermeture par la croix ?
    """
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'TITRE ?',
            "Voulez-vous réellement fermer la fenêtre des\
            téléchargements ? \n Cette action supprimera tous les\
            téléchargements en cours !", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.emit(SIGNAL("killAll()"))
            event.accept()
        else:
            event.ignore()
    """

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


db = DbConnect()

class Preferences(QWidget):
    def __init__(self, config, parent):
        QWidget.__init__(self)
        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        self.config = config
        self.ui.lineEditPlayer.setText(config.player)
        self.ui.lineEditDirUser.setText(config.dir_user)

        for c in self.config.categories:
            cb = self.findChild(QCheckBox, c.name)
            if cb:
                cb.setCheckState(Qt.Checked)

    def tr(self):
        self.ui.retranslateUi(self)

    @pyqtSlot()
    def on_buttonBox_accepted(self):
        new_dir_user = str(self.ui.lineEditDirUser.text())
        if self.config.dir_user != new_dir_user:
            try:
                os.renames(self.config.dir_user, new_dir_user)
                self.config.dir_user = new_dir_user
            except Exception, e:
                r = QMessageBox.critical(self, "Path", "Le chemin %s n'existe pas"%new_dir_user)
                print e
                return
                
        self.config.player = self.ui.lineEditPlayer.text()
        self.config.categories = []
        for cb in self.findChildren(QCheckBox):
            if cb.isChecked():
                cat = DAO.category(self.config.url_dl, self.config.dir_user,
                        cb.objectName())
                cat.videos = DAO.videos(cat)
                self.config.categories.append(cat)
        self.config.save()
        self.emit(SIGNAL("configChanged(list)"), self.config.categories)
        self.close()

    @pyqtSlot()
    def on_buttonBox_rejected(self):
        self.close()

class FileViewer(QFrame):
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
            listCategory = c.findChildren(TableViewCategory)
            if len(listCategory) == 0:
                continue
            listCategory = listCategory[0]

            QObject.disconnect(listCategory, SIGNAL("selectionChanged(TableViewCategory)"), 
                    self.selectionChanged)
            QObject.connect(listCategory, SIGNAL("selectionChanged(TableViewCategory)"), 
                    self.selectionChanged)

            QObject.disconnect(listCategory, SIGNAL("activated(QModelIndex)"),
                    self.play_requested)
            QObject.connect(listCategory, SIGNAL("activated(QModelIndex)"),
                    self.play_requested)


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
        self.emit(SIGNAL("play(Video)"), v)

    def add(self, video):
        categoryGB = self.findChild(CategoryGroupBox, video.category.name)
        catTV = categoryGB.findChildren(TableViewCategory)
        if len(catTV) == 0:
            return
        catTV[0].add(video)

    def remove(self, video):
        categoryGB = self.findChild(CategoryGroupBox, video.category.name)
        catTV = categoryGB.findChildren(TableViewCategory)
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


class DownloadManager(QObject):
    def __init__(self, parent, ui_listAvailables):
        QObject.__init__(self)
        self.videos = {}
        self.nb_downloads_in_progress = 0
        self.ui_download = Ui_DownloadManager(parent)
        self.ui_listAvailables = ui_listAvailables

        QObject.connect(self.ui_download, SIGNAL("killAll()"), self.killAll)
    
    def download_selected(self):
        for v in self.ui_listAvailables.selectedVideos():
            self.download(v)

    def download(self, video):
        if video in self.videos.values():
            return

        cmd = "/usr/bin/flvstreamer -er %s -o %s" % \
                (video.url, video.path)

        if debug:
            cmd = "python fake.py"

        layout = self.ui_download.new_layout()
        layout.progressBar.setToolTip(video.name)

        self.nb_downloads_in_progress += 1
        process = DownloadProcess()
        process.start(cmd)

        download = Download(process, layout)
        
        QObject.connect(self, SIGNAL("deleteLayout(object)"), 
                self.ui_download.deleteLayout)

        QObject.connect(download, SIGNAL("terminated(DownloadProcess, int)"), 
                self.downloadTerminated)

        self.videos[download] = video
        self.ui_download.show()

    def downloadTerminated(self, download, exitCode):
        if exitCode == 0:
            self.videos[download].save()
            self.emit(SIGNAL("download_terminated(Video)"), self.videos[download])
        else:
            v = self.videos.pop(download)
            v.rm()

        self.emit(SIGNAL("deleteLayout(object)"), download.layout)

        self.nb_downloads_in_progress -= 1

        if self.nb_downloads_in_progress < 1:
            self.ui_download.close()

    def refresh_availables(self, videos):
        self.ui_listAvailables.refresh(videos)

    def killAll(self):
        for d in self.videos.keys():
            d.stop()

            
class VideoManager(QObject):
    def __init__(self, listAvailables_ui, fileViewer_ui, config):
        QObject.__init__(self)
        self.ui_listAvailables = listAvailables_ui
        self.ui_fileviewer = fileViewer_ui
        self.config = config
        self.refresh_fileviewer(self.config.categories)

        QObject.connect(self.ui_fileviewer, SIGNAL("play(Video)"), 
                self.play)

    def video_downloaded(self, video):
        self.ui_listAvailables.remove(video)
        self.ui_fileviewer.add(video)

    def refresh_fileviewer(self, categories):
        self.ui_fileviewer.refresh_all(categories)

    def blacklist_selected(self):
        for v in self.ui_listAvailables.selectedVideos():
            v.blacklist()
            self.ui_listAvailables.remove(v)
            self.config.blacklist.append(v.url)

    def play_selected(self, index=None):
        v = self.ui_fileviewer.videoSelected()
        self.play(v)

    def play(self, video):
        if not video:
            return
        playerProcess = PlayerProcess(self.config.player, video)
        playerProcess.start()
        video.marked_as_seen(True)

    def remove_selected(self):
        v = self.ui_fileviewer.videoSelected()
        if v:
            v.rm()
            self.ui_fileviewer.remove(v)

    def marked_as_seen(self, seen=True):
        video = self.ui_fileviewer.videoSelected()
        video.marked_as_seen(seen)
        self.ui_fileviewer.marked_as_seen_selected(seen)


class ListAvailables(QListView):
    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.model = ListAvailablesVideosModel(parent)
        self.setModel(self.model)
        
        QObject.connect(self, SIGNAL("activated(QModelIndex)"),
                self.download)

    def clear(self):
        self.model.tabData = []

    def video(self, row):
        return self.model.tabData[row]

    def add(self, video):
        if DAO.video_exist(video):
            return
        self.model.add(video)

    def remove(self, video):
        self.model.remove(video)

    def selectedVideos(self):
        indexes = self.selectedIndexes()
        videos = []
        for i in indexes:
            v = self.video(i.row())
            videos.append(v)
        return videos

    def download(self, index=None):
        if index and isinstance(index, QModelIndex):
            video = self.video(index.row())
            self.emit(SIGNAL("download(Video)"), video)
        else:
            for v in self.selectedVideos():
                self.emit(SIGNAL("download(Video)"), v)

    def refresh(self, liste):
        self.clear()
        for item in liste:
            self.add(item)

class CDL(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.config = Config()

        self.ui.wait = Ui_Wait(self)
        self.downloadManager = DownloadManager(self, self.ui.listAvailables)
        self.videoManager = VideoManager(self.ui.listAvailables,
                self.ui.fileviewer, self.config)

        QObject.connect(self.downloadManager, SIGNAL("download_terminated(Video)"),
                self.videoManager.video_downloaded)

        QObject.connect(self, SIGNAL("refresh(PyQt_PyObject)"),
                self.downloadManager.refresh_availables)

        QObject.connect(self.ui.listAvailables, SIGNAL("download(Video)"),
                self.downloadManager.download)

    	QObject.connect(self.ui.wait, SIGNAL("open()"), self.ui.wait.open)
    	QObject.connect(self.ui.wait, SIGNAL("close()"), self.ui.wait.close)

    def showPreferences(self):
        self.pref = Preferences(self.config, self)
    	QObject.connect(self.pref, SIGNAL("configChanged(list)"),
                self.videoManager.refresh_fileviewer)
        self.pref.show()

    def refresh_availables(self):
        def threadListNewVideos(self):
            self.ui.wait.emit(SIGNAL("open()"))
            liste = get_list_new_videos(self.config)
            self.emit(SIGNAL("refresh(PyQt_PyObject)"), liste)
            self.ui.wait.emit(SIGNAL("close()"))

        if self.downloadManager.nb_downloads_in_progress != 0:
            r = QMessageBox.critical(self, "Veuillez patienter !", 
                    u"Tous les téléchargements ne sont pas terminés, veuillez patienter quelques instants avant de raffraichir cette liste")
            return

        threading.Thread(target=threadListNewVideos, args=[self]).start()

    def quit(self):
        if hasattr(self, 'pref'):
            self.pref.close()
        if hasattr(self, 'downloadManager'):
            self.downloadManager.ui_download.close()

        self.close()

    def closeEvent(self, closeEvent):
        self.quit()

    @pyqtSlot()
    def on_pushButtonRefresh_clicked(self):
        self.refresh_availables()

    @pyqtSlot()
    def on_pushButtonDownload_clicked(self):
        self.downloadManager.download_selected()

    @pyqtSlot()
    def on_pushButtonPlay_clicked(self):
        self.videoManager.play_selected()

    @pyqtSlot()
    def on_pushButtonBlacklist_clicked(self):
        try:
            self.videoManager.blacklist_selected()
        except Exception, e:
            print "error while blacklisting video"
            print traceback.format_exc(e)

    @pyqtSlot()
    def on_pushButtonSeen_clicked(self):
        self.videoManager.marked_as_seen(True)

    @pyqtSlot()
    def on_pushButtonNotSeen_clicked(self):
        self.videoManager.marked_as_seen(False)

    @pyqtSignature("")
    def on_pushButtonRemove_clicked(self):
        self.videoManager.remove_selected()

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
    db.close()
    app.closeAllWindows()
    window = None # FIX Segmentation Fault
    sys.exit(ret)

