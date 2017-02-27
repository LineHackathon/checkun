#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import boto3

try:
    # 環境変数読み込み
    aws_flag = True
    aws_s3_bucket_name = os.environ['AWS_S3_BUCKET_NAME']

except:
    aws_flag = False
    aws_s3_bucket_name = 'testtest'
#AWS_S3_BUCKET_NAME = 'checkunreceipt'

def is_valid():
	return aws_flag

def get_db(name):
	print('get_db')
	s3 = boto3.resource('s3')

	bucket = s3.Bucket(aws_s3_bucket_name)
	print(aws_s3_bucket_name)
	print(bucket.name)

	file_path = 'db' + '/' + name + '.json'
	key = file_path

	for obj in bucket.objects.all():
		print('key:' + obj.key)
		if obj.key.startswith(key):
			print('hit')
			res = obj.get()
			body = res['Body'].read()
			with open(file_path, 'wb') as fd:
				print(file_path)
				fd.write(body)
				fd.close()
			return file_path

	with open(file_path, 'wb') as fd:
		print('create:' + file_path)
		#fd.write(body)
		fd.close()
		data = open(file_path, 'rb')
		bucket.put_object(Key=key, Body=data)

	return file_path

def update_db(name):
	print('update_db')
	s3 = boto3.resource('s3')

	bucket = s3.Bucket(aws_s3_bucket_name)

	file_path = 'db' + '/' + name + '.json'
	key = file_path
	print('key:' + key)
	data = open(file_path, 'rb')
	bucket.put_object(Key=key, Body=data)

def set_user_pict(uid, pict_name):
	file_path = 'static' + '/' + pict_name
	key = 'users' + '/' + uid + '_' + pict_name
	set_file(key, file_path)

def get_user_pict(uid, pict_name):
	file_path = 'static' + '/' + pict_name
	key = 'users' + '/' + uid + '_' + pict_name
	get_file(key, file_path)

#set /static/file_name to S3
#key=gid/file_name
#file_name:receipt_uid_date_time.jpg
def set_receipt(gid, uid, file_name):
	file_path = 'static' + '/' + file_name
	key = 'groups' + '/' + gid + '/' + uid + '_' + file_name
	set_file(key, file_path)

def set_receipt2(file_name):
	file_path = 'static/' + file_name
	key = 'receipt/' + file_name
	set_file(key, file_path)

#get file and save to /static/file_name
def get_receipt(gid, uid, file_name):
	file_path = 'static' + '/' + file_name
	key = 'groups' + '/' + gid + '/' + uid + '_' + file_name
	get_file(key, file_path)

def delete_receipt(gid, uid, file_name):
	file_path = 'static' + '/' + file_name
	key = 'groups' + '/' + gid + '/' + uid + '_' + file_name
	delete_file(key, file_path)


def set_file(key, file_path):
	s3 = boto3.resource('s3')

	bucket = s3.Bucket(aws_s3_bucket_name)
	#print(bucket.name)
	#print(bucket.objects.all())
	#for obj_summary in bucket.objects.all():
	#	print(obj_summary)
	# Upload a new file
	data = open(file_path, 'rb')
	bucket.put_object(Key=key, Body=data)


def get_file(key, file_path):
	s3 = boto3.resource('s3')

	bucket = s3.Bucket(aws_s3_bucket_name)
	#print(bucket.name)
	#print(bucket.objects.all())
	#for obj_summary in bucket.objects.all():
	#	print(obj_summary)

	obj = bucket.Object(key)
	res = obj.get()
	body = res['Body'].read()

	with open(file_path, 'wb') as fd:
		print(file_path)
		fd.write(body)
		fd.close()

def delete_file(gid, uid, file_name):
	s3 = boto3.resource('s3')

	bucket = s3.Bucket(aws_s3_bucket_name)
	#print(bucket.name)
	#print(bucket.objects.all())
	#for obj_summary in bucket.objects.all():
	#	print(obj_summary)

	obj = bucket.Object(key)
	obj.delete()


if __name__ == "__main__":
	pass
