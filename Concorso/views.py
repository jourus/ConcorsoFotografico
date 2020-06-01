# coding=latin-1

"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, make_response
from sqlalchemy import func
from Concorso import app
import sys  
   

sys.path.append("Concorso")  

from control import add_vote, calcola_classifica, get_active_contest, create_contest, get_active_cookie, close_active_contest

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
    
    # Se non e' stato inserito nessun voto, non fa nulla ed esce.
    if choice == "":
        return render_template(
                'vote.html',
                title='Votazione',
                year=datetime.now().year,
                message= 'Non hai scelto nessuno, ritenta!',
                cookie_msg = ""
                )

    my_message = f"Hai scelto la foto di {choice}!"
    
    active_cookie = get_active_cookie()

    the_cookie = request.cookies.get(active_cookie)
    
    app.logger.info("Il contenuto del cookie e' %s", the_cookie)

  

    if the_cookie == "" or the_cookie == None:
        my_cookie_msg = f"Grazie per aver votato, se sei amico di {choice}, fatti offrire una birra."
        add_vote(choice)

        # inserire la chiamata a DB per votare. se fallisce, il valore del cookie da impostare rimane vuoto
        
        the_cookie = "votato"
    else:
        my_cookie_msg = "Grazie per la tua preferenza, ma avevi gia' votato e si puo' concedere un solo voto per persona."
        
    
    resp = make_response(render_template(
        'vote.html',
        title='Votazione',
        year=datetime.now().year,
        message=my_message,
        cookie_msg = the_cookie
        ))

    
    if the_cookie:
        resp.set_cookie(active_cookie, the_cookie, max_age=60*60*24*30)       

    return resp



@app.route('/classifica')
def classifica():
    """Renders the hit page."""

    app.logger.debug(calcola_classifica())

    return render_template(
        'classifica.html',
        title='Classifica',
        year=datetime.now().year,
        message='Classifica della competizione',
        body_classifica = calcola_classifica()
    )


@app.route('/new_contest/', methods=['GET', 'POST'])
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

        msg = f'Post! Hai passato il parametro {descrizione}.'
        esito, messaggio = create_contest(descrizione=descrizione, data=datetime.now())

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


