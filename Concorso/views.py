# -*- coding: utf-8 -*-

"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, make_response, redirect, url_for
from flask_login import login_user, login_required, current_user, logout_user
# from flask import Flask, render_template, redirect, url_for, request
from sqlalchemy import func
from Concorso import app
from .model import User, db

import sys  
   

# sys.path.append("Concorso")  

from Concorso.control import add_vote, calcola_classifica, get_active_contest, create_contest, get_active_cookie, close_active_contest, get_elenco_contest, represents_int

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/vote/')
@app.route('/vote/<choice>')
def vote(choice=""):
    """Renders the vote page."""
    invalid_vote = { 'template_name_or_list': 'vote_invalid.html',
                           'title': u'Il voto non è andato a buon fine',
                            'year': datetime.now().year,
                            'message': 'Grazie per il tuo tentativo, ma non hai espresso \
                                nessuna preferenza, ritenta!',
                            'status': 'grey'}


    # Se non e' stato inserito nessun voto, non fa nulla ed esce.
    if choice == "":
        invalid_vote['message'] = 'Grazie per il tuo tentativo, ma non hai \
                        espresso nessuna preferenza, ritenta!'
        return render_template(**invalid_vote)


    #  In questo caso, è stato espresso un voto.
    my_message = f"Hai scelto la foto di {choice}!"
    
    # Recupero il token del cookie del contest corrente, serve per 
    # verificare se è stato espresso un voto
    active_cookie = get_active_cookie()

    # se non c'è alcun contest, termina
    if active_cookie == "":
        invalid_vote['message'] = "Grazie per il tuo tentativo, ma c'è alcun \
                        contest attivo in questo momento. Riprova più tardi."
        return render_template(**invalid_vote)


    # Recupero il valore del cookie del contest corrente per capire se è già 
    # stato impostato
    the_cookie = request.cookies.get(active_cookie)
    
    app.logger.info("Il contenuto del cookie e' %s", the_cookie)

    voti = 0


    if the_cookie == "" or the_cookie == None:
        the_cookie="3"
    
    try:
        voti_residui = int(the_cookie)
    except ValueError as e:
        app.logger.warning(f"Il cookie conteneva un valore non numerico: {e}")

    if voti_residui > 0:

        # inserire la chiamata a DB per votare. se fallisce, il valore del cookie da impostare rimane vuoto

        return render_template(
            'vote.html',
            title='Votazione',
            year=datetime.now().year,
            message=my_message,
            cookie_msg = the_cookie,
            scelta=choice
            )


    else:
        invalid_vote['message'] = "Grazie per il tuo tentativo, ma hai \
                                terminato i voti a tua disposizione."
        return render_template(**invalid_vote)


        
    
@app.route("/no_vote/")
def no_vote():
    """Renders the no_vote page."""
    return render_template(
        'vote_invalid.html',
        title='Voto non effettuato',
        year=datetime.now().year,
        message='Puoi ancora votare.'
    )

@app.route("/voted/<scelta>")
def voted(scelta):

    request_parm = {'template_name_or_list': 'vote_esito.html',
                           'title': u'Il voto non è andato a buon fine',
                           'message': u'Errore generico',
                            'year': datetime.now().year,
                            'status': 'grey'}

    # verificare se è stato espresso un voto
    active_cookie = get_active_cookie()

    # se non c'è alcun contest, termina
    if active_cookie == "":
        request_parm["message"] = f"Spiacente, al momento non c'è alcuna \
                    votazione attiva."
        request_parm["status"] = "red"
        return render_template(**request_parm)

    # Recupero il valore del cookie del contest corrente per capire se è già 
    # stato impostato
    the_cookie = request.cookies.get(active_cookie)
    
    app.logger.info("Il contenuto del cookie e' %s", the_cookie)

    if the_cookie == "" or the_cookie == None:
        the_cookie='3'
    
    voti_residui = 0
    app.logger.info("Sono qui 001")
    try:
        voti_residui = int(the_cookie)
        app.logger.info("Sono qui 002")
        
    except ValueError as v_err:
        app.logger.warning(v_err)
    
    except e:
        app.logger.error(e)
    
    app.logger.info(f"HEY! Ci sono ancora {voti_residui} voti residui...")

    if voti_residui > 0:
        voti_residui-=1
        add_vote(scelta)

        # Rendo più carino il messaggio coi voti disponibili.
        if voti_residui <= 0:
            request_parm["title"]=f"Grazie per aver votato, questo era l'ultimo voto disponibile. Goditi l'esposizione"
        elif voti_residui == 1:
            request_parm["title"]=f'Grazie per aver votato, hai a disposizione ancora un singolo voto'
        else:
            request_parm["title"]=f'Grazie per aver votato, hai a disposizione ancora {voti_residui} voti'

        #request_parm["title"]=f'Grazie per aver votato, hai a disposizione ancora {voti_residui} voto/i.'
        request_parm["message"]=f'La tua scelta è stata {scelta}'
        request_parm["status"]  = "green"
        resp = make_response(render_template(**request_parm))

        resp.set_cookie(active_cookie, f"{voti_residui}", max_age=60*60*24*30)   

        return resp
    else:
        request_parm["message"] ="Grazie per il tuo tentativo, ma hai \
                                terminato i voti a tua disposizione."
        request_parm["status"]  = "red"
        return render_template(**request_parm)




