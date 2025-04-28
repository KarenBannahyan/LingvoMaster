import customtkinter as ctk
import json
import os
import requests
import httpx
from bs4 import BeautifulSoup
import pyperclip
from datetime import datetime
from threading import Thread
import re
import random


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LingvoMaster Pro")
        self.geometry("1000x650")
        self.minsize(900, 600)

        # Setup theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize data
        self.initialize_data()

        # Setup UI
        self.setup_main_ui()

    def initialize_data(self):
        # User data
        self.word_stats = {
            "total": 0,
            "day": 0,
            "week": 0,
            "month": 0
        }
        self.test_stats = {
            "best_score": 0,
            "average_score": 0
        }
        self.daily_goal = 10
        self.daily_progress = 0

        # Create logs directory if not exists
        os.makedirs("logs", exist_ok=True)
        self.words_file = "logs/user_words.json"
        self.words = self.load_words()
        self.word_stats["total"] = len(self.words)

        # AI Chat configuration
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = "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"  # Replace with your actual API key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://www.webstylepress.com",
            "X-Title": "WebStylePress",
            "Content-Type": "application/json"
        }

        # Translator languages
        self.languages = {
            "Auto Detect": "auto", "Armenian": "hy", "English": "en", "French": "fr",
            "Spanish": "es", "German": "de", "Russian": "ru", "Chinese": "zh",
            "Japanese": "ja", "Korean": "ko", "Italian": "it", "Portuguese": "pt",
            "Dutch": "nl", "Arabic": "ar", "Hindi": "hi", "Turkish": "tr",
            "Hebrew": "he", "Greek": "el", "Swedish": "sv", "Polish": "pl",
            "Ukrainian": "uk", "Czech": "cs", "Finnish": "fi", "Hungarian": "hu",
            "Romanian": "ro", "Thai": "th", "Vietnamese": "vi", "Indonesian": "id"
        }

    def load_words(self):
        try:
            if os.path.exists(self.words_file):
                with open(self.words_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading words: {e}")
        return []

    def save_words(self):
        try:
            with open(self.words_file, "w", encoding="utf-8") as f:
                json.dump(self.words, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving words: {e}")

    def save_word(self, word, translation, sentence):
        if not word or not translation:
            return

        new_word = {
            "word": word.capitalize(),
            "translation": translation,
            "sentence": sentence.capitalize(),
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "review_count": 0,
            "last_reviewed": None
        }

        self.words.append(new_word)
        self.word_stats["total"] = len(self.words)
        self.word_stats["day"] += 1
        self.daily_progress += 1
        self.save_words()
        self.show_main_screen()

    def setup_main_ui(self):
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        # Main layout (2 columns)
        self.grid_columnconfigure(0, weight=0, minsize=250)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left Column (Menu)
        self.setup_menu()

        # Right Column (Content)
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)

        self.show_main_screen()

    def setup_menu(self):
        menu_frame = ctk.CTkFrame(self, corner_radius=0)
        menu_frame.grid(row=0, column=0, sticky="nsew")

        # Logo
        ctk.CTkLabel(
            menu_frame,
            text="LingvoMaster",
            font=("Arial", 22, "bold"),
            pady=30
        ).pack()

        # Separator
        ctk.CTkFrame(menu_frame, height=2, fg_color=("#D0D0D0", "#404040")).pack(fill="x", padx=20)

        # Menu buttons
        buttons = [
            ("➕ Add Word", self.show_add_word_screen),
            ("🔍 Search", self.show_search_screen),
            ("📖 All Words", self.show_all_words),
            ("🗑️ Delete Word", self.show_delete_word_screen),
            ("✏️ Test", self.start_test),
            ("🌐 Translator", self.show_translator),
            ("🤖 AI Chat", self.show_ai_chat),
            ("📂 Import/Export", self.open_json_manager)
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(
                menu_frame,
                text=text,
                command=command,
                font=("Arial", 14),
                anchor="w",
                height=45,
                corner_radius=8,
                fg_color="transparent",
                hover_color=("#E0E0E0", "#383838"),
                border_width=1,
                border_color=("#D0D0D0", "#404040")
            )
            btn.pack(fill="x", padx=20, pady=5)

        # Theme switcher
        theme_switch = ctk.CTkSwitch(
            menu_frame,
            text="Dark Theme",
            command=self.toggle_theme,
            font=("Arial", 12),
            progress_color="#4CC2FF"
        )
        theme_switch.pack(side="bottom", pady=20)

    def show_main_screen(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Daily progress
        progress_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=30, pady=20)

        ctk.CTkLabel(
            progress_frame,
            text=f"📅 Daily Progress: {self.daily_progress}/{self.daily_goal}",
            font=("Arial", 16, "bold")
        ).pack(side="left")

        progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=200,
            height=10,
            corner_radius=5,
            progress_color="#4CC2FF"
        )
        progress_bar.pack(side="left", padx=10)
        progress_bar.set(self.daily_progress / self.daily_goal)

        # Statistics
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="both", expand=True, padx=30, pady=10)

        stats_card = ctk.CTkFrame(
            stats_frame,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#383838"),
            fg_color=("#F8F8F8", "#333333")
        )
        stats_card.pack(fill="both", expand=True)

        ctk.CTkLabel(
            stats_card,
            text="📊 Your Statistics",
            font=("Arial", 18, "bold"),
            pady=15
        ).pack()

        grid_frame = ctk.CTkFrame(stats_card, fg_color="transparent")
        grid_frame.pack(pady=10)

        # Words
        ctk.CTkLabel(
            grid_frame,
            text=f"📝 Total Words: {self.word_stats['total']}",
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=20, pady=5, sticky="w")

        ctk.CTkLabel(
            grid_frame,
            text=f"📅 New Today: {self.word_stats['day']}",
            font=("Arial", 14)
        ).grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # Tests
        ctk.CTkLabel(
            grid_frame,
            text=f"🏆 Best Score: {self.test_stats['best_score']}%",
            font=("Arial", 14)
        ).grid(row=0, column=1, padx=20, pady=5, sticky="w")

        ctk.CTkLabel(
            grid_frame,
            text=f"📊 Average: {self.test_stats['average_score']}%",
            font=("Arial", 14)
        ).grid(row=1, column=1, padx=20, pady=5, sticky="w")

        # Motivation
        motivation_frame = ctk.CTkFrame(
            self.content_frame,
            corner_radius=12,
            border_width=1,
            border_color=("#E0E0E0", "#383838"),
            fg_color=("#F0F9FF", "#1E2A3A")
        )
        motivation_frame.pack(fill="x", padx=30, pady=20)

        ctk.CTkLabel(
            motivation_frame,
            text=f"🔥 Words left today: {self.daily_goal - self.daily_progress}",
            font=("Arial", 14),
            pady=10
        ).pack()

    # ===== AI Chat Functionality =====
    def show_ai_chat(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Chat title
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(pady=10)

        ctk.CTkLabel(
            title_frame,
            text="🤖 AI Language Assistant",
            font=("Arial", 20, "bold")
        ).pack()

        # Chat display
        self.chat_display = ctk.CTkTextbox(
            self.content_frame,
            wrap="word",
            font=("Arial", 14),
            fg_color=("#444654", "#444654"),
            text_color=("#ececf1", "#ececf1"),
            state="disabled"
        )
        self.chat_display.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Input frame
        input_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 20))

        # User input
        self.user_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message here...",
            font=("Arial", 14),
            fg_color=("#565869", "#565869"),
            border_width=0
        )
        self.user_input.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Send button
        send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self.send_ai_message,
            width=100,
            fg_color=("#19c37d", "#19c37d"),
            hover_color=("#16a065", "#16a065"),
            font=("Arial", 14, "bold")
        )
        send_button.pack(side="right")

        # Back button
        back_button = ctk.CTkButton(
            self.content_frame,
            text="Back to Main",
            command=self.show_main_screen,
            fg_color="transparent",
            border_width=1,
            border_color=("#D0D0D0", "#404040"),
            font=("Arial", 12)
        )
        back_button.pack(pady=(0, 10))

        # Bind Enter key to send message
        self.user_input.bind("<Return>", lambda event: self.send_ai_message())

        # Add initial greeting
        self.add_ai_message("AI", "Hello! I'm your language learning assistant. How can I help you today?")

    def add_ai_message(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"{sender}: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

    def send_ai_message(self):
        user_message = self.user_input.get().strip()
        if not user_message:
            return

        self.user_input.delete(0, "end")
        self.add_ai_message("You", user_message)

        # Disable input while processing
        self.user_input.configure(state="disabled")

        # Show loading message
        self.add_ai_message("AI", "Thinking...")

        # Start API call in a separate thread
        Thread(target=self.get_ai_response, args=(user_message,), daemon=True).start()

    def get_ai_response(self, user_message):
        try:
            payload = {
                "model": "deepseek/deepseek-r1:free",
                "messages": [{"role": "user", "content": user_message}]
            }

            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

            ai_response = data.get("choices", [{}])[0].get("message", {}).get("content", "No response received.")

            # Remove the "Thinking..." message and add the real response
            self.after(0, lambda: self.update_ai_chat(ai_response))

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.after(0, lambda: self.update_ai_chat(error_msg))

    def update_ai_chat(self, response):
        # Remove the "Thinking..." message
        self.chat_display.configure(state="normal")
        self.chat_display.delete("end-2l", "end")

        # Add the actual response
        self.add_ai_message("AI", response)

        # Re-enable input
        self.user_input.configure(state="normal")
        self.user_input.focus()

    # ===== Translator Functionality =====
    def show_translator(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Translator title
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(pady=10)

        ctk.CTkLabel(
            title_frame,
            text="🌐 Translator",
            font=("Arial", 20, "bold")
        ).pack()

        # Input frame
        input_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        input_frame.pack(pady=10)

        # Input label and field
        ctk.CTkLabel(
            input_frame,
            text="Enter text to translate:",
            font=("Arial", 14)
        ).pack(anchor="w")

        self.translate_input = ctk.CTkEntry(
            input_frame,
            width=400,
            font=("Arial", 14)
        )
        self.translate_input.pack(pady=5)

        # Language selection frame
        lang_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        lang_frame.pack(pady=10)

        # From language
        ctk.CTkLabel(
            lang_frame,
            text="From:",
            font=("Arial", 14)
        ).grid(row=0, column=0, padx=5, sticky="w")

        self.from_lang_var = ctk.StringVar(value="French")
        from_menu = ctk.CTkOptionMenu(
            lang_frame,
            variable=self.from_lang_var,
            values=list(self.languages.keys()),
            width=150
        )
        from_menu.grid(row=0, column=1, padx=5)

        # To language
        ctk.CTkLabel(
            lang_frame,
            text="To:",
            font=("Arial", 14)
        ).grid(row=0, column=2, padx=5, sticky="w")

        self.to_lang_var = ctk.StringVar(value="Russian")
        to_menu = ctk.CTkOptionMenu(
            lang_frame,
            variable=self.to_lang_var,
            values=list(self.languages.keys())[1:],
            width=150
        )
        to_menu.grid(row=0, column=3, padx=5)

        # Translate button
        translate_button = ctk.CTkButton(
            self.content_frame,
            text="Translate",
            command=self.translate_text,
            width=150,
            height=40,
            font=("Arial", 14, "bold")
        )
        translate_button.pack(pady=15)

        # Output frame
        output_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        output_frame.pack(pady=10)

        ctk.CTkLabel(
            output_frame,
            text="Translation:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w")

        self.translate_output = ctk.CTkTextbox(
            output_frame,
            width=400,
            height=100,
            font=("Arial", 14),
            wrap="word",
            state="disabled"
        )
        self.translate_output.pack(pady=5)

        # Copy button
        copy_button = ctk.CTkButton(
            output_frame,
            text="Copy to Clipboard",
            command=self.copy_translation,
            width=150,
            height=30
        )
        copy_button.pack(pady=5)

        # Back button
        back_button = ctk.CTkButton(
            self.content_frame,
            text="Back to Main",
            command=self.show_main_screen,
            fg_color="transparent",
            border_width=1,
            border_color=("#D0D0D0", "#404040"),
            font=("Arial", 12)
        )
        back_button.pack(pady=10)

    def translate_text(self):
        text = self.translate_input.get().strip()
        if not text:
            return

        from_lang = self.from_lang_var.get()
        to_lang = self.to_lang_var.get()

        # Show loading state
        self.translate_output.configure(state="normal")
        self.translate_output.delete("1.0", "end")
        self.translate_output.insert("end", "Translating...")
        self.translate_output.configure(state="disabled")

        # Start translation in a separate thread
        Thread(target=self.perform_translation, args=(text, from_lang, to_lang), daemon=True).start()

    def perform_translation(self, text, from_lang, to_lang):
        try:
            BASE_URL = "https://translate.google.com/m"
            params = {
                "hl": self.languages[to_lang],
                "sl": self.languages[from_lang],
                "q": text
            }

            with httpx.Client() as client:
                response = client.get(BASE_URL, params=params)
                if response.status_code != 200:
                    raise Exception("Translation service unavailable")

                soup = BeautifulSoup(response.text, "html.parser")
                result = soup.find("div", class_="result-container")
                translation = result.text if result else "Translation not found"

                # Update UI with translation
                self.after(0, lambda: self.display_translation(translation))

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.after(0, lambda: self.display_translation(error_msg))

    def display_translation(self, text):
        self.translate_output.configure(state="normal")
        self.translate_output.delete("1.0", "end")
        self.translate_output.insert("end", text)
        self.translate_output.configure(state="disabled")

    def copy_translation(self):
        text = self.translate_output.get("1.0", "end-1c")
        if text and text != "Translating..." and not text.startswith("Error:"):
            pyperclip.copy(text)

    # ===== Delete Word Functionality =====
    def show_delete_word_screen(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Title
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        title_frame.pack(pady=10)

        ctk.CTkLabel(
            title_frame,
            text="🗑️ Delete Word",
            font=("Arial", 20, "bold")
        ).pack()

        # Search frame
        search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        search_frame.pack(pady=10)

        ctk.CTkLabel(
            search_frame,
            text="Search word to delete:",
            font=("Arial", 14)
        ).pack(side="left", padx=5)

        self.delete_search_entry = ctk.CTkEntry(
            search_frame,
            width=250,
            font=("Arial", 14)
        )
        self.delete_search_entry.pack(side="left", padx=5)

        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_word_to_delete,
            width=80
        )
        search_button.pack(side="left", padx=5)

        # Results frame
        self.delete_results_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            height=300,
            fg_color=("#F8F8F8", "#333333")
        )
        self.delete_results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Back button
        back_button = ctk.CTkButton(
            self.content_frame,
            text="Back to Main",
            command=self.show_main_screen,
            fg_color="transparent",
            border_width=1,
            border_color=("#D0D0D0", "#404040"),
            font=("Arial", 12)
        )
        back_button.pack(pady=10)

    def search_word_to_delete(self):
        # Clear previous results
        for widget in self.delete_results_frame.winfo_children():
            widget.destroy()

        search_term = self.delete_search_entry.get().strip().lower()
        if not search_term:
            return

        found_words = []
        for word in self.words:
            if (search_term in word["word"].lower() or
                    search_term in word["translation"].lower()):
                found_words.append(word)

        if not found_words:
            ctk.CTkLabel(
                self.delete_results_frame,
                text="No words found matching your search",
                font=("Arial", 14)
            ).pack(pady=20)
            return

        for word in found_words:
            word_frame = ctk.CTkFrame(
                self.delete_results_frame,
                corner_radius=8,
                border_width=1,
                border_color=("#E0E0E0", "#383838")
            )
            word_frame.pack(fill="x", pady=2, padx=2)

            # Word info
            ctk.CTkLabel(
                word_frame,
                text=f"{word['word']} - {word['translation']}",
                font=("Arial", 14)
            ).pack(side="left", padx=10, pady=5)

            # Delete button
            delete_btn = ctk.CTkButton(
                word_frame,
                text="Delete",
                command=lambda w=word: self.delete_word(w),
                width=80,
                fg_color="#ff5555",
                hover_color="#cc0000"
            )
            delete_btn.pack(side="right", padx=5)

    def delete_word(self, word):
        self.words.remove(word)
        self.save_words()
        self.word_stats["total"] = len(self.words)
        self.show_delete_word_screen()

    # ===== Other Screens =====
    def show_add_word_screen(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Add word form
        form_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        form_frame.pack(pady=50)

        ctk.CTkLabel(
            form_frame,
            text="➕ Add New Word",
            font=("Arial", 20, "bold"),
            pady=20
        ).pack()

        # Word input
        ctk.CTkLabel(form_frame, text="Word:", font=("Arial", 14)).pack(pady=5)
        word_entry = ctk.CTkEntry(form_frame, width=300)
        word_entry.pack(pady=5)

        # Translation input
        ctk.CTkLabel(form_frame, text="Translation:", font=("Arial", 14)).pack(pady=5)
        translation_entry = ctk.CTkEntry(form_frame, width=300)
        translation_entry.pack(pady=5)

        # Sentence input
        ctk.CTkLabel(form_frame, text="Example Sentence:", font=("Arial", 14)).pack(pady=5)
        sentence_entry = ctk.CTkEntry(form_frame, width=300)
        sentence_entry.pack(pady=5)

        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="Save",
            command=lambda: self.save_word(
                word_entry.get(),
                translation_entry.get(),
                sentence_entry.get()
            ),
            width=120
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Back",
            command=self.show_main_screen,
            width=120,
            fg_color="transparent",
            border_width=1,
            border_color=("#D0D0D0", "#404040")
        ).pack(side="left", padx=10)

    def show_search_screen(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Search form
        search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        search_frame.pack(pady=20)

        ctk.CTkLabel(
            search_frame,
            text="🔍 Search Word",
            font=("Arial", 20, "bold"),
            pady=10
        ).pack()

        # Search input
        search_entry = ctk.CTkEntry(search_frame, width=300, placeholder_text="Enter word to search...")
        search_entry.pack(pady=10)

        # Search button
        ctk.CTkButton(
            search_frame,
            text="Search",
            command=lambda: self.perform_search(search_entry.get()),
            width=120
        ).pack(pady=5)

        # Back button
        ctk.CTkButton(
            search_frame,
            text="Back",
            command=self.show_main_screen,
            width=120,
            fg_color="transparent",
            border_width=1,
            border_color=("#D0D0D0", "#404040")
        ).pack(pady=5)

        # Results frame
        self.search_results_frame = ctk.CTkScrollableFrame(self.content_frame, height=300)
        self.search_results_frame.pack(fill="both", expand=True, padx=30, pady=10)

    def perform_search(self, search_term):
        # Clear previous results
        for widget in self.search_results_frame.winfo_children():
            widget.destroy()

        if not search_term:
            ctk.CTkLabel(
                self.search_results_frame,
                text="Please enter a search term",
                font=("Arial", 14)
            ).pack(pady=10)
            return

        search_term = search_term.lower()
        found_results = False

        # Search in user_words.json
        for word in self.words:
            if (search_term in word["word"].lower() or
                    search_term in word["translation"].lower() or
                    (word["sentence"] and search_term in word["sentence"].lower())):
                found_results = True
                self.display_search_result(word)

        # Search in all JSON files in logs directory
        for filename in os.listdir("logs"):
            if filename.endswith(".json") and filename != "user_words.json":
                try:
                    with open(os.path.join("logs", filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict):
                                    if (search_term in item.get("word", "").lower() or
                                            search_term in item.get("translation", "").lower() or
                                            search_term in item.get("sentence", "").lower()):
                                        found_results = True
                                    self.display_search_result(item)
                except Exception as e:
                    print(f"Error reading {filename}: {e}")

        if not found_results:
            ctk.CTkLabel(
                self.search_results_frame,
                text=f"No results found for '{search_term}'",
                font=("Arial", 14)
            ).pack(pady=10)

    def display_search_result(self, word_data):
        result_frame = ctk.CTkFrame(
            self.search_results_frame,
            corner_radius=8,
            border_width=1,
            border_color=("#E0E0E0", "#383838")
        )
        result_frame.pack(fill="x", pady=5, padx=5)

        # Word and translation
        ctk.CTkLabel(
            result_frame,
            text=f"{word_data.get('word', 'N/A')} - {word_data.get('translation', 'N/A')}",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=5)

        # Example sentence if exists
        if word_data.get("sentence"):
            ctk.CTkLabel(
                result_frame,
                text=f"Example: {word_data['sentence']}",
                font=("Arial", 12)
            ).pack(anchor="w", padx=10, pady=2)

        # Date added if exists
        if word_data.get("date_added"):
            ctk.CTkLabel(
                result_frame,
                text=f"Added: {word_data['date_added']}",
                font=("Arial", 10),
                text_color=("gray50", "gray70")
            ).pack(anchor="w", padx=10, pady=2)

    def show_all_words(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # All words view
        all_words_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        all_words_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            all_words_frame,
            text="📖 All Words",
            font=("Arial", 20, "bold"),
            pady=10
        ).pack()

        # Words list
        self.words_list_frame = ctk.CTkScrollableFrame(
            all_words_frame,
            height=400,
            fg_color=("#F8F8F8", "#333333")
        )
        self.words_list_frame.pack(fill="both", expand=True)

        # Back button
        ctk.CTkButton(
            all_words_frame,
            text="Back to Main",
            command=self.show_main_screen,
            width=120,
            fg_color="transparent",
            border_width=1,
            border_color=("#D0D0D0", "#404040"),
            font=("Arial", 12)
        ).pack(pady=10)

        # Display all words
        self.display_all_words()

    def display_all_words(self):
        # Clear current list
        for widget in self.words_list_frame.winfo_children():
            widget.destroy()

        if not self.words:
            ctk.CTkLabel(
                self.words_list_frame,
                text="Your word list is empty",
                font=("Arial", 14)
            ).pack(pady=20)
            return

        for word in self.words:
            word_frame = ctk.CTkFrame(
                self.words_list_frame,
                corner_radius=8,
                border_width=1,
                border_color=("#E0E0E0", "#383838")
            )
            word_frame.pack(fill="x", pady=2, padx=2)

            # Word and translation
            ctk.CTkLabel(
                word_frame,
                text=f"{word['word']} - {word['translation']}",
                font=("Arial", 14)
            ).pack(anchor="w", padx=10, pady=5)

            # Example sentence if exists
            if word.get("sentence"):
                ctk.CTkLabel(
                    word_frame,
                    text=f"Example: {word['sentence']}",
                    font=("Arial", 12),
                    text_color=("gray50", "gray70")
                ).pack(anchor="w", padx=10, pady=2)

    def start_test(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Check if there are words to test
        if not self.words:
            ctk.CTkLabel(
                self.content_frame,
                text="No words available for testing. Add some words first!",
                font=("Arial", 16)
            ).pack(pady=50)

            ctk.CTkButton(
                self.content_frame,
                text="Back to Main",
                command=self.show_main_screen,
                width=120,
                fg_color="transparent",
                border_width=1,
                border_color=("#D0D0D0", "#404040"),
                font=("Arial", 12)
            ).pack(pady=10)
            return

        # Test setup
        self.test_words = random.sample(self.words, min(10, len(self.words)))
        self.current_test_index = 0
        self.correct_answers = 0

        # Test frame
        test_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        test_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Question label
        self.question_label = ctk.CTkLabel(
            test_frame,
            text="",
            font=("Arial", 18, "bold"),
            wraplength=500
        )
        self.question_label.pack(pady=20)

        # Answer entry
        self.answer_entry = ctk.CTkEntry(
            test_frame,
            width=300,
            font=("Arial", 14),
            placeholder_text="Type your answer..."
        )
        self.answer_entry.pack(pady=10)

        # Submit button
        submit_button = ctk.CTkButton(
            test_frame,
            text="Submit",
            command=self.check_test_answer,
            width=120,
            font=("Arial", 14)
        )
        submit_button.pack(pady=10)

        # Progress label
        self.progress_label = ctk.CTkLabel(
            test_frame,
            text=f"Question 1 of {len(self.test_words)}",
            font=("Arial", 12)
        )
        self.progress_label.pack(pady=5)

        # Back button
        back_button = ctk.CTkButton(
            test_frame,
            text="Cancel Test",
            command=self.show_main_screen,
            fg_color="transparent",
            border_width=1,
            border_color=("#D0D0D0", "#404040"),
            font=("Arial", 12)
        )
        back_button.pack(pady=10)

        # Start the test
        self.show_next_test_question()

    def show_next_test_question(self):
        if self.current_test_index >= len(self.test_words):
            self.show_test_results()
            return

        current_word = self.test_words[self.current_test_index]

        # Randomly decide whether to ask for word or translation
        if random.choice([True, False]):
            self.question_label.configure(text=f"What is the translation of: '{current_word['word']}'?")
            self.correct_answer = current_word['translation']
        else:
            self.question_label.configure(text=f"What is the word for: '{current_word['translation']}'?")
            self.correct_answer = current_word['word']

        self.progress_label.configure(text=f"Question {self.current_test_index + 1} of {len(self.test_words)}")
        self.answer_entry.delete(0, "end")

    def check_test_answer(self):
        user_answer = self.answer_entry.get().strip()
        if not user_answer:
            return

        if user_answer.lower() == self.correct_answer.lower():
            self.correct_answers += 1

        self.current_test_index += 1
        self.show_next_test_question()

    def show_test_results(self):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Calculate score
        score = int((self.correct_answers / len(self.test_words)) * 100)

        # Update test stats
        if score > self.test_stats["best_score"]:
            self.test_stats["best_score"] = score

        if self.test_stats["average_score"] == 0:
            self.test_stats["average_score"] = score
        else:
            self.test_stats["average_score"] = (self.test_stats["average_score"] + score) // 2

        # Results frame
        results_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        results_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Result message
        if score >= 80:
            result_text = "🎉 Excellent! 🎉"
            color = "#4CC2FF"
        elif score >= 60:
            result_text = "👍 Good job! 👍"
            color = "#4CC2FF"
        else:
            result_text = "Keep practicing!"
            color = "#FF5555"

        ctk.CTkLabel(
            results_frame,
            text="Test Results",
            font=("Arial", 24, "bold"),
            pady=20
        ).pack()

        ctk.CTkLabel(
            results_frame,
            text=f"You scored: {score}%",
            font=("Arial", 20),
            text_color=color
        ).pack(pady=10)

        ctk.CTkLabel(
            results_frame,
            text=f"{self.correct_answers} correct out of {len(self.test_words)}",
            font=("Arial", 16)
        ).pack(pady=5)

        ctk.CTkLabel(
            results_frame,
            text=result_text,
            font=("Arial", 18),
            text_color=color
        ).pack(pady=20)

        # Back button
        ctk.CTkButton(
            results_frame,
            text="Back to Main",
            command=self.show_main_screen,
            width=150,
            font=("Arial", 14)
        ).pack(pady=20)

    def open_json_manager(self):
        print("Import/Export will be implemented here")

    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if current == "dark" else "dark")


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()