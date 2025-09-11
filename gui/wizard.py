# gui/wizard.py
import os, sys, pathlib, threading, queue, subprocess, webbrowser, platform, json, shutil
import tkinter as tk
from tkinter import ttk, messagebox

APPDIR = pathlib.Path(getattr(sys, '_MEIPASS', pathlib.Path(__file__).resolve().parent.parent))
BIN_NAME = 'quietpatch.exe' if os.name == 'nt' else 'quietpatch'
CLI = (APPDIR / BIN_NAME)

# Cross‑platform app data/log dir
if sys.platform.startswith('win'):
    DATA_DIR = pathlib.Path(os.getenv('PROGRAMDATA', 'C:/ProgramData')) / 'QuietPatch'
elif sys.platform == 'darwin':
    DATA_DIR = pathlib.Path.home() / 'Library' / 'Application Support' / 'QuietPatch'
else:
    DATA_DIR = pathlib.Path.home() / '.local' / 'share' / 'QuietPatch'
LOGS = DATA_DIR / 'logs'
REPORTS = DATA_DIR / 'reports'
TEMPLATES = APPDIR / 'resources' / 'templates'
for p in (LOGS, REPORTS):
    p.mkdir(parents=True, exist_ok=True)

APP_STATE = {
    'last_report': None,
    'log_tail': '',
}

class Wizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('QuietPatch')
        self.geometry('760x520')
        self.resizable(True, True)
        self.style = ttk.Style(self); self.style.theme_use('clam')
        self.container = ttk.Frame(self); self.container.pack(fill='both', expand=True, padx=14, pady=14)
        self.frames = {}
        for F in (Welcome, Options, Progress):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        self.show('Welcome')

    def show(self, name: str):
        self.container.rowconfigure(0, weight=1); self.container.columnconfigure(0, weight=1)
        self.frames[name].tkraise()

    # Error dialog per UX spec
    def err(self, title: str, impact: str, steps: list[str], fix_cmd: str | None = None, diag: str | None = None):
        dlg = tk.Toplevel(self); dlg.title(title); dlg.geometry('580x420'); dlg.transient(self); dlg.grab_set()
        ttk.Label(dlg, text=title, font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(10,6), padx=12)
        ttk.Label(dlg, text=f"Impact: {impact}", wraplength=540).pack(anchor='w', padx=12)
        frm = ttk.Frame(dlg); frm.pack(fill='both', expand=True, padx=12, pady=8)
        ttk.Label(frm, text='Steps to resolve:').pack(anchor='w')
        txt = tk.Text(frm, height=6, wrap='word'); txt.pack(fill='both', expand=True)
        for i, s in enumerate(steps, 1): txt.insert('end', f"{i}. {s}\n")
        txt.config(state='disabled')
        btns = ttk.Frame(dlg); btns.pack(fill='x', pady=8)
        if fix_cmd:
            def run_fix():
                try:
                    subprocess.Popen(fix_cmd, shell=True)
                except Exception as e:
                    messagebox.showerror('QuietPatch', f'Could not run fix: {e}')
            ttk.Button(btns, text='Fix', command=run_fix).pack(side='left')
        if diag:
            def copy_diag():
                self.clipboard_clear(); self.clipboard_append(diag); self.update()
                messagebox.showinfo('QuietPatch', 'Diagnostics copied.')
            ttk.Button(btns, text='Copy diagnostics', command=copy_diag).pack(side='left', padx=6)
        ttk.Button(btns, text='Close', command=dlg.destroy).pack(side='right')

