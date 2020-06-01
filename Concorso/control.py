# coding=latin-1

import sys

#sys.path.append("C:\\Users\\jouru\\source\\repos\\FlaskWebProject1\\FlaskWebProject1\\ConcorsoFotografico2020\\")  
# sys.path.append("")

from model import Voti, Contest, db
from datetime import datetime
from flask import Flask
from sqlalchemy import func, orm
from secrets import token_urlsafe

# app = Flask(__name__)

from Concorso import app

def add_vote(choice):
    try:
        app.logger.info ('Tentativo di voto...')
        contest = get_active_contest()
        
        if contest == None:
            raise Exception("Nessun contest attivo!")

        new_vote = Voti(voto=choice, id_contest = contest, ts=datetime.now())
        
        print(new_vote.voto)
        
        db.session.add(new_vote)
        db.session.commit()
        return True
    except Exception as ex:
        app.logger.error(ex)
        return False
    
def setup_db():
    db.create_all()


def get_active_contest():
    try:
        return db.session.query(Contest.id).filter(Contest.stato == 'attivo').scalar()

    except orm.exc.MultipleResultsFound as multi_line:
        app.logger.error('Too many active row found!')
        raise multi_line



def calcola_classifica(contest_id=None):
    """ Calcola la classifica finale per un certo contest.

        :param contest_id: Rappresenta l'id del contest di cui preparare la 
                  classifica. Se non viene passato, viene assegnato in 
                  automatico quello del contest attivo.
        :return:
    """
    conteggio = func.count(Voti.voto)

    if contest_id==None:
        contest_id = get_active_contest()

    return db.session.query(Voti.voto, conteggio).filter(Voti.id_contest == contest_id).group_by(Voti.voto).order_by(conteggio.desc(), Voti.voto).all()


def get_active_cookie():
    _contest = get_active_contest()

    return db.session.query(Contest.cookie).filter(Contest.id == _contest).scalar()
    
def close_active_contest():
    _contest = get_active_contest()
    x = db.session.query(Contest).get(_contest)  
    x.stato = 'concluso'
    db.session.commit()

 

def create_contest(descrizione, data):
    
    if get_active_contest() != None:
        app.logger.warning("Tentativo di creare un nuovo contest quando ce n'è un altro attivo.")
        return False, "Tentativo di creare un nuovo contest quando ce n'è un altro attivo."

    new_contest = Contest(descrizione=descrizione, data_contest=data, stato='attivo', cookie=new_cookie(), ts=datetime.now())

    db.session.add(new_contest)
    db.session.commit()

    return True, ''


def new_cookie():
    """
        Restituisce un token url safe da usare come cookie per le votazioni.
    """
    return f"Vote_{token_urlsafe()}"

    
def stampa_classifica(contest_id=None):
    """
        Prepara l'html del body della tabella della classifica.
        Per puro divertimento, uso due volte la map per applicare tale formattazione.

        Richiede l'id del contest, se non viene passato, prende quello attivo.

    """

    if contest_id == None:
        contest_id = get_active_contest()

    # richiamo il calcolo della classifica
    risultati = calcola_classifica(contest_id)

    # mini funzione per formattare tutte le celle di una riga
    def cell(z): return f"<td>{z}<\\td>"
    
    # mini funzione per formattare le righe (usando la funzione cell)
    def row(r): return f"<tr>{''.join(map(cell,r))}<\\tr>\n"

    # join finale
    return ''.join(map(row, risultati))
