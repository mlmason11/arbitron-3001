import requests

from bs4 import BeautifulSoup as BS
from datetime import datetime
from flask import jsonify, request, session, make_response
from time import localtime

def get_nba():
	BUDGET = 1000.00

	# Calculates the whole number decimal odds from the +/- moneyline odds
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

	# Retrieve information from the website and make the BeautifulSoup object, our "soup"
	data = requests.get('https://www.oddstrader.com/nba/?g=game&m=money')
	soup = BS(data.text, 'html.parser')

	# We get the specific information from the selected html elements in the BeautifulSoup object
	date = soup.find('span', class_='_6a2e80e4').get_text()
	game_times_list = [obj.contents.contents[2].get_text() for obj in soup.find_all('div', class_='eventStatus')]
	teams_list = [obj.get_text() for obj in soup.find_all('span', class_='teamName blueHover')]
	odds_numbers_list = [obj.contents.get_text() for obj in soup.find_all('button', class_='buttons__Plain-sc-rlvloz-0 Oddstyles__Button-sc-1czxac9-1 lnKGbX dVXwRa')]
	bookies_list = [obj.contents.attrs['href'].split('/')[-2] for obj in soup.find_all('div', class_='_4128fd60 _908f0bbc')]

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
				if not i == j:
					decimal_1 = 1/odds_from_moneyline(game['team_1_odds'][bookies_list[i]])
					decimal_2 = 1/odds_from_moneyline(game['team_2_odds'][bookies_list[j]])
					arb_decimal = decimal_1 + decimal_2
					if arb_decimal < 1:
						arbitrage_opportunity = {
							'budget': BUDGET,
							'after': BUDGET + round(BUDGET / arb_decimal - BUDGET, 2),
							'current_date': str(localtime()[1]) + '/' + str(localtime()[2])  + '/' + str(localtime()[0]),
							'current_time': str(localtime()[3]) + ':' + str(localtime()[4])  + ':' + str(localtime()[5]),
							'current_timezone': str(datetime.now().astimezone().tzinfo),
							'game_date': game['game_date'],
							'game_time': game['game_time'],
							'profit': round(BUDGET / arb_decimal - BUDGET, 2),
							'bookie_1': bookies_list[i],
							'moneyline_1': game['team_1_odds'][bookies_list[i]],
							'stake_1': round((BUDGET * decimal_1) / arb_decimal, 2),
							'team_1': game['team_1'],
							'bookie_2': bookies_list[j],
							'moneyline_2': game['team_2_odds'][bookies_list[j]],
							'stake_2': round((BUDGET * decimal_2) / arb_decimal, 2),
							'team_2': game['team_2']
						}
						arbitrage_opportunity_list.append(arbitrage_opportunity)

	# Return any arbitrage opportunities as a jsonified list
	return make_response(jsonify(arbitrage_opportunity_list), 200)

def nba():
	BUDGET = 1000.00

	# Calculates the whole number decimal odds from the +/- moneyline odds
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
				if not i == j:
					decimal_1 = 1/odds_from_moneyline(game['team_1_odds'][bookies_list[i]])
					decimal_2 = 1/odds_from_moneyline(game['team_2_odds'][bookies_list[j]])
					arb_decimal = decimal_1 + decimal_2
					if arb_decimal < 1:
						arbitrage_opportunity = {
							'budget': BUDGET,
							'after': BUDGET + round(BUDGET / arb_decimal - BUDGET, 2),
							'current_date': str(localtime()[1]) + '/' + str(localtime()[2])  + '/' + str(localtime()[0]),
							'current_time': str(localtime()[3]) + ':' + str(localtime()[4])  + ':' + str(localtime()[5]),
							'current_timezone': str(datetime.datetime.now().astimezone().tzinfo),
							'game_date': game['game_date'],
							'game_time': game['game_time'],
							'profit': round(BUDGET / arb_decimal - BUDGET, 2),
							'bookie_1': bookies_list[i],
							'moneyline_1': game['team_1_odds'][bookies_list[i]],
							'stake_1': round((BUDGET * decimal_1) / arb_decimal, 2),
							'team_1': game['team_1'],
							'bookie_2': bookies_list[j],
							'moneyline_2': game['team_2_odds'][bookies_list[j]],
							'stake_2': round((BUDGET * decimal_2) / arb_decimal, 2),
							'team_2': game['team_2']
						}
						arbitrage_opportunity_list.append(arbitrage_opportunity)

	# Return any arbitrage opportunities as a jsonified list
	return make_response(jsonify(arbitrage_opportunity_list), 200)