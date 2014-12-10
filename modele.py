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

from DAO import DAO



class Category(Entity):
    using_options(tablename='category')
    name = Field(Unicode, primary_key=True)
    code_sous_cat = Field(Unicode)
    path = Field(Unicode)
    url = Field(Unicode)
    videos = OneToMany('Video')
    config = ManyToMany('Config', inverse='categories')
    config_availables = ManyToMany('Config', inverse='categories_availables')

    def __init__(self, name, dir_user, code_sous_cat, url, create_path=False):
        self.name = unicode(name)
        if dir_user:
            self.path = os.path.join(unicode(dir_user), self.name)

        self.code_sous_cat = unicode(code_sous_cat)
        self.url = unicode(url)

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

        print "%s - %s" % (self.code_sous_cat, self.url);

        videos_found = []
        video_ids_already_found = []
        video_nodes = []

        url_blacklist = [d.url for d in blacklist]

        is_mea = re.search('getMEAs', self.url)

        dom = minidom.parse(urllib.urlopen(self.url))
        if is_mea:
            nodes = dom.getElementsByTagName('MEA')

            for node in nodes:
                rubrique_node_list = node.getElementsByTagName('RUBRIQUE')
                try:
                    rubrique_name = str(rubrique_node_list[0].firstChild.nodeValue)
                    if rubrique_name != self.code_sous_cat:
                        continue
                except:
                    continue

                video_id = str(node.getElementsByTagName('ID')[0].firstChild.nodeValue);
                base_url = u'http://service.canal-plus.com/video/rest/'
                rubrique_url = base_url + '/getVideosLiees/cplus/' + video_id
                dom = minidom.parse(urllib.urlopen(rubrique_url))
                video_nodes.extend(dom.getElementsByTagName('VIDEO'))
        else:
            video_nodes = dom.getElementsByTagName('VIDEO')

        for vn in video_nodes:
            category = vn.getElementsByTagName('CATEGORIE')[0].firstChild.nodeValue
            video_id = str(vn.getElementsByTagName('ID')[0].firstChild.nodeValue);

            if video_id in video_ids_already_found:
                continue

            rubrique_node_list = vn.getElementsByTagName('RUBRIQUE')
            try:
                rubrique_name = str(rubrique_node_list[0].firstChild.nodeValue)
                if rubrique_name != self.code_sous_cat:
                    continue

                if category != 'QUOTIDIEN' \
                    and category != 'EMISSION' \
                    and category != 'BA' \
                    and ( category != "BONUS" and rubrique_name != 'L_OEIL_DE_LINKS'):
                    continue

                debit_node_list = vn.getElementsByTagName('HLS')
                date_node_list = vn.getElementsByTagName('DATE')
                titre = vn.getElementsByTagName('TITRE')[0].firstChild.nodeValue;
                sous_titre = vn.getElementsByTagName('SOUS_TITRE')[0].firstChild.nodeValue;
            except:
                continue

            if date_node_list.length == debit_node_list.length:
                for dn in date_node_list:
                    url = str(debit_node_list[0].firstChild.nodeValue)
                    if url in url_blacklist:
                        continue
                    if url.find('m3u8') > -1:
                        date = str(dn.firstChild.nodeValue)
                        description = titre + ' - ' + sous_titre
                        v = {
                            'url': url,
                            'category': self,
                            'description': description,
                            'name': sous_titre,
                            'date': date
                        }
                    videos_found.append(v)
        return videos_found

class Config(Entity):
    using_options(tablename='config')
    dir_user = Field(Unicode)
    player = Field(Unicode)
    blacklist = ManyToMany('Download', inverse='blacklist')
    categories_availables = ManyToMany('Category')
    categories = ManyToMany('Category')

    def __init__(self, dir_user, player):
        self.dir_user = unicode(dir_user)
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

    def __init__(self, url, category, name, description, date=None):
        self.url = unicode(url)
        self.category = category
        self.description = unicode(description)
        self.name = unicode(name)
        self.name = self.name.replace(' ', '_').replace('/', '-')
        self.date = unicode(date)
        self.path = unicode(os.path.join(self.category.path, self.name + '.ts'))

    def rm(self):
        try:
            print self.path
            os.remove(self.path)
        except:
            print "cannot remove"
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
        self.description = unicode(description)
        self.path = unicode(os.path.join(self.category.path, self.name + '.ts'))

        if not length:
            self.length = 0
        else:
            self.length = length

        self.seen = seen

    def __repr__(self):
        return u"Video [%s] %s\t%s" % (self.category, self.url, self.date)

    def rm(self):
        try:
            os.remove(self.path)
        except:
            pass
        finally:
            self.delete()

    def marked_as_seen(self, seen):
        self.seen = seen
        DAO.commit()
