from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
# from string import ascii_lowercase, ascii_uppercase, digits, punctuation


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})


db = SQLAlchemy(metadata=metadata)


class User(db.Model):

	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, nullable=False, unique=True)
	password = db.Column(db.String)
	first_name = db.Column(db.String, nullable=False)
	last_name = db.Column(db.String, nullable=False)
	budget = db.Column(db.Float)


class ArbitrageOpportunity(db.Model):

	__tablename__ = 'arbitrage_opportunities'

	id = db.Column(db.Integer, primary_key=True)
	bookie_1_id = db.Column(db.String, db.ForeignKey('bookies.id'))
	bookie_2_id = db.Column(db.String, db.ForeignKey('bookies.id'))
	team_1_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
	team_2_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
	league_id = db.Column(db.String, db.ForeignKey('leagues.id'))
	profit = db.Column(db.Float)
	day = db.Column(db.Integer)
	month = db.Column(db.Integer)
	year = db.Column(db.Integer)
	time = db.Column(db.String)

class Bookie(db.Model):

	__tablename__ = 'bookies'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)

class League(db.Model):

	__tablename__ = 'leagues'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	sport = db.Column(db.String)

	league_arbitrage_opportunities = db.relationship('LeagueArbitrageOpportunity', back_populates='league')
	arbitrage_opportunities = association_proxy('league_arbitrage_opportunities', 'league')

class Team(db.Model):

	__tablename__ = 'teams'

	id = db.Column(db.Integer, primary_key=True)
	league_id = db.Column(db.String, db.ForeignKey('leagues.id'))
	name = db.Column(db.String)
	city = db.Column(db.String)
	league = db.relationship('League', back_populates='teams')

	team_arbitrage_opportunities = db.relationship('TeamArbitrageOpportunity', back_populates='team')
	arbitrage_opportunities = association_proxy('team_arbitrage_opportunities', 'team')

class LeagueArbitrageOpportunity(db.Model):

	__tablename__ = 'league_arbitrage_opportunities'

	id = db.Column(db.Integer, primary_key=True)
	arbitrage_opportunity_id = db.Column(db.Integer, db.ForeignKey('arbitrage_opportunities.id'))
	league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))

	arbitrage_opportunity = db.relationship('ArbitrageOpportunity', back_populates='league_arbitrage_opportunities')
	league = db.relationship('League', back_populates='league_arbitrage_opportunities')

class TeamArbitrageOpportunity(db.Model):

	__tablename__ = 'team_arbitrage_opportunities'

	id = db.Column(db.Integer, primary_key=True)
	arbitrage_opportunity_id = db.Column(db.Integer, db.ForeignKey('arbitrage_opportunities.id'))
	team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))

	arbitrage_opportunity = db.relationship('ArbitrageOpportunity', back_populates='team_arbitrage_opportunities')
	team = db.relationship('Team', back_populates='team_arbitrage_opportunities')