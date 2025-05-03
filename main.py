import tkinter as tk
from tkinter import ttk
import webbrowser
import threading
import pyautogui

user_1_state = "normal"
user_2_state = "disabled"

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

        global user_1_state, user_2_state

        # User 1 Label, Entry, and Button
        self.label_user_1 = ttk.Label(self, text="User 1")
        self.label_user_1.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_user_1 = ttk.Entry(self, width=50)
        self.entry_user_1.grid(row=0, column=1, padx=10, pady=10)
        self.entry_user_1.bind("<Return>", lambda event: self.submit_user_1_text())
        self.submit_button_1 = ttk.Button(self, text="Submit", command=self.submit_user_1_text, state=user_1_state)
        self.submit_button_1.grid(row=0, column=2, padx=10, pady=10)

        # User 2 Label, Entry, and Button
        self.label_user_2 = ttk.Label(self, text="User 2")
        self.label_user_2.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_user_2 = ttk.Entry(self, width=50)
        self.entry_user_2.grid(row=1, column=1, padx=10, pady=10)
        self.entry_user_2.bind("<Return>", lambda event: self.submit_user_2_text())
        self.submit_button_2 = ttk.Button(self, text="Submit", command=self.submit_user_2_text, state=user_2_state)
        self.submit_button_2.grid(row=1, column=2, padx=10, pady=10)

        # GPT Button
        self.gpt_button = ttk.Button(self, text="Open ChatGPT", command=self.open_gpt)
        self.gpt_button.grid(row=2, column=0, columnspan=3, pady=20, sticky="ew")

    def submit_user_1_text(self):
        global user_1_state, user_2_state
        
        user_input = self.entry_user_1.get()
        print(f"User 1 submitted: {user_input}")

        user_1_state = "disabled"
        self.submit_button_1.config(state=user_1_state)
        user_2_state = "normal"
        self.submit_button_2.config(state=user_2_state)
        
        self.entry_user_1.delete(0, tk.END)

        pyautogui.press('tab')

    def submit_user_2_text(self):
        global user_1_state, user_2_state
        
        user_input = self.entry_user_2.get()
        print(f"User 2 submitted: {user_input}")
        
        user_2_state = "disabled"
        self.submit_button_2.config(state=user_2_state)
        user_1_state = "normal"
        self.submit_button_1.config(state=user_1_state)

        self.entry_user_2.delete(0, tk.END)

        # Press tab twice to switch focus
        pyautogui.press('tab')
        pyautogui.press('tab')

    def open_gpt(self):
        webbrowser.open("https://www.chatgpt.com/?q=tell+me+something+interesting")

    def combine_parts(self, engagement, script):
        # TODO: Improve the prompt

        prompt = f"""
        The user's engagement level is {engagement}.\n
        The conversation script so far is the below:\n
        {script}
        """
        return prompt

    def evaluate_engagement(self):
        '''
        TODO: Evaluating the engagement part
        '''
        pass

    def acquire_script(self):
        '''
        TODO: Acquiring the script part. Articulate since the code is activated
        '''
        pass

if __name__ == "__main__":
    main()