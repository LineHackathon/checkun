#!/usr/bin/python
# -*- coding: utf-8 -*-

# import yaml
import os
import json
from pymongo import MongoClient

MONGO_URL = os.environ.get('MONGOHQ_URL')
print(MONGO_URL)

if MONGO_URL:
	client = MongoClient(MONGO_URL)
    # Get the database
	db = client['checkun_db']
else:
	client = MongoClient('mongodb://localhost:27017/')
	db = client['test_db']

col_users = db['users']
col_groups = db['groups']
col_hist_groups = db['hist_groups']

####################################################
# user collection(table)
#
# users = [
#     {
#         id: user_id,
#         groups: [{id:group_id_1, state:flg}, {id:group_id_2, state:flg}, ...]
#     },
#     {
#         id: user_id,
#         groups: [{id:group_id_1, state:flg}, {id:group_id_2, state:flg}, ...]
#     },
#     ...
# ]
# 
# ユーザーテーブル
# シンプルにユーザーIDと所属するグループID一覧のみ管理する(複数のグループに所属可能)
#
# ・ユーザー情報はLine APIのget_profile()でその都度取得
# ・ユーザーテーブルに直接group_idを追加/削除できない。
#   グループテーブルにユーザーを登録/削除する時、このテーブルにgroup_idを自動追加/削除
# ・グループの情報はgroupテーブルから取得
# ・(T.B.D)清算中の場合、group_id:1 / 精算完了の場合、group_id:0
#
# 関数一覧
# ・register_user
#     ユーザー登録(bot追加時)。初期情報は{}
# ・get_groups_of_user
#     所属グループの全て、或いは、清算中のみ取得
# ・delete_user
####################################################

#uinfo:{groups:[{}]}
def register_user(uid):
	if uid:
		user = {}
		user['id'] = uid
		user['info'] = {}
		user['groups'] = []
		col_users.insert_one(user)

def is_user_registerd(uid):
	flag = False
	if uid:
		user = col_users.find_one({'id':uid})
		if user:
			flag = True

	return flag


def get_users():
	users = []
	all_users = col_users.find()
	for user in all_users:
		users.append(user['id'])

	return users

#所属グループ一覧を取得
#all:falseの場合、active(清算中)グループのみ
def get_groups_of_user(uid, all=False):
	groups_of_user = []
	if uid:
		user = col_users.find_one({'id':uid})
		if user:
			groups = user['groups']
			for group in groups:
				if all:
					groups_of_user.append(group['id'])
				else:
					if group['state']:
						groups_of_user.append(group['id'])

	return groups_of_user

def add_group_to_user(gid, uid):
	if uid:
		user = col_users.find_one({'id': uid})
		if user:
			user_groups = user['groups']
			group = {'id': gid, 'state': 1}
			user_groups.append(group)
			col_users.update({'id': uid}, {'$set': {'groups': user_groups}})

def delete_group_from_user(gid, uid):
	if uid:
		user = col_users.find_one({'id': uid})
		if gid:
			user_groups = user['groups']
			user_groups.append(gid)
			col_users.update({'id': uid}, {'$set': {'groups': user_groups}})


def delete_user(uid):
	if uid:
		col_users.delete_one({'id': uid})

def delete_all_users():
	all_users = col_users.find()
	for user in all_users:
		delete_user(user['id'])

####################################################
# group collection(table)
#
#
# groups = [
#     {
#         id: group_id,
#         info: {name: group_name}, #必要なら、グループ情報管理用テーブルを別途追加
#         receipts:[{file_name:receipt.jpg, id:user_id}]
#         #支払い金額
#         users:{user_id_1: {amount:[a1, a2, ...]}, user_id_2: {amount:[a1, a2, ...]}, ...}
#         #精算金額(axが正数の場合は支払い、負数の場合は受け取る)
#         adjustments:{user_id_1: {user_id_2:a1, user_id_2:a2}, user_id_2:{user_id_1:a1, user_id_3:a3}, ...}
#     },
#     {
#         id: group_id,
#         name: group_name,
#         users:{user_id_1: {amount:[a1, a2, ...]}, user_id_2: {amount:[a1, a2, ...]}, ...}
#         adjustments:{}
#     },
#     ...
# ]
#
# グループテーブル
# グループ内の各ユーザーの支払いを管理
#
####################################################

#group作成
#group名はLine APIから取得できない?ので、必要なら追加
def create_group(gid, ginfo={}):
	if gid:
		group = {}
		group['id'] = gid
		group['info'] = ginfo
		group['receipts'] = []
		#group['users'] = []
		group['users'] = {}
		group['adjustments'] = {}
		col_groups.insert_one(group)

