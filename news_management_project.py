
import sys
import os
import pymysql
from pymysql.cursors import DictCursor
import customtkinter as ctk
from tkinter import messagebox as tkmb, filedialog
from tkinter import END
from datetime import datetime

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASS = ""           
DB_NAME = "news_portal"

APP_TITLE = "News Portal — Editor"

def get_connection():
    return pymysql.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS,
        database=DB_NAME, cursorclass=DictCursor,
        autocommit=False, connect_timeout=5
    )

# CRUD 

def create_author(name, email, bio=""):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO Authors (name,email,bio) VALUES (%s,%s,%s)", (name,email,bio))
        conn.commit()
    finally:
        conn.close()

def find_author_by_name_and_email(name, email):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT author_id,name FROM Authors WHERE name=%s AND email=%s", (name,email))
            return cur.fetchone()
    finally:
        conn.close()

def fetch_categories():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT category_id,category_name FROM Categories ORDER BY category_name")
            return cur.fetchall()
    finally:
        conn.close()

def create_category(category_name):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO Categories (category_name) VALUES (%s)", (category_name,))
        conn.commit()
    finally:
        conn.close()

def create_article(title, content, author_id, category_id, published=True):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO Articles (title,content,author_id,category_id,is_published) VALUES (%s,%s,%s,%s,%s)",
                (title, content, author_id, category_id, int(bool(published)))
            )
        conn.commit()
    finally:
        conn.close()

def update_article(article_id, title, content, published=True):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE Articles SET title=%s, content=%s, is_published=%s WHERE article_id=%s",
                (title, content, int(bool(published)), article_id)
            )
        conn.commit()
    finally:
        conn.close()

