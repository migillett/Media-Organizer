from media_organize import media_organize
import logging
import os
from sys import exit

try:
    from tkinter import *
    from tkinter import messagebox, ttk, filedialog, scrolledtext
except ImportError as e:
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
        self.title(title)

        padding = 8
        entry_width = 80

        self.source_dir = StringVar(self, value='')
        self.dest_dir = StringVar(self, value='')

        self.total_files = 0
        self.total_dirs = 0

        self.start_gui(padding, entry_width)

        
    def start_gui(self, padding, entry_width):
        # Source
        source_frame = ttk.LabelFrame(self, text='Source')
        source_frame.grid(column=0, row=0, padx=padding, pady=padding, columnspan=2)

        select_source_button = ttk.Button(source_frame, text='Browse', command=self.browse_source)
        select_source_button.grid(column=0, row=0, padx=padding, pady=padding)

        self.source_entry = Entry(source_frame, textvariable=self.source_dir, width=entry_width)
        self.source_entry.grid( column=1, row=0, padx=padding)
        
        # Destination
        dest_frame = ttk.LabelFrame(self, text='Destination')
        dest_frame.grid(column=0, row=1, padx=padding, pady=padding, columnspan=2)

        select_dest_button = ttk.Button(dest_frame, text='Browse', command=self.browse_destination)
        select_dest_button.grid(column=0, row=0, padx=padding, pady=padding)

        self.dest_entry = Entry(dest_frame, textvariable=self.dest_dir, width=entry_width)
        self.dest_entry.grid( column=1, row=0, padx=padding)

        # logs
        st = scrolledtext.ScrolledText(self)
        st.grid(column=0, row=2, columnspan=2, sticky='EW')
        text_handler = TextHandler(st)
        logging.basicConfig(
            filename='media_organize.log',
            level=logging.INFO)

        logger = logging.getLogger()
        logger.addHandler(text_handler)

        # Begin button
        start_button = ttk.Button(self, text='Start', command=self.start)
        start_button.grid(column=0, row=3, pady=padding, sticky='E')

        # cancel button
        cancel_button = ttk.Button(self, text='Exit', command=self.onExit)
        cancel_button.grid(column=1, row=3, pady=padding, sticky='W')

    def browse_source(self):
        self.source_dir = filedialog.askdirectory(initialdir=self.source_dir, title='Select Source Directory')
        self.source_entry.insert(0, self.source_dir)
        
    def browse_destination(self):
        self.dest_dir = filedialog.askdirectory(initialdir=self.source_dir, title='Select Destination Directory')
        self.dest_entry.insert(0, self.dest_dir)

    def start(self):
        source = self.source_entry.get()
        destination = self.dest_entry.get()

        if source == '' or destination == '':
            messagebox.showerror('Error', 'Please specify source and destination directories')

        else:
            logging.info(f'Source folder: {source}\nDestination folder: {destination}')
            logging.info('Starting folder analysis...')
            for _, dirs, files in os.walk(self.source_dir):
                self.total_files += len(files)
                self.total_dirs += len(dirs)
            logging.info(f'\nAnalysis Complete - Total Files: {self.total_files} | Directories: {self.total_dirs}\n')
            logging.info('Starting file copy')
            media_organize(source=self.source_dir, destination=self.dest_dir)


    def onExit(self):
        exit()


if __name__ == '__main__':
    app = App(title='Media Organizer V0.1')
    app.mainloop()
