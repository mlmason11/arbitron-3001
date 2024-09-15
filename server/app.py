import requests
from bs4 import BeautifulSoup as BS
from flask import Flask, jsonify, request, session, make_response
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from models import db, ArbitrageOpportunity, User, Team, League, Bookkeeper
from helpers import NBA_TEAMS, NHL_TEAMS, MLB_TEAMS, add_arbitrages, clean_ncaab_team_name, create_games_dict_list, create_arbitrage_opportunities_list, update_avg_profit_and_variance, get_sport_data

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
CORS(app)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return '<h1>Hello World!</h1>'

## ----- USER CREATION, DELETION, LOGIN, & SESSION ----- ##

@app.post('/users')
def create_user():
    try:
        data = request.json
        password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(
            username=data['username'],
            password=password_hash,
            email=data['email'],
            budget=data['budget']
        )
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return make_response(jsonify(new_user.to_dict()), 201)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 406)

@app.post('/login')
def login():
    try:
        data = request.json
        user = User.query.filter(User.username == data['username']).first()
        if bcrypt.check_password_hash(user.password, data['password']):
            session['user_id'] = user.id
            return make_response(jsonify(user.to_dict()), 202)
        else:
            raise Exception("Username and Password don't match any accounts")
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 401)

@app.delete('/logout')
def logout():
    session.pop('user_id')
    return make_response(jsonify({}), 204)

@app.get('/check_session')
def check_session():
    try:
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        return make_response(jsonify(user.to_dict()), 200)
    except Exception:
        return make_response(jsonify({}), 401)

## ----- BOOKKEEPER ROUTES ----- ##

@app.get('/bookkeepers/')
def get_all_bookkeepers():
    """Returns a list of all bookkeepers with their average profit and variance."""
    try:
        bookkeepers = Bookkeeper.query.all()
        bookkeeper_list = [bk.to_dict() for bk in bookkeepers]
        return make_response(jsonify(bookkeeper_list), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.get('/bookkeepers/<int:id>')
def get_bookkeeper_by_id(id):
    """Returns detailed data about a specific bookkeeper, including odds, average profit, and arbitrage opportunities."""
    try:
        bookkeeper = Bookkeeper.query.filter(Bookkeeper.id == id).first()
        arbs_as_bk1 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.Bookkeeper_1_id == id).all()
        arbs_as_bk2 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.Bookkeeper_2_id == id).all()
        arbs_list = [arb.to_dict() for arb in arbs_as_bk1 + arbs_as_bk2]

        response = {
            'bookkeeper': bookkeeper.to_dict(),
            'arbitrage_opportunities': arbs_list
        }
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)

## ----- TEAM ROUTES ----- ##

@app.get('/teams/')
def get_all_teams():
    """Returns a list of all teams with their average profit and variance."""
    try:
        teams = Team.query.all()
        team_list = [team.to_dict() for team in teams]
        return make_response(jsonify(team_list), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.get('/teams/<int:id>')
def get_team_by_id(id):
    """Returns detailed data about a specific team, including odds, average profit, variance, and arbitrage opportunities."""
    try:
        team = Team.query.filter(Team.id == id).first()
        team_arbs_1 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.team_1_id == id).all()
        team_arbs_2 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.team_2_id == id).all()
        team_arb_list = [arb.to_dict() for arb in team_arbs_1 + team_arbs_2]

        response = {
            'team': team.to_dict(),
            'arbitrage_opportunities': team_arb_list
        }
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)

## ----- LEAGUE ROUTES ----- ##

@app.get('/leagues/')
def get_all_leagues():
    """Returns a list of all leagues with their average profit and variance."""
    try:
        leagues = League.query.all()
        league_list = [league.to_dict() for league in leagues]
        return make_response(jsonify(league_list), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.get('/leagues/<int:id>')
def get_league_by_id(id):
    """Returns detailed data about a specific league, including odds, average profit, variance, and arbitrage opportunities."""
    try:
        league = League.query.filter(League.id == id).first()
        league_arbs = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.league_id == id).all()
        arb_list = [arb.to_dict() for arb in league_arbs]

        response = {
            'league': league.to_dict(),
            'arbitrage_opportunities': arb_list
        }
        return make_response(jsonify(response), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 404)

## ----- NBA, NHL, NCAAB, MLB SCRAPING ROUTES ----- ##

@app.route('/nba')
def nba():
    try:
        url = 'https://www.sportsbookreview.com/betting-odds/nba-basketball/money-line/full-game/'
        game_data = get_sport_data(url, lambda obj: obj.get_text(), league_name='nba', team_names_dict=NBA_TEAMS)
        return make_response(jsonify(game_data), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/nhl')
def nhl():
    try:
        url = 'https://www.sportsbookreview.com/betting-odds/nhl-hockey/'
        game_data = get_sport_data(url, lambda obj: obj.contents[1].contents[0].get_text(), league_name='nhl', team_names_dict=NHL_TEAMS)
        return make_response(jsonify(game_data), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/ncaab')
def ncaab():
    try:
        url = 'https://www.sportsbookreview.com/betting-odds/ncaa-basketball/money-line/full-game/'
        game_data = get_sport_data(url, lambda obj: clean_ncaab_team_name(obj.contents[1].contents[0].get_text()), league_name='ncaab')
        return make_response(jsonify(game_data), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/mlb')
def mlb():
    try:
        url = 'https://www.sportsbookreview.com/betting-odds/mlb-baseball/'
        game_data = get_sport_data(url, lambda obj: obj.contents[1].contents[0].get_text(), league_name='mlb', team_names_dict=MLB_TEAMS)
        return make_response(jsonify(game_data), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
