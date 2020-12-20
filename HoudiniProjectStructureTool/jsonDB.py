import requests,json


url='https://docs.google.com/spreadsheets/d/1w8-NzJHNIui1vQngLymwwIYfvjPVjmZbRQ7K_YnYqKA/edit#gid=0'
token=url.replace('https://docs.google.com/spreadsheets/d/', '').split('/edit#')
initUrl = 'https://spreadsheets.google.com/feeds/list/REPLACETOKEN/SHEETNUM/public/full?alt=json'
sheet1url=initUrl.replace('REPLACETOKEN', token[0]).replace('SHEETNUM', '1')
data=requests.get(sheet1url).json()
content=data['feed']['entry']
projNum=len(content)
for n in range(projNum):
	projname=content[n]['gsx$projectname']['$t']
	rootpath=content[n]['gsx$rootpath']['$t']
	fps=content[n]['gsx$fps']['$t']
	print (projname,rootpath,fps)
