#!/bin/python
# -*- coding: utf-8 -*-



from PyQt4.QtGui import *
from PyQt4.QtCore import *
from Ui_MainWindow import Ui_MainWindow
from xml.dom import minidom
import urllib
import sys
import os
import re
import traceback

try:
    import sqlite3
except Exception, e:
    print e
    exit(1)

#debug = False
debug = True

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
    def __init__(self, url, dir_user, name):
        self.path = os.path.join(dir_user, name)
        self.name = name
        self.url = os.path.join(url, self.name)
        if not os.path.exists(self.path):
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
                        list_videos.append(Video(url, self, date))
        return list_videos

class Config:
    def __init__(self, db):
        self.db = db
        tables = self.db.query("SELECT name FROM SQLite_Master")
        if len(tables) == 0:
            self.reset()
        else:
            self.dir_user = DAO.dir_user(self.db)
            self.url_dl = DAO.url_dl(self.db)
            self.categories_availables = DAO.categories_availables(self.db,
                    self.url_dl, self.dir_user)
            self.categories = DAO.categories(self.db, self.url_dl, self.dir_user)

    def path(self, category):
        #FIXME GET PATH IN BDD
        return os.path.join(self.dir_user)
    
    def reset(self):
        DAO.reset_config(self.db)
        self.dir_user = DAO.dir_user(self.db)
        self.url_dl = DAO.url_dl(self.db)
        self.categories_availables = DAO.categories_availables(self.db,
                self.url_dl, self.dir_user)
        self.categories = DAO.categories(self.db, self.url_dl, self.dir_user)

class DAO:

    @classmethod
    def reset_config(cls, db):
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
    def dir_user(cls, db):
        r = db.query("SELECT dir_user FROM config")
        return r[0][0]

    @classmethod
    def url_dl(cls, db):
        r = db.query("SELECT url FROM config")
        return r[0][0]
        

    @classmethod
    def categories_availables(self, db, url_dl, dir_user):
        result = db.query("SELECT * FROM \
            category_available")
        categories = []
        for r in result:
            name = r[0]
            c = Category(url_dl, dir_user,  name)
            categories.append(c)

        return categories

    @classmethod
    def categories(self, db, url_dl, dir_user):
        result = db.query("SELECT * FROM category")
        categories = []
        for r in result:
            name = r[0]
            c = Category(url_dl, dir_user,  name)
            categories.append(c)

        return categories


class Video:
    def __init__(self, url, category, date):
        self.url = url
        self.category = category
        self.date = date
        filename = url.split('/')[-1]
        self.name = filename
        self.path = os.path.join(self.category.path, filename)
        self.length = 0
    def __repr__(self):
        return "[%s] %s\t%s" % (self.category, self.url, self.date)
    def download(self):
        cmd = "flvstreamer -er %s -o %s" % \
                (self.url, self.path)
        try:
            ret = os.system(cmd)
        except Exception, e:
            traceback.format_exc(e)
            exit(2)
        return ret
        
        

def download_videos(config):
    videos = []
    for c in config.categories:
        if debug:
            print u"categorie %s trouvée"%c
        try:
            videos.extend(c.list_videos())
        except Exception, e:
            print traceback.format_exc(e)
            exit(1)
    for v in videos:
        if v.download() != 0:
            print u"%s n'a pas été téléchargé" % v
            continue
        c.db.add_video(v.url, v.category, v.path, v.name, v.date, v.length)

        
def FileViewer():
    def __init__(self):
        pass

    def refresh(self):
        pass

def FileGroupBox(QGroupBox):
    def __init__(self, parent=None):
        QGroupbox.__init__(parent)
        self.setFlat(False)
        self.setCheckable(True)
        self.setChecked(True)

def ListViewCategory(QListView):
    def __init__(self, parent=None):
        QListView.__init__(parent)

class CDL(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        db = DbConnect()
        config = Config(db)
        db.close()


    def find(self):
        pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = CDL()
    window.show()
    ret = app.exec_()
    app.closeAllWindows()
    window = None # FIX Segmentation Fault
    sys.exit(ret)

