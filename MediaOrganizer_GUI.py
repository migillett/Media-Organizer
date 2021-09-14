from functions.RAW_to_JPEG import raw_to_jpeg

from threading import Thread
from shutil import copy
from time import ctime
from datetime import datetime
import logging
import os
from sys import exit

try:
    from tkinter import *
    from tkinter import messagebox, ttk, filedialog, scrolledtext
    from tkinter.ttk import Progressbar
except ImportError as e:
    logging.error(f'ERROR: {e}')
    exit('Please install tkinter using pip3 install tkinter')


class TextHandler(logging.Handler):
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


class App(Tk):
    def __init__(self, title):
        super(App, self).__init__()

        self.photo_ext = ('.jpg', '.jpeg', '.JPG', '.JPEG', '.png', '.PNG')
        self.raw_photo_ext = ('.CR2', '.ARW', '.NEF', '.CRW', '.DNG', '.TIF')
        self.video_ext = ('.mov', '.m4v', '.mp4', '.wmv', '.wma', '.avi', '.MOV', '.MPG')

        self.photo_count = 0
        self.video_count = 0
        self.total_media = 0
        self.processed_media = 0

        self.title(title)

        padding = 8
        entry_width = 80

        self.source_dir = StringVar(self, value='')
        self.dest_dir = StringVar(self, value='')

        self.rename_enable = BooleanVar(self, value=False)
        self.convert_raw = BooleanVar(self, value=False)

        self.total_files = 0
        self.total_dirs = 0

        self.start_gui(padding, entry_width)


    def count_media_files(self):
        # counts all of the media files in the root folder (used later for pbar)
        self.photo_count = 0
        self.video_count = 0
        self.total_media = 0
        self.processed_media = 0

        logging.info('Starting folder analysis...')

        for root, _, files in os.walk(self.source_dir):
            for file in files:
                filename = os.path.join(root, file)

                if filename.endswith(self.photo_ext) or filename.endswith(self.raw_photo_ext):
                    self.photo_count += 1

                elif filename.endswith(self.video_ext):
                    self.video_count += 1

        self.total_media = self.photo_count + self.video_count
        logging.info(f'Analysis complete. {self.photo_count} photos and {self.video_count} videos found.')
        

    # returns the year and full date of file creation
    def date_created(self, file):
        c_time = ctime(os.path.getmtime(file))
        formatted_time = str(datetime.strptime(c_time, "%a %b %d %H:%M:%S %Y"))
        date = formatted_time.split(' ')[0]
        year = date.split('-')[0]
        return year, date


    # makes sure the directory in question exists. If not, make it
    def check_dir(self, directory):
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except PermissionError:
                logging.error(f'Insufficient permissions to create directory at: {directory}')


    def copy_media(self, filename, source_path, destination_path, destination_folder):
        if not source_path.startswith('.'):
            # make sure the path you want to save to exists (for organization purposes)
            self.check_dir(destination_folder)

            # If the file doesn't already exist, copy it.
            if not os.path.exists(destination_path):
                copy(source_path, destination_path)
                logging.info(f'Copied file: {filename}')
            else:
                logging.info(f'File skipped: {filename}')

            self.processed_media += 1


    def start_gui(self, padding, entry_width):
        # Source
        source_frame = ttk.LabelFrame(self, text='Source Directory')
        source_frame.grid(column=0, row=0, padx=padding, pady=padding, columnspan=2, sticky='EW')

        select_source_button = ttk.Button(source_frame, text='Browse', command=self.browse_source)
        select_source_button.grid(column=0, row=0, padx=padding, pady=padding)

        self.source_entry = Entry(source_frame, textvariable=self.source_dir, width=entry_width)
        self.source_entry.grid( column=1, row=0, padx=padding)
        
        # Destination
        dest_frame = ttk.LabelFrame(self, text='Destination Directory')
        dest_frame.grid(column=0, row=1, padx=padding, pady=padding, columnspan=2, sticky='EW')

        select_dest_button = ttk.Button(dest_frame, text='Browse', command=self.browse_destination)
        select_dest_button.grid(column=0, row=0, padx=padding, pady=padding)

        self.dest_entry = Entry(dest_frame, textvariable=self.dest_dir, width=entry_width)
        self.dest_entry.grid( column=1, row=0, padx=padding)

        # Options
        opt_frame = ttk.LabelFrame(self, text='Options')
        opt_frame.grid(column=0, row=2, columnspan=2, padx=padding, pady=padding, sticky='EW')

            # rename files enable
        self.rename_checkbox = Checkbutton(opt_frame, text='Rename Files', variable=self.rename_enable, onvalue=True, offvalue=False)
        self.rename_checkbox.grid(column=0, row=0)

            # convert raw images to jpeg
        self.convert_raw_checkbox = Checkbutton(opt_frame, text='Convert RAW Images', variable=self.convert_raw, onvalue=True, offvalue=False)
        self.convert_raw_checkbox.grid(column=1, row=0)

        # Logs frame
        log_frame = ttk.LabelFrame(self, text='Status')
        log_frame.grid(column=0, row=3, columnspan=2, padx=padding, pady=padding, sticky='EW')

            # logs
        st = scrolledtext.ScrolledText(log_frame)
        st.grid(sticky='EW')
        text_handler = TextHandler(st)
        logging.basicConfig(
            filename='media_organize.log',
            level=logging.INFO)

        logger = logging.getLogger()
        logger.addHandler(text_handler)

        # # Progress Frame
        # progress_frame = ttk.LabelFrame(self, text='Progress')
        # progress_frame.grid(column=0, row=4, columnspan=2, padx=padding, pady=padding, sticky='EW')
        # progress_frame.grid_columnconfigure(0, weight=1)

        #     # Progress Bar
        # self.pbar = Progressbar(progress_frame, orient=HORIZONTAL, length=self.total_media, mode='determinate')
        # self.pbar.grid(column=0, row=0, sticky='EW', pady=padding, padx=padding)

        # Begin button
        start_button = ttk.Button(self, text='Start', command=self.start)
        start_button.grid(column=0, row=11, pady=padding, sticky='E')

        # Cancel button
        cancel_button = ttk.Button(self, text='Exit', command=self.onExit)
        cancel_button.grid(column=1, row=11, pady=padding, sticky='W')


    def browse_source(self):
        self.source_dir = filedialog.askdirectory(initialdir=self.source_dir, title='Select Source Directory')
        self.source_entry.delete(0, END)
        self.source_entry.insert(0, self.source_dir)
        

    def browse_destination(self):
        self.dest_dir = filedialog.askdirectory(initialdir=self.source_dir, title='Select Destination Directory')
        self.dest_entry.delete(0, END)
        self.dest_entry.insert(0, self.dest_dir)


    def start(self):
        logging.info('=====================================================\n')

        self.source_dir = self.source_entry.get()
        self.dest_dir = self.dest_entry.get()

        if self.source_dir == '' or self.dest_dir == '':
            logging.error('ERROR: Please specify source and destination folders.')
            messagebox.showerror('Error', 'Please specify source and destination folders.')

        elif self.source_dir == self.dest_dir:
            logging.error('ERROR: Source directory and destination directory cannot be the same.')
            messagebox.showerror('Error', 'Source directory and destination directory cannot be the same.')

        else:
            self.count_media_files()

            logging.info(f'Source folder: {self.source_dir}\nDestination folder: {self.dest_dir}')
            logging.info(f'RAW image conversion set to {self.convert_raw.get()}')
            logging.info(f'File renaming set to {self.rename_enable.get()}')

            logging.info('Starting file copy')

            for root, dirs, files in os.walk(self.source_dir):
                for file in files:

                    filename_source = os.path.join(root, file)
                    y, date = self.date_created(filename_source)
                    final_folder = os.path.join(self.dest_dir, y)

                    # rename the media if the checkbox is enabled
                    if self.rename_enable.get():
                        new_media_name = os.path.join(final_folder, f'{date}_{file}')
                    else:
                        new_media_name = os.path.join(final_folder, file)

                    ### COPY PHOTOS
                    if filename_source.endswith(self.photo_ext):
                        t = Thread(target=self.copy_media(file, filename_source, new_media_name, final_folder))
                        t.start()

                    ### COPY RAW IMAGES
                    elif filename_source.endswith(self.raw_photo_ext):

                        if self.convert_raw.get(): # if the checkbox is enabled, convert the raw image into jpeg
                            self.check_dir(final_folder)
                            t = Thread(target=raw_to_jpeg(filename_source, final_folder))
                            self.processed_media += 1

                        else:
                            t = Thread(target=self.copy_media(file, filename_source, new_media_name, final_folder))

                        t.start()

                    ### COPY VIDEOS
                    elif filename_source.endswith(self.video_ext):
                        t = Thread(target=self.copy_media(file, filename_source, new_media_name, final_folder))
                        t.start()

                    # self.pbar['value'] = self.processed_media
                    self.update()
            
            logging.info(f'\nFile copy complete. {self.processed_media} media files copied.\n\n=====================================================\n')
            messagebox.showinfo('Success!', 'File copy complete.')


    def onExit(self):
        logging.info('Quitting...')
        exit()


if __name__ == '__main__':
    app = App(title='Media Organizer')
    app.mainloop()
