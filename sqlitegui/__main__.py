import sqlite3
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import tkinter.ttk as ttk
import sys

class DBContainer(object):
    def __init__(self):
        self.db = None
        self.cur = None

    def GetTables(self, path):
        self.db = sqlite3.connect(path)
        self.cur = self.db.cursor()
        table_query = self.cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

        tables = []

        for t in table_query:
            tables.append(t[0])
        return tables

    def GetTableData(self, table_name):
        headers = []
        values = []

        for h in self.cur.execute("PRAGMA table_info('%s')" % table_name):
            headers.append(h[1])

        for row in self.cur.execute('SELECT * FROM %s' % table_name):
            values.append(row[:])

        return (headers, values)

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.grid(sticky=tk.NSEW)
        top=self.winfo_toplevel()
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight= 20)
        self.columnconfigure(1, weight= 0)
        self.columnconfigure(2, weight= 80)
        self.columnconfigure(3, weight= 0)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=100)
        self.db = DBContainer()
        self.CreateWidgets()

    def CreateWidgets(self):
        self.TableContent = ttk.Treeview(self)
        self.TableContent.grid(row=1, column=2, sticky=tk.NSEW)
        #the DBTree widget will display the tables contained in a database
        self.DBTree = ttk.Treeview(self, show='tree')
        self.DBTree.bind('<<TreeviewSelect>>', self.TreeSelect)
        self.DBTree.grid(row=1, column=0, sticky=tk.NSEW)
        self.TreeScroll = ttk.Scrollbar(self, orient = tk.VERTICAL, command=self.DBTree.yview)
        self.DBTree['yscrollcommand'] = self.TreeScroll.set
        self.TreeScroll.grid(row=1, column=1, sticky=tk.NS)
        #the menubar and corresponding buttons
        top=self.winfo_toplevel()
        self.MenuBar = tk.Menu(top)
        top['menu']=self.MenuBar
        self.FileMenu = tk.Menu(self.MenuBar, tearoff=0)
        self.MenuBar.add_cascade(label='File', menu=self.FileMenu)
        self.FileMenu.add_command(label='Open database...', command=self.OpenDatabase)

    def OpenDatabase(self):
        self.FilePath = filedialog.askopenfilename(initialdir='C:\\', \
            title='Select database', filetypes=(('all files','*.*'),))
        try:
            self.BuildTree(self.db.GetTables(self.FilePath))
        except BaseException as e:
            messagebox.showerror("Error", e)

    def DisplayTable(self, heads, vals):
        #we destroy the table first so we can remake it with the proper number
        #of columns
        self.TableContent.destroy()
        self.TableContent = ttk.Treeview(self, columns=heads)
        #tuck away the icon column since we won't use it
        self.TableContent.column('#0', minwidth=0, width=0, stretch=False)

        for c in heads:
             self.TableContent.heading(c, text=c)
             #coaxing the widget into expanding past the right edge of the
             #application, so the scrollbars will work
             self.TableContent.column(c, stretch=True, width=0, minwidth=200)

        for v in vals:
            self.TableContent.insert('', 'end', values=v)

        self.TableContent.grid(row=1, column=2, sticky=tk.NSEW)
        self.ScrollX = ttk.Scrollbar(self, orient = tk.HORIZONTAL, command=self.TableContent.xview)
        self.TableContent['xscrollcommand'] = self.ScrollX.set
        self.ScrollX.grid(row=2, column=2, sticky=tk.EW)

        self.ScrollY = ttk.Scrollbar(self, orient = tk.VERTICAL, command=self.TableContent.yview)
        self.TableContent['yscrollcommand'] = self.ScrollY.set
        self.ScrollY.grid(row=1, column=3, sticky=tk.NS)

    def BuildTree(self, tables):
        self.TreeClean()
        for t in tables:
            self.DBTree.insert('', 'end', text=t, iid=t)

    def TreeSelect(self, event):
        selected_table = self.DBTree.focus()
        headers, values = self.db.GetTableData(selected_table)
        self.DisplayTable(headers, values)

    def TreeClean(self):
        for i in self.DBTree.get_children(''):
            self.DBTree.delete(i)

app = Application()
app.master.title('SQLiteGUI')
app.mainloop()
