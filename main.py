import tkinter as tk
from tkinter import ttk
import webbrowser
import threading

def main():
    app = Application()
    app.mainloop()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        '''
        Window configuration
        '''
        self.title("Brainflirt")
        self.geometry("1000x1000")
        self.main_frame = Main(self)
        self.main_frame.pack()

class Main(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.button = ttk.Button(self, text="Open Webpage", command=self.open_webpage)
        self.button.pack(pady=20)
        # TODO: I want matplot lib

    def open_webpage(self):
        webbrowser.open("https://www.chatgpt.com/?q=tell+me+something+interesting+about+the+usa")

    def combine_parts(self, engagement, script):
        '''
        TODO: Combining the engagement and script parts
        '''
        pass

    def evaluate_engagement(self):
        '''
        TODO: Evaluating the engagement part
        '''
        pass

    def acquire_script(self):
        '''
        TODO: Acquiring the script part
        '''
        pass

if __name__ == "__main__":
    main()