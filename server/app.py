from flask import Flask, jsonify, request, session, make_response
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
from models import db, ArbitrageOpportunity, Bet, User, Team, League, Bookkeeper
from helpers import NBA_TEAMS, NHL_TEAMS, MLB_TEAMS, paginate, clean_ncaab_team_name, get_sport_data

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
CORS(app)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return '<h1>Hello World!</h1>'

# ----- BOOKKEEPER ROUTES ----- #

@app.get('/bookkeepers')
def get_all_bookkeepers():
    """Returns a list of bookkeepers with filtering and pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        profit_min = request.args.get('profit_min', 0, type=float)
        profit_max = request.args.get('profit_max', 100, type=float)
        variance_min = request.args.get('variance_min', 0, type=float)
        variance_max = request.args.get('variance_max', 100, type=float)
        sort_by = request.args.get('sort_by', 'name')

        query = Bookkeeper.query.filter(
            Bookkeeper.avg_profit_percent.between(profit_min, profit_max),
            Bookkeeper.var_profit_percent.between(variance_min, variance_max)
        )

        if sort_by == 'profit':
            query = query.order_by(Bookkeeper.avg_profit_percent.desc())
        elif sort_by == 'variance':
            query = query.order_by(Bookkeeper.var_profit_percent.desc())
        else:
            query = query.order_by(Bookkeeper.name)

        paginated_bookkeepers = paginate(query, page, per_page=10)
        bookkeepers = [bk.to_dict() for bk in paginated_bookkeepers.items]

        return make_response(jsonify({
            'bookkeepers': bookkeepers,
            'totalPages': paginated_bookkeepers.pages
        }), 200)
    except SQLAlchemyError as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.get('/bookkeepers/<int:id>')
def get_bookkeeper_by_id(id):
    """Returns details of a single bookkeeper by ID."""
    try:
        bookkeeper = Bookkeeper.query.get_or_404(id)
        return make_response(jsonify(bookkeeper.to_dict()), 200)
    except SQLAlchemyError as e:
        return make_response(jsonify({'error': str(e)}), 500)

# ----- TEAM ROUTES ----- #

@app.get('/teams')
def get_all_teams():
    """Returns a list of teams with filtering and pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        profit_min = request.args.get('profit_min', 0, type=float)
        profit_max = request.args.get('profit_max', 100, type=float)
        variance_min = request.args.get('variance_min', 0, type=float)
        variance_max = request.args.get('variance_max', 100, type=float)
        sort_by = request.args.get('sort_by', 'name')

        query = Team.query.filter(
            Team.avg_profit_percent.between(profit_min, profit_max),
            Team.var_profit_percent.between(variance_min, variance_max)
        )

        if sort_by == 'profit':
            query = query.order_by(Team.avg_profit_percent.desc())
        elif sort_by == 'variance':
            query = query.order_by(Team.var_profit_percent.desc())
        else:
            query = query.order_by(Team.name)

        paginated_teams = paginate(query, page, per_page=10)
        teams = [team.to_dict() for team in paginated_teams.items]

        return make_response(jsonify({
            'teams': teams,
            'totalPages': paginated_teams.pages
        }), 200)
    except SQLAlchemyError as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.get('/teams/<int:id>')
def get_team_by_id(id):
    """Returns details of a single team by ID."""
    try:
        team = Team.query.get_or_404(id)
        return make_response(jsonify(team.to_dict()), 200)
    except SQLAlchemyError as e:
        return make_response(jsonify({'error': str(e)}), 500)

# ----- LEAGUE ROUTES ----- #

