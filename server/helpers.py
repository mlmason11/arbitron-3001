import numpy as np
import re
import requests
from bs4 import BeautifulSoup as BS
from app import session, make_response, jsonify
from datetime import datetime
from time import localtime
from models import db, ArbitrageOpportunity, Team, League, Bookie, User

# Date located in <p> tag with class name OddsTable_timeText__lFfv_
# Minus odds indicate a favorite, while plus odds indicate an underdog.
# For instance, if oddsmakers heavily favor the Phoenix Suns in a game against the Indiana Pacers, the Suns might have odds of -250. In this case, you would have to wager $250 on Phoenix to win $100.
# If oddsmakers list the Pacers as +300 underdogs, you stand to win $300 with a $100 wager.
# If the moneyline is positive, it is divided by 100 and add 1. Thus, +400 moneyline = 5.0 in decimal odds. If the moneyline is negative, 100 is divided by the absolute moneyline amount (the minus signed is removed), and then 1 is added. For example, −400 moneyline is 100/400 + 1, or 1.25, in decimal odds.

# Get the first two <spans> of class GameRows_participantBox__0WCRz. Extract the text. These are the teams that are playing.
# We will be working with the following 7 <divs> of class OddsCells_numbersContainer__6V_XO
# Within each of these <divs> we want to find the two <spans> of both classes OddsCells_pointer___xLMm && OddsCells_margin__7d2oM
# The text of the second child <span> (after the <span> of class OddsCells_adjust__hGhKV) of each of these parent <spans> will contain our odds. Extract this information.
# The first number we extract will correspond to the first team we extracted earler, and the second number we extract will correspond to the second team. Organize the data as such.
# Repeat this for each of the following 6 <divs> of class OddsCells_numbersContainer__6V_XO
# Then, repeat the entire process for the rest of the <spans> of class GameRows_participantBox__0WCRz, two at a time. It is very important that we work with the <spans> of class GameRows_participantBox__0WCRz two at a time to ensure there is no jumbling of teams and games.

# Matches all NBA team names to their cities
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
	"L.A. Clippers": "Clippers",
	"L.A. Lakers": "Lakers",
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

NHL_TEAMS = {
    'ANA': 'Ducks',
    'ARI': 'Coyotes',
    'BOS': 'Bruins',
    'BUF': 'Sabres',
    'CAL': 'Flames',
    'CAR': 'Hurricanes',
    'CHI': 'Blackhawks',
    'COL': 'Avalanche',
    'CLB': 'Blue Jackets',
    'DAL': 'Stars',
    'DET': 'Red Wings',
    'EDM': 'Oilers',
    'FLA': 'Panthers',
    'LA': 'Kings',
    'MIN': 'Wild',
    'MON': 'Canadiens',
    'NAS': 'Predators',
    'NJ': 'Devils',
    'NYR': 'Rangers',
    'NYI': 'Islanders',
    'OTT': 'Senators',
    'PHI': 'Flyers',
    'PIT': 'Penguins',
    'SJ': 'Sharks',
    'SEA': 'Kraken',
    'STL': 'Blues',
    'TB': 'Lightning',
    'TOR': 'Maple Leafs',
    'VAN': 'Canucks',
    'VEG': 'Golden Knights',
    'WAS': 'Capitals',
    'WIN': 'Jets'
}

MLB_TEAMS = {
    'ATL': 'Braves',
    'ARI': 'Diamondbacks',
    'BAL': 'Orioles',
    'BOS': 'Red Sox',
    'CHC': 'Cubs',
    'CHW': 'White Sox',
    'CIN': 'Reds',
    'CLE': 'Guardians',
    'COL': 'Rockies',
    'DET': 'Tigers',
    'HOU': 'Astros',
    'KC': 'Royals',
    'LAA': 'Angels',
    'LAD': 'Dodgers',
    'MIA': 'Marlins',
    'MIL': 'Brewers',
    'MIN': 'Twins',
    'NYM': 'Mets',
    'NYY': 'Yankees',
    'OAK': 'Athletics',
    'PHI': 'Phillies',
    'PIT': 'Pirates',
    'SD': 'Padres',
    'SF': 'Giants',
    'SEA': 'Mariners',
    'STL': 'Cardinals',
    'TB': 'Rays',
    'TEX': 'Rangers',
    'TOR': 'Blue Jays',
    'WAS': 'Nationals'
}

def logged_in_user():
    return User.query.filter(User.id == session.get('user_id')).first()

def authorize():
    if not logged_in_user():
        return {'message': "No logged in user"}, 401

def clean_ncaab_team_name(s):
    # Pattern explanation:
    # ^\(\d+\)\s* matches a string that starts with an opening parenthesis,
    # followed by one or more digits (\d+),
    # followed by a closing parenthesis,
    # and optionally followed by whitespace characters (\s*).
    return re.sub(r'^\(\d+\)\s*', '', s)

# Calculates the odds in whole number + decimal form from the +/- moneyline form odds
# Takes in a string, returns a float
def odds_from_moneyline(moneyline):
	if len(moneyline) > 1 and int(moneyline[1:]):
		if moneyline[0] == '+':
			return (int(moneyline[1:]) / 100) + 1
		elif moneyline[0] == '-':
			return (100 / int(moneyline[1:])) + 1
		else:
			return '-'
	else:
		return '-'

