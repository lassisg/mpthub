import subprocess


def main():
    data_options = [
        'README.md;.',
        'LICENSE;.',
        'mpt/assets/*;./mpt/assets/']
    app_name = 'MPT_Analysis'
    icon_path = './mpt/assets/icon.ico'

    subprocess.run(f"python -m PyInstaller --clean -D --noconfirm -w \
                    --add-data={data_options[0]} \
                    --add-data={data_options[1]} \
                    --add-data={data_options[2]} \
                    -n {app_name} -i {icon_path} app.py")
