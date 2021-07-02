# import sqlite3
from sqlalchemy import create_engine, Table, MetaData
import pandas as pd
from sqlalchemy.schema import DropTable
from .settings import Settings
from pathlib import Path

settings = Settings()


def resolve_paths() -> None:
    if not Path(settings.BASE_PATH).exists():
        Path.mkdir(Path(settings.BASE_PATH))

    if not Path(settings.EXPORT_PATH).exists():
        Path.mkdir(Path(settings.EXPORT_PATH))


def connect():
    return create_engine(f"sqlite:///{settings.DB_PATH}")


def persist() -> str:
    """Perform table creation for the app, based on default data. If tables \
        already exists, nothing is done.
    """
    resolve_paths()

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
        'p_size': [settings.DEFAULT_P_SIZE],
        'min_frames': [settings.DEFAULT_MIN_FRAMES],
        'fps': [settings.DEFAULT_FPS],
        'delta_t': [settings.DEFAULT_DELTA_T],
        'total_frames': [settings.DEFAULT_TOTAL_FRAMES],
        'width_px': [settings.DEFAULT_WIDTH_PX],
        'width_si': [settings.DEFAULT_WIDTH_SI],
        'time': [settings.DEFAULT_TIME],
        'temperature_C': [settings.DEFAULT_TEMPERATURE_C]
    })

    # trajectories_df = pd.DataFrame(
    #     columns=['file_name', 'trajectory', 'frame', 'x', 'y'])

    # summary_df = pd.DataFrame(
    #     columns=['full_path', 'file_name', 'trajectories', 'valid', 'deff'])

    msg = create_table('app_config', app_config_df)
    msg += f"\n{create_table('diffusivity', diffusivity_df)}"
    msg += f"\n{create_table('analysis_config', analysis_config_df)}"
    msg += f"\n{update_table('analysis_config', analysis_config_df)}"
    # msg += f"\n{create_table('trajectories', trajectories_df)}"
    # msg += f"\n{create_table('summary', summary_df)}"
    # msg += f"\n{update_table('summary', summary_df)}"
    msg += f"\n{drop_table('summary')}"
    msg += f"\n{drop_table('trajectories')}"
    return msg


def update_table(table_name: str, data: pd.DataFrame) -> str:
    """Updates a table based on received DataFrame. Ignores update if pandas \
        detect that the table is already updated.

    Arguments:
        table_name {str} -- Name of the table to be updated.
        data {pd.DataFrame} -- Data to be inserted.
    """

    conn = connect()
    current_table_df = None
    current_table_df = pd.read_sql_table(table_name, con=conn)
    msg = ""
    try:
        if current_table_df.columns.size != data.columns.size:
            for (column, column_data) in data.iteritems():
                if data[column].any() and current_table_df[column].any():
                    data[column] = column_data

            data.to_sql(table_name, con=conn,
                        index=False, if_exists='replace')

            msg = f"Table '{table_name}' updated."
    except KeyError:
        data.to_sql(table_name, con=conn,
                    index=False, if_exists='replace')
        msg = f"Table '{table_name}' updated."
    except Exception:
        msg = "Exception."
    finally:
        current_table_df = None
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
    except Exception:
        msg = "Exception."
    finally:
        return msg


def drop_table(table_name: str) -> str:
    """Drops a table if it extists.

    Arguments:
        table_name {str} -- Name of the table to be dropped.
    """
    conn = connect()
    msg = ""

    try:
        if conn.has_table(table_name):
            conn.execute(
                DropTable(Table(table_name, MetaData())))
            msg = f"Table '{table_name}' dropped."
        else:
            msg = f"Table '{table_name}' not found. Aborting."

    except Exception:
        msg = "Exception."
    finally:
        return msg
