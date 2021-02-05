import requests
import json
 
 
def get_wp_staff():
    url = 'https://graph.facebook.com/company/organization_members'
    token = 'asd'  # demo
    '''
    proxies = {
        'https': 'https://okapi.tnn:14239'
    }
    '''
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
 
    response = requests.request(
        'GET',
        url,
        headers=headers,
        #proxies=proxies
    )
    return json.loads(response.text)['data']
 
 
def get_trello_staff():
    url = "https://api.trello.com/1/organizations/rpprodbuild/members"
 
    headers = {
        "Accept": "application/json"
    }
 
    query = {
        'key': 'qwe',  # demo
        'token': 'asd',  # demo
    }
 
    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=query
    )
 
    return json.loads(response.text)
 
 
tid_to_wpid = {}
username_to_id = {}
for ti in get_trello_staff():
    for wi in wp_usr_list:
        if ti['fullName'] in wi['fullName']:
            tid_to_wpid[ti['id']] = wi['id']
            username_to_id[ti['username'][-2:]
                           ] = {'wp_id': wi['id'], 'tr_id': ti['id']}
print(tid_to_wpid)
print(username_to_id)
