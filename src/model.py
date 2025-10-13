"""Models for Grreat experiments"""

from datetime import datetime, timezone

from pydantic import model_validator
from sqlalchemy.orm import Relationship
from sqlmodel import SQLModel, Field


class FactionTotal(SQLModel, table=True):
    """A faction's total population for a particular
    set of faction totals.

    Each set of totals has at most one entry for
    each faction.
    """

    faction_totals_id: int | None = Field(
        foreign_key="faction_totals.id", primary_key=True
    )
    faction_id: int = Field(primary_key=True)
    population: int


class FactionTotals(SQLModel, table=True):
    """A list of faction totals"""

    id: int | None = Field(primary_key=True)
    totals: list[FactionTotal] = Relationship(
        back_populates="faction_totals_id"
    )


class PopulationDistribution(SQLModel, table=True):
    """A population distribution

    Attributes:
        id: The unique identifier for the population distribution
        uniform_rect_distribution_id: The foreign key to the uniform distribution
           if this is a uniform rectangular distribution
        checkerboard_rect_distribution_id: The foreign key to the checkerboard
           distribution if this is a checkerboard rectangular distribution
    """

    id: int | None = Field(primary_key=True)
    uniform_rect_distribution_id: int | None = Field(
        foreign_key="uniform_rect_distribution.id"
    )
    checkerboard_rect_distribution_id: int | None = Field(
        foreign_key="checkerboard_rect_distribution.id"
    )

    @model_validator(mode="after")
    def validate_distribution(self):
        """Validate that only one of the distributions is set"""
        num_set_ids = sum(
            1 if i else 0
            for i in (
                self.uniform_rect_distribution_id,
                self.checkerboard_rect_distribution_id,
            )
        )
        if num_set_ids != 1:
            raise ValueError("Exactly one distribution type id must be set.")


class UniformRectDistribution(SQLModel, table=True):
    """A uniform population distribution on a rectangular grid

    Attributes:
        id: The unique identifier for the uniform distribution instance
        faction_totals_id: The set of totals for all factions with non-zero
            populations in this distribution
        width: The width of the grid in precincts
        height: The height of the grid in precincts
    """

    id: int | None = Field(primary_key=True)
    faction_totals_id: int | None = Field(foreign_key="faction_totals.id")
    width: int
    height: int


class CheckerboardRectDistribution(SQLModel, table=True):
    """A checkerboard population distribution on a rectangular grid

    This is not a random distribution. The upper right block has
    even_precinct_population its neighbor has odd_precinct_population.
    The next row down starts with odd_precinct_population, forming
    a checkerboard pattern.

    Attributes:
        id: The unique identifier for the checkerboard distribution instance
        even_precinct_population: In the even blocks, each precinct has this
           population.
        odd_precinct_population: In the odd blocks, each precinct has this
           population.
        num_block_width: The width of the grid in blocks
        num_block_height: The height of the grid in blocks
        block_width: The width of each block in precincts
        block_height: The height of each block in precincts
    """

    id: int | None = Field(primary_key=True)
    even_precinct_population: int | None = Field(
        foreign_key="faction_totals.id"
    )
    odd_precinct_population: int | None = Field(foreign_key="faction_totals.id")
    num_block_width: int
    num_block_height: int
    block_width: int
    block_height: int


class PopulationMap(SQLModel, table=True):
    """Population map model for Grreat experiments

    Attributes:
        id: The unique identifier for the population map
        creation_time: The time at which the population map was created
        distribution_id: The distribution from which
            this population map was drawn
        faction_counts: The counts of the populations in the cells in
            the population map
    """

    id: int | None = Field(primary_key=True)
    creation_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    distribution_id: int | None = Field(
        foreign_key="population_distribution.id"
    )
    faction_counts: list["PopulationMapCellFactionCount"] = Relationship(
        back_populates="population_map_cell_id"
    )


class PopulationMapCellFactionCount(SQLModel, table=True):
    """A faction count in a population map cell

    Initially, the x and y coordinates are of the center of
    a grid square. However, later maps might have irregular
    precinct shapes.

    Attributes:
        x: The x coordinate of a point in the cell
        y: The y coordinate of a point in the cell
        population_map_id: The population map this cell is part of
        faction_id: The faction counted by this cell
        count: The number of individuals belonging to
           this faction in this cell.
    """

    x: float = Field(primary_key=True)
    y: float = Field(primary_key=True)
    population_map_id: int = Field(
        foreign_key="population_map.id", index=True, primary_key=True
    )
    faction_id: int = Field(primary_key=True)
    count: int = Field(default=0)
