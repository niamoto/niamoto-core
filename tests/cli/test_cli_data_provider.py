# coding: utf-8

import unittest
import os

from click.testing import CliRunner

from niamoto.testing import set_test_path

set_test_path()

from niamoto.conf import settings, NIAMOTO_HOME
from niamoto.db import metadata as niamoto_db_meta
from niamoto.db.connector import Connector
from niamoto.bin.commands import data_provider
from niamoto.testing.test_database_manager import TestDatabaseManager
from niamoto.testing.test_data_provider import TestDataProvider
from niamoto.data_providers.plantnote_provider import PlantnoteDataProvider
from niamoto.testing.base_tests import BaseTestNiamotoSchemaCreated


class TestCLIDataProvider(BaseTestNiamotoSchemaCreated):
    """
    Test case for data provider cli methods.
    """

    TEST_DB_PATH = os.path.join(
        NIAMOTO_HOME,
        'data',
        'plantnote',
        'ncpippn_test.sqlite',
    )

    def tearDown(self):
        del1 = niamoto_db_meta.data_provider.delete()
        with Connector.get_connection() as connection:
            connection.execute(del1)

    def test_list_data_provider_types(self):
        runner = CliRunner()
        result = runner.invoke(data_provider.list_data_provider_types)
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(data_provider.list_data_provider_types)
        self.assertEqual(result.exit_code, 0)

    def test_list_data_providers(self):
        runner = CliRunner()
        result = runner.invoke(data_provider.list_data_providers)
        self.assertEqual(result.exit_code, 0)
        TestDataProvider.register_data_provider('test_data_provider_1')
        result = runner.invoke(data_provider.list_data_providers)
        self.assertEqual(result.exit_code, 0)

    def test_add_data_provider(self):
        runner = CliRunner()
        result = runner.invoke(
            data_provider.add_data_provider,
            ['test_provider', 'PLANTNOTE'],
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            data_provider.add_data_provider,
            ['test_provider', 'PLANTNOTE'],
        )
        self.assertEqual(result.exit_code, 1)

    def test_update_data_provider(self):
        runner = CliRunner()
        PlantnoteDataProvider.register_data_provider(
            'test_data_provider_1'
        )
        result = runner.invoke(
            data_provider.update_data_provider_cli,
            ['test_data_provider_1', '--new_name', 'YO'],
        )
        self.assertEqual(result.exit_code, 0)

    def test_delete_data_provider(self):
        runner = CliRunner()
        TestDataProvider.register_data_provider('test_data_provider_1')
        result = runner.invoke(
            data_provider.delete_data_provider,
            ['test_data_provider_1'],
            input='N'
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            data_provider.delete_data_provider,
            ['-y', True, 'test_data_provider_1']
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            data_provider.delete_data_provider,
            ['-y', True, 'test_data_provider_1']
        )
        self.assertEqual(result.exit_code, 1)

    def test_sync(self):
        runner = CliRunner()
        PlantnoteDataProvider.register_data_provider(
            'plantnote_provider',
            self.TEST_DB_PATH,
        )
        result = runner.invoke(
            data_provider.sync,
            ['plantnote_provider', self.TEST_DB_PATH]
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            data_provider.sync,
            ['plantnote_provider', self.TEST_DB_PATH]
        )
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(
            data_provider.sync,
            ['plantnote', self.TEST_DB_PATH]
        )
        self.assertEqual(result.exit_code, 1)
        result = runner.invoke(
            data_provider.sync,
            ['plantnote_provider', "yo"]
        )
        self.assertEqual(result.exit_code, 1)


if __name__ == '__main__':
    TestDatabaseManager.setup_test_database()
    TestDatabaseManager.create_schema(settings.NIAMOTO_SCHEMA)
    TestDatabaseManager.create_schema(settings.NIAMOTO_RASTER_SCHEMA)
    TestDatabaseManager.create_schema(settings.NIAMOTO_VECTOR_SCHEMA)
    unittest.main(exit=False)
    TestDatabaseManager.teardown_test_database()
