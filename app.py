from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_debugtoolbar import DebugToolbarExtension
import datetime

# Init app
app = Flask(__name__)
# app.config['SQLALCHEMY_ECHO'] = True
app.debug = True
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# toolbar = DebugToolbarExtension(app)

# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)


# Models
# PlayerModel
class Players(db.Model):
    __tablename__ = 'players'
    __table_args__ = {'schema': 'licenta'}

    id = db.Column(db.BigInteger,
                   db.Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False,
                               cache=1), primary_key=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    shirt_number = db.Column(db.BigInteger, nullable=False)
    position = db.Column(db.Text, nullable=False)
    age = db.Column(db.BigInteger, nullable=False)
    team = db.Column(db.ForeignKey('licenta.teams.name'), nullable=False)

    teams = db.relationship('Teams', back_populates='players')

    def __init__(self, first_name, last_name, shirt_number, position, age, team):
        self.first_name = first_name
        self.last_name = last_name
        self.shirt_number = shirt_number
        self.position = position
        self.age = age
        self.team = team


# TeamModel
class Teams(db.Model):
    __tablename__ = 'teams'
    __table_args__ = {'schema': 'licenta'}

    id = db.Column(db.Integer,
                   db.Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=True, cache=1),
                   primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    country = db.Column(db.Text, nullable=False)
    city = db.Column(db.Text, nullable=False)
    points = db.Column(db.BigInteger)

    players = db.relationship('Players', back_populates='teams')

    def __init__(self, name, country, city, points):
        self.name = name
        self.country = country
        self.city = city
        self.points = points


# Schemas
# Player Schema
class PlayerSchema(ma.Schema):
    class Meta:
        fields = ('first_name', 'last_name', 'shirt_number', 'position', 'age', 'team')


# Init player schema
player_schema = PlayerSchema()
players_schema = PlayerSchema(many=True)


# Team Schema
class TeamSchema(ma.Schema):
    class Meta:
        fields = ('name', 'country', 'city', 'points')


# Init team schema
team_schema = TeamSchema()
teams_schema = TeamSchema(many=True)


# Routes
# 1. Insert team
@app.route('/insert-team', methods=['POST'])
def add_team():
    name = request.json['name']
    country = request.json['country']
    city = request.json['city']
    points = request.json['points']

    new_team = Teams(name, country, city, points)

    t1 = datetime.datetime.now()
    db.session.add(new_team)
    t2 = datetime.datetime.now()
    print(((t2 - t1).total_seconds()) * 1000)
    db.session.commit()

    return team_schema.jsonify(new_team)


# 2. Update a team
@app.route('/update-team', methods=['PUT'])
def update_team():
    name = request.json['name']
    points = request.json['points']

    t1 = datetime.datetime.now()
    teams = Teams.query.filter(Teams.name == name).all()
    team = teams[0]
    team.points = points
    t2 = datetime.datetime.now()
    print(((t2 - t1).total_seconds()) * 1000)
    db.session.commit()

    return team_schema.jsonify(team)


# 3. Delete players by position and age
@app.route('/delete-player/<position>/<age>', methods=['DELETE'])
def delete_player(position, age):
    t1 = datetime.datetime.now()
    stmt = Players.__table__.delete().where(Players.position == position).where(Players.age > age)
    db.session.execute(stmt)
    t2 = datetime.datetime.now()
    print(((t2 - t1).total_seconds()) * 1000)
    db.session.commit()

    return jsonify("Deleted")


# 4. Get player and team by position
@app.route('/player-by-position/<position>', methods=['GET'])
def get_players_and_team_by_position(position):
    t1 = datetime.datetime.now()
    all_players = Players.query.join(Teams, Players.team == Teams.name).filter(Players.position == position).filter(
        Players.team.match("%United")).all()
    t2 = datetime.datetime.now()
    print(((t2 - t1).total_seconds()) * 1000)
    result = players_schema.dump(all_players)

    return jsonify(result)


# 5. Get all players
@app.route('/players', methods=['GET'])
def get_players():
    t1 = datetime.datetime.now()
    all_players = Players.query.order_by(Players.id.asc())
    result = players_schema.dump(all_players)
    t2 = datetime.datetime.now()
    print(((t2 - t1).total_seconds()) * 1000)

    return jsonify(result)


# 6. Get team by points
@app.route('/teams/<points>', methods=['GET'])
def get_teams_by_points(points):
    t1 = datetime.datetime.now()
    all_teams = Teams.query.filter(Teams.points > points).all()
    t2 = datetime.datetime.now()
    print(((t2 - t1).total_seconds()) * 1000)
    result = teams_schema.dump(all_teams)

    return jsonify(result)


# Run server
if __name__ == '__main__':
    app.run(debug=True)
