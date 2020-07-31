# blastomussa
# personal use MacOS
# tkinter GUI download playlists, id3v2 tag update, and auto itunes import
# IT WORKS 6/28/20
# organized 6/29
# py2app not working trouble importing modules, try something else or virtualenv
# might want to change the download button to below the form
# BEST VERSION as of 7/22; needs exception handling
from __future__ import unicode_literals
from youtube_dl import YoutubeDL, DownloadError
from tkinter import Tk, Label, Button, Menu, Entry, StringVar, Toplevel, filedialog, LabelFrame, Frame
from pathlib import Path
from os import path, mkdir, rmdir, remove, listdir, rename
from shutil import move
from re import sub
import eyed3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error

EMPTY=""
ITUNES = "/Users/blastomussa/music/itunes/itunes media/Automatically Add to iTunes.localized"

class DownloaderApp(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Youtube to MP3 GUI")
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # menu bar widgets
        self.menu = Menu(self.master)
        self.filemenu = Menu(self.menu, tearoff=0)
        self.filemenu.add_command(label="Help", command=self.helper)
        self.filemenu.add_command(label="Exit", command=self.master.quit)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.about = Menu(self.menu, tearoff=0)
        self.about.add_command(label="Version 2")
        self.about.add_command(label="About...", command=self.aboutwindow)
        self.menu.add_cascade(label="About", menu=self.about)

        # string vars
        self.url = StringVar()
        self.message = StringVar()
        self.artist = StringVar()
        self.album = StringVar()
        self.art = None
        self.art_text = StringVar()

        # organizing frames
        self.frame1 = Frame(self.master)
        self.frame1.pack(side="bottom", fill="both", expand=True)
        self.frame2 = Frame(self.master)
        self.frame2.pack(side="top", fill="both", expand=True)
        self.frame3 = LabelFrame(self.frame1)
        self.frame3.pack(padx=5,pady=3)

        # user input widget
        self.url_label = Label(self.frame3, text="URL:").grid(row=0,column=0)
        self.url_entry = Entry(self.frame3, width=40, textvariable=self.url).grid(row=0,column=1)
        self.artist_label = Label(self.frame3, text="Artist:").grid(row=1,column=0)
        self.artist_entry = Entry(self.frame3, width=40, textvariable=self.artist).grid(row=1,column=1)
        self.album_label = Label(self.frame3, text="Album:").grid(row=2,column=0)
        self.album_entry = Entry(self.frame3, width=40, textvariable=self.album).grid(row=2,column=1)

        # choose album art widgets
        self.art_button = Button(self.frame3, text="Choose Album Art", command=self.getArt).grid(row=3,column=0)
        self.art_label = Label(self.frame3, textvariable=self.art_text).grid(row=3,column=1)

        # padding around each user input widget
        for child in self.frame3.winfo_children():
            child.grid_configure(padx=5, pady=3)

        # status bar widget; added before download to sticky to bottom first
        self.statusbar = Label(self.frame1, textvariable=self.message, bd=1, relief="sunken", anchor="w")
        self.statusbar.pack(side="bottom", fill="x")
        
        # download button widget
        self.download_button = Button(self.frame2, text="Download", command=self.download)
        self.download_button.pack(side="bottom", padx=5, pady=3)

        self.master.bind('<Return>', self.download)
        self.master.config(menu=self.menu)

    def download(self, *args):
        #### change the direction of slashes for Windows ###
        self.folder = str(Path.home()) + '/Desktop/NewMusic'
        request = str(self.url.get())
        self.artist_text = str(self.artist.get())
        self.album_text = str(self.album.get())

        if request != EMPTY:
            try:
                if path.isdir(self.folder) != True:
                    mkdir(self.folder)
                else:
                    self.remove_temp()
                    mkdir(self.folder)

                output = self.folder + '/%(title)s.%(ext)s'
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output,
                    'progress_hooks': [self.my_hook],
                    'quiet': True,
                    'postprocessors': [
                        {'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192'}]}

                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([request])

                self.add_meta()
                self.itunes_import()

                self.remove_temp()
                if self.art != None:
                    remove(self.art)

                self.url.set(EMPTY)
                self.artist.set(EMPTY)
                self.album.set(EMPTY)
                self.art_text.set(EMPTY)
                self.master.update()
            except DownloadError:
                self.remove_temp()
                string = self.url.get()
                string = "Download Error..." + string + " is not a valid URL."
                self.message.set(string)
                self.url.set(EMPTY)
                self.master.update()

    def my_hook(self, d):
        if d['status'] == 'downloading':
            string = 'Downloading.....' + d['_percent_str']
            self.message.set(string)
            self.master.update()
        elif d['status'] == 'finished':
            string = 'Download Complete....'
            self.message.set(string)
            self.master.update()
        else:
            pass

    def getArt(self):
        # get rid of tilde for WINDOWS
        self.art = filedialog.askopenfilename(initialdir="~/Desktop",  title="Select Image", filetypes=(("jpeg files","*.jpg"),("jpeg files","*.jpeg")))
        self.art_text.set(self.art)

    def itunes_import(self):
        if path.isdir(ITUNES) == True:
            if path.isdir(self.folder) == True:
                for file in listdir(self.folder):
                    #removes unwanted title strings before move
                    #doesnt work right might need to eyed3 title of file
                    # still doesnt work with path rename
                    # need to idv3 the title
                    x = self.artist_text + " - "
                    y = "(Offical Video)"
                    newname = sub(x, EMPTY, file)
                    newname = sub(y, EMPTY, newname)
                    file_path = self.folder + "/" + file
                    new_path = self.folder + "/" + newname
                    rename(file_path,new_path)
                    import_path = ITUNES + '/' + file
                    move(new_path, import_path)

    def remove_temp(self):
        if path.isdir(self.folder) == True:
            for file in listdir(self.folder):
                file_path = self.folder + "/" + file
                remove(file_path)
        rmdir(self.folder)

    def add_meta(self):
        #test artist and album tags with mutagen
        if self.artist != EMPTY:
            for file in listdir(self.folder):
                file_path = self.folder + "/" + file
                audiofile = eyed3.load(file_path)
                audiofile.tag.artist = self.artist_text
                audiofile.tag.save()
        if self.album != EMPTY:
            for file in listdir(self.folder):
                file_path = self.folder + "/" + file
                audiofile = eyed3.load(file_path)
                audiofile.tag.album = self.album_text
                audiofile.tag.save()
        if self.art != None:
            for file in listdir(self.folder):
                file_path = self.folder + "/" + file
                audiofile = MP3(file_path, ID3=ID3)
                audiofile.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(self.art,'rb').read()))
                audiofile.save()

    def helper(self):
        HELP_TEXT = """
        In the case of Errors or Failed Download:

            - Download Location:
                    - downloads are save the iTunes Automatic Import folder
                            - if the song is not in your itunes then the download failed
            - Check video URL:
                    - navigate directly to video/playlist and copy url from the web browser
                    - make sure you are not signed into Youtube Premium premium videos are unsupported
        """

        toplevel = Toplevel()
        label1 = Label(toplevel, text=HELP_TEXT, height=0, width=100, justify='left')
        label1.pack()

    def aboutwindow(self):
        ABOUT = """About"""
        ABOUT_TEXT = """
            Youtube to MP3 Downloader is a GUI interface that allows users to download high
        quality albums from Youtube and other music hosting sites directly to the users desktop.
        For a full list of support sites visit:"""
        SITES ="http://ytdl-org"
        DISCLAIMER = """
        Disclaimer"""
        DISCLAIMER_TEXT = """       Youtube to MP3 Downloader was created using Python 3
        and youtube-dl, an open sourced command line tool. This software is
        protected by the GNU General Public License and as such can be shared freely.
        """
        WARNING = """******* This software comes with no guarantee. Use at your own risk. *******

        Copyright 2011-2020 youtube-dl developers
        """
        toplevel = Toplevel()
        label0 = Label(toplevel, text=ABOUT, height=0, width=100)
        label0.pack()

        label1 = Label(toplevel, text=ABOUT_TEXT, height=0, width=100, justify="left")
        label1.pack()

        label2 = Label(toplevel, text=SITES, fg="blue", cursor="hand2", height=0, width=100)
        label2.pack()

        label3 = Label(toplevel, text=DISCLAIMER, height=0, width=100)
        label3.pack()

        label4 = Label(toplevel, text=DISCLAIMER_TEXT, height=0, width=100, justify="left")
        label4.pack()

        label5 = Label(toplevel, text=WARNING, height=0, width=100)
        label5.pack()

def main():
    root = Tk()
    app = DownloaderApp(master=root)
    app.mainloop()

if __name__ == '__main__':
    main()
