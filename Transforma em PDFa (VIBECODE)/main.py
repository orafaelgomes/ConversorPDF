import subprocess
import threading
import time
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

from ghostscript_bundle import get_ghostscript_command
from importer import scan_folder


def build_output_path(input_path: str, output_dir: str | None = None) -> Path:
    input_file = Path(input_path)
    target_dir = Path(output_dir) if output_dir else input_file.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / f"{input_file.stem}_pdfa.pdf"


class PdfAToolApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Conversor PDF para PDF/A")
        self.root.geometry("700x420")
        self.root.minsize(650, 380)

        self.input_paths: list[str] = []
        self.output_path: str | None = None
        self.output_dir: str | None = None
        self.file_items: dict[str, str] = {}
        self.cancel_event = threading.Event()
        self.batch_thread: threading.Thread | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Selecionar PDFs", command=self.select_pdfs)
        file_menu.add_command(label="Selecionar pasta", command=self.select_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.destroy)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)

        action_menu = tk.Menu(menu_bar, tearoff=0)
        action_menu.add_command(label="Converter para PDF/A", command=self.start_conversion)
        action_menu.add_command(label="Limpar fila", command=self.clear_queue)
        menu_bar.add_cascade(label="Ações", menu=action_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.show_about)
        menu_bar.add_cascade(label="Ajuda", menu=help_menu)

        main_frame = ttk.Frame(self.root, padding=16)
        main_frame.pack(fill="both", expand=True)

        title = ttk.Label(
            main_frame,
            text="Conversor de PDF para PDF/A",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(anchor="w", pady=(0, 12))

        description = ttk.Label(
            main_frame,
            text="Selecione arquivos ou pastas com PDFs e converta em lote para PDF/A.",
            wraplength=620,
        )
        description.pack(anchor="w", pady=(0, 18))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 12))

        select_button = ttk.Button(button_frame, text="Selecionar PDFs", command=self.select_pdfs)
        select_button.pack(side="left", padx=(0, 8))

        select_folder_button = ttk.Button(button_frame, text="Selecionar pasta", command=self.select_folder)
        select_folder_button.pack(side="left", padx=(0, 8))

        output_button = ttk.Button(button_frame, text="Escolher pasta de saída", command=self.choose_output_dir)
        output_button.pack(side="left", padx=(0, 8))

        remove_button = ttk.Button(button_frame, text="Remover selecionado", command=self.remove_selected)
        remove_button.pack(side="left", padx=(0, 8))

        clear_button = ttk.Button(button_frame, text="Limpar fila", command=self.clear_queue)
        clear_button.pack(side="left", padx=(0, 8))

        convert_button = ttk.Button(button_frame, text="Converter para PDF/A", command=self.start_conversion)
        convert_button.pack(side="left")

        cancel_button = ttk.Button(button_frame, text="Cancelar", command=self.cancel_conversion)
        cancel_button.pack(side="left", padx=(8, 0))

        self.status_var = tk.StringVar(value="Nenhum arquivo selecionado.")
        self.convert_button = convert_button
        self.cancel_button = cancel_button
        self.select_button = select_button
        self.output_button = output_button
        self.remove_button = remove_button
        self.clear_button = clear_button
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="#1f4e79")
        status_label.pack(anchor="w", pady=(8, 6))

        self.path_var = tk.StringVar(value="Caminho do arquivo: ainda não selecionado")
        path_label = ttk.Label(main_frame, textvariable=self.path_var, wraplength=620)
        path_label.pack(anchor="w", pady=(0, 6))

        self.output_var = tk.StringVar(value="Pasta de saída: a definir")
        output_label = ttk.Label(main_frame, textvariable=self.output_var, wraplength=620)
        output_label.pack(anchor="w", pady=(0, 12))

        self.progress = ttk.Progressbar(main_frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=(0, 8))

        self.file_tree = ttk.Treeview(main_frame, columns=("file", "status"), show="headings", height=6)
        self.file_tree.heading("file", text="Arquivo")
        self.file_tree.heading("status", text="Status")
        self.file_tree.column("file", width=450, anchor="w")
        self.file_tree.column("status", width=120, anchor="center")
        self.file_tree.pack(fill="both", expand=True, pady=(0, 12))

        self.log_box = tk.Text(main_frame, height=6, wrap="word", state="disabled")
        self.log_box.pack(fill="both", expand=True)

        self._append_log("Aplicação iniciada. Selecione um arquivo PDF para começar.")

    def select_pdfs(self) -> None:
        file_paths = filedialog.askopenfilenames(
            title="Selecionar arquivos PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os arquivos", "*.*")],
        )
        if not file_paths:
            return

        self.input_paths = list(file_paths)
        self.output_path = str(build_output_path(self.input_paths[0], self.output_dir))
        self.path_var.set(f"Arquivos selecionados: {len(self.input_paths)}")
        self.output_var.set(f"Pasta de saída: {self.output_dir or Path(self.input_paths[0]).parent}")
        self.status_var.set("Arquivos selecionados. Pronto para converter em lote.")
        self._append_log(f"{len(self.input_paths)} arquivos selecionados para conversão.")
        self._populate_file_list()

    def select_folder(self) -> None:
        folder_path = filedialog.askdirectory(title="Selecionar pasta de PDFs")
        if not folder_path:
            return

        found_pdfs = [str(p) for p in scan_folder(folder_path, recursive=True, patterns=["*.pdf"])]
        if not found_pdfs:
            messagebox.showwarning("Aviso", "Nenhum arquivo PDF foi encontrado na pasta selecionada.")
            self._append_log(f"Nenhum PDF encontrado em: {folder_path}")
            return

        self.input_paths = found_pdfs
        self.output_path = str(build_output_path(self.input_paths[0], self.output_dir))
        self.path_var.set(f"Arquivos selecionados: {len(self.input_paths)}")
        self.output_var.set(f"Pasta de saída: {self.output_dir or Path(self.input_paths[0]).parent}")
        self.status_var.set("Pasta importada. Pronto para converter em lote.")
        self._append_log(f"{len(self.input_paths)} PDFs encontrados em {folder_path}.")
        self._populate_file_list()

    def remove_selected(self) -> None:
        selected = self.file_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Selecione um item para remover da fila.")
            return

        removed = []
        for item_id in selected:
            if item_id in self.input_paths:
                removed.append(item_id)
            self.file_tree.delete(item_id)

        if removed:
            self.input_paths = [path for path in self.input_paths if path not in removed]
            for path in removed:
                self.file_items.pop(path, None)
            self.path_var.set(f"Arquivos selecionados: {len(self.input_paths)}")
            self.status_var.set("Itens removidos da fila de trabalho.")
            self._append_log(f"Removido(s) {len(removed)} item(ns) da fila de conversão.")
        else:
            self._append_log("Nenhum item válido selecionado para remoção.")

    def clear_queue(self) -> None:
        if not self.input_paths:
            messagebox.showinfo("Info", "A fila de trabalho já está vazia.")
            return

        self.input_paths = []
        self.file_items.clear()
        self.file_tree.delete(*self.file_tree.get_children())
        self.path_var.set("Arquivos selecionados: 0")
        self.status_var.set("Fila de trabalho limpa.")
        self._append_log("Fila de trabalho completamente limpa.")

    def choose_output_dir(self) -> None:
        selected_dir = filedialog.askdirectory(title="Escolher pasta de saída")
        if not selected_dir:
            return

        self.output_dir = selected_dir
        if self.input_paths:
            self.output_path = str(build_output_path(self.input_paths[0], self.output_dir))
            self.output_var.set(f"Pasta de saída: {self.output_dir}")
        else:
            self.output_var.set(f"Pasta de saída: {selected_dir}")
        self._append_log(f"Pasta de saída definida: {selected_dir}")

    def _populate_file_list(self) -> None:
        self.file_tree.delete(*self.file_tree.get_children())
        self.file_items.clear()

        for file_path in self.input_paths:
            item_id = self.file_tree.insert("", "end", iid=file_path, values=(Path(file_path).name, "Pendente"))
            self.file_items[file_path] = item_id

    def _mark_file_status(self, input_path: str, status: str) -> None:
        item_id = self.file_items.get(input_path)
        if item_id:
            self.file_tree.item(item_id, values=(Path(input_path).name, status))

    def _update_progress(self, done: int, total: int) -> None:
        self.progress["maximum"] = total
        self.progress["value"] = done
        self.status_var.set(f"Convertendo {done} de {total} arquivos...")

    def _find_ghostscript(self) -> str | None:
        return get_ghostscript_command()

    def start_conversion(self) -> None:
        if self.batch_thread and self.batch_thread.is_alive():
            messagebox.showinfo("Aguarde", "A conversão já está em andamento.")
            return

        if not self.input_paths:
            messagebox.showwarning("Aviso", "Selecione um ou mais arquivos PDF antes de converter.")
            self._append_log("Conversão cancelada: nenhum arquivo foi selecionado.")
            return

        ghostscript = self._find_ghostscript()
        if not ghostscript:
            self.status_var.set("Falha na conversão: Ghostscript não encontrado.")
            self._append_log("Ghostscript não foi localizado nem instalado automaticamente.")
            messagebox.showerror(
                "Erro",
                "Ghostscript não foi encontrado. O instalador deve estar disponível junto ao aplicativo."
            )
            return

        self.cancel_event.clear()
        self._set_ui_running(True)
        self._append_log(f"Iniciando conversão em lote para {len(self.input_paths)} arquivos...")

        self.batch_thread = threading.Thread(target=self._run_conversion, args=(ghostscript,), daemon=True)
        self.batch_thread.start()

    def cancel_conversion(self) -> None:
        if self.batch_thread and self.batch_thread.is_alive():
            self.cancel_event.set()
            self._append_log("Pedido de cancelamento recebido. Interrompendo a conversão...")
            self.status_var.set("Cancelando a conversão...")
        else:
            self._append_log("Nenhuma conversão em andamento para cancelar.")

    def _run_conversion(self, ghostscript: str) -> None:
        total_files = len(self.input_paths)
        self._run_in_main(self._update_progress, 0, total_files)
        processed = 0
        successes = 0
        failures: list[tuple[str, str]] = []

        for input_path in self.input_paths:
            if self.cancel_event.is_set():
                self._append_log("Conversão cancelada pelo usuário.")
                break

            self._run_in_main(self._mark_file_status, input_path, "Em progresso")
            output_path = build_output_path(input_path, self.output_dir)
            command = [
                ghostscript,
                "-dPDFA=2",
                "-dBATCH",
                "-dNOPAUSE",
                "-dNOOUTERSAVE",
                "-sDEVICE=pdfwrite",
                "-dPDFACompatibilityPolicy=1",
                "-sProcessColorModel=DeviceRGB",
                "-sColorConversionStrategy=RGB",
                f"-sOutputFile={output_path}",
                input_path,
            ]

            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                while True:
                    if self.cancel_event.is_set():
                        process.terminate()
                        process.wait(timeout=5)
                        raise RuntimeError("Cancelado")
                    if process.poll() is not None:
                        break
                    time.sleep(0.1)

                return_code = process.returncode
                stderr_output = process.stderr.read().strip() if process.stderr else ""
                if return_code != 0:
                    raise subprocess.CalledProcessError(return_code, command, stderr=stderr_output)

                successes += 1
                self._run_in_main(self._mark_file_status, input_path, "Concluído")
                self._append_log(f"Arquivo convertido e salvo em: {output_path}")
            except subprocess.CalledProcessError as exc:
                failures.append((input_path, exc.stderr.strip() or str(exc)))
                self._run_in_main(self._mark_file_status, input_path, "Falha")
                self._append_log(f"Erro em {Path(input_path).name}: {exc.stderr.strip() or str(exc)}")
            except Exception as exc:
                if str(exc) == "Cancelado":
                    self._run_in_main(self._mark_file_status, input_path, "Cancelado")
                    self._append_log(f"Conversão cancelada durante {Path(input_path).name}.")
                    break
                failures.append((input_path, str(exc)))
                self._run_in_main(self._mark_file_status, input_path, "Falha")
                self._append_log(f"Erro em {Path(input_path).name}: {exc}")
            finally:
                processed += 1
                self._run_in_main(self._update_progress, processed, total_files)

        self._run_in_main(self._finalize_conversion, successes, total_files, failures)

    def _finalize_conversion(self, successes: int, total_files: int, failures: list[tuple[str, str]]) -> None:
        self.output_path = str(build_output_path(self.input_paths[0], self.output_dir))
        self.output_var.set(f"Pasta de saída: {self.output_dir or Path(self.input_paths[0]).parent}")
        self._set_ui_running(False)

        if self.cancel_event.is_set():
            self.status_var.set("Conversão cancelada pelo usuário.")
            messagebox.showinfo("Cancelado", "A conversão foi cancelada.")
            return

        self.status_var.set("Conversão em lote concluída.")
        summary_message = f"{successes} de {total_files} arquivos convertidos com sucesso."
        if failures:
            summary_message += f"\n{len(failures)} falharam. Veja o log para detalhes."
            self._append_log("Relatório final:\n" + "\n".join([f"{Path(path).name}: {error}" for path, error in failures]))
            messagebox.showwarning("Conversão parcial", summary_message)
        else:
            messagebox.showinfo("Sucesso", summary_message)

    def _set_ui_running(self, running: bool) -> None:
        state = "disabled" if running else "normal"
        self.select_button.config(state=state)
        self.output_button.config(state=state)
        self.convert_button.config(state=state)
        self.cancel_button.config(state="normal" if running else "disabled")

    def _run_in_main(self, callback, *args):
        self.root.after(0, lambda: callback(*args))

    def show_about(self) -> None:
        messagebox.showinfo(
            "Sobre",
            "Conversor PDF para PDF/A\n\nVersão inicial com interface simples e conversão via Ghostscript.",
        )

    def _append_log(self, message: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"{message}\n")
        self.log_box.configure(state="disabled")
        self.log_box.see("end")


def main() -> None:
    root = tk.Tk()
    app = PdfAToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
