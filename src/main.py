import argparse
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from tap import Tap


def one_plus_power_of_two(s: str) -> int:
    """Validate that the input is one plus a power of two

    The power of 2 must be at least 2.
    """
    try:
        value = int(s)
        if value < 3 or (value - 1) & (value - 2) != 0:
            raise argparse.ArgumentTypeError(
                "Value must be one plus a power of two (at least 3)."
            )
        return value
    except ValueError:
        raise argparse.ArgumentTypeError("Value must be an integer.")


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


class GrreatConfig(Tap):
    """Configuration for Minimal Grreat simulation"""

    world_width: int
    world_height: int
    precinct_population: int
    red_fraction: float
    geo_random_steps: int
    geo_neighbor_weight: float
    num_districts: int
    output_directory: Path

    def configure(self) -> None:
        """TAP config that doesn't fit as class attributes"""
        self.add_argument(
            "--world-width",
            type=one_plus_power_of_two,
            help="Width of the world in precincts. "
            "Must be one plus a power of two (at least 3)",
        )
        self.add_argument(
            "--world-height",
            type=one_plus_power_of_two,
            help="Height of the world in precincts. "
            "Must be one plus a power of two (at least 3)",
        )
        self.add_argument(
            "--precinct-population",
            type=int_at_least(1),
            default=1000,
            help="Number of voters in each precinct. Must be at least 1.",
        )
        self.add_argument(
            "--red-fraction",
            type=zero_to_one,
            default=0.5,
            help="Fraction of red voters in the world. "
            "Must be between 0.0 and 1.0 inclusive.",
        )
        self.add_argument(
            "--geo-random-steps",
            type=int_at_least(4),
            default=4,
            help="Number of completely random steps to take when initializing "
            "the population geography before taking neighbors into account. "
            "(Must be at least 4.)",
        )
        self.add_argument(
            "--geo-neighbor-weight",
            type=zero_to_one,
            default=0.5,
            help="Fraction of the precinct's population determined by the "
            "average of its neighbors' populations, the rest is a random value "
            "sampled uniformly from remaining population members without "
            "replacement. (Must be between 0.0 and 1.0 inclusive.)",
        )
        self.add_argument(
            "--num-districts",
            type=int_at_least(2),
            default=10,
            help="Number of districts to create in the world. "
            "Must be at least 2.",
        )
        now_str = datetime.now().astimezone().strftime("%Y-%m-%dT%H-%M-%S")
        self.add_argument(
            "--output-directory",
            type=Path,
            default=Path(f"output-{now_str}"),
            help="Directory where output files will be saved.",
        )


def main() -> int:
    """Run Grreat simulation"""
    args = GrreatConfig().parse_args()
    print(args)
    # TODO: stub
    return 0


if __name__ == "__main__":
    sys.exit(main())
