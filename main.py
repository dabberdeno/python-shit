from tkinter import ttk, filedialog, messagebox
import os
import threading
from pytube import YouTube
import requests
from bs4 import BeautifulSoup
import re

class VideoDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Video Downloader")

        
        self.dark_mode = tk.BooleanVar(value=True)

       
        self.header = tk.Label(master, text="Video Downloader", font=("Helvetica", 16, "bold"), pady=10)
        self.header.pack()

      
        self.dark_mode_toggle = tk.Checkbutton(master, text="Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode)
        self.dark_mode_toggle.pack()

        
        self.label = tk.Label(master, text="Enter Video Link:")
        self.label.pack()
        self.entry = tk.Entry(master, width=50)
        self.entry.pack()

        #creating menus
        self.menu_bar = tk.Menu(master)
        master.config(menu=self.menu_bar)

       
        self.create_file_menu()

  
        self.create_source_menu()

        # Download button
        self.download_button = tk.Button(master, text="Download", command=self.download, relief=tk.FLAT)
        self.download_button.pack()

        # Progress bar
        self.progress_bar = ttk.Progressbar(master, length=200, mode="indeterminate", style="green.Horizontal.TProgressbar")
        self.progress_bar.pack()

        # Folder path display
        self.folder_path_label = tk.Label(master, text="", pady=10)
        self.folder_path_label.pack()
        self.remembered_folder_path = None


        style = ttk.Style()
        style.configure("green.Horizontal.TProgressbar", troughcolor="#121212", background="#4CAF50")

        self.canvas = tk.Canvas(master, width=master.winfo_screenwidth(), height=master.winfo_screenheight(), bg="black")
        self.canvas.pack()
        self.matrix_background = MatrixBackground(self.canvas, master.winfo_screenwidth(), master.winfo_screenheight(), symbol_count=150, opacity=0.4)

    def create_file_menu(self):
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Save Folder", command=self.select_save_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.destroy)

    def create_source_menu(self):
        source_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Source", menu=source_menu)
        self.source_var = tk.StringVar(value="YouTube")  # Default source
        sources = ["YouTube", "Facebook", "Twitter", "Instagram"]
        for source_option in sources:
            source_menu.add_radiobutton(label=source_option, variable=self.source_var, value=source_option)

    def toggle_dark_mode(self):
        theme = "dark" if self.dark_mode.get() else "light"
        self.master.tk_setPalette(background="#121212" if theme == "dark" else "#FFFFFF",
                                  foreground="#FFFFFF" if theme == "dark" else "#000000",
                                  activeBackground="#4285F4", activeForeground="white")

    def select_save_folder(self):
        folder_path = filedialog.askdirectory(title="Select Directory to Save Files", initialdir=self.remembered_folder_path)
        if folder_path:
            self.remembered_folder_path = folder_path
            self.folder_path_label.config(text=f"Save Folder: {folder_path}")

    def download(self):
        video_link = self.entry.get()
        save_directory = self.remembered_folder_path or filedialog.askdirectory(title="Select Directory to Save Files")

        if video_link and save_directory:
            source_choice = self.source_var.get()

            download_thread = threading.Thread(target=self.download_video, args=(video_link, save_directory, source_choice))
            download_thread.start()

    def download_video(self, link, save_path, source):
        try:
            if source == "YouTube":
                youtube_video = YouTube(link)
                video_stream = youtube_video.streams.filter(file_extension="mp4", progressive=True).first()
                video_stream.download(save_path)
                downloaded_file = f"{youtube_video.title}.mp4"

            else:
                video_url = self.get_video_url(link, source)
                response = requests.get(video_url)
                file_name = f"{source.lower()}_video.mp4"
                with open(os.path.join(save_path, file_name), 'wb') as f:
                    f.write(response.content)
                downloaded_file = file_name

            self.progress_bar.start()
            self.progress_bar.stop()
            messagebox.showinfo("Success", f"Video downloaded: {os.path.join(save_path, downloaded_file)}")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request Error: {e}")

        except Exception as e:
            messagebox.showerror("Error", f"Download Error: {e}")

    def get_video_url(self, link, source):
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')

        if source == "Facebook":
            video_data = soup.find('script', {'type': 'application/ld+json'}).text
            video_url = re.search(r'"contentUrl": "(.+?)"', video_data).group(1)
        elif source == "Twitter":
            video_url = soup.find('meta', {'property': 'og:video'})['content']
        elif source == "Instagram":
            video_url = soup.find('meta', {'property': 'og:video'})['content']
        else:
            raise ValueError("Invalid source")

        return video_url


class MatrixBackground:
    def __init__(self, canvas, width, height, symbol_count=100, opacity=0.4):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.symbols = [chr(i) for i in range(0x30a1, 0x30ff + 1)] + [str(i) for i in range(1, 11)] + [" " * i for i in range(1, 11)]
        self.symbol_count = symbol_count
        self.opacity = opacity
        self.matrix_stream = []

        self.generate_matrix_stream()
        self.animate_matrix()

    def generate_matrix_stream(self):
        for _ in range(self.symbol_count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            speed = random.uniform(1, 5)
            symbol = random.choice(self.symbols)
            self.matrix_stream.append({"x": x, "y": y, "speed": speed, "symbol": symbol})

    def animate_matrix(self):
        self.canvas.delete("matrix_text")
        for symbol_info in self.matrix_stream:
            x, y, speed, symbol = symbol_info.values()
            self.canvas.create_text(x, y, text=symbol, font=("Courier", 12), fill=f"#00FF00", tags="matrix_text")

            symbol_info["y"] = (y + speed) % self.height

        self.canvas.after(50, self.animate_matrix)


if __name__ == "__main__":
    import random

    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()
