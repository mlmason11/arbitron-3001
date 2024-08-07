from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates


metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class ArbitrageOpportunity(db.Model):

	__tablename__ = 'arbitrage_opportunities'

	id = db.Column(db.Integer, primary_key=True)
	moneyline_1 = db.Column(db.String)
	moneyline_2 = db.Column(db.String)
	decimal_1 = db.Column(db.Float)
	decimal_2 = db.Column(db.Float)
	stake_1_percent = db.Column(db.Float)
	stake_2_percent = db.Column(db.Float)
	profit_percent = db.Column(db.Float)
	date = db.Column(db.String)
	time = db.Column(db.String)
	timezone = db.Column(db.String)
	game_date = db.Column(db.String)
	game_time = db.Column(db.String)

	event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
	league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))

	event = db.relationship('Event', back_populates='aos')
	league = db.relationship('League', back_populates='aos')
	bookkeepers = db.relationship('Bookkeeper', back_populates='aos')
	odds = db.relationship('Odds', back_populates='aos')
	teams = db.relationship('Team', back_populates='aos')


	def to_dict_short(self):
		return {
			'id': self.id,
			'moneyline_1': self.moneyline_1,
			'moneyline_2': self.moneyline_2,
			'decimal_1': self.decimal_1,
			'decimal_2': self.decimal_2,
			'stake_1_percent': self.stake_1_percent,
			'stake_2_percent': self.stake_2_percent,
			'profit_percent': self.profit_percent,
			'date': self.date,
			'time': self.time,
			'timezone': self.timezone,
			'game_date': self.game_date,
			'game_time': self.game_time,
			'event_id': self.event_id,
			'league_id': self.league_id
		}

	def to_dict(self):
		return {
			**(self.to_dict_short()),
			'event': self.event.to_dict_short(),
			'league': self.league.to_dict_short(),
			'bookkeepers': [bk.to_dict_short() for bk in self.bookkeepers],
			'teams': [t.to_dict_short() for t in self.teams]
		}

class Bet(db.Model):

	__tablename__ = 'bets'

	id = db.Column(db.Integer, primary_key=True)
	stake = db.Column(db.Float, nullable=False)
	predicted_outcome = db.Column(db.Float)
	actual_outcome = db.Column(db.Float)
	# created_at = db.Column(db.DateTime, default=datetime.utcnow)

	bookkeeper_id = db.Column(db.Integer, db.ForeignKey('bookkeepers.id'))
	odds_id = db.Column(db.Integer, db.ForeignKey('odds.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	bookkeeper = db.relationship('Bookkeepers', back_populates='bets')
	odds = db.relationship('Odds', back_populates='bets')
	user = db.relationship('User', back_populates='bets')

	def to_dict(self):
		return {
			'id': self.id,
			'stake': self.stake,
			'predicted_outcome': self.predicted_outcome,
			'actual_outcome': self.actual_outcome,
			# 'created_at': self.created_at,
			'bookkeeper_id': self.bookkeeper_id,
			'odds_id': self.odds_id,
			'user_id': self.user_id
		}

class Bookkeeper(db.Model):

	__tablename__ = 'bookkeepers'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	reliability_score = db.Column(db.String)
	avg_profit_percent = db.Column(db.Float)
	var_profit_percent = db.Column(db.Float)
	last_updated_utc = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

	aos = db.relationship('ArbitrageOpportunity', back_populates='bookkeepers')
	bets = db.relationship('Bet', back_populates='bookkeeper')
	odds = db.relationship('Odds', back_populates='bookkeeper')

	def to_dict_short(self):
		return {
			'id': self.id,
			'name': self.name,
			'reliability_score': self.reliability_score,
			'avg_profit_percent': self.avg_profit_percent,
			'var_profit_percent': self.var_profit_percent,
			'last_updated': self.last_updated
		}

	def to_dict(self):
		return {
			**(self.to_dict_short()),
			'aos': [ao.to_dict_short for ao in self.aos]
		}

class Event(db.Model):

	__tablename__ = 'events'

	id = db.Column(db.Integer, primary_key=True)
	date = db.Column(db.String)
	time = db.Column(db.String)

	league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))

	league = db.relationship('League', back_populates='events')
	odds = db.relationship('Odds', back_populates='event')
	teams = db.relationship('Team', back_populates='events')


class League(db.Model):

	__tablename__ = 'leagues'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	avg_profit_percent = db.Column(db.Float)
	var_profit_percent = db.Column(db.Float)
	last_updated_utc = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

	teams = db.relationship('Team', back_populates='league')
	events = db.relationship('Event', back_populates='league')
	aos = db.relationship('ArbitrageOpportunity', back_populates='league')

	def to_dict_short(self):
		return {
			'id': self.id,
			'name': self.name,
			'avg_profit_percent': self.avg_profit_percent,
			'var_profit_percent': self.var_profit_percent,
			'last_updated_utc': self.last_updated_utc
		}

	def to_dict(self):
		return {
			**(self.to_dict_short()),
			'teams': [t.to_dict_short() for t in self.teams],
			'events': [e.to_dict_short() for e in self.events]
		}

class Odds(db.Model):

	__tablename__ = 'odds'

	id = db.Column(db.Integer, primary_key=True)
	moneyline = db.Column(db.String, nullable=False)
	decimal = db.Column(db.Float)

	bookkeeper_id = db.Column(db.Integer, db.ForeignKey('bookkeepers.id'))
	event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
	league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
	team_id = db.Column(db.Integer, db.ForeignKey('team.id'))

	bookkeeper = db.relationship('Bookkeeper', back_populates='odds')
	event = db.relationship('Event', back_populates='odds')
	league = db.relationship('League', back_populates='odds')
	team = db.relationship('Team', back_populates='odds')
	aos = db.relationship('ArbitrageOpportunity', back_populates='odds')

class Team(db.Model):

	__tablename__ = 'teams'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	city = db.Column(db.String)
	avg_profit_percent = db.Column(db.Float)
	var_profit_percent = db.Column(db.Float)
	last_updated_utc = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

	league_id = db.Column(db.String, db.ForeignKey('leagues.id'))

	league = db.relationship('League', back_populates='teams')
	aos = db.relationship('ArbitrageOpportunity', back_populates='teams')

	def to_dict_short(self):
		return {
			'id': self.id,
			'name': self.name,
			'city': self.city,
			'avg_profit_percent': self.avg_profit_percent,
			'var_profit_percent': self.var_profit_percent,
			'last_updated': self.last_updated,
			'league_id': self.league_id,
			'league': self.league
		}

class User(db.Model):

	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, nullable=False, unique=True)
	password = db.Column(db.String)
	email = db.Column(db.String)
	balance = db.Column(db.Float)

	def to_dict(self):
		return {
			'id': self.id,
			'username': self.username,
			'email': self.email,
			'budget': self.budget
		}
