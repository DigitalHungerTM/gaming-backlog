import time

import click
from flask import Blueprint

from backlog_app.db import db, Game
from igdb import apicalypse
from igdb.igdb import igdb
from igdb.proto.igdbapi_pb2 import GameResult

"""
Blueprint for adding CLI commands, registered in __init__.py with cli_group='backlog'.
Call these commands on the cli with `flask backlog <command name>`
"""

bp = Blueprint('utils', __name__, cli_group='backlog')


@bp.cli.command('update-image-ids')
def update_image_ids():
    """
    Update all IGDB image id's of games in the database where IGDB ID is not None.
    """
    print('Updating image ids for games with an IGDB ID')
    games = db.session.query(Game).where(Game.igdb_id != None).all()
    games_dict = {g.igdb_id: g for g in games}
    igdb_ids = list(map(str, games_dict.keys()))
    page_size = 500 # default limit is 10, this is the maximum limit. See https://api-docs.igdb.com/#pagination
    covers_dict = {}
    for i in range(0, len(igdb_ids), page_size):
        start = time.time()
        query = (
            apicalypse.QueryBuilder()
            .fields(['game', 'image_id'])
            .where(f'game = ({','.join(igdb_ids)})')
            .offset(i)
            .limit(page_size)
        )
        covers = igdb.api_request_plain('/covers', query.build()).json()
        for c in covers:
            covers_dict[c['game']] = c['image_id']

        end = time.time()
        if end - start < 2.5:
            time.sleep(2.5 - (end-start))

    for game in games:
        image_id = covers_dict.get(game.igdb_id)
        if image_id is None:
            print(f'No image id found for igdb game id {game.igdb_id}')
            continue
        game.igdb_image_id = image_id

    db.session.commit()
    print(f'Updated {len(covers_dict)} rows')


@bp.cli.command('test-search-game')
@click.argument('title')
def search_game(title: str):
    """
    Test the protobuf deserialization by searching for a game.
    :param title: Game title to search for.
    """
    query = (
        apicalypse.QueryBuilder()
        .fields(['name', 'cover', 'cover.image_id'])
        .search(title)
    )
    data = igdb.api_request('/games.pb', query.build())
    message = GameResult()
    message.ParseFromString(data)
    print(message.games)