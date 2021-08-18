import tkinter as tk
from tkinter import filedialog
import tkinter.font as fnt
from typing import *
import youtube_dl
import threading

CHOOSE_FORMAT_OPTION = 'Use format option on the right.'
CHOOSE_ALL_VIDEOS = 'Choose all videos.'
PLAYLIST_SPECIAL_OPTS_N = 1

TEST_URL = 'https://www.youtube.com/watch?v=BaW_jenozKc'

class URLFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        font_normal = fnt.Font(size=12)
        self.label_info = tk.Label(self, text='', font=font_normal)
        self.label_info.grid(column=0, row=0, columnspan=2, padx=10, sticky=tk.W)
        self.label_url = tk.Label(self, text='URL:', font=font_normal)
        self.label_url.grid(column=0, row=1, padx=10, sticky=tk.E)
        self.entry_url = tk.Entry(self, font=font_normal)
        self.entry_url.grid(column=1, row=1, sticky=tk.W, ipady=5, ipadx=200)

        self.btn_submiturl = tk.Button(self, text='Submit!', font=font_normal, bg='yellow')
        self.btn_submiturl.grid(column=2, row=1, padx=20)
    def registerURLSubmitBtnCmd(self, func):
        self.btn_submiturl['command'] = func
    def getURL(self):
        return self.entry_url.get()
    def changeInfoLabel(self, s):
        self.label_info['text'] = s

class ListFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        font_normal = fnt.Font(size=12)
        self.label_lsbx = tk.Label(self, text='Viable options', font=font_normal)
        self.label_lsbx.grid(column=0, row=0, pady=5, padx=10, sticky=tk.W)
        self.lsbx = tk.Listbox(self)
        self.lsbx.grid(column=0, row=1, ipady=100, ipadx=100, padx=10, pady=10, sticky=tk.W)
        self.is_display_playlist = False

    def displayInfo(self, info, is_playlist):
        self.lsbx.delete(0, tk.END)
        self.is_display_playlist = is_playlist
        if is_playlist:
            self.label_lsbx['text'] = 'Playlist contains:'
            self.displayPlaylistNames(info)
        else:
            self.label_lsbx['text'] = 'Format options:'
            self.displayVideoFormats(info)

    def displayPlaylistNames(self, playlist_info):
        self.lsbx['selectmode'] = 'multiple'
        self.lsbx.insert(tk.END, CHOOSE_ALL_VIDEOS)
        self.lsbx.insert(
            tk.END, *[video['title'] for video in playlist_info['entries']]
        )
        self.lsbx.select_set(0)
    def displayVideoFormats(self, video_info):
        # same as ydl.list_formats(video_info), but with custom option
        self.lsbx['selectmode'] = 'browse'
        self.lsbx.insert(tk.END, CHOOSE_FORMAT_OPTION)
        with youtube_dl.YoutubeDL() as ydl:
            formats = video_info.get('formats')
            table = [
                [f['format_id'], f['ext'], ydl.format_resolution(f), ydl._format_note(f)]
                for f in formats
                if f.get('preference') is None or f['preference'] >= -1000]
            if len(formats) > 1:
                table[-1][-1] += (' ' if table[-1][-1] else '') + '(best)'
            table = [', '.join(row) for row in table]
            self.lsbx.insert(tk.END, *table)
        self.lsbx.select_set(0)
        
    def getSelectedFormatNumber(self):
        # used for download video
        if self.is_display_playlist:
            raise Exception('Now displaying playlist!')
        s = self.lsbx.get(self.lsbx.curselection()[0])
        try: return int(s.split(',')[0])
        except: return s
    
    def getSelectedURLs(self, playlist_info):
        # used for download playlist
        if not self.is_display_playlist:
            raise Exception('Now displaying single video!')
        select_ls = self.lsbx.curselection()
        if 0 in select_ls:  # choose all. Also not a good design practice
            url_ls = [
                video['webpage_url']
                for video in playlist_info['entries']
            ]
        else:
            url_ls = [
                playlist_info['entries'][i-PLAYLIST_SPECIAL_OPTS_N]['webpage_url']
                for i in select_ls
            ]
        return url_ls
        

class SettingFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.setting_subframe = []
        self.createWidgets()

    def createWidgets(self):
        self.formatfrm = SettingFormatSubframe(self)
        self.addSubframe(self.formatfrm)

        self.fnamefrm = SettingFilenameSubframe(self)
        self.addSubframe(self.fnamefrm)

    def addSubframe(self, subframe):
        subframe.grid(column=0, row=len(self.setting_subframe))
        self.setting_subframe.append(subframe)
        
    def getFormatOptions(self):
        d = dict()
        for subframe in self.setting_subframe:
            d.update(subframe.getFormatOptions())
        return d

    def getDownloadSpecificOptions(self):
        d = dict()
        for subframe in self.setting_subframe:
            d.update(subframe.getDownloadSpecificOptions())
        return d

class SettingFormatSubframe(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        font_normal = fnt.Font(size=12)
        self.label_fmt = tk.Label(self, text='Format:', font=font_normal)
        self.label_fmt.grid(column=0, row=0, sticky=tk.W)
        self.entry_fmt = tk.Entry(self, font=font_normal)
        self.entry_fmt.grid(column=1, row=0, sticky=tk.W, ipady=5, ipadx=150, padx=10)
    def getFormatOptions(self):
        d = dict()
        if self.entry_fmt.get() != '':
            d.update({'format': self.entry_fmt.get()})
        return d
    def getDownloadSpecificOptions(self):
        return dict()

class SettingFilenameSubframe(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        font_normal = fnt.Font(size=12)
        self.label_fname = tk.Label(self, text='Filename:', font=font_normal)
        self.label_fname.grid(column=0, row=0, sticky=tk.W)
        self.entry_fname = tk.Entry(self, font=font_normal)
        self.entry_fname.grid(column=1, row=0, sticky=tk.W, ipady=5, ipadx=150, padx=10)
        self.entry_fname.insert(0, '%(title)s-%(id)s.%(ext)s')

        self.folderfrm = tk.Frame(self)
        self.folderfrm.grid(column=0, row=1, columnspan=2, sticky=tk.W)
        self.label_folder = tk.Label(self.folderfrm, text='Folder:', font=font_normal)
        self.label_folder.grid(column=0, row=0, sticky=tk.E)
        self.btn_folder = tk.Button(self.folderfrm, text='Choose', command=self.onClickBtnFolder)
        self.btn_folder.grid(column=1, row=0, sticky=tk.W, padx=50)
        self.folder = ''
    def onClickBtnFolder(self):
        self.folder = filedialog.askdirectory()
        self.label_folder['text'] = 'Folder: ' + self.folder
    def getFormatOptions(self):
        return dict()
    def getDownloadSpecificOptions(self):
        if self.folder == '':
            raise Exception('Need to choose folder!')
        if self.entry_fname.get() == '':
            raise Exception('Need to have nonempty filename!')
        return {'outtmpl': f'{self.folder}/{self.entry_fname.get()}'}

class DownloadFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        font_normal = fnt.Font(size=12)
        self.label_info = tk.Label(self, text='', font=font_normal)
        self.label_info.grid(column=0, row=0, padx=10, sticky=tk.E)
        self.btn_download = tk.Button(self, text='Download!', font=font_normal, bg='yellow')
        self.btn_download.grid(column=0, row=1, padx=10, pady=10, ipady=5, ipadx=20, sticky=tk.E)
    def registerDownloadBtnCmd(self, func):
        self.btn_download['command'] = func
    def changeInfoLabel(self, s):
        self.label_info['text'] = s

class MainFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.resizeToWindow()
        self.hideResultFrames()

    def createWidgets(self):
        font_title = fnt.Font(size=32, family="Courier new")
        font_normal = fnt.Font(size=12)
        self.background_frame = tk.Frame(self)

        self.label_title = tk.Label(self, text='Youtube Downloader', font=font_title)
        self.label_title.grid(column=0, row=0, columnspan=3, padx=10, sticky=tk.W)

        self.urlfrm = URLFrame(self)
        self.urlfrm.grid(column=0, row=1, columnspan=2, pady=20, sticky=tk.W)
        self.urlfrm.registerURLSubmitBtnCmd(self.onClickSubmitURLBtn)

        self.lsfrm = ListFrame(self)
        self.lsfrm.grid(column=0, row=2, rowspan=2, sticky=tk.W)
        
        self.settingfrm = SettingFrame(self)
        self.settingfrm.grid(column=1, row=2, sticky=tk.W+tk.N)

        self.dlfrm = DownloadFrame(self)
        self.dlfrm.grid(column=1, row=3, sticky=tk.S+tk.E)
        self.dlfrm.registerDownloadBtnCmd(self.onClickDownloadBtn)

        self.cur_url = None
        self.is_playlist = None

    def resizeToWindow(self):
        self.master.update()
        self.master.geometry(f'{self.winfo_width()}x{self.winfo_height()}')

    def hideResultFrames(self):
        self.lsfrm.grid_remove()
        self.settingfrm.grid_remove()
        self.dlfrm.grid_remove()
    
    def showResultFrames(self):
        # can be called multiple times without issue
        self.lsfrm.grid()
        self.settingfrm.grid()
        self.dlfrm.grid()

    def onClickSubmitURLBtn(self):
        self.urlfrm.changeInfoLabel('Checking...')
        url = self.urlfrm.getURL()
        if not self.isSupportedURL(url):
            self.urlfrm.changeInfoLabel('URL not valid!')
            return

        is_success, info = self.tryToGetInfo(dict(), url)

        if not is_success:
            self.urlfrm.changeInfoLabel("Can't get info!")
            return
        
        self.showResultFrames()
        self.cur_url = url
        self.is_playlist = self.isPlaylist(info)

        self.lsfrm.displayInfo(info, self.is_playlist)

        if self.is_playlist:
            self.playlist_info = info
            self.urlfrm.changeInfoLabel(f'Done! Loaded playlist: {info["title"]}')
        else:
            self.urlfrm.changeInfoLabel(f'Done! Loaded playlist: {info["title"]}')

    def isSupportedURL(self, url):
        # https://stackoverflow.com/questions/61465405/how-to-check-if-a-url-is-valid-that-youtube-dl-supports
        extractors = youtube_dl.extractor.gen_extractors()
        for e in extractors:
            if e.suitable(url) and e.IE_NAME != 'generic':
                return True
        return False

    def tryToGetInfo(self, ydl_opts, url):
        info_dict = None
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
        except:
            return False, None
        return True, info_dict

    def isPlaylist(self, info):
        return 'entries' in info.keys()

    def isFormatValidForURL(self):
        # This testing method will include format number not found, etc.
        ydl_opts = self.settingfrm.getFilterOptions()
        is_success, info = self.tryToGetInfo(ydl_opts, self.cur_url)
        return is_success

    def onClickDownloadBtn(self):
        # using stored url & stuff to do things
        if self.cur_url == None:
            raise Exception('There are no URLs to download!')
        try:
            if self.is_playlist:
                self.downloadPlaylist()
            else:
                self.downloadVideo()
        except Exception as e:
            self.dlfrm.changeInfoLabel(str(e))
            return
        self.dlfrm.changeInfoLabel('Download registered! Start another thread to download...')

    def downloadPlaylist(self):
        # get chosen video
        url_ls = self.lsfrm.getSelectedURLs(self.playlist_info)
        ydl_opts = self.settingfrm.getDownloadSpecificOptions()
        ydl_opts.update(self.settingfrm.getFormatOptions())

        if not self.tryToGetInfo(ydl_opts, TEST_URL)[0]:
            raise Exception('Something went wrong with setting!')

        thr = threading.Thread(
            target=self.threadDownloadVideo, args=[ydl_opts, url_ls]
        )
        thr.setDaemon(True)
        thr.start()

    def downloadVideo(self):
        # get chosen video
        ydl_opts = self.settingfrm.getDownloadSpecificOptions()
        fmt_num = self.lsfrm.getSelectedFormatNumber()

        # TODO: not a good design practice: violates OCP & DIP
        if fmt_num == CHOOSE_FORMAT_OPTION:
            ydl_opts.update(self.settingfrm.getFormatOptions())
        else:
            ydl_opts.update({'format': str(fmt_num)})

        if not self.tryToGetInfo(ydl_opts, TEST_URL)[0]:
            raise Exception('Something went wrong with setting!')
        
        thr = threading.Thread(
            target=self.threadDownloadVideo, args=[ydl_opts, [self.cur_url]]
        )
        thr.setDaemon(True)
        thr.start()
    
    def threadDownloadVideo(self, ydl_opts, url_ls):
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(url_ls)
            self.dlfrm.changeInfoLabel('Download success!')
        except Exception as e:
            self.dlfrm.changeInfoLabel('Download went wrong...!\n' + str(e))
        

root = tk.Tk()
frm = MainFrame(root)
root.title('Youtube Downloader')
frm.mainloop()

