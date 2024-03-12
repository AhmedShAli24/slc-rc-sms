import os 
import requests
from flask import Flask, render_template,request,url_for
from pprint import pprint
from googleapiclient.discovery import build
import json

app = Flask(__name__)

TEXT_BELT_API_KEY = os.environ["TEXT_BELT_API_KEY"]

temp = "Hey {name}, did you meet with {ref_name} today"

conversation= {}
save_info = []

@app.get('/')
def Home():
    return render_template('index.html')    

@app.post('/results')
def results():
    data = request.form.get('data')
    fixed_data = data.replace('\r','')
    rows = fixed_data.split("\n")  # we want to split the data into rows
    # split makes it a list now 
    keys =[]
    result= []

    count = 0
    for row in rows: # we are looping through the rows 
        values = row.split(",")
        count += count + 1
        if count == 1:
            keys = values
        else:
            dictionary = {}
            key_index = 0
            for key in keys:
                dictionary[key] = values[key_index]
                key_index += 1
            result.append(dictionary)
            temp_message= request.form.get("template")
            
    for value in result:
            resp = requests.post('https://textbelt.com/text', {
            'phone': value['phone'],
            'message':temp_message.format(First_Name= value['fname']),
            'key': TEXT_BELT_API_KEY,
            "replyWebhookUrl" : 'https://lamb-relaxing-wildly.ngrok-free.app/reply'
            })
            j_Son_value = resp.json()
            textID = j_Son_value.get('textId')
            conversation[textID] = []  
            conversation[textID].append({'from' : 'system' , 'text': temp_message.format(First_Name= value['fname'])} )
            
    with open('conversation.json' , 'w') as file:
        json.dump(conversation, file, indent=4)
    ## makes this json into a dictionary
    #print(j_Son_value)
    return render_template("result.html",jsonValue = j_Son_value)

@app.post("/reply")
def replies():
    reply = request.json
   
    textId =reply.get('textId')
    user_info ={'from' : reply.get('fromNumber') , 'text': reply.get('text')}
    conversation.get(textId).append(user_info)
    
    service = build('sheets', 'v4')

    spreadsheets = service.spreadsheets()

    new_sheet_request = spreadsheets.create(body ={"properties": {"title": "hello"}})

    new_sheet_response = new_sheet_request.execute()

    spreadId = new_sheet_response['spreadsheetId']

    values = [['Text Id','From', "Text"]]
    
    
    values.append([reply.get('textId'),user_info.get('from'),user_info.get('text')])

    body = {
        'values': values
    }

    result = spreadsheets.values().append(
        spreadsheetId=spreadId,
        range="Sheet1",  # Update with your sheet name or range
        valueInputOption="RAW",
        body=body
    ).execute()


    service.close()
    
    
    
    with open('conversation.json' , 'w') as file:
        json.dump(conversation, file, indent=4)
    return "ok"
    "test"
    
app.run(debug=True)