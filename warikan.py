#!/usr/bin/python
# -*- coding: utf-8 -*-

from pprint import pprint

def calc_warikan(amounts):
    members = amounts.keys()
    payments = []
    for k, v in amounts.items():
        payments.append({'payment_uid': k, 'amount': v, 'debt_uid': members})
    return calc_warikan3(members, payments, 0)

def calc_warikan2(members, amounts, additionals={}, rates={}):
    payments = []
    for k, v in amounts.items():
        payments.append({'payment_uid': k, 'amount': v, 'debt_uid': members})

    return calc_warikan3(members, payments, 0, additionals, rates)


def calc_warikan3(members, payments, _round=100, additionals={}, rates={}):
    rate_default = 1.0
    additional_default = 0

    print members
    print payments
    print _round
    print additionals
    print rates

    totals={}
    amounts={}

    # additionals の処理
    for k, v in additionals.items():
        payments.append({'payment_uid': k, 'amount': -v, 'debt_uid': members})

    # 支払データをまとめる
    for payment in payments:
        users = payment['debt_uid']
        amount = payment['amount']
        amounts[payment['payment_uid']] = amounts.get(payment['payment_uid'], 0) + amount

        # 割り勘の分母を求める
        denomi = 0.0
        for user in users:
            denomi += rates.get(user, rate_default)
        # print 'denomi:{}'.format(denomi)

        # 割り振ったあとの余りを求める
        average = int(amount // denomi)
        remainder = amount
        for user in users:
            remainder -= int(average * rates.get(user, rate_default))
        # print 'average:{}'.format(average)
        # print 'remainder:{}'.format(remainder)

        # 負債の計算
        for i, user in enumerate(users):
            totals[user] = totals.get(user,0) + int(average * rates.get(user, 1.0))
            # totals[user] += additionals.get(user,0)
            if(i < remainder):
                totals[user] += 1
        # print 'totals:{}'.format(totals)

    # 渡す額，貰う額を決定
    gives={}
    takes={}
    transfer_total = 0
    for member in members:
        diff = totals.get(member, 0) - amounts.get(member, 0)
        # print diff
        if(diff > 0):
            gives[member] = diff
            takes[member] = 0
        else:
            gives[member] = 0
            takes[member] = -diff
        transfer_total += abs(diff)
    # print ''
    # print 'amounts:{}'.format(amounts)
    # print 'gives:{}'.format(gives)
    # print 'takes:{}'.format(takes)
    # print 'transfer_total:{}'.format(transfer_total)

    # お金のやり取りを計算
    transfer_list = []
    while(transfer_total != 0):
        give_max_member = max(gives.items(), key=lambda x:x[1])[0]
        take_max_member = max(takes.items(), key=lambda x:x[1])[0]
        transfer = min(gives[give_max_member], takes[take_max_member])
        transfer_total -= transfer * 2
        gives[give_max_member] -= transfer
        takes[take_max_member] -= transfer
        transfer_list.append({'from': give_max_member, 'to': take_max_member, 'amount': transfer})
        # print transfer_total
    # print transfer_list

    # 丸め計算
    if _round > 1:
        for transfer in transfer_list:
            amount = float(transfer['amount'])
            amount = round(amount / _round) * _round
            # transfer['amount'] = ((transfer['amount'] + _round/2) // _round) * _round
            transfer['amount'] = int(amount)
        # 0円を削除
        for transfer in transfer_list[:]:
            if transfer['amount'] == 0:
                transfer_list.remove(transfer)

    return transfer_list


if __name__ == "__main__":
    # レンタカー ：9,800円（ユーザーAが自宅近くのレンタカー屋でカード支払い）
    # ガソリン代 ：7,600円（ユーザーBがガソリンスタンドでカード支払い）
    # 高速道路料金 ：7,400円（ユーザーCのETCカードで支払い）
    # フリーパス：17,600円（ユーザーDがWeb予約で事前決済）
    members = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    payments = [
        {'payment_uid': 'A', 'amount': 9800, 'debt_uid': [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
            # 'A', 'B', 'C', 'D', 'E', 'F', 'G',
        ]},
        {'payment_uid': 'B', 'amount': 7600, 'debt_uid': [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
            # 'A', 'B', 'C', 'D', 'E', 'F', 'G',
        ]},
        {'payment_uid': 'C', 'amount': 7400, 'debt_uid': [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
            # 'A', 'B', 'C', 'D', 'E', 'F', 'G',
        ]},
        {'payment_uid': 'D', 'amount': 17600, 'debt_uid': [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
            # 'A', 'B', 'D',
        ]},
    ]
    additionals = {
        # 'H': 20000,
    }
    rates = {
        'F': 1.1,
    }
    transfer_list = calc_warikan3(members, payments, 0, additionals, rates)
    pprint(transfer_list)

    transfer_list = calc_warikan3(members, payments, 10, additionals, rates)
    pprint(transfer_list)

    # members = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    # amounts = {
    #     'A': 9800,
    #     'B': 7600,
    #     'C': 7400,
    #     'D': 17600,
    # }
    # additionals = {
    #     'H': 2000,
    # }
    # rates = {
    #     'F': 1.1,
    # }
    # transfer_list = calc_warikan2(members, amounts, additionals, rates)
    # pprint(transfer_list)

    # amounts = {
    #     'A': 9800,
    #     'B': 7600,
    #     'C': 7400,
    #     'D': 17600,
    #     'E': 0,
    #     'F': 0,
    #     'G': 0,
    #     'H': 0,
    # }
    # transfer_list = calc_warikan(amounts)
    # pprint(transfer_list)
