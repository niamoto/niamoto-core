# coding: utf-8

import sqlalchemy as sa

from niamoto.data_marts.dimensions.base_dimension import BaseDimension
from niamoto.data_publishers.taxon_data_publisher import TaxonDataPublisher
from niamoto.db.metadata import TaxonRankEnum


class TaxonDimension(BaseDimension):
    """
    Extension of the base dimension representing the taxon dimension.
    """

    DEFAULT_NAME = "taxon_dimension"
    COLUMNS = [
        sa.Column('full_name', sa.String),
        sa.Column('rank_name', sa.String),
        sa.Column('rank', sa.String),
    ] + [sa.Column(opt.value.lower(), sa.String) for opt in TaxonRankEnum]
    PUBLISHER = TaxonDataPublisher()

    def __init__(self, name=DEFAULT_NAME, publisher=PUBLISHER):
        super(TaxonDimension, self).__init__(
            name,
            self.COLUMNS,
            publisher=publisher
        )

    def populate_from_publisher(self, *args, **kwargs):
        return super(TaxonDimension, self).populate_from_publisher(
            *args,
            flatten=True,
            **kwargs
        )
