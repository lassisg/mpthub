import sqlite3
from pathlib import Path
from dynaconf import settings


class Database:
    def __init__(self) -> None:
        """Initializes database for the analysis.

        Opens sqlite database if exists (otherwise creates it) and creates\
            a connection to it. For safety, calls a function to create some\
            essential tables in case they doesn't exist.
        """
        self.conn = sqlite3.connect(settings.DB_PATH)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self) -> None:
        """Creates essential tables if they doesn't exist.

        Creates the three essential tables used by the app:
        - app_config: Holds import and export paths string.
        - diffusivity: Holds diffusivity ranges for immobile, sub-diffusive,\
            diffusive and active behavior.
        - analysis_config: Holds acquisition data, i.e., particle size, frames\
            per second, total number of frames in the video, width (in px),\
            width (in µm), minimum number of frames to be considered a valid\
            trajectory.
        """
        self.cur.execute("""CREATE TABLE IF NOT EXISTS app_config(
            id INT PRIMARY KEY,
            open_folder VARCHAR,
            save_folder VARCHAR); """)

        self.cur.execute("""CREATE TABLE IF NOT EXISTS diffusivity(
            name CHAR(50) PRIMARY KEY,
            min REAL,
            max REAL); """)

        self.cur.execute("""CREATE TABLE IF NOT EXISTS analysis_config(
            id INT PRIMARY KEY,
            size INT,
            min_frames INT,
            fps INT,
            total_frames INT,
            width_px INT,
            width_si INT); """)
        self.conn.commit()

    def persist(self) -> None:
        """Insert data on tables if there are none. This prevents crashes\
            as there must exist some essential data.
        """
        app_config = f"""INSERT OR IGNORE
                           INTO 'app_config' (id, open_folder, save_folder)
                         VALUES (1, '{settings.DEFAULT_OPEN_FOLDER}',
                                    '{settings.DEFAULT_SAVE_FOLDER}');"""
        self.cur.execute(app_config)

        diffusivity = f"""INSERT OR IGNORE
                            INTO 'diffusivity' (min, max, name)
                          VALUES ('immobile',
                                  {settings.DEFAULT_IMMOBILE.min},
                                  {settings.DEFAULT_IMMOBILE.max}),
                                 ('sub-diffusive',
                                  {settings.DEFAULT_SUB_DIFFUSIVE.min},
                                  {settings.DEFAULT_SUB_DIFFUSIVE.max}),
                                 ('diffusive',
                                  {settings.DEFAULT_DIFFUSIVE.min},
                                  {settings.DEFAULT_DIFFUSIVE.max}),
                                 ('active',
                                  {settings.DEFAULT_ACTIVE.min},
                                  NULL);"""
        self.cur.execute(diffusivity)

        analysis = f""" INSERT OR IGNORE
                          INTO 'analysis_config' (id, size, min_frames,
                                                  fps, total_frames,
                                                  width_px, width_si)
                        VALUES (1, {settings.SIZE}, {settings.MIN_FRAMES},
                                {settings.FPS}, {settings.TOTAL_FRAMES},
                                {settings.WIDTH_PX}, {settings.WIDTH_SI})"""
        self.cur.execute(analysis)

        self.conn.commit()

    def fetch(self, table: str) -> list:
        """Fetch data from a given table.

        Parameters
        ----------
        table : str
            Table name.

        Returns
        -------
        list
            List with fetched data from given table.
        """
        self.cur.execute(f"SELECT * FROM {table}")
        config = self.cur.fetchall()
        return config

    def insert(self, table: str, values: list) -> None:
        """Inserts data into a given table.

        Parameters
        ----------
        table : str
            Name of the table to receive the values.

        values : list
            Values to be inserted into the given table.
        """
        sep = ", "
        query_values = sep.join(values)
        column_values = sep.join(['?' for item in values])
        insert_query = f"INSERT INTO {table} VALUES ({column_values})"

        self.cur.execute(insert_query, (query_values))
        self.conn.commit()

    def update_app_config(self, path_data: tuple) -> None:
        """Updates App configuration table (import and export paths).

        Parameters
        ----------
        path_data : tuple
            Paths data to be updated into table.
        """
        app_config = """UPDATE app_config
                           SET open_folder = ?,
                               save_folder = ?
                         WHERE id = 1;"""
        self.cur.execute(app_config, path_data)
        self.conn.commit()

    def update_diffusivity_config(self, range_data: tuple) -> None:
        """Updates Diffusivity ranges configuration table.

        Parameters
        ----------
        range_data : tuple
            Range data to be updated into table, according to the range.
        """
        diffusivity = """UPDATE diffusivity
                            SET min = ?,
                                max = ?
                          WHERE name = ?;"""
        self.cur.execute(diffusivity, range_data)
        self.conn.commit()

    def update_analysis_config(self, config_range: tuple) -> None:
        """Updates Analysis configuration table.

        Parameters
        ----------
        config_range : tuple
            Essential configuration tha must exist for the app to really work.
        """
        analysis = """UPDATE analysis_config
                         SET size = ?,
                             min_frames = ?,
                             fps = ?,
                             total_frames = ?,
                             width_px = ?,
                             width_um = ?
                       WHERE id = 1;"""
        self.cur.execute(analysis, config_range)
        self.conn.commit()
