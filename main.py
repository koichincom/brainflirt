import tkinter as tk
from tkinter import ttk
import threading
import pyperclip
import datetime
from datetime import datetime

import src.muse_lsl
import src.engagement_predictor
from src.engagement_predictor import predict_engagement

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
        self.main_frame.grid(row=0, column=0, padx=20, pady=20)

class Main(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configure grid weights for the main frame
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Manage states as instance variables
        self.states = {
            "user_1": "normal",
            "user_2": "disabled",
            "copy_prompt": "disabled"
        }
        
        # Session management instance variables
        self.session_counter = 0
        self.session_max = 5  # 5 rounds per session
        
        # Track session timing and engagement result
        self.session_start_time = None
        self.current_engagement = "normal"
        
        self.conversation_history = []

        # Buffer for raw feature vectors per utterance
        self.engagement_feature_buffer = []

        # User 1 Label, Entry, and Button
        self.label_user_1 = ttk.Label(self, text="User 1")
        self.label_user_1.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_user_1 = ttk.Entry(self, width=50)
        self.entry_user_1.grid(row=0, column=1, padx=10, pady=10)

        self.entry_user_1.bind("<Return>", lambda event: self.submit_user_1_text())
        self.submit_button_1 = ttk.Button(self, text="Submit", command=self.submit_user_1_text, state=self.states["user_1"])
        self.submit_button_1.grid(row=0, column=2, padx=10, pady=10)

        # User 2 Label, Entry, and Button
        self.label_user_2 = ttk.Label(self, text="User 2")
        self.label_user_2.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_user_2 = ttk.Entry(self, width=50)
        self.entry_user_2.grid(row=1, column=1, padx=10, pady=10)

        self.entry_user_2.bind("<Return>", lambda event: self.submit_user_2_text())
        self.submit_button_2 = ttk.Button(self, text="Submit", command=self.submit_user_2_text, state=self.states["user_2"])
        self.submit_button_2.grid(row=1, column=2, padx=10, pady=10)

        # Copy Prompt Button
        self.copy_prompt_button = ttk.Button(self, text="Copy GPT Prompt", command=self.copy_prompt_to_clipboard, state=self.states["copy_prompt"])
        self.copy_prompt_button.grid(row=4, column=0, columnspan=3, pady=(20,10), sticky="ew")

    def apply_state(self):
        # Apply state
        self.submit_button_1.config(state=self.states["user_1"])
        self.submit_button_2.config(state=self.states["user_2"])
        self.copy_prompt_button.config(state=self.states["copy_prompt"])

    def submit_user_1_text(self):
        if self.states["user_1"] == "normal":
            user_input = self.entry_user_1.get().strip()
            
            if not user_input:
                return
                
            print(f"User 1 submitted: {user_input}")
            self.conversation_history.append(f"User 1: {user_input}")

            self.states["copy_prompt"] = "disabled"
            self.states["user_1"] = "disabled"
            self.states["user_2"] = "normal"
            self.apply_state()
            
            self.entry_user_1.delete(0, tk.END)
            self.entry_user_2.focus_set()

            if self.session_counter == 0:
                # mark the start time of a new session
                self.session_start_time = datetime.now()

    def submit_user_2_text(self):
        if self.states["user_2"] == "normal":
            user_input = self.entry_user_2.get().strip()
            
            if not user_input:
                return
                
            print(f"User 2 submitted: {user_input}")
            self.conversation_history.append(f"User 2: {user_input}")

            self.entry_user_2.delete(0, tk.END)
            self.entry_user_1.focus_set()

            # Increment session counter
            self.session_counter += 1

            # When the session is complete, compute engagement using Muse2 data
            if self.session_counter == self.session_max:
                elapsed_sec = max(1, int((datetime.now() - self.session_start_time).total_seconds()))
                try:
                    features = src.muse_lsl.get_current_features(duration_sec=elapsed_sec)
                    self.current_engagement = predict_engagement(features)
                except Exception as e:
                    print(f"[ENGAGEMENT] fallback due to error: {e}")
                    self.current_engagement = "normal"

                self.states["copy_prompt"] = "normal"
                self.states["user_1"] = "disabled"
                self.states["user_2"] = "disabled"
                self.apply_state()
            else:
                self.states["copy_prompt"] = "disabled"
                self.states["user_1"] = "normal"
                self.states["user_2"] = "disabled"
                self.apply_state()

    def copy_prompt_to_clipboard(self):
        conversation_script = "\n".join(self.conversation_history)

        prompt = self.generate_prompt(conversation_script)
        pyperclip.copy(prompt)
        print("Prompt copied to clipboard!")
        
        # Reset session
        self.session_counter = 0
        self.states["copy_prompt"] = "disabled"
        self.states["user_1"] = "normal"
        self.states["user_2"] = "disabled"
        self.apply_state()

        self.conversation_history.clear()

    def generate_prompt(self, conversation_script):
        engagement = self.current_engagement
        prompt = f"""
        Based on the conversation script for this session and user 2's engagement level, please provide advice to user 1 on what to talk about next.
        The conversation script is a dialogue between user 1 and user 2 for this session, and it is a continuation of the last prompt I gave you (if this is not the first prompt).
        The engagement level measures how engaged user 2 has been during this session, with three levels: low, normal, and high.
        To analyze changes in user 2's engagement level, you should consider the past engagement levels provided in previous prompts (if this is not the first prompt).

        Please format the output as follows:
        1. Suggest a few topics or questions that user 2 might be interested in discussing.
        2. Provide short insights about the conversation dynamics.
        Keep the response simple and easy to understand.

        User 2's engagement level for this session is: {engagement}.
        The conversation script for this session is:\n
        {conversation_script}
        """
        return prompt


if __name__ == "__main__":
    main()