@app.route('/classifica')
def classifica():
    """Renders the hit page."""

    id_contest = request.args.get('contest_list')


    if not represents_int(id_contest):
        id_contest = get_active_contest()
    
    if  id_contest == None:
        id_contest = '0'

    # Recupero l'elenco dei contest attivi
    elenco = get_elenco_contest()
    
    # Voglio selezionare la classifica che è stata scelta. Ho quindi fatto questa lambda function che aggiunge la voce "selected" accanto al contest scelto. Andrò poi ad applicarla alla classifica.
    imposta_selezione = lambda r: (r[0], r[1], r[2], 'selected') if r[0]==int(id_contest) else (r[0], r[1], r[2], '')
    
    # Applico la mia funzione all'elenco
    body_contests = list(map(imposta_selezione, elenco))

    app.logger.warning(id_contest)

    app.logger.warning(body_contests)
    app.logger.debug(calcola_classifica())

    return render_template(
        'classifica.html',
        title='Classifica',
        year=datetime.now().year,
        message='Classifica della competizione',
        body_classifica = calcola_classifica(id_contest),
        body_contests =  body_contests
    )




@app.route('/new_contest/', methods=['GET', 'POST'])
@login_required
def new_contest():
    """Renders the hit page."""
   

    msg = 'Apertura di un nuovo contest...'

    if get_active_contest() != None:
        # ci sono ancora contest attivi!!
        return render_template(
            'new_contest.html',
            title='Nuovo contest',
            year=datetime.now().year,
            message="Impossibile creare un nuovo contest: ne esiste ancora uno attivo!",
            visible="hidden"
        )


    if request.method =='POST': #creo una nuova votazione
        app.logger.debug(request.form)
        descrizione = request.form['descrizione']
        max_voti = request.form['max_voti']

        msg = f'Post! Hai passato il parametro {descrizione}.'
        esito, messaggio = create_contest(descrizione=descrizione, data=datetime.now(),voti=max_voti)

        if esito:
            msg="Il nuovo contest e' stato creato, iniziate a votare."
        else:
            msg=f"Impossibile creare un nuovo contest: {messaggio}"
            



    return render_template(
        'new_contest.html',
        title='Nuovo contest',
        year=datetime.now().year,
        message=msg,
        visible=""
    )



@app.route('/close_contest/', methods=['GET', 'POST'])
@login_required
def close_contest():
    """Renders the hit page."""

    if request.method =='POST': #chiudere la votazione corrente...
        app.logger.debug(request.form)
        descrizione = request.form['descrizione']
        if descrizione == 'Chiudere':
            app.logger.warning("E' stata richiesta la chiusura del contest corrente...")
            close_active_contest()



    msg = "Trovato un un contest attivo." if get_active_contest() else "Nessun contest attivo."
    
    
    return render_template(
        'close_contest.html',
        title='Chiusura contest',
        year=datetime.now().year,
        message=msg,
        visible=""
        )






# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Verifica le credenziali dell'utente e, se valide, garantisce l'accesso"""
    
    error = None
    if request.method == 'POST':

        email = request.form['username']
        password = request.form['password'] 

        user = User.query.filter_by(email=email).first()

        if user == None or not user.check_password(password):
            error = 'Invalid Credentials. Please try again.'
        else:
                user = User.query.get(email)
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)

                return redirect(url_for('home'))



    return render_template('login.html', error=error)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('home'))


@app.route("/check/", methods=['GET'])
def check_varie():
    

    def text_is_logged():
        if current_user.is_authenticated:
            return "Login Attiva"
        else:
            return "Non Loggato"
    

    return f"Valore per User; {text_is_logged()}"


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     """For GET requests, display the login form. 
#     For POSTS, login the current user by processing the form.

#     """
#     # print db
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.get(form.email.data)
#         if user:
#             if bcrypt.check_password_hash(user.password, form.password.data):
#                 user.authenticated = True
#                 db.session.add(user)
#                 db.session.commit()
#                 login_user(user, remember=True)
#                 return redirect(url_for("bull.reports"))
#     return render_template("login.html", form=form)

# @app.route("/logout", methods=["GET"])
# @login_required
# def logout():
#     """Logout the current user."""
#     user = current_user
#     user.authenticated = False
#     db.session.add(user)
#     db.session.commit()
#     logout_user()
#     return render_template("logout.html")
