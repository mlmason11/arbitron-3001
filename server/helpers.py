import re
from datetime import datetime
from time import localtime
from models import db, ArbitrageOpportunity, Team, League, Bookie

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

def clean_ncaab_team_name(s):
    # Pattern explanation:
    # ^\(\d+\)\s* matches a string that starts with an opening parenthesis,
    # followed by one or more digits (\d+),
    # followed by a closing parenthesis,
    # and optionally followed by whitespace characters (\s*).
    cleaned_name = re.sub(r'^\(\d+\)\s*', '', s)
    return cleaned_name

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
		db.session.commit()