import os, json, datetime, platform, psutil, zipfile, block, subprocess, shutil
from flask import Flask, request, session, redirect, render_template, flash, jsonify, copy_current_request_context
from random import choice
from base64 import decode
from threading import *
import requests
from time import sleep
import subprocess
import ssl
import socket

app = Flask(__name__)
app.secret_key = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
app.config['CORS_HEADERS'] = 'Content-Type'

def isActive():
    if session.get("token") != None:
        return True
    return False

def getDate(aa='all'):
    now = datetime.datetime.now()
    date_ = {
        'day': now.strftime("%a"),
        'date': now.strftime("%d"),
        'month': now.strftime("%b"),
        'year': now.strftime("%Y"),
        'clock': now.strftime("%I:%M %p"),
        'all': now.strftime("%a, %d %b %Y %I:%M %p")
    }
    return date_[aa]

def idGenerator():
    import string
    id_ = string.digits
    id_ = "".join(choice(id_) for x in range(int(10)))
    return id_

with open('data.json', 'r') as data:
    data = json.load(data)

def saveData():
    with open('data.json','w') as wd:
        json.dump(data, wd, indent=4)
    return

def onSessionExpired(json_=False):
    session.clear()
    session['r'] = request.url
    if json_:
        return jsonify({
            'status':'error',
            'message':'Session Expired'
        })
    flash("Session expired. Please re-login","danger")
    return redirect('/login')

def getDomains(where, val):
    domains = []
    for i in data['domains']:
        if i[where].lower() == val.lower():
            domains.append(i)
    return domains

def getSites(where, val):
    sites = []
    for i in data['sites']:
        if i[where].lower() == val.lower():
            sites.append(i)
    return sites

def getDb(where, val):
    sites = []
    for i in data['database']['db']:
        if i[where].lower() == val.lower():
            sites.append(i)
    return sites

def getDbUser(where, val):
    sites = []
    for i in data['database']['user']:
        if i[where].lower() == val.lower():
            sites.append(i)
    return sites

def updateSite(where, val, col, to_):
    for i in data['sites']:
        if i[where].lower() == val.lower():
            i[col] = to_
    saveData()
    return

def updateDb(where, val, col, to_):
    for i in data['database']['db']:
        if i[where].lower() == val.lower():
            i[col] = to_
    saveData()
    return


def popen(cmd):
    tr_ = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = tr_.communicate()
    try:
        return str(decode(out))
    except:
        return str(out)
    
@app.route('/ssh', methods=['GET', 'POST'])
def ssh():
    if request.method == 'POST':
        command = request.form.get('command')
        if command:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            return jsonify({'output': output.decode('utf-8'), 'error': error.decode('utf-8')})
    return render_template('ssh.html')

@app.route('/database/grant')
def appDatabaseGrant():
    if not isActive():
        return onSessionExpired()
    field = request.args
    @copy_current_request_context
    def run_task():
        os.system("mysql -u root -e \"grant all privileges on {db}.* to '{user}'@'localhost'\"".format(**field))
        for i in range(len(data['database']['db'])):
            if data['database']['db'][i]['name'] == field['db']:
                data['database']['db'][i]['user'].append(field['user'])
        saveData()
    Thread(target=run_task, daemon=True).start()
    sleep(3)
    flash(f"Successfully grant privileges on {field['db']} to {field['user']}")
    return redirect('/database')

@app.route('/database/user/delete')
def appDatabaseDelUser():
    if not isActive():
        return onSessionExpired()
    field = request.args
    @copy_current_request_context
    def run_task():
        os.system("mysql -u root -e \"drop user '{name}'@'localhost'\"".format(**field))
        for i in data['database']['user']:
            if i['name'] == field['name']:
                data['database']['user'].remove(i)
        saveData()
    Thread(target=run_task, daemon=True).start()
    sleep(3)
    flash("Successfully delete user", "success")
    return redirect('/database')

@app.route('/database/user/add', methods=['POST'])
def appDatabaseAddUser():
    if not isActive():
        return onSessionExpired()
    field = request.form
    @copy_current_request_context
    def run_task():
        os.system("mysql -u root -e \"create user '{name}'@'localhost' identified with mysql_native_password by '{password}'\"".format(**field))
        r_ = {
            "name": field['name'],
            "password": field['password']
        }
        data['database']['user'].append(r_)
        saveData()
    Thread(target=run_task, daemon=True).start()
    sleep(3)
    flash("Successfully add user","success")
    return redirect('/database')

