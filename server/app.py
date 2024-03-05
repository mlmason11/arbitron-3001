import requests
from bs4 import BeautifulSoup as BS
# from selenium import webdriver
from flask import Flask, jsonify, request, session, make_response
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from models import db, ArbitrageOpportunity, User, Team, League, Bookie
from helpers import NBA_TEAMS, NHL_TEAMS, MLB_TEAMS, add_arbitrages, clean_ncaab_team_name, create_games_dict_list, create_arbitrage_opportunities_list, logged_in_user, authorize

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

CORS(app)

bcrypt = Bcrypt(app)

def logged_in_user():
    return User.query.filter(User.id == session.get('user_id')).first()

def authorize():
    if not logged_in_user():
        return {'message': "No logged in user"}, 401


@app.route('/')
def index():
	return '<h1>Hello World!</h1>'

## ----- USER CREATION, DELETION, LOGIN, & SESSION ----- ##

# USER SIGNUP #
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
        return make_response( jsonify( new_user.to_dict() ), 201 )
    except Exception as e:
        return make_response( jsonify({ 'error': str(e) }), 406 )

# SESSION LOGIN #
@app.post('/login')
def login():
    data = request.json
    user = User.query.filter(User.username == data['username']).first()

    if user and bcrypt.check_password_hash(user.password, data['password']):
        session['user_id'] = user.id
        return make_response(jsonify(user.to_dict()), 202)
    else:
        return make_response( jsonify({ 'error': "Username and Password don't match any accounts" }), 401 )

# LOGOUT #
@app.delete('/logout')
def logout():
    session.pop('user_id')
    return make_response( jsonify({}), 204 )

# CHECK SESSION #
@app.get('/check_session')
def check_session():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        return make_response( jsonify( user.to_dict() ), 200 )
    else:
        return make_response( jsonify({}), 401 )

@app.route('/nba')
def nba():
	# Retrieve information from the website and make the BeautifulSoup object, our "soup"
	data = requests.get('https://www.sportsbookreview.com/betting-odds/nba-basketball/money-line/full-game/')
	soup = BS(data.text, 'html.parser')

	# We get the specific information from the selected html elements in the BeautifulSoup object
	date = soup.find('p', class_='OddsTable_timeText__lFfv_').get_text()
	game_times_list = [obj.contents[0].get_text() for obj in soup.find_all('div', class_='GameRows_timeContainer__27ifL')]
	teams_list = [obj.get_text() for obj in soup.find_all('span', class_='GameRows_participantBox__0WCRz')]
	odds_numbers_list = [obj.contents[1].get_text() for obj in soup.find_all('span', class_='OddsCells_pointer___xLMm')]
	bookies_list = [obj.contents[0].attrs['href'].split('/')[-1].split('_')[0] for obj in soup.find_all('div', class_='Sportsbooks_sportbook__FqMkt')]

	game_dict_list = create_games_dict_list(game_times_list, date, teams_list, bookies_list, odds_numbers_list)
	arbitrage_opportunity_list = create_arbitrage_opportunities_list(game_dict_list, bookies_list, league_name='nba')
	add_arbitrages(arbitrage_opportunity_list, NBA_TEAMS)

	# Return any arbitrage opportunities as a jsonified list. If there are no opportunities then we notifiy the user of this.
	if len(arbitrage_opportunity_list) > 0:
		return make_response(jsonify(arbitrage_opportunity_list), 200)
	else:
		# return make_response(jsonify({'error': 'no arbitrage opportunities can be found at this time'}), 200)
		return make_response(jsonify(game_dict_list))

