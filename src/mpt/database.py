import sqlite3
import os


class Database:
    def __init__(self, base_dir: str) -> None:
        self.base_path = base_dir
        self.db_path = os.path.join(self.base_path, 'config.db')
        self.report_path = os.path.join(self.base_path, 'export')

        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()

        self.cur.execute("""CREATE TABLE IF NOT EXISTS app_config (
            open_folder VARCHAR,
            save_folder VARCHAR);""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS diffusivity (
            name CHAR(50) PRIMARY KEY,
            min REAL,
            max REAL);""")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS analysis_config (
            id INT PRIMARY KEY,
            size INT,
            fps INT,
            total_frames INT,
            width_px INT,
            width_um INT,
            min_frames INT);""")
        self.conn.commit()

    def persist(self) -> None:
        app_config = f"""INSERT OR IGNORE 
                           INTO 'app_config' (open_folder, save_folder)
                         VALUES ('{self.db_path}', '{self.report_path}');"""
        self.cur.execute(app_config)

        diffusivity = """INSERT OR IGNORE 
                           INTO 'diffusivity' (min, max, name)
                         VALUES (0.0, 0.199, 'immobile'),
                                (0.2, 0.899, 'sub-diffusive'),
                                (0.9, 1.199, 'diffusive'),
                                (1.2, NULL, 'active');"""
        self.cur.execute(diffusivity)

        analysis = """INSERT OR IGNORE 
                        INTO 'analysis_config' (id, size, fps, total_frames, 
                                                width_px, width_um, min_frames) 
                      VALUES (1, 200, 30, 606, 512, 160, 590)"""
        self.cur.execute(analysis)

        self.conn.commit()

    def fetch(self, table):
        self.cur.execute(f"SELECT * FROM {table}")
        config = self.cur.fetchall()
        return config

    def insert(self, table: str, values: list):
        sep = ", "
        query_values = sep.join(values)
        column_values = sep.join(['?' for item in values])
        insert_query = f"INSERT INTO {table} VALUES ({column_values})"

        self.cur.execute(insert_query, (query_values))
        self.conn.commit()

    def update_app_config(self, path_data: tuple) -> None:
        app_config = """UPDATE app_config 
                           SET open_folder = ?,
                               save_folder = ?;"""
        self.cur.execute(app_config, path_data)
        self.conn.commit()

    def update_diffusivity_config(self, range_data: tuple) -> None:
        diffusivity = """UPDATE diffusivity 
                            SET min = ?,
                                max = ?
                          WHERE name = ?;"""
        self.cur.execute(diffusivity, range_data)
        self.conn.commit()

    def update_analysis_config(self, config_range: tuple) -> None:
        analysis = """UPDATE analysis_config
                         SET size = ?,
                             fps = ?,
                             total_frames = ?,
                             width_px = ?,
                             width_um = ?,
                             min_frames = ?
                       WHERE id = 1;"""
        self.cur.execute(analysis, config_range)
        self.conn.commit()
