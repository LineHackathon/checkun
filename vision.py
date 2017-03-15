#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import base64
import json
from datetime import datetime
from requests import Request, Session

try:
    # 環境変数読み込み
    vision_flag = True
    vision_url = u'https://vision.googleapis.com/v1/images:annotate?key='
    api_key = os.environ['GOOGLE_API_KEY']

except:
    vision_flag = False
#vision_url = u'https://vision.googleapis.com/v1/images:annotate?key='
#api_key = os.environ['GOOGLE_API_KEY']

def is_money_mark(mark):
	#print(mark)
	if mark == '¥' or mark == '円':
		return True
	else:
		return False

def strip_amount(amount_text):
    amount = ''
    for c in amount_text:
        #print(c)
        if c.isdigit() or is_money_mark(c):
            amount += c

    return amount

def strip_amount_test(amount_text):
	amount = ''
	#amount = amount.strip(' ')
	#ok
	#amount = amount.replace(' ', '')
	#amount = amount.replace(',', '')

	for c in amount_text:
		#print(c)
		if c.isdigit() or is_money_mark(c):
			amount += c

	print(amount)
	#print('¥1,  2  4   56,, 7,8'.replace(' ', '').replace(',', ''))

    #return amount
    

def get_amount(amount_text):
	total_amount_start_index = 0

	#TBD:iはbyte単位になっているので、is_money_markが正常に動作しない
	for i in range(len(amount_text)):
		if amount_text[i].isdigit() or is_money_mark(amount_text[i]):
			total_amount_start_index = i
			break

	print(total_amount_start_index)
	sub_text = amount_text[total_amount_start_index:]
	total_amount_end_index = sub_text.find('\n')
	total_amount = sub_text[0:total_amount_end_index]
	print(total_amount_end_index)
	print(total_amount)

	return total_amount

def extract_amount(receipt_text):
	total_amount_index = receipt_text.find('合計')
	total_amount_len = len('合計')
	print(total_amount_index)
	print(total_amount_len)

	sub_text = receipt_text[(total_amount_index + total_amount_len):]
	total_amount = get_amount(sub_text)

	total_amount = strip_amount(total_amount)

	return total_amount

def analayze_use(receipt_text):
    #とりあえず日時を返す。
    #todo:
    #return 'receipt<' + datetime.now().strftime("%m%d%H%M") + '>'
    return datetime.now().strftime("%m%d%H%M")

def strip_char(text, c):
	strip_text = ''

def recognize_receipt(str_image_path):
    bin_receipt = open(str_image_path, 'rb').read()
    str_encode_file = base64.b64encode(bin_receipt)
    str_url = vision_url
    str_api_key = api_key
    str_headers = {'Content-Type': 'application/json'}

    str_json_data = {
        'requests': [
            {
                'image': {
                    'content': str_encode_file
                },
                'features': [
                    {
                        'type': "TEXT_DETECTION",
                        'maxResults': 10
                    }
                ]
            }
        ]
    }

    print("begin request")
    obj_session = Session()
    obj_request = Request("POST",
                          str_url + str_api_key,
                          data=json.dumps(str_json_data),
                          headers=str_headers
                          )
    obj_prepped = obj_session.prepare_request(obj_request)
    obj_response = obj_session.send(obj_prepped,
                                    verify=True,
                                    timeout=60
                                    )
    print("end request")

    if obj_response.status_code == 200:
        #print obj_response.text
        #with open('data.json', 'w') as outfile:
        #    json.dump(obj_response.text, outfile)
        #NG: ascii error when find 合計
        #return obj_response.text
        #NG: can't find 合計
        #return obj_response.text.encode('utf-8')

        result_dict = json.loads(obj_response.text)
        receipt_text = result_dict['responses'][0]['textAnnotations'][0]['description']
        #print(receipt_text)
        #unicode->str(utf-8)
        return receipt_text.encode('utf-8')
    else:
        return "error"

def get_receipt_amount(str_image_path):
    if vision_flag == False:
        return 0

    #receipt_text = recognize_receipt('static/S__25034777.jpg')
    receipt_text = recognize_receipt(str_image_path)
    use = analayze_use(receipt_text)
    amount = extract_amount(receipt_text)
    if amount is None:
        amount = 0

    return (use, amount)
 
if __name__ == '__main__':
	#extract_amount(test_text)

	#receipt_text = recognize_receipt('static/S__25034777.jpg')
	#extract_amount(receipt_text)

	#receipt_text = recognize_receipt('static/5648161172742.jpg')
	#extract_amount(receipt_text)

	#receipt_text = recognize_receipt('static/5648165471052.jpg')
	#extract_amount(receipt_text)
    
    #amount_use, receipt_amount = get_receipt_amount('static/receipt.jpg')
    #print(amount_use)
    #print(receipt_amount)
	pass
