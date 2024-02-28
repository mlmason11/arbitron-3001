import requests
import datetime
import leagues

from bs4 import BeautifulSoup as BS
from selenium import webdriver
from time import localtime, sleep
from flask import Flask, jsonify, request, session, make_response
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from models import db, ArbitrageOpportunity, User, Team, League, Bookie

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

migrate = Migrate(app, db)

db.init_app(app)

CORS(app)

# Calculates the odds in whole number + decimal form from the +/- moneyline form odds
# Takes in a string, returns a float
def odds_from_moneyline(moneyline):
	if len(moneyline) > 1 and int(moneyline[1:]):
		if moneyline[0] == '+':
			return (int(moneyline[1:]) / 100) + 1
		elif moneyline[0] == '-':
			return (100 / int(moneyline[1:])) + 1
		else:
			return 'moneyline must be an integer that is either positive or negative'
	else:
		return 'moneyline odds are not available for this matchup'

@app.route('/')
def index():
	return '<h1>Hello World!</h1>'

@app.route('/nba')
def nba():

	NBA_TEAMS = {
		"Atlanta": "Hawks",
		"Boston": "Celtics",
		"Brooklyn": "Nets",
		"Charlotte": "Hornets",
		"Chicago": "Bulls",
		"Cleveland": "Cavaliers",
		"Dallas": "Mavericks",
		"Denver": "Nuggets",
		"Detroit": "Pistons",
		"Golden State": "Warriors",
		"Houston": "Rockets",
		"Indiana": "Pacers",
		"Los Angeles Clippers": "Clippers",
		"Los Angeles Lakers": "Lakers",
		"Memphis": "Grizzlies",
		"Miami": "Heat",
		"Milwaukee": "Bucks",
		"Minnesota": "Timberwolves",
		"New Orleans": "Pelicans",
		"New York": "Knicks",
		"Oklahoma City": "Thunder",
		"Orlando": "Magic",
		"Philadelphia": "76ers",
		"Phoenix": "Suns",
		"Portland": "Trail Blazers",
		"Sacramento": "Kings",
		"San Antonio": "Spurs",
		"Toronto": "Raptors",
		"Utah": "Jazz",
		"Washington": "Wizards"
	}

	# Retrieve information from the website and make the BeautifulSoup object, our "soup"
	data = requests.get('https://www.sportsbookreview.com/betting-odds/nba-basketball/money-line/full-game/')
	soup = BS(data.text, 'html.parser')

	# We get the specific information from the selected html elements in the BeautifulSoup object
	date = soup.find('p', class_='OddsTable_timeText__lFfv_').get_text()
	game_times_list = [obj.contents[0].get_text() for obj in soup.find_all('div', class_='GameRows_timeContainer__27ifL')]
	teams_list = [obj.get_text() for obj in soup.find_all('span', class_='GameRows_participantBox__0WCRz')]
	odds_numbers_list = [obj.contents[1].get_text() for obj in soup.find_all('span', class_='OddsCells_pointer___xLMm')]
	bookies_list = [obj.contents[0].attrs['href'].split('/')[-1].split('_')[0] for obj in soup.find_all('div', class_='Sportsbooks_sportbook__FqMkt')]

	# Efficiently organize all information about each game in a list of dictionaries
	game_dict_list = []
	for i in range(0, len(game_times_list)):
		game_dict = {
			'game_date': date[:-1] if not type(date[-1]) == int else date,
			'game_time': game_times_list[i],
			'team_1': teams_list[2*i],
			'team_1_odds': {bookies_list[j]:odds_numbers_list[(12 * i) + (2 * j)] for j in range(0, len(bookies_list))},
			'team_2': teams_list[2*i+1],
			'team_2_odds': {bookies_list[j]:odds_numbers_list[(12 * i) + (2 * j) + 1] for j in range(0, len(bookies_list))}
		}
		game_dict_list.append(game_dict)

	# For each game in the dictionary we test for arbitrage opportunities using all the bookies for each team
	arbitrage_opportunity_list = []
	for game in game_dict_list:
		for i in range(0, len(bookies_list)):
			for j in range(0, len(bookies_list)):
				if i != j and game['team_1_odds'][bookies_list[i]] != '-' and game['team_2_odds'][bookies_list[j]] != '-':
					decimal_1 = 1/odds_from_moneyline(game['team_1_odds'][bookies_list[i]])
					decimal_2 = 1/odds_from_moneyline(game['team_2_odds'][bookies_list[j]])
					arb_decimal = decimal_1 + decimal_2
					if arb_decimal < 1:
						arbitrage_opportunity = {
							'current_date': str(localtime()[1]) + '/' + str(localtime()[2])  + '/' + str(localtime()[0]),
							'current_time': str(localtime()[3]) + ':' + str(localtime()[4])  + ':' + str(localtime()[5]),
							'current_timezone': str(datetime.datetime.now().astimezone().tzinfo),
							'game_date': game['game_date'],
							'game_time': game['game_time'],
							'profit_percent': 1 / arb_decimal,
							'bookie_1': bookies_list[i],
							'decimal_1': decimal_1,
							'moneyline_1': game['team_1_odds'][bookies_list[i]],
							'stake_1_percent': decimal_1 / arb_decimal,
							'team_1': game['team_1'],
							'bookie_2': bookies_list[j],
							'decimal_2': decimal_2,
							'moneyline_2': game['team_2_odds'][bookies_list[j]],
							'stake_2_percent': decimal_2 / arb_decimal,
							'team_2': game['team_2'],
							'league_name': 'nba',
						}
						arbitrage_opportunity_list.append(arbitrage_opportunity)


	if len(arbitrage_opportunity_list) > 0:
		for arb in arbitrage_opportunity_list:
			exists = ArbitrageOpportunity.query.filter_by(
				game_date=arb['game_date'],
				team_1_id=arb['team_1_id'],
				team_2_id=arb['team_2_id'],
				bookie_1_id=arb['bookie_1_id'],
				bookie_2_id=arb['bookie_2_id'],
				league_id=arb['league_id']
			).first()

			if not exists:
				league = League.query.filter_by(name=arb['league_name']).first()
				if not league:
					league = League(name=arb['league_name'])
					db.session.add(league)

				bookie_1 = Bookie.query.filter_by(name=arb['bookie_1']).first()
				if not bookie_1:
					bookie_1 = Bookie(name=arb['bookie_1'])
					db.session.add(bookie_1)

				bookie_2 = Bookie.query.filter_by(name=arb['bookie_2']).first()
				if not bookie_2:
					bookie_2 = Bookie(name=arb['bookie_2'])
					db.session.add(bookie_2)

				team_1 = Team.query.filter_by(name=NBA_TEAMS[arb['team_1']]).first()
				if not team_1:
					team_1 = Team(
						league_id=league.id,
						league_name=arb['league_name'],
						name=NBA_TEAMS[arb['team_1']],
						city=arb['team_1']
					)
					db.session.add(team_1)

				team_2 = Team.query.filter_by(name=NBA_TEAMS[arb['team_2']]).first()
				if not team_2:
					team_2 = Team(
						league_id=league.id,
						league_name=arb['league_name'],
						name=NBA_TEAMS[arb['team_2']],
						city=arb['team_1']
					)
					db.session.add(team_2)

				db.session.flush()

				opportunity = ArbitrageOpportunity(
					bookie_1_id=bookie_1.id,
					bookie_2=bookie_2.id,
					team_1_id=team_1.id,
					team_2_id=team_2.id,
					league_id=league.id,
					moneyline_1=arb['moneyline_1'],
					moneyline_2=arb['moneyline_2'],
					decimal_1=arb['decimal_1'],
					decimal_2=arb['decimal_2'],
					stake_1_percent=arb['stake_1_percent'],
					stake_2_percent=arb['stake_2_percent'],
					profit_percent=arb['profit_percent'],
					date=arb['current_date'],
					time=arb['current_time'],
					timezone=arb['current_timezone'],
					game_date=arb['game_date'],
					game_time=arb['game_time'],
				)
				db.session.add(opportunity)
		db.session.commit()

		# Return any arbitrage opportunities as a jsonified list. If there are no opportunities then we notifiy the user of this.
		return make_response(jsonify(arbitrage_opportunity_list), 200)
	else:
		return make_response(jsonify(game_dict_list), 200)

# @app.get('/arbitrage_opportunities')
# def get_arbitrage_opportunities():
# 	pass

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