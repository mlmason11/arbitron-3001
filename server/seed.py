from helpers import NBA_TEAMS, NHL_TEAMS, MLB_TEAMS, clean_ncaab_team_name, get_sport_data

if __name__ == '__main__':
	get_sport_data('https://www.sportsbookreview.com/betting-odds/nba-basketball/money-line/full-game/',
					lambda obj: obj.contents[0].get_text(),
					'nba',
					NBA_TEAMS)

	get_sport_data('https://www.sportsbookreview.com/betting-odds/nhl-hockey/',
					lambda obj: obj.contents[1].contents[0].get_text(),
					'nhl',
					NHL_TEAMS)

	get_sport_data('https://www.sportsbookreview.com/betting-odds/ncaa-basketball/money-line/full-game/',
					lambda obj: clean_ncaab_team_name(obj.contents[1].contents[0].get_text()),
					'ncaab')

	get_sport_data('https://www.sportsbookreview.com/betting-odds/mlb-baseball/',
					lambda obj: obj.contents[1].contents[0].get_text(),
					'mlb',
					MLB_TEAMS)