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
