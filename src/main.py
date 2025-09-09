import argparse
import itertools
import logging
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, AfterValidator, ValidationError
from typing import TypedDict, Annotated

from pydantic_core import ErrorDetails
from tap import to_tap_class


def one_plus_power_of_two(s: str, arg_name: str | None = None) -> int:
    """Validate that the input is one plus a power of two

    The power of 2 must be at least 2.

    Args:
        s: The string to validate as one plus a power of two.
        arg_name: Optional name of the argument for error messages. This is
            to use outside argparse.
    """
    err_prefix = f"error: argument {arg_name}: " if arg_name else ""
    try:
        value = int(s)
    except ValueError:
        raise ValueError(f"{err_prefix}Value must be an integer.")

    if value < 3 or (value - 1) & (value - 2) != 0:
        raise ValueError(
            f"{err_prefix}Value must be one plus a power of two (at least 3)."
        )
    return value


def zero_to_one(s: str) -> float:
    """Validate that the input is a float between 0.0 and 1.0 inclusive"""
    try:
        value = float(s)
        if value < 0.0 or value > 1.0:
            raise argparse.ArgumentTypeError(
                "Value must be between 0.0 and 1.0 inclusive."
            )
        return value
    except ValueError:
        raise argparse.ArgumentTypeError("Value must be a float.")


def int_at_least(min_value: int) -> Callable[[str], int]:
    """Return a function that validates that the input is an integer at
    least min_value"""

    def validator(s: str) -> int:
        try:
            value = int(s)
            if value < min_value:
                raise argparse.ArgumentTypeError(
                    f"Value must be at least {min_value}."
                )
            return value
        except ValueError:
            raise argparse.ArgumentTypeError("Value must be an integer.")

    return validator


# A string verified to be one of the valid logging level names
# that may be passed to logging.getLevelNameNamesMapping() to get the
# corresponding integer logging level.
LogLevel = str

ALL_LOG_LEVEL_NAMES = list(
    itertools.chain.from_iterable(
        [(k, k.casefold()) for k in logging.getLevelNamesMapping().keys()]
    )
)


def log_level(s: str) -> LogLevel:
    """Validate that the input is a valid logging level

    Allow case-insensitive matching of logging level names and return the
    corresponding integer logging level if valid, otherwise raise an error.
    """
    l_map = {
        name.casefold(): level
        for name, level in logging.getLevelNamesMapping().items()
    }
    level = l_map.get(s.casefold(), None)
    if level is None:
        raise argparse.ArgumentTypeError(
            f"Value must be one of {', '.join(ALL_LOG_LEVEL_NAMES)}."
        )
    return logging.getLevelName(level)


P_WORLD_WIDTH = Annotated[
    int,
    AfterValidator(one_plus_power_of_two),
    Field(
        ge=3,
        description="Width of the world in precincts. "
        "Must be one plus a power of two (at least 3)",
    ),
]
P_WORLD_HEIGHT = Annotated[
    int,
    AfterValidator(one_plus_power_of_two),
    Field(
        ge=3,
        description="Height of the world in precincts. "
        "Must be one plus a power of two (at least 3)",
    ),
]
P_PRECINCT_POPULATION = Annotated[
    int,
    Field(
        ge=1,
        description="Number of voters in each precinct. Must be at least 1.",
    ),
]
P_RED_FRACTION = Annotated[
    float,
    Field(
        ge=0.0,
        le=1.0,
        description="Fraction of red voters in the world. "
        "Must be between 0.0 and 1.0 inclusive.",
    ),
]
P_GEO_RANDOM_STEPS = Annotated[
    int,
    Field(
        ge=4,
        description="Number of completely random steps to take when initializing "
        "the population geography before taking neighbors into account. "
        "(Must be at least 4.)",
    ),
]
P_GEO_NEIGHBOR_WEIGHT = Annotated[
    float,
    Field(
        ge=0.0,
        le=1.0,
        description="Fraction of the precinct's population determined by the "
        "average of its neighbors' populations, the rest is a random value "
        "sampled uniformly from remaining population members without "
        "replacement. (Must be between 0.0 and 1.0 inclusive.)",
    ),
]
P_NUM_DISTRICTS = Annotated[
    int,
    Field(
        ge=2,
        description="Number of districts to create in the world. "
        "Must be at least 2.",
    ),
]
P_NUM_DELEGATES_PER_DISTRICT = Annotated[
    int,
    Field(
        ge=1,
        description="Number of delegates to elect per district. "
        "Must be at least 1.",
    ),
]
P_OUTPUT_DIRECTORY = Annotated[
    Path,
    Field(
        description="Directory where output files will be saved. Besides "
        "simulation results, this will also contain a population map "
        "file that can be loaded in future runs to evaluate the "
        "results of different and ransom values on the same "
        "underlying population distribution.",
    ),
]
P_LOAD_POP_MAP = Annotated[
    Path | None,
    Field(
        default=None,
        description="Path to a pre-generated population map file to load instead "
        "of generating a new one. If this is provided, the other "
        "population generation parameters will be ignored.",
    ),
]
P_LOG_LEVEL = Annotated[
    LogLevel,
    Field(
        description="Logging level to use.",
    ),
]


class GrreatConfigModel(BaseModel):
    """Pydantic model for Grreat configuration"""

    world_width: P_WORLD_WIDTH
    world_height: P_WORLD_HEIGHT
    precinct_population: P_PRECINCT_POPULATION = 1000
    red_fraction: P_RED_FRACTION = 0.5
    geo_random_steps: P_GEO_RANDOM_STEPS = 4
    geo_neighbor_weight: P_GEO_NEIGHBOR_WEIGHT = 0.5
    num_districts: P_NUM_DISTRICTS = 10
    num_delegates_per_district: P_NUM_DELEGATES_PER_DISTRICT = 1
    output_directory: P_OUTPUT_DIRECTORY = Field(
        default_factory=lambda: Path(
            f"output-{datetime.now().astimezone().strftime('%Y-%m-%dT%H-%M-%S')}"
        )
    )
    load_pop_map: P_LOAD_POP_MAP = None
    precincts: list[list[float]] | None = None
    log_level: P_LOG_LEVEL = "INFO"


class PopulationMap(TypedDict):
    """TypedDict for a population map file"""

    width: int
    height: int
    precinct_population: int
    precincts: list[list[float]]


def load_population_map(path: Path) -> PopulationMap | str:
    """Load a population map from the given path."""
    # TODO: Implement loading logic for population map file format.
    try:
        return PopulationMap(
            width=0, height=0, precinct_population=0, precincts=[]
        )
    except (FileNotFoundError, ValueError) as e:
        return f"Error loading population map from {path}: {e}"


def main() -> int:
    """Run Grreat simulation"""
    try:
        make_arg_parser = to_tap_class(GrreatConfigModel)
        args = make_arg_parser().parse_args()
        model = GrreatConfigModel(**args.as_dict())
        GrreatConfigModel.model_validate(model)
        print(args)
        # TODO: stub
        return 0
    except ValidationError as e:
        errs: list[ErrorDetails] = e.errors()
        for err in errs:
            print(
                f"Validation error in field '{'.'.join(map(str, err['loc']))}': {err['msg']}",
                file=sys.stderr,
            )
        return 1


if __name__ == "__main__":
    sys.exit(main())
