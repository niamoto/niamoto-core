# coding: utf-8

import sqlalchemy as sa
import pandas as pd

from niamoto.db import metadata as meta
from niamoto.db.connector import Connector
from niamoto.data_marts.dimensions.base_dimension import \
    DIMENSION_TYPE_REGISTRY
from niamoto.exceptions import DimensionNotRegisteredError


class DimensionManager:
    """
    Dimension manager: register dimensions, list dimensions,
    list dimension types...
    """

    @classmethod
    def get_dimension_types(cls):
        """
        :return: The list of (conformed) dimension types.
        """
        return DIMENSION_TYPE_REGISTRY

    @classmethod
    def get_registered_dimensions(cls):
        """
        :return: The list of registered dimensions.
        """
        sel = sa.select([meta.dimension_registry, ])
        with Connector.get_connection() as connection:
            return pd.read_sql(
                sel,
                connection,
                index_col=meta.dimension_registry.c.id.name
            )

    @classmethod
    def assert_dimension_is_registered(cls, dimension_name, connection=None):
        """
        Assert that a dimension is registered.
        Raise DimensionNotRegisteredError otherwise.
        :param dimension_name: The name of the dimension to check.
        :param connection: If passed, use an existing connection.
        """
        sel = meta.dimension_registry.select().where(
            meta.dimension_registry.c.name == dimension_name
        )
        if connection is not None:
            r = connection.execute(sel).rowcount
        else:
            with Connector.get_connection() as connection:
                r = connection.execute(sel).rowcount
        if r == 0:
            m = "The dimension '{}' is not registered in database."
            raise DimensionNotRegisteredError(m.format(dimension_name))

    @classmethod
    def get_dimension(cls, dimension_name):
        """
        Loads a registered dimension.
        :param dimension_name: The name of the dimension to load.
        :return: The loaded dimension.
        """
        sel = sa.select([
            meta.dimension_registry.c.dimension_type_key,
            meta.dimension_registry.c.label_column,
        ]).where(
            meta.dimension_registry.c.name == dimension_name
        )
        with Connector.get_connection() as connection:
            result = connection.execute(sel).fetchone()
            dim_type, label_column = result
        return DIMENSION_TYPE_REGISTRY[dim_type]['class'].load(
            dimension_name,
            label_col=label_column,
        )

    @classmethod
    def delete_dimension(cls, dimension_name):
        """
        Delete a registered dimension.
        :param dimension_name: The dimension name.
        """
        cls.get_dimension(dimension_name).drop_dimension()
