#!/bin/python
# -*- coding: utf-8 -*-



from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Ui_MainWindow import Ui_MainWindow
from Ui_Download import Ui_Download
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


try:
    import sqlite3
except Exception, e:
    print e
    exit(1)

debug = False
#debug = True

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
    def __init__(self, url, dir_user, name, create_path=False):
        self.path = os.path.join(dir_user, name)
        self.name = name
        self.url = os.path.join(url, self.name)
        self.videos = []
        if create_path and not os.path.exists(self.path):
            try:
                os.makedirs(self.path)
            except Exception, e:
                print "%s ne peut être créé" % self.dir_user
                exit(2)
 
    def __repr__(self):
        return self.name

    def list_videos(self):
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
            if date_node_list.length == debit_node_list.length and \
                    rubrique.lower().find(self.name.lower()) > -1:
                for dn in date_node_list:
                    url = str(debit_node_list[0].firstChild.nodeValue)
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
        else:
            self.dir_user = DAO.dir_user()
            self.url_dl = DAO.url_dl()
            self.categories_availables = DAO.categories_availables(self.url_dl, 
                    self.dir_user)
            self.categories = DAO.categories(self.url_dl, self.dir_user)
            for c in self.categories:
                c.videos = DAO.videos(c)

    def path(self, category):
        #FIXME GET PATH IN BDD
        return os.path.join(self.dir_user)
    
    def reset(self):
        DAO.reset_config()
        self.dir_user = DAO.dir_user()
        self.url_dl = DAO.url_dl()
        self.categories_availables = DAO.categories_availables(
                self.url_dl, self.dir_user)
        self.categories = DAO.categories(self.url_dl, self.dir_user)

class DAO:

    @classmethod
    def reset_config(cls):
        global db
        db.execute("CREATE TABLE config(dir_user, url)")
        db.execute("CREATE TABLE category_available(name)")
        db.execute("CREATE TABLE category(name)")
        db.execute("CREATE TABLE video(url, category, path, name, date,\
                length)") #FIXME : if not exist  

        db.execute("INSERT INTO config(dir_user, url) VALUES (?, ?)",
                (os.path.join(os.path.expanduser("~"), 'Canal+DL'),
                    'http://www.canalplus.fr/rest/bootstrap.php?/bigplayer/search/'))
        db.executemany("INSERT INTO category_available(name) VALUES (?)",
                (("discrete",),
                 ("boite",), 
                 ("planquee",), 
                 ("guignols",), 
                 ("petit",),
                 ("petite",), 
                 ("meteo",), 
                 ("pepites",),   
                 ("groland",), 
                 ("sav",), 
                 ("tele",), 
                 ("salut",), 
                 ("zapping",)
                 ))

        db.executemany("INSERT INTO category(name) VALUES (?)",
                (("petit",),
            ("zapping", )))
        db.commit()

    @classmethod
    def add_video(cls, video):
        global db
        db.execute("INSERT INTO video(url, category, path, name, date, length) \
                VALUES(?, ?, ?, ?, ?, ?)", 
                (video.url, video.category.name, video.path, video.name,
                    video.date, video.length))
        db.commit()

    @classmethod
    def videos(cls, category):
        global db
        result = db.query("SELECT url, path, name, date, length FROM video WHERE category=?",
                (category.name, ))
        videos = []
        for r in result:
            url = r[0]
            path = r[1]
            name = r[2]
            date = r[3]
            length = r[4]
            videos.append(Video(url, category, path=path, name=name,
                date=date, length=length))

        return videos

    @classmethod
    def dir_user(cls):
        global db
        r = db.query("SELECT dir_user FROM config")
        return r[0][0]

    @classmethod
    def url_dl(cls):
        global db
        r = db.query("SELECT url FROM config")
        return r[0][0]
        

    @classmethod
    def categories_availables(self, url_dl, dir_user):
        global db
        result = db.query("SELECT * FROM \
            category_available")
        categories = []
        for r in result:
            name = r[0]
            c = Category(url_dl, dir_user,  name)
            categories.append(c)

        return categories

    @classmethod
    def categories(self, url_dl, dir_user):
        global db
        result = db.query("SELECT * FROM category")
        categories = []
        for r in result:
            name = r[0]
            c = Category(url_dl, dir_user,  name)
            categories.append(c)

        return categories




