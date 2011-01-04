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
    number = Field(Unicode)
    path = Field(Unicode)
    url = Field(Unicode)
    videos = OneToMany('Video')
    config = ManyToMany('Config', inverse='categories')
    config_availables = ManyToMany('Config', inverse='categories_availables')

    def __init__(self, name, url=None, dir_user=None, number=None, create_path=False):
        self.name = unicode(name)
        if number:
            self.number = unicode(number)
        if dir_user:
            self.path = os.path.join(unicode(dir_user), self.name)
        if url:
            self.url = os.path.join(unicode(url), self.number)

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

        dom = minidom.parse(urllib.urlopen(self.url))

        videos_id = []
        meas = dom.getElementsByTagName('MEA')
        for i in meas:
            if i.getElementsByTagName('ID')[0].childNodes != []:
                id = i.getElementsByTagName('ID')[0].firstChild.nodeValue
                videos_id.append(id)

        for video_id in videos_id:
            video_url = "http://www.canalplus.fr/rest/bootstrap.php?/bigplayer/getVideos/" + video_id
            video_dom = minidom.parse(urllib.urlopen(video_url))

            video = video_dom.getElementsByTagName('VIDEO')
            if not len(video):
                continue

            videos = video[0].getElementsByTagName('MEDIA')[0].getElementsByTagName('VIDEOS')[0]
            url = str(videos.getElementsByTagName('HAUT_DEBIT')[0].firstChild.nodeValue)
            if url in url_blacklist:
                continue

            description = ""
            titrage = video[0].getElementsByTagName('INFOS')[0].getElementsByTagName('TITRAGE')[0]
            if titrage.getElementsByTagName('TITRE')[0].childNodes != []:
                if titrage.getElementsByTagName('SOUS_TITRE')[0].childNodes != []:
                    description = \
                        titrage.getElementsByTagName('TITRE')[0].firstChild.nodeValue \
                        + " (" + \
                        titrage.getElementsByTagName('SOUS_TITRE')[0].firstChild.nodeValue \
                        + ")"
            if url.find('rtmp') > -1:
                v = {
                    'url': url, 
                    'category': self,
                    'description': description
                }
                list_dict.append(v)
        return list_dict

class Config(Entity):
    using_options(tablename='config')
    dir_user = Field(Unicode)
    url_dl_show = Field(Unicode)
    url_dl_videos = Field(Unicode)
    player = Field(Unicode)
    blacklist = ManyToMany('Download', inverse='blacklist')
    categories_availables = ManyToMany('Category')
    categories = ManyToMany('Category')

    def __init__(self, dir_user, url_dl_show, url_dl_videos, player):
        self.dir_user = unicode(dir_user)
        self.url_dl_show = unicode(url_dl_show)
        self.url_dl_videos = unicode(url_dl_videos)
        self.player = unicode(player)
        self.categories_availables = []
        self.categories = []
        self.blacklist = []

class Download(Entity):
    using_options(tablename='download')
    url = Field(Unicode, primary_key=True)
    category = ManyToOne('Category')    
    name = Field(Unicode)
    path = Field(Unicode)
    date = Field(Unicode)
    description = Field(Unicode)
    blacklist = ManyToMany('Config', inverse='blacklist')

    def __init__(self, url, category, description="", date=None, name=None):
        self.url = unicode(url)
        self.category = category
        self.description = unicode(description)

        if not name:
            filename = url.split('/')[-1]
            try:
                matches = re.findall("(.*)(......)_CAN_([0-9]*)_video_H\.flv", filename)
                if len(matches) > 0:
                    self.name = u"%s%s_%s.flv" % (matches[0][0], matches[0][1],
                            matches[0][2])
                else:
                    matches =re.compile("(.*)_([0-9]*)_AUTO_([0-9]*)_.*_video_H\.flv").findall(filename)
                    self.name = u"%s_%s_%s.flv" % (matches[0][0], matches[0][1],
                            matches[0][2])
                if not date:
                    m = re.compile("(..)(..)(..)").findall(matches[0][1])
                    self.date = u"%s/%s/%s" % (m[0][2], m[0][1], m[0][0])

                    
            except:
                self.name = unicode(filename)
                self.date = "???"
        else:
            self.name = unicode(name)
            self.date = "???"


        self.path = unicode(os.path.join(self.category.path, self.name))

    def rm(self):
        try:
            os.remove(self.path)
        except:
            pass

class Video(Entity):
    using_options(tablename='video')
    url = Field(Unicode, primary_key=True)
    date = Field(Unicode)
    name = Field(Unicode)
    path = Field(Unicode)
    length = Field(Integer)
    seen = Field(Boolean)
    description = Field(Unicode)
    category = ManyToOne('Category')

    def __init__(self, url, category, name, date, description="",
                    length=None, seen=False):

        self.url = unicode(url)
        self.category = category
        self.date = unicode(date)
        self.name = unicode(name)
        self.path = unicode(os.path.join(self.category.path, self.name))
        self.description = unicode(description)

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
            self.delete()

    def marked_as_seen(self, seen):
        self.seen = seen
