"""
This collection of tests is intended to be run in a pre-prod environment that has access to all of the resources
required to fully execute BCP commands. These tests will be accessing the database, writing actual files, reading in
actual files, and writing data to the database. These tests will require:

    - an instance of each supported database type (mssql, etc.)
    - an account that has access to create/drop tables and insert data into those tables in said database

The settings that appear within each of the connection fixtures, and at the top of each test class, should be updated
to reflect the associated pre-prod environment. They are not saved (and should be set back to anonymous names after
testing and before saving) because they would contain actual machine names and credentials.
"""
import pathlib
import subprocess

import pytest

from .context import STATIC_FILES, Connection, BCP, DataFile


@pytest.fixture
def mssql_bcp() -> BCP:
    host = 'MSSQL'
    username = None
    password = None
    conn = Connection(host=host, driver='mssql', username=username, password=password)
    return BCP(conn)

@pytest.mark.skip
class TestMSSQL:

    database = 'DATABASE'
    schema = 'SCHEMA'

    def test_mssql_can_dump_tables(self, mssql_bcp):
        query = f'''
            select s.name as schema_name, t.name as table_name
            from {self.database}.sys.tables t
            join {self.database}.sys.schemas s
            on s.schema_id = t.schema_id
        '''
        output_file_path = DataFile(STATIC_FILES / pathlib.Path('output.dat'))
        output_file = DataFile(output_file_path)
        mssql_bcp.dump(query, output_file)
        assert True is output_file.file.is_file()
        output_file.file.unlink()

    def test_mssql_can_load_tables(self, mssql_bcp):
        table = f'{self.database}.{self.schema}.input_file'
        create = f'create table {table} (schema_name varchar(20), table_name varchar(100))'
        drop = f'drop table {table}'
        sqlcmd = f'sqlcmd -S {mssql_bcp.connection.host} -Q'
        subprocess.run(f'{sqlcmd} "{create}"', check=True)
        input_file_path = DataFile(STATIC_FILES / pathlib.Path('input.dat'))
        input_file = DataFile(input_file_path)
        mssql_bcp.load(input_file, table)
        subprocess.run(f'{sqlcmd} "{drop}"', check=True)
        assert 1 == 1
