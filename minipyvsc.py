
import tkinter as tk
from tkinter import messagebox
from tkinter import Listbox
from tkinter import PhotoImage
import mysql.connector
import csv
import datetime
from PIL import ImageTk,Image
from win10toast import ToastNotifier

import matplotlib.pyplot as plt

         

# Global variables
select_index = 0
notes_ids = [] # store the ids because of listbox limitation :(


def onselect(evt):
    global select_index
    # Note here that Tkinter passes an event object to onselect()
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    select_index = index
    display_note(index, value)

# GUI CODES
window = tk.Tk()
window.title("Sticky notes-Schedule ur day/Flashcard")
window.geometry('500x700')

top = tk.Frame(window)
mid = tk.Frame(window)


list_notes = Listbox(top, height=30,
                     width=17,
                     bg="grey",
                     font = "Helvetica 15",
                     fg="black")
list_notes.bind('<<ListboxSelect>>', onselect)
list_notes.pack(side=tk.TOP, fill=tk.Y, padx=(10,0), pady=(10, 10))

scroll_list = tk.Scrollbar(top)
scroll_list.pack(side=tk.RIGHT, fill=tk.BOTH)
scroll_list.config(command=list_notes.yview)
list_notes.config(yscrollcommand=scroll_list.set, cursor="hand2", background="#ffffe0", highlightbackground="black", bd=0)

text_frame = tk.Frame(mid)
note_title = tk.Entry(text_frame, width=53, font = "Helvetica 13")
note_title.insert(tk.END, "Title")
note_title.config(background="#ffffff", highlightbackground="black")
note_title.pack(side=tk.TOP, pady=(0, 5), padx=(10, 10))


scroll_text = tk.Scrollbar(text_frame)
scroll_text.pack(side=tk.RIGHT, fill=tk.Y)
note_text = tk.Text(text_frame, height=20, width=53, font = "Helvetica 13")
note_text.pack(side=tk.TOP, fill=tk.Y, padx=(10, 0), pady=(0, 5))
note_text.tag_config("tag_your_message", foreground="blue")
note_text.insert(tk.END, "Notes")
scroll_text.config(command=note_text.yview)
note_text.config(yscrollcommand=scroll_text.set, background="#ffffff", highlightbackground="black")

text_frame.pack(side=tk.TOP)

button_frame = tk.Frame(mid)

btn_save = tk.Button(button_frame,text="ADD", command=lambda : save_note())
btn_edit = tk.Button(button_frame, text="UPDATE", command=lambda : update_note())
btn_delete = tk.Button(button_frame, text="DELETE", command=lambda : delete_note())


btn_save.grid(row=0, column=1)
btn_edit.grid(row=0, column=2)
btn_delete.grid(row=0, column=3)

button_frame.pack(side=tk.TOP)


top.pack(side=tk.LEFT)
mid.pack(side=tk.RIGHT)

# DATABASE FUNCTIONS STARTS
conn = mysql.connector.connect(host="localhost", port=3306, user="root", passwd="guruvishnu")


def create_db(conn):
    mycursor = conn.cursor()
    query = "CREATE DATABASE IF NOT EXISTS db_notes"
    mycursor.execute(query)


def create_table(conn):
    create_db(conn)
    conn.database = "db_notes"
    mycursor = conn.cursor()
    query = "CREATE TABLE IF NOT EXISTS tb_notes (" \
          "note_id INT AUTO_INCREMENT PRIMARY KEY, " \
          "title VARCHAR(255) NOT NULL, " \
          "note VARCHAR(2000) NOT NULL)"
    mycursor.execute(query)


def insert(conn, title, note):
    conn.database = "db_notes"
    mycursor = conn.cursor()
    ins = "INSERT INTO tb_notes (title, note) VALUES (%s, %s)"
    val = (title, note)
    mycursor.execute(ins, val)
    conn.commit()
    return mycursor.lastrowid


def select_all(conn):
    conn.database = "db_notes"
    ins = "SELECT * from tb_notes"
    mycursor = conn.cursor()
    mycursor.execute(ins)
    return mycursor.fetchall()


def select_specific(conn, note_id):
    conn.database = "db_notes"
    ins="SELECT title,note FROM tb_notes WHERE note_id = "+ str(note_id)
    mycursor = conn.cursor()
    mycursor.execute(ins)
    return mycursor.fetchone()


def db_update_note(conn, title, note, note_id):
    conn.database = "db_notes"
    mycursor = conn.cursor()
    ins = "UPDATE tb_notes SET title = '{}', note = '{}' WHERE note_id = {}".format(title,note,note_id)
    #val = (title, note, note_id)
    mycursor.execute(ins)
    conn.commit()


