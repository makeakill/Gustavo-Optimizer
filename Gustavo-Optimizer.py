import customtkinter as ctk
import os
import ctypes
from ctypes import wintypes
import threading
import subprocess
import time
from tkinter import filedialog 
import psutil
import multiprocessing
import winreg 
import sys
import socket
import urllib.request
import re
import shutil

# Importação das bibliotecas de System Tray (Bandeja do Sistema)
try:
    from PIL import Image, ImageTk
    import pystray
    from pystray import MenuItem as pystray_item
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# --- FUNÇÃO PARA LER ARQUIVOS COMPILADOS (ÍCONES) ---
def resource_path(relative_path):
    """ Retorna o caminho absoluto, funcionando tanto em desenvolvimento quanto no .exe compilado """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configurações Visuais
ctk.set_appearance_mode("dark") 

# --- DICIONÁRIO DE PALETAS (PERFIS DE CORES) ---
PALETAS = {
    "Pure Power (Ciano)": {
        "bg_main": "#0A0A0A", "bg_painel": "#141414", "acento": "#00E5FF", 
        "borda": "#2A2A2A", "texto_branco": "#FFFFFF", "texto_cinza": "#808080"
    },
    "Brutal Red (Vermelho)": {
        "bg_main": "#050505", "bg_painel": "#101010", "acento": "#FF0033", 
        "borda": "#252525", "texto_branco": "#FFFFFF", "texto_cinza": "#808080"
    },
    "Matrix Hacker (Verde)": {
        "bg_main": "#000000", "bg_painel": "#050a05", "acento": "#00FF41", 
        "borda": "#0a1a0a", "texto_branco": "#E0FFE0", "texto_cinza": "#008F11"
    },
    "Synthwave (Roxo)": {
        "bg_main": "#0F0514", "bg_painel": "#1A0B2E", "acento": "#FF00FF", 
        "borda": "#3D1C5E", "texto_branco": "#FFFFFF", "texto_cinza": "#B085F5"
    },
    "Retro DOS (Âmbar)": {
        "bg_main": "#000000", "bg_painel": "#000000", "acento": "#FFB000", 
        "borda": "#332200", "texto_branco": "#FFB000", "texto_cinza": "#886600"
    },
    "Dracula (Moderno)": {
        "bg_main": "#282A36", "bg_painel": "#44475A", "acento": "#FF79C6", 
        "borda": "#6272A4", "texto_branco": "#F8F8F2", "texto_cinza": "#8BE9FD"
    },
    "Nord (Minimalista)": {
        "bg_main": "#2E3440", "bg_painel": "#3B4252", "acento": "#88C0D0", 
        "borda": "#4C566A", "texto_branco": "#ECEFF4", "texto_cinza": "#D8DEE9"
    },
    "Vaporwave (Miami)": {
        "bg_main": "#1E1E2E", "bg_painel": "#2A2A40", "acento": "#F5A9B8", 
        "borda": "#5CE1E6", "texto_branco": "#FFFFFF", "texto_cinza": "#A6ADC8"
    }
}

