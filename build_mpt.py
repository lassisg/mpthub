import subprocess
from os.path import join as path_join
import sys


def main():
    # App related information
    app_name = 'MPTHub'
    icon_path = './ui/resources/icons/node-magnifier.ico'

    # data options (semicolon is path separator on Windows)
    data_options = [
        'README.md;.',
        'LICENSE;.',
        'mpt/assets/*;./mpt/assets/',
        'ui/*;./ui/',
    ]

    # Hidden imports required by trackpy/PySide6
    hidden = [
        'pandas',
        'sqlalchemy.sql.default_comparator',
        'scipy.spatial.transform._rotation_groups',
        'scipy.special.cython_special',
    ]

    # Added '--exclude-module matplotlib' due to build errors
    # Solution from https://rb.gy/qgabep
    subprocess.run(f"{sys.executable} -m PyInstaller \
                    --log-level WARN \
                    --clean -D --noconfirm -w \
                    {' '.join(f'--add-data={opt}' for opt in data_options)} \
                    {' '.join(f'--hidden-import={imp}' for imp in hidden)} \
                    --exclude-module matplotlib \
                    -n {app_name} \
                    -i {icon_path} \
                    app.py",
                   check=True)


if __name__ == '__main__':
    main()