@app.get('/leagues')
def get_all_leagues():
    """Returns a list of leagues with filtering and pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        profit_min = request.args.get('profit_min', 0, type=float)
        profit_max = request.args.get('profit_max', 100, type=float)
        variance_min = request.args.get('variance_min', 0, type=float)
        variance_max = request.args.get('variance_max', 100, type=float)
        sort_by = request.args.get('sort_by', 'name')

        query = League.query.filter(
            League.avg_profit_percent.between(profit_min, profit_max),
            League.var_profit_percent.between(variance_min, variance_max)
        )

        if sort_by == 'profit':
            query = query.order_by(League.avg_profit_percent.desc())
        elif sort_by == 'variance':
            query = query.order_by(League.var_profit_percent.desc())
        else:
            query = query.order_by(League.name)

        paginated_leagues = paginate(query, page, per_page=10)
        leagues = [league.to_dict() for league in paginated_leagues.items]

        return make_response(jsonify({
            'leagues': leagues,
            'totalPages': paginated_leagues.pages
        }), 200)
    except SQLAlchemyError as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.get('/leagues/<int:id>')
def get_league_by_id(id):
    """Returns details of a single league by ID."""
    try:
        league = League.query.get_or_404(id)
        return make_response(jsonify(league.to_dict()), 200)
    except SQLAlchemyError as e:
        return make_response(jsonify({'error': str(e)}), 500)

# ----- ARBITRAGE OPPORTUNITY ROUTES ----- #

@app.get('/arbitrage_opportunities')
def get_all_arbitrage_opportunities():
    """Returns a list of arbitrage opportunities."""
    try:
        arbitrage_opportunities = ArbitrageOpportunity.query.all()
        ao_list = [ao.to_dict() for ao in arbitrage_opportunities]
        return make_response(jsonify(ao_list), 200)
    except SQLAlchemyError as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.get('/arbitrage_opportunities/<int:id>')
def get_arbitrage_opportunity_by_id(id):
    """Returns details of a single arbitrage opportunity by ID."""
    try:
        arbitrage_opportunity = ArbitrageOpportunity.query.get_or_404(id)
        return make_response(jsonify(arbitrage_opportunity.to_dict()), 200)
    except SQLAlchemyError as e:
        return make_response(jsonify({'error': str(e)}), 500)

# ----- BET ROUTES ----- #

@app.get('/bets')
def get_all_bets():
    """Returns a list of all bets."""
    try:
        bets = Bet.query.all()
        bet_list = [bet.to_dict() for bet in bets]
        return make_response(jsonify(bet_list), 200)
    except SQLAlchemyError as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.get('/bets/<int:id>')
def get_bet_by_id(id):
    """Returns details of a single bet by ID."""
    try:
        bet = Bet.query.get_or_404(id)
        return make_response(jsonify(bet.to_dict()), 200)
    except SQLAlchemyError as e:
        return make_response(jsonify({'error': str(e)}), 500)

# ----- USER ROUTES ----- #

@app.post('/users')
def create_user():
    """Creates a new user."""
    try:
        data = request.json
        password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = User(
            username=data['username'],
            password=password_hash,
            email=data['email'],
            balance=data.get('balance', 0)
        )
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        return make_response(jsonify(new_user.to_dict()), 201)
    except SQLAlchemyError as e:
        return make_response(jsonify({'error': str(e)}), 406)

@app.post('/login')
def login():
    """Logs in an existing user."""
    try:
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and bcrypt.check_password_hash(user.password, data['password']):
            session['user_id'] = user.id
            return make_response(jsonify(user.to_dict()), 202)
        else:
            return make_response(jsonify({'error': "Invalid credentials"}), 401)
    except SQLAlchemyError as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.delete('/logout')
def logout():
    """Logs out the current user."""
    session.pop('user_id', None)
    return make_response(jsonify({}), 204)

@app.get('/check_session')
def check_session():
    """Checks if the user is logged in."""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        return make_response(jsonify(user.to_dict()), 200)
    return make_response(jsonify({}), 401)

## ----- NBA, NHL, NCAAB, MLB SCRAPING ROUTES ----- ##

@app.route('/nba')
def nba():
    try:
        url = 'https://www.sportsbookreview.com/betting-odds/nba-basketball/money-line/full-game/'
        game_data = get_sport_data(url, lambda obj: obj.get_text(), league_name='nba', team_names_dict=NBA_TEAMS)
        return make_response(jsonify(game_data), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/nhl')
def nhl():
    try:
        url = 'https://www.sportsbookreview.com/betting-odds/nhl-hockey/'
        game_data = get_sport_data(url, lambda obj: obj.contents[1].contents[0].get_text(), league_name='nhl', team_names_dict=NHL_TEAMS)
        return make_response(jsonify(game_data), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/ncaab')
def ncaab():
    try:
        url = 'https://www.sportsbookreview.com/betting-odds/ncaa-basketball/money-line/full-game/'
        game_data = get_sport_data(url, lambda obj: clean_ncaab_team_name(obj.contents[1].contents[0].get_text()), league_name='ncaab')
        return make_response(jsonify(game_data), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/mlb')
def mlb():
    try:
        url = 'https://www.sportsbookreview.com/betting-odds/mlb-baseball/'
        game_data = get_sport_data(url, lambda obj: obj.contents[1].contents[0].get_text(), league_name='mlb', team_names_dict=MLB_TEAMS)
        return make_response(jsonify(game_data), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
