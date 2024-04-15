from app import app
from helpers import NBA_TEAMS, NHL_TEAMS, MLB_TEAMS, clean_ncaab_team_name, get_sport_data, calculate_avg_profit, calculate_variance
from models import db, ArbitrageOpportunity, Bookie, League, Team

if __name__ == '__main__':
	with app.app_context():
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

		teams = Team.query.all()
		for team in teams:
			team_arbs_1 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.team_1_id == team.id)
			team_arbs_2 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.team_2_id == team.id)
			team_arbs = [*team_arbs_1, *team_arbs_2]
			if team_arbs:
				team.avg_profit_percent = calculate_avg_profit(team_arbs)
				team.var_profit_percent = calculate_variance(team_arbs)

		bookies = Bookie.query.all()
		for bookie in bookies:
			bookie_arbs_1 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.bookie_1_id == bookie.id)
			bookie_arbs_2 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.bookie_2_id == bookie.id)
			bookie_arbs = [*bookie_arbs_1, *bookie_arbs_2]
			if bookie_arbs:
				bookie.avg_profit_percent = calculate_avg_profit(bookie_arbs)
				bookie.var_profit_percent = calculate_variance(bookie_arbs)

		leagues = League.query.all()
		for league in leagues:
			league_arbs = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.league_id == league.id)
			if league_arbs:
				league.avg_profit_percent = calculate_avg_profit(league_arbs)
				league.var_profit_percent = calculate_variance(league_arbs)

		db.session.commit()
