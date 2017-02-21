#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import base64
import json
from requests import Request, Session

vision_url = u'https://vision.googleapis.com/v1/images:annotate?key='
api_key = os.environ['GOOGLE_API_KEY']

test_text = 'MOS BURGER.\n栄一丁目店\n名古屋市中区栄1丁目7番33号\n電話: 052-220-7750\n☆釧路ザンタレバーガー 甘酢たれ☆\nさっぱりとした醤油ベースのゴマ油と\nネギ香るオリジナルソースがくせになる\n2015/11/11 20:06\nNo. A-0380234\nお客様NO 0023\nイートイン\nオニポテセットM\n-オニオン&ポテト\n¥240\nアイスコーヒーM\n¥310\nセット値引\n-V110\n小計\n¥810\n(内税) 8.0%\n¥60\n合計\n¥81 0\n予頁り金\n¥1,010\nお釣り\n¥200\n通常価格よりも\n110円お得になりました。\n当0\nを0定\n802\nト-\n11111\nた シ目当\nしレ杯\n/6まの2す\nり時とま\nな 入くし\nに 購だ供\nE Tた提\nkee おヒいご\n-ちで\nコ持)\nードお込\nンに\nレ内︶\nブ日円\n'
test_text2 = 'MOS BURGER.\\n\u6804\u4e00\u4e01\u76ee\u5e97\\n\u540d\u53e4\u5c4b\u5e02\u4e2d\u533a\u68041\u4e01\u76ee7\u756a33\u53f7\\n\u96fb\u8a71: 052-220-7750\\n\u2606\u91e7\u8def\u30b6\u30f3\u30bf\u30ec\u30d0\u30fc\u30ac\u30fc \u7518\u9162\u305f\u308c\u2606\\n\u3055\u3063\u3071\u308a\u3068\u3057\u305f\u91a4\u6cb9\u30d9\u30fc\u30b9\u306e\u30b4\u30de\u6cb9\u3068\\n\u30cd\u30ae\u9999\u308b\u30aa\u30ea\u30b8\u30ca\u30eb\u30bd\u30fc\u30b9\u304c\u304f\u305b\u306b\u306a\u308b\\n2015/11/11 20:06\\nNo. A-0380234\\n\u304a\u5ba2\u69d8NO 0023\\n\u30a4\u30fc\u30c8\u30a4\u30f3\\n\u30aa\u30cb\u30dd\u30c6\u30bb\u30c3\u30c8M\\n-\u30aa\u30cb\u30aa\u30f3&\u30dd\u30c6\u30c8\\n\u00a5240\\n\u30a2\u30a4\u30b9\u30b3\u30fc\u30d2\u30fcM\\n\u00a5310\\n\u30bb\u30c3\u30c8\u5024\u5f15\\n-V110\\n\u5c0f\u8a08\\n\u00a5810\\n(\u5185\u7a0e) 8.0%\\n\u00a560\\n\u5408\u8a08\\n\u00a581 0\\n\u4e88\u9801\u308a\u91d1\\n\u00a51,010\\n\u304a\u91e3\u308a\\n\u00a5200\\n\u901a\u5e38\u4fa1\u683c\u3088\u308a\u3082\\n110\u5186\u304a\u5f97\u306b\u306a\u308a\u307e\u3057\u305f\u3002\\n\u5f530\\n\u30920\u5b9a\\n802\\n\u30c8-\\n11111\\n\u305f \u30b7\u76ee\u5f53\\n\u3057\u30ec\u676f\\n/6\u307e\u306e2\u3059\\n\u308a\u6642\u3068\u307e\\n\u306a \u5165\u304f\u3057\\n\u306b \u8cfc\u3060\u4f9b\\nE T\u305f\u63d0\\nkee \u304a\u30d2\u3044\u3054\\n-\u3061\u3067\\n\u30b3\u6301)\\n\u30fc\u30c9\u304a\u8fbc\\n\u30f3\u306b\\n\u30ec\u5185\ufe36\\n\u30d6\u65e5\u5186\\n'


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
    #receipt_text = recognize_receipt('static/S__25034777.jpg')
    receipt_text = recognize_receipt(str_image_path)
    amount = extract_amount(receipt_text)
    if amount is None:
        amount = 0

    return amount
 
if __name__ == '__main__':
	#extract_amount(test_text)

	#receipt_text = recognize_receipt('static/S__25034777.jpg')
	#extract_amount(receipt_text)

	#receipt_text = recognize_receipt('static/5648161172742.jpg')
	#extract_amount(receipt_text)

	#receipt_text = recognize_receipt('static/5648165471052.jpg')
	#extract_amount(receipt_text)
	pass