@app.route('/database/delete')
def appDatabaseDelete():
    if not isActive():
        return onSessionExpired()
    db_ = getDb('name', request.args['name'].lower())
    if db_ == []:
        flash("Database not found","danger")
        return redirect('/database')
    @copy_current_request_context
    def run_task():
        os.system(f'mysql -u root -e "drop database {request.args["name"].lower()}"')
        for i in data['database']['db']:
            if i['name'].lower() == request.args['name'].lower():
                data['database']['db'].remove(i)
        saveData()
    Thread(target=run_task, daemon=True).start()
    sleep(3)
    flash("Successfully delete database","success")
    return redirect('/database')

@app.route('/database/add', methods=['POST'])
def appDatabaseAdd():
    if not isActive():
        return onSessionExpired()
    db_ = getDb('name', request.form['name'].lower())
    if db_ != []:
        flash("Database already exist", "danger")
        return redirect('/database')
    @copy_current_request_context
    def run_task():
        os.system(f'mysql -u root -e "create database {request.form["name"].lower()}"')
    T = Thread(target=run_task)
    T.daemon = True
    T.start()
    r_ = {
                "name": request.form['name'].lower(),
                "access": []
            }
    sleep(3)
    data['database']['db'].append(r_)
    saveData()
    flash("Successfully create Database", "success")
    return redirect('/database')

@app.route('/database')
def appDatabase():
    if not isActive():
        return onSessionExpired()
    return render_template('database.html', database=data['database']['db'], user=data['database']['user'], phpmyadmin=data['phpmyadmin'])

@app.route('/ssl/install')
def appSSLWebsiteInstall():
    if not isActive():
        return onSessionExpired(True)
    site_ = getSites('id', request.args['id'])[0]
    def run_task():
        with app.app_context():
            os.system(f"sudo certbot --nginx -d {site_['url']}")
            updateSite('id', site_['id'], 'ssl', True)
    T = Thread(target=run_task)
    T.daemon = True
    T.start()
    flash("SSL Install on progress. You can wait till the status turn green.", "info")
    return redirect('/ssl')

@app.route('/ssl/status')
def appSSLWebsiteStatus():
    if not isActive():
        return onSessionExpired()
    def check_ssl_certificate(domain):
        try:
            context = ssl.create_default_context()
            with context.wrap_socket(socket.socket(), server_hostname=domain) as sock:
                sock.connect((domain, 443))
                certificate = sock.getpeercert()
                # print(certificate)
                # # for k in certificate['issuer']:
                # #     print(f"{k}")
                issuer_organization = None
                for item in certificate['issuer']:
                    for attribute, value in item:
                        if attribute == 'organizationName':
                            issuer_organization = value
                            break
                if issuer_organization:
                    return issuer_organization
                else:
                    return 'Unknown SSL Issuer'
        except ssl.SSLError as e:
            return f'{e}'
        except socket.gaierror as e:
            return f'{e}'
    return check_ssl_certificate(request.args['url'].replace("https://","").replace("http://",""))

@app.route('/ssl')
def appSSLWebsite():
    if not isActive():
        return onSessionExpired()
    return render_template('ssl.html', sites=data['sites'])

@app.route('/website/delete')
def appDeleteWebsite():
    if not isActive():
        return onSessionExpired()
    site_ = getSites('id', request.args['id'])[0]
    shutil.rmtree(site_['path'])
    os.remove(f'/etc/nginx/sites-enabled/{site_["url"].replace(".","_")}')
    for i in data['sites']:
        if i['id'] == request.args['id']:
            data['sites'].remove(i)
    saveData()
    if site_['lang'] == 'python':
        def run_task():
            with app.app_context():
                os.system(f'screen -X -S {site_["url"]} kill')
                os.system("sudo systemctl restart nginx")
        T = Thread(target=run_task)
        T.daemon = True
        T.start()
    flash("Successfully delete website","success")
    return redirect('/website')
    

@app.route('/website/file', methods=['POST'])
def appFileWebsite():
    if not isActive():
        return onSessionExpired()
    site_ = getSites('id', request.args['id'])[0]
    file_ = request.files['webfile']
    if file_.filename == '':
        flash("No web file imported!","danger")
        return redirect('/website')
    file_.save(os.path.join(site_['path'],'temp.zip'))
    if not os.path.isfile(f"{site_['path']}/temp.zip"):
        flash("No File found", "danger")
        return redirect('/website')
    try:
        with zipfile.ZipFile(f"{site_['path']}/temp.zip") as zip_ref:
            zip_ref.extractall(site_['path'])
    except Exception as e:
        flash(str(e))
        return redirect('/website')
    if os.path.isfile(f"{site_['path']}/temp.zip"):
        os.remove(f"{site_['path']}/temp.zip")
    flash("Successfully update file, Please restart it.", "success")
    return redirect('/website')

