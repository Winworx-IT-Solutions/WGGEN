# WireGuard Server Manager (WGSM)
# GUI for WGGEN written in Flask

import sqlite3
from flask import Flask, session, redirect, url_for, escape, render_template, request, g
from simplepam import authenticate

from weblib.helper import Helper
import weblib.interface

app = Flask(__name__)
app.secret_key = "geheime scheisse"

#=============================#
# set up database
#=============================#
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('wgsm.db')
    return db
    
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


#=============================#
# set up error handlers
#=============================#
@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('index'))


#=============================#
# Index/Start page
#=============================#
@app.route('/')
def index():
    if Helper.user_logged_in(session) == False: return redirect(url_for('login'))
    return render_template('index.html', page_title="WGSM - Index", logged_in_user=escape(session['username']))


#=============================#
# Subnet Pages
#=============================#
@app.route('/vpn_subnets', methods=['GET', 'POST'])
def vpn_subnets():
    if Helper.user_logged_in(session) == False: return redirect(url_for('login'))
    
    if request.method == 'GET':
        return render_template('vpn_subnets.html', page_title="WGSM - VPN Subnets", logged_in_user=escape(session['username']), subnets=weblib.vpn_subnet.load_all_subnets(get_db()))

    if request.method == 'POST':
        desc = request.form['desc']
        weblib.vpn_subnet.create_new_subnet(get_db(), 16, desc) # pass in 16 as netmask, maybe add support for other netmasks later on
        return redirect(url_for('vpn_subnets'))


#=============================#
# Interface Pages
#=============================#
@app.route('/wg_interfaces', methods=['GET', 'POST'])
def wg_interfaces():
    if Helper.user_logged_in(session) == False: return redirect(url_for('login'))
      
    if request.method == 'GET':
        return render_template('interfaces.html', page_title="WGSM - Interfaces", logged_in_user=escape(session['username']), interfaces=weblib.interface.load_all_interfaces_from_db(get_db()))
            

@app.route('/wg_interface_detail', methods=['GET', 'POST'])
def wg_interface_detail():
    if Helper.user_logged_in(session) == False: return redirect(url_for('login'))
    
    interface_name = request.args.get('name')
    interface_info, peer_info = Helper.get_interface_detail(get_db(), interface_name)
 
    if len(interface_info) != 0:
        return render_template('interface_detail.html', page_title=f"Interface: {interface_info.name}", logged_in_user=escape(session['username']), 
                                    interface_info=interface_info, peer_info=peer_info)
    return redirect(url_for('wg_interfaces'))
    
#=============================#
# Peer Pages
#=============================#
@app.route('/wg_peers', methods=['GET', 'POST'])
def wg_peers():
    if Helper.user_logged_in(session) == False: return redirect(url_for('login'))
    if request.method == 'GET':
        interfaces = Helper.list_wg_interfaces(get_db())
        peers = Helper.list_wg_peers(get_db())
        return render_template('peers.html', page_title="WGSM - Peers", logged_in_user=escape(session['username']), peers=peers, interfaces=interfaces)
    


#=============================#
# Login/Logout
#=============================#
@app.route('/login', methods=['GET', 'POST'])
def login():
        if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                if authenticate(str(username), str(password)):
                        session['username'] = request.form['username']
                        return redirect(url_for('index'))
                else:
                        return 'Invalid username/password'
        return render_template('login.html')

@app.route('/logout')
def logout():
        session.pop('username', None)
        return redirect(url_for('index'))
        

#=============================#
# run app
#=============================#
if __name__ == '__main__':
        app.run(debug=True)
 