# Efficiently organize all information about each game in a list of dictionaries
def create_games_dict_list(game_times_list, date, teams_list, bookies_list, odds_numbers_list):
	game_dict_list = []
	num_bookies = len(bookies_list)
	for i in range(0, len(game_times_list)):
		game_dict = {
			'game_date': date[:-1] if not type(date[-1]) == int else date,
			'game_time': game_times_list[i],
			'team_1': teams_list[2 * i],
			'team_1_odds': {bookies_list[j]:odds_numbers_list[2 * (num_bookies * i + j)] for j in range(0, num_bookies)},
			'team_2': teams_list[2 * i + 1],
			'team_2_odds': {bookies_list[j]:odds_numbers_list[2 * (num_bookies * i + j) + 1] for j in range(0, num_bookies)}
		}
		game_dict_list.append(game_dict)
	return game_dict_list

# For each game in the dictionary we test for arbitrage opportunities using all the bookies for each team
def create_arbitrage_opportunities_list(game_dict_list, bookies_list, league_name):
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
							'current_timezone': str(datetime.now().astimezone().tzinfo),
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
							'league_name': league_name
						}
						arbitrage_opportunity_list.append(arbitrage_opportunity)
	return arbitrage_opportunity_list

def calculate_avg_profit(opportunities):
    # Calculate average profit percent
    profits = np.array([opportunity.profit_percent for opportunity in opportunities])
    return np.mean(profits)

def calculate_variance(opportunities):
    # Calculate variance for a given list of opportunities and average profit percent
    profits = np.array([opportunity.profit_percent for opportunity in opportunities])
    return np.var(profits)

def update_avg_profit_and_variance(league, team_1, team_2, bookie_1, bookie_2):
    # Calculate and update average profit percent for league, team_1, team_2, bookie_1, bookie_2
	league.avg_profit_percent = calculate_avg_profit(league.aos)
	league.var_profit_percent = calculate_variance(league.aos)

	team_1.avg_profit_percent = calculate_avg_profit(team_1.aos)
	team_1.var_profit_percent = calculate_variance(team_1.aos)

	team_2.avg_profit_percent = calculate_avg_profit(team_2.aos)
	team_2.var_profit_percent = calculate_variance(team_2.aos)

	bookie_1.avg_profit_percent = calculate_avg_profit(bookie_1.aos)
	bookie_1.var_profit_percent = calculate_variance(bookie_2)

	bookie_2.avg_profit_percent = calculate_avg_profit(bookie_2.aos)
	bookie_2.var_profit_percent = calculate_variance(bookie_2.aos)

# Automates the addition of any arbitrage opportunities to our database
def add_arbitrages(arb_list, team_names_dict):
	if len(arb_list) > 0:
		for arb in arb_list:
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

			team_1 = Team.query.filter_by(name=(arb['team_1'] if arb['league_name'] == 'ncaab' else team_names_dict[arb['team_1']])).first()
			if not team_1:
				team_1 = Team(
					league_id=league.id,
					league_name=arb['league_name'],
					name=arb['team_1'] if arb['league_name'] == 'ncaab' else team_names_dict[arb['team_1']],
					city=arb['team_1']
				)
				db.session.add(team_1)

			team_2 = Team.query.filter_by(name=(arb['team_2'] if arb['league_name'] == 'ncaab' else team_names_dict[arb['team_2']])).first()
			if not team_2:
				team_2 = Team(
					league_id=league.id,
					league_name=arb['league_name'],
					name=arb['team_2'] if arb['league_name'] == 'ncaab' else team_names_dict[arb['team_2']],
					city=arb['team_2']
				)
				db.session.add(team_2)

			db.session.flush()

			exists = ArbitrageOpportunity.query.filter_by(
				game_date=arb['game_date'],
				moneyline_1=arb['moneyline_1'],
				moneyline_2=arb['moneyline_2'],
				team_1_id=team_1.id,
				team_2_id=team_2.id,
				bookie_1_id=bookie_1.id,
				bookie_2_id=bookie_2.id,
				league_id=league.id
			).first()

			if not exists:
				opportunity = ArbitrageOpportunity(
					bookie_1_id=bookie_1.id,
					bookie_2_id=bookie_2.id,
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

		update_avg_profit_and_variance(league, team_1, team_2, bookie_1, bookie_2)
		db.session.commit()

# def get_sport_data(url, teams_selector, league_name, team_names_dict={}):
#     # Retrieve information from the website and make the BeautifulSoup object, our "soup"
#     data = requests.get(url)
#     soup = BS(data.text, 'html.parser')

#     # We get the specific information from the selected html elements in the BeautifulSoup object
#     date = soup.find('p', class_='OddsTable_timeText__lFfv_').get_text()
#     game_times_list = [obj.contents[0].get_text() for obj in soup.find_all('div', class_='GameRows_timeContainer__27ifL')]
#     teams_list = [teams_selector(obj) for obj in soup.find_all('div', class_='GameRows_participantContainer__6Rpfq')]
#     odds_numbers_list = [obj.contents[1].get_text() for obj in soup.find_all('span', class_='OddsCells_pointer___xLMm')]
#     bookies_list = [obj.contents[0].attrs['href'].split('/')[-1].split('_')[0] for obj in soup.find_all('div', class_='Sportsbooks_sportbook__FqMkt')]

#     game_dict_list = create_games_dict_list(game_times_list, date, teams_list, bookies_list, odds_numbers_list)
#     arbitrage_opportunity_list = create_arbitrage_opportunities_list(game_dict_list, bookies_list, league_name=league_name)
#     add_arbitrages(arb_list=arbitrage_opportunity_list, team_names_dict=team_names_dict)

#     # Return any arbitrage opportunities as a jsonified list. If there are no opportunities then we notify the user of this.
#     if len(arbitrage_opportunity_list) > 0:
#         return make_response(jsonify(arbitrage_opportunity_list), 200)
#     else:
#         return make_response(jsonify({'error': f'no arbitrage betting opportunities available for {league_name.upper()} at this time'}))