import sqlite3
from sqlalchemy import create_engine
from dynaconf import settings
import pandas as pd


def connect():
    return create_engine(f"sqlite:///{settings.DB_PATH}")


def persist() -> str:
    """Perform table creation for the app, based on default data. If tables \
        already exists, nothing is done.
    """
    app_config_df = pd.DataFrame.from_dict({
        'open_folder': [settings.DEFAULT_OPEN_FOLDER],
        'save_folder': [settings.DEFAULT_SAVE_FOLDER]
    })

    diffusivity_df = pd.DataFrame({
        'immobile': [settings.DEFAULT_IMMOBILE_MIN,
                     settings.DEFAULT_IMMOBILE_MAX],
        'sub_diffusive': [settings.DEFAULT_SUB_DIFFUSIVE_MIN,
                          settings.DEFAULT_SUB_DIFFUSIVE_MAX],
        'diffusive': [settings.DEFAULT_DIFFUSIVE_MIN,
                      settings.DEFAULT_DIFFUSIVE_MAX],
        'active': [settings.DEFAULT_ACTIVE_MIN,
                   None]
    })

    analysis_config_df = pd.DataFrame({
        'p_size': settings.DEFAULT_P_SIZE,
        'min_frames': settings.DEFAULT_MIN_FRAMES,
        'fps': settings.DEFAULT_FPS,
        'total_frames': settings.DEFAULT_TOTAL_FRAMES,
        'width_px': settings.DEFAULT_WIDTH_PX,
        'width_si': settings.DEFAULT_WIDTH_SI
    })

    trajectories_df = pd.DataFrame(
        columns=['file_name', 'trajectory', 'frame', 'x', 'y'])

    summary_df = pd.DataFrame(
        columns=['full_path', 'file_name', 'trajectories', 'valid'])

    msg = create_table('app_config', app_config_df)
    msg += f"\n{create_table('diffusivity', diffusivity_df)}"
    msg += f"\n{create_table('analysis_config', analysis_config_df)}"
    msg += f"\n{create_table('trajectories', trajectories_df)}"
    msg += f"\n{create_table('summary', summary_df)}"
    return msg


def create_table(table_name: str, data: pd.DataFrame) -> str:
    """Creates table based on received DataFrame. Forces fail if pandas \
        detect that the table already exists.

    Arguments:
        table_name {str} -- Name of the table to be created.
        data {pd.DataFrame} -- Data to be inserted.
    """
    conn = connect()
    try:
        data.to_sql(table_name, con=conn, index=False, if_exists='fail')
        msg = f"Table '{table_name}' created."
    except ValueError:
        msg = f"Table '{table_name}' already exists. Aborting."
    finally:
        return msg


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
            p_size INT,
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
                            INTO 'diffusivity' (name, min, max)
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
                          INTO 'analysis_config' (id, p_size, min_frames,
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
