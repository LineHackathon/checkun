#!/usr/bin/python
# -*- coding: utf-8 -*-

# import yaml
import os
import json
from pymongo import MongoClient
from datetime import datetime

MONGO_URL = os.environ.get('MONGOHQ_URL')
print(MONGO_URL)
#app.logger.info(MONGO_URL)

client = MongoClient(MONGO_URL)
# Get the database
db = client[MONGO_URL[-15:]]

col_users = db.users
col_groups = db.groups
col_payments = db.payments
col_status = db.status


###################
# status table
###################
def add_status_info(uid, status_info):
    if get_status_info(uid):
        col_status.find_one_and_update({'uid': uid}, {'status_info':status_info})

    else:
        col_status.insert_one({'uid':uid, 'status_info':status_info})

def set_status_info(uid, status_info):
    add_status_info(uid, status_info)

def update_status_info(uid, status_info):
    add_status_info(uid, status_info)

def get_all_status():
    return status_table.all()

def get_status_info(uid):
    status_info = {}
    status_data = col_statu.find_one({'uid': uid})
    if status_data:
        status_info = status_data['status_info']

    return status_info

def delete_status_info(uid):
    col_status.delete_one({'uid': uid})


###################
# user table
###################

def add_user(uid, name, pict, status, follow):
    ''' ユーザ追加 '''
    user_data = {'uid':uid, 'name':name, 'pict':pict, 'status':status, 'follow':follow}

    if get_user(uid):
        col_users.find_one_and_update({'uid': uid}, user_data)
    else:
        col_users.insert_one(user_data)

def get_user(uid):
    user = col_users.find_one({'uid': uid})
    return user

def get_users():
    return col_users.find(None, {_id:0})

def delete_user(uid):
    col_users.delete_one({'uid': uid})

def delete_all_users():
    col_users.delete_many(None)


###################
# group table
###################

def add_group(gid, gtype, name=None):
    ''' グループ追加
        name(Noneの場合), users, accountant, settlement_users, round は生成'''

    if get_group(gid):
        update_group(gid, name)
    else:
        if name is None:
            name = gid

        group_data = {
            'gid':gid,
            'type':gtype,
            'name':name,
            'users':[],
            'accountant':False,
            'settlement_users':[],
            'round_value':100,
            'rates':{},
            'additionals':{},
        }
        col_groups.insert_one(group_data)

def update_group(gid, name=None, accountant=None, round_value=None, rates=None, additionals=None):
    update_data = {}
    if name is not None:
        update_data['name'] = name

    if accountant is not None:
        update_data['accountant'] = accountant

    if round_value is not None:
        update_data['round_value'] = round_value

    if rates is not None:
        update_data['rates'] = rates

    if additionals is not None:
        update_data['additionals'] = additionals

    col_groups.find_one_and_update({'gid': gid}, {'$set': update_data})


def get_groups():
    return col_groups.find(None, {'_id': 0})

def get_group(gid):
    return col_groups.find({'gid': gid})

def delete_group(gid):
    ''' グループ削除 '''
    col_groups.delete_one({'gid': gid})

def delete_all_groups():
    col_groups.delete_many(None)

def add_user_to_group(gid, uid):
    users = get_group_users(gid)
    if uid not in users:
        users.insert(uid)
        col_groups.find_one_and_update({'gid': gid}, {'$set': {'users': users}})

def get_group_users(gid):
    return col_groups.find_one({'gid': gid})['users']

def delete_user_groups(uid):
    for group in get_grpous():
        delete_user_from_group(group['gid'], uid)

def delete_user_from_group(gid, uid):
    users = get_group(gid)['users']
    if uid in users:
        users.remove(uid)
        col_groups.find_one_and_update({'gid': gid}, {'$set': {'users': users}})

def get_user_groups(uid):
    ''' table(group)のusersにuidが含まれるグループデータをリストで渡す '''
    user_groups = []

    for group in get_groups():
        if uid in group['users']:
            user_groups.append(group['gid'])

    return user_groups


###################
# payment table
###################
def add_payment(gid, payment_uid, amount, description=None, receipt=None):
    ''' table(payments) に新しい支払を追加
        id, payment_date, modification_date は生成する
        imageの指定があれば、s3にアップ'''

    payment_date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    modification_date = payment_date
    payment_data = {
        'gid':gid,
        'payment_uid':payment_uid,
        'amount':amount,
        'description':description,
        'receipt':receipt,
        'payment_date':payment_date,
        'modification_date':modification_date,
        'debt_uid': get_group_users(gid),
        'state': 'active'
    }
    col_payments.insert_one(payment_data)

#すべての支払い一覧を返す
def get_payments():
    return col_payments.find(None, {'_id': 0})

#指定グループの全メンバーの支払い一覧を返す
def get_group_payments(gid):
    return col_payments.find({'gid': gid})

#指定ユーザーの全グループでの支払い一覧を返す
def get_user_payments(payment_uid):
    return col_payments.find({'payment_uid': payment_uid})

#指定グループ、ユーザーの支払い一覧を返す
def get_group_user_payments(gid, payment_uid):
    return col_payments.find({'gid': gid, 'payment_uid': payment_uid})

#指定グループ、ユーザーの最後(最新)支払いを返す
#支払い訂正で使用
def get_group_user_latest_payment(gid, payment_uid):
    payment = {}
    group_user_payments = get_group_user_payments(gid, payment_uid)
    if group_user_payments:
        payment = group_user_payments[-1]

    return payment

#指定グループの全メンバーの支払い一覧を削除
def delete_group_payments(gid):
    col_payments.delete_many({'gid': gid})

def get_payment(eid):
    return col_payments.find_one({'_id': eid})

#指定ユーザーの全グループでの支払い一覧を削除
def delete_user_payments(payment_uid):
    col_payments.delete_many({'payment_uid': payment_uid})

#指定グループ、ユーザーの支払い一覧を削除
def delete_group_user_payments(gid, payment_uid):
    col_payments.delete_many({'gid': gid, 'payment_uid': payment_uid})

def delete_payment(eids):
    ''' table(payments) の id=payment_id を削除 or 不可視にする '''
    if not isinstance(eids, (list, tuple)):
        eids = [eids]

    for eid in eids:
        col_payments.delete_one({'_id': eid})

def update_group_user_payments_state(gid, payment_uid, state):
    col_payments.find_one_and_update({'gid': gid, 'payment_uid': payment_uid}, {'$set': {'state': state}})


def update_payment(eid, amount=None, description=None, receipt=None, debt_uid = None):
    ''' table(payments) の amount, description, image を上書きする
        modification_date更新
        imageの指定があれば、s3にアップ'''

    payment = {}

    if amount is not None:
        payment['amount'] = amount

    if description is not None:
        payment['description'] = description

    if receipt is not None:
        payment['receipt'] = receipt

    if debt_uid is not None:
        payment['debt_uid'] = debt_uid

    modification_date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    payment['modification_date'] = modification_date

    col_payments.find_one_and_update({'_id': eid}, {'$set': payment})


if __name__ == "__main__":
    pass
    # col_test = db.test
    # col_test.insert({'uid': 'testuid'})
    # for col_name in db.collection_names(False):
    #     print(col_name)
    #     for doc in db[col_name].find():
    #         print(doc)
    #
    # db.drop_collection('test')

    # for col_name in db.collection_names(False):
    #     print(col_name)
    #     for doc in db[col_name].find():
    #         print(doc)
