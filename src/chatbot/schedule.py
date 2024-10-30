"""Handles code to schedule events for the chatbot."""

import atexit
import random

from apscheduler.schedulers.background import BackgroundScheduler

import database as db

from .events import generate_event
from .model import Model
from .posts import generate_social_media_post


def schedule_events(model: Model) -> None:
    """Schedule events for the chatbot."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        _scheduled_generation,
        trigger="interval",
        minutes=1,
        args=[model],
    )
    scheduler.start()
    atexit.register(scheduler.shutdown)


def _scheduled_generation(model: Model) -> None:
    """
    Called once a minute and uses internal logic decide what to generate.
    """
    char_ids = db.select_character_ids()
    for char_id in char_ids:
        if random.random() < 1 / 30:
            # Thoughts happen twice an hour on average
            generate_event(model, char_id, "thought")
        if random.random() < 1 / 30:
            # Events happen twice an hour on average
            generate_event(model, char_id, "event")
        if random.random() < 1 / 60:
            # Posts happen once an hour on average
            generate_social_media_post(model, char_id)
