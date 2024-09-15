from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

# MetaData to handle naming conventions for constraints
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
})

# Initialize the SQLAlchemy object
db = SQLAlchemy(metadata=metadata)

class ArbitrageOpportunity(db.Model):
    __tablename__ = 'arbitrage_opportunities'

    id = db.Column(db.Integer, primary_key=True)
    profit_percent = db.Column(db.Float)
    game_date = db.Column(db.String)
    game_time = db.Column(db.String)

    # Foreign keys to connect relationships
    bookkeeper_1_id = db.Column(db.Integer, db.ForeignKey('bookkeepers.id'))
    bookkeeper_2_id = db.Column(db.Integer, db.ForeignKey('bookkeepers.id'))
    team_1_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    team_2_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    league_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))

    # Relationships to associate entities
    bookkeeper_1 = db.relationship('Bookkeeper', foreign_keys=[bookkeeper_1_id], back_populates='arbitrage_opportunities_as_bk1')
    bookkeeper_2 = db.relationship('Bookkeeper', foreign_keys=[bookkeeper_2_id], back_populates='arbitrage_opportunities_as_bk2')
    team_1 = db.relationship('Team', foreign_keys=[team_1_id], back_populates='arbitrage_opportunities_as_team1')
    team_2 = db.relationship('Team', foreign_keys=[team_2_id], back_populates='arbitrage_opportunities_as_team2')
    league = db.relationship('League', back_populates='arbitrage_opportunities')

    def to_dict(self):
        return {
            'id': self.id,
            'profit_percent': self.profit_percent,
            'game_date': self.game_date,
            'game_time': self.game_time,
            'bookkeeper_1': self.bookkeeper_1.to_dict_short(),
            'bookkeeper_2': self.bookkeeper_2.to_dict_short(),
            'team_1': self.team_1.to_dict_short(),
            'team_2': self.team_2.to_dict_short(),
            'league': self.league.to_dict_short()
        }

class Bookkeeper(db.Model):
    __tablename__ = 'bookkeepers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    avg_profit_percent = db.Column(db.Float)
    var_profit_percent = db.Column(db.Float)

    # Relationships to arbitrage opportunities (as bk1 and bk2)
    arbitrage_opportunities_as_bk1 = db.relationship('ArbitrageOpportunity', foreign_keys='ArbitrageOpportunity.bookkeeper_1_id', back_populates='bookkeeper_1')
    arbitrage_opportunities_as_bk2 = db.relationship('ArbitrageOpportunity', foreign_keys='ArbitrageOpportunity.bookkeeper_2_id', back_populates='bookkeeper_2')

    # Relationship to bets
    bets = db.relationship('Bet', back_populates='bookkeeper')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'avg_profit_percent': self.avg_profit_percent,
            'var_profit_percent': self.var_profit_percent
        }

    def to_dict_short(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    avg_profit_percent = db.Column(db.Float)
    var_profit_percent = db.Column(db.Float)

    # Relationships to arbitrage opportunities (as team1 and team2)
    arbitrage_opportunities_as_team1 = db.relationship('ArbitrageOpportunity', foreign_keys='ArbitrageOpportunity.team_1_id', back_populates='team_1')
    arbitrage_opportunities_as_team2 = db.relationship('ArbitrageOpportunity', foreign_keys='ArbitrageOpportunity.team_2_id', back_populates='team_2')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'avg_profit_percent': self.avg_profit_percent,
            'var_profit_percent': self.var_profit_percent
        }

    def to_dict_short(self):
        return {
            'id': self.id,
            'name': self.name
        }

class League(db.Model):
    __tablename__ = 'leagues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    avg_profit_percent = db.Column(db.Float)
    var_profit_percent = db.Column(db.Float)

    # Relationship to arbitrage opportunities
    arbitrage_opportunities = db.relationship('ArbitrageOpportunity', back_populates='league')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'avg_profit_percent': self.avg_profit_percent,
            'var_profit_percent': self.var_profit_percent
        }

    def to_dict_short(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Bet(db.Model):
    __tablename__ = 'bets'

    id = db.Column(db.Integer, primary_key=True)
    stake = db.Column(db.Float, nullable=False)
    predicted_outcome = db.Column(db.Float)
    actual_outcome = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    bookkeeper_id = db.Column(db.Integer, db.ForeignKey('bookkeepers.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    bookkeeper = db.relationship('Bookkeeper', back_populates='bets')
    user = db.relationship('User', back_populates='bets')

    def to_dict(self):
        return {
            'id': self.id,
            'stake': self.stake,
            'predicted_outcome': self.predicted_outcome,
            'actual_outcome': self.actual_outcome,
            'created_at': self.created_at,
            'bookkeeper_id': self.bookkeeper_id,
            'user_id': self.user_id
        }

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    balance = db.Column(db.Float)

    # Relationship to bets
    bets = db.relationship('Bet', back_populates='user')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'balance': self.balance
        }
