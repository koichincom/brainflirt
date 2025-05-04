import tkinter as tk
from tkinter import ttk
import webbrowser
import pyautogui
import urllib.parse
import threading
import pyperclip

user_1_state = "normal"
user_2_state = "disabled"
copy_prompt_state = "disabled"

session_of_conversation = 5 # 5 times of conversation is considered 1 session
counter_for_session = 0 # counter should be set to 0 by default

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
        self.geometry("750x300")
        
        # Configure grid weight for vertical centering
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create main frame with padding
        self.main_frame = Main(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20)  # Changed from pack() to grid()

class Main(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configure grid weights for the main frame
        self.grid_rowconfigure(3, weight=1)  # Add weight to row between buttons and copy prompt
        self.grid_columnconfigure(1, weight=1)  # Center horizontally
        
        global user_1_state, user_2_state, copy_prompt_state
        self.conversation_history = []

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

        # Copy Prompt Button
        self.copy_prompt_button = ttk.Button(self, text="Copy GPT Prompt", command=self.copy_prompt_to_clipboard, state=copy_prompt_state)
        self.copy_prompt_button.grid(row=4, column=0, columnspan=3, pady=(20,10), sticky="ew")

    def apply_state(self):
        global user_1_state, user_2_state, copy_prompt_state
        
        self.submit_button_1.config(state=user_1_state)
        self.submit_button_2.config(state=user_2_state)
        self.copy_prompt_button.config(state=copy_prompt_state)


    def submit_user_1_text(self):
        global user_1_state, user_2_state
        
        if user_1_state == "normal":
            user_input = self.entry_user_1.get().strip()  # Remove whitespace
            
            if not user_input:
                return
                
            print(f"User 1 submitted: {user_input}")
            self.conversation_history.append(f"User 1: {user_input}")

            user_1_state = "disabled"
            user_2_state = "normal"
            self.apply_state()
            
            self.entry_user_1.delete(0, tk.END)
            self.entry_user_2.focus_set()

    def submit_user_2_text(self):
        global user_1_state, user_2_state, copy_prompt_state, counter_for_session, session_of_conversation
        
        if user_2_state == "normal":
            user_input = self.entry_user_2.get().strip()
            
            if not user_input:
                return
                
            print(f"User 2 submitted: {user_input}")
            self.conversation_history.append(f"User 2: {user_input}")
            
            user_2_state = "disabled"
            user_1_state = "normal"
            self.apply_state()

            self.entry_user_2.delete(0, tk.END)
            self.entry_user_1.focus_set()  # Replace pyautogui with direct focus

            counter_for_session += 1
        
        if counter_for_session % session_of_conversation == 0:
            print("hey!!")
            copy_prompt_state = "normal"
            user_1_state = "disabled"
            user_2_state = "disabled"
            self.apply_state()

            try:
                self.copy_prompt_to_clipboard()
            except Exception as e:
                print(f"Error copying prompt to clipboard: {e}")
                copy_prompt_state = "disabled"
                self.apply_state()
                return
            
            copy_prompt_state = "disabled"
            user_1_state = "normal"
            user_2_state = "disabled"
            self.apply_state()


    def copy_prompt_to_clipboard(self):
        engagement = "normal"
        conversation_script = "\n".join(self.conversation_history)

        prompt = self.generate_prompt(engagement, conversation_script)
        encoded_prompt = urllib.parse.quote(prompt)
        pyperclip.copy(encoded_prompt)

    def generate_prompt(self, engagement, conversation_script):
        prompt = f"""
        Based on the conversation script, and the user 2's engagement level since the last interaction, 
        please provide advice to user 1 on what to talk about next.
        The conversation script is a dialogue between user 1 and user 2,
        and the engagement level is a measure of how engaged user 2 has been since the last exchange.
        Please provide a response that is appropriate for the user's engagement level.
        Suggest a few topics or questions that user 2 might be interested in discussing.
        Also provide short insights about the conversation dynamics.

        The user 2's engagement level since the last interaction is: {engagement}.
        The conversation script so far is:
        {conversation_script}
        """
        return prompt


if __name__ == "__main__":
    main()