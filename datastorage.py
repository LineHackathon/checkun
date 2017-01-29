#!/usr/bin/python
# -*- coding: utf-8 -*-

# import yaml
import json
from pymongo import Connection

MONGO_URL = os.environ.get('MONGOHQ_URL')

if MONGO_URL:
    # Get a connection
    connection = Connection(MONGO_URL)
    # Get the database
    db = connection[urlparse(MONGO_URL).path[1:]]
else:
    # Not on an app with the MongoHQ add-on, do some localhost action
    connection = Connection('localhost', 27017)
    db = connection['test_db']


##########################
# group collection(table)
##########################

#とりあえずgroup_idのみ。必要ならその他情報も追加
#ginfo:{}
def add_group(gid, ginfo={}):

def update_group(gid, ginfo={}):

def delete_group(gid):


##########################
# user collection(table)
##########################

#とりあえずuser_idのみ。必要ならその他情報も追加
#uinfo:{}
def register_user(uid, uinfo={}):

#ユーザー情報更新
def update_user(uid, uinfo={}):


def delete_user(uid):


##########################
# group->user collection(table)
##########################




##########################
# user->group collection(table)
##########################


if __name__ == "__main__":
    pass