@app.route('/website/restart')
def appRestartWebsite():
    if not isActive():
        return onSessionExpired()
    site_ = getSites('id', request.args['id'])[0]
    if site_['lang'] == 'python':
        def run_task():
            with app.app_context():
                os.system(f'screen -X -S {site_["url"]} kill')
                os.system(f"screen -dmS {site_['url']}")
                os.system(f"screen -S {site_['url']} -X stuff 'cd {site_['path']} && python3 container.py\n'")
        T = Thread(target=run_task)
        T.daemon = True
        T.start()
        flash("Successfully restart website", "success")
        return redirect('/website')
    def run_task_else():
        with app.app_context():
            os.system("sudo systemctl restart nginx")
    T = Thread(target=run_task_else)
    T.daemon = True
    T.start()
    flash("Successfully restart website", "success")
    return redirect('/website')


@app.route('/website/stop')
def appStopWebsite():
    if not isActive():
        return onSessionExpired()
    site_ = getSites('id', request.args['id'])[0]
    if site_['lang'] == 'python':
        def run_task():
            with app.app_context():
                os.system(f'screen -X -S {site_["url"]} kill')
                updateSite('id', site_['id'], 'status', 'stopped')
        T = Thread(target=run_task)
        T.daemon = True
        T.start()
        flash("Website successfully stopped","success")
        return redirect('/website')
    flash("HTML/Php site can not be stopped, otherwise you can remove it.","danger")
    return redirect('/website')

@app.route('/website/deploy/status')
def appGetStatusDeployWebsite():
    if not isActive():
        return onSessionExpired(True)
    site_ = getSites('id', request.args['id'])[0]
    return site_['status']

@app.route('/website/deploy')
def appDeployWebsite():
    if not isActive():
        return onSessionExpired(True)
    site_ = getSites('id', request.args['id'])[0]
    updateSite('id', site_['id'], 'status', 'stopped')
    if site_['lang'] == 'python':
        container_ = f"""from {site_['filename'].replace('.py','')} import {site_['endpoint']}
if __name__ == '__main__':
    from waitress import serve
    serve({site_['endpoint']}, host='0.0.0.0', port={site_['port']})"""
        with open(f"{site_['path']}/container.py","w") as cont:
            cont.write(container_)
    def run_task():
        with app.app_context():
            os.system(f"screen -dmS {site_['url']}")
            os.system(f"screen -S {site_['url']} -X stuff 'cd {site_['path']} && python3 container.py\n'")
            updateSite('id', site_['id'], 'status', 'running')
            updateSite('id', site_['id'], 'deployed', True)
    T = Thread(target=run_task)
    T.daemon = True
    T.start()
    return jsonify({
        'status':'success',
        'message':'Deploy on progress'
    })

@app.route('/website/ssltls/status')
def appGetSSLStatus():
    return 'y'

@app.route('/website/ssltls')
def appSslWebsite():
    site_ = getSites('id', request.args['id'])[0]
    updateSite('id', site_['id'], 'ssl', False)
    return jsonify({
        'status':'success',
        'message':"Skipped. You can set it in SSL/TLS menu."
    })

@app.route('/website/build')
def appBuildWebsite():
    if not isActive():
        return onSessionExpired(True)
    site_ = getSites('id', request.args['id'])[0]
    port_ = str(site_['id'])[:4].replace('0','8')
    site_['port'] = port_
    saveData()
    ret_ = ""
    if site_['lang'] == 'html':
        block_ = block.html(site_)
    elif site_['lang'] == 'php':
        block_ = block.php(site_)
    elif site_['lang'] == 'python':
        block_ = block.python(site_)
    with open(f'/etc/nginx/sites-enabled/{site_["url"].replace(".","_")}', 'w') as ww:
        ww.write(block_)
    ret_ += block_
    ret_ += "\n\nSuccessfully build server block"
    from time import sleep
    sleep(3)
    return jsonify({
        'status':'success',
        'message': ret_
    })

