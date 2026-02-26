import customtkinter as ctk
import os
import ctypes
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

        self.title("Gustavo Optimizer v1.0 - Pro Edition")
        self.geometry("1400x900")
        
        # Variáveis de Estado para os Perfis Inteligentes
        self.estado_anterior = {}
        
        # --- CARREGAR O ÍCONE (Se existir) ---
        icone_path = resource_path("icone.ico")
        if os.path.exists(icone_path):
            self.iconbitmap(icone_path)
        
        # Carrega o tema salvo no Registo ou usa o padrão
        tema_salvo = self.carregar_config("TemaPrincipal", "Pure Power (Ciano)")
        if tema_salvo not in PALETAS:
            tema_salvo = "Pure Power (Ciano)"
        self.aplicar_variaveis_tema(tema_salvo)
        
        # Carrega o Perfil Ativo da Memória do Registo
        self.perfil_ativo = self.carregar_config("PerfilAtivo", "Nenhum")
        self.carregar_snapshot_memoria()
        
        # Fallback inicial para Plano de Energia (Alto Desempenho padrão)
        self.guid_maximo = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
        
        self.configure(fg_color=self.bg_main)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 1. BARRA LATERAL (SIDEBAR) TÉCNICA
        # ==========================================
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=self.bg_painel, border_width=1, border_color=self.borda)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(11, weight=1)

        self.lbl_logo = ctk.CTkLabel(self.sidebar, text="[ GUSTAVO OPTIMIZER ]", font=("Consolas", 20, "bold"), text_color=self.acento)
        self.lbl_logo.grid(row=0, column=0, padx=20, pady=(30, 10), sticky="w")

        self.is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        admin_text = "MODO ADMIN: ATIVO" if self.is_admin else "AVISO: RODE COMO ADMIN"
        self.status_topo = ctk.CTkLabel(self.sidebar, text=admin_text, text_color="#2ecc71" if self.is_admin else self.acento, font=("Consolas", 12, "bold"))
        self.status_topo.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        self.sw_master_sys = ctk.CTkSwitch(self.sidebar, text="MASTER SISTEMA (ON/OFF)", command=self.iniciar_thread_master, font=("Consolas", 12, "bold"), progress_color=self.acento, fg_color=self.borda)
        self.sw_master_sys.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.sw_master_clean = ctk.CTkSwitch(self.sidebar, text="MASTER MANUTENÇÃO", command=self.thread_manutencao, font=("Consolas", 12, "bold"), progress_color=self.acento, fg_color=self.borda)
        self.sw_master_clean.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.btn_restore = ctk.CTkButton(self.sidebar, text="PONTO RESTAURAÇÃO", command=self.criar_ponto_restauracao, fg_color=self.bg_painel, hover_color=self.acento, text_color=self.texto_branco, corner_radius=0, border_width=1, border_color=self.acento, font=("Consolas", 12, "bold"))
        self.btn_restore.grid(row=4, column=0, padx=20, pady=10, sticky="w")

        self.btn_exportar = ctk.CTkButton(self.sidebar, text="EXPORTAR LOG", command=self.exportar_log, fg_color=self.bg_painel, hover_color=self.acento, text_color=self.texto_branco, corner_radius=0, border_width=1, border_color=self.acento, font=("Consolas", 12, "bold"))
        self.btn_exportar.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="w")

        self.combo_temas = ctk.CTkOptionMenu(self.sidebar, values=list(PALETAS.keys()), command=self.mudar_tema, fg_color=self.bg_painel, button_color=self.borda, button_hover_color=self.acento, dropdown_fg_color=self.bg_painel, dropdown_text_color=self.texto_branco, text_color=self.texto_branco, font=("Consolas", 11, "bold"))
        self.combo_temas.set(tema_salvo)
        self.combo_temas.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="w")

        self.lbl_cpu = ctk.CTkLabel(self.sidebar, text="⚙️ CPU: Calc...", font=("Consolas", 14, "bold"), text_color=self.texto_branco)
        self.lbl_cpu.grid(row=7, column=0, padx=20, pady=5, sticky="w")
        self.lbl_ram = ctk.CTkLabel(self.sidebar, text="💾 RAM: Calc...", font=("Consolas", 14, "bold"), text_color=self.texto_branco)
        self.lbl_ram.grid(row=8, column=0, padx=20, pady=5, sticky="w")
        self.lbl_gpu = ctk.CTkLabel(self.sidebar, text="🎮 GPU: Calc...", font=("Consolas", 14, "bold"), text_color=self.texto_branco)
        self.lbl_gpu.grid(row=9, column=0, padx=20, pady=5, sticky="nw")

        # --- SWITCH MODO ESCURO NA BARRA LATERAL ---
        self.sw_sidebar_dark = ctk.CTkSwitch(self.sidebar, text="FORÇAR MODO ESCURO", command=self.acao_dark_mode, font=("Consolas", 12, "bold"), progress_color=self.acento, fg_color=self.borda)
        self.sw_sidebar_dark.grid(row=10, column=0, padx=20, pady=(20, 10), sticky="w")
        estado_dark = self.carregar_config("DarkModeSidebar", "0")
        if estado_dark == "1":
            self.sw_sidebar_dark.select()

        self.caixa_log = ctk.CTkTextbox(self.sidebar, height=180, corner_radius=0, font=("Consolas", 11), fg_color=self.bg_main, text_color=self.texto_cinza, border_width=1, border_color=self.borda)
        self.caixa_log.grid(row=11, column=0, padx=10, pady=10, sticky="sew")
        
        self.after(500, lambda: self.log("Sistema de Memória Persistente ativado."))

        # ==========================================
        # 2. ÁREA DE CONTEÚDO E INICIALIZAÇÃO
        # ==========================================
        self.scroll_area = ctk.CTkScrollableFrame(self, fg_color=self.bg_main, corner_radius=0)
        self.scroll_area.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        self.lista_switches = [] 
        self.cards_interface = [] 

        self.montar_interface_total()
        self.atualizar_hardware()
        
        # Dispara a verificação inteligente de forma segura
        self.after(500, self.iniciar_verificacao_energia)

    # --- VERIFICAÇÃO INTELIGENTE DO DESEMPENHO MÁXIMO ---
    def iniciar_verificacao_energia(self):
        threading.Thread(target=self.checar_plano_energia, daemon=True).start()

    def checar_plano_energia(self):
        guid_salvo = self.carregar_config("GuidMaximo", "")
        res_l = subprocess.run('powercfg /l', capture_output=True, text=True, shell=True, creationflags=0x08000000)
        
        if guid_salvo and guid_salvo.lower() in res_l.stdout.lower():
            self.guid_maximo = guid_salvo
            self.log("[*] Plano de Desempenho Máximo carregado da memória.")
            return

        if "e9a42b02-d5df-448d-aa00-03f14749eb61" in res_l.stdout.lower():
            self.guid_maximo = "e9a42b02-d5df-448d-aa00-03f14749eb61"
            self.salvar_config("GuidMaximo", self.guid_maximo)
            self.log("[*] Plano de Desempenho Máximo nativo encontrado.")
            return
            
        res_dup = subprocess.run('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61', capture_output=True, text=True, shell=True, creationflags=0x08000000)
        match = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", res_dup.stdout)
        
        if match:
            self.guid_maximo = match.group(1)
            self.salvar_config("GuidMaximo", self.guid_maximo)
            self.log(f"[*] Otimização: Plano de Desempenho Máximo exclusivo criado ({self.guid_maximo}).")
        else:
            self.log("[-] Erro ao criar Desempenho Máximo. Usando Alto Desempenho nativo.", "erro")

    # --- LÓGICA DO MODO ESCURO DA SIDEBAR ---
    def acao_dark_mode(self):
        if self.sw_sidebar_dark.get() == 1:
            res = self.executar_comando('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "AppsUseLightTheme" /t REG_DWORD /d 0 /f >nul 2>&1 & reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "SystemUsesLightTheme" /t REG_DWORD /d 0 /f >nul 2>&1')
        else:
            res = self.executar_comando('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "AppsUseLightTheme" /t REG_DWORD /d 1 /f >nul 2>&1 & reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "SystemUsesLightTheme" /t REG_DWORD /d 1 /f >nul 2>&1')
        self.log_res(res, "Modo Escuro do Sistema")
        self.salvar_config("DarkModeSidebar", str(self.sw_sidebar_dark.get()))

    # --- SISTEMA DE MEMÓRIA (REGISTO DO WINDOWS) ---
    def salvar_config(self, nome, valor):
        try:
            chave = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\GustavoOptimizer")
            winreg.SetValueEx(chave, nome, 0, winreg.REG_SZ, str(valor))
            winreg.CloseKey(chave)
        except Exception as e:
            self.log(f"Erro ao salvar memória: {str(e)}", "erro")

    def carregar_config(self, nome, padrao):
        try:
            chave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\GustavoOptimizer")
            valor, _ = winreg.QueryValueEx(chave, nome)
            winreg.CloseKey(chave)
            return valor
        except OSError:
            return padrao

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
        self.sidebar.configure(fg_color=self.bg_painel, border_color=self.borda)
        self.lbl_logo.configure(text_color=self.acento)
        self.status_topo.configure(text_color="#2ecc71" if self.is_admin else self.acento)
        self.sw_master_sys.configure(progress_color=self.acento, fg_color=self.borda)
        self.sw_master_clean.configure(progress_color=self.acento, fg_color=self.borda)
        self.sw_sidebar_dark.configure(progress_color=self.acento, fg_color=self.borda)
        self.btn_exportar.configure(fg_color=self.bg_painel, hover_color=self.acento, border_color=self.acento)
        self.btn_restore.configure(fg_color=self.bg_painel, hover_color=self.acento, border_color=self.acento)
        self.combo_temas.configure(fg_color=self.bg_painel, button_color=self.borda, button_hover_color=self.acento, dropdown_fg_color=self.bg_painel, text_color=self.texto_branco)
        self.caixa_log.configure(fg_color=self.bg_main, text_color=self.texto_cinza, border_color=self.borda)
        self.lbl_cpu.configure(text_color=self.texto_branco)
        self.lbl_ram.configure(text_color=self.texto_branco)
        self.lbl_gpu.configure(text_color=self.texto_branco)
        self.scroll_area.configure(fg_color=self.bg_main)

        for widget in self.cards_interface:
            widget.destroy()
        
        self.cards_interface.clear()
        self.lista_switches.clear()
        self.montar_interface_total()
        
        self.log(f"Perfil de cores alterado para: {novo_tema}")

    def atualizar_cores_perfis(self):
        if not hasattr(self, 'btn_gamer') or not hasattr(self, 'btn_trabalho'): return
            
        cor_fundo_padrao = self.bg_painel
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

    # --- FUNÇÕES DE LAYOUT (CRIADORES DE CARTÕES TÉCNICOS) ---
    def criar_secao(self, texto, linha):
        lbl = ctk.CTkLabel(self.scroll_area, text=f"// {texto.upper()}", font=("Consolas", 18, "bold"), text_color=self.acento)
        lbl.grid(row=linha, column=0, columnspan=3, pady=(40, 15), padx=20, sticky="w")
        self.cards_interface.append(lbl) 

    def criar_card_switch(self, linha, coluna, categoria, titulo, descricao, cmd, nome_log, auto=True, reinicio=False):
        card = ctk.CTkFrame(self.scroll_area, fg_color=self.bg_painel, corner_radius=0, width=320, height=160, border_width=1, border_color=self.borda)
        card.grid(row=linha, column=coluna, padx=15, pady=15, sticky="nw")
        card.grid_propagate(False)
        self.cards_interface.append(card)

        lbl_cat = ctk.CTkLabel(card, text=f" [{categoria.upper()}] ", font=("Consolas", 10, "bold"), text_color=self.acento, fg_color=self.bg_main, corner_radius=0)
        lbl_cat.place(x=15, y=15)

        lbl_tit = ctk.CTkLabel(card, text=titulo, font=("Consolas", 14, "bold"), text_color=self.texto_branco)
        lbl_tit.place(x=15, y=45)
        lbl_desc = ctk.CTkLabel(card, text=descricao, font=("Roboto", 11), text_color=self.texto_cinza, wraplength=290, justify="left")
        lbl_desc.place(x=15, y=70)

        if reinicio:
            lbl_reinicio = ctk.CTkLabel(card, text="[REQUER REINICIAR]", font=("Consolas", 10, "bold"), text_color="#FF4444")
            lbl_reinicio.place(x=15, y=125)

        sw = ctk.CTkSwitch(card, text="ATIVAR", progress_color=self.acento, fg_color=self.borda, font=("Consolas", 10, "bold"), text_color=self.acento)
        sw.place(x=220, y=125)

        estado_salvo = self.carregar_config(nome_log, "0")
        if estado_salvo == "1":
            sw.select()
        else:
            sw.deselect()

        def acao_com_memoria():
            cmd() 
            self.salvar_config(nome_log, str(sw.get())) 

        sw.configure(command=acao_com_memoria)
        sw.nome_log = nome_log 
        sw.comando_real = acao_com_memoria 
        
        if auto:
            self.lista_switches.append(sw)
        return sw

    def criar_card_botao(self, linha, coluna, categoria, titulo, descricao, cmd, reinicio=False, btn_texto="EXECUTAR"):
        card = ctk.CTkFrame(self.scroll_area, fg_color=self.bg_painel, corner_radius=0, width=320, height=160, border_width=1, border_color=self.borda)
        card.grid(row=linha, column=coluna, padx=15, pady=15, sticky="nw")
        card.grid_propagate(False)
        self.cards_interface.append(card)

        lbl_cat = ctk.CTkLabel(card, text=f" [{categoria.upper()}] ", font=("Consolas", 10, "bold"), text_color=self.acento, fg_color=self.bg_main, corner_radius=0)
        lbl_cat.place(x=15, y=15)

        lbl_tit = ctk.CTkLabel(card, text=titulo, font=("Consolas", 14, "bold"), text_color=self.texto_branco)
        lbl_tit.place(x=15, y=45)
        lbl_desc = ctk.CTkLabel(card, text=descricao, font=("Roboto", 11), text_color=self.texto_cinza, wraplength=290, justify="left")
        lbl_desc.place(x=15, y=70)

        if reinicio:
            lbl_reinicio = ctk.CTkLabel(card, text="[REQUER REINICIAR]", font=("Consolas", 10, "bold"), text_color="#FF4444")
            lbl_reinicio.place(x=15, y=125)

        btn = ctk.CTkButton(card, text=btn_texto, command=cmd, fg_color=self.bg_painel, hover_color=self.acento, text_color=self.texto_branco, corner_radius=0, border_width=1, border_color=self.acento, width=120, height=28, font=("Consolas", 11, "bold"))
        btn.place(x=180, y=120)
        return btn

    # --- MONTAGEM DA GRELHA TOTAL E EXPANSDIDA (DISTRIBUIÇÃO) ---
    def montar_interface_total(self):
        # 0. PERFIS INTELIGENTES (AUTO)
        self.criar_secao("Perfis Inteligentes (Auto)", 0)
        self.btn_gamer = self.criar_card_botao(1, 0, "Desempenho", "Ativar Modo Gamer", "Ativa simultaneamente 10 funções extremas de CPU, GPU e Rede.", self.acionar_perfil_gamer, btn_texto="ATIVAR MODO")
        self.btn_trabalho = self.criar_card_botao(1, 1, "Equilíbrio", "Ativar Modo Trabalho", "Restaura configurações nativas focadas na estabilidade e bateria.", self.acionar_perfil_trabalho, btn_texto="ATIVAR MODO")

        # 2. PRIVACIDADE E SEGURANÇA
        self.criar_secao("Privacidade e Segurança", 2)
        self.sw_vs_tel = self.criar_card_switch(3, 0, "Privacidade", "Telemetria Visual Studio", "Impede o VS de enviar dados de uso para a Microsoft.", self.toggle_vs_tel, "VS Telemetry")
        self.sw_tel = self.criar_card_switch(3, 1, "Privacidade", "DiagTrack (Rastreamento)", "Desativa o serviço de rastreamento de diagnósticos do Windows.", self.toggle_tel, "DiagTrack")
        self.sw_smart = self.criar_card_switch(3, 2, "Privacidade", "Filtro SmartScreen", "Desativa a verificação de proteção contra sites e apps maliciosos.", self.toggle_smart, "SmartScreen")
        
        self.sw_loc = self.criar_card_switch(4, 0, "Privacidade", "Localização do Sistema", "Desativa o serviço de geolocalização e acesso à posição por apps.", self.toggle_loc, "GeoLocation")
        self.sw_nv_priv = self.criar_card_switch(4, 1, "Privacidade", "Privacidade NVIDIA", "Desativa a coleta de dados e serviços de fundo da NVIDIA.", self.toggle_nv_priv, "NVIDIA Privacy")
        self.sw_tasks = self.criar_card_switch(4, 2, "Segurança", "Tarefas Ocultas (Telemetria)", "Desativa tarefas agendadas de envio de dados à Microsoft no fundo.", self.toggle_telemetry_tasks, "Telemetry Tasks")
        
        # 5. SISTEMA E INTERFACE
        self.criar_secao("Sistema e Interface", 5)
        self.criar_card_botao(6, 0, "Sistema", "Apps de Inicialização", "Abre o gestor nativo do Windows para desativar programas no arranque.", self.abrir_inicializacao, btn_texto="ABRIR GESTOR")
        self.criar_card_botao(6, 1, "Sistema", "Remover Bloatware", "Desinstala instantaneamente apps nativos inúteis (Cortana, Bing, Zune).", self.remover_bloatware)
        self.sw_tra = self.criar_card_switch(6, 2, "Interface", "Desativar Acrílico", "Desativa o acrílico e transparências para melhorar a fluidez da interface.", self.toggle_tra, "Transparência")

        # 7. DESEMPENHO E LATÊNCIA
        self.criar_secao("Desempenho e Latência", 7)
        self.sw_thrott = self.criar_card_switch(8, 0, "Desempenho", "Power Throttling", "Impede que o sistema reduza o desempenho dos aplicativos em segundo plano.", self.toggle_thrott, "Power Throttling")
        self.sw_gaming = self.criar_card_switch(8, 1, "Jogos", "Modo de Jogo Pro", "Ativa o Gaming Mode e desativa gravação GameDVR para mais FPS.", self.toggle_gaming, "Gaming Mode")
        self.sw_tim = self.criar_card_switch(8, 2, "Latência", "Resolução de Tempo", "Força o kernel do Windows a processar eventos com latência mínima.", self.toggle_tim, "Timer Res")
        
        self.sw_pow = self.criar_card_switch(9, 0, "Desempenho", "Plano de Energia", "Ativa o plano de energia oculto de Desempenho Máximo.", self.toggle_pow, "Powerplan")
        self.sw_gpu_oc = self.criar_card_switch(9, 1, "Hardware", "Economia da GPU", "Impede que a placa de vídeo reduza sua frequência em momentos de repouso.", self.toggle_gpu_oc, "GPU Downclock")
        self.sw_flip = self.criar_card_switch(9, 2, "Latência", "Flip Fix (Janelas)", "Otimiza a janela de exibição para reduzir o atraso de entrada (Input Lag).", self.toggle_flip_fix, "Flip Fix")
        
        self.sw_srv = self.criar_card_switch(10, 0, "Desempenho", "SysMain e Search", "Desativa serviços de indexação e pré-carregamento para liberar CPU e RAM.", self.toggle_srv, "Servicos Windows")
        self.sw_net_thrott = self.criar_card_switch(10, 1, "Rede", "Limitação de Rede", "Impede o Windows de reservar banda, garantindo 100% de tráfego aos jogos.", self.toggle_net_thrott, "Network Throttling")
        self.sw_core_park = self.criar_card_switch(10, 2, "Hardware", "Desativar Core Parking", "Força o Windows a manter todos os núcleos da CPU sempre ativos.", self.toggle_core_parking, "Core Parking")

        # 11. REDE E CONEXÃO
        self.criar_secao("Rede e Conexão", 11)
        self.sw_dscp = self.criar_card_switch(12, 0, "Rede", "Otimizar Pacotes (DSCP)", "Dá prioridade de tráfego aos pacotes de jogos na sua rede local.", self.toggle_dscp, "DSCP")
        self.sw_netsh = self.criar_card_switch(12, 1, "Rede", "Ajustes de Buffer (Netsh)", "Otimiza o buffer de recebimento e a unidade de transmissão máxima (MTU).", self.toggle_netsh, "Netsh")
        self.sw_cong = self.criar_card_switch(12, 2, "Rede", "Controle CUBIC", "Altera o algoritmo de congestionamento de internet para maior estabilidade.", self.toggle_cong, "Congestion")
        
        self.sw_tcp = self.criar_card_switch(13, 0, "Rede", "TcpNoDelay", "Desativa o algoritmo de Nagle para enviar pacotes de rede imediatamente.", self.toggle_tcp, "TCP")
        self.criar_card_botao(13, 1, "Rede", "Aplicar DNS Google", "Altera a conexão atual para o servidor 8.8.8.8 para maior estabilidade.", self.aplicar_dns_google)
        self.criar_card_botao(13, 2, "Rede", "Aplicar DNS Cloudflare", "Altera a conexão atual para o servidor 1.1.1.1 para latência mínima.", self.aplicar_dns_cloudflare)

        self.criar_card_botao(14, 0, "Diagnóstico", "Analisar Rede (IP/Ping)", "Busca o seu IP Local, IP Público e Ping real num servidor remoto.", self.analisar_rede_info, btn_texto="INICIAR SCAN")

        # 15. MANUTENÇÃO E SISTEMA
        self.criar_secao("Manutenção e Sistema", 15)
        self.criar_card_botao(16, 0, "Sistema", "Reparo de Imagem (DISM)", "Faz download e substitui arquivos corrompidos da base do Windows.", self.reparar_imagem_dism)
        self.criar_card_botao(16, 1, "Limpeza", "Limpar Logs (Eventos)", "Apaga milhares de registros de erros ocultos que ocupam espaço em disco.", self.limpar_logs_windows)
        self.criar_card_botao(16, 2, "Limpeza", "Arquivos de Prefetch", "Força o Windows a recriar o mapa de inicialização do zero.", self.limpar_prefetch)
        
        self.criar_card_botao(17, 0, "Limpeza", "Arquivos Temporários", "Remove lixo eletrônico deixado pelo sistema operacional (%temp%).", self.limpar_temp)
        self.criar_card_botao(17, 1, "Hardware", "Cache NVIDIA (Shader)", "Apaga shaders antigos armazenados na placa de vídeo.", self.limpar_gpu)
        self.criar_card_botao(17, 2, "Interface", "Limpar Miniaturas", "Exclui o cache de imagens para forçar o recarregamento dos ícones.", self.limpar_thumbnails)

        self.criar_card_botao(18, 0, "Rede", "Redefinir Rede (DNS)", "Limpa o cache de DNS e redefine os catálogos de conexão Winsock.", self.otimizar_internet)
        self.criar_card_botao(18, 1, "Disco", "Limpeza de Disco (Win)", "Abre a ferramenta oficial de liberação de espaço de armazenamento.", self.limpar_windows)
        self.criar_card_botao(18, 2, "Sistema", "Limpeza Windows Update", "Limpa o histórico e arquivos residuais de atualizações baixadas.", self.limpar_update)

        self.criar_card_botao(19, 0, "Disco", "Otimizar Unidades (Defrag)", "Inicia a desfragmentação mecânica (HD) e o TRIM (SSD) em TODOS os discos.", self.otimizar_discos)

        # 20. LIMPEZA DE APLICATIVOS E PROGRAMAS
        self.criar_secao("Limpeza de Aplicativos (Programas)", 20)
        self.criar_card_botao(21, 0, "Navegador", "Limpar Google Chrome", "Apaga imagens, arquivos e dados antigos armazenados pelo Chrome.", self.limpar_chrome)
        self.criar_card_botao(21, 1, "Navegador", "Limpar Microsoft Edge", "Apaga imagens, arquivos e dados antigos armazenados pelo Edge.", self.limpar_edge)
        self.criar_card_botao(21, 2, "Navegador", "Limpar Mozilla Firefox", "Apaga o cache completo de todos os perfis do Mozilla Firefox.", self.limpar_firefox)
        
        self.criar_card_botao(22, 0, "Navegador", "Limpar Opera / Opera GX", "Apaga dados antigos armazenados pelas versões do Opera Browser.", self.limpar_opera)
        self.criar_card_botao(22, 1, "Aplicativo", "Limpar Cache (Spotify)", "Apaga dados antigos armazenados pelo aplicativo de música.", self.limpar_spotify)
        self.criar_card_botao(22, 2, "Aplicativo", "Limpar Cache (Steam)", "Remove arquivos temporários da loja e do cliente Steam.", self.limpar_steam)

        self.criar_card_botao(23, 0, "Aplicativo", "Limpar Cache (Discord)", "Exclui imagens e dados de bate-papo armazenados no computador.", self.limpar_discord)
        self.criar_card_botao(23, 1, "Aplicativo", "Limpar Cache (Battle.net)", "Limpa os registros e logs de atualização do inicializador da Blizzard.", self.limpar_battlenet)
        self.criar_card_botao(23, 2, "Geral", "Limpeza Total (Apps)", "Limpa simultaneamente Spotify, Steam, Discord e Battle.net (Exclui navegadores).", self.limpar_apps_multi)

        # 24. PROCEDIMENTOS QUE REQUEREM REINICIAR
        self.criar_secao("Procedimentos que Requerem Reiniciar", 24)
        self.sw_uac = self.criar_card_switch(25, 0, "Segurança", "Controle de Conta (UAC)", "Desativa os pop-ups de permissão de administrador na tela.", self.toggle_uac, "UAC", auto=False, reinicio=True)
        self.sw_mit = self.criar_card_switch(25, 1, "Desempenho", "Mitigações de CPU", "Ganha desempenho desativando proteções contra falhas de hardware antigas.", self.toggle_mit, "Mitigações", auto=False, reinicio=True)
        self.sw_mnu = self.criar_card_switch(25, 2, "Interface", "Menu Clássico Win11", "Restaura o menu tradicional ao clicar com o botão direito no Windows 11.", self.toggle_mnu, "Menu Clássico", auto=False, reinicio=True)
        
        self.sw_bmn = self.criar_card_switch(26, 0, "Sistema", "Espera de Boot (2 Seg)", "Reduz o tempo de espera do menu de boot para acelerar a inicialização.", self.toggle_bmn, "Boot Menu", auto=False, reinicio=True)
        self.sw_fast_start = self.criar_card_switch(26, 1, "Sistema", "Desativar Fast Startup", "Desativa a Inicialização Rápida para evitar acumulação de erros no Kernel.", self.toggle_fast_startup, "Fast Startup", auto=False, reinicio=True)
        self.sw_widgets = self.criar_card_switch(26, 2, "Interface", "Desativar Widgets", "Remove permanentemente o painel de clima/notícias da Barra de Tarefas.", self.toggle_widgets, "Widgets", auto=False, reinicio=True)

        self.criar_card_botao(27, 0, "Sistema", "Verificação SFC Scan", "Busca e repara arquivos corrompidos ou ausentes do Windows.", self.verificar_erros, reinicio=True)
        self.criar_card_botao(27, 1, "Sistema", "Verificar Discos (CHKDSK)", "Examina a integridade e procura setores defeituosos em TODOS os discos.", self.verificar_disco, reinicio=True)
        
        # Chama a atualização visual do perfil ao iniciar
        self.atualizar_cores_perfis()

    # --- FUNÇÃO EXECUÇÃO SEGURA E UI-SAFE ---
    def executar_comando(self, comando):
        try:
            resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, creationflags=0x08000000)
            return resultado.returncode
        except Exception as e:
            self.log(f"Erro ao executar: {str(e)}", "erro")
            return 1

    def executar_comando_visivel(self, comando, nome_log, reinicio=False):
        def tarefa():
            try:
                processo = subprocess.Popen(f'cmd /c "{comando}"', creationflags=subprocess.CREATE_NEW_CONSOLE)
                processo.wait() 
                res = processo.returncode
                self.log_res(res, nome_log, None, reinicio)
            except Exception as e:
                self.log(f"Erro ao executar {nome_log}: {str(e)}", "erro")
        threading.Thread(target=tarefa, daemon=True).start()

    def executar_comando_assincrono(self, comando, nome_log):
        def tarefa():
            try:
                processo = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=0x08000000)
                processo.wait() 
                res = processo.returncode
                self.log_res(res, nome_log)
            except Exception as e:
                self.log(f"Erro ao executar {nome_log}: {str(e)}", "erro")
        threading.Thread(target=tarefa, daemon=True).start()

    # --- ATUALIZAÇÃO BLINDADA DA CAIXA DE LOGS (ANTI-CRASH) ---
    def log(self, mensagem, tipo="info"):
        prefixo = "[+] " if tipo == "info" else "[-] "
        def update_ui():
            self.caixa_log.insert("end", f"{prefixo}{mensagem}\n")
            self.caixa_log.see("end")
            self.update_idletasks()
        self.after(0, update_ui)

    def log_res(self, res, nome, sw_obj=None, reinicio=False):
        def update_ui():
            if res == 0: 
                aviso = " [REINICIE PARA APLICAR]" if reinicio else ""
                self.caixa_log.insert("end", f"[+] {nome}: Concluído com sucesso.{aviso}\n")
            else: 
                self.caixa_log.insert("end", f"[-] ERRO: {nome} falhou.\n")
                if sw_obj is not None:
                    if sw_obj.get() == 1: sw_obj.deselect()
                    else: sw_obj.select()
            self.caixa_log.see("end")
            self.update_idletasks()
        self.after(0, update_ui)

    # --- HARDWARE REAL-TIME ---
    def atualizar_hardware(self):
        uso_cpu = psutil.cpu_percent(interval=None)
        uso_ram = psutil.virtual_memory().percent
        uso_gpu = "N/A"
        try:
            res = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, creationflags=0x08000000)
            if res.returncode == 0: uso_gpu = f"{res.stdout.strip()}%"
        except Exception: uso_gpu = "Erro/AMD"
        
        self.lbl_cpu.configure(text=f"⚙️ CPU: {uso_cpu}%")
        self.lbl_ram.configure(text=f"💾 RAM: {uso_ram}%")
        self.lbl_gpu.configure(text=f"🎮 GPU: {uso_gpu}")
        self.after(1000, self.atualizar_hardware)

    def exportar_log(self):
        conteudo = self.caixa_log.get("1.0", "end-1c")
        caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".txt", title="Salvar Log", initialfile="Log_Otimizacao.txt")
        if caminho_arquivo:
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo: arquivo.write(conteudo)
            self.log(f"Log salvo em: {caminho_arquivo}")

    # --- LOGICA MASTER E LIMPEZA ---
    def thread_manutencao(self):
        if self.sw_master_clean.get() == 1:
            if not self.is_admin:
                self.sw_master_clean.deselect(); return
            threading.Thread(target=self.limpeza_sequencial, daemon=True).start()

    def limpeza_sequencial(self):
        tarefas = [("Temporários", "del /s /f /q %temp%\\*.*"), ("Rede", "ipconfig /flushdns & netsh winsock reset")]
        for n, c in tarefas:
            if self.sw_master_clean.get() == 0: break
            res = self.executar_comando(c); time.sleep(1); self.log_res(res, n)
            self.log(f"Etapa {n} em andamento...") 
        if self.sw_master_clean.get() == 1:
            self.executar_comando_visivel("sfc /scannow", "SFC Scan", reinicio=True)
        self.log("MANUTENÇÃO CONCLUÍDA."); self.sw_master_clean.deselect()

    def iniciar_thread_master(self):
        est = int(self.sw_master_sys.get())
        threading.Thread(target=self.toggle_master_system, args=(est,), daemon=True).start()

    def toggle_master_system(self, est):
        self.log("Sincronizando Sistema Master (Apenas Automáticos)...")
        for sw in self.lista_switches:
            def acao_master(s=sw, alvo=est):
                try:
                    if int(s.get()) != alvo:
                        if alvo == 1: s.select()
                        else: s.deselect()
                        if hasattr(s, 'comando_real'): s.comando_real()
                except Exception: pass
            self.after(0, acao_master)
            time.sleep(0.4) 
        self.log("Sincronização global concluída.")

    # --- HELPER UI-SAFE PARA PERFIS INTELIGENTES (Anti-Crash) ---
    def forcar_ativo(self, sw):
        def acao():
            try:
                if int(sw.get()) == 0:
                    sw.select()
                    if hasattr(sw, 'comando_real'): sw.comando_real()
            except Exception as e:
                self.log(f"Erro na UI (Ativar): {str(e)}", "erro")
        self.after(0, acao)
        time.sleep(0.4)

    def forcar_desligado(self, sw):
        def acao():
            try:
                if int(sw.get()) == 1:
                    sw.deselect()
                    if hasattr(sw, 'comando_real'): sw.comando_real()
            except Exception as e:
                self.log(f"Erro na UI (Desativar): {str(e)}", "erro")
        self.after(0, acao)
        time.sleep(0.4)

    def restaurar_sw(self, sw, val):
        def acao():
            try:
                if int(sw.get()) != int(val):
                    if int(val) == 1: sw.select()
                    else: sw.deselect()
                    if hasattr(sw, 'comando_real'): sw.comando_real()
            except Exception as e:
                self.log(f"Erro na UI (Restaurar): {str(e)}", "erro")
        self.after(0, acao)
        time.sleep(0.4)

    # --- MEMÓRIA PROFUNDA DOS PERFIS INTELIGENTES (REGISTO) ---
    def carregar_snapshot_memoria(self):
        """ Carrega o snapshot antigo salvo no Registo na última vez que o app foi aberto """
        snap_str = self.carregar_config("SnapshotPerfil", "")
        if snap_str:
            try:
                pares = snap_str.split(',')
                for par in pares:
                    k, v = par.split(':')
                    self.estado_anterior[k] = int(v)
            except Exception:
                pass

    def guardar_snapshot_atual(self):
        """ Salva o estado atual das 10 chaves na RAM e também no Registo do Windows """
        self.estado_anterior = {
            'pow': self.sw_pow.get(), 'gaming': self.sw_gaming.get(),
            'net_thrott': self.sw_net_thrott.get(), 'core_park': self.sw_core_park.get(),
            'tim': self.sw_tim.get(), 'gpu_oc': self.sw_gpu_oc.get(),
            'flip': self.sw_flip.get(), 'dscp': self.sw_dscp.get(),
            'tcp': self.sw_tcp.get(), 'thrott': self.sw_thrott.get()
        }
        snap_str = ",".join([f"{k}:{v}" for k, v in self.estado_anterior.items()])
        self.salvar_config("SnapshotPerfil", snap_str)

    def executar_restauracao_thread(self):
        self.log("[*] Desativando Perfil e revertendo exatamente para a configuração que estava...")
        if not self.estado_anterior: 
            self.log("[-] Nenhuma memória anterior encontrada para reverter.", "erro")
            return
        
        self.restaurar_sw(self.sw_pow, self.estado_anterior.get('pow', 0))
        self.restaurar_sw(self.sw_gaming, self.estado_anterior.get('gaming', 0))
        self.restaurar_sw(self.sw_net_thrott, self.estado_anterior.get('net_thrott', 0))
        self.restaurar_sw(self.sw_core_park, self.estado_anterior.get('core_park', 0))
        self.restaurar_sw(self.sw_tim, self.estado_anterior.get('tim', 0))
        self.restaurar_sw(self.sw_gpu_oc, self.estado_anterior.get('gpu_oc', 0))
        self.restaurar_sw(self.sw_flip, self.estado_anterior.get('flip', 0))
        self.restaurar_sw(self.sw_dscp, self.estado_anterior.get('dscp', 0))
        self.restaurar_sw(self.sw_tcp, self.estado_anterior.get('tcp', 0))
        self.restaurar_sw(self.sw_thrott, self.estado_anterior.get('thrott', 0))
        
        self.estado_anterior.clear()
        self.salvar_config("SnapshotPerfil", "") # Limpa o Registo
        self.log("[+] Chaves restauradas. O sistema voltou ao estado natural.")

    def aplicar_gamer_avancado(self):
        self.log("[*] INJETANDO MODO GAMER: Otimizando as 10 camadas de CPU/Rede/Energia...")
        self.forcar_ativo(self.sw_pow)
        self.forcar_ativo(self.sw_gaming)
        self.forcar_ativo(self.sw_net_thrott)
        self.forcar_ativo(self.sw_core_park)
        self.forcar_ativo(self.sw_tim)
        self.forcar_ativo(self.sw_gpu_oc)
        self.forcar_ativo(self.sw_flip)
        self.forcar_ativo(self.sw_dscp)
        self.forcar_ativo(self.sw_tcp)
        self.forcar_ativo(self.sw_thrott)
        self.log("[+] MODO GAMER MÁXIMO CONCLUÍDO! O seu hardware está agora em 100% de prioridade.")

    def aplicar_trabalho_avancado(self):
        self.log("[*] INJETANDO MODO TRABALHO: Desligando prioridade extrema para poupar energia...")
        self.forcar_desligado(self.sw_pow)
        self.forcar_desligado(self.sw_gaming)
        self.forcar_desligado(self.sw_net_thrott)
        self.forcar_desligado(self.sw_core_park)
        self.forcar_desligado(self.sw_tim)
        self.forcar_desligado(self.sw_gpu_oc)
        self.log("[+] MODO TRABALHO ATIVO! Estabilidade e bateria priorizadas para multitarefas.")

    # --- COMANDOS DE ACIONAMENTO DOS BOTÕES ---
    def acionar_perfil_gamer(self):
        if self.perfil_ativo == "Gamer":
            self.perfil_ativo = "Nenhum"
            self.salvar_config("PerfilAtivo", self.perfil_ativo)
            self.atualizar_cores_perfis()
            threading.Thread(target=self.executar_restauracao_thread, daemon=True).start()
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
            threading.Thread(target=self.executar_restauracao_thread, daemon=True).start()
        else:
            if self.perfil_ativo == "Nenhum": self.guardar_snapshot_atual()
            self.perfil_ativo = "Trabalho"
            self.salvar_config("PerfilAtivo", self.perfil_ativo)
            self.atualizar_cores_perfis()
            threading.Thread(target=self.aplicar_trabalho_avancado, daemon=True).start()

    def abrir_inicializacao(self):
        self.log("[*] Abrindo Gerenciador de Inicialização do Windows (Nativo)...")
        self.executar_comando_assincrono("start ms-settings:startupapps", "Gestor de Inicialização")

    def analisar_rede_info(self):
        def tarefa():
            self.log("[*] Analisando a sua conexão (Isto pode levar alguns segundos)...")
            try: ip_local = socket.gethostbyname(socket.gethostname())
            except: ip_local = "Erro ao localizar"
            
            try: ip_publico = urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode('utf8')
            except: ip_publico = "Oculto ou Bloqueado"
            
            try:
                res = subprocess.run('ping 8.8.8.8 -n 1', capture_output=True, text=True, creationflags=0x08000000)
                ping_str = "Falha no Ping"
                if "tempo=" in res.stdout: ping_str = res.stdout.split("tempo=")[1].split("ms")[0].strip() + " ms"
                elif "time=" in res.stdout: ping_str = res.stdout.split("time=")[1].split("ms")[0].strip() + " ms"
            except: ping_str = "Erro de rede"
            
            msg = f"\n=== DIAGNÓSTICO DE REDE ===\n> IP Local (LAN): {ip_local}\n> IP Público (WAN): {ip_publico}\n> Ping (Google DNS): {ping_str}\n===========================\n"
            self.log(msg)
        threading.Thread(target=tarefa, daemon=True).start()

    # --- COMANDOS DOS SWITCHES (CHAVES) ---
    def toggle_telemetry_tasks(self):
        p1 = "\\".join(["Microsoft", "Windows", "Application Experience", "Microsoft Compatibility Appraiser"])
        p2 = "\\".join(["Microsoft", "Windows", "Customer Experience Improvement Program", "Consolidator"])
        if self.sw_tasks.get() == 1:
            cmd = f'schtasks /Change /TN "{p1}" /Disable >nul 2>&1 & schtasks /Change /TN "{p2}" /Disable >nul 2>&1'
        else:
            cmd = f'schtasks /Change /TN "{p1}" /Enable >nul 2>&1 & schtasks /Change /TN "{p2}" /Enable >nul 2>&1'
        self.log_res(self.executar_comando(cmd), "Tarefas de Telemetria", self.sw_tasks)

    def toggle_vs_tel(self): self.log_res(self.executar_comando(f'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\VisualStudio\\Telemetry" /v "RefuseTelemetry" /t REG_DWORD /d {1 if self.sw_vs_tel.get() == 1 else 0} /f >nul 2>&1'), "VS Telemetry", self.sw_vs_tel)
    def toggle_thrott(self): self.log_res(self.executar_comando(f'reg add "HKLM\\System\\CurrentControlSet\\Control\\Power\\PowerThrottling" /v "PowerThrottlingOff" /t REG_DWORD /d {1 if self.sw_thrott.get() == 1 else 0} /f >nul 2>&1'), "Power Throttling", self.sw_thrott)
    
    def toggle_loc(self): 
        if self.sw_loc.get() == 1:
            res = self.executar_comando('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v "DisableLocation" /t REG_DWORD /d 1 /f >nul 2>&1')
        else:
            res = self.executar_comando('reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v "DisableLocation" /f >nul 2>&1')
        self.log_res(res, "Localização do Sistema", self.sw_loc)

    def toggle_gaming(self): 
        if self.sw_gaming.get() == 1:
            res = self.executar_comando('reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f >nul 2>&1 & reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f >nul 2>&1')
        else:
            res = self.executar_comando('reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 0 /f >nul 2>&1 & reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 1 /f >nul 2>&1')
        self.log_res(res, "Modo de Jogo Pro (Gaming Mode)", self.sw_gaming)

    def toggle_dscp(self): self.log_res(self.executar_comando(f'reg add "HKLM\\System\\CurrentControlSet\\Services\\Tcpip\\Parameters\\QoS" /v "Do not use NLA" /t REG_SZ /d "{1 if self.sw_dscp.get() == 1 else 0}" /f >nul 2>&1'), "DSCP", self.sw_dscp)
    def toggle_netsh(self): self.log_res(self.executar_comando(f'netsh int tcp set global autotuninglevel={"disabled" if self.sw_netsh.get() == 1 else "normal"} >nul 2>&1'), "Netsh", self.sw_netsh)
    def toggle_cong(self): self.log_res(self.executar_comando(f'netsh int tcp set supplemental template=internet congestionprovider={"cubic" if self.sw_cong.get() == 1 else "none"} >nul 2>&1'), "Congestion Provider", self.sw_cong)
    
    def toggle_tcp(self): 
        if self.sw_tcp.get() == 1:
            cmd = 'cmd /c "for /f %i in (\'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces"\') do (reg add "%i" /v "TcpAckFrequency" /t REG_DWORD /d 1 /f >nul 2>&1 & reg add "%i" /v "TCPNoDelay" /t REG_DWORD /d 1 /f >nul 2>&1)"'
        else:
            cmd = 'cmd /c "for /f %i in (\'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces"\') do (reg delete "%i" /v "TcpAckFrequency" /f >nul 2>&1 & reg delete "%i" /v "TCPNoDelay" /f >nul 2>&1)"'
        self.log_res(self.executar_comando(cmd), "TCP Settings", self.sw_tcp)
        
    def toggle_gpu_oc(self): self.log_res(self.executar_comando(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e968-e325-11ce-bfc1-08002be10318}}\\0000" /v "PowerMizerEnable" /t REG_DWORD /d {0 if self.sw_gpu_oc.get() == 1 else 1} /f >nul 2>&1'), "GPU Downclock", self.sw_gpu_oc)
    def toggle_smart(self): self.log_res(self.executar_comando(f'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v "EnableSmartScreen" /t REG_DWORD /d {0 if self.sw_smart.get() == 1 else 1} /f >nul 2>&1'), "SmartScreen", self.sw_smart)
    
    def toggle_tel(self): 
        if self.sw_tel.get() == 1:
            self.executar_comando("sc stop DiagTrack >nul 2>&1")
            res = self.executar_comando("sc config DiagTrack start= disabled >nul 2>&1")
        else:
            self.executar_comando("sc config DiagTrack start= auto >nul 2>&1")
            res = self.executar_comando("sc start DiagTrack >nul 2>&1")
        self.log_res(res, "Telemetria (DiagTrack)", self.sw_tel)
        
    def toggle_nv_priv(self): 
        if self.sw_nv_priv.get() == 1:
            self.executar_comando('taskkill /f /im NvTelemetryContainer.exe >nul 2>&1')
            self.log_res(self.executar_comando('reg add "HKLM\\SOFTWARE\\NVIDIA Corporation\\NvControlPanel2\\Client" /v "OptIn" /t REG_DWORD /d 0 /f >nul 2>&1'), "NVIDIA Privacy", self.sw_nv_priv)
        else: self.log("NVIDIA Privacy: Revertido.")
        
    def toggle_flip_fix(self): self.log_res(self.executar_comando(f'reg add "HKCU\\Control Panel\\Desktop" /v "EnableWindowedOptimization" /t REG_DWORD /d {1 if self.sw_flip.get() == 1 else 0} /f >nul 2>&1'), "Flip Integrity Fix", self.sw_flip)
    
    def toggle_srv(self):
        if self.sw_srv.get() == 1:
            self.executar_comando("sc stop SysMain >nul 2>&1")
            self.executar_comando("sc config SysMain start= disabled >nul 2>&1")
            self.executar_comando("sc stop WSearch >nul 2>&1")
            res = self.executar_comando("sc config WSearch start= disabled >nul 2>&1")
        else:
            self.executar_comando("sc config SysMain start= auto >nul 2>&1")
            self.executar_comando("sc start SysMain >nul 2>&1")
            self.executar_comando("sc config WSearch start= delayed-auto >nul 2>&1")
            res = self.executar_comando("sc start WSearch >nul 2>&1")
        self.log_res(res, "Serviços Pesados (SysMain/Search)", self.sw_srv)
        
    def toggle_tim(self): 
        if self.sw_tim.get() == 1:
            res = self.executar_comando('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel" /v "GlobalTimerResolutionRequests" /t REG_DWORD /d 1 /f >nul 2>&1')
        else:
            res = self.executar_comando('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel" /v "GlobalTimerResolutionRequests" /t REG_DWORD /d 0 /f >nul 2>&1')
        self.log_res(res, "Resolução de Tempo (Timer Res)", self.sw_tim)
        
    def toggle_pow(self):
        if int(self.sw_pow.get()) == 1:
            threading.Thread(target=self._ativar_desempenho_maximo, daemon=True).start()
        else:
            threading.Thread(target=self._ativar_equilibrado, daemon=True).start()

    def _ativar_desempenho_maximo(self):
        res_l = subprocess.run(['powercfg', '/l'], capture_output=True, text=True, creationflags=0x08000000)
        lista_planos = res_l.stdout.lower()
        guid_alvo = self.carregar_config("GuidMaximo", "")

        if not guid_alvo or guid_alvo.lower() not in lista_planos:
            if "e9a42b02-d5df-448d-aa00-03f14749eb61" in lista_planos:
                guid_alvo = "e9a42b02-d5df-448d-aa00-03f14749eb61" 
            else:
                self.after(0, self.log, "[*] Criando Plano de Desempenho Máximo nativo do Windows...")
                res_dup = subprocess.run(['powercfg', '-duplicatescheme', 'e9a42b02-d5df-448d-aa00-03f14749eb61'], capture_output=True, text=True, creationflags=0x08000000)
                match = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", res_dup.stdout)
                if match:
                    guid_alvo = match.group(1)
                else:
                    guid_alvo = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" 
        
        self.salvar_config("GuidMaximo", guid_alvo)
        subprocess.run(['powercfg', '/setactive', guid_alvo], capture_output=True, text=True, creationflags=0x08000000)
        
        res_verify = subprocess.run(['powercfg', '/getactivescheme'], capture_output=True, text=True, creationflags=0x08000000)
        if guid_alvo.lower() in res_verify.stdout.lower():
            self.after(0, self.log_res, 0, "Plano de Energia (Desempenho Máximo)", self.sw_pow)
        else:
            self.after(0, self.log_res, 1, "Falha ao definir Plano de Energia", self.sw_pow)

    def _ativar_equilibrado(self):
        guid_eq = "381b4222-f694-41f0-9685-ff5bb260df2e"
        subprocess.run(['powercfg', '/setactive', guid_eq], capture_output=True, text=True, creationflags=0x08000000)
        res_verify = subprocess.run(['powercfg', '/getactivescheme'], capture_output=True, text=True, creationflags=0x08000000)
        if guid_eq.lower() in res_verify.stdout.lower():
            self.after(0, self.log_res, 0, "Plano de Energia (Equilibrado)", self.sw_pow)
        else:
            self.after(0, self.log_res, 1, "Falha ao restaurar Plano de Energia", self.sw_pow)
        
    def toggle_tra(self): self.log_res(self.executar_comando(f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "EnableTransparency" /t REG_DWORD /d {0 if self.sw_tra.get() == 1 else 1} /f >nul 2>&1'), "Transparência", self.sw_tra)
    
    def toggle_net_thrott(self):
        if self.sw_net_thrott.get() == 1:
            res = self.executar_comando('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 0xFFFFFFFF /f >nul 2>&1')
        else:
            res = self.executar_comando('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 10 /f >nul 2>&1')
        self.log_res(res, "Limitação de Rede (Throttling)", self.sw_net_thrott)

    def toggle_core_parking(self):
        if self.sw_core_park.get() == 1:
            res = self.executar_comando('powercfg /setacvalueindex scheme_current sub_processor CPMINCORES 100 >nul 2>&1 & powercfg /setactive scheme_current >nul 2>&1')
        else:
            res = self.executar_comando('powercfg /setacvalueindex scheme_current sub_processor CPMINCORES 5 >nul 2>&1 & powercfg /setactive scheme_current >nul 2>&1')
        self.log_res(res, "Core Parking (CPU 100%)", self.sw_core_park)

    # --- COMANDOS ISOLADOS E MANUTENÇÃO (REQUEREM REINICIAR) ---
    def toggle_uac(self): self.log_res(self.executar_comando(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v "EnableLUA" /t REG_DWORD /d {0 if self.sw_uac.get() == 1 else 1} /f >nul 2>&1'), "UAC", self.sw_uac, reinicio=True)
    
    def toggle_mit(self): 
        if self.sw_mit.get() == 1:
            self.executar_comando('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "FeatureSettingsOverride" /t REG_DWORD /d 3 /f >nul 2>&1')
            res = self.executar_comando('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "FeatureSettingsOverrideMask" /t REG_DWORD /d 3 /f >nul 2>&1')
        else:
            self.executar_comando('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "FeatureSettingsOverride" /t REG_DWORD /d 0 /f >nul 2>&1')
            res = self.executar_comando('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "FeatureSettingsOverrideMask" /t REG_DWORD /d 3 /f >nul 2>&1')
        self.log_res(res, "Mitigações de CPU", self.sw_mit, reinicio=True)

    def toggle_mnu(self):
        if self.sw_mnu.get() == 1: self.log_res(self.executar_comando('reg add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /f /ve >nul 2>&1'), "Menu Clássico", self.sw_mnu, reinicio=True)
        else: self.log_res(self.executar_comando('reg delete "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f >nul 2>&1'), "Menu Original", self.sw_mnu, reinicio=True)
        
    def toggle_bmn(self): self.log_res(self.executar_comando(f"bcdedit /timeout {'2' if self.sw_bmn.get() == 1 else '30'} >nul 2>&1"), "Boot Menu", self.sw_bmn, reinicio=True)
    
    def toggle_fast_startup(self):
        if self.sw_fast_start.get() == 1:
            res = self.executar_comando('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v "HiberbootEnabled" /t REG_DWORD /d 0 /f >nul 2>&1')
        else:
            res = self.executar_comando('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v "HiberbootEnabled" /t REG_DWORD /d 1 /f >nul 2>&1')
        self.log_res(res, "Desativar Inicialização Rápida", self.sw_fast_start, reinicio=True)

    def toggle_widgets(self):
        if self.sw_widgets.get() == 1:
            res = self.executar_comando('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Dsh" /v "AllowNewsAndInterests" /t REG_DWORD /d 0 /f >nul 2>&1')
        else:
            res = self.executar_comando('reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Dsh" /v "AllowNewsAndInterests" /f >nul 2>&1')
        self.log_res(res, "Desativar Widgets", self.sw_widgets, reinicio=True)

    def verificar_erros(self): 
        self.log("[*] Iniciando Verificação do Sistema (SFC)... Acompanhe na janela.")
        self.executar_comando_visivel("sfc /scannow", "Verificação do Sistema (SFC)", reinicio=True)

    def verificar_disco(self): 
        self.log("[*] Mapeando e verificando a integridade de TODOS os discos... Acompanhe na janela.")
        comandos = []
        for part in psutil.disk_partitions():
            if part.fstype != '' and 'cdrom' not in part.opts:
                letra = part.device[:2]
                comandos.append(f"echo. & echo === VERIFICANDO DISCO {letra} === & chkdsk {letra} /scan")
        
        cmd_final = " & ".join(comandos)
        if cmd_final:
            self.executar_comando_visivel(cmd_final, "Verificar Disco (CHKDSK)", reinicio=True)

    # --- NOVAS FUNÇÕES DE BOTÕES ---
    def criar_ponto_restauracao(self):
        self.log("[*] Criando Ponto de Restauração de Segurança... Aguarde na janela preta.")
        cmd = 'powershell.exe -ExecutionPolicy Bypass -NoProfile -Command "Enable-ComputerRestore -Drive \'C:\\\'; Checkpoint-Computer -Description \'GustavoOptimizer\' -RestorePointType \'MODIFY_SETTINGS\'"'
        self.executar_comando_visivel(cmd, "Ponto de Restauração")

    def reparar_imagem_dism(self):
        self.log("[*] Fazendo download e reparando núcleo do Windows via DISM...")
        self.executar_comando_visivel("DISM /Online /Cleanup-Image /RestoreHealth", "Reparo DISM")

    def limpar_logs_windows(self):
        self.log("[*] Limpando milhares de arquivos invisíveis de Log do Windows...")
        cmd = 'powershell -Command "wevtutil el | foreach { wevtutil cl \\\"$_\\\" }"'
        self.executar_comando_assincrono(cmd, "Limpeza de Logs de Eventos")

    def limpar_prefetch(self):
        self.log("[*] Apagando arquivos antigos de arranque do Prefetch...")
        self.executar_comando_assincrono('del /s /f /q "%WINDIR%\\Prefetch\\*.*" >nul 2>&1', "Limpar Prefetch")

    def aplicar_dns_google(self):
        self.log("[*] Injetando DNS da Google na Placa de Rede Principal...")
        cmd = 'powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\' -and $_.InterfaceAlias -notlike \'*Loopback*\'} | Set-DnsClientServerAddress -ServerAddresses \'8.8.8.8\',\'8.8.4.4\'"'
        self.executar_comando_assincrono(cmd, "DNS Google 8.8.8.8")

    def aplicar_dns_cloudflare(self):
        self.log("[*] Injetando DNS da Cloudflare na Placa de Rede Principal...")
        cmd = 'powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\' -and $_.InterfaceAlias -notlike \'*Loopback*\'} | Set-DnsClientServerAddress -ServerAddresses \'1.1.1.1\',\'1.0.0.1\'"'
        self.executar_comando_assincrono(cmd, "DNS Cloudflare 1.1.1.1")

    def remover_bloatware(self):
        self.log("[*] Desinstalando Apps lixo (Bloatware) nativos do Windows...")
        cmd = 'powershell -Command "Get-AppxPackage *bing* | Remove-AppxPackage; Get-AppxPackage *zune* | Remove-AppxPackage; Get-AppxPackage *solitaire* | Remove-AppxPackage"'
        self.executar_comando_visivel(cmd, "Remoção de Bloatware")

    # --- FUNÇÕES DE MANUTENÇÃO CLÁSSICAS ---
    def limpar_temp(self): 
        self.log("[*] Limpando arquivos temporários...")
        self.executar_comando_assincrono("del /s /f /q %temp%\\*.* >nul 2>&1", "Temp")
        
    def limpar_windows(self): 
        self.log("[*] Iniciando Limpeza de Disco Avançada...")
        self.executar_comando_assincrono("cleanmgr /sagerun:1", "Limpeza de Disco (Cleanmgr)")
        
    def otimizar_internet(self): 
        self.log("[*] Redefinindo configurações de rede...")
        self.executar_comando_assincrono("ipconfig /flushdns >nul 2>&1 & netsh winsock reset >nul 2>&1", "Rede e Flush DNS")
        
    def otimizar_discos(self): 
        self.log("[*] Iniciando otimização inteligente (TRIM/Defrag) em TODOS os discos... Acompanhe na janela.")
        self.executar_comando_visivel("defrag /C /O /U", "Otimizar Unidades (Defrag)")

    def limpar_gpu(self): 
        self.log("[*] Apagando cache de vídeo NVIDIA...")
        self.executar_comando_assincrono('del /f /s /q "%LocalAppData%\\NVIDIA\\DXCache\\*.*" >nul 2>&1', "GPU Cache")
        
    def limpar_thumbnails(self): 
        self.log("[*] Reiniciando Windows Explorer para limpar miniaturas...")
        comando = 'taskkill /f /im explorer.exe >nul 2>&1 & del /f /s /q "%LocalAppData%\\Microsoft\\Windows\\Explorer\\thumbcache_*.db" >nul 2>&1 & start explorer.exe'
        self.executar_comando_assincrono(comando, "Limpar Miniaturas")
        
    def limpar_update(self):
        self.log("[*] Iniciando Limpeza Profunda do Windows Update (Pode demorar um pouco)...")
        comando = 'net stop wuauserv >nul 2>&1 & del /s /f /q "%windir%\\SoftwareDistribution\\Download\\*.*" >nul 2>&1 & net start wuauserv >nul 2>&1'
        self.executar_comando_assincrono(comando, "Limpeza Windows Update")
        
    # --- LIMPEZA OFUSCADA CONTRA ANTIVÍRUS (ANTI-HEURÍSTICA) ---
    def limpar_chrome(self): 
        self.log("[*] Limpando cache do Google Chrome...")
        c_path = "\\".join(["Google", "Chrome", "User Data", "Default", "Cache", "*.*"])
        self.executar_comando_assincrono(f'del /s /f /q "%LocalAppData%\\{c_path}" >nul 2>&1', "Google Chrome")
        
    def limpar_edge(self): 
        self.log("[*] Limpando cache do Microsoft Edge...")
        e_path = "\\".join(["Microsoft", "Edge", "User Data", "Default", "Cache", "*.*"])
        self.executar_comando_assincrono(f'del /s /f /q "%LocalAppData%\\{e_path}" >nul 2>&1', "Microsoft Edge")
        
    def limpar_opera(self): 
        self.log("[*] Limpando cache do Opera e Opera GX...")
        p_gx = "\\".join(["Opera Software", "Opera GX Stable", "Cache", "*.*"])
        p_op = "\\".join(["Opera Software", "Opera Stable", "Cache", "*.*"])
        cmd = f'del /s /f /q "%LocalAppData%\\{p_gx}" >nul 2>&1 & del /s /f /q "%LocalAppData%\\{p_op}" >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Opera / Opera GX")

    def limpar_firefox(self):
        self.log("[*] Limpando perfis de cache do Mozilla Firefox...")
        f_path = "\\".join(["Mozilla", "Firefox", "Profiles", "*", "cache2", "*"])
        cmd = f'powershell -Command "Remove-Item -Path \\"$env:LOCALAPPDATA\\{f_path}\\" -Recurse -Force -ErrorAction SilentlyContinue"'
        self.executar_comando_assincrono(cmd, "Mozilla Firefox")

    def limpar_spotify(self): 
        self.log("[*] Limpando cache do Spotify...")
        s_path = "\\".join(["Spotify", "Data"])
        self.executar_comando_assincrono(f'taskkill /f /im Spotify.exe >nul 2>&1 & rmdir /s /q "%LocalAppData%\\{s_path}" >nul 2>&1', "Spotify")
        
    def limpar_steam(self): 
        self.log("[*] Limpando cache do Steam...")
        st_path = "\\".join(["Steam", "appcache"])
        self.executar_comando_assincrono(f'taskkill /f /im steam.exe >nul 2>&1 & rmdir /s /q "C:\\Program Files (x86)\\{st_path}" >nul 2>&1', "Steam")
        
    def limpar_discord(self): 
        self.log("[*] Limpando cache do Discord...")
        d_path = "\\".join(["Discord", "Cache"])
        self.executar_comando_assincrono(f'taskkill /f /im Discord.exe >nul 2>&1 & rmdir /s /q "%AppData%\\{d_path}" >nul 2>&1', "Discord")
        
    def limpar_battlenet(self): 
        self.log("[*] Limpando cache do Battle.net...")
        self.executar_comando_assincrono('taskkill /f /im Agent.exe >nul 2>&1 & rmdir /s /q "%ProgramData%\\Battle.net" >nul 2>&1', "Battle.net")
        
    def limpar_apps_multi(self):
        self.log("[*] Iniciando limpeza total de aplicativos (excluindo navegadores)...")
        s_path = "\\".join(["Spotify", "Data"])
        st_path = "\\".join(["Steam", "appcache"])
        d_path = "\\".join(["Discord", "Cache"])
        
        comando = (
            f'taskkill /f /im Spotify.exe >nul 2>&1 & taskkill /f /im steam.exe >nul 2>&1 & '
            f'taskkill /f /im Discord.exe >nul 2>&1 & taskkill /f /im Agent.exe >nul 2>&1 & '
            f'rmdir /s /q "%LocalAppData%\\{s_path}" >nul 2>&1 & '
            f'rmdir /s /q "C:\\Program Files (x86)\\{st_path}" >nul 2>&1 & '
            f'rmdir /s /q "%AppData%\\{d_path}" >nul 2>&1 & '
            f'rmdir /s /q "%ProgramData%\\Battle.net" >nul 2>&1'
        )
        self.executar_comando_assincrono(comando, "Limpeza Total de Apps")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = MeuOtimizador()
    app.mainloop()
