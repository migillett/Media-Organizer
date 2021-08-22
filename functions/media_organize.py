#!/usr/bin/python3

import os
from shutil import copy
from datetime import datetime
from time import ctime
import logging
from functions.RAW_to_JPEG import raw_to_jpeg

# CONFIG HERE ####################################
# replace these with as many directories as you wish

source_dir = [
  'source/dir1',
  'source/dir2'
]

dest_dir = 'destination/dir'

# CODE BEGINS HERE ###############################

def date_created(file):
    c_time = ctime(os.path.getmtime(file))
    formatted_time = str(datetime.strptime(c_time, "%a %b %d %H:%M:%S %Y"))
    date = formatted_time.split(' ')[0]
    year = date.split('-')[0]
    return year, date


def check_dir(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except PermissionError:
            logging.error(f'Insufficient permissions to create directory at: {directory}')


def file_copy(source, destination, export_directory):
    # If the files starts with a . ignore it. Don't know how it sees them anyway
    if not source.startswith('.'):

        # see if the export directory exists. If not, make it.
        check_dir(export_directory)

        # If the file doesn't already exist, copy it.
        if not os.path.exists(destination):
            copy(source, destination)
            logging.info(f'Copied file: {source}')
        else:
            logging.info(f'File skipped: {source}')


def media_organize(source, destination, rename=False, convert_raw=False):
    # rename allows for the program to pull the file modification date and add it to the start of the filename.
        # disabled by default
    logging.info(f'\nFile renaming is set to: {rename}')

    # this allows you to mass-convert RAW images to JPEG.
        # disabled by default
    logging.info(f'Converting RAW images to JPEG is set to: {convert_raw}\n')

    # extensions to search for in the directories
    photo_ext = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')
    raw_photo_ext = ('.CR2', '.ARW', '.NEF', '.CRW', '.DNG', '.TIF')
    video_ext = ('.mov', '.m4v', '.mp4', '.wmv', '.wma', '.avi', '.MOV', '.MPG')

    photos = 0
    videos = 0

    # walk through each directory and see what's in there
    for root, dirs, files in os.walk(source):
        for name in files:
            filename = os.path.join(root, name)
            y, date = date_created(filename)

            if filename.endswith(photo_ext):
                final_folder = os.path.join(destination, 'photos', y)

                if rename:
                    new_photo = os.path.join(final_folder, f'{date}_{name}')
                else:
                    new_photo = os.path.join(final_folder, name)

                file_copy(filename, new_photo, final_folder)
                photos += 1

            elif filename.endswith(raw_photo_ext) and convert_raw:
                final_folder = os.path.join(destination, 'photos', y)
                check_dir(final_folder)
                raw_to_jpeg(source_file=filename, destination_folder=final_folder)
                photos += 1


            elif filename.endswith(video_ext):
                video_dir = os.path.join(destination, 'videos', y)

                if rename:
                    new_video = os.path.join(video_dir, f'{date}_{name}')
                else:
                    new_video = os.path.join(video_dir, name)

                file_copy(filename, new_video, video_dir)
                videos += 1

    logging.info(f'\nAll media gathered from {source}')
    logging.info(f'{photos} photos copied | {videos} videos copied')


if __name__ == '__main__':
    for source in source_dir:
        media_organize(source, dest_dir)
