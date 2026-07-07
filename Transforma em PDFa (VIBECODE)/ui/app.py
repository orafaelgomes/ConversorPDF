"""
UI mínimo (Tkinter) para a Fase 3 — esqueleto do workspace.

Funcionalidades:
- Adicionar arquivo/pasta
- Remover item
- Iniciar processamento em background
- Painel simples de status por item

Executar: `python -m ui.app`
"""
import threading
import queue
import time
import concurrent.futures
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from importer import scan_folder
from verificador_pdfa import validar_pdfa
from converter import convert_with_ghostscript


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Transforma em PDFa — Workspace (esqueleto)")
        self.geometry("800x480")

        self.work_queue = []  # lista de dicts: {path, status}
        self.event_q = queue.Queue()
        self.cancel_event = threading.Event()
        self.executor = None

        self._build_ui()

        # iniciar polling para eventos do worker
        self.after(200, self._poll_events)

    def _build_ui(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # lista de arquivos
        self.tree = ttk.Treeview(frame, columns=("file", "status", "log"), show="headings")
        self.tree.heading("file", text="Arquivo")
        self.tree.heading("status", text="Status")
        self.tree.heading("log", text="Log (últimas linhas)")
        self.tree.column("file", width=420)
        self.tree.column("status", width=120)
        self.tree.column("log", width=240)
        # tags para cores
        self.tree.tag_configure('pending', background='#f0f0f0')
        self.tree.tag_configure('processing', background='#e6f0ff')
        self.tree.tag_configure('done', background='#e6ffe6')
        self.tree.tag_configure('error', background='#ffe6e6')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # barra lateral de ações
        side = ttk.Frame(frame, width=200)
        side.pack(side=tk.RIGHT, fill=tk.Y)

        btn_add_file = ttk.Button(side, text="Adicionar arquivo", command=self.add_file)
        btn_add_file.pack(fill=tk.X, pady=4)

        btn_add_folder = ttk.Button(side, text="Adicionar pasta", command=self.add_folder)
        btn_add_folder.pack(fill=tk.X, pady=4)

        btn_remove = ttk.Button(side, text="Remover selecionado", command=self.remove_selected)
        btn_remove.pack(fill=tk.X, pady=4)

        btn_start = ttk.Button(side, text="Iniciar processamento", command=self.start_processing)
        btn_start.pack(fill=tk.X, pady=12)

        # controle de paralelismo
        ttk.Label(side, text="Workers:").pack(fill=tk.X, pady=(8, 0))
        self.workers_var = tk.IntVar(value=2)
        self.spin_workers = ttk.Spinbox(side, from_=1, to=16, textvariable=self.workers_var)
        self.spin_workers.pack(fill=tk.X, pady=4)

        btn_cancel = ttk.Button(side, text="Cancelar", command=self.cancel_processing)
        btn_cancel.pack(fill=tk.X, pady=4)

        btn_view_log = ttk.Button(side, text="Ver log", command=self.view_log_selected)
        btn_view_log.pack(fill=tk.X, pady=4)
        # binding para duplo-clique abrir log
        self.tree.bind("<Double-1>", lambda e: self.view_log_selected())

    def add_file(self):
        paths = filedialog.askopenfilenames(title="Selecione PDFs", filetypes=[("PDF","*.pdf")])
        for p in paths:
            self._add_item(p)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Selecione pasta")
        if not folder:
            return
        for f in scan_folder(folder, recursive=True, patterns=["*.pdf"]):
            self._add_item(str(f))

    def _add_item(self, path):
        if any(item['path'] == path for item in self.work_queue):
            return
        item = {'path': path, 'status': 'Pendente'}
        self.work_queue.append(item)
        self.tree.insert('', 'end', iid=path, values=(path, item['status'], ''), tags=('pending',))

    def remove_selected(self):
        sel = self.tree.selection()
        for iid in sel:
            self.tree.delete(iid)
            self.work_queue[:] = [it for it in self.work_queue if it['path'] != iid]

    def view_log_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecione um item para ver o log")
            return
        path = sel[0]
        try:
            from logger_json import read_all
            entries = read_all(path)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler logs: {e}")
            return

        win = tk.Toplevel(self)
        win.title(f"Logs — {Path(path).name}")
        txt = tk.Text(win, wrap=tk.NONE, width=120, height=30)
        txt.pack(fill=tk.BOTH, expand=True)
        for e in entries:
            ts = e.get('timestamp', '')
            evt = e.get('event', '')
            details = e.get('status') or e.get('detalhes') or ''
            txt.insert(tk.END, f"[{ts}] {evt} {details}\n")
        txt.configure(state=tk.DISABLED)

    def start_processing(self):
        if not self.work_queue:
            messagebox.showinfo("Info", "Nenhum item na lista de trabalho")
            return
        # iniciar pool de workers
        if self.executor is not None:
            messagebox.showwarning("Aviso", "Processamento já em execução")
            return

        self.cancel_event.clear()
        workers = max(1, int(self.workers_var.get() or 1))
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=workers)

        # coletar paths no momento do start
        paths = [item['path'] for item in list(self.work_queue)]

        for p in paths:
            # marcar como em processamento imediatamente
            self.event_q.put((p, 'Em processamento', ''))
            fut = self.executor.submit(self._process_path, p)
            if not hasattr(self, 'futures'):
                self.futures = []
            self.futures.append(fut)

        # thread para monitorar término do pool
        t = threading.Thread(target=self._monitor_executor, daemon=True)
        t.start()

    def cancel_processing(self):
        # sinaliza cancelamento; não força matar threads já rodando
        self.cancel_event.set()
        if self.executor:
            try:
                self.executor.shutdown(wait=False)
            except Exception:
                pass
            self.executor = None
        # marcar itens restantes como cancelados
        for it in list(self.work_queue):
            if it.get('status') not in ('Convertido', 'Já é PDF/A', 'Falha/Erro', 'Cancelado'):
                self.event_q.put((it['path'], 'Cancelado', ''))

    def _monitor_executor(self):
        # aguarda conclusão das futures e limpa executor
        if not hasattr(self, 'futures'):
            self.executor = None
            return
        try:
            for fut in concurrent.futures.as_completed(self.futures):
                try:
                    fut.result()
                except Exception:
                    pass
        finally:
            self.executor = None
            # sinaliza finalização geral
            self.event_q.put(("__all_done__", "ALL_DONE", ""))

    def _worker_thread(self):
        # legacy: não usado quando se usa executor
        pass

    def _process_path(self, path):
        # executado em thread do executor
        if self.cancel_event.is_set():
            try:
                from logger_json import log_event
                log_event({"event": "cancelled", "path": path})
            except Exception:
                pass
            self.event_q.put((path, 'Cancelado', ''))
            return

        try:
            import asyncio
            res = asyncio.run(validar_pdfa(path))
        except Exception:
            res = {'status': 'erro', 'detalhes': ['falha validação']}

        if res.get('status') == 'conforme':
            status = 'Já é PDF/A'
        elif res.get('status') == 'erro':
            status = 'Falha/Erro'
        else:
            output_path = str(Path(path).with_name(Path(path).stem + '_pdfa.pdf'))
            try:
                conv = convert_with_ghostscript(path, output_path, timeout=90)
                if conv.get('returncode') == 0 and not conv.get('timeout'):
                    status = 'Convertido'
                else:
                    status = 'Falha/Erro'
                    if conv.get('timeout'):
                        try:
                            from logger_json import log_event
                            log_event({"event": "timeout", "path": path})
                        except Exception:
                            pass
            except Exception:
                status = 'Falha/Erro'

        try:
            from logger_json import log_event, read_recent
            log_event({"event": "status", "path": path, "status": status})
            recent = read_recent(path, n=3)
            preview = " | ".join([str(x.get('event') or x.get('detalhes') or '') for x in recent])
        except Exception:
            preview = ''

        self.event_q.put((path, status, preview))

    def _poll_events(self):
        try:
            while True:
                data = self.event_q.get_nowait()
                # eventos antigos podem ter forma (path,status) ou nova forma (path,status,preview)
                if len(data) == 2:
                    path, status = data
                    preview = ''
                else:
                    path, status, preview = data
                # atualizar na tree
                if self.tree.exists(path):
                    # atualizar valores e tags
                    # adicionar ícone simples por status
                    icons = {
                        'Em processamento': '🔄',
                        'Convertido': '✅',
                        'Já é PDF/A': '🟢',
                        'Falha/Erro': '❌',
                        'Cancelado': '⏹️'
                    }
                    disp = f"{icons.get(status, '')} {status}"
                    self.tree.item(path, values=(path, disp, preview))
                    tag = 'pending'
                    if status == 'Em processamento':
                        tag = 'processing'
                    elif status in ('Convertido', 'Já é PDF/A'):
                        tag = 'done'
                    elif status.startswith('Falha') or status == 'Falha/Erro':
                        tag = 'error'
                    self.tree.item(path, tags=(tag,))
                    # atualizar tooltip (text) simplista: set values já atualiza
                    # atualizar work_queue quando item finaliza
                    if tag in ('done', 'error') or status == 'Cancelado':
                        for it in self.work_queue:
                            if it['path'] == path:
                                it['status'] = status
                                break
                else:
                    # item pode ter sido removido; ignorar
                    pass
        except queue.Empty:
            pass
        finally:
            self.after(200, self._poll_events)


def main():
    app = App()
    app.mainloop()


if __name__ == '__main__':
    main()

    
