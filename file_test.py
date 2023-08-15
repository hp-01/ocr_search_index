import os
import tkinter as tk
from tkinter import filedialog
import pymongo
from pymongo import MongoClient
client = MongoClient()

database = client["msc_project"]
file_collection = database["files"]

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
    id = str(res.inserted_id)
    print(id)
    addToStorage(id, content)
    return

def addToStorage(file_name, content):
    f = open("storage/"+file_name, "wb")
    f.write(content)
    f.close()
    return

addToDatabase()