def get_groups(all=False):
	groups = []
	all_groups = col_groups.find()
	for group in all_groups:
		groups.append(group['id'])

	if all:
		all_groups = col_groups.find()
		for group in all_groups:
			groups.append(group['id'])

	return groups

#group名など更新
def update_group_info(gid, ginfo={}):
	if gid:
		col_groups.update({'id': gid}, {'$set': {'info': ginfo}})

def get_users_in_group(gid):
	users_in_group = []
	if gid:
		group = col_groups.find_one({'id': gid})
		group_users = group['users']
		for uid in group_users.keys():
			users_in_group.append(uid)
		
		#for user in group_users:
		#	users_in_group.append(user['id'])
	
	return users_in_group

#精算グループへ招待
#usersテーブルのユーザーuidに所属グループgidを追加
def invite_user_to_group(uid, gid):
	if gid:
		#query = {'id': gid}
		group = col_groups.find_one({'id': gid})
		group_users = group['users']
		#group_users.append({'id': uid, 'amount': []})
		group_users[uid] = {'amount': []}
		col_groups.update({'id': gid}, {'$set': {'users': group_users}})

		add_group_to_user(gid, uid)

#領収書追加(/static/receipt_file)
#todo:add to aws S3
def add_group_user_receipt(gid, uid, receipt_file):
	if gid:
		#query = {'id': gid}
		group = col_groups.find_one({'id': gid})
		group_receipts = group['receipts']
		group_receipt = {'file_name': receipt_file, 'id': uid}
		group_receipts.append(group_receipt)
		col_groups.update({'id': gid}, {'$set': {'receipts': group_receipts}})

#todo:get receipt image from aws S3 and save to /static
def get_group_user_receips(gid, uid):
	user_receipts = []
	if gid:
		group = col_groups.find_one({'id': gid})
		group_receipts = group['receipts']
		if group_receipts:
			for receipt in group_receipts:
				if (receipt['id'] == uid):
					user_receipts.append(receipt['file_name'])

	return user_receipts

#todo:S3
def get_group_all_receips(gid):
	all_receipts = []
	if gid:
		group = col_groups.find_one({'id': gid})
		group_receipts = group['receipts']
		if group_receipts:
			for receipt in group_receipts:
				all_receipts.append(receipt['file_name'])

	return all_receipts

#グループ内のユーザーの支払い金額追加(複数支払い対応)
def add_group_user_amount(gid, uid, amount):
	if gid:
		#query = {'id': gid}
		group = col_groups.find_one({'id': gid})
		group_users = group['users']
		group_user = group_users[uid]
		user_amounts = group_user['amount']
		user_amounts.append(amount)
		col_groups.update({'id': gid}, {'$set': {'users': group_users}})
	

#グループ内のユーザーの支払い金額一覧取得
def get_group_user_amounts(gid, uid):
	user_amounts = []
	if gid:
		group = col_groups.find_one({'id': gid})
		group_users = group['users']
		group_user = group_users[uid]
		user_amounts = group_user['amount']
		if user_amounts:
			for amount in user_amounts:
				user_amounts.append(amount)

	return user_amounts
	

#グループ内のユーザー数取得
def get_group_user_count(gid):
	if gid:
		#query = {'id': gid}
		group = col_groups.find_one({'id': gid})
		group_users = group['users']
		return group_users.count

#グループ内のユーザーの支払いを更新(修正)
def update_group_user_amount(gid, uid, index, amount):
	if gid:
		#query = {'id': gid}
		group = col_groups.find_one({'id': gid})
		group_users = group['users']
		group_user = group_users[uid]
		user_amounts = group_user['amount']
		if (index < user_amounts.count):
			user_amounts[index] = amount

		col_groups.update({'id': gid}, {'$set': {'users': group_users}})
	

#グループからユーザーを削除
#usersテーブルのユーザーuidの所属グループgidも削除
def delete_group_user(gid, uid):
	if gid:
		#query = {'id': gid}
		group = col_groups.find_one({'id': gid})
		group_users = group['users']
		group_users.remove(uid)
		col_groups.update({'id': gid}, {'$set': {'users': group_users}})

		delete_group_from_user(gid, uid)

#グループ削除
#usersテーブルのユーザーuid(複数)の所属グループgidも削除
def delete_group(gid):
	if gid:
		col_groups.delete_one({'id': gid})

		users = col_users.find()
		for user in users:
			delete_group_from_user(gid, user['id'])

def delete_all_groups():
	all_groups = col_groups.find()
	for group in all_groups:
		delete_group(group['id'])

#精算完了後別テーブルへ移動(テーブルが大きくなると、パフォーマンスに影響が出るので)
#usersテーブルのユーザーが所属するグループの状態をfalseに変更
def move_to_history(gid):
	pass



if __name__ == "__main__":
	pass
