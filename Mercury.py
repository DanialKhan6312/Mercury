from flask import Flask, Response, request
import requests
from twilio.twiml.messaging_response import Message, MessagingResponse
from googlesearch import search
from bs4 import BeautifulSoup
from gensim.summarization import summarize
symp=[]
dis=''
url1 = "https://endlessmedicalapi1.p.rapidapi.com/InitSession"
url2 = "https://endlessmedicalapi1.p.rapidapi.com/AcceptTermsOfUse"
passp="I have read, understood and I accept and agree to comply with the Terms of Use of EndlessMedicalAPI and Endless Medical services. The Terms of Use are available on endlessmedical.com"


headers = {
    'x-rapidapi-key': "7915225bd7msh73a301162699522p1a0345jsn65d195cdd8f4",
    'x-rapidapi-host': "endlessmedicalapi1.p.rapidapi.com"
    }

id = requests.request("GET", url1, headers=headers).json()["SessionID"]
querystring1 = {"SessionID":id,"passphrase":passp}
terms=requests.request("POST", url2, headers=headers,params = querystring1)

app = Flask(__name__)

stage = 1
@app.route("/")
def check_app():
    
    return Response("It works!")
@app.route("/twilio",methods=["POST"])
def incoming_msg():
    global stage, headers, id, symp, passp,dis
    input= request.form["Body"]
    response = MessagingResponse()
    message = Message()
    response.append(message)
    print (input)
    symps=''
    if stage ==1:
        if input.lower() == "start app":
            out = "Hello, welcome to Mercury the first and only SMS based health info center\n\nTo begin, enter the patient\'s age"
            stage = stage+1
        else:
            out = "Please use the phrase \"Start app\" to begin"
    elif stage == 2:
        url3 = "https://endlessmedicalapi1.p.rapidapi.com/UpdateFeature"
        querystring2 = {"SessionID": id, "name": 'age', "value": input}
        age = requests.request("POST", url3, headers=headers, params=querystring2)
        stage = stage+1
        out = "Age of "+input+" confirmed, now please enter a symptom"
    elif stage == 3:

        if input.lower() == "done":
            out = "Analysing symptoms"
            url4 = "https://endlessmedicalapi1.p.rapidapi.com/Analyze"
            querystring3 = {"SessionID": id}
            diag = requests.request("GET", url4, headers=headers, params=querystring3)
            print (diag.text)
            dis=str(list(diag.json()["Diseases"][0])[0])
            out = "Possible state of patient: "+dis+" \n\nuse phrase \"Details\" for more"
            stage= stage+1
        else:
            out = input.upper() + " added, enter another symptom or use the phrase\"Done\" "
            symp.append(input.upper())
            url3 = "https://endlessmedicalapi1.p.rapidapi.com/UpdateFeature"

            if "temperature" in input:
                querystring21 = {"SessionID": id, "name": "Temp", "value": 100}
                symps = requests.request("POST", url3, headers=headers, params=querystring21)
            else:
                querystring2 = {"SessionID": id, "name": input.title().replace(" ","")+"ROS", "value": 4}
                symps = requests.request("POST", url3, headers=headers, params=querystring2)
                querystring20 = {"SessionID": id, "name": input.title().replace(" ", ""), "value": 4}
                symps = requests.request("POST", url3, headers=headers, params=querystring20)
    elif stage == 4:
        if input.lower()=="details":
            searchlink = search(dis,num_results=5)[0]
            print(searchlink)
            page = requests.get(searchlink).text
            soup =BeautifulSoup(page,features="html.parser")
            p_tags = soup.find_all('p')
            p_tags_text = [tag.get_text().strip() for tag in p_tags]
            sentence_list = [sentence for sentence in p_tags_text if not '\n' in sentence]
            sentence_list = [sentence for sentence in sentence_list if '.' in sentence]
            article = ' '.join(sentence_list)
            out = "Here is a quick summary\n\n"+str(summarize(article, ratio=0.04))

            print (out)

    print (str(stage)+" "+str(symp))

    message.body("Mercury Client: \n\n\n\n" + out)
    return str(response)
if __name__ == "__main__":
    app.run(debug=True)