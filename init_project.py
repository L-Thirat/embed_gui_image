import os


def create_folders():
    """ Generate folders for this project """
    if not os.path.exists('output/original'):
        os.makedirs('output/original')
    if not os.path.exists('output/compare'):
        os.makedirs('output/compare')
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists('log'):
        os.makedirs('log')


def init_dir(basedir, sub_dir):
    # init directory
    if not os.path.exists(basedir + sub_dir):
        os.makedirs(basedir + sub_dir)


def init_param():
    params = {
        "load_data": {
            "file_path_o": "",
            "file_path_c": "",
            "tk_photo_line": None,
            "tk_photo_org": None,
            "tk_photo_cp": None,
            "load_img_o": None,
            "load_img_cp": None,
            "load_filename": None,
            "raw_data_draw": {
                "filename": "",
                "detect": [],
                "inside": [],
                "area": [],
            },
        },
        "output_display": {
            "error_box": {},
            "error_line": {}
        },
        "drawing": {
            "drawing_data": {
                "detect": {
                    "color": "yellow",
                    "prev": [],
                    "polygon": [],
                    "temp_pol": [],
                },
                "inside": {
                    "color": "blue",
                    "prev": [],
                    "polygon": [],  # line
                    "temp_pol": [],  # not use
                },
                "area": {
                    "color": "red",
                    "prev": [],
                    "polygon": [],
                    "temp_pol": [],
                }
            },
            "prev_sub_pol": [],
            "count_draw_sub_pol": 0,
            "start_x": None,
            "start_y": None,
            "range_rgb": [{
                "point": None,
                "min": [255, 255, 255],
                "max": [0, 0, 0]
            }]
        },
        "status": {
            "save_status": False,
            "mode": "detect",
        }
    }
    return params
