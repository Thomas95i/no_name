#!/usr/bin/env python3

import flask as fl
import sqlite3
import hashlib
import PIL
from PIL import Image
from werkzeug.utils import secure_filename
import os

img_path = 'user_images/'

"""
<function part>
"""
def crypted_string(string):
    """
    Fonction permettant de crypter une chaine de caractère avec le protocole sha1.
    La fonction retourne un nombre hexadécimal.
    """
    b_string=string.encode()
    crypted_string=hashlib.sha1(b_string)
    return crypted_string.hexdigest()

def return_value(liste, val):
    for a in liste:
        if a[0] == val:
            return a[1]

def img_save(img, filename): 
    for x in range (len(os.listdir('static/'+img_path))):
        if os.listdir('static/'+img_path)[x].split('.')[0] == filename.split('.')[0]:
            os.remove('static/'+img_path + os.listdir('static/'+img_path)[x])
    img.save('static/'+img_path + filename)

def img_resize(filename ,dim=150): # A tester. Réflechir sur les arguments : Un seul argument comprenant path+filename ou deux arguments séparés ?
    img = Image.open('static/'+img_path+filename)
    if img.size[0] >= img.size[1]:
        wpercent = (dim / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((dim, hsize), PIL.Image.ANTIALIAS)
    else:
        hpercent = (dim / float(img.size[1]))
        wsize = int((float(img.size[0]) * float(hpercent)))
        img = img.resize((wsize, dim), PIL.Image.ANTIALIAS)
    os.remove('static/'+img_path+filename)
    img.save('static/'+img_path+filename)

def img_check(filename):
    returned_filename = 'default.jpg'
    for ext_filename in os.listdir('static/' + img_path):
        if ext_filename.split('.')[0] == filename:
            returned_filename = ext_filename
    return img_path+returned_filename

"""
</function part>
"""

"""
<DataBase part>
"""
conn = sqlite3.connect('no_name_data.db')
d = conn.cursor()

d.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255),
                password VARCHAR(255)
                )''')

d.execute('''INSERT INTO users (username, password) SELECT ?, ? 
            WHERE NOT EXISTS (SELECT ? FROM users WHERE username = ?)'''\
            , ('Admin', crypted_string('AKdbE3SA1'), 'Admin', 'Admin'))

d.execute('''INSERT INTO users (username, password) SELECT ?, ? 
            WHERE NOT EXISTS (SELECT ? FROM users WHERE username = ?)'''\
            , ('Mario', crypted_string('mamamia'), 'Mario', 'Mario'))

conn.commit()
conn.close()
"""
</DataBase part>
"""

"""
<Flask part>
"""

app = fl.Flask(__name__)
app.secret_key = '8ea6a2db7a40f7f8f62199b26780b1ea12b2e341'

@app.context_processor
def header():
    return dict(unknown_pwd = False,\
                unknown_user = False,\
                own_profile = False,\
                existing_user = False,\
                not_same_password = False,\
                dickhead = False,\
                profile_text = 'Default text'\
                )

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'logged' in fl.session.keys():
        return fl.redirect('/'+crypted_string(str(fl.session['logged']))+'/')
    else:
        if fl.request.method == 'POST':
            conn = sqlite3.connect('no_name_data.db')
            e = conn.cursor()
            user_list= [a[0] for a in e.execute('SELECT username FROM users').fetchall()]
            if fl.request.form['user'] in user_list:
                mdp =e.execute('SELECT password FROM users WHERE username = ?', (fl.request.form['user'],)).fetchone()[0]
                if crypted_string(fl.request.form['password']) == mdp:
                    user_id = e.execute('SELECT id FROM users WHERE username = ?', (fl.request.form['user'],)).fetchone()[0]
                    conn.close()
                    fl.session['logged'] = user_id
                    return fl.redirect('/'+crypted_string(str(fl.session['logged']))+'/')
                else:
                    conn.close()
                    return fl.render_template('login.html', unknown_pwd = True)
            else:
                conn.close()
                return fl.render_template('login.html', unknown_user = True)
        return fl.render_template('login.html')

@app.route('/<crypt_user_id>/', methods = ['GET', 'POST'])
def profile(crypt_user_id):
    if 'logged' in fl.session.keys():
        if fl.request.method == 'GET':
            user_pic = fl.url_for('static', filename = img_check(crypt_user_id))
            conn = sqlite3.connect('no_name_data.db')
            r = conn.cursor()
            user_list = [(crypted_string(str(a[0])), a[1]) for a in r.execute('SELECT id, username FROM users').fetchall()]
            if crypted_string(str(fl.session['logged'])) == crypt_user_id:
                username = r.execute('SELECT username FROM users WHERE id = ?', (fl.session['logged'],)).fetchone()[0]
                conn.close()
                return fl.render_template('profile.html', username = username, user_pic = user_pic, own_profile = True, user_list = user_list)
            else:
                conn.close()
                username = return_value(user_list, crypt_user_id)
                return fl.render_template('profile.html', user_pic = user_pic, username = username, user_list = user_list)
        elif fl.request.method == 'POST':
            up_pic = fl.request.files['up_file']             # Verifier si extensions authorisées !!
            sec_up_name = crypted_string(str(fl.session['logged'])) + '.' + up_pic.filename.split('.')[-1]
            img_save(up_pic, sec_up_name)
            img_resize(sec_up_name)
            return fl.redirect('/'+crypt_user_id+'/')
    else:
        return fl.redirect(fl.url_for('login'))

@app.route('/sign_up/', methods = ['GET', 'POST'])
def sign_up():
    if fl.request.method == 'POST':
        if fl.request.form['username'] != '' and fl.request.form['password'] != '':
            if fl.request.form['password'] == fl.request.form['confirm_pwd']:
                conn = sqlite3.connect('no_name_data.db')
                t = conn.cursor()
                user_list= [a[0] for a in t.execute('SELECT username FROM users').fetchall()]
                if fl.request.form['username'] not in user_list:
                    t.execute('''INSERT INTO users (username, password) SELECT ?, ? 
                                WHERE NOT EXISTS (SELECT ? FROM users WHERE username = ?)'''\
                                , (fl.request.form['username'], crypted_string(fl.request.form['password']), fl.request.form['username'], fl.request.form['username']))
                    conn.commit()
                    user_id = t.execute('SELECT id FROM users WHERE username = ?', (fl.request.form['username'],)).fetchone()[0]
                    conn.close()
                    fl.session['logged'] = user_id
                    return fl.redirect('/'+crypted_string(str(user_id))+'/')
                else:
                    conn.close()
                    return fl.render_template('signup.html',  existing_user = True)
            else:
                return fl.render_template('signup.html', not_same_password = True)
        else:
            return fl.render_template('signup.html', dickhead = True)
    return fl.render_template('signup.html')

if __name__ == "__main__":                     
    app.run(host = 'localhost', debug = True)

"""
</Flask part>
"""