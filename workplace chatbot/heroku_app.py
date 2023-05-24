from flask import Flask, request, Response
import requests
import json
import re

app = Flask(__name__)
wp_token = 'DQVJzYXY3eG1RU3NBSEsya05sM2hqOEMwdkM0YkMwN1RSS3JoeWtYM05oRW'\
    'RNT0JVb0drWEJsX2ZAuYzJJa2wwTWxmY0lqbUNnMElLVUMxMmxuQVhoc09KX2xjUF'\
    'dNSlhjSl8yZAVhLT1VBUGRia1ROXzdzYVAyc082WFlXWVA5ZAXUxTU00dHR1czFkb'\
    '21sUkFwUDQ3WDFuX1Vra1l4ZADVOUWtNQThkQU9rdkVLbEpOOGRsc0Q2dkVsbmt2a'\
    'FhKOS10V2lhbWhn'
wp_headers = {
    'Authorization': 'Bearer ' + wp_token,
    'Content-Type': 'application/json'
}
tr_headers = {"Accept": "application/json"}
query = {
    'key': 'e16b5d87b76092e1854b698a1cc9f465',
    'token': '1594c0a47da4689feb849ef6444572de271cd4ad664a5c46ac33ff31'
    '973733c7'
}
tid_wpid = {'6013adbeb2e35865db709850': '100063124216900'}
id_db = {'zz': {'wp_id': '100063124216900',
                'tr_id': '6013adbeb2e35865db709850'}}


@app.route('/')
def index():
    return 'Last update:2021/02/03 12:27'


@app.route('/', methods=['POST'])
def respond():
    req_act = request.json['action']
    print('action type: ' + req_act['type'])
    if req_act['type'] == 'commentCard':
        req_text = req_act['data']['text']  # comment content
        card = req_act['data']['card']
        commenter = req_act['memberCreator']['username'][-2:]  # wc, yc
        shot_owner = card['name'].split('] [')[2]
        pattern = re.compile(r'@[a-z]+')
        brief = re.sub(pattern, '', req_text)  # remove username
        brief = brief.replace('\n', '').replace(' ', '')
        if len(brief) > 10:
            brief = brief[:10] + r'...'
        # get each card member's trello id
        card_members_id = (get_card_members_id(card['id']))
        if commenter == shot_owner:
            card_members_id.remove(id_db[commenter]['tr_id'])
        # get Workplace id via Trello id
        send_wp_ids = [tid_wpid[i] for i in card_members_id]
        mention_list = pattern.findall(req_text)
        for staff in mention_list:
            send_wp_ids.append(id_db[staff[-2:]]['wp_id'])
        send_wp_ids = list(set(send_wp_ids))
        [send_msg(i, brief, commenter) for i in send_wp_ids]
    return Response(status=200)


def send_msg(wp_id, brief, commenter):
    req_data = request.json['action']['data']
    shot_name = req_data['card']['name']
    short_link = req_data['card']['shortLink']
    text = shot_name + r'\n⚠️You got new comment from ' + commenter + \
        brief + r'\nhttps://trello.com/c/' + short_link
    data = '{"recipient":{"id":"' + wp_id + '"},"message":{"text":"' + \
        text + '"}}'
    response = requests.request(
        'POST',
        'https://graph.facebook.com/me/messages',
        headers=wp_headers,
        data=data.encode('utf-8')
    )
    print(response.text)


def get_card_members_id(card_id):
    url = "https://api.trello.com/1/cards/" + card_id + '/idMembers'
    response = requests.request(
        "GET",
        url,
        headers=tr_headers,
        params=query,
    )
    return json.loads(response.text)


if __name__ == '__main__':
    app.run(debug=True)
