import sqlite3


class Database:
    def __init__(self, db: str) -> None:
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS diffusivity (
            name CHAR(50) PRIMARY KEY,
            min REAL,
            max REAL);""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS analysis_config (
            id INT PRIMARY KEY,
            fps INT,
            total_frames INT,
            width_px INT,
            width_um INT,
            min_frames INT);""")
        self.conn.commit()

    def persist(self):
        diffusivity = """INSERT OR IGNORE 
                         INTO 'diffusivity' (min, max, name)
                         VALUES (0.0, 0.199, 'immobile'),
                                (0.2, 0.899, 'sub-diffusive'),
                                (0.9, 1.199, 'diffusive'),
                                (1.2, NULL, 'active');"""
        self.cur.execute(diffusivity)

        analysis = """INSERT OR IGNORE 
                      INTO 'analysis_config'
                      (id, fps,total_frames, width_px, width_um, min_frames) 
                      VALUES (1, 30, 606, 512, 160, 590)"""
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

    def remove(self, columns):
        pass

    def update(self, columns):
        pass
