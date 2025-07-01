import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
try:
    import fitz  # PyMuPDF for PDF
except ImportError:
    fitz = None
try:
    from ebooklib import epub
except ImportError:
    epub = None
import random
import json
import urllib.request

# Dynamically determine supported extensions based on available libraries
SUPPORTED_EXTENSIONS = set()
SUPPORTED_EXTENSIONS.add('.txt')
if fitz:
    SUPPORTED_EXTENSIONS.add('.pdf')
if epub:
    SUPPORTED_EXTENSIONS.add('.epub')

EBOOKS_DIR = 'ebooks'
REC_FILE = 'recent_reads.json'
os.makedirs(EBOOKS_DIR, exist_ok=True)

def load_recent_reads():
    if os.path.exists(REC_FILE):
        with open(REC_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_recent_reads(data):
    with open(REC_FILE, 'w') as f:
        json.dump(data, f)

def load_external_recs():
    try:
        with open('external_recommendations.json', 'r') as f:
            return json.load(f)
    except Exception:
        return []

def display_title(fname):
    name = os.path.splitext(fname)[0]
    return name.replace('_', ' ').strip()

class EbookReaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Ebook Reader')
        self.geometry('900x600')
        self.configure(bg='#eceae4')
        self.current_book = None
        self.current_ext = None
        self.current_pages = []
        self.current_page_idx = 0
        self.recent_reads = load_recent_reads()
        self.show_home()
        self.bind('<Left>', lambda e: self.prev_page())
        self.bind('<Right>', lambda e: self.next_page())

    def show_home(self):
        for widget in self.winfo_children():
            widget.destroy()
        home = tk.Frame(self, bg='#eceae4')
        home.pack(fill='both', expand=True)
        # Center content
        center = tk.Frame(home, bg='#eceae4')
        center.place(relx=0.5, rely=0.5, anchor='center')
        # App icon (simple emoji)
        tk.Label(center, text='📚', bg='#eceae4', font=('Segoe UI', 48)).pack(pady=(0, 10))
        tk.Label(center, text='Welcome to Ebook Reader', bg='#eceae4', fg='#222', font=('Segoe UI', 24, 'bold')).pack(pady=(0, 20))
        rec = self.get_recommendation()
        if rec:
            tk.Label(center, text='Recommended for you:', bg='#eceae4', fg='#444', font=('Segoe UI', 14, 'bold')).pack(pady=(0, 5))
            tk.Label(center, text=rec, bg='#eceae4', fg='#2d3e50', font=('Segoe UI', 16, 'bold')).pack(pady=(0, 15))
        ext_recs = load_external_recs()
        if ext_recs:
            tk.Label(center, text='Recommended from Online:', bg='#eceae4', fg='#444', font=('Segoe UI', 14, 'bold')).pack(pady=(10, 5))
            for ext in ext_recs:
                card = tk.Frame(center, bg='#f5f5f3', bd=1, relief='solid')
                card.pack(pady=4, padx=10, fill='x')
                tk.Label(card, text=ext['title'], bg='#f5f5f3', fg='#2d3e50', font=('Segoe UI', 12, 'bold')).pack(side='left', padx=10, pady=5)
                tk.Button(card, text='Add to Library', command=lambda e=ext: self.download_external(e), font=('Segoe UI', 10, 'bold'), bg='#bdb7a4', fg='#222').pack(side='right', padx=10, pady=5)
        tk.Button(center, text='Go to Library', command=self.show_library, font=('Segoe UI', 15, 'bold'), bg='#4caf50', fg='white', width=18, height=2).pack(pady=30)

    def download_external(self, ext):
        fname = ext['title'].replace(' ', '_').replace('(', '').replace(')', '').replace("'", "") + '.' + ext['type']
        dest = os.path.join(EBOOKS_DIR, fname)
        if os.path.exists(dest):
            messagebox.showinfo('Info', 'Ebook already in library.')
            return
        try:
            with urllib.request.urlopen(ext['source']) as response, open(dest, 'wb') as out:
                content = response.read()
                # If chapter, just take first 3000 chars
                if ext['type'] == 'txt' and 'Chapter 1' in ext['title']:
                    content = content[:3000]
                out.write(content)
            messagebox.showinfo('Success', f'Added "{ext["title"]}" to library!')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to download: {e}')

    def get_recommendation(self):
        files = [f for f in os.listdir(EBOOKS_DIR) if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS]
        if not files:
            return None
        unread = [f for f in files if f not in self.recent_reads]
        if unread:
            return random.choice(unread)
        # Recommend least recently opened
        sorted_reads = sorted(self.recent_reads.items(), key=lambda x: x[1])
        return sorted_reads[0][0] if sorted_reads else random.choice(files)

    def show_library(self):
        for widget in self.winfo_children():
            widget.destroy()
        lib_frame = tk.Frame(self, bg='#eceae4')
        lib_frame.pack(fill='both', expand=True)
        # Header
        header = tk.Frame(lib_frame, bg='#eceae4')
        header.pack(pady=(30, 10), fill='x')
        tk.Button(header, text='🏠 Home', command=self.show_home, font=('Segoe UI', 13, 'bold'), bg='#bdb7a4', fg='#222', bd=0, padx=14, pady=8, activebackground='#bdb7a4', activeforeground='#222').pack(side='left', padx=10)
        tk.Label(header, text='My Library', bg='#eceae4', fg='#222', font=('Segoe UI', 28, 'bold')).pack(side='left', padx=20)
        upload_btn = tk.Button(header, text='＋ Add Ebook(s)', command=self.upload_ebook, font=('Segoe UI', 13, 'bold'), bg='#4caf50', fg='white', bd=0, padx=18, pady=8, activebackground='#388e3c', activeforeground='white')
        upload_btn.pack(side='right', padx=10)
        remove_btn = tk.Button(header, text='🗑 Remove Selected', command=lambda: None, font=('Segoe UI', 13, 'bold'), bg='#e53935', fg='white', bd=0, padx=18, pady=8, activebackground='#b71c1c', activeforeground='white')
        remove_btn.pack(side='right', padx=10)
        # Grid area
        grid_frame = tk.Frame(lib_frame, bg='#eceae4')
        grid_frame.pack(expand=True, fill='both', padx=30, pady=10)
        # List all books in a grid
        books = [f for f in os.listdir(EBOOKS_DIR) if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS]
        self.grid_cards = []
        columns = 4
        self.selected_card_idx = None
        def on_card_click(idx):
            # Deselect all
            for i, card in enumerate(self.grid_cards):
                card.config(bg='#f5f5f3')
            # Select this one
            self.grid_cards[idx].config(bg='#bdb7a4')
            self.selected_card_idx = idx
        for idx, fname in enumerate(books):
            row, col = divmod(idx, columns)
            card = tk.Frame(grid_frame, bg='#f5f5f3', bd=2, relief='ridge', width=180, height=90)
            card.grid(row=row, column=col, padx=16, pady=16, sticky='nsew')
            card.grid_propagate(False)
            title = display_title(fname)
            label = tk.Label(card, text=title, bg='#f5f5f3', fg='#2d3e50', font=('Segoe UI', 13, 'bold'), wraplength=160, justify='center')
            label.pack(expand=True, fill='both', padx=8, pady=8)
            card.bind('<Button-1>', lambda e, i=idx: on_card_click(i))
            label.bind('<Button-1>', lambda e, i=idx: on_card_click(i))
            card.bind('<Double-Button-1>', lambda e, f=fname: self.open_reader_page_grid(f))
            label.bind('<Double-Button-1>', lambda e, f=fname: self.open_reader_page_grid(f))
            self.grid_cards.append(card)
        # Make grid expand
        for c in range(columns):
            grid_frame.grid_columnconfigure(c, weight=1)
        for r in range((len(books) + columns - 1) // columns):
            grid_frame.grid_rowconfigure(r, weight=1)
        def remove_ebook_grid():
            if self.selected_card_idx is None:
                messagebox.showinfo('Info', 'No ebook selected.')
                return
            fname = books[self.selected_card_idx]
            confirm = messagebox.askyesno('Remove Ebook', f'Are you sure you want to remove "{display_title(fname)}"?')
            if confirm:
                try:
                    os.remove(os.path.join(EBOOKS_DIR, fname))
                    self.show_library()
                except Exception as e:
                    messagebox.showerror('Error', f'Failed to remove ebook: {e}')
        remove_btn.config(command=remove_ebook_grid)

    def open_reader_page_grid(self, fname):
        ext = os.path.splitext(fname)[1].lower()
        path = os.path.join(EBOOKS_DIR, fname)
        # PDF support check
        if ext == '.pdf' and not fitz:
            messagebox.showerror('PDF Not Supported', 'PDF support requires the PyMuPDF (fitz) library. Please install it to read PDF files.')
            return
        for widget in self.winfo_children():
            widget.destroy()
        reader_frame = tk.Frame(self, bg='#eceae4')
        reader_frame.pack(fill='both', expand=True)
        # Top bar
        topbar = tk.Frame(reader_frame, bg='#f5f5f3', height=48, bd=0, relief='flat')
        topbar.pack(side='top', fill='x')
        tk.Button(topbar, text='🏠 Home', command=self.show_home, font=('Segoe UI', 12, 'bold'), bg='#bdb7a4', fg='#222', bd=0, padx=12, pady=6).pack(side='left', padx=10, pady=8)
        tk.Button(topbar, text='⟵ Back to Library', command=self.show_library, font=('Segoe UI', 12, 'bold'), bg='#bdb7a4', fg='#222', bd=0, padx=12, pady=6).pack(side='left', padx=10, pady=8)
        tk.Label(topbar, text=display_title(fname), bg='#f5f5f3', fg='#222', font=('Segoe UI', 16, 'bold')).pack(side='left', padx=20, pady=8)
        # Font controls
        font_frame = tk.Frame(reader_frame, bg='#eceae4')
        font_frame.pack(fill='x', pady=(5, 0))
        tk.Label(font_frame, text='Font:', bg='#eceae4', fg='#444', font=('Segoe UI', 11)).pack(side='left', padx=(20, 2))
        font_families = ['Georgia', 'Arial', 'Times New Roman', 'Courier New', 'Segoe UI']
        font_var = tk.StringVar(value='Georgia')
        font_menu = tk.OptionMenu(font_frame, font_var, *font_families)
        font_menu.pack(side='left', padx=2)
        tk.Label(font_frame, text='Size:', bg='#eceae4', fg='#444', font=('Segoe UI', 11)).pack(side='left', padx=(16, 2))
        size_var = tk.IntVar(value=18)
        size_menu = tk.OptionMenu(font_frame, size_var, *[str(s) for s in range(10, 33, 2)])
        size_menu.pack(side='left', padx=2)
        # Progress/Time bar
        info_frame = tk.Frame(reader_frame, bg='#eceae4')
        info_frame.pack(fill='x', pady=(5, 0))
        progress_label = tk.Label(info_frame, text='', bg='#eceae4', fg='#444', font=('Segoe UI', 12, 'bold'))
        progress_label.pack(side='left', padx=20)
        time_label = tk.Label(info_frame, text='', bg='#eceae4', fg='#888', font=('Segoe UI', 12))
        time_label.pack(side='right', padx=20)
        # Navigation
        nav_frame = tk.Frame(reader_frame, bg='#eceae4')
        nav_frame.pack(pady=(10, 0))
        prev_btn = tk.Button(nav_frame, text='⟨', font=('Segoe UI', 20, 'bold'), bg='#eceae4', fg='#222', bd=0, activebackground='#d6d3c4', activeforeground='#222', width=3, height=1)
        prev_btn.pack(side='left', padx=20)
        # Ensure page_label is defined before show_page
        page_label = tk.Label(nav_frame, text='', bg='#eceae4', fg='#888', font=('Segoe UI', 10))
        page_label.pack(side='left', padx=10)
        next_btn = tk.Button(nav_frame, text='⟩', font=('Segoe UI', 20, 'bold'), bg='#eceae4', fg='#222', bd=0, activebackground='#d6d3c4', activeforeground='#222', width=3, height=1)
        next_btn.pack(side='left', padx=20)
        # Reading text area (no scroll)
        text_area = tk.Text(reader_frame, wrap='word', font=(font_var.get(), size_var.get()), bg='#f9fafc', fg='#222', bd=0, relief='flat', padx=30, pady=20, height=12)
        text_area.pack(fill='both', expand=True, padx=0, pady=(0, 10))
        text_area.config(state='disabled')
        self.text_area = text_area  # For touch_flip
        # Load and paginate book
        if ext == '.txt':
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        elif ext == '.pdf' and fitz:
            try:
                doc = fitz.open(path)
                text = '\n'.join(page.get_text() for page in doc)
            except Exception as e:
                text = f'Error reading PDF: {e}'
        elif ext == '.epub' and epub:
            try:
                book = epub.read_epub(path)
                text = ''
                for item in book.get_items():
                    if item.get_type() == epub.ITEM_DOCUMENT:
                        text += item.get_content().decode('utf-8', errors='ignore')
                import re
                text = re.sub('<[^<]+?>', '', text)
            except Exception as e:
                text = f'Error reading EPUB: {e}'
        else:
            text = f'Unsupported file type: {ext}. Please add support for this format.'
        # Pagination logic (by word count)
        def get_words_per_page():
            base = 250  # base words for size 18
            size = size_var.get()
            return max(60, int(base * 18 / size))
        def paginate_by_words(text):
            import re
            words = text.split()
            words_per_page = get_words_per_page()
            pages = []
            current_page = []
            count = 0
            chapter_pattern = re.compile(r'^chapter\b', re.IGNORECASE)
            for word in words:
                # If this word starts a chapter, start a new page
                if chapter_pattern.match(word) and current_page:
                    pages.append(' '.join(current_page))
                    current_page = []
                    count = 0
                current_page.append(word)
                count += 1
                if count >= words_per_page:
                    pages.append(' '.join(current_page))
                    current_page = []
                    count = 0
            if current_page:
                pages.append(' '.join(current_page))
            return pages or ['']
        pages = paginate_by_words(text)
        # Navigation logic
        state = {'idx': 0}
        def show_page(idx):
            state['idx'] = max(0, min(idx, len(pages)-1))
            text_area.config(state='normal')
            text_area.delete('1.0', tk.END)
            text_area.insert(tk.END, pages[state['idx']])
            text_area.config(state='disabled')
            page_label.config(text=f'Page {state["idx"]+1} of {len(pages)}')
            prev_btn.config(state='normal' if state['idx'] > 0 else 'disabled')
            next_btn.config(state='normal' if state['idx'] < len(pages)-1 else 'disabled')
        prev_btn.config(command=lambda: show_page(state['idx']-1))
        next_btn.config(command=lambda: show_page(state['idx']+1))
        def update_font(*args):
            text_area.config(font=(font_var.get(), size_var.get()))
            nonlocal pages
            pages = paginate_by_words(text)
            show_page(state['idx'])
        font_var.trace_add('write', update_font)
        size_var.trace_add('write', update_font)
        show_page(0)

    def create_widgets(self):
        self.topbar = tk.Frame(self, bg='#f5f5f3', height=40)
        self.topbar.pack(side='top', fill='x')
        self.title_label = tk.Label(self.topbar, text='Select an ebook', bg='#f5f5f3', fg='#222', font=('Segoe UI', 15, 'bold'))
        self.title_label.pack(side='left', padx=20, pady=5)
        self.sidebar = tk.Frame(self, width=180, bg='#d6d3c4')
        self.sidebar.pack(side='left', fill='y')
        self.library_label = tk.Label(self.sidebar, text='Library', bg='#d6d3c4', fg='#222', font=('Segoe UI', 13, 'bold'))
        self.library_label.pack(pady=10)
        self.library_list = tk.Listbox(self.sidebar, bg='#f5f5f3', fg='#222', font=('Segoe UI', 11), selectbackground='#bdb7a4')
        self.library_list.pack(fill='both', expand=True, padx=10, pady=5)
        self.library_list.bind('<<ListboxSelect>>', self.on_select_ebook)
        self.upload_btn = tk.Button(self.sidebar, text='Upload Ebook', command=self.upload_ebook, bg='#bdb7a4', fg='#222', font=('Segoe UI', 10, 'bold'))
        self.upload_btn.pack(pady=10, padx=10, fill='x')
        self.reader_frame = tk.Frame(self, bg='#eceae4')
        self.reader_frame.pack(side='right', fill='both', expand=True)
        nav_frame = tk.Frame(self.reader_frame, bg='#eceae4')
        nav_frame.pack(pady=10)
        self.prev_btn = tk.Button(nav_frame, text='⟨', command=self.prev_page, font=('Segoe UI', 18), bg='#eceae4', fg='#222', bd=0, activebackground='#d6d3c4', activeforeground='#222')
        self.prev_btn.pack(side='left', padx=30)
        self.page_label = tk.Label(nav_frame, text='', bg='#eceae4', fg='#888', font=('Segoe UI', 10))
        self.page_label.pack(side='left', padx=10)
        self.next_btn = tk.Button(nav_frame, text='⟩', command=self.next_page, font=('Segoe UI', 18), bg='#eceae4', fg='#222', bd=0, activebackground='#d6d3c4', activeforeground='#222')
        self.next_btn.pack(side='left', padx=30)
        # Use a regular Text widget, no scroll
        self.text_area = tk.Text(self.reader_frame, wrap='word', font=('Georgia', 15), bg='#f5f5f3', fg='#222', bd=0, relief='flat', padx=40, pady=20, height=12)
        self.text_area.pack(fill='both', expand=True, padx=60, pady=10)
        self.text_area.config(state='disabled')

    def touch_flip(self, event):
        widget = event.widget
        # Only handle if widget is a text area
        if not hasattr(self, 'text_area') or widget != self.text_area:
            return
        width = self.text_area.winfo_width()
        x = event.x
        if x < width // 3:
            # Simulate left arrow
            self.text_area.event_generate('<<PrevPage>>')
        elif x > 2 * width // 3:
            # Simulate right arrow
            self.text_area.event_generate('<<NextPage>>')

    def refresh_library(self):
        self.library_list.delete(0, tk.END)
        for fname in os.listdir(EBOOKS_DIR):
            if os.path.splitext(fname)[1].lower() in SUPPORTED_EXTENSIONS:
                self.library_list.insert(tk.END, display_title(fname))

    def upload_ebook(self):
        # Only allow supported file types in the dialog
        filetypes = [(f'{ext.upper()} files', f'*{ext}') for ext in SUPPORTED_EXTENSIONS]
        file_path = filedialog.askopenfilename(title='Select Ebook', filetypes=filetypes)
        if file_path:
            fname = os.path.basename(file_path)
            dest = os.path.join(EBOOKS_DIR, fname)
            if os.path.exists(dest):
                messagebox.showinfo('Info', 'Ebook already exists in library.')
                return
            try:
                with open(file_path, 'rb') as src, open(dest, 'wb') as dst:
                    dst.write(src.read())
                self.refresh_library()
            except Exception as e:
                messagebox.showerror('Error', f'Failed to add ebook: {e}')

    def on_select_ebook(self, event):
        selection = self.library_list.curselection()
        if not selection:
            return
        fname = self.library_list.get(selection[0])
        self.open_reader_window(fname)

    def open_reader_window(self, fname):
        ext = os.path.splitext(fname)[1].lower()
        path = os.path.join(EBOOKS_DIR, fname)
        reader_win = tk.Toplevel(self)
        reader_win.title(fname)
        reader_win.geometry('700x500')
        reader_win.configure(bg='#eceae4')
        title_label = tk.Label(reader_win, text=display_title(fname), bg='#f5f5f3', fg='#222', font=('Segoe UI', 15, 'bold'))
        title_label.pack(side='top', fill='x', pady=5)
        # Font controls
        font_frame = tk.Frame(reader_win, bg='#eceae4')
        font_frame.pack(fill='x', pady=(5, 0))
        tk.Label(font_frame, text='Font:', bg='#eceae4', fg='#444', font=('Segoe UI', 11)).pack(side='left', padx=(20, 2))
        font_families = ['Georgia', 'Arial', 'Times New Roman', 'Courier New', 'Segoe UI']
        font_var = tk.StringVar(value='Georgia')
        font_menu = tk.OptionMenu(font_frame, font_var, *font_families)
        font_menu.pack(side='left', padx=2)
        tk.Label(font_frame, text='Size:', bg='#eceae4', fg='#444', font=('Segoe UI', 11)).pack(side='left', padx=(16, 2))
        size_var = tk.IntVar(value=18)
        size_menu = tk.OptionMenu(font_frame, size_var, *[str(s) for s in range(10, 33, 2)])
        size_menu.pack(side='left', padx=2)
        # Navigation
        nav_frame = tk.Frame(reader_win, bg='#eceae4')
        nav_frame.pack(pady=10)
        prev_btn = tk.Button(nav_frame, text='⟨', font=('Segoe UI', 18), bg='#eceae4', fg='#222', bd=0, activebackground='#d6d3c4', activeforeground='#222')
        prev_btn.pack(side='left', padx=30)
        # Ensure page_label is defined before show_page
        page_label = tk.Label(nav_frame, text='', bg='#eceae4', fg='#888', font=('Segoe UI', 10))
        page_label.pack(side='left', padx=10)
        next_btn = tk.Button(nav_frame, text='⟩', font=('Segoe UI', 18), bg='#eceae4', fg='#222', bd=0, activebackground='#d6d3c4', activeforeground='#222')
        next_btn.pack(side='left', padx=30)
        # Use a regular Text widget, no scroll
        text_area = tk.Text(reader_win, wrap='word', font=(font_var.get(), size_var.get()), bg='#f5f5f3', fg='#222', bd=0, relief='flat', padx=40, pady=20, height=12)
        text_area.pack(fill='both', expand=True, padx=60, pady=10)
        text_area.config(state='disabled')
        # Load and paginate book
        if ext == '.txt':
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        elif ext == '.pdf' and fitz:
            try:
                doc = fitz.open(path)
                text = '\n'.join(page.get_text() for page in doc)
            except Exception as e:
                text = f'Error reading PDF: {e}'
        elif ext == '.epub' and epub:
            try:
                book = epub.read_epub(path)
                text = ''
                for item in book.get_items():
                    if item.get_type() == epub.ITEM_DOCUMENT:
                        text += item.get_content().decode('utf-8', errors='ignore')
                import re
                text = re.sub('<[^<]+?>', '', text)
            except Exception as e:
                text = f'Error reading EPUB: {e}'
        else:
            text = f'Unsupported file type: {ext}. Please add support for this format.'
        # Pagination logic (by word count)
        def get_words_per_page():
            base = 250  # base words for size 18
            size = size_var.get()
            return max(60, int(base * 18 / size))
        def paginate_by_words(text):
            import re
            words = text.split()
            words_per_page = get_words_per_page()
            pages = []
            current_page = []
            count = 0
            chapter_pattern = re.compile(r'^chapter\b', re.IGNORECASE)
            for word in words:
                # If this word starts a chapter, start a new page
                if chapter_pattern.match(word) and current_page:
                    pages.append(' '.join(current_page))
                    current_page = []
                    count = 0
                current_page.append(word)
                count += 1
                if count >= words_per_page:
                    pages.append(' '.join(current_page))
                    current_page = []
                    count = 0
            if current_page:
                pages.append(' '.join(current_page))
            return pages or ['']
        pages = paginate_by_words(text)
        # Navigation logic
        state = {'idx': 0}
        def show_page(idx):
            state['idx'] = max(0, min(idx, len(pages)-1))
            text_area.config(state='normal')
            text_area.delete('1.0', tk.END)
            text_area.insert(tk.END, pages[state['idx']])
            text_area.config(state='disabled')
            page_label.config(text=f'Page {state["idx"]+1} of {len(pages)}')
            prev_btn.config(state='normal' if state['idx'] > 0 else 'disabled')
            next_btn.config(state='normal' if state['idx'] < len(pages)-1 else 'disabled')
        prev_btn.config(command=lambda: show_page(state['idx']-1))
        next_btn.config(command=lambda: show_page(state['idx']+1))
        def update_font(*args):
            text_area.config(font=(font_var.get(), size_var.get()))
            nonlocal pages
            pages = paginate_by_words(text)
            show_page(state['idx'])
        font_var.trace_add('write', update_font)
        size_var.trace_add('write', update_font)
        show_page(0)

    def show_page(self, idx):
        if not self.current_pages:
            self.text_area.config(state='normal')
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert(tk.END, 'No content.')
            self.text_area.config(state='disabled')
            self.page_label.config(text='')
            self.prev_btn.config(state='disabled')
            self.next_btn.config(state='disabled')
            return
        self.current_page_idx = max(0, min(idx, len(self.current_pages)-1))
        self.text_area.config(state='normal')
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert(tk.END, self.current_pages[self.current_page_idx])
        self.text_area.config(state='disabled')
        self.page_label.config(text=f'Page {self.current_page_idx+1} of {len(self.current_pages)}')
        self.prev_btn.config(state='normal' if self.current_page_idx > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_page_idx < len(self.current_pages)-1 else 'disabled')
        # Update topbar title
        if self.current_book:
            self.title_label.config(text=self.current_book)
        else:
            self.title_label.config(text='Select an ebook')

    def prev_page(self):
        if self.current_page_idx > 0:
            self.show_page(self.current_page_idx - 1)

    def next_page(self):
        if self.current_page_idx < len(self.current_pages)-1:
            self.show_page(self.current_page_idx + 1)

    def _on_swipe_start(self, event):
        self._swipe_x = event.x

    def _on_swipe_end(self, event, show_page, state, total_pages):
        dx = event.x - getattr(self, '_swipe_x', event.x)
        threshold = 60  # Minimum pixels to count as a swipe
        if dx > threshold and state['idx'] > 0:
            show_page(state['idx']-1)
        elif dx < -threshold and state['idx'] < total_pages-1:
            show_page(state['idx']+1)

if __name__ == '__main__':
    app = EbookReaderApp()
    app.mainloop()
