# coding=latin-1

from Concorso.model import Voti, Contest, db
from datetime import datetime
from flask import Flask
from sqlalchemy import func, orm
from secrets import token_urlsafe
from Concorso import app

def add_vote(choice):
    """
        Inserisce il voto richiesto per il contest corrente.
        1.  Recupera il contest corrente;
        2.  Se non esiste un contest attivo, solleva un'eccezione;
        3.  Inserisce il voto
    """

    try:
        app.logger.info ('Tentativo di voto...')
        contest = get_active_contest()
        
        if contest == None:
            raise Exception("Nessun contest attivo!")

        new_vote = Voti(voto=choice, id_contest = contest, ts=datetime.now())
        
        app.logger.debug(f"Il voto richiesto è {new_vote.voto}")
        
        db.session.add(new_vote)
        db.session.commit()
        return True

    except Exception as ex:
        app.logger.error(ex)
        return False
    
def setup_db():
    """
        Inizializza il db da zero;
    """
    db.create_all()


def get_active_contest():
    """
        Recupera l'id del contest corrente
    """
    try:
        return db.session.query(Contest.id).filter(Contest.stato == 'attivo').scalar()

    except orm.exc.MultipleResultsFound as multi_line:
        app.logger.error('Too many active contests found!')
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
    """
        Restituisce il nome del cookie di salvataggio del voto per il contest attivo.
    """

    _contest = get_active_contest()

    return db.session.query(Contest.cookie).filter(Contest.id == _contest).scalar()
    
def close_active_contest():
    """
        Chiude il contest corrente.
        Va a buon fine anche se non ce ne sono di attivi.
        : return    True --> Tutto ok
                    False --> Errore.
    """
    try:
        _contest = get_active_contest()
        if _contest == None:
            return True

        x = db.session.query(Contest).get(_contest)  
        x.stato = 'concluso'
        db.session.commit()
        return True

    except Exception as ex:
        app.logger.error("Tentativo di chiusura del contest fallito", ex)
        return False
        

    
 

def create_contest(descrizione, data):
    """
        Crea un  nuovo contest (se non ce ne sono già di attivi.)
        In tal caso, restituisce una tupla con il messaggio di errore.
        T.B.D. --> Ci potrebbe essere un errore se si prova a creare un contest con una descrizione già presente in db.
    """

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

    

def get_elenco_contest():
    """
        Restituisce l'elenco dei contest attivi;
    """
    return db.session.query(Contest.id, Contest.descrizione, Contest.stato).all()
    # for riga in lista:
    #     print(riga.id, riga.descrizione, riga.stato)


def represents_int(s):
    """
        Verifica che una certa stringa rappresenti un intero.
    """
    if s == None:
        return False

    try: 
        int(s)
        return True
    except ValueError:
        return False


# def stampa_classifica(contest_id=None):
#     """
#         Prepara l'html del body della tabella della classifica.
#         Per puro divertimento, uso due volte la map per applicare tale formattazione.

#         Richiede l'id del contest, se non viene passato, prende quello attivo.

#     """

#     if contest_id == None:
#         contest_id = get_active_contest()

#     # richiamo il calcolo della classifica
#     risultati = calcola_classifica(contest_id)

#     # mini funzione per formattare tutte le celle di una riga
#     def cell(z): return f"<td>{z}<\\td>"
    
#     # mini funzione per formattare le righe (usando la funzione cell)
#     def row(r): return f"<tr>{''.join(map(cell,r))}<\\tr>\n"

#     # join finale
#     return ''.join(map(row, risultati))
