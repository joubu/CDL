# -*- coding: utf-8 -*-


import os

#from sqlalchemy.orm import scoped_session, sessionmaker
from elixir import setup_all, create_all
from elixir import metadata, session

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import not_
# Emplacement du fichier
WORKING_DIR = os.path.dirname(__file__)

DB_FILE = os.path.join(WORKING_DIR, 'database.db')
metadata.bind = 'sqlite:///%s' % DB_FILE
metadata.bind.echo = False


class DAO(object):
    """
    Accès aux données players et games
    """

    @classmethod
    def init(cls):
        """
        Initialisation de la bdd
        Création si besoin des tables
        """
        setup_all()
        create_all()
        config = cls.config()
        if not config:
            config = cls.reload_config()
        return config

    @classmethod
    def add(cls, entity):
        """
        Ajoute un objet en session
        """
        session.add(entity)

    @classmethod
    def commit(cls):
        """
        Commite les changements effectués
        """
        session.flush()
        session.commit()

    @classmethod
    def merge(cls, item):
        return session.merge(item)

    @classmethod
    def change_session(cls):
        session2 = ScopedSession(sessionmaker())

    @classmethod
    def category(cls, name):
        try:
            from modele import Category
            return session.query(Category).filter(Category.name==name).first()
        except:
            return None

    @classmethod
    def download(cls, url, category, description):
        from modele import Download
        try:
            download = session.query(Download).filter(Download.url==unicode(url)).one()
            return download
        except:
            return Download(url, category, description)
    @classmethod
    def downloads(cls):
        try:
            from modele import Download, Config
            url_blacklist = [e.url for e in 
                    session.query(Config).first().blacklist]
                        
            return session.query(Download).filter(
                    not_(Download.url.in_(url_blacklist))).all()
        except Exception, e:
            return None

    @classmethod
    def already_downloaded(cls, url):
        try:
            from modele import Video
            video = session.query(Video).filter(Video.url==url).first()
            if video:
                return True
            return False
        except:
            return False
    @classmethod
    def videos(cls):
        try:
            from modele import Video
            return session.query(Video).all()
        except:
            return None

    @classmethod
    def categories(cls):
        try:
            from modele import Config
            return session.query(Config).all()[-1].categories
        except:
            return None

    @classmethod
    def categories_availables(cls):
        try:
            from modele import Config
            return session.query(Config).all()[-1].categories_availables
        except:
            return None

    @classmethod
    def player(cls):
        try:
            from modele import Config
            config = session.query(Config).all()[-1]
            return config.player
        except:
            return None # On ne doit pas se trouver ici, il doit toujours y avoir une config

    @classmethod
    def config(cls):
        from modele import Config
        try:
            config = session.query(Config).all()[-1]
        except:
            config = cls.reload_config()

        return config

    @classmethod
    def reload_config(cls):
        from modele import Config, Category
        dir_user = unicode(os.path.join(os.path.expanduser("~"), 'Canal+DL'))
        url_dl_show = u'http://www.canalplus.fr/rest/bootstrap.php?/bigplayer/getMEAs/'
        url_dl_videos = u'http://www.canalplus.fr/rest/bootstrap.php?/bigplayer/getVideos/'
        player = u'vlc'

        c = Config(dir_user, url_dl_show, url_dl_videos, player)
        name_number = {
                 u"discrete": "0",
                 u"boite":    "0", 
                 u"boucan":   "62",
                 u"guignols": "48", 
                 u"grand":    "104",
                 u"groland":  "254", 
                 u"petit":    "249",
                 u"petite":   "0", 
                 u"matinale": "0",
                 u"meteo":    "0", 
                 u"pepites":  "47",
                 u"sav":      "252", 
                 u"salut":    "0", 
                 u"zapping":  "201"
                 }
        for k, v in name_number.iteritems():
            c.categories_availables.append(
                Category(k, url_dl_show, dir_user, v, create_path=False)
            )

        petit = session.query(Category).filter(Category.name==u'petit').first()
        zapping = session.query(Category).filter(Category.name==u'zapping').first()
        c.categories.append(petit)
        c.categories.append(zapping)

        cls.commit()

        return c
        
