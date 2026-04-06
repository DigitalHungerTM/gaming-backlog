import json
import time

from flask import Blueprint, render_template, request, redirect, url_for, flash, app
from flask_wtf import FlaskForm
from sqlalchemy import select, func, delete, update
from sqlalchemy.orm import load_only
from wtforms import StringField, SelectField, DecimalField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import Length, Optional, NumberRange, InputRequired

from backlog_app import apicalypse
from backlog_app.db import db, Game, Launcher, Status, Proton
from backlog_app.igdb import igdb, cover_url_builder

bp = Blueprint('backlog', __name__)


class AddGameForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(max=255)])
    # the launcher, status and proton field choices will have to be defined after instantiation
    launcher_id = SelectField('Launcher', coerce=int, validators=[InputRequired()])
    status_id = SelectField('Status', coerce=int, validators=[InputRequired()])
    proton_id = SelectField('ProtonDB Rating', coerce=int, validators=[InputRequired()])
    rating = DecimalField('Rating', places=1, validators=[Optional(), NumberRange(min=0, max=5)],
                          render_kw={"step": "0.5"})
    man = BooleanField('Man...')
    review = TextAreaField('Review', validators=[Length(max=3000)])
    submit = SubmitField('Save')


class UpdateGameForm(AddGameForm):
    cancel = SubmitField('Cancel', render_kw={"formnovalidate": "true", "class": "btn btn-secondary"})


@bp.route('/')
def index():
    games = db.session.scalars(select(Game))
    playing_games = db.session.scalars(select(Game).join(Status).where(Status.name == 'playing').order_by(Game.title))
    return render_template('backlog/index.html', games=games, playing_games=playing_games)


@bp.route('/add', methods=('GET', 'POST'))
def add():
    # todo: revamp this route to use IGDB as source of truth, store cover image ID in database with game for less requests on game lookup
    add_game_form = AddGameForm()
    add_game_form.launcher_id.choices = [(l.id, l.name) for l in
                                         db.session.scalars(select(Launcher).order_by(Launcher.id))]
    add_game_form.status_id.choices = [(s.id, s.name) for s in db.session.scalars(select(Status).order_by(Status.id))]
    add_game_form.proton_id.choices = [(p.id, p.rating) for p in db.session.scalars(select(Proton).order_by(Proton.id))]

    if add_game_form.validate_on_submit():
        new_game = Game()
        add_game_form.populate_obj(new_game)

        if new_game.status_id == 6:  # status id for 'want to play'
            max_queue_order = db.session.execute(select(func.max(Game.queue_order))).scalar()
            new_game.queue_order = max_queue_order + 1 if max_queue_order else 1

        db.session.add(new_game)
        db.session.commit()
        return redirect(url_for('backlog.detail', id=new_game.id))

    return render_template('backlog/add.html', form=add_game_form)


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update_game(id):
    game = db.get_or_404(Game, id)
    want_to_play = game.status.id == 6  # status id for 'want to play'

    update_game_form = UpdateGameForm(obj=game)
    update_game_form.launcher_id.choices = [(l.id, l.name) for l in db.session.scalars(
        select(Launcher).options(load_only(Launcher.id, Launcher.name)).order_by(Launcher.id))]
    update_game_form.status_id.choices = [(s.id, s.name) for s in db.session.scalars(
        select(Status).options(load_only(Status.id, Status.name)).order_by(Status.id))]
    update_game_form.proton_id.choices = [(p.id, p.rating) for p in db.session.scalars(
        select(Proton).options(load_only(Proton.id, Proton.rating)).order_by(Proton.id))]

    if request.method == 'POST' and update_game_form.cancel.data:
        return redirect(url_for('backlog.detail', id=game.id))

    if update_game_form.validate_on_submit():
        update_game_form.populate_obj(game)

        if not want_to_play and game.status_id == 6:  # was not want to play and now is
            max_queue_order = db.session.scalar(select(func.max(Game.queue_order)))
            game.queue_order = max_queue_order + 1 if max_queue_order else 1

        elif want_to_play and not game.status_id == 6:  # was want to play and now is not
            # for some reason the DBAPI can't handle things when queue order has a unique constraint so I removed it.
            game.queue_order = None
            games_in_queue = db.session.scalars(select(Game).where(Game.status_id == 6).order_by(Game.queue_order))
            updates = [
                {'id': game.id, 'queue_order': i + 1}
                for i, game in enumerate(games_in_queue)
            ]
            db.session.execute(update(Game), updates)

        db.session.commit()
        return redirect(url_for('backlog.detail', id=game.id))

    print(update_game_form)
    return render_template('backlog/update.html', game=game, form=update_game_form)


