import os
from google.cloud import vision
import tkinter as tk
from tkinter import filedialog
import pymongo
from pymongo import MongoClient
import proto

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' 

import spacy
nlp = spacy.load("en_core_web_sm")
stop_words = spacy.lang.en.stop_words.STOP_WORDS

client = MongoClient()
database = client["msc_project"]
file_collection = database["files"]
search = database["search"]

root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()

def addToDatabase(file_path=file_path):
    f = open(file_path, "rb")
    content = f.read()
    f.close()
    original_file_name = os.path.basename(file_path)
    extension = original_file_name.split(".")[-1]
    print(original_file_name, extension)
    res = file_collection.insert_one({ "file_name": original_file_name, "extension": extension })
    file_id = str(res.inserted_id)
    print(file_id)
    addToStorage(file_id, content)
    text = addToOCR(content)
    text = text.lower()
    tokens = addToTokenization(text)
    addToSearchIndex(tokens, file_id)
    return

def addToOCR(content):
    image = vision.Image(content=content)
    client = vision.ImageAnnotatorClient()
    response = client.text_detection(image=image)
    response = proto.Message.to_dict(response)
    response = response["full_text_annotation"]["text"]
    # print(response.replace("\n", " "))
    return response.replace("\n", " ")

def addToTokenization(text):
    doc = nlp(text)
    filtered_tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct] 
    filtered_tokens = set(filtered_tokens)
    # print(filtered_tokens)
    return filtered_tokens

def addToSearchIndex(tokens, file_id):
    for token in tokens:
        search.update_one({"word": token}, {"$addToSet": {"documents": {
                  "$each": [file_id]}}}, upsert=True)
    return

def addToStorage(file_name, content):
    f = open("storage/"+file_name, "wb")
    f.write(content)
    f.close()
    return

def searchIndex(word="good"):
    documents = {}
    for item in search.find({"$text": {"$search": word}}):
        for document in item["documents"]:
            if documents.get(document) is None: documents[document] =  1
            else: documents[document] += 1
    result = []
    for item in sorted(documents.items(), key=lambda x: x[1], reverse=True):
        result.append(item)
    print(result)

searchIndex()

# addToDatabase()