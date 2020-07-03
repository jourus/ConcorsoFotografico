# coding=latin-1

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import Column, Integer, String, Date

from Concorso import app


db = SQLAlchemy(app)



class Contest(db.Model):
    __tablename__='contest'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    descrizione = db.Column('descrizione', db.String(100), unique=True)
    data_contest = db.Column('data_contest', db.DateTime)
    stato = db.Column('stato', db.String(10))
    cookie = db.Column('cookie', db.String(50), unique=True)
    ts = db.Column('ts', db.Date)
    max_voti = db.Column('max_voti', db.Integer, nullable=True, default=0)
    
    voti = db.relationship("Voti", backref="voti")
    
    def __repr__(self):
        return "<Contest(descrizione='%s', data_contest='%s', stato='%s', cookie='%s', ts='%s', max_voti='%s')>" % \
                (self.descrizione, self.data_contest, self.stato, self.cookie, self.ts, self.max_voti)





class Voti(db.Model):
    __tablename__='voti'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    # id_contest = db.Column('id_contest', db.Integer)

    id_contest = db.Column('id_contest', db.Integer, \
        db.ForeignKey('contest.id'), nullable=False)

    voto = db.Column('voto', db.String(100))
    ts = db.Column('ts', db.Date)


    def __repr__(self):
        return "<Contest(id_contest='%s', voto='%s', ts='%s')>" % \
                (self.id_contest, self.voto,  self.ts)



class User(db.Model):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    __tablename__ = 'user'

    email = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
    
    def check_password(self, password):
        """Verifica che la password sia valida"""
        return password == self.password;
            
        