@app.route('/nhl')
def nhl():
	# Retrieve information from the website and make the BeautifulSoup object, our "soup"
	data = requests.get('https://www.sportsbookreview.com/betting-odds/nhl-hockey/')
	soup = BS(data.text, 'html.parser')

	# We get the specific information from the selected html elements in the BeautifulSoup object
	date = soup.find('p', class_='OddsTable_timeText__lFfv_').get_text()
	game_times_list = [obj.contents[0].get_text() for obj in soup.find_all('div', class_='GameRows_timeContainer__27ifL')]
	teams_list = [obj.contents[1].contents[0].get_text() for obj in soup.find_all('div', class_='GameRows_participantContainer__6Rpfq')]
	odds_numbers_list = [obj.contents[1].get_text() for obj in soup.find_all('span', class_='OddsCells_pointer___xLMm')]
	bookies_list = [obj.contents[0].attrs['href'].split('/')[-1].split('_')[0] for obj in soup.find_all('div', class_='Sportsbooks_sportbook__FqMkt')]

	game_dict_list= create_games_dict_list(game_times_list, date, teams_list, bookies_list, odds_numbers_list)
	arbitrage_opportunity_list = create_arbitrage_opportunities_list(game_dict_list, bookies_list, league_name='nhl')
	add_arbitrages(arbitrage_opportunity_list, NHL_TEAMS)

	# Return any arbitrage opportunities as a jsonified list. If there are no opportunities then we notifiy the user of this.
	if len(arbitrage_opportunity_list) > 0:
		return make_response(jsonify(arbitrage_opportunity_list), 200)
	else:
		# return make_response(jsonify({'error': 'no arbitrage opportunities can be found at this time'}), 200)
		return make_response(jsonify({'error': 'no arbitrage betting opportunities available at this time'}))

@app.route('/ncaab')
def ncaab():
	# Retrieve information from the website and make the BeautifulSoup object, our "soup"
	data = requests.get('https://www.sportsbookreview.com/betting-odds/ncaa-basketball/money-line/full-game/')
	soup = BS(data.text, 'html.parser')

	# We get the specific information from the selected html elements in the BeautifulSoup object
	date = soup.find('p', class_='OddsTable_timeText__lFfv_').get_text()
	game_times_list = [obj.contents[0].get_text() for obj in soup.find_all('div', class_='GameRows_timeContainer__27ifL')]
	teams_list = [clean_ncaab_team_name(obj.contents[1].contents[0].get_text()) for obj in soup.find_all('div', class_='GameRows_participantContainer__6Rpfq')]
	odds_numbers_list = [obj.contents[1].get_text() for obj in soup.find_all('span', class_='OddsCells_pointer___xLMm')]
	bookies_list = [obj.contents[0].attrs['href'].split('/')[-1].split('_')[0] for obj in soup.find_all('div', class_='Sportsbooks_sportbook__FqMkt')]

	game_dict_list= create_games_dict_list(game_times_list, date, teams_list, bookies_list, odds_numbers_list)
	arbitrage_opportunity_list = create_arbitrage_opportunities_list(game_dict_list, bookies_list, league_name='ncaab')
	add_arbitrages(arb_list=arbitrage_opportunity_list, team_names_dict={})

	# Return any arbitrage opportunities as a jsonified list. If there are no opportunities then we notifiy the user of this.
	if len(arbitrage_opportunity_list) > 0:
		return make_response(jsonify(arbitrage_opportunity_list), 200)
	else:
		# return make_response(jsonify({'error': 'no arbitrage opportunities can be found at this time'}), 200)
		return make_response(jsonify(game_dict_list))

@app.route('/mlb')
def mlb():
	# Retrieve information from the website and make the BeautifulSoup object, our "soup"
	data = requests.get('https://www.sportsbookreview.com/betting-odds/mlb-baseball/')
	soup = BS(data.text, 'html.parser')

	# We get the specific information from the selected html elements in the BeautifulSoup object
	date = soup.find('p', class_='OddsTable_timeText__lFfv_').get_text()
	game_times_list = [obj.contents[0].get_text() for obj in soup.find_all('div', class_='GameRows_timeContainer__27ifL')]
	teams_list = [obj.contents[1].contents[0].get_text() for obj in soup.find_all('div', class_='GameRows_participantContainer__6Rpfq')]
	odds_numbers_list = [obj.contents[1].get_text() for obj in soup.find_all('span', class_='OddsCells_pointer___xLMm')]
	bookies_list = [obj.contents[0].attrs['href'].split('/')[-1].split('_')[0] for obj in soup.find_all('div', class_='Sportsbooks_sportbook__FqMkt')]

	game_dict_list= create_games_dict_list(game_times_list, date, teams_list, bookies_list, odds_numbers_list)
	arbitrage_opportunity_list = create_arbitrage_opportunities_list(game_dict_list, bookies_list, league_name='mlb')
	add_arbitrages(arb_list=arbitrage_opportunity_list, team_names_dict=MLB_TEAMS)

	# Return any arbitrage opportunities as a jsonified list. If there are no opportunities then we notifiy the user of this.
	if len(arbitrage_opportunity_list) > 0:
		return make_response(jsonify(arbitrage_opportunity_list), 200)
	else:
		# return make_response(jsonify({'error': 'no arbitrage opportunities can be found at this time'}), 200)
		return make_response(jsonify(game_dict_list))

