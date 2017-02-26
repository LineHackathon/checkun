#!/usr/bin/python
# -*- coding: utf-8 -*-

from tinydb import TinyDB, Query
import aws3
import vision
import os
from datetime import datetime

#user table
#groups table
#payments table
#debt table?

#print('get db start')
#test_db = TinyDB('db/test.json')
#test_db_file = aws3.get_db('test1')
#print(test_db_file)
#test_db = TinyDB(test_db_file)

try:
    # 環境変数読み込み
    aws3_db_name = os.environ['CHECKUN_DB_NAME']

except:
    aws3_db_name = 'checkun'

db_file = aws3.get_db(aws3_db_name)
#test
#db_file = 'db/checkun.json'
#print(db_file)
db = TinyDB(db_file, indent=2, sort_keys=True, separators=(',', ': '))
#print('get db end')

user_table = db.table('users')
group_table = db.table('groups')
payment_table = db.table('payments')
debt_table = db.table('debt')

status_db_name = 'db/status.json'
status_db = TinyDB(status_db_name, indent=2, sort_keys=True, separators=(',', ': '))
status_table = status_db.table('status')

def update_db():
    if aws3.is_valid() == True:
        aws3.update_db(aws3_db_name)

def update_receipt(gid, payment_uid, receipt):
    if aws3.is_valid() == True:
        aws3.set_receipt(gid, payment_uid, receipt)

def update_user_pict(uid, pict):
    if aws3.is_valid() == True:
        aws3.set_user_pict(uid, pict)


###################
# status table
###################
def add_status_info(uid, status_info):
    if is_user_status_exist(uid):
        update_status_info(uid, status_info)
    else:
        status_table.insert({'uid':uid, 'status_info':status_info})

def set_status_info(uid, status_info):
    update_status_info(uid, status_info)

def get_all_status():
    return status_table.all()

def get_status_info(uid):
    #print('get_status_info:' + uid)
    status_info = {}
    if is_user_status_exist(uid):
        user_status = status_table.search(Query().uid == uid)
        if len(user_status) > 0:
            status_info = user_status[0]['status_info']

    return status_info

def get_status_info_element_with_name(uid, info_ele_name):
    info_element = {}
    if is_user_status_exist(uid):
        user_status = status_table.search(Query().uid == uid)
        if len(user_status) > 0:
            status_info = user_status[0]['status_info']
            info_element[info_ele_name] = status_info[info_ele_name]

    return info_element

def update_status_info(uid, status_info):
    #print('update_status_info:' + uid)
    if is_user_status_exist(uid):
        print(uid + ' exist')
        status_table.update({'uid':uid, 'status_info':status_info}, Query().uid == uid)
    else:
        status_table.insert({'uid':uid, 'status_info':status_info})

def update_status_info_element(uid, info_ele_name, info_ele_value):
    if is_user_status_exist(uid):
        user_status = status_table.search(Query().uid == uid)
        if len(user_status) > 0:
            status_info = user_status[0]['status_info']
            status_info[info_ele_name] = info_ele_value
            status_table.update({'uid':uid, 'status_info':status_info}, Query().uid == uid)

def delete_status_info(uid):
    status_table.remove(Query().uid == uid)

def is_user_status_exist(uid):
    return status_table.contains(Query().uid == uid)

def is_status_exist(status):
    if status is not None and len(status) > 0:
        return True
    else:
        return False

###################
# user table
###################
def add_user(uid, name, pict, status, follow):
    ''' ユーザ追加 '''
    if is_user_exist(uid):
        update_user(uid,name,pict,status,follow)
        return
    else:
        user_table.insert({'uid':uid, 'name':name, 'pict':pict, 'status':status, 'follow':follow})

    #save pict to user folder in S3
    # if pict is not None:
    #     update_user_pict(uid, pict)

    update_db()

#return list
def get_user(uid):
    users = user_table.search(Query().uid == uid)

    if len(users) > 1:
        print '{} in user_table is more than one!!'.format(uid)
    if users:
        return users[0]
    return None

#必要なら分割update_user_xxx
def update_user(uid,name,pict,status,follow):
    new_user_data = {'uid':uid, 'name':name, 'pict':pict, 'status':status, 'follow':follow}

    if new_user_data != get_user(uid):
        user_table.update(new_user_data, Query().uid == uid)
        update_db()

#return list
def get_users():
    return user_table.all()
    #return user_table.get(Query().uid == 'uid')
    #return user_table.get(eid = 'uid')

def delete_user(uid):
    user_table.remove(Query().uid == uid)
    update_db()

def delete_all_users():
    user_table.purge()
    update_db()

def is_user_exist(uid):
    return user_table.contains(Query().uid == uid)

###################
# group table
###################
def add_group(gid, gtype, name=None):
    ''' グループ追加
        name(Noneの場合), users, accountant, settlement_users, round は生成'''

    if is_group_exist(gid):
        update_group(gid, name)
    else:
        if name is None:
            name = gid

        group_table.insert({
            'gid':gid,
            'type':gtype,
            'name':name,
            'users':[],
            'accountant':False,
            'settlement_users':[],
            'round_value':100,
            'rates':{},
            'additionals':{},
        })

    update_db()