@app.route('/website/unzip')
def appUnzipFile():
    if not isActive():
        return onSessionExpired(True)
    site_ = getSites('id', request.args['id'])[0]
    if not os.path.isfile(f"{site_['path']}/temp.zip"):
        return jsonify({
            "status":"error",
            "message":"Zip file not found"}
        )
    try:
        with zipfile.ZipFile(f"{site_['path']}/temp.zip") as zip_ref:
            zip_ref.extractall(site_['path'])
    except Exception as e:
        return jsonify({
            'status':'error',
            'message': str(e)
        })
    if os.path.isfile(f"{site_['path']}/temp.zip"):
        os.remove(f"{site_['path']}/temp.zip")
    return jsonify({
        'status':'success',
        'message':'Successfully unziped file'
    })

@app.route('/website/add', methods=['POST'])
def appAddWebsite():
    if not isActive():
        return onSessionExpired()
    field = request.form
    web_ = {
        "id": idGenerator(),
        "url": getDomains('id', field['domain'])[0]['domain'],
        "lang": field['lang'],
        "created": getDate(),
        "filename": field['filename'],
        "endpoint": field['endpoint'],
        "path": f"/root/{getDomains('id', field['domain'])[0]['domain'].replace('.','_')}"
    }
    if field['lang'] == 'html' or field['lang'] == 'php':
        web_['path'] = f"/var/www/{getDomains('id', field['domain'])[0]['domain'].replace('.','_')}"
    if getDomains('id', field['domain']) == []:
        flash("Domain not found in this server!","danger")
        return redirect('/website')
    file_ = request.files['webfile']
    if file_.filename == '':
        flash("No web file imported!","danger")
        return redirect('/website')
    os.system(f"sudo mkdir {web_['path']}")
    file_.save(os.path.join(web_['path'],'temp.zip'))
    data['sites'].append(web_)
    saveData()
    flash("Successfully add website","success")
    return redirect('/website')

@app.route('/website/run')
def appRunWeb():
    if not isActive():
        return onSessionExpired()
    site_ = getSites('id', request.args['id'])[0]
    if site_.get('deployed') == None:
        return render_template('deploy.html', web_id=request.args['id'])
    def run_task():
        with app.app_context():
            os.system(f"screen -dmS {site_['url']}")
            os.system(f"screen -S {site_['url']} -X stuff 'cd {site_['path']} && python3 container.py\n'")
            updateSite('id', site_['id'], 'status', 'running')
    T = Thread(target=run_task)
    T.daemon = True
    T.start()
    flash("Successfully run website.","success")
    return redirect('/website')

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            break
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} {unit}"


@app.route('/website')
def appWebsite():
    if not isActive():
        return onSessionExpired()
    for i in data['sites']:
        i['totalSize'] = format_size(get_folder_size(i['path']))
    return render_template('website.html', websites=data['sites'], domains=data['domains'])

@app.route('/domain/delete')
def appDeleteDomain():
    if not isActive():
        return onSessionExpired()
    for i in data['domains']:
        if i['id'] == request.args['id']:
            data['domains'].remove(i)
    saveData()
    flash("Successfully delete domain","success")
    return redirect('/domain')

@app.route('/domain/add', methods=['POST'])
def appAddDomain():
    if not isActive():
        return onSessionExpired()
    field = request.form
    if getDomains('domain',field['domainName']) != []:
        flash("Domain already Added", "danger")
        return redirect('/domain')
    dt_ = {
        "domain":field['domainName'],
        "path": f"/root/{field['domainName'].replace('.','_')}",
        "id": idGenerator()
    }
    data['domains'].append(dt_)
    saveData()
    flash("Successfully add domain","success")
    return redirect('/domain')

@app.route('/domain')
def appDomain():
    if not isActive():
        return onSessionExpired()
    return render_template('domain.html', domains=data['domains'])

@app.route('/dashboard')
def appDashboard():
    if not isActive():
        return onSessionExpired()
    return render_template('dashboard.html', env_os=platform.platform(),
                                            env_cpu=platform.processor(),
                                            usage_cpu=psutil.cpu_percent(),
                                            usage_disk=psutil.disk_usage('/').percent,
                                            usage_ram=psutil.virtual_memory().percent
                                            )

@app.route('/')
def appIndex():
    return redirect('/login')

@app.route('/login', methods=['POST','GET'])
def appLogin():
    if request.method == 'GET':
        if isActive():
            return redirect('/dashboard')
        return render_template('login.html')
    elif request.method == 'POST':
        field = request.form
        if field['username'] == data['username'] and field['password'] == data['password']:
            session['token'] = "LoggedIn"
            if session.get('r') != None:
                return redirect(session['r'])
            return redirect('/dashboard')
        flash("Wrong Username or Password", "danger")
        return redirect('/login')

@app.route('/logout')
def appLogout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)