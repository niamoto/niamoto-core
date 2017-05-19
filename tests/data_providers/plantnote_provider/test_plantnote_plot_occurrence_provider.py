# coding: utf-8

import unittest
import os

from niamoto.testing import set_test_path
set_test_path()

from niamoto.conf import settings, NIAMOTO_HOME
from niamoto.db.connector import Connector
from niamoto.data_providers.plantnote_provider import PlantnoteDataProvider
from niamoto.testing.base_tests import BaseTestNiamotoSchemaCreated
from niamoto.testing.test_database_manager import TestDatabaseManager
from niamoto.taxonomy import populate


class TestPlantnotePlotOccurrenceProvider(BaseTestNiamotoSchemaCreated):
    """
    Test case for plantnote plot occurrence provider.
    """

    TEST_DB_PATH = os.path.join(
        NIAMOTO_HOME,
        'data',
        'plantnote',
        'ncpippn_test.sqlite',
    )

    @classmethod
    def setUpClass(cls):
        super(TestPlantnotePlotOccurrenceProvider, cls).setUpClass()
        # Register Pl@ntnote data provider
        PlantnoteDataProvider.register_data_provider_type(
            database=settings.TEST_DATABASE
        )
        PlantnoteDataProvider.register_data_provider(
            'pl@ntnote_provider',
            cls.TEST_DB_PATH,
            database=settings.TEST_DATABASE,
        )
        # Populate taxon
        populate.populate_ncpippn_taxon_database(
            populate.load_ncpippn_taxon_dataframe_from_json(),
            database=settings.TEST_DATABASE,
        )

    def test_get_dataframe_and_sync(self):
        db = settings.TEST_DATABASE
        pt_provider = PlantnoteDataProvider(
            'pl@ntnote_provider',
            self.TEST_DB_PATH,
            database=db,
        )
        with Connector.get_connection(database=db) as connection:
            prov = pt_provider.plot_occurrence_provider
            df1 = prov.get_niamoto_plot_occurrence_dataframe(connection)
            self.assertEqual(len(df1), 0)
            # Sync plots and occurrences
            plot_prov = pt_provider.plot_provider
            occ_prov = pt_provider.occurrence_provider
            plot_prov.sync(connection)
            occ_prov.sync(connection)
            # Sync plot-occurrences
            df2 = prov.get_provider_plot_occurrence_dataframe()
            cols = df2.columns
            for i in ['occurrence_identifier', ]:
                self.assertIn(i, cols)
            prov.sync(connection)
            df3 = prov.get_niamoto_plot_occurrence_dataframe(connection)
            self.assertEqual(len(df2), len(df3))


if __name__ == '__main__':
    TestDatabaseManager.setup_test_database()
    TestDatabaseManager.create_schema('niamoto')
    unittest.main(exit=False)
    TestDatabaseManager.teardown_test_database()