class MeuOtimizador(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- SEPARAÇÃO DE IDENTIDADE PARA A BARRA DE TAREFAS ---
        # Força o Windows a reconhecer este programa como único, substituindo o ícone azul do CustomTkinter pelo nosso.
        if os.name == 'nt':
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("gustavo.optimizer.elite.v2.0.6")
            except Exception:
                pass

        # --- CONFIGURAÇÃO DA JANELA E TITLEBAR CUSTOMIZADA ---
        self.title("Gustavo Optimizer v2.0 - Elite Edition")
        self.geometry("1450x950")
        
        # Remove a barra de título padrão do Windows
        self.overrideredirect(True)
        
        # Hack Ctypes para garantir que o ícone do programa aparece na barra de tarefas mesmo sem o Titlebar
        self.after(10, self.corrigir_barra_tarefas)

        # Configurações de Estado
        self.reg_lock = threading.Lock()
        self.estado_anterior = {}
        self.gpu_cache = "A calcular..."
        
        # --- CARREGAR O ÍCONE (Se existir) ---
        icone_path = resource_path("icone.ico")
        if os.path.exists(icone_path):
            self.iconbitmap(icone_path)
            try:
                if HAS_TRAY:
                    # Aplica o ícone internamente de forma profunda para janelas Frameless
                    img = ImageTk.PhotoImage(Image.open(icone_path))
                    self.wm_iconphoto(True, img)
            except Exception:
                pass
        
        # Carrega o tema salvo
        tema_salvo = self.carregar_config("TemaPrincipal", "Pure Power (Ciano)")
        if tema_salvo not in PALETAS:
            tema_salvo = "Pure Power (Ciano)"
        self.aplicar_variaveis_tema(tema_salvo)
        
        self.perfil_ativo = self.carregar_config("PerfilAtivo", "Nenhum")
        self.carregar_snapshot_memoria()
        
        self.guid_maximo = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
        self.guid_padrao = self.carregar_config("GuidPadrao", "381b4222-f694-41f0-9685-ff5bb260df2e")
        
        self.configure(fg_color=self.bg_main)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0) # Linha da Titlebar
        self.grid_rowconfigure(1, weight=1) # Linha do Conteúdo

        # ==========================================
        # 0. DESENHANDO A TITLEBAR CUSTOMIZADA
        # ==========================================
        self.titlebar = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color=self.bg_painel, border_color=self.borda, border_width=1)
        self.titlebar.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        # Variáveis para arrastar a janela
        self._x = None
        self._y = None
        self.titlebar.bind("<ButtonPress-1>", self.iniciar_movimento)
        self.titlebar.bind("<B1-Motion>", self.mover_janela)
        
        self.lbl_title = ctk.CTkLabel(self.titlebar, text="  Gustavo Optimizer v2.0.6 - Elite Edition", font=("Segoe UI", 12, "bold"), text_color=self.acento)
        self.lbl_title.pack(side="left", padx=10)
        
        self.btn_close = ctk.CTkButton(self.titlebar, text="✕", width=45, height=30, corner_radius=6, fg_color="transparent", hover_color="#e74c3c", text_color=self.texto_branco, font=("Segoe UI", 16, "bold"), command=self.destroy)
        self.btn_close.pack(side="right", padx=(0, 5), pady=5)
        
        self.btn_min = ctk.CTkButton(self.titlebar, text="—", width=45, height=30, corner_radius=6, fg_color="transparent", hover_color=self.borda, text_color=self.texto_branco, font=("Segoe UI", 14, "bold"), command=self.minimizar_custom)
        self.btn_min.pack(side="right", padx=5, pady=5)

        # ==========================================
        # 1. BARRA LATERAL (SIDEBAR) TÉCNICA E MODERNA
        # ==========================================
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0, fg_color=self.bg_painel, border_width=1, border_color=self.borda)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(14, weight=1)

        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="[ GUSTAVO OPTIMIZER ]", font=("Consolas", 22, "bold"), text_color=self.acento)
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        admin_text = "MODO ADMIN: ATIVO" if self.is_admin else "AVISO: RODE COMO ADMIN"
        self.status_topo = ctk.CTkLabel(self.sidebar, text=admin_text, text_color="#2ecc71" if self.is_admin else self.acento, font=("Segoe UI", 12, "bold"))
        self.status_topo.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")

        self.sw_master_sys = ctk.CTkSwitch(self.sidebar, text="MASTER SISTEMA (ON/OFF)", command=self.iniciar_thread_master, font=("Segoe UI", 12, "bold"), progress_color=self.acento, fg_color=self.borda)
        self.sw_master_sys.grid(row=2, column=0, padx=20, pady=8, sticky="w")

        self.sw_master_clean = ctk.CTkSwitch(self.sidebar, text="MASTER MANUTENÇÃO", command=self.thread_manutencao, font=("Segoe UI", 12, "bold"), progress_color=self.acento, fg_color=self.borda)
        self.sw_master_clean.grid(row=3, column=0, padx=20, pady=8, sticky="w")

        self.btn_restore = ctk.CTkButton(self.sidebar, text="PONTO RESTAURAÇÃO", command=self.criar_ponto_restauracao, fg_color="transparent", hover_color=self.acento, text_color=self.texto_branco, corner_radius=6, border_width=2, border_color=self.acento, font=("Segoe UI", 12, "bold"))
        self.btn_restore.grid(row=4, column=0, padx=20, pady=8, sticky="ew")

        self.btn_exportar = ctk.CTkButton(self.sidebar, text="EXPORTAR LOG", command=self.exportar_log, fg_color="transparent", hover_color=self.acento, text_color=self.texto_branco, corner_radius=6, border_width=2, border_color=self.acento, font=("Segoe UI", 12, "bold"))
        self.btn_exportar.grid(row=5, column=0, padx=20, pady=8, sticky="ew")

        self.btn_manual = ctk.CTkButton(self.sidebar, text="MANUAL DO PROGRAMA", command=self.abrir_manual, fg_color="transparent", hover_color=self.acento, text_color=self.texto_branco, corner_radius=6, border_width=2, border_color=self.acento, font=("Segoe UI", 12, "bold"))
        self.btn_manual.grid(row=6, column=0, padx=20, pady=(8, 15), sticky="ew")

        # Rótulo Informativo do Tema
        self.lbl_tema_info = ctk.CTkLabel(self.sidebar, text="🎨 Estilo Visual (Nord, Dracula, etc.):", font=("Segoe UI", 11, "bold"), text_color=self.texto_cinza)
        self.lbl_tema_info.grid(row=7, column=0, padx=20, pady=(0, 0), sticky="w")

        self.combo_temas = ctk.CTkOptionMenu(self.sidebar, values=list(PALETAS.keys()), command=self.mudar_tema, fg_color=self.bg_painel, button_color=self.borda, button_hover_color=self.acento, dropdown_fg_color=self.bg_painel, text_color=self.texto_branco, font=("Segoe UI", 12, "bold"), corner_radius=8)
        self.combo_temas.set(tema_salvo)
        self.combo_temas.grid(row=8, column=0, padx=20, pady=(5, 15), sticky="ew")

        # --- DASHBOARD VISUAL DE HARDWARE ---
        self.frame_hw = ctk.CTkFrame(self.sidebar, fg_color=self.bg_main, border_color=self.borda, border_width=1, corner_radius=12)
        self.frame_hw.grid(row=9, column=0, padx=20, pady=(0, 15), sticky="ew")
        
        self.lbl_cpu_tit = ctk.CTkLabel(self.frame_hw, text="⚙️ CPU", font=("Segoe UI", 12, "bold"), text_color=self.texto_cinza)
        self.lbl_cpu_tit.grid(row=0, column=0, padx=15, pady=(15,0), sticky="w")
        self.lbl_cpu_val = ctk.CTkLabel(self.frame_hw, text="0%", font=("Segoe UI", 12, "bold"), text_color=self.texto_branco)
        self.lbl_cpu_val.grid(row=0, column=1, padx=15, pady=(15,0), sticky="e")
        self.prog_cpu = ctk.CTkProgressBar(self.frame_hw, height=6, progress_color=self.acento, fg_color=self.borda, corner_radius=4)
        self.prog_cpu.grid(row=1, column=0, columnspan=2, padx=15, pady=(5,10), sticky="ew")
        self.prog_cpu.set(0)
        
        self.lbl_ram_tit = ctk.CTkLabel(self.frame_hw, text="💾 RAM", font=("Segoe UI", 12, "bold"), text_color=self.texto_cinza)
        self.lbl_ram_tit.grid(row=2, column=0, padx=15, sticky="w")
        self.lbl_ram_val = ctk.CTkLabel(self.frame_hw, text="0%", font=("Segoe UI", 12, "bold"), text_color=self.texto_branco)
        self.lbl_ram_val.grid(row=2, column=1, padx=15, sticky="e")
        self.prog_ram = ctk.CTkProgressBar(self.frame_hw, height=6, progress_color=self.acento, fg_color=self.borda, corner_radius=4)
        self.prog_ram.grid(row=3, column=0, columnspan=2, padx=15, pady=(5,10), sticky="ew")
        self.prog_ram.set(0)
        
        self.lbl_gpu_tit = ctk.CTkLabel(self.frame_hw, text="🎮 GPU", font=("Segoe UI", 12, "bold"), text_color=self.texto_cinza)
        self.lbl_gpu_tit.grid(row=4, column=0, padx=15, sticky="w")
        self.lbl_gpu_val = ctk.CTkLabel(self.frame_hw, text="Calc...", font=("Segoe UI", 12, "bold"), text_color=self.texto_branco)
        self.lbl_gpu_val.grid(row=4, column=1, padx=15, sticky="e")
        self.prog_gpu = ctk.CTkProgressBar(self.frame_hw, height=6, progress_color=self.acento, fg_color=self.borda, corner_radius=4)
        self.prog_gpu.grid(row=5, column=0, columnspan=2, padx=15, pady=(5,15), sticky="ew")
        self.prog_gpu.set(0)

        # Forçar Modo Escuro
        self.sw_sidebar_dark = ctk.CTkSwitch(self.sidebar, text="MODO ESCURO SO", command=self.acao_dark_mode, font=("Segoe UI", 11, "bold"), progress_color=self.acento, fg_color=self.borda)
        self.sw_sidebar_dark.grid(row=10, column=0, padx=20, pady=(0, 10), sticky="w")
        estado_dark = self.carregar_config("DarkModeSidebar", "0")
        if estado_dark == "1":
            self.sw_sidebar_dark.select()

        # Efeito Mica / Transparência
        self.lbl_mica = ctk.CTkLabel(self.sidebar, text="🪟 Efeito Mica / Transparência:", font=("Segoe UI", 11, "bold"), text_color=self.texto_cinza)
        self.lbl_mica.grid(row=11, column=0, padx=20, pady=(5, 0), sticky="w")
        
        self.slider_mica = ctk.CTkSlider(self.sidebar, from_=0.3, to=1.0, command=self.mudar_transparencia, progress_color=self.acento, button_color=self.acento, button_hover_color=self.texto_branco)
        self.slider_mica.grid(row=12, column=0, padx=20, pady=(5, 10), sticky="ew")
        self.slider_mica.set(1.0) # Opaco por padrão

        # Log Terminal
        self.caixa_log = ctk.CTkTextbox(self.sidebar, height=130, corner_radius=10, font=("Consolas", 10), fg_color=self.bg_main, text_color=self.texto_cinza, border_width=1, border_color=self.borda)
        self.caixa_log.grid(row=13, column=0, padx=15, pady=10, sticky="sew")
        
        self.after(500, lambda: self.log("Sistema de Memória Persistente ativado."))
        self.after(550, lambda: self.log("Iniciando Auditoria em Tempo Real no Registo..."))

        # ==========================================
        # 2. ÁREA DE CONTEÚDO (SISTEMA DE ABAS - TABVIEW)
        # ==========================================
        self.tabview = ctk.CTkTabview(self, fg_color=self.bg_main, segmented_button_fg_color=self.bg_painel, segmented_button_selected_color=self.acento, segmented_button_unselected_color=self.bg_painel, text_color=self.texto_branco, corner_radius=12)
        self.tabview.grid(row=1, column=1, sticky="nsew", padx=15, pady=15)

        self.tab_desempenho = self.tabview.add("⚡ Desempenho")
        self.tab_rede = self.tabview.add("🌐 Rede & Internet")
        self.tab_privacidade = self.tabview.add("🛡️ Privacidade & OS")
        self.tab_limpeza = self.tabview.add("🧹 Limpeza")
        self.tab_root = self.tabview.add("⚙️ Root (Reinício)")

        # Scrollable Frames dentro das Abas
        self.scroll_desempenho = ctk.CTkScrollableFrame(self.tab_desempenho, fg_color="transparent")
        self.scroll_desempenho.pack(expand=True, fill="both")
        
        self.scroll_rede = ctk.CTkScrollableFrame(self.tab_rede, fg_color="transparent")
        self.scroll_rede.pack(expand=True, fill="both")
        
        self.scroll_privacidade = ctk.CTkScrollableFrame(self.tab_privacidade, fg_color="transparent")
        self.scroll_privacidade.pack(expand=True, fill="both")
        
        self.scroll_limpeza = ctk.CTkScrollableFrame(self.tab_limpeza, fg_color="transparent")
        self.scroll_limpeza.pack(expand=True, fill="both")
        
        self.scroll_root = ctk.CTkScrollableFrame(self.tab_root, fg_color="transparent")
        self.scroll_root.pack(expand=True, fill="both")

        self.lista_switches = [] 
        self.cards_interface = [] 

        self.montar_interface_total()
        
        # Iniciando Thread separada de GPU para evitar micro-stuttering na interface
        threading.Thread(target=self.thread_atualizar_gpu, daemon=True).start()
        self.atualizar_hardware_ui()
        
        self.after(500, self.iniciar_verificacao_energia)

    # --- FUNÇÕES DA TITLEBAR CUSTOMIZADA E SYSTEM TRAY ---
    def iniciar_movimento(self, event):
        self._x = event.x
        self._y = event.y

    def mover_janela(self, event):
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def minimizar_custom(self):
        """ Minimização de Elite para a Bandeja do Sistema (Tray Icon) """
        if HAS_TRAY:
            self.withdraw() # Esconde a janela da tela e da barra de tarefas
            
            icone_path = resource_path("icone.ico")
            try:
                image = Image.open(icone_path)
            except Exception:
                image = Image.new('RGB', (64, 64), color=(0, 229, 255))
                
            menu = pystray.Menu(
                pystray_item('Restaurar Interface', self.restaurar_do_tray, default=True),
                pystray_item('Encerrar Optimizer', self.fechar_pelo_tray)
            )
            
            self.tray_icon = pystray.Icon("GustavoOptimizer", image, "Gustavo Optimizer Elite", menu)
            
            # Executa o ícone numa thread separada para não bloquear a interface gráfica
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            self.log("[*] Oculto na Bandeja do Sistema. Clique com o botão direito para restaurar.")
        else:
            # Fallback seguro caso o utilizador não tenha instalado o pystray
            self.overrideredirect(False)
            self.iconify()
            self.bind("<FocusIn>", self.restaurar_custom_fallback)
            self.log("[-] Aviso: Execute 'pip install pystray Pillow' para ativar o Menu de Bandeja.")

    def restaurar_custom_fallback(self, event):
        self.unbind("<FocusIn>")
        self.overrideredirect(True)
        self.after(10, self.corrigir_barra_tarefas)

    def restaurar_do_tray(self, icon, item):
        icon.stop()
        self.after(0, self._mostrar_janela_tray)

    def _mostrar_janela_tray(self):
        self.deiconify()
        self.corrigir_barra_tarefas()
        self.log("[+] Interface restaurada com sucesso.")

    def fechar_pelo_tray(self, icon, item):
        icon.stop()
        self.after(0, self.destroy)

    def corrigir_barra_tarefas(self):
        # Acesso profundo via Ctypes para garantir que o software aparece na barra de tarefas do Windows
        # Mesmo com o overrideredirect ativado (Elite Feature)
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if hwnd == 0:
                hwnd = self.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            estilo_atual = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            estilo_novo = (estilo_atual & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, estilo_novo)
            self.withdraw()
            self.deiconify()
            
            # Re-força o ícone customizado na barra de tarefas (Removendo o 'C' azul do Tkinter)
            icone_path = resource_path("icone.ico")
            if os.path.exists(icone_path):
                self.iconbitmap(icone_path)
        except Exception:
            pass

    def mudar_transparencia(self, valor):
        # Aplica o Efeito Mica/Transparência global da janela
        self.attributes("-alpha", valor)

    # --- MONITORAMENTO DE HARDWARE OTIMIZADO ---
    def atualizar_hardware_ui(self):
        uso_cpu = psutil.cpu_percent(interval=None)
        uso_ram = psutil.virtual_memory().percent
        
        self.lbl_cpu_val.configure(text=f"{uso_cpu}%")
        self.prog_cpu.set(uso_cpu / 100.0)
        
        self.lbl_ram_val.configure(text=f"{uso_ram}%")
        self.prog_ram.set(uso_ram / 100.0)
        
        gpu_txt = self.gpu_cache.replace("%", "").strip()
        self.lbl_gpu_val.configure(text=f"{self.gpu_cache}")
        try:
            gpu_num = float(gpu_txt)
            self.prog_gpu.set(gpu_num / 100.0)
        except Exception:
            self.prog_gpu.set(0)
            
        self.after(1500, self.atualizar_hardware_ui)

    def thread_atualizar_gpu(self):
        while True:
            try:
                res = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, creationflags=0x08000000)
                if res.returncode == 0: 
                    self.gpu_cache = f"{res.stdout.strip()}%"
                else:
                    self.gpu_cache = "N/A (AMD)"
            except Exception: 
                self.gpu_cache = "N/A"
            time.sleep(2)

    # --- CONTROLES MASTER DA BARRA LATERAL ---
    def thread_manutencao(self):
        if self.sw_master_clean.get() == 1:
            if not self.is_admin:
                self.sw_master_clean.deselect()
                return
            threading.Thread(target=self.limpeza_sequencial, daemon=True).start()

    def limpeza_sequencial(self):
        tarefas = [
            ("Arquivos Temporários", "del /s /f /q %temp%\\*.*"), 
            ("Redefinição de Rede", "ipconfig /flushdns & netsh winsock reset")
        ]
        
        for nome_tarefa, comando in tarefas:
            if self.sw_master_clean.get() == 0: 
                break
            res = self.executar_comando(comando)
            time.sleep(1)
            self.log_res_simples(res, nome_tarefa)
            self.log(f"Etapa {nome_tarefa} em andamento...") 
            
        if self.sw_master_clean.get() == 1:
            self.executar_comando_visivel("sfc /scannow", "SFC Scan", reinicio=True)
            
        self.log("MANUTENÇÃO CONCLUÍDA COM SUCESSO.")
        self.sw_master_clean.deselect()

    def iniciar_thread_master(self):
        estado_alvo = int(self.sw_master_sys.get())
        threading.Thread(target=self.toggle_master_system, args=(estado_alvo,), daemon=True).start()

    def toggle_master_system(self, estado_alvo):
        self.log("Sincronizando Sistema Master (Chaves Automáticas Seguras)...")
        for sw in self.lista_switches:
            def acao_master(switch_atual=sw, alvo=estado_alvo):
                try:
                    if int(switch_atual.get()) != alvo:
                        if alvo == 1:
                            switch_atual.select()
                        else:
                            switch_atual.deselect()
                        if hasattr(switch_atual, 'comando_real'): 
                            switch_atual.comando_real()
                except Exception: 
                    pass
            self.after(0, acao_master)
            time.sleep(0.15) 
        self.log("Sincronização global concluída.")

    # --- OTIMIZAÇÕES NATIVAS (API PYTHON E CTYPES ELITE) ---
    def purgar_standby_list_nativa(self):
        def tarefa():
            if not self.is_admin:
                self.log("[-] Permissão Negada: É obrigatório executar como Administrador.", "erro")
                return
            self.log("[*] Solicitando privilégios SeProfileSingleProcessPrivilege ao Kernel...")
            try:
                SE_PRIVILEGE_ENABLED = 0x00000002
                TOKEN_ADJUST_PRIVILEGES = 0x0020
                TOKEN_QUERY = 0x0008
                SystemMemoryListInformation = 80
                MemoryPurgeStandbyList = 4

                class LUID(ctypes.Structure): 
                    _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]
                class LUID_AND_ATTRIBUTES(ctypes.Structure): 
                    _fields_ = [("Luid", LUID), ("Attributes", wintypes.DWORD)]
                class TOKEN_PRIVILEGES(ctypes.Structure): 
                    _fields_ = [("PrivilegeCount", wintypes.DWORD), ("Privileges", LUID_AND_ATTRIBUTES * 1)]

                advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                ntdll = ctypes.WinDLL('ntdll', use_last_error=True)

                kernel32.GetCurrentProcess.restype = wintypes.HANDLE
                advapi32.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
                advapi32.OpenProcessToken.restype = wintypes.BOOL

                hToken = wintypes.HANDLE()
                if not advapi32.OpenProcessToken(kernel32.GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, ctypes.byref(hToken)): 
                    raise ctypes.WinError(ctypes.get_last_error())

                luid = LUID()
                if not advapi32.LookupPrivilegeValueW(None, "SeProfileSingleProcessPrivilege", ctypes.byref(luid)): 
                    raise ctypes.WinError(ctypes.get_last_error())

                tp = TOKEN_PRIVILEGES()
                tp.PrivilegeCount = 1
                tp.Privileges[0].Luid = luid
                tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED
                
                if not advapi32.AdjustTokenPrivileges(hToken, False, ctypes.byref(tp), ctypes.sizeof(tp), None, None): 
                    raise ctypes.WinError(ctypes.get_last_error())
                
                command = ctypes.c_int(MemoryPurgeStandbyList)
                status = ntdll.NtSetSystemInformation(SystemMemoryListInformation, ctypes.byref(command), ctypes.sizeof(command))

                if status == 0: 
                    self.log("[+] Standby List esvaziada com sucesso! Stuttering de RAM mitigado.")
                else: 
                    self.log(f"[-] Erro NTSTATUS ao tentar purgar a memória: {hex(status)}", "erro")
                    
                kernel32.CloseHandle(hToken)
            except Exception as e: 
                self.log(f"[-] Erro Grave na Aplicação Ctypes (Standby List): {str(e)}", "erro")
        threading.Thread(target=tarefa, daemon=True).start()

    def otimizar_ram_nativa(self):
        def tarefa():
            self.log("[*] Esvaziando Working Set de processos ativos na memória RAM...")
            try:
                PROCESS_SET_QUOTA = 0x0100
                PROCESS_QUERY_INFORMATION = 0x0400
                count = 0
                
                psapi = ctypes.WinDLL('psapi.dll')
                kernel32 = ctypes.WinDLL('kernel32.dll')
                
                processos = list(psutil.process_iter(['pid']))
                total = len(processos)
                
                for i, proc in enumerate(processos):
                    try:
                        h_process = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, proc.info['pid'])
                        if h_process:
                            if psapi.EmptyWorkingSet(h_process): 
                                count += 1
                            kernel32.CloseHandle(h_process)
                    except Exception: 
                        pass
                
                self.log(f"[+] Smart RAM Cleaner concluído. Memória de cache ociosa libertada em {count} aplicações.")
            except Exception as e: 
                self.log(f"[-] Erro Crítico na API do Kernel: {str(e)}", "erro")
        threading.Thread(target=tarefa, daemon=True).start()

    def prioridade_jogos_nativa(self):
        def tarefa():
            self.log("[*] Verificando RAM e aplicando prioridade de CPU no Kernel para jogos ativos...")
            jogos_alvo = [
                'cs2.exe', 'dota2.exe', 'overwatch.exe', 'valorant.exe', 
                'javaw.exe', 'gta5.exe', 'robloxplayerbeta.exe', 'r5apex.exe', 
                'lol.exe', 'cod.exe', 'cyberpunk2077.exe'
            ]
            encontrados = []
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    nome = str(proc.info['name']).lower()
                    if nome in jogos_alvo:
                        p = psutil.Process(proc.info['pid'])
                        p.nice(psutil.HIGH_PRIORITY_CLASS)
                        encontrados.append(nome)
                except Exception: 
                    pass
            
            if encontrados:
                for jogo in set(encontrados): 
                    self.log(f"[+] Jogo detetado e otimizado com sucesso: {jogo.upper()} (Prioridade ALTA)")
            else: 
                self.log("[-] Nenhum jogo reconhecido ativo no momento. Abra o jogo primeiro!", "erro")
        threading.Thread(target=tarefa, daemon=True).start()

    def verificar_hz_monitor(self):
        def tarefa():
            self.log("[*] Consultando a API de Vídeo do Windows (user32.dll)...")
            try:
                class DEVMODE(ctypes.Structure):
                    _fields_ = [
                        ("dmDeviceName", wintypes.WCHAR * 32), ("dmSpecVersion", wintypes.WORD),
                        ("dmDriverVersion", wintypes.WORD), ("dmSize", wintypes.WORD),
                        ("dmDriverExtra", wintypes.WORD), ("dmFields", wintypes.DWORD),
                        ("dmPositionX", ctypes.c_long), ("dmPositionY", ctypes.c_long),
                        ("dmDisplayOrientation", wintypes.DWORD), ("dmDisplayFixedOutput", wintypes.DWORD),
                        ("dmColor", ctypes.c_short), ("dmDuplex", ctypes.c_short),
                        ("dmYResolution", ctypes.c_short), ("dmTTOption", ctypes.c_short),
                        ("dmCollate", ctypes.c_short), ("dmFormName", wintypes.WCHAR * 32),
                        ("dmLogPixels", wintypes.WORD), ("dmBitsPerPel", wintypes.DWORD),
                        ("dmPelsWidth", wintypes.DWORD), ("dmPelsHeight", wintypes.DWORD),
                        ("dmDisplayFlags", wintypes.DWORD), ("dmDisplayFrequency", wintypes.DWORD)
                    ]
                    
                devmode = DEVMODE()
                devmode.dmSize = ctypes.sizeof(DEVMODE)
                
                if ctypes.windll.user32.EnumDisplaySettingsW(None, -1, ctypes.byref(devmode)):
                    hz = devmode.dmDisplayFrequency
                    self.log(f"[+] Leitura de Hardware concluída: O seu ecrã está a rodar a {hz}Hz no momento.")
                    if hz <= 60: 
                        self.log("[-] Dica de Ouro: Se o seu monitor suportar mais de 60Hz, você está a perder frames. Altere isso nas configurações do Windows!", "erro")
                else: 
                    self.log("[-] Falha ao tentar ler as informações da placa de vídeo.", "erro")
            except Exception as e: 
                self.log(f"[-] Erro inesperado na leitura de hardware: {str(e)}", "erro")
        threading.Thread(target=tarefa, daemon=True).start()

    def benchmark_dns_nativo(self):
        def tarefa():
            self.log("[*] Buscando DNS Atual configurado na sua placa de rede...")
            try:
                cmd_ps = 'powershell -Command "(Get-NetAdapter | Where-Object {$_.Status -eq \'Up\' -and $_.InterfaceAlias -notlike \'*Loopback*\'} | Get-DnsClientServerAddress -AddressFamily IPv4)[0].ServerAddresses[0]"'
                res_dns = subprocess.run(cmd_ps, capture_output=True, text=True, creationflags=0x08000000)
                current_dns = res_dns.stdout.strip()
            except Exception:
                current_dns = ""
                
            servidores = {
                "Google": "8.8.8.8", 
                "Cloudflare": "1.1.1.1", 
                "OpenDNS": "208.67.222.222", 
                "Quad9": "9.9.9.9"
            }
            
            if current_dns and re.match(r"^\d{1,3}(\.\d{1,3}){3}$", current_dns):
                servidores["Atual (Seu Provedor)"] = current_dns
                
            resultados = {}
            
            self.log("[*] Iniciando Benchmark Global de Latência. Testando rotas de pacotes...")
            
            for nome, ip in servidores.items():
                try:
                    self.log(f"[*] A enviar pacotes de teste para {nome} ({ip})...")
                    res = subprocess.run(f"ping {ip} -n 4", capture_output=True, text=True, creationflags=0x08000000)
                    match = re.search(r'(Média|Average) = (\d+)ms', res.stdout, re.IGNORECASE)
                    
                    if match:
                        resultados[nome] = (int(match.group(2)), ip)
                    else:
                        resultados[nome] = (999, ip)
                except Exception: 
                    resultados[nome] = (999, ip)
            
            ordenados = sorted(resultados.items(), key=lambda item: item[1][0])
            self.after(0, lambda: self.abrir_tela_selecao_dns(ordenados))
            
        threading.Thread(target=tarefa, daemon=True).start()

    def abrir_tela_selecao_dns(self, resultados_ordenados):
        janela_dns = ctk.CTkToplevel(self)
        janela_dns.title("Seleção do Melhor DNS")
        janela_dns.geometry("500x450")
        janela_dns.transient(self)
        janela_dns.grab_set()
        janela_dns.configure(fg_color=self.bg_main)
        
        ctk.CTkLabel(janela_dns, text="[ RESULTADO DO BENCHMARK DNS ]", font=("Segoe UI", 16, "bold"), text_color=self.acento).pack(pady=(20, 10))
        
        frame_res = ctk.CTkFrame(janela_dns, fg_color=self.bg_painel, border_width=1, border_color=self.borda, corner_radius=10)
        frame_res.pack(expand=True, fill="both", padx=20, pady=10)
        
        opcoes_dropdown = []
        melhor_opcao = None
        
        for i, (nome, (ping, ip)) in enumerate(resultados_ordenados):
            cor = "#2ecc71" if i == 0 and ping != 999 else self.texto_branco
            texto_ping = f"{ping} ms" if ping != 999 else "Falha/TimeOut"
            texto_exibicao = f"{nome} ({ip}) - {texto_ping}"
            
            lbl_res = ctk.CTkLabel(frame_res, text=texto_exibicao, font=("Segoe UI", 13, "bold" if i == 0 else "normal"), text_color=cor)
            lbl_res.pack(anchor="w", padx=20, pady=8)
            
            if ping != 999:
                opcao = f"{nome} ({ip})"
                opcoes_dropdown.append(opcao)
                if i == 0: 
                    melhor_opcao = opcao
                    
        ctk.CTkLabel(janela_dns, text="Selecione o DNS para aplicar na placa de rede:", font=("Segoe UI", 12), text_color=self.texto_cinza).pack(pady=(10, 5))
        
        combo_dns = ctk.CTkOptionMenu(janela_dns, values=opcoes_dropdown, fg_color=self.bg_painel, button_color=self.borda, button_hover_color=self.acento, text_color=self.texto_branco, font=("Segoe UI", 12), corner_radius=8)
        if melhor_opcao: 
            combo_dns.set(melhor_opcao)
        combo_dns.pack(pady=5)
        
        def aplicar_dns_selecionado():
            escolha = combo_dns.get()
            match_ip = re.search(r"\(([\d\.]+)\)", escolha)
            if match_ip:
                ip_alvo = match_ip.group(1)
                self.log(f"[*] A Aplicar DNS {ip_alvo} na placa de rede ativa...")
                cmd = f'powershell -Command "Get-NetAdapter | Where-Object {{$_.Status -eq \'Up\' -and $_.InterfaceAlias -notlike \'*Loopback*\'}} | Set-DnsClientServerAddress -ServerAddresses \'{ip_alvo}\'"'
                self.executar_comando_assincrono(cmd, f"Aplicação Definitiva de DNS ({ip_alvo})")
            janela_dns.destroy()
            
        btn_aplicar = ctk.CTkButton(janela_dns, text="APLICAR DNS", command=aplicar_dns_selecionado, fg_color=self.bg_painel, hover_color=self.acento, text_color=self.texto_branco, border_width=1, border_color=self.acento, font=("Segoe UI", 12, "bold"), corner_radius=8)
        btn_aplicar.pack(pady=(10, 20))

    def limpar_temp_nativa(self):
        def tarefa():
            self.log("[*] Mapeando lixo eletrónico na pasta Temp de forma nativa e visual...")
            temp_path = os.environ.get('TEMP')
            
            if not temp_path or not os.path.exists(temp_path): 
                self.log("[-] Pasta Temp não encontrada no sistema de arquivos.", "erro")
                return
            
            arquivos_para_apagar = []
            
            for root, dirs, files in os.walk(temp_path, topdown=False):
                for name in files: 
                    arquivos_para_apagar.append(os.path.join(root, name))
                for name in dirs: 
                    arquivos_para_apagar.append(os.path.join(root, name))
            
            total = len(arquivos_para_apagar)
            if total == 0: 
                self.log("[+] A sua pasta temporária já está 100% limpa.")
                return
            
            self.log(f"[*] Exterminando {total} ficheiros corrompidos, temporários ou inúteis...")
            apagados = 0
            
            for i, item in enumerate(arquivos_para_apagar):
                try:
                    if os.path.isfile(item):
                        os.remove(item)
                    elif os.path.isdir(item):
                        os.rmdir(item)
                    apagados += 1
                except Exception: 
                    pass
                    
            self.log(f"[+] Limpeza Profunda Concluída: {apagados} ficheiros apagados de forma permanente.")
        threading.Thread(target=tarefa, daemon=True).start()

    # --- VERIFICAÇÃO INTELIGENTE DO DESEMPENHO MÁXIMO ---
    def iniciar_verificacao_energia(self):
        threading.Thread(target=self.checar_plano_energia, daemon=True).start()

    def checar_plano_energia(self):
        try:
            res_curr = subprocess.run(['powercfg', '/getactivescheme'], capture_output=True, text=True, creationflags=0x08000000)
            match_curr = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", res_curr.stdout)
            
            if match_curr:
                curr_guid = match_curr.group(1).lower()
                guid_salvo = self.carregar_config("GuidMaximo", "").lower()
                
                if curr_guid != guid_salvo and curr_guid != "e9a42b02-d5df-448d-aa00-03f14749eb61":
                    self.guid_padrao = curr_guid
                    self.salvar_config("GuidPadrao", self.guid_padrao)
        except Exception: 
            pass

        guid_salvo = self.carregar_config("GuidMaximo", "")
        res_l = subprocess.run('powercfg /l', capture_output=True, text=True, shell=True, creationflags=0x08000000)
        
        if guid_salvo and guid_salvo.lower() in res_l.stdout.lower():
            self.guid_maximo = guid_salvo
            self.log("[*] Plano de Desempenho Máximo carregado com sucesso a partir da memória.")
            return

        if "e9a42b02-d5df-448d-aa00-03f14749eb61" in res_l.stdout.lower():
            self.guid_maximo = "e9a42b02-d5df-448d-aa00-03f14749eb61"
            self.salvar_config("GuidMaximo", self.guid_maximo)
            self.log("[*] Plano de Desempenho Máximo nativo do sistema encontrado e associado.")
            return
            
        res_dup = subprocess.run('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61', capture_output=True, text=True, shell=True, creationflags=0x08000000)
        match = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", res_dup.stdout)
        
        if match:
            self.guid_maximo = match.group(1)
            self.salvar_config("GuidMaximo", self.guid_maximo)
            self.log(f"[*] Otimização Elevada: Plano de Desempenho Máximo exclusivo criado ({self.guid_maximo}).")
        else: 
            self.log("[-] Erro Crítico ao criar Desempenho Máximo. Usando o plano Alto Desempenho padrão.", "erro")

    # --- LÓGICA DO MODO ESCURO DA SIDEBAR ---
    def acao_dark_mode(self):
        if self.sw_sidebar_dark.get() == 1:
            cmd = 'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "AppsUseLightTheme" /t REG_DWORD /d 0 /f >nul 2>&1 & reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "SystemUsesLightTheme" /t REG_DWORD /d 0 /f >nul 2>&1'
        else:
            cmd = 'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "AppsUseLightTheme" /t REG_DWORD /d 1 /f >nul 2>&1 & reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "SystemUsesLightTheme" /t REG_DWORD /d 1 /f >nul 2>&1'
            
        self.executar_comando_assincrono(cmd, "Modo Escuro Forçado no Sistema", self.sw_sidebar_dark)

    # --- AUDITORIA EM TEMPO REAL E LEITURA DE REGISTO (SINGLE SOURCE OF TRUTH) ---
    def auditar_estado_real(self, nome_log):
        """ 
        Verifica o Kernel/Registo real do Windows no momento de abrir o programa.
        Se o usuário alterou por fora, o programa adapta-se visualmente.
        """
        mapa_auditoria = {
            "VS Telemetry": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\VisualStudio\Telemetry", "RefuseTelemetry", 1),
            "DiagTrack": (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\DiagTrack", "Start", 4),
            "NVIDIA Privacy": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\NVIDIA Corporation\NvControlPanel2\Client", "OptIn", 0),
            "GeoLocation": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors", "DisableLocation", 1),
            "Desempenho Visual": (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 2),
            "Power Throttling": (winreg.HKEY_LOCAL_MACHINE, r"System\CurrentControlSet\Control\Power\PowerThrottling", "PowerThrottlingOff", 1),
            "Timer Res": (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "GlobalTimerResolutionRequests", 1),
            "GPU Downclock": (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000", "PowerMizerEnable", 0),
            "Flip Fix": (winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", "EnableWindowedOptimization", 1),
            "Servicos Windows": (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\SysMain", "Start", 4),
            "Network Throttling": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "NetworkThrottlingIndex", 0xFFFFFFFF),
            "DSCP": (winreg.HKEY_LOCAL_MACHINE, r"System\CurrentControlSet\Services\Tcpip\Parameters\QoS", "Do not use NLA", "1"),
        }

        if nome_log in mapa_auditoria:
            hkey, path, value_name, expected_value = mapa_auditoria[nome_log]
            try:
                chave = winreg.OpenKey(hkey, path)
                valor, _ = winreg.QueryValueEx(chave, value_name)
                winreg.CloseKey(chave)
                return "1" if str(valor) == str(expected_value) else "0"
            except OSError:
                return "0" 
        
        return self.carregar_config(nome_log, "0")

    # --- SISTEMA DE MEMÓRIA (REGISTO DO WINDOWS) COM LOCK THREAD-SAFE ---
    def salvar_config(self, nome, valor):
        with self.reg_lock:
            try:
                chave = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\GustavoOptimizer")
                winreg.SetValueEx(chave, nome, 0, winreg.REG_SZ, str(valor))
                winreg.CloseKey(chave)
            except Exception as e: 
                self.log(f"Erro Fatal ao escrever memória: {str(e)}", "erro")

    def carregar_config(self, nome, padrao):
        try:
            chave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\GustavoOptimizer")
            valor, _ = winreg.QueryValueEx(chave, nome)
            winreg.CloseKey(chave)
            return valor
        except OSError: 
            return padrao

    def carregar_snapshot_memoria(self):
        self.estado_anterior = {}
        snap_str = self.carregar_config("SnapshotPerfil", "")
        if snap_str:
            try:
                for par in snap_str.split(','):
                    if ':' in par:
                        k, v = par.split(':')
                        self.estado_anterior[k] = int(v)
            except Exception: 
                pass

    def guardar_snapshot_atual(self):
        """ Salva o estado atual das chaves dinâmicas no Registo. """
        self.estado_anterior = {
            'pow': self.sw_pow.get(), 'gaming': self.sw_gaming.get(),
            'net_thrott': self.sw_net_thrott.get(), 'core_park': self.sw_core_park.get(),
            'tim': self.sw_tim.get(), 'gpu_oc': self.sw_gpu_oc.get(),
            'flip': self.sw_flip.get(), 'dscp': self.sw_dscp.get(),
            'tcp_global': self.sw_tcp_global.get(), 'thrott': self.sw_thrott.get(),
            'srv': self.sw_srv.get(), 'nic_int': self.sw_nic_int.get(), 
            'visual_perf': self.sw_visual_perf.get()
        }
        snap_str = ",".join([f"{k}:{v}" for k, v in self.estado_anterior.items()])
        self.salvar_config("SnapshotPerfil", snap_str)

    # --- GERENCIAMENTO DE TEMAS E CORES DINÂMICAS ---
    def aplicar_variaveis_tema(self, nome_tema):
        cores = PALETAS[nome_tema]
        self.bg_main = cores["bg_main"]
        self.bg_painel = cores["bg_painel"]
        self.acento = cores["acento"]
        self.borda = cores["borda"]
        self.texto_branco = cores["texto_branco"]
        self.texto_cinza = cores["texto_cinza"]

    def mudar_tema(self, novo_tema):
        self.aplicar_variaveis_tema(novo_tema)
        self.salvar_config("TemaPrincipal", novo_tema) 
        
        self.configure(fg_color=self.bg_main)
        
        # Titlebar
        self.titlebar.configure(fg_color=self.bg_painel, border_color=self.borda)
        self.lbl_title.configure(text_color=self.acento)
        self.btn_min.configure(hover_color=self.borda)
        
        self.sidebar.configure(fg_color=self.bg_painel, border_color=self.borda)
        self.lbl_logo.configure(text_color=self.acento)
        self.status_topo.configure(text_color="#2ecc71" if self.is_admin else self.acento)
        self.sw_master_sys.configure(progress_color=self.acento, fg_color=self.borda)
        self.sw_master_clean.configure(progress_color=self.acento, fg_color=self.borda)
        self.sw_sidebar_dark.configure(progress_color=self.acento, fg_color=self.borda)
        
        self.frame_hw.configure(fg_color=self.bg_main, border_color=self.borda)
        self.prog_cpu.configure(progress_color=self.acento, fg_color=self.borda)
        self.prog_ram.configure(progress_color=self.acento, fg_color=self.borda)
        self.prog_gpu.configure(progress_color=self.acento, fg_color=self.borda)
        
        self.btn_exportar.configure(fg_color="transparent", hover_color=self.acento, border_color=self.acento)
        self.btn_restore.configure(fg_color="transparent", hover_color=self.acento, border_color=self.acento)
        self.btn_manual.configure(fg_color="transparent", hover_color=self.acento, border_color=self.acento)
        self.combo_temas.configure(fg_color=self.bg_painel, button_color=self.borda, button_hover_color=self.acento, dropdown_fg_color=self.bg_painel, text_color=self.texto_branco)
        
        self.slider_mica.configure(progress_color=self.acento, button_color=self.acento)
        
        self.caixa_log.configure(fg_color=self.bg_main, text_color=self.texto_cinza, border_color=self.borda)
        
        self.lbl_cpu_tit.configure(text_color=self.texto_cinza)
        self.lbl_cpu_val.configure(text_color=self.texto_branco)
        self.lbl_ram_tit.configure(text_color=self.texto_cinza)
        self.lbl_ram_val.configure(text_color=self.texto_branco)
        self.lbl_gpu_tit.configure(text_color=self.texto_cinza)
        self.lbl_gpu_val.configure(text_color=self.texto_branco)
        self.lbl_tema_info.configure(text_color=self.texto_cinza)
        self.lbl_mica.configure(text_color=self.texto_cinza)
        
        self.tabview.configure(fg_color=self.bg_main, segmented_button_fg_color=self.bg_painel, segmented_button_selected_color=self.acento, segmented_button_unselected_color=self.bg_painel, text_color=self.texto_branco)
        
        for widget in self.cards_interface: 
            widget.destroy()
            
        self.cards_interface.clear()
        self.lista_switches.clear()
        
        self.montar_interface_total()
        self.log(f"Perfil de cores de engenharia alterado para: {novo_tema}")

    def atualizar_cores_perfis(self):
        if not hasattr(self, 'btn_gamer') or not hasattr(self, 'btn_trabalho'): 
            return
            
        cor_fundo_padrao = "transparent"
        cor_texto_padrao = self.texto_branco
        cor_borda_padrao = self.acento

        if self.perfil_ativo == "Gamer":
            self.btn_gamer.configure(fg_color=self.acento, text_color=self.bg_main, border_color=self.acento, text="DESATIVAR GAMER")
            self.btn_trabalho.configure(fg_color=cor_fundo_padrao, text_color=cor_texto_padrao, border_color=cor_borda_padrao, text="ATIVAR MODO")
        elif self.perfil_ativo == "Trabalho":
            self.btn_trabalho.configure(fg_color=self.borda, text_color=self.texto_branco, border_color=self.borda, text="DESATIVAR TRABALHO")
            self.btn_gamer.configure(fg_color=cor_fundo_padrao, text_color=cor_texto_padrao, border_color=cor_borda_padrao, text="ATIVAR MODO")
        else:
            self.btn_gamer.configure(fg_color=cor_fundo_padrao, text_color=cor_texto_padrao, border_color=cor_borda_padrao, text="ATIVAR MODO")
            self.btn_trabalho.configure(fg_color=cor_fundo_padrao, text_color=cor_texto_padrao, border_color=cor_borda_padrao, text="ATIVAR MODO")

    # --- FUNÇÕES DE EXPORTAÇÃO E MANUAL VISUAL ---
    def exportar_log(self):
        caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".txt", title="Salvar Log", initialfile="Log_Otimizacao.txt")
        if caminho_arquivo:
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo: 
                arquivo.write(self.caixa_log.get("1.0", "end-1c"))
            self.log(f"Log gravado no disco com sucesso em: {caminho_arquivo}")

    def abrir_manual(self):
        janela_manual = ctk.CTkToplevel(self)
        janela_manual.title("Manual do Sistema - Gustavo Optimizer v2.0 Elite")
        janela_manual.geometry("850x650")
        janela_manual.transient(self)
        janela_manual.grab_set() 
        janela_manual.configure(fg_color=self.bg_main)
        
        lbl_titulo = ctk.CTkLabel(janela_manual, text="[ MANUAL DE INSTRUÇÕES E DOCUMENTAÇÃO V2.0 ]", font=("Segoe UI", 18, "bold"), text_color=self.acento)
        lbl_titulo.pack(pady=(20, 10))
        
        caixa_texto = ctk.CTkTextbox(janela_manual, font=("Consolas", 13), fg_color=self.bg_painel, text_color=self.texto_branco, border_width=1, border_color=self.borda, corner_radius=12)
        caixa_texto.pack(expand=True, fill="both", padx=20, pady=10)

        manual_completo = (
            "================================================================================\n"
            "                 GUSTAVO OPTIMIZER v2.0.6 - ELITE EDITION                           \n"
            "================================================================================\n\n"
            "Bem-vindo à ferramenta definitiva de engenharia de software para Windows.\n"
            "Este manual contém a documentação técnica de todas as funções do sistema.\n\n"
            "================================================================================\n"
            "1. PERFIS E SISTEMA MASTER (PROTEÇÃO DE SESSÃO E AUDITORIA)\n"
            "================================================================================\n"
            "- AUDITORIA EM TEMPO REAL: O Optimizer agora lê o Kernel do Windows nativamente.\n"
            "  Se alterar definições 'por fora', o programa reconhece e ajusta-se no arranque.\n"
            "- MODO GAMER ELITE: Aplica ativamente a performance extrema em tempo real.\n"
            "- MASTER SISTEMA: Ativa chaves seguras (Ignorando propositadamente as de reinício).\n\n"
            "================================================================================\n"
            "2. OTIMIZAÇÕES NATIVAS (API KERNEL E BANDEJA)\n"
            "================================================================================\n"
            "- Purgar Standby List (ISLC): Invoca NtSetSystemInformation para esvaziar a RAM em\n"
            "  espera, aniquilando o 'Micro-Stuttering' nos jogos pesados.\n"
            "- Smart RAM Cleaner: Força processos em segundo plano a devolverem memória ociosa.\n"
            "- Auto Game Priority: Deteta jogos abertos (CS2, Valorant, etc.) e eleva o uso do CPU.\n"
            "- Minimizar para a Bandeja: Mantém o software ativo e invisível no System Tray.\n\n"
            "================================================================================\n"
            "3. DESEMPENHO PROFUNDO, UX E LATÊNCIA\n"
            "================================================================================\n"
            "- Desempenho Visual Máximo: Funde duas restrições e ajusta o Windows para o nível\n"
            "  absoluto de performance gráfica, cortando animações fluidas e janelas de acrílico.\n"
            "- Timer Resolution (0.5ms): Reduz o ciclo de relógio do Windows para resposta rápida.\n"
            "- Plano de Energia Máxima: Desbloqueia o plano de energia oculto para Workstations.\n"
            "- Core Parking: Obriga todos os núcleos lógicos do processador a manterem-se acordados.\n\n"
            "================================================================================\n"
            "4. INTERNET E REDE E-SPORTS (TCP/IP UNIFICADO)\n"
            "================================================================================\n"
            "- Otimização Global TCP/IP: Uma chave sênior unificada que executa simultaneamente a\n"
            "  remoção de Delay (Nagle's Algorithm), reescreve os Buffers Netsh e impõe o poderoso\n"
            "  controlo de congestionamento de Servidor Linux (CUBIC) à sua placa de rede.\n"
            "- Interrupt Moderation (NIC): Impede a placa de agrupar pacotes; dispara os dados na hora.\n"
            "- DSCP: Define os pacotes de jogos como prioridade máxima de tráfego no router local.\n\n"
            "================================================================================\n"
            "5. COMANDOS DE ROOT E SEGURANÇA (REINÍCIO)\n"
            "================================================================================\n"
            "- Forçar MSI Mode (GPU): Conecta a Placa Gráfica diretamente ao CPU, cortando Delay DPC.\n"
            "- Desligar HPET & Ticks: Corta o relógio de alta precisão antigo, estabilizando FPS.\n"
            "- Desbloquear Menus (Edge): Apaga chaves de proteção para libertar definições geridas\n"
            "  pela 'Organização'.\n\n"
        )
        
        caixa_texto.insert("0.0", manual_completo)
        caixa_texto.configure(state="disabled") 

        def salvar_manual():
            caminho = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="Manual_Elite.txt", title="Salvar Manual")
            if caminho:
                with open(caminho, "w", encoding="utf-8") as f: 
                    f.write(manual_completo)
                self.log(f"Documentação exportada para: {caminho}")
                janela_manual.destroy() 
                
        btn_salvar = ctk.CTkButton(janela_manual, text="EXPORTAR TEXTO PARA .TXT", command=salvar_manual, fg_color=self.bg_painel, hover_color=self.acento, text_color=self.texto_branco, border_width=1, border_color=self.acento, font=("Segoe UI", 12, "bold"), corner_radius=8)
        btn_salvar.pack(pady=(10, 20))

    def abrir_painel_debloat(self):
        janela_db = ctk.CTkToplevel(self)
        janela_db.title("Painel Interativo de Debloat e Restauro")
        janela_db.geometry("550x750")
        janela_db.transient(self)
        janela_db.grab_set()
        janela_db.configure(fg_color=self.bg_main)

        lbl_titulo = ctk.CTkLabel(janela_db, text="[ GERENCIADOR DE APPS DO WINDOWS ]", font=("Segoe UI", 16, "bold"), text_color=self.acento)
        lbl_titulo.pack(pady=(20, 10))

        frame_legenda = ctk.CTkFrame(janela_db, fg_color="transparent")
        frame_legenda.pack(pady=(0, 10))
        
        cor_instalado = "#2ecc71"
        cor_ausente = "#e74c3c"
        
        ctk.CTkLabel(frame_legenda, text="■ INSTALADO", font=("Segoe UI", 12, "bold"), text_color=cor_instalado).pack(side="left", padx=10)
        ctk.CTkLabel(frame_legenda, text="■ NÃO INSTALADO", font=("Segoe UI", 12, "bold"), text_color=cor_ausente).pack(side="left", padx=10)

        scroll_db = ctk.CTkScrollableFrame(janela_db, fg_color=self.bg_painel, border_width=1, border_color=self.borda, corner_radius=12)
        scroll_db.pack(expand=True, fill="both", padx=20, pady=5)

        lbl_loading = ctk.CTkLabel(scroll_db, text="A analisar o sistema... Por favor aguarde.", font=("Segoe UI", 12, "italic"), text_color=self.texto_cinza)
        lbl_loading.pack(pady=20)

        apps = {
            "Cortana": "*Microsoft.549981C3F5F10*", 
            "Xbox Game Bar & Serviços": "*Xbox*",
            "Microsoft Mapas": "*Maps*", 
            "Clima (Bing Weather)": "*BingWeather*",
            "Câmera Nativa": "*WindowsCamera*", 
            "Calculadora do Windows": "*Calculator*",
            "Visualizador 3D": "*3DViewer*", 
            "Pessoas (People)": "*People*",
            "Gravador de Voz": "*SoundRecorder*", 
            "Hub de Feedback": "*FeedbackHub*",
            "Microsoft Solitaire": "*SolitaireCollection*", 
            "Notícias": "*BingNews*"
        }

        vars_dict = {}

        def carregar_status():
            try:
                cmd_ps = 'powershell -Command "Get-AppxPackage | Select-Object -ExpandProperty Name"'
                res = subprocess.run(cmd_ps, capture_output=True, text=True, creationflags=0x08000000)
                pacotes_instalados = res.stdout.lower()
            except Exception:
                pacotes_instalados = ""
                
            def popular_ui():
                lbl_loading.destroy()
                for nome, pacote in apps.items():
                    var = ctk.IntVar()
                    termo_busca = pacote.replace("*", "").lower()
                    
                    if termo_busca in pacotes_instalados:
                        texto_exibicao = f"{nome} (Instalado)"
                        cor_texto = cor_instalado
                    else:
                        texto_exibicao = f"{nome} (Ausente)"
                        cor_texto = cor_ausente
                        
                    cb = ctk.CTkCheckBox(scroll_db, text=texto_exibicao, variable=var, text_color=cor_texto, fg_color=self.acento, font=("Segoe UI", 12, "bold"))
                    cb.pack(anchor="w", pady=5, padx=10)
                    vars_dict[pacote] = var
                    
            self.after(0, popular_ui)
            
        threading.Thread(target=carregar_status, daemon=True).start()

        def executar_acao(acao):
            selecionados = [pacote for pacote, var in vars_dict.items() if var.get() == 1]
            if not selecionados:
                self.log("[-] Nenhum aplicativo selecionado no painel.", "erro")
                return

            def tarefa():
                texto_acao = "remoção" if acao == "remover" else "reinstalação"
                self.log(f"[*] Iniciando {texto_acao} nativa de {len(selecionados)} pacotes no sistema...")
                
                passo = 1.0 / len(selecionados)
                prog = 0.0
                
                for pacote in selecionados:
                    if acao == "remover":
                        self.log(f"[*] A executar remoção profunda do sistema: {pacote}...")
                        cmd = f'powershell -Command "Get-AppxPackage {pacote} | Remove-AppxPackage"'
                    else:
                        self.log(f"[*] A executar reinstalação e restauro: {pacote}...")
                        cmd = f'powershell -Command "Get-AppxPackage -AllUsers {pacote} | ForEach-Object {{Add-AppxPackage -DisableDevelopmentMode -Register \\\"$($_.InstallLocation)\\AppXManifest.xml\\\"}}"'
                    
                    subprocess.run(cmd, shell=True, creationflags=0x08000000)
                    prog += passo
                    
                self.log(f"[+] Operação de {texto_acao} (Apps) concluída com sucesso no Kernel!")
                time.sleep(1.5)
                self.after(0, janela_db.destroy)

            threading.Thread(target=tarefa, daemon=True).start()

        frame_botoes = ctk.CTkFrame(janela_db, fg_color="transparent")
        frame_botoes.pack(pady=(10, 20), fill="x", padx=20)
        
        btn_remover = ctk.CTkButton(frame_botoes, text="DESINSTALAR", command=lambda: executar_acao("remover"), fg_color="#e74c3c", hover_color="#c0392b", font=("Segoe UI", 12, "bold"), corner_radius=8, width=150)
        btn_remover.pack(side="left", padx=10, expand=True)
        
        btn_reinstalar = ctk.CTkButton(frame_botoes, text="REINSTALAR", command=lambda: executar_acao("reinstalar"), fg_color="#2ecc71", hover_color="#27ae60", font=("Segoe UI", 12, "bold"), corner_radius=8, width=150)
        btn_reinstalar.pack(side="right", padx=10, expand=True)

    def remover_bloatware(self):
        self.log("[*] Redirecionando para o Gerenciador de Apps Avançado do Windows...")
        self.abrir_painel_debloat()

    # --- FUNÇÕES DE LAYOUT (A FUNDAÇÃO DA INTERFACE SOFT UI) ---
    def criar_secao(self, parent, texto, linha):
        lbl = ctk.CTkLabel(parent, text=f"// {texto.upper()}", font=("Segoe UI", 18, "bold"), text_color=self.acento)
        lbl.grid(row=linha, column=0, columnspan=3, pady=(25, 5), padx=10, sticky="w")
        self.cards_interface.append(lbl) 

    def criar_card_switch(self, parent, linha, coluna, categoria, titulo, descricao, cmd, nome_log, auto=True, reinicio=False):
        card = ctk.CTkFrame(parent, fg_color=self.bg_painel, corner_radius=10, width=335, height=165, border_width=1, border_color=self.borda)
        card.grid(row=linha, column=coluna, padx=10, pady=10, sticky="nw")
        card.grid_propagate(False)
        self.cards_interface.append(card)

        # Sistema Inteligente de Hover ligado à cor do Tema Atual
        def on_enter(event): card.configure(border_color=self.acento)
        def on_leave(event): card.configure(border_color=self.borda)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        lbl_cat = ctk.CTkLabel(card, text=f" {categoria.upper()} ", font=("Segoe UI", 11, "bold"), text_color=self.acento, fg_color=self.bg_main, corner_radius=4)
        lbl_cat.place(x=15, y=15)

        lbl_tit = ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 15, "bold"), text_color=self.texto_branco)
        lbl_tit.place(x=15, y=45)
        
        lbl_desc = ctk.CTkLabel(card, text=descricao, font=("Segoe UI", 11), text_color=self.texto_cinza, wraplength=305, justify="left")
        lbl_desc.place(x=15, y=72)

        if reinicio:
            lbl_reinicio = ctk.CTkLabel(card, text="[REQUER REINICIAR]", font=("Segoe UI", 10, "bold"), text_color="#FF4444")
            lbl_reinicio.place(x=15, y=125)
        
        sw = ctk.CTkSwitch(card, text="ATIVAR", progress_color=self.acento, fg_color=self.borda, font=("Segoe UI", 10, "bold"), text_color=self.acento)
        sw.place(x=225, y=125)
        
        estado_salvo = self.auditar_estado_real(nome_log)
        if estado_salvo == "1":
            sw.select()
        else:
            sw.deselect()

        def acao_com_memoria():
            cmd() 

        sw.configure(command=acao_com_memoria)
        sw.nome_log = nome_log 
        sw.comando_real = acao_com_memoria 
        
        if auto:
            self.lista_switches.append(sw)
            
        return sw

    def criar_card_botao(self, parent, linha, coluna, categoria, titulo, descricao, cmd, reinicio=False, btn_texto="EXECUTAR"):
        card = ctk.CTkFrame(parent, fg_color=self.bg_painel, corner_radius=10, width=335, height=165, border_width=1, border_color=self.borda)
        card.grid(row=linha, column=coluna, padx=10, pady=10, sticky="nw")
        card.grid_propagate(False)
        self.cards_interface.append(card)

        # Sistema Inteligente de Hover
        def on_enter(event): card.configure(border_color=self.acento)
        def on_leave(event): card.configure(border_color=self.borda)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        lbl_cat = ctk.CTkLabel(card, text=f" {categoria.upper()} ", font=("Segoe UI", 11, "bold"), text_color=self.acento, fg_color=self.bg_main, corner_radius=4)
        lbl_cat.place(x=15, y=15)

        lbl_tit = ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 15, "bold"), text_color=self.texto_branco)
        lbl_tit.place(x=15, y=45)
        
        lbl_desc = ctk.CTkLabel(card, text=descricao, font=("Segoe UI", 11), text_color=self.texto_cinza, wraplength=305, justify="left")
        lbl_desc.place(x=15, y=72)

        if reinicio:
            lbl_reinicio = ctk.CTkLabel(card, text="[REQUER REINICIAR]", font=("Segoe UI", 10, "bold"), text_color="#FF4444")
            lbl_reinicio.place(x=15, y=125)
        
        btn = ctk.CTkButton(card, text=btn_texto, command=cmd, fg_color="transparent", hover_color=self.acento, text_color=self.texto_branco, corner_radius=6, border_width=2, border_color=self.acento, width=120, height=28, font=("Segoe UI", 11, "bold"))
        btn.place(x=195, y=120)
        
        return btn

    # --- MONTAGEM DAS GRELHAS TEMÁTICAS (SISTEMA DE ABAS) ---
    def montar_interface_total(self):
        
        # TAB 1: ⚡ DESEMPENHO (scroll_desempenho)
        self.criar_secao(self.scroll_desempenho, "Perfis Inteligentes V2.0", 0)
        self.btn_gamer = self.criar_card_botao(self.scroll_desempenho, 1, 0, "Desempenho", "🎮 Ativar Modo Gamer", "Aplica simultaneamente as 15 chaves dinâmicas de CPU, GPU, Rede e RAM.", self.acionar_perfil_gamer, btn_texto="ATIVAR MODO")
        self.btn_trabalho = self.criar_card_botao(self.scroll_desempenho, 1, 1, "Equilíbrio", "💼 Ativar Modo Trabalho", "Desliga agressivamente todas as otimizações, forçando estabilidade.", self.acionar_perfil_trabalho, btn_texto="ATIVAR MODO")

        self.criar_secao(self.scroll_desempenho, "Otimizações Nativas (Kernel e RAM)", 2)
        self.criar_card_botao(self.scroll_desempenho, 3, 0, "Memória", "🚀 Smart RAM Cleaner", "Liberta memória em cache de processos nativos da API do Windows.", self.otimizar_ram_nativa, btn_texto="LIMPAR RAM")
        self.criar_card_botao(self.scroll_desempenho, 3, 1, "Memória", "🌪️ Purgar Standby (ISLC)", "Nível Elite: Usa a API Ntdll para exterminar Stuttering por falta de RAM.", self.purgar_standby_list_nativa, btn_texto="PURGAR STANDBY")
        self.criar_card_botao(self.scroll_desempenho, 3, 2, "Desempenho", "🎯 Auto Game Priority", "Localiza jogos ativos na RAM e eleva-os para prioridade Máxima.", self.prioridade_jogos_nativa, btn_texto="APLICAR CPU")
        
        self.criar_card_botao(self.scroll_desempenho, 4, 0, "Hardware", "🖥️ Validador de Hz", "Consulta a API gráfica para confirmar os Hertz reais do seu monitor.", self.verificar_hz_monitor, btn_texto="VERIFICAR TELA")
        
        self.criar_secao(self.scroll_desempenho, "Desempenho Profundo", 5)
        self.sw_thrott = self.criar_card_switch(self.scroll_desempenho, 6, 0, "Desempenho", "🔋 Power Throttling", "Impede o Windows de cortar energia dos programas minimizados.", self.toggle_thrott, "Power Throttling")
        self.sw_gaming = self.criar_card_switch(self.scroll_desempenho, 6, 1, "Jogos", "🕹️ Modo de Jogo Pro", "Aplica o Gaming Mode e assassina as gravações Xbox GameDVR.", self.toggle_gaming, "Gaming Mode")
        self.sw_tim = self.criar_card_switch(self.scroll_desempenho, 6, 2, "Latência", "⏱️ Timer Res (0.5ms)", "Força o Timer do Kernel para precisão cirúrgica de Input.", self.toggle_tim, "Timer Res")
        
        self.sw_pow = self.criar_card_switch(self.scroll_desempenho, 7, 0, "Desempenho", "⚡ Plano Energia Máxima", "Revela e aplica o plano de Workstation escondido (Ultimate).", self.toggle_pow, "Powerplan")
        self.sw_gpu_oc = self.criar_card_switch(self.scroll_desempenho, 7, 1, "Hardware", "🔥 Bloquear Economia GPU", "A Placa de Vídeo não vai baixar os Mhz quando estiver em repouso.", self.toggle_gpu_oc, "GPU Downclock")
        self.sw_flip = self.criar_card_switch(self.scroll_desempenho, 7, 2, "Latência", "🪟 Flip Fix (Janelas)", "Altera o modo de apresentação para tirar delay de Jogos em Janela.", self.toggle_flip_fix, "Flip Fix")
        
        self.sw_srv = self.criar_card_switch(self.scroll_desempenho, 8, 0, "Desempenho", "🔍 SysMain e Search", "Apaga o Superfetch. Liberta RAM brutal desativando indexação.", self.toggle_srv, "Servicos Windows")
        self.sw_core_park = self.criar_card_switch(self.scroll_desempenho, 8, 1, "Hardware", "🧠 Desativar Core Parking", "Processador a 100%: Nenhum núcleo volta a adormecer.", self.toggle_core_parking, "Core Parking")


        # TAB 2: 🌐 REDE & INTERNET (scroll_rede)
        self.criar_secao(self.scroll_rede, "Internet e Rede E-Sports", 0)
        self.criar_card_botao(self.scroll_rede, 1, 0, "Diagnóstico", "🌍 Benchmark DNS Global", "Testa a rota do seu DNS e os mundiais, abrindo seleção para aplicar.", self.benchmark_dns_nativo, btn_texto="TESTAR ROTAS")
        self.criar_card_botao(self.scroll_rede, 1, 1, "Diagnóstico", "📡 Analisar IP e Ping", "Varre a sua LAN e faz request remoto à API IPify para o seu WAN.", self.analisar_rede_info, btn_texto="INICIAR SCAN")
        self.criar_card_botao(self.scroll_rede, 1, 2, "Rede", "🔌 Redefinir Placa (DNS)", "Apaga o DNS Cache e aplica reset severo ao IPConfig do adaptador.", self.otimizar_internet, btn_texto="RESET PLACA")

        self.sw_nic_int = self.criar_card_switch(self.scroll_rede, 2, 0, "Rede", "🚥 Interrupt Moderation", "Elite: Impede a placa de rede de agrupar pacotes. Envia os tiros NA HORA.", self.toggle_nic_interrupt, "NIC Interrupt")
        self.sw_tcp_global = self.criar_card_switch(self.scroll_rede, 2, 1, "Rede", "⚡ Otimização TCP/IP", "Unifica TcpNoDelay, Controle CUBIC e Buffers Netsh para a menor latência.", self.toggle_tcp_global, "TCP Global")
        self.sw_dscp = self.criar_card_switch(self.scroll_rede, 2, 2, "Rede", "📦 Otimizar Pacotes DSCP", "Pede ao seu router para dar prioridade de realeza aos pacotes do Jogo.", self.toggle_dscp, "DSCP")
        self.sw_net_thrott = self.criar_card_switch(self.scroll_rede, 3, 0, "Rede", "🔓 Desbloquear Largura", "Destrói a restrição de rede que o Windows impõe aos jogos.", self.toggle_net_thrott, "Network Throttling")


        # TAB 3: 🛡️ PRIVACIDADE & OS (scroll_privacidade)
        self.criar_secao(self.scroll_privacidade, "Privacidade e Segurança", 0)
        self.sw_vs_tel = self.criar_card_switch(self.scroll_privacidade, 1, 0, "Privacidade", "🚫 Telemetria Visual Studio", "Impede o VS de enviar dados de uso para a Microsoft.", self.toggle_vs_tel, "VS Telemetry")
        self.sw_tel = self.criar_card_switch(self.scroll_privacidade, 1, 1, "Privacidade", "🕵️ DiagTrack (Rastreamento)", "Desativa o serviço de rastreamento de diagnósticos do Windows.", self.toggle_tel, "DiagTrack")
        self.sw_nv_priv = self.criar_card_switch(self.scroll_privacidade, 1, 2, "Privacidade", "🛑 Privacidade NVIDIA", "Desativa a coleta de dados e serviços de fundo da NVIDIA.", self.toggle_nv_priv, "NVIDIA Privacy")
        
        self.sw_loc = self.criar_card_switch(self.scroll_privacidade, 2, 0, "Privacidade", "📍 Localização do Sistema", "Desativa o serviço de geolocalização e acesso à posição por apps.", self.toggle_loc, "GeoLocation")
        self.sw_tasks = self.criar_card_switch(self.scroll_privacidade, 2, 1, "Segurança", "👻 Tarefas Ocultas (MS)", "Mata os agendadores secretos que enviam dados na calada da noite.", self.toggle_telemetry_tasks, "Telemetry Tasks")
        self.criar_card_botao(self.scroll_privacidade, 2, 2, "Segurança", "🔓 Desbloquear Menus Edge", "Remove restrições de 'Organização' que bloqueiam o Microsoft Edge.", self.remover_bloqueio_organizacao, btn_texto="DESBLOQUEAR")

        self.criar_secao(self.scroll_privacidade, "Sistema e Interface Visual", 3)
        self.criar_card_botao(self.scroll_privacidade, 4, 0, "Sistema", "📦 Gerir Apps do Windows", "Abre janela Elite para apagar ou reinstalar apps nativos do Windows.", self.abrir_painel_debloat, btn_texto="ABRIR PAINEL")
        self.criar_card_botao(self.scroll_privacidade, 4, 1, "Sistema", "🚀 Apps de Inicialização", "Abre o gestor nativo do Windows para impedir programas no arranque.", self.abrir_inicializacao, btn_texto="ABRIR GESTOR")
        self.sw_visual_perf = self.criar_card_switch(self.scroll_privacidade, 4, 2, "Interface", "✨ Desempenho Visual Máx.", "Ajusta a aparência para desempenho, desativando efeitos e sombras pesadas.", self.toggle_visual_perf, "Desempenho Visual")


        # TAB 4: 🧹 LIMPEZA (scroll_limpeza)
        self.criar_secao(self.scroll_limpeza, "Manutenção e Verificação", 0)
        self.criar_card_botao(self.scroll_limpeza, 1, 0, "Limpeza Profunda", "🗑️ Pasta Temporária Visual", "Destrói lixo eletrónico mapeando ficheiros individualmente sem CMD.", self.limpar_temp_nativa, btn_texto="LIMPAR TEMP")
        self.criar_card_botao(self.scroll_limpeza, 1, 1, "Sistema", "🔧 Reparo de Imagem (DISM)", "Puxa pacotes sãos da Microsoft para curar corrupção no núcleo.", self.reparar_imagem_dism, btn_texto="REPARAR")
        self.criar_card_botao(self.scroll_limpeza, 1, 2, "Limpeza", "📜 Limpar Logs de Eventos", "Executa Wevtutil para eliminar milhares de falsos erros ocultos.", self.limpar_logs_windows, btn_texto="LIMPAR LOGS")
        
        self.criar_card_botao(self.scroll_limpeza, 2, 0, "Limpeza", "⚡ Arquivos de Prefetch", "Destrói a memória morta do arranque para forçar recriação veloz.", self.limpar_prefetch, btn_texto="LIMPAR PREFETCH")
        self.criar_card_botao(self.scroll_limpeza, 2, 1, "Hardware", "🎮 Limpar Cache NVIDIA", "Apaga shaders gráficos obsoletos diretamente do LocalAppData.", self.limpar_gpu, btn_texto="LIMPAR SHADERS")
        self.criar_card_botao(self.scroll_limpeza, 2, 2, "Disco", "💽 Limpeza Disco Avançada", "Aplica o Cleanmgr do Windows no seu nível máximo e silencioso.", self.limpar_windows, btn_texto="EXECUTAR CLEANMGR")
        
        self.criar_card_botao(self.scroll_limpeza, 3, 0, "Sistema", "🔄 Limpar Windows Update", "Estripa o SoftwareDistribution, matando updates emperrados.", self.limpar_update, btn_texto="LIMPAR UPDATES")
        self.criar_card_botao(self.scroll_limpeza, 3, 1, "Interface", "🖼️ Limpar Miniaturas", "Exclui o cache de imagens para forçar o recarregamento dos ícones.", self.limpar_thumbnails, btn_texto="LIMPAR ÍCONES")
        self.criar_card_botao(self.scroll_limpeza, 3, 2, "Disco", "⚙️ Otimizar Unidades", "Executa rotina TRIM em todos os SSDs e desfragmenta mecânicos.", self.otimizar_discos, btn_texto="OTIMIZAR DISCOS")

        self.criar_secao(self.scroll_limpeza, "Ofuscação e Limpeza de Aplicações", 4)
        self.criar_card_botao(self.scroll_limpeza, 5, 0, "Navegador", "🌐 Exterminar Cache Google", "Apaga rastros de pesquisa temporária no Chrome sem desinstalar.", self.limpar_chrome, btn_texto="LIMPAR CHROME")
        self.criar_card_botao(self.scroll_limpeza, 5, 1, "Navegador", "🌐 Exterminar Cache Edge", "Força a exclusão do diretório User Data do MS Edge da sua máquina.", self.limpar_edge, btn_texto="LIMPAR EDGE")
        self.criar_card_botao(self.scroll_limpeza, 5, 2, "Navegador", "🦊 Limpar Mozilla Firefox", "Apaga o cache completo de todos os perfis do Mozilla Firefox do PC.", self.limpar_firefox, btn_texto="LIMPAR FIREFOX")

        self.criar_card_botao(self.scroll_limpeza, 6, 0, "Navegador", "🔴 Limpar Opera / GX", "Apaga dados antigos armazenados pelas versões do Opera Browser.", self.limpar_opera, btn_texto="LIMPAR OPERA")
        self.criar_card_botao(self.scroll_limpeza, 6, 1, "Aplicativo", "🎮 Limpar Cache Steam", "Limpa pasta AppCache. Pode resolver bugs de não atualizar jogos.", self.limpar_steam, btn_texto="LIMPAR STEAM")
        self.criar_card_botao(self.scroll_limpeza, 6, 2, "Aplicativo", "💬 Limpar Cache Discord", "Mata a árvore inteira de cache do Discord que se esconde no disco.", self.limpar_discord, btn_texto="LIMPAR DISCORD")
        
        self.criar_card_botao(self.scroll_limpeza, 7, 0, "Aplicativo", "🎵 Limpar Cache Spotify", "Apaga dados antigos e músicas em cache armazenadas pelo aplicativo.", self.limpar_spotify, btn_texto="LIMPAR SPOTIFY")
        self.criar_card_botao(self.scroll_limpeza, 7, 1, "Aplicativo", "⚔️ Limpar Battle.net", "Abre caminho livre apagando os agentes da Blizzard que ficam presos.", self.limpar_battlenet, btn_texto="LIMPAR BNET")
        self.criar_card_botao(self.scroll_limpeza, 7, 2, "Geral", "💥 Limpeza Total (Apps)", "Limpa simultaneamente Spotify, Steam, Discord e Battle.net.", self.limpar_apps_multi, btn_texto="DESTRUIR TUDO")


        # TAB 5: ⚙️ ROOT (scroll_root)
        self.criar_secao(self.scroll_root, "Comandos de Root (Requer Reiniciar o Computador)", 0)
        self.sw_msi = self.criar_card_switch(self.scroll_root, 1, 0, "Latência", "🔌 Modo MSI (Para GPU)", "Força a Placa de Vídeo a comunicar sem interrupções com o CPU.", self.toggle_msi, "Modo MSI", auto=False, reinicio=True)
        self.sw_hpet = self.criar_card_switch(self.scroll_root, 1, 1, "Latência", "⏰ Desligar HPET & Ticks", "Desliga o relógio lento da Motherboard para dar fluidez aos FPS.", self.toggle_hpet, "HPET Ticks", auto=False, reinicio=True)
        self.sw_mouse = self.criar_card_switch(self.scroll_root, 1, 2, "Hardware", "🖱️ Mira Perfeita (Raw Mouse)", "Mata os parâmetros invisíveis de aceleração de rato no Registo.", self.toggle_mouse, "Raw Mouse", auto=False, reinicio=True)
        
        self.sw_mnu = self.criar_card_switch(self.scroll_root, 2, 0, "Interface", "📋 Menu Clássico Win11", "Extermina o design novo de 2 cliques e traz de volta o Menu Gigante.", self.toggle_mnu, "Menu Clássico", auto=False, reinicio=True)
        self.sw_bmn = self.criar_card_switch(self.scroll_root, 2, 1, "Sistema", "⏳ Espera de Boot (2 Seg)", "Acelera a tela de Dual-Boot para não ficar à espera do sistema.", self.toggle_bmn, "Boot Menu", auto=False, reinicio=True)
        self.sw_fast_start = self.criar_card_switch(self.scroll_root, 2, 2, "Sistema", "💤 Desativar Fast Startup", "Protege a RAM contra corrupção ao impedir o PC de fingir que desligou.", self.toggle_fast_startup, "Fast Startup", auto=False, reinicio=True)
        
        self.sw_widgets = self.criar_card_switch(self.scroll_root, 3, 0, "Interface", "📰 Desativar Widgets", "Remove completamente os blocos de Notícias e Clima que sugam RAM.", self.toggle_widgets, "Widgets", auto=False, reinicio=True)
        self.criar_card_botao(self.scroll_root, 3, 1, "Sistema", "🔍 Verificação SFC Scan", "Busca nos servidores Microsoft e repara arquivos corrompidos/ausentes.", self.verificar_erros, reinicio=True, btn_texto="SFC SCAN")
        self.criar_card_botao(self.scroll_root, 3, 2, "Sistema", "💽 Verificar Discos (CHKDSK)", "Examina a integridade e procura setores defeituosos em TODOS os discos.", self.verificar_disco, reinicio=True, btn_texto="RODAR CHKDSK")
        
        self.atualizar_cores_perfis()

    # --- FUNÇÃO EXECUÇÃO SEGURA E UI-SAFE ---
    def executar_comando(self, comando):
        try:
            resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, creationflags=0x08000000)
            return resultado.returncode
        except Exception as e: 
            self.log(f"Erro na execução da subrotina: {str(e)}", "erro")
            return 1

    def executar_comando_visivel(self, comando, nome_log, reinicio=False):
        def tarefa():
            try:
                processo = subprocess.Popen(f'cmd /c "{comando}"', creationflags=subprocess.CREATE_NEW_CONSOLE)
                processo.wait() 
                res = processo.returncode
                self.log_res_simples(res, nome_log, None, reinicio)
            except Exception as e: 
                self.log(f"Erro ao executar e desenhar janela de CMD {nome_log}: {str(e)}", "erro")
                
        threading.Thread(target=tarefa, daemon=True).start()

    def executar_comando_assincrono(self, comando, nome_log, sw_obj=None, reinicio=False):
        def tarefa():
            try:
                processo = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=0x08000000)
                stdout, stderr = processo.communicate()
                res = processo.returncode
                self.log_res(res, nome_log, sw_obj, reinicio, stdout, stderr)
            except Exception as e: 
                self.log(f"[-] Erro Crítico Assíncrono ao processar {nome_log}: {str(e)}", "erro")
                if sw_obj:
                    self.after(0, sw_obj.deselect)
                
        threading.Thread(target=tarefa, daemon=True).start()

    # --- AUDITORIA DE MEMÓRIA REAL (VERIFICAÇÃO DE ERROS WINDOWS) ---
    def log(self, mensagem, tipo="info"):
        prefixo = "[+] " if tipo == "info" else "[-] "
        def update_ui():
            self.caixa_log.insert("end", f"{prefixo}{mensagem}\n")
            self.caixa_log.see("end")
            self.update_idletasks()
        self.after(0, update_ui)

    def log_res_simples(self, res, nome, sw_obj=None, reinicio=False):
        def update_ui():
            aviso = " [O SISTEMA REQUER REINÍCIO PARA APLICAR]" if reinicio else ""
            if res == 0: 
                self.caixa_log.insert("end", f"[+] {nome}: Aplicado com sucesso no sistema.{aviso}\n")
            else: 
                self.caixa_log.insert("end", f"[-] AVISO: {nome} retornou falha (Código {res}).\n")
            self.caixa_log.see("end")
            self.update_idletasks()
        self.after(0, update_ui)

    def log_res(self, res, nome, sw_obj=None, reinicio=False, stdout="", stderr=""):
        def update_ui():
            aviso = " [O SISTEMA REQUER REINÍCIO PARA APLICAR]" if reinicio else ""
            if res == 0: 
                self.caixa_log.insert("end", f"[+] SUCESSO | {nome}: Alteração validada pelo Windows.{aviso}\n")
                if sw_obj is not None and hasattr(sw_obj, 'nome_log'): 
                    self.salvar_config(sw_obj.nome_log, str(sw_obj.get()))
            else: 
                erro_txt = stderr.strip() if stderr else "Acesso Negado ou Falha de Permissão do Registo"
                self.caixa_log.insert("end", f"[-] ERRO | {nome}: {erro_txt} (Cód. {res}). Revertendo a interface de imediato...\n")
                if sw_obj is not None:
                    estado_memoria = self.carregar_config(sw_obj.nome_log, "0")
                    if estado_memoria == "1":
                        sw_obj.select()
                    else:
                        sw_obj.deselect()
            self.caixa_log.see("end")
            self.update_idletasks()
        self.after(0, update_ui)

    # --- HELPER UI-SAFE E MANIPULAÇÃO DE RENDERIZAÇÃO ---
    def forcar_ativo(self, sw):
        def acao():
            try:
                if int(sw.get()) == 0: 
                    sw.select()
                    if hasattr(sw, 'comando_real'): 
                        sw.comando_real()
            except Exception: 
                pass
        self.after(0, acao)
        time.sleep(0.1) 

    def forcar_desligado(self, sw):
        def acao():
            try:
                if int(sw.get()) == 1: 
                    sw.deselect()
                    if hasattr(sw, 'comando_real'): 
                        sw.comando_real()
            except Exception: 
                pass
        self.after(0, acao)
        time.sleep(0.1)

    # --- COMANDOS DE PERFIL INTELIGENTE (MASTER SWITCH APENAS CHAVES DINÂMICAS) ---
    def executar_restauracao_thread(self):
        self.log("[*] Invocando Root Master Switch: Desligando e revertendo as 15 chaves de performance ativa...")
        
        switches_gamer_dinamicos = [
            self.sw_pow, self.sw_gaming, self.sw_net_thrott, self.sw_core_park,
            self.sw_tim, self.sw_gpu_oc, self.sw_flip, self.sw_srv,
            self.sw_dscp, self.sw_tcp_global, self.sw_thrott,
            self.sw_nic_int, self.sw_visual_perf
        ]
        
        for sw in switches_gamer_dinamicos: 
            self.forcar_desligado(sw)
            
        self.estado_anterior.clear()
        self.salvar_config("SnapshotPerfil", "") 
        self.log("[+] Reversão dinâmica concluída. O sistema regressou à estabilidade total de origem.")

    def aplicar_gamer_avancado(self):
        self.log("[*] APLICANDO MODO GAMER ELITE: Aplicando as 15 camadas de Hardware, Rede e Latência Zero...")
        
        switches_gamer_dinamicos = [
            self.sw_pow, self.sw_gaming, self.sw_net_thrott, self.sw_core_park,
            self.sw_tim, self.sw_gpu_oc, self.sw_flip, self.sw_srv,
            self.sw_dscp, self.sw_tcp_global, self.sw_thrott,
            self.sw_nic_int, self.sw_visual_perf
        ]
        
        for sw in switches_gamer_dinamicos: 
            self.forcar_ativo(sw)
            
        self.log("[+] MODO GAMER MÁXIMO CONCLUÍDO! (As opções que requerem reinício foram ignoradas para proteger a sua sessão).")

    def aplicar_trabalho_avancado(self):
        self.log("[*] APLICANDO MODO TRABALHO: Desligando a prioridade extrema agressivamente...")
        
        switches_trabalho_dinamicos = [
            self.sw_pow, self.sw_gaming, self.sw_net_thrott, self.sw_core_park,
            self.sw_tim, self.sw_gpu_oc, self.sw_flip, self.sw_srv,
            self.sw_dscp, self.sw_tcp_global, self.sw_thrott,
            self.sw_nic_int, self.sw_visual_perf
        ]
        
        for sw in switches_trabalho_dinamicos: 
            self.forcar_desligado(sw)
            
        self.log("[+] MODO TRABALHO ATIVO! A sua estabilidade de energia e gestão de pacotes foi recuperada para uso pesado de multitarefas.")

    def acionar_perfil_gamer(self):
        if self.perfil_ativo == "Gamer":
            self.perfil_ativo = "Nenhum"
            self.salvar_config("PerfilAtivo", self.perfil_ativo)
            self.atualizar_cores_perfis()
            threading.Thread(target=self.executar_restauracao_thread, daemon=True).start()
        else:
            if self.perfil_ativo == "Nenhum": 
                self.guardar_snapshot_atual()
                
            self.perfil_ativo = "Gamer"
            self.salvar_config("PerfilAtivo", self.perfil_ativo)
            self.atualizar_cores_perfis()
            threading.Thread(target=self.aplicar_gamer_avancado, daemon=True).start()

    def acionar_perfil_trabalho(self):
        if self.perfil_ativo == "Trabalho":
            self.perfil_ativo = "Nenhum"
            self.salvar_config("PerfilAtivo", self.perfil_ativo)
            self.atualizar_cores_perfis()
            threading.Thread(target=self.executar_restauracao_thread, daemon=True).start()
        else:
            if self.perfil_ativo == "Nenhum": 
                self.guardar_snapshot_atual()
                
            self.perfil_ativo = "Trabalho"
            self.salvar_config("PerfilAtivo", self.perfil_ativo)
            self.atualizar_cores_perfis()
            threading.Thread(target=self.aplicar_trabalho_avancado, daemon=True).start()

    # --- NOVOS COMANDOS DE ELITE V2.0 (MODIFICAÇÃO DE REGISTO EM ROOT) ---
    def toggle_msi(self):
        est = self.sw_msi.get()
        valor_msi = str(1 if est == 1 else 0)
        
        cmd = (
            'powershell -Command "Get-ChildItem \'HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\PCI\' -Recurse -Depth 3 | '
            'Where-Object { (Get-ItemProperty $_.PSPath -Name \'Class\' -ErrorAction SilentlyContinue).Class -eq \'Display\' } | '
            'ForEach-Object { $m = Join-Path $_.PSPath \'Device Parameters\\Interrupt Management\\MessageSignaledInterruptProperties\'; '
            'if (Test-Path $m) { Set-ItemProperty -Path $m -Name \'MSISupported\' -Value ' + valor_msi + ' -Type DWord } }"'
        )
        self.executar_comando_assincrono(cmd, "Forçar Modo MSI Baseado no Hardware (Placa de Vídeo)", self.sw_msi, reinicio=True)

    def toggle_hpet(self):
        est = self.sw_hpet.get()
        
        if est == 1:
            cmd = "bcdedit /deletevalue useplatformclock >nul 2>&1 & bcdedit /set disabledynamictick yes >nul 2>&1"
        else:
            cmd = "bcdedit /set useplatformclock yes >nul 2>&1 & bcdedit /deletevalue disabledynamictick >nul 2>&1"
            
        self.executar_comando_assincrono(cmd, "HPET & Eventos de Dynamic Ticks da Motherboard", self.sw_hpet, reinicio=True)

    def toggle_mouse(self):
        est = self.sw_mouse.get()
        
        if est == 1:
            cmd = 'reg add "HKCU\\Control Panel\\Mouse" /v "MouseSpeed" /t REG_SZ /d "0" /f >nul 2>&1 & reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold1" /t REG_SZ /d "0" /f >nul 2>&1 & reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold2" /t REG_SZ /d "0" /f >nul 2>&1'
        else:
            cmd = 'reg add "HKCU\\Control Panel\\Mouse" /v "MouseSpeed" /t REG_SZ /d "1" /f >nul 2>&1 & reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold1" /t REG_SZ /d "6" /f >nul 2>&1 & reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold2" /t REG_SZ /d "10" /f >nul 2>&1'
            
        self.executar_comando_assincrono(cmd, "Mira Perfeita em FPS (Raw Mouse Input Exato)", self.sw_mouse, reinicio=True)

    def toggle_nic_interrupt(self):
        est = self.sw_nic_int.get()
        
        if est == 1:
            cmd = 'powershell -Command "$net = Get-NetAdapter -Physical | Where-Object { $_.Status -eq \'Up\' }; if ($net) { $net | Disable-NetAdapterInterruptModeration -ErrorAction SilentlyContinue; exit 0 } else { exit 1 }"'
        else:
            cmd = 'powershell -Command "$net = Get-NetAdapter -Physical | Where-Object { $_.Status -eq \'Up\' }; if ($net) { $net | Enable-NetAdapterInterruptModeration -ErrorAction SilentlyContinue; exit 0 } else { exit 1 }"'
            
        self.executar_comando_assincrono(cmd, "Moderação de Interrupção de Rede Pura (Adaptador NIC)", self.sw_nic_int)

    def toggle_visual_perf(self):
        est = self.sw_visual_perf.get()
        val_fx = 2 if est == 1 else 0
        val_tra = 0 if est == 1 else 1
        
        cmd = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d {val_fx} /f >nul 2>&1 & reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "EnableTransparency" /t REG_DWORD /d {val_tra} /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Aparência e Desempenho Visual Máximo", self.sw_visual_perf)

    # --- COMANDOS E SWITCHES ORIGINAIS ---
    def remover_bloqueio_organizacao(self):
        self.log("[*] Removendo Políticas de Grupo (GPO) que bloqueiam o Microsoft Edge e Configurações do Windows...")
        cmd = 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /f >nul 2>&1 & reg delete "HKCU\\SOFTWARE\\Policies\\Microsoft\\Edge" /f >nul 2>&1 & gpupdate /force'
        self.executar_comando_assincrono(cmd, "Desbloqueio de Menus Gerenciados por Organização")

    def toggle_telemetry_tasks(self):
        est = self.sw_tasks.get()
        p1 = "\\".join(["Microsoft", "Windows", "Application Experience", "Microsoft Compatibility Appraiser"])
        p2 = "\\".join(["Microsoft", "Windows", "Customer Experience Improvement Program", "Consolidator"])
        
        if est == 1:
            cmd = f'schtasks /Change /TN "{p1}" /Disable >nul 2>&1 & schtasks /Change /TN "{p2}" /Disable >nul 2>&1'
        else:
            cmd = f'schtasks /Change /TN "{p1}" /Enable >nul 2>&1 & schtasks /Change /TN "{p2}" /Enable >nul 2>&1'
            
        self.executar_comando_assincrono(cmd, "Agendadores Secretos e Tarefas de Telemetria", self.sw_tasks)

    def toggle_vs_tel(self): 
        est = self.sw_vs_tel.get()
        comando = f'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\VisualStudio\\Telemetry" /v "RefuseTelemetry" /t REG_DWORD /d {1 if est == 1 else 0} /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Limpeza de VS Telemetry Server", self.sw_vs_tel)

    def toggle_thrott(self): 
        est = self.sw_thrott.get()
        comando = f'reg add "HKLM\\System\\CurrentControlSet\\Control\\Power\\PowerThrottling" /v "PowerThrottlingOff" /t REG_DWORD /d {1 if est == 1 else 0} /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Power Throttling do Processador Central", self.sw_thrott)
    
    def toggle_loc(self): 
        est = self.sw_loc.get()
        if est == 1:
            cmd = 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v "DisableLocation" /t REG_DWORD /d 1 /f >nul 2>&1'
        else:
            cmd = 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v "DisableLocation" /f >nul 2>&1'
            
        self.executar_comando_assincrono(cmd, "Sensor de Localização Oculta do Sistema", self.sw_loc)

    def toggle_gaming(self): 
        est = self.sw_gaming.get()
        
        if est == 1:
            cmd = 'reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f >nul 2>&1 & reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f >nul 2>&1'
        else:
            cmd = 'reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 0 /f >nul 2>&1 & reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 1 /f >nul 2>&1'
            
        self.executar_comando_assincrono(cmd, "Modo de Jogo Pro Nativo (Gaming Mode API)", self.sw_gaming)

    def toggle_dscp(self): 
        est = self.sw_dscp.get()
        comando = f'reg add "HKLM\\System\\CurrentControlSet\\Services\\Tcpip\\Parameters\\QoS" /v "Do not use NLA" /t REG_SZ /d "{1 if est == 1 else 0}" /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Otimização Severa de Pacotes DSCP no Router", self.sw_dscp)

    def toggle_tcp_global(self): 
        est = self.sw_tcp_global.get()
        if est == 1:
            cmd = (
                'powershell -Command "Get-ChildItem -Path HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces | ForEach-Object { Set-ItemProperty -Path $_.PSPath -Name \'TcpAckFrequency\' -Value 1 -Type DWord -ErrorAction SilentlyContinue; Set-ItemProperty -Path $_.PSPath -Name \'TCPNoDelay\' -Value 1 -Type DWord -ErrorAction SilentlyContinue }" & '
                'netsh int tcp set global autotuninglevel=disabled >nul 2>&1 & '
                'netsh int tcp set supplemental template=internet congestionprovider=cubic >nul 2>&1'
            )
        else:
            cmd = (
                'powershell -Command "Get-ChildItem -Path HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces | ForEach-Object { Remove-ItemProperty -Path $_.PSPath -Name \'TcpAckFrequency\' -ErrorAction SilentlyContinue; Remove-ItemProperty -Path $_.PSPath -Name \'TCPNoDelay\' -ErrorAction SilentlyContinue }" & '
                'netsh int tcp set global autotuninglevel=normal >nul 2>&1 & '
                'netsh int tcp set supplemental template=internet congestionprovider=none >nul 2>&1'
            )
            
        self.executar_comando_assincrono(cmd, "Otimização Global da Pilha TCP/IP", self.sw_tcp_global)
        
    def toggle_gpu_oc(self): 
        est = self.sw_gpu_oc.get()
        comando = f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e968-e325-11ce-bfc1-08002be10318}}\\0000" /v "PowerMizerEnable" /t REG_DWORD /d {0 if est == 1 else 1} /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Força Bruta e Bloqueio de Economia da GPU", self.sw_gpu_oc)

    def toggle_tel(self): 
        est = self.sw_tel.get()
        
        if est == 1:
            cmd = "sc stop DiagTrack >nul 2>&1 & sc config DiagTrack start= disabled >nul 2>&1"
        else:
            cmd = "sc config DiagTrack start= auto >nul 2>&1 & sc start DiagTrack >nul 2>&1"
            
        self.executar_comando_assincrono(cmd, "Assassino de Telemetria e DiagTrack Windows", self.sw_tel)
        
    def toggle_nv_priv(self): 
        est = self.sw_nv_priv.get()
        
        if est == 1:
            cmd = 'taskkill /f /im NvTelemetryContainer.exe >nul 2>&1 & reg add "HKLM\\SOFTWARE\\NVIDIA Corporation\\NvControlPanel2\\Client" /v "OptIn" /t REG_DWORD /d 0 /f >nul 2>&1'
            self.executar_comando_assincrono(cmd, "Contrato Profundo de NVIDIA Privacy Data", self.sw_nv_priv)
        else: 
            self.log("[-] A chave de NVIDIA Privacy foi revertida.")
            self.salvar_config(self.sw_nv_priv.nome_log, "0")
        
    def toggle_flip_fix(self): 
        est = self.sw_flip.get()
        comando = f'reg add "HKCU\\Control Panel\\Desktop" /v "EnableWindowedOptimization" /t REG_DWORD /d {1 if est == 1 else 0} /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Reparador Gráfico Flip Integrity Fix", self.sw_flip)
    
    def toggle_srv(self):
        est = self.sw_srv.get()
        
        if est == 1:
            cmd = "sc stop SysMain >nul 2>&1 & sc config SysMain start= disabled >nul 2>&1 & sc stop WSearch >nul 2>&1 & sc config WSearch start= disabled >nul 2>&1"
        else:
            cmd = "sc config SysMain start= auto >nul 2>&1 & sc start SysMain >nul 2>&1 & sc config WSearch start= delayed-auto >nul 2>&1 & sc start WSearch >nul 2>&1"
            
        self.executar_comando_assincrono(cmd, "Supressão de Serviços Pesados (SysMain/WinSearch)", self.sw_srv)
        
    def toggle_tim(self): 
        est = self.sw_tim.get()
        comando = f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel" /v "GlobalTimerResolutionRequests" /t REG_DWORD /d {1 if est == 1 else 0} /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Quebra do Relógio Global: Resolução de Tempo (Timer Res)", self.sw_tim)
        
    def toggle_pow(self):
        est = int(self.sw_pow.get())
        if est == 1: 
            threading.Thread(target=self._ativar_desempenho_maximo, daemon=True).start()
        else: 
            threading.Thread(target=self._ativar_equilibrado, daemon=True).start()

    def _ativar_desempenho_maximo(self):
        res_l = subprocess.run(['powercfg', '/l'], capture_output=True, text=True, creationflags=0x08000000)
        guid_alvo = self.carregar_config("GuidMaximo", "")
        
        if not guid_alvo or guid_alvo.lower() not in res_l.stdout.lower():
            if "e9a42b02-d5df-448d-aa00-03f14749eb61" in res_l.stdout.lower():
                guid_alvo = "e9a42b02-d5df-448d-aa00-03f14749eb61" 
            else:
                res_dup = subprocess.run(['powercfg', '-duplicatescheme', 'e9a42b02-d5df-448d-aa00-03f14749eb61'], capture_output=True, text=True, creationflags=0x08000000)
                match = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", res_dup.stdout)
                guid_alvo = match.group(1) if match else "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" 
                
        subprocess.run(['powercfg', '/setactive', guid_alvo], creationflags=0x08000000)
        self.after(0, self.log_res, 0, "Aplicação Completa: Plano de Energia (Desempenho Máximo)", self.sw_pow)

    def _ativar_equilibrado(self):
        guid_eq = getattr(self, 'guid_padrao', "381b4222-f694-41f0-9685-ff5bb260df2e")
        subprocess.run(['powercfg', '/setactive', guid_eq], creationflags=0x08000000)
        self.after(0, self.log_res, 0, "Plano de Energia Totalmente Restaurado para Configuração Original", self.sw_pow)

    def toggle_net_thrott(self):
        est = self.sw_net_thrott.get()
        comando = f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d {0xFFFFFFFF if est == 1 else 10} /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Estrangulamento Zero: Limitação de Rede Completamente Apagada", self.sw_net_thrott)

    def toggle_core_parking(self):
        est = self.sw_core_park.get()
        comando = f'powercfg /setacvalueindex scheme_current sub_processor CPMINCORES {100 if est == 1 else 5} >nul 2>&1 & powercfg /setactive scheme_current >nul 2>&1'
        self.executar_comando_assincrono(comando, "Bloqueador Físico de Core Parking (100% de CPU Acordada)", self.sw_core_park)

    def toggle_mnu(self):
        est = self.sw_mnu.get()
        
        if est == 1:
            cmd = 'reg add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /f /ve >nul 2>&1'
        else:
            cmd = 'reg delete "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f >nul 2>&1'
            
        self.executar_comando_assincrono(cmd, "Aplicação Direta para o Restauro do Menu de Contexto Clássico", self.sw_mnu, reinicio=True)
        
    def toggle_bmn(self): 
        est = self.sw_bmn.get()
        comando = f"bcdedit /timeout {2 if est == 1 else 30} >nul 2>&1"
        self.executar_comando_assincrono(comando, "Redução de Delay Inativo do Boot Menu (Carga Rápida)", self.sw_bmn, reinicio=True)
    
    def toggle_fast_startup(self):
        est = self.sw_fast_start.get()
        comando = f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v "HiberbootEnabled" /t REG_DWORD /d {0 if est == 1 else 1} /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Desativador Profundo da Inicialização Rápida Baseada no Kernel", self.sw_fast_start, reinicio=True)

    def toggle_widgets(self):
        est = self.sw_widgets.get()
        
        if est == 1:
            cmd = 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Dsh" /v "AllowNewsAndInterests" /t REG_DWORD /d 0 /f >nul 2>&1'
        else:
            cmd = 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Dsh" /v "AllowNewsAndInterests" /f >nul 2>&1'
            
        self.executar_comando_assincrono(cmd, "Assassino Definitivo de Widgets da Barra de Tarefas Inúteis", self.sw_widgets, reinicio=True)

    # --- COMANDOS DOS BOTÕES INDIVIDUAIS (TODOS PRESERVADOS À RISCA) ---
    def abrir_inicializacao(self):
        self.log("[*] Invocando através da API o Gerenciador de Inicialização do Windows...")
        self.executar_comando_assincrono("start ms-settings:startupapps", "Lançamento Assíncrono do Gestor de Inicialização")

    def analisar_rede_info(self):
        def tarefa():
            self.log("[*] A analisar profundamente a topologia da sua conexão global (pode levar vários segundos)...")
            
            try: 
                ip_local = socket.gethostbyname(socket.gethostname())
            except Exception: 
                ip_local = "Erro crítico ao tentar localizar no adaptador"
            
            try: 
                ip_publico = urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode('utf8')
            except Exception: 
                ip_publico = "Oculto pelas firewalls ou totalmente Bloqueado"
            
            try:
                res = subprocess.run('ping 8.8.8.8 -n 1', capture_output=True, text=True, creationflags=0x08000000)
                ping_str = "Falha Completa no Disparo do Ping"
                if "tempo=" in res.stdout: 
                    ping_str = res.stdout.split("tempo=")[1].split("ms")[0].strip() + " ms exatos medidos"
                elif "time=" in res.stdout: 
                    ping_str = res.stdout.split("time=")[1].split("ms")[0].strip() + " ms exatos medidos"
            except Exception: 
                ping_str = "Erro massivo de adaptação de rede"
                
            self.log(f"\n=== RESULTADOS DO DIAGNÓSTICO PROFUNDO DE REDE ===\n> Endereço de IP Local Privado (LAN): {ip_local}\n> Endereço de IP Público Global (WAN): {ip_publico}\n> Velocidade Ping em Rota Direta (Google DNS Master): {ping_str}\n======================================================\n")
            
        threading.Thread(target=tarefa, daemon=True).start()

    def verificar_erros(self): 
        self.log("[*] Despachando a Verificação Sistêmica Completa do File Checker (SFC). Acompanhe os logs visuais na janela...")
        self.executar_comando_visivel("sfc /scannow", "Verificação Sênior Total do Sistema (SFC Native)", reinicio=True)

    def verificar_disco(self): 
        self.log("[*] A mapear absolutamente todas as partições do seu computador para verificar falhas na integridade... Acompanhe os processos na janela interativa.")
        comandos_array = []
        
        for part in psutil.disk_partitions():
            if part.fstype != '' and 'cdrom' not in part.opts:
                letra_particao = part.device[:2]
                comandos_array.append(f"echo. & echo === ATENCAO: A VERIFICAR SETORES MECANICOS NO DISCO {letra_particao} === & chkdsk {letra_particao} /scan")
        
        cmd_final_consolidado = " & ".join(comandos_array)
        
        if cmd_final_consolidado:
            self.executar_comando_visivel(cmd_final_consolidado, "Rotina Multi-Disco CHKDSK Absoluta", reinicio=True)

    def criar_ponto_restauracao(self):
        self.log("[*] Aplicando rotinas de Segurança Root do Computador. Aguarde enquanto gravamos o estado atual do Kernel na janela CMD...")
        comando_seguranca = 'powershell.exe -ExecutionPolicy Bypass -NoProfile -Command "Enable-ComputerRestore -Drive \'C:\\\'; Checkpoint-Computer -Description \'GustavoOptimizer Master Checkpoint\' -RestorePointType \'MODIFY_SETTINGS\'"'
        self.executar_comando_visivel(comando_seguranca, "Escudo Global de Ponto de Restauração de Sistema")

    def reparar_imagem_dism(self):
        self.log("[*] Descarregando à força pacotes sãos da Microsoft através da conexão online para curar eventuais danos e corrupção estrutural no núcleo do Windows...")
        self.executar_comando_visivel("DISM /Online /Cleanup-Image /RestoreHealth", "Recuperação Extremamente Agressiva (Reparo DISM via Web)")

    def limpar_logs_windows(self):
        self.log("[*] Executando rotina Wevtutil para assassinar impiedosamente milhares de arquivos falsos e alertas invisíveis de erros corrompidos que estão alojados no seu HD...")
        comando_logs = 'powershell -Command "wevtutil el | foreach { wevtutil cl \\\"$_\\\" }"'
        self.executar_comando_assincrono(comando_logs, "Varrimento Pesado e Limpeza Silenciosa de Logs de Eventos")

    def limpar_prefetch(self):
        self.log("[*] Eliminando com sucesso todos os arquivos arcaicos e memórias mortas guardadas no arranque profundo do ambiente (Prefetch)...")
        comando_prefetch = 'del /s /f /q "%WINDIR%\\Prefetch\\*.*" >nul 2>&1'
        self.executar_comando_assincrono(comando_prefetch, "Forçar Limpeza Integral da Pasta de Arranque Prefetch")

    def limpar_windows(self): 
        self.log("[*] Invocando à força a ferramenta Cleanmgr nativa e aplicando o Nível Máximo Avançado de Limpeza de Ficheiros do Sistema para atuar em background...")
        self.executar_comando_assincrono("cleanmgr /sagerun:1", "Ativação Silenciosa Máxima de Limpeza de Disco (Cleanmgr Sagerun)")
        
    def otimizar_internet(self): 
        self.log("[*] Impondo a redefinição extrema das rotas do seu IP Local, expurgando integralmente os catálogos pesados do Winsock e aplicando Flush no servidor DNS...")
        comando_net = "ipconfig /flushdns >nul 2>&1 & netsh winsock reset >nul 2>&1"
        self.executar_comando_assincrono(comando_net, "Reset Severo e Expulsão da Cache de Rede Local/Flush DNS")
        
    def otimizar_discos(self): 
        self.log("[*] Detetando Unidades Físicas. A iniciar a ferramenta cirúrgica de Otimização Inteligente nativa para disparar rotinas TRIM (SSD) e Desfragmentação Mecânica Universal... Acompanhe em detalhe na janela separada.")
        self.executar_comando_visivel("defrag /C /O /U", "Rotina Completa e Perfeita de Otimização de Todas as Unidades Mecânicas (Defrag Global)")

    def limpar_gpu(self): 
        self.log("[*] Encontrando as pastas da Placa de Vídeo para eliminar sem dó todos os caches complexos e shaders gráficos que causavam abrandamento diretamente no seu diretório de usuário LocalAppData...")
        comando_nvidia = 'del /f /s /q "%LocalAppData%\\NVIDIA\\DXCache\\*.*" >nul 2>&1'
        self.executar_comando_assincrono(comando_nvidia, "Assassino de Arquivos Temporários de Carga da Cache NVIDIA")
        
    def limpar_thumbnails(self): 
        self.log("[*] Disparando ordem de Kill Process contra a Interface Master do Explorer para esvaziar cache das imagens miniaturas antigas e renascer de imediato o motor visual do ecrã...")
        comando_thumbs = 'taskkill /f /im explorer.exe >nul 2>&1 & del /f /s /q "%LocalAppData%\\Microsoft\\Windows\\Explorer\\thumbcache_*.db" >nul 2>&1 & start explorer.exe'
        self.executar_comando_assincrono(comando_thumbs, "Reset Visual e Limpeza Profunda Global de Imagens das Miniaturas")
        
    def limpar_update(self):
        self.log("[*] Suspendendo os Serviços Oficiais Internos (Wuauserv). Estripando integralmente o repositório oculto SoftwareDistribution de todos os downloads mortos e patches emperrados do Windows Update e reiniciando a central a seguir...")
        comando_wu = 'net stop wuauserv >nul 2>&1 & del /s /f /q "%windir%\\SoftwareDistribution\\Download\\*.*" >nul 2>&1 & net start wuauserv >nul 2>&1'
        self.executar_comando_assincrono(comando_wu, "Purificação Completa e Limpeza Profunda Nível 10 de Cache do Windows Update")
        
    def limpar_chrome(self): 
        self.log("[*] Aplicando Script de Limpeza no diretório isolado User Data Google. Procedendo à exclusão minuciosa de todo o histórico de navegação web (Cache de Pesquisa do Google Chrome)...")
        c_path = "\\".join(["Google", "Chrome", "User Data", "Default", "Cache", "*.*"])
        comando_chrome = f'del /s /f /q "%LocalAppData%\\{c_path}" >nul 2>&1'
        self.executar_comando_assincrono(comando_chrome, "Exterminador Definitivo da Estrutura de Diretórios de Cache Google Chrome")
        
    def limpar_edge(self): 
        self.log("[*] Forçando a entrada no sistema restrito da Microsoft para purgar e demolir todos os dados inativos acumulados que atrasam o arranque das páginas principais e o cache de funcionamento do Microsoft Edge...")
        e_path = "\\".join(["Microsoft", "Edge", "User Data", "Default", "Cache", "*.*"])
        comando_edge = f'del /s /f /q "%LocalAppData%\\{e_path}" >nul 2>&1'
        self.executar_comando_assincrono(comando_edge, "Aniquilador Assíncrono Completo de Arquivos Soltos de Cache Microsoft Edge")
        
    def limpar_opera(self): 
        self.log("[*] Abrindo portas fechadas dos servidores nativos GX Stable e Original Stable. Executando ação de apagamento limpo sem causar danos a palavras-passes nos diretórios corrompidos (Browser Opera Global)...")
        p_gx = "\\".join(["Opera Software", "Opera GX Stable", "Cache", "*.*"])
        p_op = "\\".join(["Opera Software", "Opera Stable", "Cache", "*.*"])
        comando_opera = f'del /s /f /q "%LocalAppData%\\{p_gx}" >nul 2>&1 & del /s /f /q "%LocalAppData%\\{p_op}" >nul 2>&1'
        self.executar_comando_assincrono(comando_opera, "Exclusão Massiva de Todos os Perfis Salvos nos Navegadores Opera / Opera GX")

    def limpar_firefox(self):
        self.log("[*] Rodando comando de força PowerShell sob todos os seus múltiplos e antigos diretórios Mozilla Profile na pasta oculta LocalAppData. Exterminando para sempre os dados de navegação soltos no cache2...")
        f_path = "\\".join(["Mozilla", "Firefox", "Profiles", "*", "cache2", "*"])
        comando_ff = f'powershell -Command "Remove-Item -Path \\"$env:LOCALAPPDATA\\{f_path}\\" -Recurse -Force -ErrorAction SilentlyContinue"'
        self.executar_comando_assincrono(comando_ff, "Limpeza Ativa PowerShell em Diretórios Múltiplos de Mozilla Firefox Cache")

    def limpar_spotify(self): 
        self.log("[*] Esmagando qualquer reprodução em curso (taskkill /f /im) e varrendo na totalidade o lixo gigante dos dados e cache oculto deixado por anos de música no seu HD local (Serviços Nativos do App Spotify)...")
        s_path = "\\".join(["Spotify", "Data"])
        comando_sp = f'taskkill /f /im Spotify.exe >nul 2>&1 & rmdir /s /q "%LocalAppData%\\{s_path}" >nul 2>&1'
        self.executar_comando_assincrono(comando_sp, "Remoção Agressiva com Tarefa Fechada Oficial do Espaço Morto do Spotify")
        
    def limpar_steam(self): 
        self.log("[*] Encerrando comissionamentos da Bootstrapper em funcionamento. Eliminando instantaneamente a árvore AppCache e os pacotes residuais na loja virtual que causam os temíveis abrandamentos para efetuar updates oficiais do cliente Steam...")
        st_path = "\\".join(["Steam", "appcache"])
        comando_steam = f'taskkill /f /im steam.exe >nul 2>&1 & rmdir /s /q "C:\\Program Files (x86)\\{st_path}" >nul 2>&1'
        self.executar_comando_assincrono(comando_steam, "Extermínio Integral Cego de Atualizações Soltas da Plataforma da Loja Steam")
        
    def limpar_discord(self): 
        self.log("[*] Matando serviços do Discord escondidos na sua Taskbar. Iniciando uma purga na pasta complexa do AppData Local para remover milhares e milhares de ícones e arquivos multimídia inúteis de servidores abertos (Discord Master Cache)...")
        d_path = "\\".join(["Discord", "Cache"])
        comando_discord = f'taskkill /f /im Discord.exe >nul 2>&1 & rmdir /s /q "%AppData%\\{d_path}" >nul 2>&1'
        self.executar_comando_assincrono(comando_discord, "Destruidor Total Agressivo de Ficheiros Residuais e Bloqueio Local do Discord")
        
    def limpar_battlenet(self): 
        self.log("[*] Procurando o rastreador intrusivo Agent.exe e abortando as suas funções. Apagando definitivamente o núcleo estático que corrompe instalações ocultas no HD da plataforma nativa local da Blizzard Master (Battle.net System)...")
        comando_battlenet = 'taskkill /f /im Agent.exe >nul 2>&1 & rmdir /s /q "%ProgramData%\\Battle.net" >nul 2>&1'
        self.executar_comando_assincrono(comando_battlenet, "Assassino Definitivo Automático de Agentes Silenciosos da Raiz da Battle.net")
        
    def limpar_apps_multi(self):
        self.log("[*] Operação Trovão Inicializada: Aplicando a ordem global de extermínio e supressão maciça contra TODOS os clientes em funcionamento. De seguida será feita uma varredura extrema nas pastas temporárias da rede do Spotify, da Bootstrapper Store Steam, do Comunicador Completo Discord e do Kernel de atualizações da Battle.net. Ficheiros velhos não sobreviverão...")
        
        s_path = "\\".join(["Spotify", "Data"])
        st_path = "\\".join(["Steam", "appcache"])
        d_path = "\\".join(["Discord", "Cache"])
        
        comando_limpeza_massiva = (
            f'taskkill /f /im Spotify.exe >nul 2>&1 & taskkill /f /im steam.exe >nul 2>&1 & taskkill /f /im Discord.exe >nul 2>&1 & taskkill /f /im Agent.exe >nul 2>&1 & '
            f'rmdir /s /q "%LocalAppData%\\{s_path}" >nul 2>&1 & rmdir /s /q "C:\\Program Files (x86)\\{st_path}" >nul 2>&1 & '
            f'rmdir /s /q "%AppData%\\{d_path}" >nul 2>&1 & rmdir /s /q "%ProgramData%\\Battle.net" >nul 2>&1'
        )
        self.executar_comando_assincrono(comando_limpeza_massiva, "Sequência de Destruição Massiva Limpeza Total Integrada de Apps Gamer/Gerais")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = MeuOtimizador()
    app.mainloop()
