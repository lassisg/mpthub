import subprocess


def main():
    data_options = [
        'README.md;.',
        'LICENSE;.',
        'mpt/assets/*;./mpt/assets/'
    ]
    # The following hidden-import were added only because of TrackPy
    hidden = [
        'scipy.spatial.transform._rotation_groups',
        'scipy.special.cython_special'
    ]
    app_name = 'MPT_Analysis'
    icon_path = './mpt/assets/icon.ico'

    # subprocess.run(f"python -m PyInstaller --clean -D --noconfirm \
    subprocess.run(f"python -m PyInstaller --clean -D --noconfirm -w \
                    --add-data={data_options[0]} \
                    --add-data={data_options[1]} \
                    --add-data={data_options[2]} \
                    --hidden-import={hidden[0]} \
                    --hidden-import={hidden[1]} \
                    -n {app_name} -i {icon_path} app.py")
