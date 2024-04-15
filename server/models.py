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

class User(db.Model):

	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, nullable=False, unique=True)
	password = db.Column(db.String)
	email = db.Column(db.String)
	budget = db.Column(db.Float)

	def to_dict(self):
		return {
			'id': self.id,
			'username': self.username,
			'email': self.email,
			'budget': self.budget
		}

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

	bookie_1_id = db.Column(db.Integer, db.ForeignKey('bookies.id'))
	bookie_2_id = db.Column(db.Integer, db.ForeignKey('bookies.id'))
	team_1_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
	team_2_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
	league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))

	bookie_1 = db.relationship('Bookie', back_populates='aos_as_bookie_1', foreign_keys=[bookie_1_id])
	bookie_2 = db.relationship('Bookie', back_populates='aos_as_bookie_2', foreign_keys=[bookie_2_id])
	team_1 = db.relationship('Team', back_populates='aos_as_team_1', foreign_keys=[team_1_id])
	team_2 = db.relationship('Team', back_populates='aos_as_team_2', foreign_keys=[team_2_id])
	league = db.relationship('League', back_populates='aos')


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
			'bookie_1_id': self.bookie_1_id,
			'bookie_2_id': self.bookie_2_id,
			'team_1_id': self.team_1_id,
			'team_2_id': self.team_2_id,
			'league_id': self.league_id
		}

	def to_dict(self):
		return {
			**(self.to_dict_short()),
			'bookie_1': self.bookie_1.to_dict_short(),
			'bookie_2': self.bookie_2.to_dict_short(),
			'team_1': self.team_1.to_dict_short(),
			'team_2': self.team_2.to_dict_short(),
			'league': self.league.to_dict_short()
		}

class Bookie(db.Model):

	__tablename__ = 'bookies'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	avg_profit_percent = db.Column(db.Float)
	var_profit_percent = db.Column(db.Float)
	last_updated_utc = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

	aos_as_bookie_1 = db.relationship('ArbitrageOpportunity', back_populates='bookie_1', foreign_keys=ArbitrageOpportunity.bookie_1_id)
	aos_as_bookie_2 = db.relationship('ArbitrageOpportunity', back_populates='bookie_2', foreign_keys=ArbitrageOpportunity.bookie_2_id)

	def to_dict_short(self):
		return {
			'id': self.id,
			'name': self.name,
			'avg_profit_percent': self.avg_profit_percent,
			'var_profit_percent': self.var_profit_percent,
			'last_updated': self.last_updated
		}

	def to_dict(self):
		return {
			**(self.to_dict_short()),
			'aos_as_bookie_1': [ao.to_dict_short for ao in self.aos_as_bookie_1],
			'aos_as_bookie_2': [ao.to_dict_short for ao in self.aos_as_bookie_2]
		}

class League(db.Model):

	__tablename__ = 'leagues'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	avg_profit_percent = db.Column(db.Float)
	var_profit_percent = db.Column(db.Float)
	last_updated_utc = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

	teams = db.relationship('Team', back_populates='league')
	aos = db.relationship('ArbitrageOpportunity', back_populates='league')

	def to_dict_short(self):
		return {
			'id': self.id,
			'name': self.name,
			'avg_profit_percent': self.avg_profit_percent,
			'var_profit_percent': self.var_profit_percent,
			'last_updated': self.last_updated
		}

	def to_dict(self):
		return {
			**(self.to_dict_short()),
			'teams': [team.to_dict_short() for team in self.teams],
			'aos': [ao.to_dict_short() for ao in self.aos]
		}

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
	aos_as_team_1 = db.relationship('ArbitrageOpportunity', back_populates='team_1', foreign_keys=ArbitrageOpportunity.team_1_id)
	aos_as_team_2 = db.relationship('ArbitrageOpportunity', back_populates='team_2', foreign_keys=ArbitrageOpportunity.team_2_id)

	def to_dict_short(self):
		return {
			'id': self.id,
			'name': self.name,
			'city': self.city,
			'avg_profit_percent': self.avg_profit_percent,
			'var_profit_percent': self.var_profit_percent,
			'last_updated': self.last_updated,
			'league_id': self.league_id
		}

	def to_dict(self):
		return {
			**(self.to_dict_short),
			'league': self.league.to_dict_short(),
			'aos_as_team_1': [ao.to_dict_short() for ao in self.aos_as_team_1],
			'aos_as_team_2': [ao.to_dict_short() for ao in self.aos_as_team_2]
		}