@app.get('/arbitrage_opportunities')
def get_arbitrage_opportunities_all():
	try:
		aos = ArbitrageOpportunity.query.all()
		ao_list = [ao.to_dict() for ao in aos]
		return make_response( jsonify( ao_list ), 200 )
	except AttributeError:
		return make_response( jsonify({ 'error': '404 arbitrage opportunities not found' }), 404 )

@app.get('/arbitrage_opportunities/<int:id>')
def get_arbitrage_opportunity_by_id():
	try:
		aos = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.id == id).first()
		ao_list = [ao.to_dict() for ao in aos]
		return make_response( jsonify( ao_list ), 200 )
	except AttributeError:
		return make_response( jsonify({ 'error': '404 arbitrage opportunities not found' }), 404 )

@app.get('/leagues/')
def get_leagues_all():
	try:
		leagues = League.query.all()
		league_list = [league.to_dict() for league in leagues]
		return make_response( jsonify( league_list ), 200 )
	except AttributeError:
		return make_response( jsonify({ 'error': '404 leagues not found' }), 404 )

@app.get('/leagues/<int:id>')
def get_league_by_id():
	try:
		league = League.query.filter(League.id == id).first()
		league_aos = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.league_id == id)
		league_ao_list = [lao.to_dict() for lao in league_aos]
		league_info_list = [league.to_dict(), *league_ao_list]
		return make_response( jsonify( league_info_list ), 200 )
	except AttributeError:
		return make_response( jsonify({ 'error': '404 team not found' }), 404 )

@app.get('/teams/')
def get_teams_all():
	try:
		teams = Team.query.all()
		team_list = [team.to_dict() for team in teams]
		return make_response( jsonify( team_list ), 200 )
	except AttributeError:
		return make_response( jsonify({ 'error': '404 teams not found' }), 404 )

# @app.get('/teams/league/<int:id>')
# def get_teams_by_league_id():
# 	try:
# 		teams = Team.query.filter(Team.league_id == id)
# 		team_list = [team.to_dict() for team in teams]
# 		return make_response( jsonify( team_list ), 200 )
# 	except AttributeError:
# 		return make_response( jsonify({ 'error': '404 teams not found' }), 404 )

@app.get('/teams/<int:id>')
def get_team_by_id():
	try:
		team = Team.query.filter(Team.id == id).first()
		team_aos_1 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.team_1_id == id)
		tao1_list = [tao1.to_dict() for tao1 in team_aos_1]
		team_aos_2 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.team_2_id == id)
		tao2_list = [tao2.to_dict() for tao2 in team_aos_2]
		team_info_list = [team.to_dict(), *tao1_list, *tao2_list]
		return make_response( jsonify( team_info_list ), 200 )
	except AttributeError:
		return make_response( jsonify({ 'error': '404 team not found' }), 404 )

@app.get('/bookkeepers/')
def get_bookkeepers_all():
	try:
		bks = Bookie.query.all()
		bk_list = [bk.to_dict() for bk in bks]
		return make_response( jsonify( bk_list ), 200 )
	except AttributeError:
		return make_response( jsonify({ 'error': '404 bookkeepers not found' }), 404 )

@app.get('/bookkeepers/<int:id>')
def get_bookkeeper_by_id():
	try:
		bk = Bookie.query.filter(Bookie.id == id).first()
		bk_aos_1 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.bookie_1_id == id)
		bkao1_list = [bkao1.to_dict() for bkao1 in bk_aos_1]
		bk_aos_2 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.bookie_2_id == id)
		bkao2_list = [bkao2.to_dict() for bkao2 in bk_aos_2]
		bk_info_list = [bk.to_dict(), *bkao1_list, *bkao2_list]
		return make_response( jsonify( bk_info_list ), 200 )
	except AttributeError:
		return make_response( jsonify({ 'error': '404 bookkeeper not found' }), 404 )

if __name__ == '__main__':
    app.run(port=5555, debug=True)