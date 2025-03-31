import logging
import tomllib
from typing import BinaryIO

import click
import pydantic

from trktor.models.ConfigDataModel import ConfigDataModel

log = logging.getLogger(__name__)


@click.command("run", short_help="Runs the bot")
@click.argument("config", envvar="TRKTOR_CONFIG", type=click.File("rb"))
def run_bot(config: BinaryIO) -> ConfigDataModel:
    data = tomllib.load(config)
    try:
        config = ConfigDataModel.model_validate(data)
    except pydantic.ValidationError as e:
        log.error(f"Failed to parse the configuration file: {e}")
    return config