@bp.route('/<int:id>/delete', methods=('POST',))
def delete_game(id):
    db.session.execute(delete(Game).where(Game.id == id))
    db.session.commit()
    return redirect(url_for('index'))


@bp.route('/<int:id>/detail')
def detail(id):
    # TODO: fix scaling with different viewports
    game = db.get_or_404(Game, id)
    cover_url = None
    if game.igdb_image_id is not None:
        cover_url = cover_url_builder(game.igdb_image_id)
    return render_template('backlog/game.html', game=game, cover_url=cover_url)


@bp.route('/random')
def random():
    random_game_choice = db.session.scalar(
        select(Game)
        .join(Game.status)
        .where(Status.name == 'not started')
        .options(load_only(Game.id))
        .order_by(func.random())
        .limit(1)
    )
    if random_game_choice is not None:
        return redirect(url_for('backlog.detail', id=random_game_choice.id))
    flash('There are no games to choose from.')
    return redirect(url_for('index'))


@bp.route('/queue')
def queue():
    games_in_queue = db.session.scalars(
        select(Game).join(Game.status).where(Status.name == 'want to play').order_by(Game.queue_order))
    return render_template('backlog/queue.html', games=games_in_queue)


class SearchIgdbGameForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(max=255)])
    submit = SubmitField('Search')


class SearchGameResult:
    id: int
    name: str
    cover_url: str
    year: int

    def __init__(self, id, name, first_release_date):
        self.id = id
        self.name = name
        self.year = time.localtime(first_release_date).tm_year

    def set_cover_url(self, image_id: str):
        self.cover_url = f'https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.webp'

    def __repr__(self):
        return f"SearchGameResult(id={self.id}, name={self.name}, year={self.year})"


class CoverSearchResult:
    image_id: str
    game_id: int

    def __init__(self, id, image_id, game):
        self.image_id = image_id
        self.game_id = game


@bp.route('/igdb', methods=('GET', 'POST'))
def igdb_games():
    form = SearchIgdbGameForm()

    if form.validate_on_submit():
        assert form.title.data is not None
        query = apicalypse.QueryBuilder().search(form.title.data).fields(['id', 'name', 'first_release_date']).limit(
            8).where('parent_game = null')
        data = igdb.api_request('/games', query.build())
        games = json.loads(data.text, object_hook=lambda d: SearchGameResult(**d))

        game_ids = ','.join([str(game.id) for game in games])
        data = igdb.api_request('/covers', apicalypse.QueryBuilder().fields(['game', 'image_id']).where(
            f'game = ({game_ids})').build())
        covers = json.loads(data.text, object_hook=lambda d: CoverSearchResult(**d))

        # stupid solution but it should work for now
        for game in games:
            for cover in covers:
                if game.id == cover.game_id:
                    game.set_cover_url(cover.image_id)

        return render_template('igdb/search_game.html', form=form, games=games)

    return render_template('igdb/search_game.html', form=form)


@bp.route('/update_image_id')
def update_image_id():
    # TODO: make this into a custom flask command using click
    """
    Useful for bulk updating image id's for games that have them missing.
    Note that not all rows might get updated, so running multiple times might be required.
    """
    games = db.session.query(Game).where(Game.igdb_id != None).where(Game.igdb_image_id == None).all()
    games_dict = {g.igdb_id: g for g in games}
    igdb_ids = list(map(str, games_dict.keys()))
    page_size = 1
    covers_dict = {}
    for i in range(0, len(igdb_ids), page_size):
        offset = i
        query = apicalypse.QueryBuilder().fields(['game', 'image_id']).where(f'game = ({','.join(igdb_ids)})').offset(
            offset).limit(page_size)
        covers = igdb.api_request('/covers', query.build()).json()
        for cover in covers:
            covers_dict[cover['game']] = cover['image_id']

    print(covers_dict)

    for game in games:
        game.igdb_image_id = covers_dict.get(game.igdb_id)

    db.session.commit()

    flash('Updated all games with IGDB ID')
    return redirect(url_for('index'))