#必要なら分割update_group_xxx
def update_group(gid, name=None, accountant=None, round_value=None, rates=None, additionals=None):
    group = {}
    if name is not None:
        group['name'] = name

    if accountant is not None:
        group['accountant'] = accountant

    if round_value is not None:
        group['round_value'] = round_value

    if rates is not None:
        group['rates'] = rates

    if additionals is not None:
        group['additionals'] = additionals

    group_table.update(group, Query().gid == gid)

    update_db()

def get_groups():
    return group_table.all()
    #return group_table.get(eid = 'gid')

def get_group_info(gid):
    groups = group_table.search(Query().gid == gid)

    if groups:
        return groups[0]
    return None

def delete_group(gid):
    ''' グループ削除 '''
    group_table.remove(Query().gid == gid)
    # payment_table.remove(Query().gid == gid)

    update_db()

def delete_all_groups():
    group_table.purge()
    update_db()


def add_user_to_group(gid, uid):
    group = group_table.search(Query().gid == gid)

    #if group is not None:
    if len(group) == 1:
        users = group[0]['users']
        for user_id in users:
            if user_id == uid:
                return

        users.append(uid)
        group[0]['users'] = users
        group_table.update(group[0], Query().gid == gid)

        update_db()

def get_group_users(gid):
    users = []

    group = group_table.search(Query().gid == gid)

    #if group is not None:
    if len(group) == 1:
        users = group[0]['users']

    return users

def delete_user_from_group(gid, uid):
    group = group_table.search(Query().gid == gid)

    #if group is not None:
    if len(group) == 1:
        users = group[0]['users']
        for user_id in users:
            if user_id == uid:
                users.remove(user_id)
                break

        group[0]['users'] = users
        group_table.update(group[0], Query().gid == gid)

        update_db()

def get_user_groups(uid):
    ''' table(group)のusersにuidが含まれるグループデータをリストで渡す '''
    groups = []

    all_groups = group_table.all()
    for g in all_groups:
        users = g['users']
        for user_id in users:
            if user_id == uid:
                groups.append(g['gid'])
                break

    return groups

#とりあえずsettlement_usersを使用。usersにflag追加しても対応可能
def add_settlement_user_to_group(gid, uid):
    group = group_table.search(Query().gid == gid)

    #if group is not None:
    if len(group) == 1:
        users = group[0]['settlement_users']
        for user_id in users:
            if user_id == uid:
                return

        users.append(uid)
        group[0]['settlement_users'] = users
        group_table.update(group[0], Query().gid == gid)

        update_db()

def get_group_settlement_users(gid):
    settlement_users = []

    group = group_table.search(Query().gid == gid)

    #if group is not None:
    if len(group) == 1:
        settlement_users = group[0]['settlement_users']

    return settlement_users

def delete_settlement_user_from_group(gid, uid):
    group = group_table.search(Query().gid == gid)

    #if group is not None:
    if len(group) == 1:
        users = group[0]['settlement_users']
        for user_id in users:
            if user_id == uid:
                users.remove(user_id)
                break

        group[0]['settlement_users'] = users
        group_table.update(group[0], Query().gid == gid)

        update_db()

def get_groups_payments(gid):
    return payment_table.search(Query().gid == gid)

#usersではなくsettlement_usersから?userが所属するすべてのgroupの支払い一覧を返す?
def get_user_groups_payments(uid):
    ''' table(group)のusersにuidが含まれるグループのpaymentsをリストで渡す '''
    payments = payment_table.search(Query().gid == gid)
    return payments

def is_group_exist(gid):
    return group_table.contains(Query().gid == gid)

def is_group_user_exist(gid, uid):
    group = group_table.search(Query().gid == gid)

    #if group is not None:
    if len(group) == 1:
        users = group[0]['settlement_users']
        for user_id in users:
            if user_id == uid:
                return True

    return False


###################
# payment table
###################
def add_payment(gid, payment_uid, amount, description=None, receipt=None):
    ''' table(payments) に新しい支払を追加
        id, payment_date, modification_date は生成する
        imageの指定があれば、s3にアップ'''

    p_id = calc_payment_id(gid, payment_uid)
    payment_date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    modification_date = payment_date
    payment_table.insert({  'gid':gid,
                            'payment_uid':payment_uid,
                            'p_id':p_id,
                            'amount':amount,
                            'description':description,
                            'receipt':receipt,
                            'payment_date':payment_date,
                            'modification_date':modification_date,
                            'debt_uids': get_group_users(gid)
                        })

    #save receipt to user folder in S3
    if receipt is not None:
        update_receipt(gid, payment_uid, receipt)
        # pass

    update_db()

#すべての支払い一覧を返す
def get_payments():
    return payment_table.all()

#指定グループの全メンバーの支払い一覧を返す
def get_group_payments(gid):
    return payment_table.search(Query().gid == gid)

#指定ユーザーの全グループでの支払い一覧を返す
def get_user_payments(payment_uid):
    return payment_table.search(Query().payment_uid == payment_uid)