class Video():
    def __init__(self, url, category, path=None, name=None, date=None,
        length=None):
        self.url = url
        self.category = category
        self.date = date
        if name == None:
            filename = url.split('/')[-1]
            self.name = filename
        else:
            self.name = name

        if path == None:
            self.path = os.path.join(self.category.path, filename)
        else:
            self.path = path

        self.length = 0

    def __repr__(self):
        return u"Video [%s] %s\t%s" % (self.category, self.url, self.date)



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
            list_videos = c.list_videos()
            c.videos = list_videos
            videos.extend(list_videos)
        except Exception, e:
            print traceback.format_exc(e)
            exit(1)

    return videos
    
class FileViewer(QGroupBox):
    def __init__(self, parent=None):
        QGroupBox.__init__(self, parent)
        self.children = None
        self.first = True

    def refresh_all(self, categories):
        if self.first:
            self.children = self.findChildren(QGroupBox)
            self.first = False

        for c in self.children:
            c.setVisible(False)
            c.setChecked(False)
            for cat in categories:
                if c.objectName() == cat.name:
                    c.setVisible(True)
                    listview = c.findChild(ListCategory)
                    listview.refresh(cat.videos)

class FileGroupBox(QGroupBox):
    def __init__(self, parent=None):
        QGroupBox.__init__(self, parent)
        #self.setFlat(False)
        self.setCheckable(True)
        self.setChecked(True)

class ListCategory(QListWidget):
    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)

    def refresh(self, videos):
        #self.reset()
        for v in videos:
            item = QListWidgetItem(v.name, self)
            item.setData(Qt.UserRole, v)
            self.addItem(item)
            item.setSelected(True)

        self.sortItems()

    def refresh_forced(self):
        pass

class DownloadProcess(QProcess):
    def __init__(self, parent=None):
        QProcess.__init__(self, parent)
        new_env=QProcess.systemEnvironment()
        self.setEnvironment(new_env)

        self.setReadChannel(QProcess.StandardError)

        QObject.connect(self, SIGNAL("readyRead()"),
                self.tryReadPourcent)
        QObject.connect(self, SIGNAL("finished(int)"), self.finished)

    def tryReadPourcent(self):
        line = self.readAll()
        r = re.findall("(\d{1,3}\.{0,1}\d{0,1})%", line)
        pourcent = 0
        if len(r) > 0:
            pourcent = int(float(r[-1]))

        self.emit(SIGNAL("majDownloadBar(int)"), pourcent)

    def finished(self, int):
        self.emit(SIGNAL("majDownloadBar(int)"), 100)

    def stop(self):
        self.kill()

class DownloadHLayout(QHBoxLayout):
    def __init__(self, progressBar, pushButton, parent=None):
        QHBoxLayout.__init__(self, parent)
        self.progressBar = progressBar
        self.pushButton = pushButton

        self.progressBar.setProperty("value", 0)
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
                self.delete)
    
        QObject.connect(self.process, SIGNAL("majDownloadBar(int)"),
                self.majProgressBar)


    def majProgressBar(self, pourcent):
        if pourcent < 100:
            self.layout.progressBar.setValue(pourcent)
        else:
            self.layout.progressBar.setValue(100)

    def delete(self):
        if self.process.state() != QProcess.NotRunning:
            self.process.stop()

        lo = self.layout.layout()
        while True:
            i=lo.takeAt(0)
            if i is None : break
            i.widget().deleteLater()
            del i

        self.emit(SIGNAL("deleteLayout(object)"), self.layout)

        del lo

