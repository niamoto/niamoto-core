# coding: utf-8

import sqlalchemy as sa
from cubes import Workspace

from niamoto.conf import settings
from niamoto.db.connector import Connector
from niamoto.data_marts.fact_tables.base_fact_table import BaseFactTable
from niamoto.data_marts.dimensions.base_dimension import \
    DIMENSION_TYPE_REGISTRY
from niamoto.data_publishers.base_data_publisher import PUBLISHER_REGISTRY
from niamoto.data_marts.dimensions.dimension_manager import DimensionManager
from niamoto.exceptions import DimensionNotRegisteredError


class DimensionalModel:
    """
    Class representing the whole dimensional model: dimensions and
    fact tables.
    """

    def __init__(self, dimensions, fact_tables, aggregates):
        """
        :param dimensions: Dict of model dimensions,
            dimension_name: dimension.
        :param fact_tables: Dict of fact_tables,
            fact_table_name: fact_table.
        :param aggregates: Dict of aggregates for the fact tables,
            fact_table_name: aggregate (please refer to cubes documentation as
            Niamoto won't do anything else to pass it directly to cubes.
            http://cubes.readthedocs.io/en/v1.1/reference/browser.html)
        """
        self.dimensions = dimensions
        self.fact_tables = fact_tables
        self.aggregates = aggregates

    def generate_cubes_model(self):
        """
        Generate a model for the cubes OLAP framework.
        """
        dims = []
        mappings = {}
        joins = []
        for k, v in self.dimensions.items():
            mappings[v.name] = '{}.id'.format(v.name)
            dims.append(v.get_cubes_dict())
            joins += v.get_cubes_joins()
            mappings.update(v.get_cubes_mappings())
        cubes = []
        for k, v in self.fact_tables.items():
            cubes.append({
                'name': '{}'.format(v.name),
                'label': '{}'.format(v.name),
                'dimensions': [dim.name for dim in v.dimensions],
                'measures': [
                    {'name': m.name}
                    for m in v.columns
                ],
                'joins': [
                    {
                        'master': {
                            'schema': settings.NIAMOTO_FACT_TABLES_SCHEMA,
                            'table': v.name,
                            'column': '{}_id'.format(d.name),
                        },
                        'detail': {
                            'schema': settings.NIAMOTO_DIMENSIONS_SCHEMA,
                            'table': d.name,
                            'column': 'id',
                        }
                    } for d in v.dimensions
                ] + joins,
                'mappings': mappings,
                'aggregates': self.aggregates[k],
            })
        return {'dimensions': dims, 'cubes': cubes}

    def get_cubes_workspace(self):
        workspace = Workspace()
        workspace.register_default_store(
            "sql",
            url=Connector.get_database_url(),
            schema=settings.NIAMOTO_FACT_TABLES_SCHEMA,
            dimension_schema=settings.NIAMOTO_DIMENSIONS_SCHEMA,
        )
        workspace.import_model(self.generate_cubes_model())
        return workspace

    def create_model(self):
        """
        Create the dimension tables and the fact tables.
        """
        with Connector.get_connection() as connection:
            for k, v in self.dimensions.items():
                v.create_dimension(connection=connection)
            for k, v in self.fact_tables.items():
                v.create_fact_table(connection=connection)

    def populate_dimensions(self):
        for k, v in self.dimensions.items():
            v.populate_from_publisher()

    def populate_fact_tables(self):
        for k, v in self.fact_tables.items():
            v.populate_from_publisher()


def load_model_from_dict(model_dict):
    """
    Load the dimensional model from a dict.
    :param model_dict: The model dict, must have the following structure:
        {
            'dimensions': [
                {
                    'name': 'dim_1', # MANDATORY
                    'label_col': 'label',
                    'dimension_type': 'DIMTYPE', # MANDATORY IF NOT REGISTERED
                    'extra_arg': extra_value,
                },
                {
                    'name': 'dim_2',
                    'dimension_type': 'DIM_2_TYPE',
                }
            ],
            'fact_tables': [
                {
                    'name': 'fact_table_1',
                    'dimensions': ['dim_1', 'dim_2'],
                    'measures': ['measure_1', 'measure_2'],
                    'publisher_key': 'FACT_TABLE_PUBLISHER_KEY',
                    'aggregates': [
                        {
                            'name': 'aggregate_name',
                            'function': 'aggregate_function',
                            'measure': 'measure_1'
                        }
                    ],
                },
            ]
        }
    For the 'aggregates' part, please refer to cubes documentation as Niamoto
    won't do anything else to pass it directly to cubes.
    http://cubes.readthedocs.io/en/v1.1/reference/browser.html
    :return: A dimensional model instance.
    """
    dims = model_dict['dimensions']
    f_tables = model_dict['fact_tables']
    dimensions = {}
    fact_tables = {}
    aggregates = {}
    for dim in dims:
        dim_name = dim.pop('name')
        try:
            # If the dimension is already registered, load it
            loaded_dimension = DimensionManager.get_dimension(dim_name)
            dimensions[dim_name] = loaded_dimension
        except DimensionNotRegisteredError:
            # Else, instantiate it
            dim_type = dim.pop('dimension_type')
            dim_cls = DIMENSION_TYPE_REGISTRY[dim_type]['class']
            d = dim_cls(dim_name, **dim)
            dimensions[dim_name] = d
    for ft in f_tables:
        ft_name = ft['name']
        ft_dims = [dimensions[i] for i in ft['dimensions']]
        measures = [sa.Column(i, sa.Float()) for i in ft['measures']]
        publisher_cls = None
        if 'publisher_key' in ft:
            pub_key = ft['publisher_key']
            publisher_cls = PUBLISHER_REGISTRY[pub_key]['class']
        fact_tables[ft_name] = BaseFactTable(
            ft_name,
            ft_dims,
            measures,
            publisher_cls=publisher_cls
        )
        aggregates[ft_name] = ft['aggregates']
    return DimensionalModel(dimensions, fact_tables, aggregates)
