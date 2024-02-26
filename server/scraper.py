import requests
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from time import sleep

from models import db, ArbitrageOpportunity


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



# def scraper():
# 	BUDGET = 100.00

# 	# def is_arbitrage(odds_1, odds_2):
# 	# 	decimal_1 = 1/odds_1
# 	# 	decimal_2 = 1/odds_2
# 	# 	arb_decimal = decimal_1 + decimal_2
# 	# 	if arb_decimal < 1:
# 	# 		return {
# 	# 			'status': 'arbitrage opportunity',
# 	# 			'profit': BUDGET / arb_decimal - BUDGET,
# 	# 			'team_1': '',
# 	# 			'bookie_1': '',
# 	# 			'stake_1': (BUDGET * decimal_1) / arb_decimal,
# 	# 			'team_2': '',
# 	# 			'bookie_2': '',
# 	# 			'stake_2': (BUDGET * decimal_2) / arb_decimal
# 	# 		}
# 	# 	else:
# 	# 		return 'no arbitrage available'

# 	def odds_from_moneyline(moneyline):
# 		if len(moneyline) > 1:
# 			if moneyline[0] == '+':
# 				return (int(moneyline[1:]) / 100) + 1
# 			elif moneyline[0] == '-':
# 				return (100/int(moneyline[1:])) + 1
# 			else:
# 				return 'moneyline cannot be zero'
# 		else:
# 			return 'odds are not available for this matchup'

# 	BOOKIES = ['fanduel', 'betmgm', 'caesars', 'draftkings', 'bet365', 'pointsbet', 'betrivers']
# 	url = 'https://www.sportsbookreview.com/betting-odds/nba-basketball/money-line/full-game/'
# 	data = requests.get(url)
# 	soup = BS(data.text, 'html.parser')

# 	date = soup.find('p.OddsTable_timeText__lFfv_').get_text()
# 	# date_parts = date.split(', ')
# 	# month_day = date_parts[1].split(' ')
# 	date_dict = {
# 		'week_day': date.split(', ')[0],
# 		'day': int(date.split(', ')[1].split(' ')[1]),
# 		'month': date.split(', ')[1].split(' ')[0],
# 		'year': date.split(', ')[2]
# 	}

# 	game_obj_list = soup.find('div', id='tbody-nba').contents

# 	# gets all needed info from a single game row
# 	# def game_info_to_dict(game):
# 	# 	teams = game.find_all('span.GameRows_participantBox__0WCRz').get_text()
# 	# 	odds_numbers = game.find_all('span.OddsCells_pointer___xLMm').contents[1].get_text()
# 	# 	return {
# 	# 		'team_1': teams[0],
# 	# 		'team_1_odds': {BOOKIES[i]:odds_from_moneyline(odds_numbers[2 * i]) for i in range(0, 6)},
# 	# 		'team_2': teams[1],
# 	# 		'team_2_odds': {BOOKIES[i]:odds_from_moneyline(odds_numbers[(2 * i) + 1]) for i in range(0, 6)}
# 	# 	}
# 	# game_dict_list = [game_info_to_dict(game) for game in game_obj_list]

# 	game_dict_list = []
# 	for game in game_obj_list:
# 		game_time = game.find('div.GameRows_timeContainer__27ifL').contents[0].get_text()
# 		teams = game.find_all('span.GameRows_participantBox__0WCRz').get_text()
# 		odds_numbers = game.find_all('span.OddsCells_pointer___xLMm').contents[1].get_text()
# 		game_dict = {
# 			'time': game_time,
# 			'team_1': teams[0],
# 			'team_1_odds': {BOOKIES[i]:odds_from_moneyline(odds_numbers[2 * i]) for i in range(0, 6)},
# 			'team_2': teams[1],
# 			'team_2_odds': {BOOKIES[i]:odds_from_moneyline(odds_numbers[(2 * i) + 1]) for i in range(0, 6)}
# 		}
# 		game_dict_list.append(game_dict)


# 	arbitrage_opportunity_list = []
# 	for game in game_dict_list:
# 		for odds_1 in game.team_1_odds:
# 			for odds_2 in game.team_2_odds:
# 				if odds_1.index() != odds_2.index():
# 					decimal_1 = 1/odds_1
# 					decimal_2 = 1/odds_2
# 					arb_decimal = decimal_1 + decimal_2
# 					if arb_decimal < 1:
# 						arbitrage_opportunity = {
# 							'profit': BUDGET / arb_decimal - BUDGET,
# 							'team_1': game.team_1,
# 							'bookie_1': BOOKIES[odds_1.index()],
# 							'stake_1': (BUDGET * decimal_1) / arb_decimal,
# 							'team_2': game.team_2,
# 							'bookie_2': BOOKIES[odds_2.index()],
# 							'stake_2': (BUDGET * decimal_2) / arb_decimal
# 						}
# 						arbitrage_opportunity_list.append(arbitrage_opportunity)


# 	#teams = soup.find_all('span.GameRows_participantBox__0WCRz').get_text()

# 	return 



# BOOKIES = ['fanduel', 'betmgm', 'caesars', 'draftkings', 'bet365', 'pointsbet', 'betrivers']
# url = 'https://www.sportsbookreview.com/betting-odds/nba-basketball/money-line/full-game/'
# data = requests.get(url)
# soup = BS(data.text, 'html.parser')

# my_data = []

# def odds_from_moneyline(moneyline):
# 	if len(moneyline) > 1:
# 		if moneyline[0] == '+':
# 			return (int(moneyline[1:]) / 100) + 1
# 		elif moneyline[0] == '-':
# 			return (100/int(moneyline[1:])) + 1
# 		else:
# 			return 'moneyline cannot be zero'
# 	else:
# 		return 'odds are not available for this matchup'

# def game_info_to_dict(game):
# 	teams = game.find_all('span.GameRows_participantBox__0WCRz').get_text()
# 	odds_numbers = game.find_all('span.OddsCells_pointer___xLMm').contents[1].get_text()
# 	return {
# 		'team_1': teams[0],
# 		'team_1_odds': {BOOKIES[i]:odds_from_moneyline(odds_numbers[2 * i]) for i in range(0, 6)},
# 		'team_2': teams[1],
# 		'team_2_odds': {BOOKIES[i]:odds_from_moneyline(odds_numbers[(2 * i) + 1]) for i in range(0, 6)}
# 	}

# def is_arbitrage(odds_1, odds_2):
# 	if (1/odds_1) + (1/odds_2) < 1:
# 		pass
# 	else:
# 		return 'no arbitrage available'

# def test_game_for_arbitrage(game):
# 	pass

# #teams = soup.find_all('span.GameRows_participantBox__0WCRz').get_text()


# date = soup.find('p.OddsTable_timeText__lFfv_').get_text()
# game_obj_list = soup.find('div', id='tbody-nba').contents
# game_dict_list = [game_info_to_dict(game) for game in game_obj_list]