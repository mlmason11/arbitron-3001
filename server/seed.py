import logging
from helpers import NBA_TEAMS, NHL_TEAMS, MLB_TEAMS, clean_ncaab_team_name, get_sport_data, calculate_avg_profit, calculate_variance
from models import db, ArbitrageOpportunity, Bookkeeper, League, Team

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    """Function to seed the database with the latest sports data and update profit/variance metrics."""
    try:
        logger.info("Fetching NBA data...")
        get_sport_data(
            'https://www.sportsbookreview.com/betting-odds/nba-basketball/money-line/full-game/',
            lambda obj: obj.contents[0].get_text(),
            'nba',
            NBA_TEAMS
        )

        logger.info("Fetching NHL data...")
        get_sport_data(
            'https://www.sportsbookreview.com/betting-odds/nhl-hockey/',
            lambda obj: obj.contents[1].contents[0].get_text(),
            'nhl',
            NHL_TEAMS
        )

        logger.info("Fetching NCAAB data...")
        get_sport_data(
            'https://www.sportsbookreview.com/betting-odds/ncaa-basketball/money-line/full-game/',
            lambda obj: clean_ncaab_team_name(obj.contents[1].contents[0].get_text()),
            'ncaab'
        )

        logger.info("Fetching MLB data...")
        get_sport_data(
            'https://www.sportsbookreview.com/betting-odds/mlb-baseball/',
            lambda obj: obj.contents[1].contents[0].get_text(),
            'mlb',
            MLB_TEAMS
        )

        logger.info("Updating teams' profit and variance...")
        teams = Team.query.all()
        for team in teams:
            team_arbs_1 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.team_1_id == team.id)
            team_arbs_2 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.team_2_id == team.id)
            team_arbs = [*team_arbs_1, *team_arbs_2]
            if team_arbs:
                team.avg_profit_percent = calculate_avg_profit(team_arbs)
                team.var_profit_percent = calculate_variance(team_arbs)

        logger.info("Updating bookkeepers' profit and variance...")
        bookkeepers = Bookkeeper.query.all()
        for bookkeeper in bookkeepers:
            bookkeeper_arbs_1 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.Bookkeeper_1_id == bookkeeper.id)
            bookkeeper_arbs_2 = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.Bookkeeper_2_id == bookkeeper.id)
            bookkeeper_arbs = [*bookkeeper_arbs_1, *bookkeeper_arbs_2]
            if bookkeeper_arbs:
                bookkeeper.avg_profit_percent = calculate_avg_profit(bookkeeper_arbs)
                bookkeeper.var_profit_percent = calculate_variance(bookkeeper_arbs)

        logger.info("Updating leagues' profit and variance...")
        leagues = League.query.all()
        for league in leagues:
            league_arbs = ArbitrageOpportunity.query.filter(ArbitrageOpportunity.league_id == league.id).all()
            if league_arbs:
                league.avg_profit_percent = calculate_avg_profit(league_arbs)
                league.var_profit_percent = calculate_variance(league_arbs)

        db.session.commit()
        logger.info("Database seeding and updates completed successfully.")

    except Exception as e:
        logger.error(f"Error seeding the database: {e}")
        db.session.rollback()  # Rollback in case of error
