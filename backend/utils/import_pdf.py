import os 
import json 
import requests


projects = [('WNS', 'f6da25c7-8275-4b2c-bbab-cc4f8ec5e029'), ('Trident', 'a64e63bc-c4c9-4506-b5f5-3143f61b78c0'),\
           ('Nestle', 'f50f2bf9-faa8-406f-999c-89d21bad6587'), ('Pernod Ricard', '4e9ef0bf-e4de-4b8f-a107-e5fd73bf2cee'),\
            ('Ashirvad Pipes', '47242578-ced9-4344-bc53-c1fb8d8bbddb'), \
            ] 

def parse_project(project_name, project_id): 
    # Load policies 
    url = 'https://nlp-dashboard.chatteron.io/api/project_file/?projectId={}&size={}&page=1'.format(project_id, 200) 
    headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjExOTk3MDIyLCJqdGkiOiIwOGMyYWU1YTczODY0NTNjYjExMDg4MWQzOWFhZjRjMiIsInVzZXJfaWQiOjF9.ICXugrwJh-ANRPTIjLcHmtP_GJgxyHhhug8HsmME1Fk'}
    response = requests.get(url, headers=headers)
    data  = response.json()
    for item in data["results"]: 
        # download pdf file 
        data_url = 'https://nlp-dashboard.chatteron.io/api/project_file/{}/download/'.format(item['id']) 
        r = requests.get(data_url) 
        path = 'data/all_pdfs/{}_{}/{}.pdf'.format(project_name, project_id, item['id'])
        if not os.path.exists(os.path.dirname(path)): 
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:  
            f.write(r.content)
        
        if r.status_code == 200 and 'errors' not in r.text:
            print(path)
            payload={'name': item["name"], 'metadata': json.dumps({'project_name': project_name, 'project_id': project_id})}
            files=[
                    ('file',(path, open(path,'rb'), 'application/pdf'))
                ]
            headers = {}
            response = requests.request("POST", 'http://localhost:8005/search_file/', headers=headers, data=payload, files=files)
            print(response.status_code)
        else: 
            print("ELSE")


def main(): 
    for project in projects: 
        parse_project(project[0], project[1])


if __name__== '__main__': 
    main()