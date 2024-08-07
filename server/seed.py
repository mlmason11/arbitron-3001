from app import app
from helpers import NBA_TEAMS, NHL_TEAMS, MLB_TEAMS, clean_ncaab_team_name, get_sport_data, calculate_avg_profit, calculate_variance
from models import db, ArbitrageOpportunity, Bookkeeper, League, Team

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

		Bookkeepers = Bookkeeper.query.all()
		for Bookkeeper in Bookkeepers:
			Bookkeeper_arbs_1 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.Bookkeeper_1_id == Bookkeeper.id)
			Bookkeeper_arbs_2 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.Bookkeeper_2_id == Bookkeeper.id)
			Bookkeeper_arbs = [*Bookkeeper_arbs_1, *Bookkeeper_arbs_2]
			if Bookkeeper_arbs:
				Bookkeeper.avg_profit_percent = calculate_avg_profit(Bookkeeper_arbs)
				Bookkeeper.var_profit_percent = calculate_variance(Bookkeeper_arbs)

		leagues = League.query.all()
		for league in leagues:
			league_arbs = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.league_id == league.id)
			if league_arbs:
				league.avg_profit_percent = calculate_avg_profit(league_arbs)
				league.var_profit_percent = calculate_variance(league_arbs)

		db.session.commit()
