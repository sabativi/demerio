import os
from demerio_utils.file_utils import create_new_dir

"Dir where file will be stored"
demerio_config_dir = os.path.join(os.path.expanduser("~"), ".demerio")
demerio_dir = os.path.join(os.path.expanduser("~"), "demerio")
if not os.path.exists(demerio_dir):
    create_new_dir(demerio_dir)
config_file = os.path.join(demerio_config_dir, "map.demerio")

redundant = 2 ## any 2 of pars can reconstruct

"Trad context : do not really know why there should be multiple for now"
trad_context = "MainWindow"

ui_dir = os.path.join(os.path.dirname(__file__), "ui")

def ui_full_path(ui_filename):
    return os.path.join(ui_dir, ui_filename)

FREQUENCY_CHECK_MS = 5000
BAR_NOTIFICATION_TIME = 2000
TIME_OUT_CALL_S = 3
