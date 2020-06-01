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
    
    voti = db.relationship("Voti", backref="voti")
    
    def __repr__(self):
        return "<Contest(descrizione='%s', data_contest='%s', stato='%s', cookie='%s', ts='%s')>" % \
                (self.descrizione, self.data_contest, self.stato, self.cookie, self.ts)





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
