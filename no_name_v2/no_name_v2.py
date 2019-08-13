#!/usr/bin/env python3

import sqlite3
import hashlib
import flask as fl
import os
import PIL
from PIL import Image

"""
<globals part>
"""
img_path = 'user_images/'
"""
</globals part>
"""

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

def img_save(img, filename): 
    for x in range (len(os.listdir('static/'+img_path))):
        if os.listdir('static/'+img_path)[x].split('.')[0] == filename.split('.')[0]:
            os.remove('static/'+img_path + os.listdir('static/'+img_path)[x])
    img.save('static/'+img_path + filename)

def img_resize(filename ,dim=150):
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

def return_value(liste, function, val):
    for a in liste:
        if function(str(a[0])) == val:
            return a[0]

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
req_db = conn.cursor()
req_db.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255),
                password VARCHAR(255),
                desc_profile VARCHAR(1000)
                )''')
req_db.execute('''CREATE TABLE IF NOT EXISTS relations (
                rel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                userA_id INTEGER,
                userB_id INTEGER,
                    FOREIGN KEY(userA_id) 
		            REFERENCES users(id),
                    FOREIGN KEY(userB_id)
                    REFERENCES users(id)
                    )''')
# req_db.execute('''
#                 CREATE TABLE IF NOT EXISTS relationships (
#                 id_relationship INTEGER PRIMARY KEY AUTOINCREMENT,
#                 id_userA INTEGER,
#                 id_userB INTEGER,
#                     FOREIGN KEY(id_userA) 
#                     REFERENCES users(id_user),
#                     FOREIGN KEY(id_userB) 
#                     REFERENCES users(id_user)
#                 );
#                 ''')

# Création par défault des compte Admin et Mario (Easter egg). Ces deux comptes seront automatiquement présent dans la base de données.

# >> Admin :
username = 'Admin'
password = 'AKdbE3SA1'
desc_profile = 'Admin profile. Don\'t piss him off if you want to keep using this website ;).'
req_db.execute('''INSERT INTO users (username, password, desc_profile) SELECT ?, ?, ? 
            WHERE NOT EXISTS (SELECT ? FROM users WHERE username = ?)'''\
            , (username, crypted_string(password), desc_profile, username, username))

# >> Mario :
username = 'Mario'
password = 'mamamia'
desc_profile = 'World\'s most famous plumber. Still haven\'t understood that his girlfriend is not really kidnapped by Browser tho...'
req_db.execute('''INSERT INTO users (username, password, desc_profile) SELECT ?, ?, ? 
            WHERE NOT EXISTS (SELECT ? FROM users WHERE username = ?)'''\
            , (username, crypted_string(password), desc_profile , username, username))

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
    return dict(title = 'No name',\
                error = ''\
                )

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'logged' in fl.session.keys():
        return fl.redirect('/'+fl.session['logged']+'/')
    else:
        if fl.request.method == 'POST':
            conn = sqlite3.connect('no_name_data.db')
            req_db = conn.cursor()
            user_list= [a[0] for a in req_db.execute('SELECT username FROM users').fetchall()]
            if fl.request.form['user'] in user_list:
                mdp =req_db.execute('SELECT password FROM users WHERE username = ?', (fl.request.form['user'],)).fetchone()[0]
                if crypted_string(fl.request.form['password']) == mdp:
                    user_id = req_db.execute('SELECT id FROM users WHERE username = ?', (fl.request.form['user'],)).fetchone()[0]
                    conn.close()
                    fl.session['logged'] = crypted_string(str(user_id))
                    return fl.redirect('/'+fl.session['logged']+'/')
                else:
                    conn.close()
                    return fl.render_template('login.html', error = 'Wrong password')
            else:
                conn.close()
                return fl.render_template('login.html', error = 'Username unknown')
        elif fl.request.method == 'GET':
            return fl.render_template('login.html')
        else:
            return fl.redirect(fl.url_for('login'))

