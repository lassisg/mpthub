import subprocess
from os.path import join as path_join
from os import sep


def main():
    env_path = "D:/virtualenvs/mpt-CrFBuUTO-py3.8"
    paths = f'{env_path}/Lib/site-packages'

    data_options = [
        'README.md;.',
        'LICENSE;.',
        'mpt/assets/*;./mpt/assets/',
        'ui/*;./ui/',
        # 'platforms/*;./platforms/'
        f'{paths}/PySide6/plugins/platforms/*;./platforms/'
    ]
    # The following hidden-import were added only because of TrackPy
    hidden = [
        'pandas',
        'sqlalchemy.sql.default_comparator',
        'scipy.spatial.transform._rotation_groups',
        'scipy.special.cython_special'
    ]
    app_name = 'MPT_Analysis'
    # icon_path = './mpt/assets/icon.ico'
    icon_path = './ui/resources/icons/node-magnifier.ico'

    # subprocess.run(f"python -m PyInstaller --clean -D --noconfirm \
    #                 --paths={path_libs} \
    #                 --debug=all \
    #                 --debug=imports \
    subprocess.run(f"python -m PyInstaller --clean -D --noconfirm -w \
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
                    -n {app_name} \
                    -i {icon_path} \
                    app.py")


if __name__ == '__main__':
    main()
