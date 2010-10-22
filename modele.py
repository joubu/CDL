#!/bin/python
# -*- coding: utf-8 -*-

import os
import re
from elixir import Entity, Field
from elixir import Integer, Unicode, Boolean, DateTime
from elixir import ManyToMany, ManyToOne, OneToMany
from elixir import using_options

from xml.dom import minidom
import urllib

from DAO import DAO, session



class Category(Entity):
    using_options(tablename='category')
    name = Field(Unicode, primary_key=True)
    keywords = Field(Unicode)
    path = Field(Unicode)
    url = Field(Unicode)
    videos = OneToMany('Video')
    #downloads = OneToMany('Download')    
    config = ManyToMany('Config', inverse='categories')
    config_availables = ManyToMany('Config', inverse='categories_availables')

    def __init__(self, name, url=None, dir_user=None, keywords=None, create_path=False):
        self.name = unicode(name)
        if keywords:
            self.keywords = unicode(keywords)
        if dir_user:
            self.path = os.path.join(unicode(dir_user), self.name)
        if url:
            self.url = os.path.join(unicode(url), self.keywords)

        self.videos = []
        if create_path and not os.path.exists(self.path):
            try:
                os.makedirs(self.path)
            except Exception, e:
                print "%s ne peut être créé" % self.path
                exit(2)
 
    def __repr__(self):
        return self.name

    def find_new_videos_availables(self, blacklist=list()):
        list_dict = []
        url_blacklist = [d.url for d in blacklist]
        print url_blacklist
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
                    if url in url_blacklist:
                        continue
                    if url.find('rtmp') > -1:
                        date = str(dn.firstChild.nodeValue)
                        v = {
                            'url': url, 
                            'category': self,
                            'date': date
                            }
                        list_dict.append(v)
        return list_dict

class Config(Entity):
    using_options(tablename='config')
    dir_user = Field(Unicode)
    url_dl = Field(Unicode)
    player = Field(Unicode)
    blacklist = ManyToMany('Download', inverse='blacklist')
    #downloads = ManyToMany('Download')
    #videos = ManyToMany('Video')
    categories_availables = ManyToMany('Category')
    categories = ManyToMany('Category')

    def __init__(self, dir_user, url_dl, player):
        self.dir_user = unicode(dir_user)
        self.url_dl = unicode(url_dl)
        self.player = unicode(player)
        self.categories_availables = []
        self.categories = []
        self.blacklist = []
        #self.videos_availables = []
        #self.videos_downloaded = []
    #def reset(self):
    #    DAO.reset_config()

class Download(Entity):
    using_options(tablename='download')
    url = Field(Unicode, primary_key=True)
    category = ManyToOne('Category')    
    name = Field(Unicode)
    path = Field(Unicode)
    date = Field(Unicode)
    blacklist = ManyToMany('Config', inverse='blacklist')

    def __init__(self, url, category, date, name=None):
        self.url = unicode(url)
        self.category = category
        self.date = unicode(date)
        if not name:
            filename = url.split('/')[-1]
            try:
                matches = re.findall("(.*)_CAN_([0-9]*)_video_H\.flv", filename)
                if len(matches) > 0:
                    self.name = u"%s_%s.flv" % (matches[0][0], matches[0][1])
                else:
                    matches =re.compile("(.*)_([0-9]*)_AUTO_([0-9]*)_.*_video_H\.flv").findall(filename)
                    self.name = u"%s_%s_%s.flv" % (matches[0][0], matches[0][1],
                            matches[0][2])
                    
            except:
                self.name = unicode(filename)
        else:
            self.name = unicode(name)


        self.path = unicode(os.path.join(self.category.path, self.name))

    def rm(self):
        try:
            os.remove(self.path)
        except:
            pass

class Video(Entity):
    using_options(tablename='video')
    url = Field(Unicode, primary_key=True)
    #date = Field(DateTime)
    date = Field(Unicode)
    name = Field(Unicode)
    path = Field(Unicode)
    length = Field(Integer)
    seen = Field(Boolean)
    category = ManyToOne('Category')

    def __init__(self, url, category, name, date,
                    length=None, seen=False):

        self.url = unicode(url)
        self.category = category
        self.date = unicode(date)
        self.name = unicode(name)
        self.path = unicode(os.path.join(self.category.path, self.name))

        if not length:
            self.length = 0
        else:
            self.length = length

        self.seen = seen

    def __repr__(self):
        return u"Video [%s] %s\t%s" % (self.category, self.url, self.date)
        #return u"Video %s" % (self.name)

    def rm(self):
        try:
            os.remove(self.path)
        except:
            pass
        finally:
            DAO.remove_video(self)

    def marked_as_seen(self, seen):
        self.seen = seen
