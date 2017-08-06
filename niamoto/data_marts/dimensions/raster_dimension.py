# coding: utf-8

import sqlalchemy as sa

from niamoto.data_marts.dimensions.base_dimension import BaseDimension
from niamoto.data_publishers.raster_data_publisher import \
    RasterValueCountPublisher


class RasterDimension(BaseDimension):
    """
    Dimension extracted from a registered raster, contains the different
    values of a raster and their associated pixel count.
    """

    def __init__(self, raster_name, cuts=None):
        """
        :param raster_name: The raster name.
        :param cuts: Cuts corresponding to categories: ([cuts], [labels]).
            len(labels) = len(cuts) + 1
            e.g: ([10, 20, 30], ['low', 'medium', 'high', 'very high'])
            corresponds to:
                [min_value, 10[   => 'low'
                [10, 20[          => 'medium'
                [20, 30[          => 'high'
                [30, max_value[   => 'very high'
            ]
        """
        self.raster_name = raster_name
        self.cuts = cuts
        properties = {}
        columns = [
            sa.Column(self.raster_name, sa.Float),
            sa.Column("pixel_count", sa.Integer)
        ]
        if self.cuts is not None:
            assert len(cuts[1]) == len(cuts[0]) + 1
            columns += [
                sa.Column("category", sa.String)
            ]
            properties['cuts'] = cuts
        super(RasterDimension, self).__init__(
            raster_name,
            columns,
            publisher=RasterValueCountPublisher(),
            label_col=self.raster_name,
            properties=properties
        )

    @classmethod
    def load(cls, dimension_name, label_col='label', properties={}):
        cuts = None
        if 'cuts' in properties:
            cuts = properties['cuts']
        return cls(dimension_name, cuts=cuts)

    def populate_from_publisher(self, *args, **kwargs):
        return super(RasterDimension, self).populate_from_publisher(
            self.raster_name,
            *args,
            cuts=self.cuts,
            **kwargs
        )

    @classmethod
    def get_description(cls):
        return "Raster dimension, values are extracted from " \
               "a registered raster."

    @classmethod
    def get_key(cls):
        return "RASTER_DIMENSION"

    def get_cubes_levels(self):
        if self.cuts is None:
            return super(RasterDimension, self).get_cubes_levels()
        return [
            {
                'name': 'category',
                'attributes': ['category', ]
            },
            {
                'name': self.name,
                'attributes': ['id', self.name],
            }
        ]
