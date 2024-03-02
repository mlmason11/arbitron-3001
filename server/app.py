import requests
from bs4 import BeautifulSoup as BS
# from selenium import webdriver
from flask import Flask, jsonify, request, session, make_response
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from models import db, ArbitrageOpportunity, User, Team, League, Bookie
from helpers import NBA_TEAMS, NHL_TEAMS, MLB_TEAMS, add_arbitrages, clean_ncaab_team_name, create_games_dict_list, create_arbitrage_opportunities_list

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

migrate = Migrate(app, db)

db.init_app(app)

CORS(app)

@app.route('/')
def index():
	return '<h1>Hello World!</h1>'

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
def get_arbitrage_opportunities():
	pass

# @app.post('/arbitrage_opportunities')
# def add_arbitrage_opportunity():
#     try:
#         a_o_data = request.json
#         new_a_o = ArbitrageOpportunity(**a_o_data)
#         db.session.add(new_a_o)
#         # session['most_recent_recipe_id'] = new_recipe.id
#         db.session.commit()
#         return make_response( jsonify( new_a_o.to_dict() ), 201 )
#     except Exception as e:
#        return make_response ( jsonify({ 'error': str(e) }), 406 )

# @app.post('/teams')
# def add_arbitrage_opportunity():
#     try:
#         team_data = request.json
#         new_team = Team(**team_data)
#         db.session.add(new_team)
#         # session['most_recent_recipe_id'] = new_recipe.id
#         db.session.commit()
#         return make_response( jsonify( new_team.to_dict() ), 201 )
#     except Exception as e:
#        return make_response ( jsonify({ 'error': str(e) }), 406 )

# @app.post('/leagues')
# def add_league():
#     try:
#         league_data = request.json
#         new_league = Team(**league_data)
#         db.session.add(new_league)
#         # session['most_recent_recipe_id'] = new_recipe.id
#         db.session.commit()
#         return make_response( jsonify( new_league.to_dict() ), 201 )
#     except Exception as e:
#        return make_response ( jsonify({ 'error': str(e) }), 406 )

if __name__ == '__main__':
    app.run(port=5555, debug=True)