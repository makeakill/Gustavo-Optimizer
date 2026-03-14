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

# =====================================================================
# IMPORTAÇÃO DAS BIBLIOTECAS DE SYSTEM TRAY (BANDEJA DO SISTEMA)
# =====================================================================
try:
    from PIL import Image, ImageTk
    import pystray
    from pystray import MenuItem as pystray_item
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False

# --- FUNÇÃO PARA LER ARQUIVOS COMPILADOS (ÍCONES E ASSETS) ---
def resource_path(relative_path):
    """ Retorna o caminho absoluto, funcionando tanto em desenvolvimento quanto no .exe compilado via PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_si():
    """ Evita que o cursor do rato fique a carregar (bolinha) ao executar processos ocultos no Windows """
    if os.name == 'nt':
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        return si
    return None

# Configurações Visuais Nativas do CustomTkinter
ctk.set_appearance_mode("dark") 

# =====================================================================
# DICIONÁRIO DE PALETAS (PERFIS DE CORES PREMIUM)
# =====================================================================
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

# =====================================================================
# CLASSE MESTRE DO OTIMIZADOR (CORE SYSTEM)
# =====================================================================
class MeuOtimizador(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- SEPARAÇÃO DE IDENTIDADE PARA A BARRA DE TAREFAS DO WINDOWS ---
        if os.name == 'nt':
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("gustavo.optimizer.stable.v2.2.0")
            except Exception:
                pass

        # --- CONFIGURAÇÃO NATIVA DA JANELA ---
        self.title("Gustavo Optimizer v2.2.0 - Stable Edition (Instabilidade Zero)")
        self.geometry("1150x720")
        self.minsize(900, 600)
        
        # Injeção Ctypes para forçar a barra de título nativa do Windows a ficar Escura
        if os.name == "nt":
            try:
                hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                if hwnd == 0: hwnd = self.winfo_id()
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(ctypes.c_int(2)), ctypes.sizeof(ctypes.c_int))
            except Exception:
                pass
        
        self.bind("<Unmap>", self.verificar_minimizacao)
        self.bind("<Configure>", self.ajustar_responsividade) # Evento para escalar fontes dinamicamente
        
        icone_path = resource_path("icone.ico")
        if os.path.exists(icone_path):
            self.iconbitmap(icone_path)

        # Objetos de Fonte Dinâmica
        self.fonte_logo = ctk.CTkFont(family="Consolas", size=22, weight="bold")
        self.fonte_status = ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
        self.fonte_botoes = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        self.fonte_hw_tit = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        self.fonte_hw_val = ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        self.fonte_log = ctk.CTkFont(family="Consolas", size=10)

        # Configurações de Estado
        self.reg_lock = threading.Lock()
        self.estado_anterior = {}
        self.gpu_cache = "A calcular..."
        self.is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        
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
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 1. BARRA LATERAL RESPONSIVA (Sem Scrollbar)
        # ==========================================
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0, fg_color=self.bg_painel, border_width=1, border_color=self.borda)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) 
        
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(0, weight=0) # Logo & Status
        self.sidebar.grid_rowconfigure(1, weight=3) # Controlos (Botões) que se expandem
        self.sidebar.grid_rowconfigure(2, weight=1) # LogBox com garantia de espaço

        # 1.1 HEADER 
        self.frame_header = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_header.grid(row=0, column=0, sticky="ew")
        
        self.lbl_logo = ctk.CTkLabel(self.frame_header, text="[ GUSTAVO OPTIMIZER ]", font=self.fonte_logo, text_color=self.acento)
        self.lbl_logo.pack(padx=20, pady=(25, 10), anchor="w")

        admin_text = "MODO ADMIN: ATIVO" if self.is_admin else "AVISO: RODE COMO ADMIN"
        self.status_topo = ctk.CTkLabel(self.frame_header, text=admin_text, text_color="#2ecc71" if self.is_admin else self.acento, font=self.fonte_status)
        self.status_topo.pack(padx=20, pady=(0, 10), anchor="w")

        # 1.2 MÓDULO DE CONTROLOS ESTÁTICO (Expansível via Flexbox/pack expand=True)
        self.frame_controles = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_controles.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        self.sw_master_sys = ctk.CTkSwitch(self.frame_controles, text="MASTER SISTEMA (ON/OFF)", command=self.iniciar_thread_master, font=self.fonte_botoes, progress_color=self.acento, fg_color=self.borda)
        self.sw_master_sys.pack(padx=15, pady=2, anchor="w", expand=True)

        self.sw_master_clean = ctk.CTkSwitch(self.frame_controles, text="MASTER MANUTENÇÃO", command=self.thread_manutencao, font=self.fonte_botoes, progress_color=self.acento, fg_color=self.borda)
        self.sw_master_clean.pack(padx=15, pady=2, anchor="w", expand=True)

        self.btn_restore = ctk.CTkButton(self.frame_controles, text="PONTO RESTAURAÇÃO", command=self.criar_ponto_restauracao, fg_color="transparent", hover_color=self.acento, text_color=self.texto_branco, corner_radius=6, border_width=2, border_color=self.acento, font=self.fonte_botoes)
        self.btn_restore.pack(padx=15, pady=2, fill="x", expand=True)

        self.btn_exportar = ctk.CTkButton(self.frame_controles, text="EXPORTAR LOG", command=self.exportar_log, fg_color="transparent", hover_color=self.acento, text_color=self.texto_branco, corner_radius=6, border_width=2, border_color=self.acento, font=self.fonte_botoes)
        self.btn_exportar.pack(padx=15, pady=2, fill="x", expand=True)

        self.btn_manual = ctk.CTkButton(self.frame_controles, text="MANUAL DO PROGRAMA", command=self.abrir_manual, fg_color="transparent", hover_color=self.acento, text_color=self.texto_branco, corner_radius=6, border_width=2, border_color=self.acento, font=self.fonte_botoes)
        self.btn_manual.pack(padx=15, pady=2, fill="x", expand=True)

        self.lbl_tema_info = ctk.CTkLabel(self.frame_controles, text="🎨 Estilo Visual (Cores):", font=self.fonte_status, text_color=self.texto_cinza)
        self.lbl_tema_info.pack(padx=15, pady=(0, 0), anchor="w", expand=True)

        self.combo_temas = ctk.CTkOptionMenu(self.frame_controles, values=list(PALETAS.keys()), command=self.mudar_tema, fg_color=self.bg_painel, button_color=self.borda, button_hover_color=self.acento, dropdown_fg_color=self.bg_painel, text_color=self.texto_branco, font=self.fonte_botoes, corner_radius=8)
        self.combo_temas.set(tema_salvo)
        self.combo_temas.pack(padx=15, pady=2, fill="x", expand=True)

        # --- DASHBOARD VISUAL DE HARDWARE ---
        self.frame_hw = ctk.CTkFrame(self.frame_controles, fg_color=self.bg_main, border_color=self.borda, border_width=1, corner_radius=12)
        self.frame_hw.pack(padx=15, pady=4, fill="x", expand=True)
        self.frame_hw.grid_columnconfigure(0, weight=1)
        self.frame_hw.grid_columnconfigure(1, weight=1)
        
        self.lbl_cpu_tit = ctk.CTkLabel(self.frame_hw, text="⚙️ CPU", font=self.fonte_hw_tit, text_color=self.texto_cinza)
        self.lbl_cpu_tit.grid(row=0, column=0, padx=15, pady=(8,0), sticky="w")
        self.lbl_cpu_val = ctk.CTkLabel(self.frame_hw, text="0%", font=self.fonte_hw_val, text_color=self.texto_branco)
        self.lbl_cpu_val.grid(row=0, column=1, padx=15, pady=(8,0), sticky="e")
        self.prog_cpu = ctk.CTkProgressBar(self.frame_hw, height=5, progress_color=self.acento, fg_color=self.borda, corner_radius=4)
        self.prog_cpu.grid(row=1, column=0, columnspan=2, padx=15, pady=(3,5), sticky="ew")
        self.prog_cpu.set(0)
        
        self.lbl_ram_tit = ctk.CTkLabel(self.frame_hw, text="💾 RAM", font=self.fonte_hw_tit, text_color=self.texto_cinza)
        self.lbl_ram_tit.grid(row=2, column=0, padx=15, sticky="w")
        self.lbl_ram_val = ctk.CTkLabel(self.frame_hw, text="0%", font=self.fonte_hw_val, text_color=self.texto_branco)
        self.lbl_ram_val.grid(row=2, column=1, padx=15, sticky="e")
        self.prog_ram = ctk.CTkProgressBar(self.frame_hw, height=5, progress_color=self.acento, fg_color=self.borda, corner_radius=4)
        self.prog_ram.grid(row=3, column=0, columnspan=2, padx=15, pady=(3,5), sticky="ew")
        self.prog_ram.set(0)
        
        self.lbl_gpu_tit = ctk.CTkLabel(self.frame_hw, text="🎮 GPU", font=self.fonte_hw_tit, text_color=self.texto_cinza)
        self.lbl_gpu_tit.grid(row=4, column=0, padx=15, sticky="w")
        self.lbl_gpu_val = ctk.CTkLabel(self.frame_hw, text="Calc...", font=self.fonte_hw_val, text_color=self.texto_branco)
        self.lbl_gpu_val.grid(row=4, column=1, padx=15, sticky="e")
        self.prog_gpu = ctk.CTkProgressBar(self.frame_hw, height=5, progress_color=self.acento, fg_color=self.borda, corner_radius=4)
        self.prog_gpu.grid(row=5, column=0, columnspan=2, padx=15, pady=(3,10), sticky="ew")
        self.prog_gpu.set(0)

        self.sw_sidebar_dark = ctk.CTkSwitch(self.frame_controles, text="MODO ESCURO SO", command=self.acao_dark_mode, font=self.fonte_status, progress_color=self.acento, fg_color=self.borda)
        self.sw_sidebar_dark.pack(padx=15, pady=2, anchor="w", expand=True)
        estado_dark = self.carregar_config("DarkModeSidebar", "0")
        if estado_dark == "1":
            self.sw_sidebar_dark.select()

        self.lbl_mica = ctk.CTkLabel(self.frame_controles, text="🪟 Efeito Transparência UI:", font=self.fonte_status, text_color=self.texto_cinza)
        self.lbl_mica.pack(padx=15, pady=(2, 0), anchor="w", expand=True)
        
        self.slider_mica = ctk.CTkSlider(self.frame_controles, from_=0.3, to=1.0, command=self.mudar_transparencia, progress_color=self.acento, button_color=self.acento, button_hover_color=self.texto_branco)
        self.slider_mica.pack(padx=15, pady=(0, 5), fill="x", expand=True)
        self.slider_mica.set(1.0) 

        # 1.3 CAIXA DE LOG (Sempre preservada)
        self.caixa_log = ctk.CTkTextbox(self.sidebar, corner_radius=10, font=self.fonte_log, fg_color=self.bg_main, text_color=self.texto_cinza, border_width=1, border_color=self.borda)
        self.caixa_log.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="nsew")
        
        self.after(500, lambda: self.log("Sistema de Memória Persistente ativado."))
        self.after(550, lambda: self.log("Iniciando Auditoria em Tempo Real no Registo do Kernel..."))

        # ==========================================
        # 2. ÁREA DE CONTEÚDO (SISTEMA DE ABAS)
        # ==========================================
        self.tabview = ctk.CTkTabview(self, fg_color=self.bg_main, segmented_button_fg_color=self.bg_painel, segmented_button_selected_color=self.acento, segmented_button_unselected_color=self.bg_painel, text_color=self.texto_branco, corner_radius=12)
        self.tabview.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

        self.tab_desempenho = self.tabview.add("⚡ Desempenho")
        self.tab_rede = self.tabview.add("🌐 Rede & Internet")
        self.tab_privacidade = self.tabview.add("🛡️ Privacidade & OS")
        self.tab_limpeza = self.tabview.add("🧹 Limpeza")
        self.tab_root = self.tabview.add("⚙️ Root (Reinício)")

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
        
        threading.Thread(target=self.thread_atualizar_gpu, daemon=True).start()
        self.atualizar_hardware_ui()
        self.after(500, self.iniciar_verificacao_energia)

    # =====================================================================
    # BLOCO 1: RESPONSIVIDADE E TRAY
    # =====================================================================
    def ajustar_responsividade(self, event):
        """ Dimensiona dinamicamente a tipografia da barra lateral de acordo com a altura da janela """
        if event.widget == self:
            h = event.height
            if h < 650:
                self.fonte_logo.configure(size=18)
                self.fonte_botoes.configure(size=10)
                self.fonte_status.configure(size=10)
                self.fonte_hw_tit.configure(size=10)
                self.fonte_hw_val.configure(size=10)
                self.fonte_log.configure(size=9)
            elif h > 850:
                self.fonte_logo.configure(size=24)
                self.fonte_botoes.configure(size=13)
                self.fonte_status.configure(size=12)
                self.fonte_hw_tit.configure(size=13)
                self.fonte_hw_val.configure(size=13)
                self.fonte_log.configure(size=11)
            else:
                self.fonte_logo.configure(size=22)
                self.fonte_botoes.configure(size=12)
                self.fonte_status.configure(size=11)
                self.fonte_hw_tit.configure(size=12)
                self.fonte_hw_val.configure(size=12)
                self.fonte_log.configure(size=10)

    def verificar_minimizacao(self, event):
        if str(event.widget) == "." and self.state() == 'iconic':
            if HAS_TRAY: self.minimizar_para_tray()

    def minimizar_para_tray(self):
        if HAS_TRAY:
            self.withdraw()
            icone_path = resource_path("icone.ico")
            try: image = Image.open(icone_path)
            except Exception: image = Image.new('RGB', (64, 64), color=(0, 229, 255))
            menu = pystray.Menu(
                pystray_item('Restaurar Interface', self.restaurar_do_tray, default=True),
                pystray_item('Encerrar Optimizer', self.fechar_pelo_tray)
            )
            self.tray_icon = pystray.Icon("GustavoOptimizer", image, "Gustavo Optimizer Elite", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            self.log("[*] Oculto na Bandeja do Sistema.")

    def restaurar_do_tray(self, icon, item):
        icon.stop()
        self.after(0, self.restaurar_janela)

    def restaurar_janela(self):
        self.deiconify()
        self.state('normal')
        self.log("[+] Interface restaurada.")
        if os.name == "nt":
            try:
                hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                if hwnd == 0: hwnd = self.winfo_id()
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(ctypes.c_int(2)), ctypes.sizeof(ctypes.c_int))
            except Exception: pass

    def fechar_pelo_tray(self, icon, item):
        icon.stop()
        self.after(0, self.destroy)

    def mudar_transparencia(self, valor):
        self.attributes("-alpha", valor)

    def acao_dark_mode(self):
        if self.sw_sidebar_dark.get() == 1:
            lote = [
                ('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "AppsUseLightTheme" /t REG_DWORD /d 0 /f >nul 2>&1 || exit 0', "Impor Cor Escura nos Programas"),
                ('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "SystemUsesLightTheme" /t REG_DWORD /d 0 /f >nul 2>&1 || exit 0', "Impor Cor Escura no Sistema")
            ]
        else:
            lote = [
                ('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "AppsUseLightTheme" /t REG_DWORD /d 1 /f >nul 2>&1 || exit 0', "Reverter Aplicativos para Claro"),
                ('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "SystemUsesLightTheme" /t REG_DWORD /d 1 /f >nul 2>&1 || exit 0', "Reverter Sistema para Claro")
            ]
        self.executar_lote_com_verificacao(lote, "Mecanismo Forçado de Modo Escuro no Windows", self.sw_sidebar_dark)

    def exportar_log(self):
        caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".txt", title="Salvar Log Definitivo de Otimização", initialfile="Log_Otimizacao_Sistema.txt")
        if caminho_arquivo:
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo: 
                arquivo.write(self.caixa_log.get("1.0", "end-1c"))
            self.log(f"[+] Relatório Mestre gravado no disco com sucesso em: {caminho_arquivo}")

    def abrir_manual(self):
        janela_manual = ctk.CTkToplevel(self)
        janela_manual.title("Manual de Engenharia do Sistema - Gustavo Optimizer v2.2.0 Stable")
        janela_manual.geometry("850x650")
        janela_manual.transient(self)
        janela_manual.grab_set() 
        janela_manual.configure(fg_color=self.bg_main)
        
        lbl_titulo = ctk.CTkLabel(janela_manual, text="[ MANUAL DE INSTRUÇÕES E DOCUMENTAÇÃO V2.2.0 ]", font=("Segoe UI", 18, "bold"), text_color=self.acento)
        lbl_titulo.pack(pady=(20, 10))
        
        caixa_texto = ctk.CTkTextbox(janela_manual, font=("Consolas", 13), fg_color=self.bg_painel, text_color=self.texto_branco, border_width=1, border_color=self.borda, corner_radius=12)
        caixa_texto.pack(expand=True, fill="both", padx=20, pady=10)

        manual_completo = (
            "================================================================================\n"
            "                 GUSTAVO OPTIMIZER v2.2.0 - STABLE EDITION                      \n"
            "================================================================================\n\n"
            "Bem-vindo à ferramenta definitiva de engenharia de software para Windows.\n"
            "Este manual contém a documentação técnica de todas as funções do sistema.\n\n"
            "================================================================================\n"
            "1. ARQUITETURA ANTI-FALHAS E VERIFICAÇÃO REAL (V2.2.0)\n"
            "================================================================================\n"
            "- A versão Stable removeu todas as chaves instáveis que causavam tela preta\n"
            "  em redes sociais (Instagram) e crashes (TDR) no driver da NVIDIA.\n"
            "- Cada chave de Registo e manipulação de rede passa por um Motor Interativo Python,\n"
            "  que reporta com precisão milimétrica cada CÓDIGO DE RETORNO de sistema.\n\n"
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
            "- Core Parking: Obriga todos os núcleos lógicos do processador a manterem-se acordados.\n"
            "- Desativar Hibernação: Remove o arquivo hiberfil.sys, libertando muito espaço em disco.\n\n"
        )
        
        caixa_texto.insert("0.0", manual_completo)
        caixa_texto.configure(state="disabled") 

        def salvar_manual():
            caminho = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="Manual_Stable_Sistema.txt", title="Salvar Manual Físico de Arquitetura")
            if caminho:
                with open(caminho, "w", encoding="utf-8") as f: 
                    f.write(manual_completo)
                self.log(f"[+] Documentação Textual exportada no seu disco para: {caminho}")
                janela_manual.destroy() 
                
        btn_salvar = ctk.CTkButton(janela_manual, text="EXPORTAR TEXTO PARA .TXT", command=salvar_manual, fg_color=self.bg_painel, hover_color=self.acento, text_color=self.texto_branco, border_width=1, border_color=self.acento, font=("Segoe UI", 12, "bold"), corner_radius=8)
        btn_salvar.pack(pady=(10, 20))

    # =====================================================================
    # BLOCO 2: TEMA E CORES DINÂMICAS (RESTAURADO)
    # =====================================================================
    def aplicar_variaveis_tema(self, nome_tema):
        cores = PALETAS.get(nome_tema, PALETAS["Pure Power (Ciano)"])
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
        
        self.btn_exportar.configure(hover_color=self.acento, border_color=self.acento)
        self.btn_restore.configure(hover_color=self.acento, border_color=self.acento)
        self.btn_manual.configure(hover_color=self.acento, border_color=self.acento)
        self.combo_temas.configure(fg_color=self.bg_painel, button_color=self.borda, button_hover_color=self.acento, dropdown_fg_color=self.bg_painel)
        self.slider_mica.configure(progress_color=self.acento, button_color=self.acento)
        
        self.caixa_log.configure(fg_color=self.bg_main, text_color=self.texto_cinza, border_color=self.borda)
        self.tabview.configure(fg_color=self.bg_main, segmented_button_fg_color=self.bg_painel, segmented_button_selected_color=self.acento, segmented_button_unselected_color=self.bg_painel, text_color=self.texto_branco)
        
        for widget in self.cards_interface: 
            widget.destroy()
        self.cards_interface.clear()
        self.lista_switches.clear()
        self.montar_interface_total()
        self.log(f"[*] Perfil de cores alterado para: {novo_tema}")

    def atualizar_cores_perfis(self):
        if not hasattr(self, 'btn_gamer') or not hasattr(self, 'btn_trabalho'): 
            return
            
        cor_fundo_padrao = "transparent"
        cor_texto_padrao = self.texto_branco
        cor_borda_padrao = self.acento

        if self.perfil_ativo == "Gamer":
            self.btn_gamer.configure(fg_color=self.acento, text_color=self.bg_main, border_color=self.acento, text="DESATIVAR GAMER")
            self.btn_trabalho.configure(fg_color=cor_fundo_padrao, text_color=cor_texto_padrao, border_color=cor_borda_padrao, text="ATIVAR MODO TRABALHO")
        elif self.perfil_ativo == "Trabalho":
            self.btn_trabalho.configure(fg_color=self.borda, text_color=self.texto_branco, border_color=self.borda, text="DESATIVAR TRABALHO")
            self.btn_gamer.configure(fg_color=cor_fundo_padrao, text_color=cor_texto_padrao, border_color=cor_borda_padrao, text="ATIVAR MODO GAMER")
        else:
            self.btn_gamer.configure(fg_color=cor_fundo_padrao, text_color=cor_texto_padrao, border_color=cor_borda_padrao, text="ATIVAR MODO GAMER")
            self.btn_trabalho.configure(fg_color=cor_fundo_padrao, text_color=cor_texto_padrao, border_color=cor_borda_padrao, text="ATIVAR MODO TRABALHO")

    # =====================================================================
    # BLOCO 3: MONITORAMENTO DE HARDWARE E LOGS
    # =====================================================================
    def atualizar_hardware_ui(self):
        uso_cpu = psutil.cpu_percent(interval=None)
        uso_ram = psutil.virtual_memory().percent
        self.lbl_cpu_val.configure(text=f"{uso_cpu}%")
        self.prog_cpu.set(uso_cpu / 100.0)
        self.lbl_ram_val.configure(text=f"{uso_ram}%")
        self.prog_ram.set(uso_ram / 100.0)
        gpu_txt = self.gpu_cache.replace("%", "").strip()
        self.lbl_gpu_val.configure(text=f"{self.gpu_cache}")
        try: self.prog_gpu.set(float(gpu_txt) / 100.0)
        except Exception: self.prog_gpu.set(0)
        self.after(1500, self.atualizar_hardware_ui)

    def thread_atualizar_gpu(self):
        while True:
            try:
                res = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, creationflags=0x08000000, startupinfo=get_si())
                if res.returncode == 0: self.gpu_cache = f"{res.stdout.strip()}%"
                else: self.gpu_cache = "N/A (AMD)"
            except Exception: self.gpu_cache = "N/A"
            time.sleep(10)

    def log(self, mensagem, tipo="info"):
        prefixo = "[+] " if tipo == "info" else "[-] "
        def update_ui():
            self.caixa_log.insert("end", f"{prefixo}{mensagem}\n")
            self.caixa_log.see("end")
            self.update_idletasks()
        self.after(0, update_ui)

    def log_res(self, res, nome, sw_obj=None, reinicio=False, stdout="", stderr=""):
        def update_ui():
            aviso = " [REQUER REINÍCIO]" if reinicio else ""
            if res == 0: 
                self.caixa_log.insert("end", f"[+] SUCESSO | {nome}: Validação executada com perfeição.{aviso}\n")
                if sw_obj is not None and hasattr(sw_obj, 'nome_log'): 
                    self.salvar_config(sw_obj.nome_log, str(sw_obj.get()))
            else: 
                erro_txt = stderr.strip() if stderr else "Falha de Permissão ou Acesso Negado pelo OS."
                self.caixa_log.insert("end", f"[-] ERRO | {nome}: {erro_txt} (Cód {res}). A reverter...\n")
                if sw_obj is not None:
                    if sw_obj.get() == 0:
                        self.salvar_config(sw_obj.nome_log, "0")
                        sw_obj.deselect()
                    else:
                        estado_memoria = self.carregar_config(sw_obj.nome_log, "0")
                        if estado_memoria == "1": sw_obj.select()
                        else: sw_obj.deselect()
            self.caixa_log.see("end")
            self.update_idletasks()
        self.after(0, update_ui)

    def log_res_simples(self, res, nome, sw_obj=None, reinicio=False):
        def update_ui():
            aviso = " [O SISTEMA REQUER REINÍCIO PARA APLICAR]" if reinicio else ""
            if res == 0: self.caixa_log.insert("end", f"[+] {nome}: Aplicado com sucesso no sistema.{aviso}\n")
            else: self.caixa_log.insert("end", f"[-] AVISO: {nome} retornou falha de Kernel (Código {res}).\n")
            self.caixa_log.see("end")
            self.update_idletasks()
        self.after(0, update_ui)

    # =====================================================================
    # BLOCO 4: CORE DE REGISTO E ESTADO
    # =====================================================================
    def salvar_config(self, nome, valor):
        with self.reg_lock:
            try:
                chave = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\GustavoOptimizer")
                winreg.SetValueEx(chave, nome, 0, winreg.REG_SZ, str(valor))
                winreg.CloseKey(chave)
            except Exception as e: self.log(f"Erro Fatal ao escrever memória: {str(e)}", "erro")

    def carregar_config(self, nome, padrao):
        try:
            chave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\GustavoOptimizer")
            valor, _ = winreg.QueryValueEx(chave, nome)
            winreg.CloseKey(chave)
            return valor
        except OSError: return padrao

    def carregar_snapshot_memoria(self):
        self.estado_anterior = {}
        snap_str = self.carregar_config("SnapshotPerfil", "")
        if snap_str:
            try:
                for par in snap_str.split(','):
                    if ':' in par:
                        k, v = par.split(':')
                        self.estado_anterior[k] = int(v)
            except Exception: pass

    def guardar_snapshot_atual(self):
        self.estado_anterior = {
            'pow': self.sw_pow.get(), 'gaming': self.sw_gaming.get(),
            'net_thrott': self.sw_net_thrott.get(), 'core_park': self.sw_core_park.get(),
            'tim': self.sw_tim.get(), 'hibernacao': self.sw_hibernacao.get(),
            'thrott': self.sw_thrott.get(), 'srv': self.sw_srv.get(), 
            'visual_perf': self.sw_visual_perf.get()
        }
        snap_str = ",".join([f"{k}:{v}" for k, v in self.estado_anterior.items()])
        self.salvar_config("SnapshotPerfil", snap_str)

    def auditar_estado_real(self, nome_log):
        mapa_auditoria = {
            "VS Telemetry": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\VisualStudio\Telemetry", "RefuseTelemetry", 1),
            "DiagTrack": (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\DiagTrack", "Start", 4),
            "NVIDIA Privacy": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\NVIDIA Corporation\NvControlPanel2\Client", "OptIn", 0),
            "GeoLocation": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors", "DisableLocation", 1),
            "Desempenho Visual": (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 2),
            "Power Throttling": (winreg.HKEY_LOCAL_MACHINE, r"System\CurrentControlSet\Control\Power\PowerThrottling", "PowerThrottlingOff", 1),
            "Timer Res": (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "GlobalTimerResolutionRequests", 1),
            "Servicos Windows": (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\SysMain", "Start", 4),
            "Network Throttling": (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "NetworkThrottlingIndex", 0xFFFFFFFF),
            "Hibernacao": (winreg.HKEY_LOCAL_MACHINE, r"System\CurrentControlSet\Control\Power", "HibernateEnabled", 0), 
        }

        if nome_log in mapa_auditoria:
            hkey, path, value_name, expected_value = mapa_auditoria[nome_log]
            try:
                chave = winreg.OpenKey(hkey, path)
                valor, _ = winreg.QueryValueEx(chave, value_name)
                winreg.CloseKey(chave)
                return "1" if str(valor) == str(expected_value) else "0"
            except OSError: return "0" 
        return self.carregar_config(nome_log, "0")

    # =====================================================================
    # BLOCO 5: MOTORES DE EXECUÇÃO E INTELIGÊNCIA DE FALSOS POSITIVOS
    # =====================================================================
    def executar_comando(self, comando):
        try:
            resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, creationflags=0x08000000, startupinfo=get_si())
            return resultado.returncode
        except Exception as e: 
            self.log(f"Erro na execução da subrotina: {str(e)}", "erro")
            return 1

    def executar_comando_visivel(self, comando, nome_log, reinicio=False):
        def tarefa():
            try:
                processo = subprocess.Popen(f'cmd /c "{comando}"', creationflags=subprocess.CREATE_NEW_CONSOLE)
                processo.wait() 
                self.log_res_simples(processo.returncode, nome_log, None, reinicio)
            except Exception as e: self.log(f"Erro na janela CMD {nome_log}: {str(e)}", "erro")
        threading.Thread(target=tarefa, daemon=True).start()

    def executar_comando_assincrono(self, comando, nome_log, sw_obj=None, reinicio=False):
        def tarefa():
            try:
                processo = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=0x08000000, startupinfo=get_si())
                stdout, stderr = processo.communicate()
                out_err = str(stdout + stderr).lower()
                is_false_positive = False
                
                # Inteligência Heurística para limpeza assíncrona
                if processo.returncode != 0:
                    if "taskkill" in comando.lower() and (processo.returncode == 128 or "não foi encontrado" in out_err or "not found" in out_err):
                        is_false_positive = True
                    elif "del " in comando.lower() and ("não foi possível encontrar" in out_err or "could not find" in out_err):
                        is_false_positive = True
                
                res_code = 0 if is_false_positive else processo.returncode
                self.log_res(res_code, nome_log, sw_obj, reinicio, stdout, stderr)
            except Exception as e: 
                self.log(f"[-] Erro Crítico Assíncrono ao processar {nome_log}: {str(e)}", "erro")
                if sw_obj: self.after(0, sw_obj.deselect)
        threading.Thread(target=tarefa, daemon=True).start()

    def executar_lote_com_verificacao(self, lista_comandos, nome_log, sw_obj=None, reinicio=False):
        def tarefa():
            sucesso_global = True
            erros_encontrados = []
            self.log(f"[*] Iniciando Protocolo de Lote: {nome_log}")
            
            for cmd, descricao in lista_comandos:
                self.log(f"   [>] Aplicando fase: {descricao}...")
                try:
                    processo = subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=0x08000000, startupinfo=get_si())
                    out_err = str(processo.stdout + processo.stderr).lower()
                    
                    if processo.returncode == 0: 
                        self.log(f"   [+] OK: Executado com perfeição.")
                    else:
                        is_false_positive = False
                        
                        if "taskkill" in cmd.lower() and (processo.returncode == 128 or "não foi encontrado" in out_err or "not found" in out_err):
                            is_false_positive = True
                        elif "reg delete" in cmd.lower() and ("não foi possível encontrar" in out_err or "unable to find" in out_err):
                            is_false_positive = True
                        elif "rmdir" in cmd.lower() and ("o sistema não pode encontrar" in out_err or "cannot find" in out_err):
                            is_false_positive = True
                        elif "del" in cmd.lower() and ("não foi possível encontrar" in out_err or "could not find" in out_err):
                            is_false_positive = True
                        elif "sc stop" in cmd.lower() and ("não foi iniciado" in out_err or "not started" in out_err):
                            is_false_positive = True
                            
                        if is_false_positive:
                            self.log(f"   [+] OK: O alvo já se encontra no estado desejado (Ignorado).")
                        else:
                            msg_curta = out_err.strip().replace('\n', ' ')[:65]
                            self.log(f"   [-] Falha na fase (Cód {processo.returncode}): {msg_curta}...", "erro")
                            sucesso_global = False
                            erros_encontrados.append(descricao)
                except Exception as e:
                    self.log(f"   [-] Erro Fatal no Python: {str(e)}", "erro")
                    sucesso_global = False
                    erros_encontrados.append(descricao)
                time.sleep(0.1)
            
            if sucesso_global: 
                self.log_res(0, nome_log, sw_obj, reinicio)
            else:
                msg_erro = "Falha sequencial: " + " | ".join(erros_encontrados)
                self.log_res(1, nome_log, sw_obj, reinicio, stderr=msg_erro)
        threading.Thread(target=tarefa, daemon=True).start()

    # =====================================================================
    # BLOCO 6: LÓGICA DE CÉREBRO/MASTER E PERFIS INTELIGENTES
    # =====================================================================
    def iniciar_thread_master(self):
        estado_alvo = int(self.sw_master_sys.get())
        threading.Thread(target=self.toggle_master_system, args=(estado_alvo,), daemon=True).start()

    def toggle_master_system(self, estado_alvo):
        acao_nome = "ATIVAR" if estado_alvo == 1 else "DESATIVAR"
        self.log(f"[*] Iniciando rotina para {acao_nome} as funções do Sistema Master sequencialmente...")
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
                except Exception: pass
            self.after(0, acao_master)
            time.sleep(1.5) 
        self.log(f"[+] MODO MASTER {acao_nome} COM SUCESSO! Operação de Sincronização global concluída.")

    def forcar_ativo(self, sw):
        def acao():
            try:
                if int(sw.get()) == 0: 
                    sw.select()
                    if hasattr(sw, 'comando_real'): sw.comando_real()
            except Exception: pass
        self.after(0, acao)

    def forcar_desligado(self, sw):
        def acao():
            try:
                if int(sw.get()) == 1: 
                    sw.deselect()
                    if hasattr(sw, 'comando_real'): sw.comando_real()
            except Exception: pass
        self.after(0, acao)

    def aplicar_modo_normal(self):
        self.log("[*] DESATIVANDO PERFIS: Restaurando sistema ao Modo Normal (Padrão de Fábrica)...")
        switches_para_desligar = [
            self.sw_pow, self.sw_gaming, self.sw_tim, self.sw_net_thrott,
            self.sw_core_park, self.sw_thrott, self.sw_srv, self.sw_visual_perf
        ]
        for sw in switches_para_desligar:
            self.forcar_desligado(sw)
            time.sleep(1.0)
            
        self.estado_anterior.clear()
        self.salvar_config("SnapshotPerfil", "") 
        self.log("[+] MODO NORMAL ATIVADO! Todas as injeções extremas foram desativadas e o seu PC regressou ao estado original.")

    def acionar_perfil_gamer(self):
        if self.perfil_ativo == "Gamer":
            self.perfil_ativo = "Nenhum"
            self.salvar_config("PerfilAtivo", self.perfil_ativo)
            self.atualizar_cores_perfis()
            threading.Thread(target=self.aplicar_modo_normal, daemon=True).start()
        else:
            if self.perfil_ativo == "Nenhum": self.guardar_snapshot_atual()
            self.perfil_ativo = "Gamer"
            self.salvar_config("PerfilAtivo", self.perfil_ativo)
            self.atualizar_cores_perfis()
            threading.Thread(target=self.aplicar_gamer_avancado, daemon=True).start()

    def acionar_perfil_trabalho(self):
        if self.perfil_ativo == "Trabalho":
            self.perfil_ativo = "Nenhum"
            self.salvar_config("PerfilAtivo", self.perfil_ativo)
            self.atualizar_cores_perfis()
            threading.Thread(target=self.aplicar_modo_normal, daemon=True).start()
        else:
            if self.perfil_ativo == "Nenhum": self.guardar_snapshot_atual()
            self.perfil_ativo = "Trabalho"
            self.salvar_config("PerfilAtivo", self.perfil_ativo)
            self.atualizar_cores_perfis()
            threading.Thread(target=self.aplicar_trabalho_avancado, daemon=True).start()

    def aplicar_gamer_avancado(self):
        self.log("[*] APLICANDO MODO GAMER ELITE: Analisando hardware e ativando rotinas sequencialmente...")
        total_ram_gb = psutil.virtual_memory().total / (1024**3)
        switches_gamer_dinamicos = [
            self.sw_pow, self.sw_gaming, self.sw_tim
        ]
        
        self.log("[*] Verificando Proteção Térmica...")
        for sw in [self.sw_core_park, self.sw_thrott, self.sw_visual_perf]:
            self.forcar_desligado(sw)
            time.sleep(1.0)
            
        if total_ram_gb <= 16.5:
            self.log(f"[*] PC Modesto Detectado ({total_ram_gb:.1f}GB RAM): A desligar SysMain para libertar memória vital.")
            switches_gamer_dinamicos.append(self.sw_srv)
        else:
            self.log(f"[*] PC High-End Detectado ({total_ram_gb:.1f}GB RAM): A manter SysMain na Engine para não destruir a navegação web.")
            self.forcar_desligado(self.sw_srv)
            time.sleep(1.0)

        self.log("[*] Iniciando injeções de performance extrema de Jogo. Aguarde a conclusão de todas as etapas...")
        for sw in switches_gamer_dinamicos: 
            self.forcar_ativo(sw)
            time.sleep(1.5)
            
        self.log("[+] MODO GAMER ATIVADO! Todas as funções foram aplicadas com sucesso (FPS Destravado).")

    def aplicar_trabalho_avancado(self):
        self.log("[*] APLICANDO MODO TRABALHO: Otimizando o sistema para produtividade multitarefa e rede fluida...")
        
        # Desliga funções extremas de jogos
        self.log("[*] Desativando Injeções Extremas de Jogos...")
        for sw in [self.sw_gaming, self.sw_tim, self.sw_core_park, self.sw_pow, self.sw_srv]:
            self.forcar_desligado(sw)
            time.sleep(1.0)
            
        # Liga funções úteis para trabalho
        self.log("[*] Aplicando protocolos de Internet Rápida e Estabilidade Visual...")
        for sw in [self.sw_net_thrott]:
            self.forcar_ativo(sw)
            time.sleep(1.0)
            
        self.log("[+] MODO TRABALHO ATIVADO! O seu PC está configurado para estabilidade absoluta e downloads velozes.")

    def iniciar_verificacao_energia(self):
        threading.Thread(target=self.checar_plano_energia, daemon=True).start()

    def checar_plano_energia(self):
        try:
            res_curr = subprocess.run(['powercfg', '/getactivescheme'], capture_output=True, text=True, creationflags=0x08000000, startupinfo=get_si())
            match_curr = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", res_curr.stdout)
            if match_curr:
                curr_guid = match_curr.group(1).lower()
                guid_salvo = self.carregar_config("GuidMaximo", "").lower()
                if curr_guid != guid_salvo and curr_guid != "e9a42b02-d5df-448d-aa00-03f14749eb61":
                    self.guid_padrao = curr_guid
                    self.salvar_config("GuidPadrao", self.guid_padrao)
        except Exception: pass

        guid_salvo = self.carregar_config("GuidMaximo", "")
        res_l = subprocess.run('powercfg /l', capture_output=True, text=True, shell=True, creationflags=0x08000000, startupinfo=get_si())
        
        if guid_salvo and guid_salvo.lower() in res_l.stdout.lower():
            self.guid_maximo = guid_salvo
            self.log("[*] Leitura Concluída: Arquitetura do Plano de Desempenho Máximo carregada perfeitamente a partir do Registo.")
            return

        if "e9a42b02-d5df-448d-aa00-03f14749eb61" in res_l.stdout.lower():
            self.guid_maximo = "e9a42b02-d5df-448d-aa00-03f14749eb61"
            self.salvar_config("GuidMaximo", self.guid_maximo)
            self.log("[*] Leitura Concluída: Plano de Desempenho Máximo de Fábrica encontrado e associado.")
            return
            
        res_dup = subprocess.run('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61', capture_output=True, text=True, shell=True, creationflags=0x08000000, startupinfo=get_si())
        match = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", res_dup.stdout)
        
        if match:
            self.guid_maximo = match.group(1)
            self.salvar_config("GuidMaximo", self.guid_maximo)
            self.log(f"[*] Injeção Crítica de Otimização: Plano de Desempenho Máximo criado no ID {self.guid_maximo}.")
        else: 
            self.log("[-] Erro de Execução ao criar Desempenho Máximo. Assumindo configurações locais padrão.", "erro")

    # =====================================================================
    # BLOCO 7: MANUTENÇÃO, DEBLOAT E LIMPEZA
    # =====================================================================
    def thread_manutencao(self):
        if self.sw_master_clean.get() == 1:
            if not self.is_admin:
                self.sw_master_clean.deselect()
                return
            threading.Thread(target=self.limpeza_sequencial, daemon=True).start()

    def limpeza_sequencial(self):
        tarefas = [
            ("Arquivos Temporários", "del /s /f /q %temp%\\*.* >nul 2>&1 || exit 0"), 
            ("Redefinição de Rede", "ipconfig /flushdns"),
            ("Redefinição de Catálogos", "netsh winsock reset")
        ]
        for nome_tarefa, comando in tarefas:
            if self.sw_master_clean.get() == 0: break
            self.log(f"[*] Etapa {nome_tarefa} em andamento...") 
            res = self.executar_comando(comando)
            time.sleep(1)
            self.log_res_simples(res, nome_tarefa)
            
        if self.sw_master_clean.get() == 1:
            self.executar_comando_visivel("sfc /scannow", "SFC Scan", reinicio=True)
            
        self.log("[+] MANUTENÇÃO MESTRA CONCLUÍDA COM SUCESSO.")
        self.sw_master_clean.deselect()

    def abrir_painel_debloat(self):
        janela_db = ctk.CTkToplevel(self)
        janela_db.title("Painel Interativo de Debloat e Restauro")
        janela_db.geometry("600x750")
        janela_db.transient(self)
        janela_db.grab_set()
        janela_db.configure(fg_color=self.bg_main)

        ctk.CTkLabel(janela_db, text="[ GERENCIADOR GLOBAL DE APPS DO WINDOWS ]", font=("Segoe UI", 16, "bold"), text_color=self.acento).pack(pady=(20, 10))

        frame_legenda = ctk.CTkFrame(janela_db, fg_color="transparent")
        frame_legenda.pack(pady=(0, 10))
        ctk.CTkLabel(frame_legenda, text="■ INSTALADO", font=("Segoe UI", 12, "bold"), text_color="#2ecc71").pack(side="left", padx=10)
        ctk.CTkLabel(frame_legenda, text="■ NÃO INSTALADO", font=("Segoe UI", 12, "bold"), text_color="#e74c3c").pack(side="left", padx=10)

        scroll_db = ctk.CTkScrollableFrame(janela_db, fg_color=self.bg_painel, border_width=1, border_color=self.borda, corner_radius=12)
        scroll_db.pack(expand=True, fill="both", padx=20, pady=5)

        lbl_loading = ctk.CTkLabel(scroll_db, text="A analisar profundamente o sistema... Por favor aguarde.", font=("Segoe UI", 12, "italic"), text_color=self.texto_cinza)
        lbl_loading.pack(pady=20)

        apps = {
            "Assistente Cortana (Obsoleto)": "*Microsoft.549981C3F5F10*", 
            "Xbox Game Bar": "*XboxGamingOverlay*",
            "Xbox Console Companion": "*XboxApp*",
            "Xbox Identity Provider": "*XboxIdentityProvider*",
            "Xbox Speech To Text": "*XboxSpeechToTextOverlay*",
            "Microsoft Mapas": "*Maps*", 
            "Clima (Bing Weather)": "*BingWeather*",
            "Câmera Nativa": "*WindowsCamera*", 
            "Calculadora do Windows": "*Calculator*",
            "Visualizador 3D": "*3DViewer*", 
            "Pessoas (People)": "*People*",
            "Gravador de Voz": "*SoundRecorder*", 
            "Hub de Feedback": "*FeedbackHub*",
            "Microsoft Solitaire": "*SolitaireCollection*", 
            "Notícias (Bing News)": "*BingNews*",
            "Skype Integrado": "*SkypeApp*",
            "Dicas do Windows (Get Help)": "*GetHelp*",
            "Paint 3D": "*MSPaint*",
            "Filmes e TV": "*ZuneVideo*",
            "Groove Música": "*ZuneMusic*",
            "Vincular ao Celular (Your Phone)": "*YourPhone*",
            "Email e Calendário Padrão": "*windowscommunicationsapps*",
            "Portal de Realidade Mista": "*MixedReality.Portal*",
            "Microsoft Notas Autoadesivas": "*MicrosoftStickyNotes*",
            "Microsoft Office Hub": "*MicrosoftOfficeHub*",
            "Microsoft To Do": "*Todos*",
            "Alarme e Relógio": "*WindowsAlarms*",
            "Serviços de Extensão de Web": "*WebpImageExtension*",
            "Hub de Desenvolvedores": "*WindowsDeveloperMode*"
        }

        vars_dict = {}

        def carregar_status():
            try:
                cmd_ps = 'powershell -Command "Get-AppxPackage | Select-Object -ExpandProperty Name"'
                res = subprocess.run(cmd_ps, capture_output=True, text=True, creationflags=0x08000000, startupinfo=get_si())
                pacotes_instalados = res.stdout.lower()
            except Exception: pacotes_instalados = ""
                
            def popular_ui():
                lbl_loading.destroy()
                for nome, pacote in apps.items():
                    var = ctk.IntVar()
                    termo_busca = pacote.replace("*", "").lower()
                    if termo_busca in pacotes_instalados:
                        texto_exibicao = f"{nome} (Instalado)"
                        cor_texto = "#2ecc71"
                    else:
                        texto_exibicao = f"{nome} (Ausente)"
                        cor_texto = "#e74c3c"
                    cb = ctk.CTkCheckBox(scroll_db, text=texto_exibicao, variable=var, text_color=cor_texto, fg_color=self.acento, font=("Segoe UI", 12, "bold"))
                    cb.pack(anchor="w", pady=5, padx=10)
                    vars_dict[pacote] = var
            self.after(0, popular_ui)
            
        threading.Thread(target=carregar_status, daemon=True).start()

        def executar_acao(acao):
            selecionados = [pacote for pacote, var in vars_dict.items() if var.get() == 1]
            if not selecionados:
                self.log("[-] Nenhum aplicativo selecionado no painel de Debloat.", "erro")
                return

            def tarefa():
                texto_acao = "remoção" if acao == "remover" else "reinstalação"
                self.log(f"[*] Iniciando {texto_acao} nativa de {len(selecionados)} pacotes via PowerShell AppX...")
                comandos_lote = []
                for pacote in selecionados:
                    if acao == "remover":
                        cmd = f'powershell -Command "Get-AppxPackage {pacote} | Remove-AppxPackage"'
                        comandos_lote.append((cmd, f"Desinstalando AppX {pacote}"))
                    else:
                        cmd = f'powershell -Command "Get-AppxPackage -AllUsers {pacote} | ForEach-Object {{Add-AppxPackage -DisableDevelopmentMode -Register \\\"$($_.InstallLocation)\\AppXManifest.xml\\\"}}"'
                        comandos_lote.append((cmd, f"Restaurando AppX {pacote}"))
                
                sucesso = True
                for cmd, desc in comandos_lote:
                    self.log(f"   [>] {desc}...")
                    res = subprocess.run(cmd, shell=True, creationflags=0x08000000, startupinfo=get_si())
                    if res.returncode != 0:
                        sucesso = False
                        self.log(f"   [-] Falha no comando: {desc}", "erro")
                        
                if sucesso: self.log(f"[+] Operação Mestra de {texto_acao} (Apps) concluída com SUCESSO ABSOLUTO!")
                else: self.log(f"[-] A operação encontrou avisos. Alguns apps base do Windows podem recusar desinstalação.", "erro")
                time.sleep(1.5)
                self.after(0, janela_db.destroy)

            threading.Thread(target=tarefa, daemon=True).start()

        frame_botoes = ctk.CTkFrame(janela_db, fg_color="transparent")
        frame_botoes.pack(pady=(10, 20), fill="x", padx=20)
        
        btn_remover = ctk.CTkButton(frame_botoes, text="DESINSTALAR (DEBLOAT)", command=lambda: executar_acao("remover"), fg_color="#e74c3c", hover_color="#c0392b", font=("Segoe UI", 12, "bold"), corner_radius=8, width=150)
        btn_remover.pack(side="left", padx=10, expand=True)
        
        btn_reinstalar = ctk.CTkButton(frame_botoes, text="RESTAURAR (XML)", command=lambda: executar_acao("reinstalar"), fg_color="#2ecc71", hover_color="#27ae60", font=("Segoe UI", 12, "bold"), corner_radius=8, width=150)
        btn_reinstalar.pack(side="right", padx=10, expand=True)

    def limpar_temp_nativa(self):
        def tarefa():
            self.log("[*] Mapeando lixo eletrónico na pasta Temp de forma nativa (Varredura C/C++)...")
            temp_path = os.environ.get('TEMP')
            if not temp_path or not os.path.exists(temp_path): 
                self.log("[-] Pasta Temp não encontrada.", "erro")
                return
            
            arquivos_para_apagar = []
            for root, dirs, files in os.walk(temp_path, topdown=False):
                for name in files: arquivos_para_apagar.append(os.path.join(root, name))
                for name in dirs: arquivos_para_apagar.append(os.path.join(root, name))
            
            total = len(arquivos_para_apagar)
            if total == 0: 
                self.log("[+] A sua pasta temporária já está 100% esterilizada.")
                return
            
            self.log(f"[*] Identificados {total} ficheiros corrompidos ou inúteis. Iniciando algoritmo de deleção...")
            apagados = 0
            for i, item in enumerate(arquivos_para_apagar):
                try:
                    if os.path.isfile(item): os.remove(item)
                    elif os.path.isdir(item): os.rmdir(item)
                    apagados += 1
                except Exception: pass
                if i % 50 == 0 and i > 0: self.log(f"   ... Destruídos {i} de {total} itens...")
            self.log(f"[+] Limpeza Profunda Concluída: {apagados} ficheiros apagados de forma permanente.")
        threading.Thread(target=tarefa, daemon=True).start()

    # =====================================================================
    # BLOCO 8: OTIMIZAÇÕES NATIVAS CTYPES E PYTHON KERNEL
    # =====================================================================
    def purgar_standby_list_nativa(self):
        def tarefa():
            if not self.is_admin:
                self.log("[-] Permissão Negada: É obrigatório executar como Administrador de Domínio.", "erro")
                return
            self.log("[*] Solicitando privilégios SeProfileSingleProcessPrivilege ao Kernel do SO...")
            try:
                SE_PRIVILEGE_ENABLED = 0x00000002
                TOKEN_ADJUST_PRIVILEGES = 0x0020
                TOKEN_QUERY = 0x0008
                SystemMemoryListInformation = 80
                MemoryPurgeStandbyList = 4

                class LUID(ctypes.Structure): _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]
                class LUID_AND_ATTRIBUTES(ctypes.Structure): _fields_ = [("Luid", LUID), ("Attributes", wintypes.DWORD)]
                class TOKEN_PRIVILEGES(ctypes.Structure): _fields_ = [("PrivilegeCount", wintypes.DWORD), ("Privileges", LUID_AND_ATTRIBUTES * 1)]

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

                if status == 0: self.log("[+] Standby List esvaziada com sucesso! O Stuttering de RAM foi aniquilado.")
                else: self.log(f"[-] Erro NTSTATUS ao tentar purgar a memória: {hex(status)}", "erro")
                kernel32.CloseHandle(hToken)
            except Exception as e: self.log(f"[-] Erro Grave na Aplicação Ctypes (Standby List): {str(e)}", "erro")
        threading.Thread(target=tarefa, daemon=True).start()

    def otimizar_ram_nativa(self):
        def tarefa():
            self.log("[*] Invocando API PSAPI.dll para esvaziar Working Set de processos ativos na RAM...")
            try:
                PROCESS_SET_QUOTA = 0x0100
                PROCESS_QUERY_INFORMATION = 0x0400
                count = 0
                psapi = ctypes.WinDLL('psapi.dll')
                kernel32 = ctypes.WinDLL('kernel32.dll')
                
                for proc in psutil.process_iter(['pid']):
                    try:
                        h_process = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA, False, proc.info['pid'])
                        if h_process:
                            if psapi.EmptyWorkingSet(h_process): count += 1
                            kernel32.CloseHandle(h_process)
                    except Exception: pass
                self.log(f"[+] Smart RAM Cleaner executado. Memória libertada em {count} aplicações em background.")
            except Exception as e: self.log(f"[-] Erro Crítico na API do Kernel Windows: {str(e)}", "erro")
        threading.Thread(target=tarefa, daemon=True).start()

    def prioridade_jogos_nativa(self):
        def tarefa():
            self.log("[*] Analisando Árvore PIDs e alocando instruções de CPU (High Priority) para Jogos...")
            jogos_alvo = ['cs2.exe', 'dota2.exe', 'overwatch.exe', 'valorant.exe', 'javaw.exe', 'gta5.exe', 'robloxplayerbeta.exe', 'r5apex.exe', 'lol.exe', 'cod.exe', 'cyberpunk2077.exe', 'rainbowsix.exe']
            encontrados = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    nome = str(proc.info['name']).lower()
                    if nome in jogos_alvo:
                        p = psutil.Process(proc.info['pid'])
                        p.nice(psutil.HIGH_PRIORITY_CLASS)
                        encontrados.append(nome)
                except Exception: pass
            
            if encontrados:
                for jogo in set(encontrados): self.log(f"[+] Sucesso: Engine detectada -> {jogo.upper()} | Prioridade ALTA da CPU Cravada.")
            else: self.log("[-] Nenhum jogo reconhecido em execução. Abra o jogo primeiro antes de clicar!", "erro")
        threading.Thread(target=tarefa, daemon=True).start()

    def verificar_hz_monitor(self):
        def tarefa():
            self.log("[*] Consultando a biblioteca física de Vídeo do Windows (user32.dll/DEVMODE)...")
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
                    self.log(f"[+] Leitura concluída: O seu monitor principal está a rodar a {hz}Hz nativos.")
                    if hz <= 60: self.log("[-] Aviso Técnico: Se comprou um monitor Gamer, você deve alterar nas opções do Windows!", "erro")
                else: self.log("[-] Falha grave ao tentar ler as informações da placa de vídeo PCI.", "erro")
            except Exception as e: self.log(f"[-] Exceção Crítica na EDID de hardware: {str(e)}", "erro")
        threading.Thread(target=tarefa, daemon=True).start()

    # =====================================================================
    # BLOCO 9: CHAVES DE REGISTO E TOGGLES (STABLE VERSION)
    # =====================================================================
    def toggle_mouse(self):
        est = self.sw_mouse.get()
        if est == 1:
            lote = [
                ('reg add "HKCU\\Control Panel\\Mouse" /v "MouseSpeed" /t REG_SZ /d "0" /f >nul 2>&1 || exit 0', "Cortar Curva de Velocidade do Rato"),
                ('reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold1" /t REG_SZ /d "0" /f >nul 2>&1 || exit 0', "Esmagar Preditivo 1"),
                ('reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold2" /t REG_SZ /d "0" /f >nul 2>&1 || exit 0', "Esmagar Preditivo 2")
            ]
        else:
            lote = [
                ('reg add "HKCU\\Control Panel\\Mouse" /v "MouseSpeed" /t REG_SZ /d "1" /f >nul 2>&1 || exit 0', "Restaurar Aceleração (MouseSpeed=1)"),
                ('reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold1" /t REG_SZ /d "6" /f >nul 2>&1 || exit 0', "Restaurar Preditivo Nível 1 (6)"),
                ('reg add "HKCU\\Control Panel\\Mouse" /v "MouseThreshold2" /t REG_SZ /d "10" /f >nul 2>&1 || exit 0', "Restaurar Preditivo Nível 2 (10)")
            ]
        self.executar_lote_com_verificacao(lote, "Mira Perfeita em FPS (Raw Mouse Input Exato)", self.sw_mouse, reinicio=True)

    def toggle_visual_perf(self):
        est = self.sw_visual_perf.get()
        val_fx = 2 if est == 1 else 0
        val_tra = 0 if est == 1 else 1
        lote = [
            (f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d {val_fx} /f >nul 2>&1 || exit 0', "Configurar Explorer VisualFX"),
            (f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "EnableTransparency" /t REG_DWORD /d {val_tra} /f >nul 2>&1 || exit 0', "Gerir Renderização Acrílica (Transparência)")
        ]
        self.executar_lote_com_verificacao(lote, "Desempenho Visual Máximo Unificado", self.sw_visual_perf)

    def remover_bloqueio_organizacao(self):
        self.log("[*] Investigando Chaves Corporativas de GPO Ocultas...")
        lote = [
            ('reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /f >nul 2>&1 || exit 0', "Remover GPO Restritiva do Edge na Máquina"),
            ('reg delete "HKCU\\SOFTWARE\\Policies\\Microsoft\\Edge" /f >nul 2>&1 || exit 0', "Remover GPO Restritiva do Edge no Utilizador"),
            ('gpupdate /force >nul 2>&1 || exit 0', "Atualizar Diretrizes do Sistema (Group Policy)")
        ]
        self.executar_lote_com_verificacao(lote, "Desbloqueio de Menus Gerenciados por Organização")

    def toggle_telemetry_tasks(self):
        est = self.sw_tasks.get()
        p1 = "\\Microsoft\\Windows\\Application Experience\\Microsoft Compatibility Appraiser"
        p2 = "\\Microsoft\\Windows\\Customer Experience Improvement Program\\Consolidator"
        acao_str = "Disable" if est == 1 else "Enable"
        lote = [
            (f'schtasks /Change /TN "{p1}" /{acao_str} >nul 2>&1 || exit 0', f"{acao_str} Microsoft Compatibility Appraiser"),
            (f'schtasks /Change /TN "{p2}" /{acao_str} >nul 2>&1 || exit 0', f"{acao_str} Tarefa de Coleta CEIP")
        ]
        self.executar_lote_com_verificacao(lote, "Gestão de Agendadores Secretos de Telemetria", self.sw_tasks)

    def toggle_vs_tel(self): 
        est = self.sw_vs_tel.get()
        lote = [(f'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\VisualStudio\\Telemetry" /v "RefuseTelemetry" /t REG_DWORD /d {1 if est == 1 else 0} /f >nul 2>&1 || exit 0', "Configurar Preferência Telemetria VS")]
        self.executar_lote_com_verificacao(lote, "Limpeza de Servidor VS Telemetry", self.sw_vs_tel)

    def toggle_thrott(self): 
        est = self.sw_thrott.get()
        lote = [(f'reg add "HKLM\\System\\CurrentControlSet\\Control\\Power\\PowerThrottling" /v "PowerThrottlingOff" /t REG_DWORD /d {1 if est == 1 else 0} /f >nul 2>&1 || exit 0', "Restrição Dinâmica de Processos de Fundo")]
        self.executar_lote_com_verificacao(lote, "Anulação de Power Throttling do Processador", self.sw_thrott)
    
    def toggle_loc(self): 
        est = self.sw_loc.get()
        if est == 1: lote = [('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v "DisableLocation" /t REG_DWORD /d 1 /f >nul 2>&1 || exit 0', "Aplicar GPO Físico Proibindo Sensor")]
        else: lote = [('reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v "DisableLocation" /f >nul 2>&1 || exit 0', "Remover GPO e Libertar Acesso à Localização")]
        self.executar_lote_com_verificacao(lote, "Bloqueio do Sensor de Localização do Sistema", self.sw_loc)

    def toggle_gaming(self): 
        est = self.sw_gaming.get()
        if est == 1:
            lote = [
                ('reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f >nul 2>&1 || exit 0', "Impor Modo de Jogo (Game Bar)"),
                ('reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f >nul 2>&1 || exit 0', "Assassinar Gravador Xbox GameDVR")
            ]
        else:
            lote = [
                ('reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 0 /f >nul 2>&1 || exit 0', "Restaurar Comportamento Não-Gamer"),
                ('reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 1 /f >nul 2>&1 || exit 0', "Ressuscitar Gravações Xbox GameDVR")
            ]
        self.executar_lote_com_verificacao(lote, "Modo de Jogo Pro Nativo", self.sw_gaming)

    def toggle_tel(self): 
        est = self.sw_tel.get()
        if est == 1:
            lote = [("sc stop DiagTrack >nul 2>&1 || exit 0", "Interromper Serviço DiagTrack"), ("sc config DiagTrack start= disabled >nul 2>&1 || exit 0", "Desativar Arranque DiagTrack")]
        else:
            lote = [("sc config DiagTrack start= auto >nul 2>&1 || exit 0", "Restaurar Serviço DiagTrack"), ("sc start DiagTrack >nul 2>&1 || exit 0", "Reiniciar Tráfego DiagTrack")]
        self.executar_lote_com_verificacao(lote, "Destruição de Telemetria Windows", self.sw_tel)
        
    def toggle_nv_priv(self): 
        est = self.sw_nv_priv.get()
        if est == 1:
            lote = [
                ('taskkill /f /im NvTelemetryContainer.exe >nul 2>&1 || exit 0', "Terminar Processo NvTelemetryContainer"),
                ('reg add "HKLM\\SOFTWARE\\NVIDIA Corporation\\NvControlPanel2\\Client" /v "OptIn" /t REG_DWORD /d 0 /f >nul 2>&1 || exit 0', "Negar Contrato Opt-In da NVIDIA")
            ]
            self.executar_lote_com_verificacao(lote, "Privacidade Sensível NVIDIA", self.sw_nv_priv)
        else: 
            self.salvar_config(self.sw_nv_priv.nome_log, "0")
    
    def toggle_srv(self):
        est = self.sw_srv.get()
        if est == 1:
            lote = [
                ("sc stop SysMain >nul 2>&1 || exit 0", "Matar Pré-Carregamento SysMain"), ("sc config SysMain start= disabled >nul 2>&1 || exit 0", "Desativar SysMain (Superfetch)"),
                ("sc stop WSearch >nul 2>&1 || exit 0", "Interromper WSearch"), ("sc config WSearch start= disabled >nul 2>&1 || exit 0", "Desativar WSearch")
            ]
        else:
            lote = [
                ("sc config SysMain start= auto >nul 2>&1 || exit 0", "Tornar SysMain Automático"), ("sc start SysMain >nul 2>&1 || exit 0", "Reiniciar Carregador"),
                ("sc config WSearch start= delayed-auto >nul 2>&1 || exit 0", "Permitir WSearch Lento"), ("sc start WSearch >nul 2>&1 || exit 0", "Voltar a Indexar")
            ]
        self.executar_lote_com_verificacao(lote, "Supressão de Serviços Pesados", self.sw_srv)
        
    def toggle_tim(self): 
        est = self.sw_tim.get()
        lote = [(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel" /v "GlobalTimerResolutionRequests" /t REG_DWORD /d {1 if est == 1 else 0} /f >nul 2>&1 || exit 0', "Impor Tick de API 0.5 milissegundos")]
        self.executar_lote_com_verificacao(lote, "Resolução de Tempo de Resposta", self.sw_tim)
        
    def toggle_net_thrott(self):
        est = self.sw_net_thrott.get()
        lote = [(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d {0xFFFFFFFF if est == 1 else 10} /f >nul 2>&1 || exit 0', "Modificar Índice Limitador de Multimédia")]
        self.executar_lote_com_verificacao(lote, "Quebra do Estrangulamento de Largura de Rede Local", self.sw_net_thrott)

    def toggle_core_parking(self):
        est = self.sw_core_park.get()
        lote = [
            (f'powercfg /setacvalueindex scheme_current sub_processor CPMINCORES {100 if est == 1 else 5} >nul 2>&1 || exit 0', "Definir Index Mínimo ACPI Core Parking"),
            ('powercfg /setactive scheme_current >nul 2>&1 || exit 0', "Forçar Refresh de Energia")
        ]
        self.executar_lote_com_verificacao(lote, "Libertação de Núcleos Adormecidos", self.sw_core_park)

    def toggle_mnu(self):
        est = self.sw_mnu.get()
        if est == 1: lote = [('reg add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /f /ve >nul 2>&1 || exit 0', "Anular Menus Win11")]
        else: lote = [('reg delete "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f >nul 2>&1 || exit 0', "Remover CLSID Win11")]
        self.executar_lote_com_verificacao(lote, "Menu de Contexto Clássico", self.sw_mnu, reinicio=True)
        
    def toggle_bmn(self): 
        est = self.sw_bmn.get()
        lote = [(f"bcdedit /timeout {2 if est == 1 else 30} >nul 2>&1 || exit 0", "Injetar Timeout BCD")]
        self.executar_lote_com_verificacao(lote, "Diminuição do Delay Ecrã de Boot", self.sw_bmn, reinicio=True)
    
    def toggle_fast_startup(self):
        est = self.sw_fast_start.get()
        lote = [(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v "HiberbootEnabled" /t REG_DWORD /d {0 if est == 1 else 1} /f >nul 2>&1 || exit 0', "Manipular HiberbootEnabled")]
        self.executar_lote_com_verificacao(lote, "Desativador Bugs na Inicialização Rápida", self.sw_fast_start, reinicio=True)

    def toggle_widgets(self):
        est = self.sw_widgets.get()
        if est == 1: lote = [('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Dsh" /v "AllowNewsAndInterests" /t REG_DWORD /d 0 /f >nul 2>&1 || exit 0', "Bloqueio Policy Dsh")]
        else: lote = [('reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Dsh" /v "AllowNewsAndInterests" /f >nul 2>&1 || exit 0', "Permitir Dsh (Widgets)")]
        self.executar_lote_com_verificacao(lote, "Remover Notícias na Taskbar", self.sw_widgets, reinicio=True)

    def toggle_hibernacao(self):
        est = self.sw_hibernacao.get()
        if est == 1: lote = [("powercfg -h off", "Desativar Hibernação e Excluir hiberfil.sys")]
        else: lote = [("powercfg -h on", "Reativar Hibernação no Disco Local")]
        self.executar_lote_com_verificacao(lote, "Controle de Hibernação e Espaço em Disco", self.sw_hibernacao)

    def toggle_pow(self):
        est = int(self.sw_pow.get())
        if est == 1: threading.Thread(target=self._ativar_desempenho_maximo, daemon=True).start()
        else: threading.Thread(target=self._ativar_equilibrado, daemon=True).start()

    def _ativar_desempenho_maximo(self):
        res_l = subprocess.run(['powercfg', '/l'], capture_output=True, text=True, creationflags=0x08000000, startupinfo=get_si())
        guid_alvo = self.carregar_config("GuidMaximo", "")
        if not guid_alvo or guid_alvo.lower() not in res_l.stdout.lower():
            if "e9a42b02-d5df-448d-aa00-03f14749eb61" in res_l.stdout.lower(): guid_alvo = "e9a42b02-d5df-448d-aa00-03f14749eb61" 
            else:
                res_dup = subprocess.run(['powercfg', '-duplicatescheme', 'e9a42b02-d5df-448d-aa00-03f14749eb61'], capture_output=True, text=True, creationflags=0x08000000, startupinfo=get_si())
                match = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", res_dup.stdout)
                guid_alvo = match.group(1) if match else "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" 
        lote = [(f'powercfg /setactive {guid_alvo} >nul 2>&1 || exit 0', "Aplicar Plano Ultimate Workstation")]
        self.executar_lote_com_verificacao(lote, "Plano de Energia Desempenho Máximo", self.sw_pow)

    def _ativar_equilibrado(self):
        guid_eq = getattr(self, 'guid_padrao', "381b4222-f694-41f0-9685-ff5bb260df2e")
        lote = [(f'powercfg /setactive {guid_eq} >nul 2>&1 || exit 0', "Recuperar Estado Energético Padrão")]
        self.executar_lote_com_verificacao(lote, "Reversão do Plano de Energia", self.sw_pow)

    # =====================================================================
    # BLOCO 10: AÇÕES INDIRETAS DE BOTÕES (DIAGNÓSTICO E LIMPEZA)
    # =====================================================================
    def abrir_inicializacao(self):
        self.log("[*] Invocando através da API Win32 o Gestor de MS-Settings para inicialização...")
        self.executar_comando_assincrono("start ms-settings:startupapps", "Abertura do Gestor Startup UI")

    def benchmark_dns_nativo(self):
        def tarefa():
            self.log("[*] Buscando DNS Atual configurado na sua placa de rede física (Powershell Adapter)...")
            try:
                cmd_ps = 'powershell -Command "(Get-NetAdapter | Where-Object {$_.Status -eq \'Up\' -and $_.InterfaceAlias -notlike \'*Loopback*\'} | Get-DnsClientServerAddress -AddressFamily IPv4)[0].ServerAddresses[0]"'
                res_dns = subprocess.run(cmd_ps, capture_output=True, text=True, creationflags=0x08000000, startupinfo=get_si())
                current_dns = res_dns.stdout.strip()
            except Exception:
                current_dns = ""
                
            servidores = {
                "Google (Global Padrão)": "8.8.8.8", 
                "Cloudflare (Velocidade DNS)": "1.1.1.1", 
                "OpenDNS (Filtros Security)": "208.67.222.222", 
                "Quad9 (Privacidade e Estabilidade)": "9.9.9.9"
            }
            
            if current_dns and re.match(r"^\d{1,3}(\.\d{1,3}){3}$", current_dns):
                servidores["Atual (Seu Provedor)"] = current_dns
                
            resultados = {}
            self.log("[*] Iniciando Benchmark Global de Latência Master. Testando rotas dinâmicas do Kernel (ICMP)...")
            
            for nome, ip in servidores.items():
                try:
                    self.log(f"[*] A enviar 4 pacotes de teste robustos para os repositórios da: {nome} ({ip})...")
                    res = subprocess.run(f"ping {ip} -n 4", capture_output=True, text=True, creationflags=0x08000000, startupinfo=get_si())
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
        janela_dns.title("Seleção Automática do Melhor DNS")
        janela_dns.geometry("500x480")
        janela_dns.transient(self)
        janela_dns.grab_set()
        janela_dns.configure(fg_color=self.bg_main)
        
        ctk.CTkLabel(janela_dns, text="[ RESULTADO DO BENCHMARK DNS NATIVO ]", font=("Segoe UI", 16, "bold"), text_color=self.acento).pack(pady=(20, 10))
        
        frame_res = ctk.CTkFrame(janela_dns, fg_color=self.bg_painel, border_width=1, border_color=self.borda, corner_radius=10)
        frame_res.pack(expand=True, fill="both", padx=20, pady=10)
        
        opcoes_dropdown = []
        melhor_opcao = None
        
        for i, (nome, (ping, ip)) in enumerate(resultados_ordenados):
            cor = "#2ecc71" if i == 0 and ping != 999 else self.texto_branco
            texto_ping = f"{ping} ms" if ping != 999 else "Falha Total / TimeOut"
            texto_exibicao = f"{nome} ({ip}) - {texto_ping}"
            
            lbl_res = ctk.CTkLabel(frame_res, text=texto_exibicao, font=("Segoe UI", 13, "bold" if i == 0 else "normal"), text_color=cor)
            lbl_res.pack(anchor="w", padx=20, pady=8)
            
            if ping != 999:
                opcao = f"{nome} ({ip})"
                opcoes_dropdown.append(opcao)
                if i == 0: 
                    melhor_opcao = opcao
                    
        ctk.CTkLabel(janela_dns, text="Selecione o endereço exato para aplicar forçado na placa de rede:", font=("Segoe UI", 12), text_color=self.texto_cinza).pack(pady=(10, 5))
        
        combo_dns = ctk.CTkOptionMenu(janela_dns, values=opcoes_dropdown, fg_color=self.bg_painel, button_color=self.borda, button_hover_color=self.acento, text_color=self.texto_branco, font=("Segoe UI", 12), corner_radius=8)
        if melhor_opcao: 
            combo_dns.set(melhor_opcao)
        combo_dns.pack(pady=5)
        
        def aplicar_dns_selecionado():
            escolha = combo_dns.get()
            match_ip = re.search(r"\(([\d\.]+)\)", escolha)
            if match_ip:
                ip_alvo = match_ip.group(1)
                self.log(f"[*] A Aplicar injeção absoluta de DNS Primário {ip_alvo} na placa de rede física ativa...")
                cmd = f'powershell -Command "Get-NetAdapter | Where-Object {{$_.Status -eq \'Up\' -and $_.InterfaceAlias -notlike \'*Loopback*\'}} | Set-DnsClientServerAddress -ServerAddresses \'{ip_alvo}\'" >nul 2>&1 || exit 0'
                lote = [(cmd, f"Implementando Adaptação Master Dinâmica de DNS ({ip_alvo})")]
                self.executar_lote_com_verificacao(lote, f"Aplicação Definitiva de Roteamento DNS ({ip_alvo})")
            janela_dns.destroy()
            
        btn_aplicar = ctk.CTkButton(janela_dns, text="INJETAR MELHOR DNS", command=aplicar_dns_selecionado, fg_color=self.bg_painel, hover_color=self.acento, text_color=self.texto_branco, border_width=1, border_color=self.acento, font=("Segoe UI", 12, "bold"), corner_radius=8)
        btn_aplicar.pack(pady=(10, 20))

    def analisar_rede_info(self):
        def tarefa():
            self.log("[*] Iniciando Diagnóstico de Rede... Aguarde alguns segundos...")
            try: ip_local = socket.gethostbyname(socket.gethostname())
            except Exception: ip_local = "Erro LAN"
            try: ip_publico = urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode('utf8')
            except Exception: ip_publico = "Restrito Firewall"
            try:
                res = subprocess.run('ping 8.8.8.8 -n 1', capture_output=True, text=True, creationflags=0x08000000, startupinfo=get_si())
                ping_str = "Inacessível"
                if "tempo=" in res.stdout: ping_str = res.stdout.split("tempo=")[1].split("ms")[0].strip() + " ms"
                elif "time=" in res.stdout: ping_str = res.stdout.split("time=")[1].split("ms")[0].strip() + " ms"
            except Exception: ping_str = "Falha Ping"
            self.log(f"\n=== MÓDULO DE ROTAS ===\n> LAN: {ip_local}\n> WAN: {ip_publico}\n> Ping: {ping_str}\n========================\n")
        threading.Thread(target=tarefa, daemon=True).start()

    def verificar_erros(self): 
        self.log("[*] Despachando a Verificação de Sistemas de Ficheiros...")
        self.executar_comando_visivel("sfc /scannow", "Auditoria SFC Native API", reinicio=True)

    def verificar_disco(self): 
        self.log("[*] Verificando partições locais...")
        comandos_array = []
        for part in psutil.disk_partitions():
            if part.fstype != '' and 'cdrom' not in part.opts:
                letra_particao = part.device[:2]
                comandos_array.append(f"echo. & echo >>> TESTE DO DISCO {letra_particao} <<< & chkdsk {letra_particao} /scan")
        cmd_final_consolidado = " & ".join(comandos_array)
        if cmd_final_consolidado: self.executar_comando_visivel(cmd_final_consolidado, "Lote CHKDSK", reinicio=True)

    # ---------------------------------------------------------------------
    # FIX APLICADO: Quebra do bloqueio de 24h e try/catch no PowerShell
    # ---------------------------------------------------------------------
    def criar_ponto_restauracao(self):
        self.log("[*] Quebrando o limite de 24h do Windows e forçando a gravação do Ponto de Restauração...")
        lote = [
            ('reg add "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\SystemRestore" /v "SystemRestorePointCreationFrequency" /t REG_DWORD /d 0 /f', "Removendo bloqueio temporal (24h) do Windows"),
            ('powershell.exe -ExecutionPolicy Bypass -NoProfile -Command "try { Enable-ComputerRestore -Drive \'C:\\\' -ErrorAction Stop; exit 0 } catch { exit 1 }"', "Injetando Ativação VSS no Disco C:"),
            ('powershell.exe -ExecutionPolicy Bypass -NoProfile -Command "try { Checkpoint-Computer -Description \'GustavoOptimizer Checkpoint\' -RestorePointType \'MODIFY_SETTINGS\' -ErrorAction Stop; exit 0 } catch { exit 1 }"', "Congelando Registos e criando o Ponto")
        ]
        self.executar_lote_com_verificacao(lote, "Gravação Segura Root Checkpoint")

    def reparar_imagem_dism(self):
        self.log("[*] Exigindo repositórios sãos do servidor Microsoft. Janela CLI aberta!")
        self.executar_comando_visivel("DISM /Online /Cleanup-Image /RestoreHealth", "Terapia de Imagem (DISM API)")

    def limpar_logs_windows(self):
        self.log("[*] Alimentando Motor Wevtutil para limpar Histórico Fantasma...")
        lote = [('powershell -Command "wevtutil el | foreach { wevtutil cl \\\"$_\\\" }"', "Limpeza Wevtutil PowerShell")]
        self.executar_lote_com_verificacao(lote, "Destruição Lógica Event Viewer")

    def limpar_prefetch(self):
        self.log("[*] Interrompendo a leitura inútil de inicialização legada...")
        lote = [('del /s /f /q "%WINDIR%\\Prefetch\\*.*" >nul 2>&1 || exit 0', "Deletar Entradas .pf")]
        self.executar_lote_com_verificacao(lote, "Destruição do Prefetch")

    def limpar_windows(self): 
        self.log("[*] Ativando Sistema Sagerun via API Nativa Cleanmgr.exe...")
        self.executar_comando_assincrono("cleanmgr /sagerun:1", "Invocar Ferramenta Cleanmgr")
        
    def otimizar_internet(self): 
        self.log("[*] Esvaziando Tabela DNS e Destruindo a Pilha WinSock.")
        lote = [("ipconfig /flushdns >nul 2>&1 || exit 0", "Enxugar DNS"), ("netsh winsock reset >nul 2>&1 || exit 0", "Destruir WinSock")]
        self.executar_lote_com_verificacao(lote, "Reset Paramétrico Adaptador LAN")
        
    def otimizar_discos(self): 
        self.log("[*] Aplicando Desfragmentação/Retrim. Janela CLI em background.")
        self.executar_comando_visivel("defrag /C /O /U", "Injeção Desfragmentadora")

    def limpar_gpu(self): 
        self.log("[*] Destruindo Shaders DirectX nativos corrompidos.")
        lote = [('del /f /s /q "%LocalAppData%\\NVIDIA\\DXCache\\*.*" >nul 2>&1 || exit 0', "Limpar Base DXCache NVIDIA")]
        self.executar_lote_com_verificacao(lote, "Extinção de Blocos de Cache GPU")
        
    def limpar_thumbnails(self): 
        self.log("[*] Matando Windows Explorer para libertar Thumbnails (.db)...")
        lote = [
            ('taskkill /f /im explorer.exe >nul 2>&1 || exit 0', "Matar explorer.exe"),
            ('del /f /s /q "%LocalAppData%\\Microsoft\\Windows\\Explorer\\thumbcache_*.db" >nul 2>&1 || exit 0', "Eliminação Matrizes .DB"),
            ('start explorer.exe', "Ressuscitar Explorer")
        ]
        self.executar_lote_com_verificacao(lote, "Exclusão Biblioteca de Ícones")
        
    def limpar_update(self):
        self.log("[*] Limpando repositório SoftwareDistribution...")
        lote = [
            ('net stop wuauserv >nul 2>&1 || exit 0', "Trancar Wuauserv"),
            ('del /s /f /q "%windir%\\SoftwareDistribution\\Download\\*.*" >nul 2>&1 || exit 0', "Eliminar Updates Engavetados"),
            ('net start wuauserv >nul 2>&1 || exit 0', "Reativar Wuauserv")
        ]
        self.executar_lote_com_verificacao(lote, "Limpeza SoftwareDistribution")
        
    def limpar_chrome(self): 
        self.log("[*] Entrando na infraestrutura Chromium Default Cache...")
        c_path = "\\".join(["Google", "Chrome", "User Data", "Default", "Cache", "*.*"])
        lote = [(f'del /s /f /q "%LocalAppData%\\{c_path}" >nul 2>&1 || exit 0', "Destruir Cache Chrome")]
        self.executar_lote_com_verificacao(lote, "Exterminador Cache Google Chrome")
        
    def limpar_edge(self): 
        self.log("[*] Obliteração de Cache no Navegador Edge Interno...")
        e_path = "\\".join(["Microsoft", "Edge", "User Data", "Default", "Cache", "*.*"])
        lote = [(f'del /s /f /q "%LocalAppData%\\{e_path}" >nul 2>&1 || exit 0', "Apagar Cache Edge")]
        self.executar_lote_com_verificacao(lote, "Erradicador Cache MS Edge")
        
    def limpar_opera(self): 
        self.log("[*] Rastreando ambientes fechados Opera Stable/GX...")
        p_gx = "\\".join(["Opera Software", "Opera GX Stable", "Cache", "*.*"])
        p_op = "\\".join(["Opera Software", "Opera Stable", "Cache", "*.*"])
        lote = [(f'del /s /f /q "%LocalAppData%\\{p_gx}" >nul 2>&1 || exit 0', "Destruidor GX"), (f'del /s /f /q "%LocalAppData%\\{p_op}" >nul 2>&1 || exit 0', "Destruidor OP")]
        self.executar_lote_com_verificacao(lote, "Limpeza Opera")

    def limpar_firefox(self):
        self.log("[*] Engatando comando recursivo Firefox...")
        f_path = "\\".join(["Mozilla", "Firefox", "Profiles", "*", "cache2", "*"])
        lote = [(f'powershell -Command "Remove-Item -Path \\"$env:LOCALAPPDATA\\{f_path}\\" -Recurse -Force -ErrorAction SilentlyContinue" >nul 2>&1 || exit 0', "Limpando Mozilla Cache2")]
        self.executar_lote_com_verificacao(lote, "Supressão Firefox Multi-Account")

    def limpar_spotify(self): 
        self.log("[*] Erradicando memória offline do Spotify...")
        s_path = "\\".join(["Spotify", "Data"])
        lote = [('taskkill /f /im Spotify.exe >nul 2>&1 || exit 0', "Travar Spotify"), (f'rmdir /s /q "%LocalAppData%\\{s_path}" >nul 2>&1 || exit 0', "Remover Árvore Mídia")]
        self.executar_lote_com_verificacao(lote, "Limpeza Spotify")
        
    def limpar_steam(self): 
        self.log("[*] Resolvendo problemas de updates Steam (appcache)...")
        st_path = "\\".join(["Steam", "appcache"])
        lote = [('taskkill /f /im steam.exe >nul 2>&1 || exit 0', "Terminar steam.exe"), (f'rmdir /s /q "C:\\Program Files (x86)\\{st_path}" >nul 2>&1 || exit 0', "Deletar Cache.vdf")]
        self.executar_lote_com_verificacao(lote, "Limpeza Steam Client")
        
    def limpar_discord(self): 
        self.log("[*] Eliminando Cache do Discord...")
        d_path = "\\".join(["Discord", "Cache"])
        lote = [('taskkill /f /im Discord.exe >nul 2>&1 || exit 0', "Matar Discord"), (f'rmdir /s /q "%AppData%\\{d_path}" >nul 2>&1 || exit 0', "Subtrair Área Cache")]
        self.executar_lote_com_verificacao(lote, "Limpeza Discord")
        
    def limpar_battlenet(self): 
        self.log("[*] Removendo Agente Atualizador Blizzard...")
        lote = [('taskkill /f /im Agent.exe >nul 2>&1 || exit 0', "Matar Agent.exe"), ('rmdir /s /q "%ProgramData%\\Battle.net" >nul 2>&1 || exit 0', "Deletar Battle.net Base")]
        self.executar_lote_com_verificacao(lote, "Bomba Lógica Battle.net")
        
    def limpar_apps_multi(self):
        self.log("[*] MODO BERSERKER: Limpeza Massiva Integrada.")
        s_path = "\\".join(["Spotify", "Data"])
        st_path = "\\".join(["Steam", "appcache"])
        d_path = "\\".join(["Discord", "Cache"])
        lote = [
            ('taskkill /f /im Spotify.exe >nul 2>&1 || exit 0', "Spotify Kill"), ('taskkill /f /im steam.exe >nul 2>&1 || exit 0', "Steam Kill"),
            ('taskkill /f /im Discord.exe >nul 2>&1 || exit 0', "Discord Kill"), ('taskkill /f /im Agent.exe >nul 2>&1 || exit 0', "Agent Kill"),
            (f'rmdir /s /q "%LocalAppData%\\{s_path}" >nul 2>&1 || exit 0', "Spotify Clean"), (f'rmdir /s /q "C:\\Program Files (x86)\\{st_path}" >nul 2>&1 || exit 0', "Steam Clean"),
            (f'rmdir /s /q "%AppData%\\{d_path}" >nul 2>&1 || exit 0', "Discord Clean"), ('rmdir /s /q "%ProgramData%\\Battle.net" >nul 2>&1 || exit 0', "Battle.net Clean")
        ]
        self.executar_lote_com_verificacao(lote, "Limpeza Integrada Múltipla")

    # =====================================================================
    # BLOCO 11: CONSTRUTORES DE LAYOUT GUI (CARDS)
    # =====================================================================
    def criar_secao(self, parent, texto, linha):
        lbl = ctk.CTkLabel(parent, text=f"// {texto.upper()}", font=("Segoe UI", 18, "bold"), text_color=self.acento)
        lbl.grid(row=linha, column=0, columnspan=3, pady=(25, 5), padx=10, sticky="w")
        self.cards_interface.append(lbl) 

    def criar_card_switch(self, parent, linha, coluna, categoria, titulo, descricao, cmd, nome_log, auto=True, reinicio=False):
        card = ctk.CTkFrame(parent, fg_color=self.bg_painel, corner_radius=10, height=160, border_width=1, border_color=self.borda)
        card.grid(row=linha, column=coluna, padx=10, pady=10, sticky="nsew") 
        card.grid_propagate(False)
        self.cards_interface.append(card)

        def on_enter(event): card.configure(border_color=self.acento)
        def on_leave(event): card.configure(border_color=self.borda)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        lbl_cat = ctk.CTkLabel(card, text=f" {categoria.upper()} ", font=("Segoe UI", 11, "bold"), text_color=self.acento, fg_color=self.bg_main, corner_radius=4)
        lbl_cat.place(x=15, y=15)

        lbl_tit = ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 15, "bold"), text_color=self.texto_branco)
        lbl_tit.place(x=15, y=45)
        
        lbl_desc = ctk.CTkLabel(card, text=descricao, font=("Segoe UI", 11), text_color=self.texto_cinza, wraplength=230, justify="left")
        lbl_desc.place(x=15, y=72)

        if reinicio:
            lbl_reinicio = ctk.CTkLabel(card, text="[REQUER REINICIAR]", font=("Segoe UI", 10, "bold"), text_color="#FF4444")
            lbl_reinicio.place(x=15, rely=0.85, anchor="w")
        
        sw = ctk.CTkSwitch(card, text="ATIVAR", progress_color=self.acento, fg_color=self.borda, font=("Segoe UI", 10, "bold"), text_color=self.acento)
        sw.place(relx=0.95, rely=0.85, anchor="e")
        
        estado_salvo = self.auditar_estado_real(nome_log)
        if estado_salvo == "1": sw.select()
        else: sw.deselect()

        def acao_com_memoria():
            cmd() 

        sw.configure(command=acao_com_memoria)
        sw.nome_log = nome_log 
        sw.comando_real = acao_com_memoria 
        
        if auto: self.lista_switches.append(sw)
        return sw

    def criar_card_botao(self, parent, linha, coluna, categoria, titulo, descricao, cmd, reinicio=False, btn_texto="EXECUTAR"):
        card = ctk.CTkFrame(parent, fg_color=self.bg_painel, corner_radius=10, height=160, border_width=1, border_color=self.borda)
        card.grid(row=linha, column=coluna, padx=10, pady=10, sticky="nsew") 
        card.grid_propagate(False)
        self.cards_interface.append(card)

        def on_enter(event): card.configure(border_color=self.acento)
        def on_leave(event): card.configure(border_color=self.borda)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        lbl_cat = ctk.CTkLabel(card, text=f" {categoria.upper()} ", font=("Segoe UI", 11, "bold"), text_color=self.acento, fg_color=self.bg_main, corner_radius=4)
        lbl_cat.place(x=15, y=15)

        lbl_tit = ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 15, "bold"), text_color=self.texto_branco)
        lbl_tit.place(x=15, y=45)
        
        lbl_desc = ctk.CTkLabel(card, text=descricao, font=("Segoe UI", 11), text_color=self.texto_cinza, wraplength=230, justify="left")
        lbl_desc.place(x=15, y=72)

        if reinicio:
            lbl_reinicio = ctk.CTkLabel(card, text="[REQUER REINICIAR]", font=("Segoe UI", 10, "bold"), text_color="#FF4444")
            lbl_reinicio.place(x=15, rely=0.85, anchor="w")
        
        btn = ctk.CTkButton(card, text=btn_texto, command=cmd, fg_color="transparent", hover_color=self.acento, text_color=self.texto_branco, corner_radius=6, border_width=2, border_color=self.acento, width=100, height=28, font=("Segoe UI", 11, "bold"))
        btn.place(relx=0.95, rely=0.85, anchor="e")
        return btn

    def montar_interface_total(self):
        
        for frame in [self.scroll_desempenho, self.scroll_rede, self.scroll_privacidade, self.scroll_limpeza, self.scroll_root]:
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=1)
            frame.grid_columnconfigure(2, weight=1)
        
        # TAB 1: ⚡ DESEMPENHO
        self.criar_secao(self.scroll_desempenho, "Perfis Inteligentes V2.0", 0)
        self.btn_gamer = self.criar_card_botao(self.scroll_desempenho, 1, 0, "Desempenho", "🎮 Ativar Modo Gamer", "Lê o hardware para aplicar otimizações seguras e latência zero.", self.acionar_perfil_gamer, btn_texto="ATIVAR MODO")
        self.btn_trabalho = self.criar_card_botao(self.scroll_desempenho, 1, 1, "Equilíbrio", "💼 Ativar Modo Trabalho", "Desliga agressivamente opções instáveis garantindo proteção ao seu trabalho.", self.acionar_perfil_trabalho, btn_texto="ATIVAR MODO")

        self.criar_secao(self.scroll_desempenho, "Otimizações Nativas (Kernel e RAM)", 2)
        self.criar_card_botao(self.scroll_desempenho, 3, 0, "Memória", "🚀 Smart RAM Cleaner", "Liberta memória em cache invocando a API de working set nativa do Windows.", self.otimizar_ram_nativa, btn_texto="LIMPAR RAM")
        self.criar_card_botao(self.scroll_desempenho, 3, 1, "Memória", "🌪️ Purgar Standby (ISLC)", "Nível Elite: Usa a API Ntdll para exterminar Stuttering forçando o despejo de páginas.", self.purgar_standby_list_nativa, btn_texto="PURGAR STANDBY")
        self.criar_card_botao(self.scroll_desempenho, 3, 2, "Desempenho", "🎯 Auto Game Priority", "Analisa a árvore local de PIDs para injetar High Priority em rotinas de jogos.", self.prioridade_jogos_nativa, btn_texto="APLICAR CPU")
        
        self.criar_card_botao(self.scroll_desempenho, 4, 0, "Hardware", "🖥️ Validador de Hz", "Consulta fisicamente a placa gráfica para atestar a comunicação de frequências do ecrã.", self.verificar_hz_monitor, btn_texto="VERIFICAR TELA")
        
        self.criar_secao(self.scroll_desempenho, "Desempenho Profundo", 5)
        self.sw_thrott = self.criar_card_switch(self.scroll_desempenho, 6, 0, "Desempenho", "🔋 Power Throttling", "Quebra a corrente que o Windows utiliza para limitar a voltagem de programas.", self.toggle_thrott, "Power Throttling")
        self.sw_gaming = self.criar_card_switch(self.scroll_desempenho, 6, 1, "Jogos", "🕹️ Modo de Jogo Pro", "Invoca a barra Game Mode oficial, mas trucida o sistema corrompido de DVR da Xbox.", self.toggle_gaming, "Gaming Mode")
        self.sw_tim = self.criar_card_switch(self.scroll_desempenho, 6, 2, "Latência", "⏱️ Timer Res (0.5ms)", "Força a diminuição do ciclo base do Windows para processar os cliques na hora absoluta.", self.toggle_tim, "Timer Res")
        
        self.sw_pow = self.criar_card_switch(self.scroll_desempenho, 7, 0, "Desempenho", "⚡ Plano Energia Máxima", "Invoca o CMD para extrair o Ultimate Power Profile escondido dos engenheiros Microsoft.", self.toggle_pow, "Powerplan")
        self.sw_srv = self.criar_card_switch(self.scroll_desempenho, 7, 1, "Desempenho", "🔍 SysMain e Search", "Apaga o serviço SysMain e Windows Search, libertando HD mecânico (Prejudica NVME).", self.toggle_srv, "Servicos Windows")
        self.sw_core_park = self.criar_card_switch(self.scroll_desempenho, 7, 2, "Hardware", "🧠 Desativar Core Parking", "Impede a Motherboard de botar os núcleos lógicos para dormir.", self.toggle_core_parking, "Core Parking")

        # MOVIDO PARA A ABA DE DESEMPENHO (Não requer reinício)
        self.sw_hibernacao = self.criar_card_switch(self.scroll_desempenho, 8, 0, "Armazenamento", "Desativar Hibernação", "Desliga a hibernação instantaneamente e apaga o enorme ficheiro hiberfil.sys, libertando GBs no Disco C:.", self.toggle_hibernacao, "Hibernacao", auto=False, reinicio=False)

        # TAB 2: 🌐 REDE & INTERNET
        self.criar_secao(self.scroll_rede, "Internet e Rede Segura", 0)
        self.criar_card_botao(self.scroll_rede, 1, 0, "Diagnóstico", "🌍 Benchmark DNS Global", "Roda pacotes ICPM puros em rotas globais e decide o ping local com Regex Python.", self.benchmark_dns_nativo, btn_texto="TESTAR ROTAS")
        self.criar_card_botao(self.scroll_rede, 1, 1, "Diagnóstico", "📡 Analisar IP e Ping", "Varre a sua placa LAN atrás do seu hostname privado e dispara pra AWS pelo seu IP WAN.", self.analisar_rede_info, btn_texto="INICIAR SCAN")
        self.criar_card_botao(self.scroll_rede, 1, 2, "Rede", "🔌 Redefinir Placa (DNS)", "Dá kill no catálogo Winsock e dá purge via DNS nativo de toda a cache local errada.", self.otimizar_internet, btn_texto="RESET PLACA")

        self.sw_net_thrott = self.criar_card_switch(self.scroll_rede, 2, 0, "Rede", "🔓 Desbloquear Largura", "Coloca Network Throttling Index como 0xFFFFFFFF, anulando a banda limite de Media que tranca a sua conexão.", self.toggle_net_thrott, "Network Throttling")

        # TAB 3: 🛡️ PRIVACIDADE & OS
        self.criar_secao(self.scroll_privacidade, "Privacidade e Segurança", 0)
        self.sw_vs_tel = self.criar_card_switch(self.scroll_privacidade, 1, 0, "Privacidade", "🚫 Telemetria Visual Studio", "Sela a chave oficial (RefuseTelemetry) que proíbe leitura dos dados da máquina.", self.toggle_vs_tel, "VS Telemetry")
        self.sw_tel = self.criar_card_switch(self.scroll_privacidade, 1, 1, "Privacidade", "🕵️ DiagTrack (Rastreamento)", "O serviço Connected User Experiences será forçosamente parado na lista root sc.exe.", self.toggle_tel, "DiagTrack")
        self.sw_nv_priv = self.criar_card_switch(self.scroll_privacidade, 1, 2, "Privacidade", "🛑 Privacidade NVIDIA", "Encerra o container persistente da Nvidia de fundo (OptIn). Drivers farão só gráfico.", self.toggle_nv_priv, "NVIDIA Privacy")
        
        self.sw_loc = self.criar_card_switch(self.scroll_privacidade, 2, 0, "Privacidade", "📍 Localização do Sistema", "A Policy de Georeferenciação passará a negar a comunicação das coordenadas.", self.toggle_loc, "GeoLocation")
        self.sw_tasks = self.criar_card_switch(self.scroll_privacidade, 2, 1, "Segurança", "👻 Tarefas Ocultas (MS)", "As tarefas do CEIP Compatibility Appraiser no Task Scheduler são obliteradas.", self.toggle_telemetry_tasks, "Telemetry Tasks")
        self.criar_card_botao(self.scroll_privacidade, 2, 2, "Segurança", "🔓 Desbloquear Menus Edge", "Arranca da raiz HKLM e HKCU os parâmetros corporativos que bloqueiam opções do Edge.", self.remover_bloqueio_organizacao, btn_texto="DESBLOQUEAR")

        self.criar_secao(self.scroll_privacidade, "Sistema e Interface Visual", 3)
        self.criar_card_botao(self.scroll_privacidade, 4, 0, "Sistema", "📦 Gerir Apps do Windows", "Interface secundária isolada que puxa AppxPackage via Powershell (Debloat).", self.abrir_painel_debloat, btn_texto="ABRIR PAINEL")
        self.criar_card_botao(self.scroll_privacidade, 4, 1, "Sistema", "🚀 Apps de Inicialização", "Chama a URL de Kernel Settings para você desativar boot lag manualmente.", self.abrir_inicializacao, btn_texto="ABRIR GESTOR")
        self.sw_visual_perf = self.criar_card_switch(self.scroll_privacidade, 4, 2, "Interface", "✨ Desempenho Visual Máx.", "Suprime Animações de Ecrã e Efeitos Acrílicos pesadíssimos do gerenciador Desktop.", self.toggle_visual_perf, "Desempenho Visual")

        # TAB 4: 🧹 LIMPEZA
        self.criar_secao(self.scroll_limpeza, "Manutenção e Verificação", 0)
        self.criar_card_botao(self.scroll_limpeza, 1, 0, "Limpeza Profunda", "🗑️ Pasta Temporária Visual", "Abre caminho recursivo na RAM OS.walk Python para deletar lixo eletrônico (TEMP).", self.limpar_temp_nativa, btn_texto="LIMPAR TEMP")
        self.criar_card_botao(self.scroll_limpeza, 1, 1, "Sistema", "🔧 Reparo de Imagem (DISM)", "Janela interativa para acionar Restauration Health global para curar DLLs corrompidos.", self.reparar_imagem_dism, btn_texto="REPARAR")
        self.criar_card_botao(self.scroll_limpeza, 1, 2, "Limpeza", "📜 Limpar Logs de Eventos", "Executa powershell wevtutil el para eliminar até o último vestígio de histórico fantasma.", self.limpar_logs_windows, btn_texto="LIMPAR LOGS")
        
        self.criar_card_botao(self.scroll_limpeza, 2, 0, "Limpeza", "⚡ Arquivos de Prefetch", "Apaga dados de aquecimento de software na inicialização.", self.limpar_prefetch, btn_texto="LIMPAR PREFETCH")
        self.criar_card_botao(self.scroll_limpeza, 2, 1, "Hardware", "🎮 Limpar Cache NVIDIA", "Extermínio da cache base DirectX/OpenGl shader das configurações gráficas.", self.limpar_gpu, btn_texto="LIMPAR SHADERS")
        self.criar_card_botao(self.scroll_limpeza, 2, 2, "Disco", "💽 Limpeza Disco Avançada", "Parametriza nativamente o Sagerun Nível 1 forçado na Cleanmgr interna.", self.limpar_windows, btn_texto="EXECUTAR CLEANMGR")
        
        self.criar_card_botao(self.scroll_limpeza, 3, 0, "Sistema", "🔄 Limpar Windows Update", "Suspende os serviços de rede (Wuauserv) para raspar arquivos gigantes mortos.", self.limpar_update, btn_texto="LIMPAR UPDATES")
        self.criar_card_botao(self.scroll_limpeza, 3, 1, "Interface", "🖼️ Limpar Miniaturas", "Destrói e recria o ecossistema visual explorer.exe para aniquilar bases .db Thumbnails.", self.limpar_thumbnails, btn_texto="LIMPAR ÍCONES")
        self.criar_card_botao(self.scroll_limpeza, 3, 2, "Disco", "⚙️ Otimizar Unidades", "Desfragmenta Mecânicos C O U e lança sinal Retrim aos seus discos em estado Sólido (SSD).", self.otimizar_discos, btn_texto="OTIMIZAR DISCOS")

        self.criar_secao(self.scroll_limpeza, "Ofuscação e Limpeza de Aplicações", 4)
        self.criar_card_botao(self.scroll_limpeza, 5, 0, "Navegador", "🌐 Exterminar Cache Google", "Corta caminho até UserData Chrome e liberta massas pesadas sem perder as senhas.", self.limpar_chrome, btn_texto="LIMPAR CHROME")
        self.criar_card_botao(self.scroll_limpeza, 5, 1, "Navegador", "🌐 Exterminar Cache Edge", "Apaga integralmente vestígios da Microsoft Edge Cache.", self.limpar_edge, btn_texto="LIMPAR EDGE")
        self.criar_card_botao(self.scroll_limpeza, 5, 2, "Navegador", "🦊 Limpar Mozilla Firefox", "Script inteligente Regex powershell limpa todos os perfis isolados (Cache2).", self.limpar_firefox, btn_texto="LIMPAR FIREFOX")

        self.criar_card_botao(self.scroll_limpeza, 6, 0, "Navegador", "🔴 Limpar Opera / GX", "Corta conexões duplas. Apaga Stable Padrão e Opera GX Padrão.", self.limpar_opera, btn_texto="LIMPAR OPERA")
        self.criar_card_botao(self.scroll_limpeza, 6, 1, "Aplicativo", "🎮 Limpar Cache Steam", "Fecha o Steam client em boot e raspa a Store Cache (.vdf). Conserta bugs de update.", self.limpar_steam, btn_texto="LIMPAR STEAM")
        self.criar_card_botao(self.scroll_limpeza, 6, 2, "Aplicativo", "💬 Limpar Cache Discord", "Esmaga processos Discord.exe e varre a pasta Roaming para matar Media corrompida.", self.limpar_discord, btn_texto="LIMPAR DISCORD")
        
        self.criar_card_botao(self.scroll_limpeza, 7, 0, "Aplicativo", "🎵 Limpar Cache Spotify", "Mata processo de Áudio e limpa GBs criados pelas playlists guardadas Offline.", self.limpar_spotify, btn_texto="LIMPAR SPOTIFY")
        self.criar_card_botao(self.scroll_limpeza, 7, 1, "Aplicativo", "⚔️ Limpar Battle.net", "Impede Agent.exe de rodar oculto e detona atualizações presas de jogos Blizzard.", self.limpar_battlenet, btn_texto="LIMPAR BNET")
        self.criar_card_botao(self.scroll_limpeza, 7, 2, "Geral", "💥 Limpeza Total (Apps)", "Função master Berserker para assassinar simultaneamente as árvores de aplicativos.", self.limpar_apps_multi, btn_texto="DESTRUIR TUDO")

        # TAB 5: ⚙️ Root (scroll_root)
        self.criar_secao(self.scroll_root, "Comandos de Root (Requer Reiniciar o Computador)", 0)
        self.sw_mouse = self.criar_card_switch(self.scroll_root, 1, 0, "Hardware", "🖱️ Mira Perfeita (Raw Mouse)", "Elimina 3 curvas de aceleração de rastreio. Mexa 1 pra 1 real na tela.", self.toggle_mouse, "Raw Mouse", auto=False, reinicio=True)
        self.sw_mnu = self.criar_card_switch(self.scroll_root, 1, 1, "Interface", "📋 Menu Clássico Win11", "Mata a injeção do UI Framework Moderno Win11. Exibe a velha aba tradicional gigante.", self.toggle_mnu, "Menu Clássico", auto=False, reinicio=True)
        self.sw_bmn = self.criar_card_switch(self.scroll_root, 1, 2, "Sistema", "⏳ Espera de Boot (2 Seg)", "Substitui os pesados 30s timeout do BCD Loader.", self.toggle_bmn, "Boot Menu", auto=False, reinicio=True)
        
        self.sw_fast_start = self.criar_card_switch(self.scroll_root, 2, 0, "Sistema", "💤 Desativar Fast Startup", "Hibernação Híbrida: Extermínio direto no Kernel HiberbootEnabled.", self.toggle_fast_startup, "Fast Startup", auto=False, reinicio=True)
        self.sw_widgets = self.criar_card_switch(self.scroll_root, 2, 1, "Interface", "📰 Desativar Widgets", "Corta os processos laterais pesados AllowNewsAndInterests (Microsoft EdgeWebView).", self.toggle_widgets, "Widgets", auto=False, reinicio=True)
        
        self.criar_card_botao(self.scroll_root, 3, 0, "Sistema", "🔍 Verificação SFC Scan", "Cria interface independente em CMD para visualizar progresso da auditoria local nativa.", self.verificar_erros, reinicio=True, btn_texto="SFC SCAN")
        self.criar_card_botao(self.scroll_root, 3, 1, "Sistema", "💽 Verificar Discos (CHKDSK)", "Mapeador em Python que rastreia Hard Disks sem mexer nas partições inválidas.", self.verificar_disco, reinicio=True, btn_texto="RODAR CHKDSK")
        
        self.atualizar_cores_perfis()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = MeuOtimizador()
    app.mainloop()