def delete(conn, note_id):
    conn.database = "db_notes"
    mycursor = conn.cursor()
    ins = "DELETE FROM tb_notes WHERE note_id = {}".format(note_id)
    #adr = (note_id,)
    mycursor.execute(ins)
    conn.commit()


def init(conn):
    create_db(conn)  # create database if not exist
    create_table(conn)  # create table if not exist

    # select data
    notes =select_all(conn)

    for note in notes:
        list_notes.insert(tk.END, note[1])
        notes_ids.append(note[0])  # save the id

init(conn)

def save_note():
    global conn
    title = note_title.get()

    if len(title) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="ENTER NOTE TITLE!")
        return

    note = note_text.get("1.0", tk.END)
    if len(note.rstrip()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="ENTER NOTES!")
        return

    # Check if title exist
    title_exist = False
    existing_titles = list_notes.get(0, tk.END)

    for t in existing_titles:
        if t == title:
            title_exist = True
            break

    if title_exist is True:
        tk.messagebox.showerror(title="ERROR!!!", message="NOTE TITLE ALREADY EXIST !")
        return

    # save in database
    inserted_id = insert(conn, title, note)
    print("Last inserted id is: " + str(inserted_id))

    # insert into the listbox
    list_notes.insert(tk.END, title)

    notes_ids.append(inserted_id)  # save notes id

    # clear UI
    note_title.delete(0, tk.END)
    note_text.delete('1.0', tk.END)


def update_note():
    global select_index, conn

    title = note_title.get()

    if len(title) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="ENTER NOTE TITLE ! ")
        return

    note = note_text.get("1.0", tk.END)
    if len(note.rstrip()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="ENTER NOTES ! ")
        return

    note_id = notes_ids[select_index]  # get the id of the selected note

    # save in database
    db_update_note(conn, title, note, note_id)

    # update list_note
    list_notes.delete(select_index)
    list_notes.insert(select_index, title)

    # clear UI
    note_title.delete(0, tk.END)
    note_text.delete('1.0', tk.END)


def delete_note():
    global select_index, conn, notes_ids
    title = note_title.get()
    notes = note_text.get("1.0", tk.END)

    print("Selected note is: " + str(select_index))

    if len(title) < 1 or len(notes.rstrip()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="SELECT NOTE TO DELETE")
        return

    result = tk.messagebox.askquestion("Delete", "Are you sure you want to delete?", icon='warning')

    if result == 'yes':
        # remove notes from db
        note_id = notes_ids[select_index]
        delete(conn, note_id)
        del notes_ids[select_index]

        # remove from UI
        note_title.delete(0, tk.END)
        note_text.delete('1.0', tk.END)
        list_notes.delete(select_index)


def display_note(index, value):
    global notes_ids, conn
    # clear the fields
    note_title.delete(0, tk.END)
    note_text.delete('1.0', tk.END)

    note = select_specific(conn, notes_ids[index])

    # insert data
    note_title.insert(tk.END, note[0])
    note_text.insert(tk.END, note[1])

    btn_delete.config(state=tk.NORMAL)
    btn_edit.config(state=tk.NORMAL)

window.mainloop()

#TRACK PROGRRESS PIE CHART CODE

opt=input("Is ur day complete : ")
if opt=='yes':
    n=len(notes_ids)
    print("Todays target no.: ",end='')
    print(notes_ids[n-1])
    n1=notes_ids[n-1]
    c=int(input("Completion: "))
    p=int(input("Partial: "))
    i=c-p
    val=[c,p,i]
    ele=['Achieved','Pending','In Progress']
    cols=['c','m','r']
    plt.pie(val,
            labels=ele,
            colors=cols,
            startangle=90,
            shadow=True,
            autopct='%1.1f%%')
    plt.title("TRACK")
    plt.show()

#NOTIFICATION BASED ON IMPORTANT DATES AND BIRTHDAY

n=str(datetime.date.today())
toaster=ToastNotifier()

with open('festive.csv',newline = '') as myfile:
    reader=csv.reader(myfile)
    for i in reader:                    
                        
        if i[0]==n:            
            toaster.show_toast("Notification from STICKY NOTES",i[1])
            
with open('bday.csv',newline = '') as myfile:
    reader=csv.reader(myfile)
    for i in reader:                      
                        
        if i[0]==n:            
            toaster.show_toast("Notification of BIRTHDAY",i[1])