@app.route('/inscription/', methods=['GET', 'POST'])
def inscription():
    if fl.request.method == 'POST':
        conn = sqlite3.connect('no_name_data.db')
        req_db = conn.cursor()
        user_list = [a[0] for a in req_db.execute('SELECT username FROM users').fetchall()]
        if fl.request.form['user'] not in user_list:
            if fl.request.form['password'] == fl.request.form['confirm_pwd']:   # A terme, condition a supprimer. Pris en charge par Javascript
                req_db.execute('''INSERT INTO users (username, password, desc_profile) SELECT ?, ?, ?
                                WHERE NOT EXISTS (SELECT ? FROM users WHERE username = ?)'''\
                                , (fl.request.form['user'], crypted_string(fl.request.form['password']), '', fl.request.form['user'], fl.request.form['user']))
                                                                                # Requete a modifier plus tard, avec ajout d'une zone de texte 
                                                                                # coté front et possibilité d'y inscrire sa description
                conn.commit()
                user_id = req_db.execute('SELECT id FROM users WHERE username = ?', (fl.request.form['user'],)).fetchone()[0]
                conn.close()
                fl.session['logged'] = crypted_string(str(user_id))
                return fl.redirect('/'+fl.session['logged']+'/')
            else:
                conn.close()
                return fl.render_template('inscription.html', error='2nd password different from the first one')
        else:
            conn.close()
            return fl.render_template('inscription.html', error='User name already taken')
    elif fl.request.method == 'GET':
        return fl.render_template('inscription.html')


@app.route('/<crypted_id>/', methods=['GET', 'POST'])
def temp(crypted_id):
    if 'logged' not in fl.session.keys():
        return fl.redirect(fl.url_for('login'))
    else:
        conn = sqlite3.connect('no_name_data.db')
        req_db = conn.cursor()
        id_list = req_db.execute('SELECT id FROM users').fetchall()
        user_id = return_value(id_list, crypted_string, crypted_id)
        if fl.request.method == 'POST':
            up_pic = fl.request.files['up_file']
            if up_pic.filename != '':                                           # Ajouter vérification extension fichier en javascript coté front
                sec_up_name = fl.session['logged']+'.'+up_pic.filename.split('.')[-1]
                img_save(up_pic, sec_up_name)
                img_resize(sec_up_name, dim=200)
            req_db.execute('''UPDATE users
                            SET desc_profile = ?
                            WHERE id = ?''',\
                            (fl.request.form['desc_profile'], user_id))
            conn.commit()
            conn.close()
            return fl.redirect('/'+crypted_id+'/')
        elif fl.request.method == 'GET':
            user_pic = fl.url_for('static', filename = img_check(crypted_id))
            user_data = req_db.execute('SELECT username, desc_profile FROM users WHERE id = ?',\
                                        (user_id,)).fetchone()
            conn.commit()
            conn.close()
            if fl.session['logged'] == crypted_id:
                return fl.render_template('profile.html', user_name = user_data[0], user_pic = user_pic, desc_profile = user_data[1], own_profile = True)
            else:
                return fl.render_template('profile.html', user_name = user_data[0], user_pic = user_pic, desc_profile = user_data[1], own_profile = False)

@app.route('/logout/')
def logout():
    fl.session.pop('logged', None)
    return fl.redirect(fl.url_for('login'))

@app.route('/users_list')
def users_list():
    if 'logged' not in fl.session.keys():
        return fl.redirect(fl.url_for('login'))
    conn = sqlite3.connect('no_name_data.db')
    req_db = conn.cursor()
    users_list =sorted([(crypted_string(str(a[0])), a[1]) for a in req_db.execute('SELECT id, username FROM users').fetchall()], key= (lambda x : x[1])) 
    return fl.render_template('users_list.html', myId = fl.session['logged'], users_list = users_list)

if __name__ == "__main__":                     
    app.run(host = 'localhost', debug = True)
"""
</Flask part>
"""