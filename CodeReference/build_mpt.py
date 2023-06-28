import subprocess
from os.path import join as path_join
import sys


def main():
    # App related information
    app_name = 'MPTHub'
    icon_path = './ui/resources/icons/node-magnifier.ico'
    env_path = sys.exec_prefix
    paths = f'{env_path}/Lib/site-packages'
    data_options = [
        'README.md;.',
        'LICENSE;.',
        'mpt/assets/*;./mpt/assets/',
        'ui/*;./ui/',
        f'{paths}/PySide6/plugins/platforms/*;./platforms/'
    ]

    # The following hidden-import were added only because of TrackPy
    hidden = [
        'pandas',
        'sqlalchemy.sql.default_comparator',
        'scipy.spatial.transform._rotation_groups',
        'scipy.special.cython_special'
    ]

    # subprocess.run(f"python -m PyInstaller --clean -D --noconfirm \
    #                 --paths={path_libs} \
    #                 --debug=all \
    #                 --debug=imports \
    #                 --log-level DEBUG \

    # Added '--exclude-module matplotlib' due to build errors
    # Solution from https://rb.gy/qgabep
    subprocess.run(f"{sys.executable} -m PyInstaller \
                    --log-level WARN \
                    --clean -D --noconfirm -w \
                    --paths={paths} \
                    --add-data={data_options[0]} \
                    --add-data={data_options[1]} \
                    --add-data={data_options[2]} \
                    --add-data={data_options[3]} \
                    --add-data={data_options[4]} \
                    --hidden-import={hidden[0]} \
                    --hidden-import={hidden[1]} \
                    --hidden-import={hidden[2]} \
                    --hidden-import={hidden[3]} \
                    --exclude-module matplotlib \
                    -n {app_name} \
                    -i {icon_path} \
                    app.py")


if __name__ == '__main__':
    main()
