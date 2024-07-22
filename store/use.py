import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("./key.json")

firebase_admin.initialize_app(cred)

db=firestore.client()


#Realtime database example
config={
   "apiKey": "AIzaSyArDt57xRItp0qpkCCZY4v0B5D-zQvha6o",
  "authDomain": "python-e8472.firebaseapp.com",
 "databaseURL": "https://python-e8472-default-rtdb.firebaseio.com",
  "projectId": "python-e8472",
  "storageBucket": "python-e8472.appspot.com",
  "messagingSenderId": "94712727954",
  "appId": "1:94712727954:web:ff42ceb76612f2f973194b",
  "measurementId": "G-9QF97M58TK"
}

#here we are doing firebase authentication
firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()

def index(request):
        #accessing our firebase data and storing it in a variable
        name = database.child('Data').child('Name').get().val()
        stack = database.child('Data').child('Stack').get().val()
        framework = database.child('Data').child('Framework').get().val()
    
        context = {
            'name':name,
            'stack':stack,
            'framework':framework
        }
        return render(request, 'store/index.html', context)