#指定グループ、ユーザーの支払い一覧を返す
def get_group_user_payments(gid, payment_uid):
    return payment_table.search((Query().gid == gid) & (Query().payment_uid == payment_uid))

#一覧を返すが、基本１つ
def get_group_user_payments_with_pid(gid, payment_uid, pid):
    return payment_table.search((Query().gid == gid) & (Query().payment_uid == payment_uid) & (Query().p_id == pid))

#指定グループ、ユーザーの最後(最新)支払いを返す
#支払い訂正で使用
def get_group_user_latest_payment(gid, payment_uid):
    payment = {}
    group_user_payments = get_group_user_payments(gid, payment_uid)
    if len(group_user_payments) > 0:
        payment = group_user_payments[len(group_user_payments) - 1]

    return payment

#指定グループの全メンバーの支払い一覧を削除
def delete_group_payments(gid):
    payment_table.remove(Query().gid == gid)

    update_db()

def get_payment(eid):
    return payment_table.get(eid=eid)

#指定ユーザーの全グループでの支払い一覧を削除
def delete_user_payments(payment_uid):
    payment_table.remove(Query().payment_uid == payment_id)

    update_db()

#指定グループ、ユーザーの支払い一覧を削除
def delete_group_user_payments(gid, payment_uid):
    payment_table.remove((Query().gid == gid) & (Query().payment_uid == payment_uid))

    update_db()

#指定グループ、ユーザー、pidの支払い(基本１つ)を削除
def delete_group_user_payments_with_pid(gid, payment_uid, pid):
    payment_table.remove((Query().gid == gid) & (Query().payment_uid == payment_uid) & (Query().p_id == pid))

    update_db()

#指定グループ、ユーザー、pidの支払いを削除
def delete_group_user_latest_payment(gid, payment_uid):
    group_user_payments = get_group_user_payments(gid, payment_uid)
    if len(group_user_payments) > 0:
        payment_id = len(group_user_payments)
        print(payment_id)
        payment_table.remove((Query().gid == gid) & (Query().payment_uid == payment_uid) & (Query().p_id == payment_id))

    update_db()

def delete_payment(eids):
    ''' table(payments) の id=payment_id を削除 or 不可視にする '''
    if not isinstance(eids, (list, tuple)):
        eids = [eids]

    payment_table.remove(eids = eids)

    update_db()

#最後(最新)支払いを更新
def update_latest_payment(gid, payment_uid, amount=None, description=None, receipt=None):
    group_user_payments = get_group_user_payments(gid, payment_uid)
    if len(group_user_payments) > 0:
        payment_id = len(group_user_payments)
        update_payment_with_id(gid, payment_uid, payment_id, amount, description, receipt)

def update_payment_with_id(gid, payment_uid, pid, amount=None, description=None, receipt=None):
    ''' table(payments) の amount, description, image を上書きする
        modification_date更新
        imageの指定があれば、s3にアップ'''
    payment = {}

    group_user_payments = get_group_user_payments_with_pid(gid, payment_uid, pid)
    if len(group_user_payments) > 0:
        payment = group_user_payments[0]

    if amount is not None:
        payment['amount'] = amount

    if description is not None:
        payment['description'] = description

    if receipt is not None:
        payment['receipt'] = receipt
        #save receipt to user folder in S3
        update_receipt(gid, payment_uid, receipt)

    modification_date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    payment['modification_date'] = modification_date
    payment_table.update(payment, (Query().gid == gid) & (Query().payment_uid == payment_uid) & (Query().p_id == pid))

    update_db()

def update_payment(eids, amount=None, description=None, receipt=None, debt_uid = None):
    ''' table(payments) の amount, description, image を上書きする
        modification_date更新
        imageの指定があれば、s3にアップ'''
    if not isinstance(eids, (list, tuple)):
        eids = [eids]

    payment = {}

    if amount is not None:
        payment['amount'] = amount

    if description is not None:
        payment['description'] = description

    if receipt is not None:
        payment['receipt'] = receipt
        #save receipt to user folder in S3
        #aws3.set_receipt(uid, receipt)

    if debt_uid is not None:
        payment['debt_uid'] = debt_uid

    modification_date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    payment['modification_date'] = modification_date
    # payment_table.insert(payment, Query().payment_id == payment_id)
    payment_table.update(payment, eids = eids)

    update_db()

def calc_payment_id(gid, payment_uid):
    group_user_payments = get_group_user_payments(gid, payment_uid)
    pid = len(group_user_payments) + 1
    return pid

#debt
#独立tableでも、groupに追加しても良い
#誰が誰に支払いするかの一覧になる


if __name__ == "__main__":
    gid = 'C5114ec5d843ca9a3ff4aa3fdaef329c5'
    # user add test
    for i in range(10):
        uid = 'test{}'.format(i)
        add_user(uid, uid, None, None, True)
        add_user_to_group(gid, uid)
    #
    # # payment add test
    # for i in range(10):
    #     uid = 'test{}'.format(i)
    #     amount = i*1000
    #     add_payment(gid, uid, amount)