def delete_article(article_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM Articles WHERE article_id=%s", (article_id,))
        conn.commit()
    finally:
        conn.close()

def fetch_articles(search="", only_mine=None, category=None):
    base = (
        "SELECT A.article_id, A.title, A.content, A.publication_date, "
        "Auth.name AS author, Cat.category_name, A.author_id "
        "FROM Articles A "
        "LEFT JOIN Authors Auth ON A.author_id = Auth.author_id "
        "LEFT JOIN Categories Cat ON A.category_id = Cat.category_id "
        "WHERE A.is_published = TRUE "
    )
    params = []
    if search:
        base += " AND (A.title LIKE %s OR A.content LIKE %s OR Auth.name LIKE %s OR Cat.category_name LIKE %s)"
        q = "%" + search + "%"
        params.extend([q, q, q, q])
    if only_mine:
        base += " AND A.author_id = %s"
        params.append(only_mine)
    if category:
        base += " AND Cat.category_name = %s"
        params.append(category)
    base += " ORDER BY A.publication_date DESC"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(base, tuple(params))
            return cur.fetchall()
    finally:
        conn.close()

def fetch_article_by_id(article_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT A.article_id, A.title, A.content, A.publication_date, "
                "Auth.name AS author, Cat.category_name "
                "FROM Articles A "
                "LEFT JOIN Authors Auth ON A.author_id = Auth.author_id "
                "LEFT JOIN Categories Cat ON A.category_id = Cat.category_id "
                "WHERE A.article_id = %s",
                (article_id,)
            )
            return cur.fetchone()
    finally:
        conn.close()


# UI HELPERSS
def center_window(win, w, h):
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    x = (sw // 2) - (w // 2)
    y = (sh // 2) - (h // 2)
    win.geometry("%dx%d+%d+%d" % (w, h, x, y))

def bring_to_front(win):
    try:
        win.lift()
        win.attributes("-topmost", True)
        win.after(200, lambda: win.attributes("-topmost", False))
        win.focus_force()
    except Exception:
        pass

def preview_text(s, n=140):
    if not s:
        return ""
    s = s.strip()
    return s if len(s) <= n else s[:n].rstrip() + "..."

# ---------------------------
# VISUAL THEME
# ---------------------------
NAV_BG = "#071022"
PANEL_BG = "#071028"
ACCENT = "#ff6b00"
FG = "#E6EEF3"
TITLE_FONT = ("Segoe UI", 14, "bold")
META_FONT = ("Segoe UI", 10)

# ---------------------------
# MAIN DASHBOARD
# ---------------------------
class Dashboard(ctk.CTkToplevel):
    def __init__(self, master, author_row):
        super().__init__(master)
        self.master = master
        if isinstance(author_row, dict):
            self.author_id = author_row.get("author_id")
            self.author_name = author_row.get("name")
        else:
            self.author_id = author_row[0]
            self.author_name = author_row[1]

        self.title("News Portal — Dashboard")
        center_window(self, 1000, 640)
        self.configure(fg_color=PANEL_BG)
        bring_to_front(self)

        # layout
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        self.current_search = ""
        self.current_category = None

        self.create_sidebar()
        self.create_toolbar()
        self.create_article_list()
        self.create_reader_panel()
        self.create_status_bar()

        self.refresh_categories()
        self.load_articles()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=NAV_BG)
        self.sidebar.grid(row=0, column=0, sticky="nsw", padx=(8,4), pady=8)
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="NEWS PORTAL", font=("Georgia", 16, "bold"), text_color=ACCENT).pack(pady=(12,6))
        ctk.CTkLabel(self.sidebar, text="Editor: %s" % self.author_name, text_color=FG, font=META_FONT).pack(pady=(0,8))

        ctk.CTkButton(self.sidebar, text="Create Article", fg_color=ACCENT, command=self.open_create).pack(fill="x", padx=12, pady=6)
        ctk.CTkButton(self.sidebar, text="All Articles", fg_color="#123", command=self.show_all).pack(fill="x", padx=12, pady=6)
        ctk.CTkButton(self.sidebar, text="My Articles", fg_color="#123", command=self.show_my).pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(self.sidebar, text="Category", text_color=FG, font=META_FONT).pack(pady=(12,4))
        self.cat_combo = ctk.CTkOptionMenu(self.sidebar, values=["All"], command=self.on_category_change, width=180)
        self.cat_combo.pack(pady=(0,8))
        ctk.CTkButton(self.sidebar, text="Manage Categories", fg_color="#2A3B50", command=self.open_categories).pack(padx=12, pady=6, fill="x")

        ctk.CTkButton(self.sidebar, text="Logout", fg_color="#7a2b2b", command=self.logout).pack(padx=12, pady=6, fill="x")
        ctk.CTkButton(self.sidebar, text="Quit App", fg_color="#444444", command=self.quit_app).pack(padx=12, pady=6, fill="x")

    def create_toolbar(self):
        toolbar = ctk.CTkFrame(self, height=48, fg_color="#071022")
        toolbar.grid(row=1, column=1, columnspan=2, sticky="ew", padx=8, pady=(8,0))
        toolbar.grid_propagate(False)
        toolbar.columnconfigure(0, weight=1)

        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(toolbar, placeholder_text="Search title, content, author or category...", textvariable=self.search_var, width=520)
        search_entry.grid(row=0, column=0, padx=(12,6), pady=8, sticky="w")
        search_entry.bind("<Return>", lambda e: self.on_search())
        search_entry.bind("<KeyRelease>", lambda e: self.on_search_live())

        ctk.CTkButton(toolbar, text="Search", width=80, fg_color=ACCENT, command=self.on_search).grid(row=0, column=1, padx=6)
        ctk.CTkButton(toolbar, text="Refresh", width=80, fg_color="#2A3B50", command=self.load_articles).grid(row=0, column=2, padx=6)
        ctk.CTkButton(toolbar, text="Export", width=80, fg_color="#2A3B50", command=self.export_current).grid(row=0, column=3, padx=6)

    def create_article_list(self):
        container = ctk.CTkFrame(self, fg_color=PANEL_BG)
        container.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(4,4), pady=8)
        container.columnconfigure(0, weight=1)
        ctk.CTkLabel(container, text="Articles", font=("Segoe UI", 16, "bold"), text_color=FG).pack(anchor="w", padx=12, pady=(8,4))
        self.articles_frame = ctk.CTkScrollableFrame(container, width=520, height=520, fg_color="#071022")
        self.articles_frame.pack(fill="both", expand=True, padx=12, pady=6)

    def create_reader_panel(self):
        panel = ctk.CTkFrame(self, fg_color="#0b1724")
        panel.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(4,8), pady=8)
        panel.columnconfigure(0, weight=1)
        ctk.CTkLabel(panel, text="Reader", font=("Segoe UI", 16, "bold"), text_color=FG).pack(anchor="w", padx=12, pady=(8,4))
        self.reader_title = ctk.CTkLabel(panel, text="Select an article to read", font=TITLE_FONT, wraplength=360, text_color=FG)
        self.reader_title.pack(anchor="w", padx=12)
        self.reader_meta = ctk.CTkLabel(panel, text="", text_color="gray", font=META_FONT)
        self.reader_meta.pack(anchor="w", padx=12, pady=(0,8))
        self.reader_text = ctk.CTkTextbox(panel, width=420, height=420)
        self.reader_text.pack(padx=12, pady=6, fill="both", expand=True)
        self.reader_text.configure(state="disabled")
        btn_frame = ctk.CTkFrame(panel, fg_color="transparent")
        btn_frame.pack(padx=12, pady=6, anchor="e")
        ctk.CTkButton(btn_frame, text="Read in Window", command=self.open_read_window).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Edit", command=self.open_edit_selected).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Delete", fg_color="#b01b1b", command=self.delete_selected).pack(side="left", padx=6)
        self.current_article_id = None

    def create_status_bar(self):
        footer = ctk.CTkFrame(self, height=28, fg_color="#071022")
        footer.grid(row=2, column=0, columnspan=3, sticky="ew")
        footer.grid_propagate(False)
        self.status_label = ctk.CTkLabel(footer, text="Ready", text_color="gray", font=META_FONT)
        self.status_label.pack(anchor="w", padx=8)

    # Actions
    def refresh_categories(self):
        cats = fetch_categories()
        names = ["All"]
        for c in cats:
            names.append(c["category_name"])
        self.cat_combo.configure(values=names)
        self.cat_combo.set("All")

    def on_category_change(self, choice):
        self.current_category = None if choice == "All" else choice
        self.load_articles()

    def on_search(self):
        self.current_search = self.search_var.get().strip()
        self.load_articles()

    def on_search_live(self):
        self.current_search = self.search_var.get().strip()
        self.load_articles()

    def load_articles(self):
        self.status("Loading articles...")
        for w in self.articles_frame.winfo_children():
            w.destroy()
        rows = fetch_articles(search=self.current_search, only_mine=None, category=self.current_category)
        if not rows:
            ctk.CTkLabel(self.articles_frame, text="No articles found.", text_color="gray").pack(pady=12)
            self.reader_title.configure(text="Select an article")
            self.reader_text.configure(state="normal"); self.reader_text.delete("0.0", "end"); self.reader_text.configure(state="disabled")
            self.current_article_id = None
            self.status("No articles")
            return
        for r in rows:
            card = ctk.CTkFrame(self.articles_frame, fg_color="#08121b", corner_radius=6)
            card.pack(fill="x", padx=8, pady=6)
            ctk.CTkLabel(card, text=r["title"], font=TITLE_FONT, anchor="w").pack(anchor="w", padx=8, pady=(6,0))
            meta = "%s  •  %s  •  %s" % (
                r.get("author") or "Unknown",
                r.get("category_name") or "Uncategorized",
                r.get("publication_date").strftime("%Y-%m-%d") if hasattr(r.get("publication_date"), "strftime") else r.get("publication_date")
            )
            ctk.CTkLabel(card, text=meta, font=META_FONT, text_color="gray").pack(anchor="w", padx=8)
            ctk.CTkLabel(card, text=preview_text(r.get("content", ""), 200), wraplength=520, anchor="w").pack(anchor="w", padx=8, pady=(0,8))
            btns = ctk.CTkFrame(card, fg_color="transparent")
            btns.pack(anchor="e", padx=8, pady=(0,8))
            ctk.CTkButton(btns, text="Read", width=80, command=lambda id=r["article_id"]: self.select_article(id)).pack(side="left", padx=4)
            ctk.CTkButton(btns, text="Open", width=80, command=lambda id=r["article_id"]: self.open_read_window(id)).pack(side="left", padx=4)
            if r.get("author_id") == self.author_id:
                ctk.CTkButton(btns, text="Edit", width=70, command=lambda id=r["article_id"]: self.open_edit_window(id)).pack(side="left", padx=4)
                ctk.CTkButton(btns, text="Delete", width=70, fg_color="#b01b1b", command=lambda id=r["article_id"]: self.confirm_delete(id)).pack(side="left", padx=4)
        # auto-select first
        self.select_article(rows[0]["article_id"])
        self.status("Loaded %d articles" % len(rows))

    def select_article(self, article_id):
        data = fetch_article_by_id(article_id)
        if not data:
            self.status("Article not found")
            return
        self.current_article_id = article_id
        self.reader_title.configure(text=data.get("title", ""))
        meta = "By %s  •  %s  •  %s" % (
            data.get("author") or "Unknown",
            data.get("category_name") or "Uncategorized",
            data.get("publication_date")
        )
        self.reader_meta.configure(text=meta)
        self.reader_text.configure(state="normal")
        self.reader_text.delete("0.0", "end")
        self.reader_text.insert("0.0", data.get("content", ""))
        self.reader_text.configure(state="disabled")

    def open_read_window(self, article_id=None):
        aid = article_id or self.current_article_id
        if not aid:
            tkmb.showinfo("No article", "No article selected to read.", parent=self)
            return
        data = fetch_article_by_id(aid)
        if not data:
            tkmb.showerror("Error", "Article not found.", parent=self)
            return
        win = ctk.CTkToplevel(self)
        win.title(data.get("title", "Article"))
        center_window(win, 760, 640)
        bring_to_front(win)
        ctk.CTkLabel(win, text=data.get("title", ""), font=("Georgia", 16, "bold"), wraplength=720).pack(padx=12, pady=(8,6))
        ctk.CTkLabel(win, text="By %s  •  %s  •  %s" % (data.get("author"), data.get("category_name"), data.get("publication_date")), text_color="gray").pack(padx=12)
        tb = ctk.CTkTextbox(win, width=720, height=470)
        tb.pack(padx=12, pady=8, fill="both", expand=True)
        tb.insert("0.0", data.get("content", ""))
        tb.configure(state="disabled")
        def export_to_txt():
            f = filedialog.asksaveasfilename(title="Export Article as .txt", defaultextension=".txt",
                                             filetypes=[("Text files","*.txt")], initialfile=(data.get("title") or "article") + ".txt")
            if f:
                try:
                    with open(f, "w", encoding="utf-8") as fh:
                        fh.write("%s\nBy %s • %s\n\n%s" % (data.get("title"), data.get("author"), data.get("category_name"), data.get("content")))
                    tkmb.showinfo("Exported", "Article exported to:\n%s" % f, parent=win)
                except Exception as exc:
                    tkmb.showerror("Error", "Could not save file:\n%s" % exc, parent=win)
        btns = ctk.CTkFrame(win, fg_color="transparent")
        btns.pack(padx=12, pady=8, anchor="e")
        ctk.CTkButton(btns, text="Export", fg_color=ACCENT, command=export_to_txt).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Close", fg_color="#444", command=win.destroy).pack(side="left", padx=6)

    def open_create(self):
        cats = fetch_categories()
        if not cats:
            tkmb.showwarning("No categories", "Please create a category before publishing.", parent=self)
            return
        win = ctk.CTkToplevel(self)
        win.title("Create Article")
        center_window(win, 640, 560)
        bring_to_front(win)
        frame = ctk.CTkFrame(win, fg_color="transparent")
        frame.pack(padx=12, pady=12, fill="both", expand=True)
        ctk.CTkLabel(frame, text="New Article", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        title_e = ctk.CTkEntry(frame, placeholder_text="Title", width=560)
        title_e.pack(pady=8)
        names = [c["category_name"] for c in cats]
        combo = ctk.CTkOptionMenu(frame, values=names, width=300)
        combo.pack(pady=6)
        body = ctk.CTkTextbox(frame, width=620, height=300)
        body.pack(pady=8)
        def save():
            t = title_e.get().strip(); b = body.get("1.0", END).strip(); sel = combo.get()
            if not (t and b and sel):
                tkmb.showwarning("Missing", "All fields are required.", parent=win)
                return
            cid = None
            for c in cats:
                if c["category_name"] == sel:
                    cid = c["category_id"]
                    break
            create_article(t, b, self.author_id, cid)
            tkmb.showinfo("Published", "Article published successfully.", parent=win)
            win.destroy()
            self.load_articles()
        ctk.CTkButton(frame, text="Publish", fg_color=ACCENT, command=save).pack(pady=6, anchor="e")

    def open_edit_selected(self):
        if not self.current_article_id:
            tkmb.showinfo("No selection", "Select an article first.", parent=self)
            return
        self.open_edit_window(self.current_article_id)

    def open_edit_window(self, aid):
        data = fetch_article_by_id(aid)
        if not data:
            tkmb.showerror("Error", "Article not found.", parent=self)
            return
        win = ctk.CTkToplevel(self)
        win.title("Edit Article")
        center_window(win, 640, 560)
        bring_to_front(win)
        frame = ctk.CTkFrame(win, fg_color="transparent")
        frame.pack(padx=12, pady=12, fill="both", expand=True)
        title_e = ctk.CTkEntry(frame, width=560)
        title_e.insert(0, data.get("title", ""))
        title_e.pack(pady=8)
        body = ctk.CTkTextbox(frame, width=620, height=340)
        body.insert("0.0", data.get("content", ""))
        body.pack(pady=8)
        def save():
            t = title_e.get().strip(); b = body.get("1.0", END).strip()
            if not (t and b):
                tkmb.showwarning("Missing", "Title and content required.", parent=win)
                return
            update_article(aid, t, b)
            tkmb.showinfo("Saved", "Article updated.", parent=win)
            win.destroy()
            self.load_articles()
        ctk.CTkButton(frame, text="Save Changes", fg_color=ACCENT, command=save).pack(pady=6, anchor="e")

    def delete_selected(self):
        if not self.current_article_id:
            tkmb.showinfo("No selection", "Choose an article first.", parent=self)
            return
        self.confirm_delete(self.current_article_id)

    def confirm_delete(self, aid):
        if tkmb.askyesno("Confirm", "Delete this article?", parent=self):
            delete_article(aid)
            tkmb.showinfo("Deleted", "Article deleted.", parent=self)
            self.load_articles()

    def open_categories(self):
        win = ctk.CTkToplevel(self)
        win.title("Manage Categories")
        center_window(win, 420, 320)
        bring_to_front(win)
        frame = ctk.CTkFrame(win, fg_color="transparent")
        frame.pack(padx=12, pady=12, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Add New Category", font=META_FONT).pack(anchor="w")
        entry = ctk.CTkEntry(frame, placeholder_text="Category name", width=280)
        entry.pack(pady=8)
        def save():
            name = entry.get().strip()
            if not name:
                tkmb.showwarning("Missing", "Category name required.", parent=win)
                return
            try:
                create_category(name)
            except Exception as e:
                tkmb.showerror("Error", str(e), parent=win)
                return
            tkmb.showinfo("Saved", "Category created.", parent=win)
            win.destroy()
            self.refresh_categories()
            self.load_articles()
        ctk.CTkButton(frame, text="Create", fg_color=ACCENT, command=save).pack(pady=8)

    def show_my(self):
        # show all but editing/deleting restricted to owner already
        self.current_search = ""
        self.current_category = None
        self.load_articles()
        self.status("Showing all articles (use search to filter)")

    def show_all(self):
        self.current_search = ""
        self.current_category = None
        self.load_articles()
        self.status("Showing all articles")

    def export_current(self):
        if not self.current_article_id:
            tkmb.showinfo("No article", "Select an article first to export.", parent=self)
            return
        data = fetch_article_by_id(self.current_article_id)
        if not data:
            tkmb.showerror("Error", "Article not found.", parent=self)
            return
        filename = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=(data.get("title") or "article") + ".txt")
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as fh:
                    fh.write("%s\nBy %s • %s\n\n%s" % (data.get("title"), data.get("author"), data.get("category_name"), data.get("content")))
                tkmb.showinfo("Exported", "Article saved to:\n%s" % filename, parent=self)
            except Exception as exc:
                tkmb.showerror("Error", "Could not write file:\n%s" % exc, parent=self)

    def logout(self):
        if tkmb.askyesno("Logout", "Return to login screen?", parent=self):
            self.destroy()
            self.master.deiconify()

    def quit_app(self):
        if tkmb.askyesno("Quit", "Exit application?", parent=self):
            self.master.destroy()
            sys.exit(0)

    def status(self, text):
        self.status_label.configure(text=text)

# ---------------------------
# LOGIN APP (entry)
# ---------------------------
class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        center_window(self, 480, 380)
        self.configure(fg_color=PANEL_BG)
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="News Portal — Editor Login", font=("Georgia", 18, "bold"), text_color=ACCENT).pack(pady=(16,6))
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(padx=16, pady=8, fill="both", expand=True)
        ctk.CTkLabel(frame, text="Name", text_color=FG).pack(anchor="w", pady=(6,0))
        self.name = ctk.CTkEntry(frame, placeholder_text="Full name", width=360)
        self.name.pack(pady=6)
        ctk.CTkLabel(frame, text="Email (acts as password)", text_color=FG).pack(anchor="w", pady=(6,0))
        self.email = ctk.CTkEntry(frame, placeholder_text="Email", width=360)
        self.email.pack(pady=6)
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=12)
        ctk.CTkButton(btn_frame, text="Log In", width=140, fg_color=ACCENT, command=self.attempt_login).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Register", width=140, fg_color="#2A3B50", command=self.open_register).pack(side="left", padx=6)
        ctk.CTkButton(self, text="Quit", fg_color="#444444", command=self.quit_app).pack(side="bottom", pady=12)

    def attempt_login(self):
        n = self.name.get().strip(); e = self.email.get().strip()
        if not (n and e):
            tkmb.showwarning("Missing", "Enter name and email", parent=self)
            return
        try:
            row = find_author_by_name_and_email(n, e)
        except Exception as exc:
            tkmb.showerror("DB Error", "Could not connect/query DB:\n%s" % exc, parent=self)
            return
        if row:
            self.withdraw()
            dash = Dashboard(self, row)
            dash.protocol("WM_DELETE_WINDOW", lambda: (dash.destroy(), self.deiconify()))
            dash.focus_force()
        else:
            tkmb.showerror("Login failed", "Invalid name or email. Or register new author.", parent=self)

    def open_register(self):
        win = ctk.CTkToplevel(self)
        win.title("Register Author")
        center_window(win, 420, 320)
        bring_to_front(win)
        frm = ctk.CTkFrame(win, fg_color="transparent")
        frm.pack(padx=12, pady=12, fill="both", expand=True)
        ctk.CTkLabel(frm, text="Register new author", font=META_FONT).pack(anchor="w")
        n = ctk.CTkEntry(frm, placeholder_text="Full name", width=320); n.pack(pady=6)
        e = ctk.CTkEntry(frm, placeholder_text="Email", width=320); e.pack(pady=6)
        b = ctk.CTkEntry(frm, placeholder_text="Bio (optional)", width=320); b.pack(pady=6)
        def save():
            if not (n.get().strip() and e.get().strip()):
                tkmb.showwarning("Missing", "Name and Email required", parent=win); return
            try:
                create_author(n.get().strip(), e.get().strip(), b.get().strip())
            except pymysql.err.IntegrityError:
                tkmb.showerror("Error", "Author or email already exists", parent=win); return
            except Exception as exc:
                tkmb.showerror("Error", "%s" % exc, parent=win); return
            tkmb.showinfo("Registered", "You can now login", parent=win)
            win.destroy()
        ctk.CTkButton(frm, text="Sign Up", fg_color=ACCENT, command=save).pack(pady=8)

    def quit_app(self):
        if tkmb.askyesno("Quit", "Exit application?", parent=self):
            self.destroy()
            sys.exit(0)

# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    try:
        app = LoginApp()
        app.mainloop()
    except Exception as e:
        tkmb.showerror("Fatal", "App error: %s" % e)
        sys.exit(1)