class DownloadManager():
    def __init__(self, parent):
        self.downloads = [] # FIXME useless ?
        self.ui = Ui_DownloadManager(parent)
    
    def add(self, video):
        cmd = "/usr/bin/flvstreamer -er %s -o %s" % \
                (video.url, video.path)

        layout = self.ui.new_layout()

        process = DownloadProcess()
        process.start(cmd)
        download = Download(process, layout)
        
        QObject.connect(download, SIGNAL("deleteLayout(object)"), 
                self.deleteLayout)


        self.downloads.append(download)
        self.ui.show()

    def deleteLayout(self, layout):
        self.ui.verticalLayout.removeItem(layout)
        del layout
        if len(self.ui.verticalLayout.children()) < 1: # FIXME
            self.ui.close()

class ListAvailables(QListWidget):
    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setStyleSheet("ListAvailableItem { \
                border: 15px solid #C4C4C3;\
                border-bottom-color: #C2C7CB;\
                border-top-left-radius: 4px;\
                border-top-right-radius: 4px;\
                min-width: 8ex;\
                padding: 2px;\
                }")
        self.downloadManager = DownloadManager(self)

    def add(self, video):
        item = ListAvailableItem(video.url, self)
        item.setData(Qt.UserRole, video)
        self.addItem(item)

    def download(self):
        selected = map(lambda i: i.data(Qt.UserRole).toPyObject(), self.selectedItems())
        for v in selected:
            self.downloadManager.add(v)

    def refresh(self, liste):
        self.clear()
        for item in liste:
            self.add(item)


class ListAvailableItem(QListWidgetItem):
    def __init__(self, name,  parent=None):
        QListWidgetItem.__init__(self, name, parent)


def get_random_video():
    cat = Category("http://lien-vers-categorie-bidon.fr",
        "/home/jonathan/Canal+DL/", "zapping")

    return Video("rtmp://vod-fms.canalplus.fr/ondemand/videos/1009/ZAPPING_EMISSION_100908_CAN_150771_video_H.flv", cat)




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

    def launch(self, videos):
        for v in videos:
            if v.download() != 0:
                print u"%s n'a pas été téléchargé" % v
                continue
            DAO.add_video(v)

        
class Ui_Wait(QProgressDialog):
    def __init__(self, parent=None):
        print "WAITING !"
        QProgressDialog.__init__(self, u"Recherche des nouvelles vidéos en cours ...",
                "Fermer", 0, 0, parent)
        self.setModal(True)
        self.setWindowTitle(u"Recherche ...")
        self.setCancelButton(None)

    def open(self):
        self.show()

    def close(self):
        self.hide()


db = DbConnect()

class CDL(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        fileviewer = self.ui.fileviewer

        self.config = Config()
        fileviewer.refresh_all(self.config.categories)

        self.wait = Ui_Wait(self)

        QObject.connect(self.ui.listAvailables, SIGNAL("refresh(PyQt_PyObject)"),
                self.ui.listAvailables.refresh)
    	QObject.connect(self.wait, SIGNAL("open()"), self.wait.open)
    	QObject.connect(self.wait, SIGNAL("close()"), self.wait.close)
    def find(self):
        pass

    @pyqtSlot()
    def on_pushButtonRefresh_clicked(self):
        videos = []
        if not debug:
            def threadListNewVideos(self):
                self.wait.emit(SIGNAL("open()"))
                liste = get_list_new_videos(self.config)
                self.ui.listAvailables.emit(SIGNAL("refresh(PyQt_PyObject)"), liste)
                self.wait.emit(SIGNAL("close()"))
			
            videos = threading.Thread(target=threadListNewVideos, args=[self]).start()
    
        self.ui.listAvailables.clear()
        
        if debug:
            videos = []
            for i in range(4):
                v = get_random_video()
                videos.append(v)

        #for v in videos:
        #    self.ui.listAvailables.add(v)

    @pyqtSlot()
    def on_pushButtonDownload_clicked(self):
        self.ui.listAvailables.download()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = CDL()
    window.show()
    ret = app.exec_()
    db.close()
    app.closeAllWindows()
    window = None # FIX Segmentation Fault
    sys.exit(ret)

