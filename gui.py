import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from pdf_processor import PDFSearcher

class SearchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Buscador de PDFs")
        self.geometry("800x750")
        self.resizable(False, False)
        
        # Tema e Cores
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#0f172a") # Fundo principal escuro
        
        self.card_color = "#1e293b" # Fundo dos cards
        self.accent_color = "#3b82f6" # Azul para bordas/foco
        self.text_main = "#f8fafc"
        self.text_muted = "#94a3b8"
        
        self.source_dir = ""
        self.target_dir = ""
        self.search_thread = None
        self.searcher = None
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Frame principal centralizado
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # 1. Header
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 20))
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="🔍 Buscador de PDFs", font=ctk.CTkFont(size=28, weight="bold"), text_color=self.text_main)
        self.title_label.pack()
        
        self.subtitle_label = ctk.CTkLabel(self.header_frame, text="Extração automatizada de páginas baseada em nomes", font=ctk.CTkFont(size=14), text_color=self.text_muted)
        self.subtitle_label.pack()
        
        # 2. Área de busca
        self.search_frame = ctk.CTkFrame(self.main_frame, fg_color=self.card_color, corner_radius=10)
        self.search_frame.pack(fill="x", pady=10, ipady=10)
        
        self.name_entry = ctk.CTkEntry(
            self.search_frame, 
            placeholder_text="Digite o nome completo...", 
            font=ctk.CTkFont(size=16),
            height=45,
            border_color=self.card_color,
            fg_color="#0f172a",
            text_color=self.text_main,
            corner_radius=8
        )
        self.name_entry.pack(fill="x", padx=20, pady=10)
        
        # 3. Seleção de pastas
        self.folders_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.folders_frame.pack(fill="x", pady=10)
        
        self.folders_frame.columnconfigure(0, weight=1)
        self.folders_frame.columnconfigure(1, weight=1)
        
        # Card Origem
        self.source_card = ctk.CTkFrame(self.folders_frame, fg_color=self.card_color, corner_radius=10)
        self.source_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        self.btn_source = ctk.CTkButton(self.source_card, text="📁 Selecionar Origem", font=ctk.CTkFont(weight="bold"), fg_color="#334155", hover_color="#475569", command=self._select_source)
        self.btn_source.pack(pady=(15, 5), padx=15, fill="x")
        
        self.lbl_source = ctk.CTkLabel(self.source_card, text="Nenhuma pasta", text_color=self.text_muted, font=ctk.CTkFont(size=12))
        self.lbl_source.pack(pady=(0, 15), padx=15)
        
        # Card Destino
        self.target_card = ctk.CTkFrame(self.folders_frame, fg_color=self.card_color, corner_radius=10)
        self.target_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        self.btn_target = ctk.CTkButton(self.target_card, text="💾 Selecionar Destino", font=ctk.CTkFont(weight="bold"), fg_color="#334155", hover_color="#475569", command=self._select_target)
        self.btn_target.pack(pady=(15, 5), padx=15, fill="x")
        
        self.lbl_target = ctk.CTkLabel(self.target_card, text="Nenhuma pasta", text_color=self.text_muted, font=ctk.CTkFont(size=12))
        self.lbl_target.pack(pady=(0, 15), padx=15)
        
        # 5. Área de status (Dashboard)
        self.dashboard_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.dashboard_frame.pack(fill="x", pady=15)
        
        self.dashboard_frame.columnconfigure((0,1,2), weight=1)
        
        self.card_total = self._create_stat_card(self.dashboard_frame, "📄 Total de PDFs", "0", 0)
        self.card_processed = self._create_stat_card(self.dashboard_frame, "⚙️ Processados", "0", 1)
        self.card_matches = self._create_stat_card(self.dashboard_frame, "✅ Encontrados", "0", 2, value_color="#22c55e")
        
        # Arquivo atual e Barra de progresso
        self.progress_container = ctk.CTkFrame(self.main_frame, fg_color=self.card_color, corner_radius=10)
        self.progress_container.pack(fill="x", pady=10, ipady=10)
        
        self.lbl_current_file = ctk.CTkLabel(self.progress_container, text="Pronto para iniciar", text_color=self.text_muted, font=ctk.CTkFont(size=12))
        self.lbl_current_file.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_container, height=12, corner_radius=6, progress_color="#3b82f6", fg_color="#334155")
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self.progress_bar.set(0)
        
        # 4. Botões principais
        self.action_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.action_frame.pack(fill="x", pady=20)
        
        self.action_frame.columnconfigure(0, weight=1)
        self.action_frame.columnconfigure(1, weight=1)
        
        self.btn_start = ctk.CTkButton(
            self.action_frame, text="▶ Iniciar Busca", 
            font=ctk.CTkFont(size=16, weight="bold"), height=50,
            fg_color="#16a34a", hover_color="#15803d",
            command=self._start_search
        )
        self.btn_start.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.btn_stop = ctk.CTkButton(
            self.action_frame, text="⏹ Encerrar Busca", 
            font=ctk.CTkFont(size=16, weight="bold"), height=50,
            fg_color="#dc2626", hover_color="#b91c1c", state="disabled",
            command=self._stop_search
        )
        self.btn_stop.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
    def _create_stat_card(self, parent, title, value, col, value_color=None):
        card = ctk.CTkFrame(parent, fg_color=self.card_color, corner_radius=10)
        if col == 0:
            card.grid(row=0, column=col, padx=(0, 5), sticky="nsew")
        elif col == 1:
            card.grid(row=0, column=col, padx=5, sticky="nsew")
        else:
            card.grid(row=0, column=col, padx=(5, 0), sticky="nsew")
            
        lbl_title = ctk.CTkLabel(card, text=title, text_color=self.text_muted, font=ctk.CTkFont(size=12))
        lbl_title.pack(pady=(10, 0))
        
        color = value_color if value_color else self.text_main
        lbl_value = ctk.CTkLabel(card, text=value, text_color=color, font=ctk.CTkFont(size=32, weight="bold"))
        lbl_value.pack(pady=(0, 10))
        
        return lbl_value

    def _truncate_path(self, path, max_length=40):
        if len(path) <= max_length:
            return path
        return "..." + path[-(max_length-3):]

    def _select_source(self):
        folder = filedialog.askdirectory(title="Selecione a pasta de origem dos PDFs")
        if folder:
            self.source_dir = folder
            self.lbl_source.configure(text=self._truncate_path(self.source_dir))
            
    def _select_target(self):
        folder = filedialog.askdirectory(title="Selecione a pasta de destino dos resultados")
        if folder:
            self.target_dir = folder
            self.lbl_target.configure(text=self._truncate_path(self.target_dir))
            
    def _start_search(self):
        search_name = self.name_entry.get().strip()
        
        if not search_name:
            self._show_feedback("⚠️ Aviso", "Por favor, digite o nome a ser pesquisado.", "warning")
            return
            
        if not self.source_dir or not self.target_dir:
            self._show_feedback("⚠️ Aviso", "Por favor, selecione as pastas de origem e destino.", "warning")
            return
            
        # Reset UI
        self.progress_bar.set(0)
        self.card_total.configure(text="0")
        self.card_processed.configure(text="0")
        self.card_matches.configure(text="0")
        self.lbl_current_file.configure(text="Iniciando busca...")
        
        # Update UI State
        self.btn_start.configure(state="disabled", fg_color="#14532d")
        self.btn_source.configure(state="disabled")
        self.btn_target.configure(state="disabled")
        self.name_entry.configure(state="disabled")
        self.btn_stop.configure(state="normal", fg_color="#dc2626")
        
        self.last_matches = 0
        
        # Init logic
        self.searcher = PDFSearcher(
            source_dir=self.source_dir,
            target_dir=self.target_dir,
            search_name=search_name,
            update_callback=self._update_progress,
            completion_callback=self._on_search_complete
        )
        
        self.search_thread = threading.Thread(target=self.searcher.start_search)
        self.search_thread.daemon = True
        self.search_thread.start()
        
    def _stop_search(self):
        if self.searcher and self.searcher.is_running:
            confirm = messagebox.askyesno("⏹ Encerrar", "Tem certeza que deseja interromper a busca?\nO progresso atual será mantido.")
            if confirm:
                self.lbl_current_file.configure(text="Interrompendo busca com segurança...")
                self.searcher.stop_search()
                self.btn_stop.configure(state="disabled")
                
    def _update_progress(self, stats):
        def update():
            self.card_total.configure(text=str(stats['total_pdfs']))
            self.card_processed.configure(text=str(stats['processed_pdfs']))
            self.card_matches.configure(text=str(stats['total_matches']))
            
            # Simple visual feedback when match found
            if stats['total_matches'] > self.last_matches:
                self.last_matches = stats['total_matches']
                # Temporarily change text color to white then back to green
                self.card_matches.configure(text_color="#ffffff")
                self.after(200, lambda: self.card_matches.configure(text_color="#22c55e"))
            
            filename = stats['current_file']
            self.lbl_current_file.configure(text=f"Processando: {self._truncate_path(filename, 50)}")
            self.progress_bar.set(stats['progress'])
            
        self.after(0, update)
        
    def _on_search_complete(self, success, message):
        def update():
            self.btn_start.configure(state="normal", fg_color="#16a34a")
            self.btn_source.configure(state="normal")
            self.btn_target.configure(state="normal")
            self.name_entry.configure(state="normal")
            self.btn_stop.configure(state="disabled", fg_color="#7f1d1d")
            
            self.lbl_current_file.configure(text=message)
            
            if success and "sucesso" in message.lower():
                self._show_feedback("✅ Concluído", message, "info")
            elif success:
                self._show_feedback("ℹ️ Informação", message, "info")
            else:
                self._show_feedback("❌ Erro / Interrupção", message, "error")
                
        self.after(0, update)
        
    def _show_feedback(self, title, message, type="info"):
        if type == "warning":
            messagebox.showwarning(title, message)
        elif type == "error":
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