class Welcome(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.c = controller
        ttk.Label(self, text='QuietPatch', font=('Segoe UI', 16, 'bold')).pack(anchor='w')
        ttk.Label(self, text='Private, offline patch advisor. No telemetry.', foreground='#666').pack(anchor='w', pady=(0,8))
        desc = ('Click Start to scan your apps and generate a deterministic report.\n'
                'Default mode is Read‑only: no changes will be made.')
        ttk.Label(self, text=desc, wraplength=700).pack(anchor='w', pady=(0,14))
        ttk.Button(self, text='Start', command=lambda: self.c.show('Options')).pack(anchor='center')

class Options(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.c = controller
        ttk.Label(self, text='Scan Options', font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        self.var_readonly = tk.BooleanVar(value=True)
        self.var_offline = tk.BooleanVar(value=True)
        self.var_deep = tk.BooleanVar(value=False)
        grid = ttk.Frame(self); grid.pack(anchor='w', pady=8)
        ttk.Checkbutton(grid, text='Read‑only (no changes)', variable=self.var_readonly).grid(row=0, column=0, sticky='w')
        ttk.Checkbutton(grid, text='Offline mode (no network)', variable=self.var_offline).grid(row=1, column=0, sticky='w')
        ttk.Checkbutton(grid, text='Deep component scan (slower)', variable=self.var_deep).grid(row=2, column=0, sticky='w')
        btns = ttk.Frame(self); btns.pack(fill='x', pady=10)
        ttk.Button(btns, text='Back', command=lambda: self.c.show('Welcome')).pack(side='left')
        ttk.Button(btns, text='Run Scan', command=self.run).pack(side='right')

    def run(self):
        opts = {
            'readonly': self.var_readonly.get(),
            'offline': self.var_offline.get(),
            'deep': self.var_deep.get(),
        }
        self.c.frames['Progress'].start_scan(opts)
        self.c.show('Progress')

class Progress(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.c = controller
        ttk.Label(self, text='Scanning…', font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        self.pb = ttk.Progressbar(self, mode='indeterminate'); self.pb.pack(fill='x', pady=6)
        self.out = tk.Text(self, height=18, wrap='word'); self.out.pack(fill='both', expand=True)
        self.btns = ttk.Frame(self); self.btns.pack(fill='x', pady=8)
        ttk.Button(self.btns, text='Cancel', command=self.cancel).pack(side='left')
        self.view_btn = ttk.Button(self.btns, text='View Report', command=self.view_report, state='disabled')
        self.view_btn.pack(side='right')
        self.proc = None; self.q = queue.Queue(); self._stop = threading.Event()

    def start_scan(self, opts):
        self.out.delete('1.0', 'end'); self.pb.start(60); self.view_btn.config(state='disabled')
        args = [str(CLI), 'scan', '--report', str(REPORTS)]
        if opts.get('offline'): args += ['--offline']
        if opts.get('readonly'): args += ['--read-only']
        if opts.get('deep'): args += ['--deep']
        # Best‑effort environment for logs
        env = os.environ.copy(); env['QP_LOG_DIR'] = str(LOGS)
        def worker():
            try:
                self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
                for line in self.proc.stdout:
                    if self._stop.is_set(): break
                    self.q.put(line)
                code = self.proc.wait()
                self.q.put({'_exit': code})
            except Exception as e:
                self.q.put({'_error': str(e)})
        threading.Thread(target=worker, daemon=True).start()
        self.after(50, self._drain)

    def _drain(self):
        try:
            while True:
                item = self.q.get_nowait()
                if isinstance(item, dict) and '_exit' in item:
                    self.pb.stop()
                    code = item['_exit']
                    if code == 0:
                        self.view_btn.config(state='normal')
                        # Discover most recent report
                        reports = sorted(REPORTS.glob('*.html'), key=lambda p: p.stat().st_mtime, reverse=True)
                        if reports: APP_STATE['last_report'] = str(reports[0])
                        self._write_out('\nScan complete. Click "View Report".')
                    else:
                        self._handle_scan_error(code)
                    return
                if isinstance(item, dict) and '_error' in item:
                    self.pb.stop()
                    self._handle_scan_error(-1, item['_error'])
                    return
                self._write_out(item)
        except Exception:
            pass
        self.after(50, self._drain)

    def _write_out(self, text):
        self.out.config(state='normal'); self.out.insert('end', text); self.out.see('end'); self.out.config(state='disabled')

    def _handle_scan_error(self, code, err_msg=None):
        diag = json.dumps({
            'platform': platform.platform(),
            'code': code,
            'python': sys.version,
        }, indent=2)
        steps = [
            'Close QuietPatch and reopen.',
            'Ensure the download was verified (see VERIFY.md).',
            'Run the CLI once and capture its output to include in your issue.',
        ]
        if err_msg: diag += f"\nerror: {err_msg}"
        self.c.err('Scan failed', 'Report could not be generated.', steps, None, diag)

    def view_report(self):
        rpt = APP_STATE.get('last_report')
        if not rpt or not os.path.exists(rpt):
            messagebox.showwarning('QuietPatch', 'No report file found.')
            return
        webbrowser.open_new_tab('file://' + os.path.abspath(rpt))

    def cancel(self):
        self._stop.set()
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
        except Exception:
            pass
        self.c.show('Options')

if __name__ == '__main__':
    try:
        Wizard().mainloop()
    except Exception as e:
        messagebox.showerror('QuietPatch', f'Fatal error: {e}')
