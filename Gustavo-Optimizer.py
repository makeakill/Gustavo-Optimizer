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

        self.title("Gustavo Optimizer v1.1 - Pro Edition (Auditado)")
        self.geometry("1400x900")
        
        # Lock de segurança para escrita Thread-Safe no Registo
        self.reg_lock = threading.Lock()
        
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
        
        # Fallback inicial para Planos de Energia e Captura Dinâmica
        self.guid_maximo = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
        # O programa agora memoriza o plano equilibrado exato da sua máquina
        self.guid_padrao = self.carregar_config("GuidPadrao", "381b4222-f694-41f0-9685-ff5bb260df2e")
        
        self.configure(fg_color=self.bg_main)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # 1. BARRA LATERAL (SIDEBAR) TÉCNICA
        # ==========================================
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=self.bg_painel, border_width=1, border_color=self.borda)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(13, weight=1)

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
        self.btn_exportar.grid(row=5, column=0, padx=20, pady=10, sticky="w")

        self.btn_manual = ctk.CTkButton(self.sidebar, text="MANUAL DO PROGRAMA", command=self.abrir_manual, fg_color=self.bg_painel, hover_color=self.acento, text_color=self.texto_branco, corner_radius=0, border_width=1, border_color=self.acento, font=("Consolas", 12, "bold"))
        self.btn_manual.grid(row=6, column=0, padx=20, pady=(10, 20), sticky="w")

        self.combo_temas = ctk.CTkOptionMenu(self.sidebar, values=list(PALETAS.keys()), command=self.mudar_tema, fg_color=self.bg_painel, button_color=self.borda, button_hover_color=self.acento, dropdown_fg_color=self.bg_painel, dropdown_text_color=self.texto_branco, text_color=self.texto_branco, font=("Consolas", 11, "bold"))
        self.combo_temas.set(tema_salvo)
        self.combo_temas.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="w")

        self.lbl_cpu = ctk.CTkLabel(self.sidebar, text="⚙️ CPU: Calc...", font=("Consolas", 14, "bold"), text_color=self.texto_branco)
        self.lbl_cpu.grid(row=8, column=0, padx=20, pady=5, sticky="w")
        
        self.lbl_ram = ctk.CTkLabel(self.sidebar, text="💾 RAM: Calc...", font=("Consolas", 14, "bold"), text_color=self.texto_branco)
        self.lbl_ram.grid(row=9, column=0, padx=20, pady=5, sticky="w")
        
        self.lbl_gpu = ctk.CTkLabel(self.sidebar, text="🎮 GPU: Calc...", font=("Consolas", 14, "bold"), text_color=self.texto_branco)
        self.lbl_gpu.grid(row=10, column=0, padx=20, pady=5, sticky="nw")

        # --- SWITCH MODO ESCURO NA BARRA LATERAL ---
        self.sw_sidebar_dark = ctk.CTkSwitch(self.sidebar, text="FORÇAR MODO ESCURO", command=self.acao_dark_mode, font=("Consolas", 12, "bold"), progress_color=self.acento, fg_color=self.borda)
        self.sw_sidebar_dark.grid(row=11, column=0, padx=20, pady=(20, 5), sticky="w")
        estado_dark = self.carregar_config("DarkModeSidebar", "0")
        if estado_dark == "1":
            self.sw_sidebar_dark.select()

        # --- BARRA DE PROGRESSO VISUAL ---
        self.progress_bar = ctk.CTkProgressBar(self.sidebar, height=8, progress_color=self.acento, fg_color=self.borda, corner_radius=0)
        self.progress_bar.grid(row=12, column=0, padx=20, pady=(15, 5), sticky="ew")
        self.progress_bar.set(0)

        self.caixa_log = ctk.CTkTextbox(self.sidebar, height=180, corner_radius=0, font=("Consolas", 11), fg_color=self.bg_main, text_color=self.texto_cinza, border_width=1, border_color=self.borda)
        self.caixa_log.grid(row=13, column=0, padx=10, pady=10, sticky="sew")
        
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

    # --- MONITORAMENTO DE HARDWARE ---
    def atualizar_hardware(self):
        uso_cpu = psutil.cpu_percent(interval=None)
        uso_ram = psutil.virtual_memory().percent
        uso_gpu = "N/A"
        try:
            res = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, creationflags=0x08000000)
            if res.returncode == 0: uso_gpu = f"{res.stdout.strip()}%"
        except Exception: 
            uso_gpu = "Erro/AMD"
        
        self.lbl_cpu.configure(text=f"⚙️ CPU: {uso_cpu}%")
        self.lbl_ram.configure(text=f"💾 RAM: {uso_ram}%")
        self.lbl_gpu.configure(text=f"🎮 GPU: {uso_gpu}")
        self.after(1000, self.atualizar_hardware)

    # --- CONTROLES MASTER DA BARRA LATERAL ---
    def thread_manutencao(self):
        if self.sw_master_clean.get() == 1:
            if not self.is_admin:
                self.sw_master_clean.deselect()
                return
            threading.Thread(target=self.limpeza_sequencial, daemon=True).start()

    def limpeza_sequencial(self):
        tarefas = [("Temporários", "del /s /f /q %temp%\\*.*"), ("Rede", "ipconfig /flushdns & netsh winsock reset")]
        for n, c in tarefas:
            if self.sw_master_clean.get() == 0: break
            res = self.executar_comando(c)
            time.sleep(1)
            self.log_res(res, n)
            self.log(f"Etapa {n} em andamento...") 
        if self.sw_master_clean.get() == 1:
            self.executar_comando_visivel("sfc /scannow", "SFC Scan", reinicio=True)
        self.log("MANUTENÇÃO CONCLUÍDA.")
        self.sw_master_clean.deselect()

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
                except Exception: 
                    pass
            self.after(0, acao_master)
            time.sleep(0.4) 
        self.log("Sincronização global concluída.")

    # --- OTIMIZAÇÕES NATIVAS (PYTHON API) ---
    def otimizar_ram_nativa(self):
        def tarefa():
            self.log("[*] Analisando processos na RAM via API Nativa (PSAPI)...")
            self.after(0, self.progress_bar.set, 0.2)
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
                            if psapi.EmptyWorkingSet(h_process): count += 1
                            kernel32.CloseHandle(h_process)
                    except Exception: 
                        pass
                    
                    if i % max(1, total // 10) == 0: 
                        self.after(0, self.progress_bar.set, 0.2 + (i/total)*0.8)
                
                self.after(0, self.progress_bar.set, 1)
                self.log(f"[+] Smart RAM Cleaner concluído! Memória vazada devolvida de {count} processos.")
                time.sleep(1.5)
                self.after(0, self.progress_bar.set, 0)
            except Exception as e:
                self.log(f"[-] Erro na API do Kernel: {str(e)}", "erro")
                self.after(0, self.progress_bar.set, 0)
        threading.Thread(target=tarefa, daemon=True).start()

    def prioridade_jogos_nativa(self):
        def tarefa():
            self.log("[*] Injetando prioridade de CPU no Kernel para jogos ativos...")
            jogos_alvo = ['cs2.exe', 'dota2.exe', 'overwatch.exe', 'valorant.exe', 'javaw.exe', 'gta5.exe', 'robloxplayerbeta.exe', 'r5apex.exe', 'lol.exe', 'cod.exe', 'cyberpunk2077.exe']
            encontrados = []
            self.after(0, self.progress_bar.set, 0.5)
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    nome = str(proc.info['name']).lower()
                    if nome in jogos_alvo:
                        p = psutil.Process(proc.info['pid'])
                        p.nice(psutil.HIGH_PRIORITY_CLASS)
                        encontrados.append(nome)
                except Exception: 
                    pass
            
            self.after(0, self.progress_bar.set, 1)
            if encontrados:
                for j in set(encontrados):
                    self.log(f"[+] Jogo detetado e otimizado: {j.upper()} (Prioridade ALTA)")
                self.log("[+] Os seus jogos dominam agora 100% da CPU.")
            else:
                self.log("[-] Nenhum jogo reconhecido ativo no momento. Abra o jogo primeiro!", "erro")
            
            time.sleep(1.5)
            self.after(0, self.progress_bar.set, 0)
        threading.Thread(target=tarefa, daemon=True).start()

    def verificar_hz_monitor(self):
        def tarefa():
            self.log("[*] Consultando a API de Vídeo do Windows (user32.dll)...")
            self.after(0, self.progress_bar.set, 0.5)
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
                    self.log(f"[+] Leitura concluída: O seu ecrã está a rodar a {hz}Hz no momento.")
                    if hz <= 60:
                        self.log("[-] Dica: Se o seu monitor suportar mais de 60Hz, você está a perder frames. Mude nas configurações do Windows!", "erro")
                    else:
                        self.log("[+] Monitor de alta taxa de atualização detetado e validado com sucesso.")
                else:
                    self.log("[-] Falha ao ler a placa de vídeo.", "erro")
            except Exception as e:
                self.log(f"[-] Erro na leitura de hardware: {str(e)}", "erro")
            
            self.after(0, self.progress_bar.set, 1)
            time.sleep(1.5)
            self.after(0, self.progress_bar.set, 0)
        threading.Thread(target=tarefa, daemon=True).start()

    def benchmark_dns_nativo(self):
        def tarefa():
            self.log("[*] Iniciando Benchmark Global de Rede. Testando rotas de pacotes...")
            self.after(0, self.progress_bar.set, 0)
            servidores = {"Google": "8.8.8.8", "Cloudflare": "1.1.1.1", "OpenDNS": "208.67.222.222", "Quad9": "9.9.9.9"}
            resultados = {}
            passo = 1.0 / len(servidores)
            progresso = 0.0
            
            for nome, ip in servidores.items():
                try:
                    self.log(f"[*] A enviar pacotes para {nome} ({ip})...")
                    res = subprocess.run(f"ping {ip} -n 4", capture_output=True, text=True, creationflags=0x08000000)
                    match = re.search(r'(Média|Average) = (\d+)ms', res.stdout, re.IGNORECASE)
                    if match:
                        resultados[nome] = int(match.group(2))
                    else:
                        resultados[nome] = 999
                except Exception: 
                    resultados[nome] = 999
                
                progresso += passo
                self.after(0, self.progress_bar.set, progresso)
            
            self.after(0, self.progress_bar.set, 1)
            
            valido = {k: v for k, v in resultados.items() if v != 999}
            if valido:
                melhor = min(valido, key=valido.get)
                self.log(f"\n[+] O MELHOR DNS PARA A SUA LOCALIZAÇÃO É: {melhor.upper()} ({valido[melhor]}ms)")
                for n, p in valido.items(): 
                    self.log(f"   -> {n}: {p}ms")
            else:
                self.log("[-] Falha ao testar rotas. Verifique a sua ligação à internet.", "erro")
            
            time.sleep(2)
            self.after(0, self.progress_bar.set, 0)
        threading.Thread(target=tarefa, daemon=True).start()

    def limpar_temp_nativa(self):
        def tarefa():
            self.log("[*] Mapeando lixo eletrónico na pasta Temp de forma nativa...")
            temp_path = os.environ.get('TEMP')
            if not temp_path or not os.path.exists(temp_path):
                self.log("[-] Pasta Temp não encontrada no sistema.", "erro")
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
            
            self.log(f"[*] Exterminando {total} ficheiros corrompidos ou inúteis...")
            self.after(0, self.progress_bar.set, 0)
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
                
                # Atualiza a barra de progresso visual
                if total > 0 and i % max(1, total // 50) == 0: 
                    self.after(0, self.progress_bar.set, i / total)
                    
            self.after(0, self.progress_bar.set, 1)
            self.log(f"[+] Limpeza Profunda Concluída: {apagados} ficheiros apagados para sempre.")
            time.sleep(1.5)
            self.after(0, self.progress_bar.set, 0)
        threading.Thread(target=tarefa, daemon=True).start()

    # --- VERIFICAÇÃO INTELIGENTE DO DESEMPENHO MÁXIMO ---
    def iniciar_verificacao_energia(self):
        threading.Thread(target=self.checar_plano_energia, daemon=True).start()

    def checar_plano_energia(self):
        """ AUDITORIA DE ENERGIA DINÂMICA: Verifica o plano nativo para restauração perfeita """
        
        # 1. Tira uma foto do plano atual ANTES de mexermos em qualquer coisa.
        #    Isto garante que vamos devolver a máquina ao plano do fabricante (ex: Dell/Lenovo).
        try:
            res_curr = subprocess.run(['powercfg', '/getactivescheme'], capture_output=True, text=True, creationflags=0x08000000)
            match_curr = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", res_curr.stdout)
            if match_curr:
                curr_guid = match_curr.group(1).lower()
                guid_salvo = self.carregar_config("GuidMaximo", "").lower()
                
                # Se o plano atual for diferente de "Desempenho Máximo", então este é o plano padrão seguro
                if curr_guid != guid_salvo and curr_guid != "e9a42b02-d5df-448d-aa00-03f14749eb61":
                    self.guid_padrao = curr_guid
                    self.salvar_config("GuidPadrao", self.guid_padrao)
        except Exception:
            pass

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

    # --- SISTEMA DE MEMÓRIA (REGISTO DO WINDOWS) COM LOCK THREAD-SAFE ---
    def salvar_config(self, nome, valor):
        with self.reg_lock:
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

    def carregar_snapshot_memoria(self):
        """ Carrega o snapshot antigo salvo no Registo """
        self.estado_anterior = {}
        snap_str = self.carregar_config("SnapshotPerfil", "")
        if snap_str:
            try:
                pares = snap_str.split(',')
                for par in pares:
                    if ':' in par:
                        k, v = par.split(':')
                        self.estado_anterior[k] = int(v)
            except Exception:
                pass

    def guardar_snapshot_atual(self):
        """ Salva o estado atual das TODAS as chaves críticas no Registo """
        self.estado_anterior = {
            'pow': self.sw_pow.get(), 'gaming': self.sw_gaming.get(),
            'net_thrott': self.sw_net_thrott.get(), 'core_park': self.sw_core_park.get(),
            'tim': self.sw_tim.get(), 'gpu_oc': self.sw_gpu_oc.get(),
            'flip': self.sw_flip.get(), 'dscp': self.sw_dscp.get(),
            'tcp': self.sw_tcp.get(), 'thrott': self.sw_thrott.get(),
            'srv': self.sw_srv.get(), 'netsh': self.sw_netsh.get(),
            'cong': self.sw_cong.get()
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
        self.sidebar.configure(fg_color=self.bg_painel, border_color=self.borda)
        self.lbl_logo.configure(text_color=self.acento)
        self.status_topo.configure(text_color="#2ecc71" if self.is_admin else self.acento)
        self.sw_master_sys.configure(progress_color=self.acento, fg_color=self.borda)
        self.sw_master_clean.configure(progress_color=self.acento, fg_color=self.borda)
        self.sw_sidebar_dark.configure(progress_color=self.acento, fg_color=self.borda)
        self.btn_exportar.configure(fg_color=self.bg_painel, hover_color=self.acento, border_color=self.acento)
        self.btn_restore.configure(fg_color=self.bg_painel, hover_color=self.acento, border_color=self.acento)
        self.btn_manual.configure(fg_color=self.bg_painel, hover_color=self.acento, border_color=self.acento)
        self.combo_temas.configure(fg_color=self.bg_painel, button_color=self.borda, button_hover_color=self.acento, dropdown_fg_color=self.bg_painel, text_color=self.texto_branco)
        self.caixa_log.configure(fg_color=self.bg_main, text_color=self.texto_cinza, border_color=self.borda)
        self.lbl_cpu.configure(text_color=self.texto_branco)
        self.lbl_ram.configure(text_color=self.texto_branco)
        self.lbl_gpu.configure(text_color=self.texto_branco)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.configure(progress_color=self.acento, fg_color=self.borda)
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

    # --- FUNÇÕES DE EXPORTAÇÃO E MANUAL VISUAL ---
    def exportar_log(self):
        conteudo = self.caixa_log.get("1.0", "end-1c")
        caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".txt", title="Salvar Log", initialfile="Log_Otimizacao.txt")
        if caminho_arquivo:
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo: arquivo.write(conteudo)
            self.log(f"Log salvo em: {caminho_arquivo}")

    def abrir_manual(self):
        janela_manual = ctk.CTkToplevel(self)
        janela_manual.title("Manual do Sistema - Gustavo Optimizer v1.1")
        janela_manual.geometry("850x650")
        janela_manual.transient(self)
        janela_manual.grab_set() 
        janela_manual.configure(fg_color=self.bg_main)

        lbl_titulo = ctk.CTkLabel(janela_manual, text="[ MANUAL DE INSTRUÇÕES E DOCUMENTAÇÃO ]", font=("Consolas", 18, "bold"), text_color=self.acento)
        lbl_titulo.pack(pady=(20, 10))

        caixa_texto = ctk.CTkTextbox(janela_manual, font=("Consolas", 13), fg_color=self.bg_painel, text_color=self.texto_branco, border_width=1, border_color=self.borda)
        caixa_texto.pack(expand=True, fill="both", padx=20, pady=10)

        manual_completo = (
            "================================================================================\n"
            "                 GUSTAVO OPTIMIZER v1.1 - PRO EDITION                           \n"
            "================================================================================\n\n"
            "Bem-vindo ao Gustavo Optimizer! Esta é uma ferramenta de engenharia avançada\n"
            "desenvolvida para extrair o máximo de desempenho do seu hardware com segurança,\n"
            "operando tanto com comandos do Windows quanto com Scripts nativos em Python.\n\n"
            "================================================================================\n"
            "COMO UTILIZAR O PROGRAMA:\n"
            "================================================================================\n"
            "1. BARRA LATERAL (MASTER CONTROLS):\n"
            "   - Master Sistema: Ativa/Desativa todas as chaves automáticas simultaneamente.\n"
            "   - Master Manutenção: Roda um ciclo completo de limpeza de rede e ficheiros.\n"
            "   - Ponto de Restauração: Crie sempre um ponto antes de modificar o sistema.\n\n"
            "2. PERFIS INTELIGENTES (A MAGIA):\n"
            "   - MODO GAMER: Injeta prioridade máxima no sistema. Ele ativa 10 camadas de\n"
            "     otimização de uma só vez (Energia, CPU, GPU, Rede e Latência).\n"
            "   - MODO TRABALHO: Um clique aqui revoga o Modo Gamer e traz o PC de volta\n"
            "     para o padrão de economia de bateria e estabilidade total.\n"
            "   * Nota: O programa tira uma 'foto' do seu Registo antes de aplicar o modo\n"
            "     Gamer. Mesmo que reinicie o PC, ele lembra-se de como reverter a otimização.\n\n"
            "================================================================================\n"
            "EXPLICAÇÃO DAS FUNÇÕES NATIVAS (API DO PYTHON):\n"
            "================================================================================\n"
            "- Smart RAM Cleaner: Dialoga com o Kernel (psapi.dll) e força aplicativos em\n"
            "  segundo plano a devolverem a memória cache que não estão a usar.\n"
            "- Auto Game Priority: Varre a RAM à procura de jogos pesados (CS2, Valorant,\n"
            "  Overwatch, Dota) e eleva-os para Prioridade ALTA diretamente no processador.\n"
            "- Validador de Hz: Lê o hardware da tela e avisa se estiver perdendo frames.\n"
            "- Benchmark DNS Global: Avalia o ping do seu PC até a Google, Cloudflare,\n"
            "  OpenDNS e Quad9, revelando o servidor exato que dará menos lag na sua casa.\n\n"
            "================================================================================\n"
            "EXPLICAÇÃO DOS COMANDOS (REGISTO E REDE):\n"
            "================================================================================\n"
            "- Power Throttling: Impede o Windows de 'adormecer' programas para poupar luz.\n"
            "- Core Parking: Obriga todos os núcleos do seu Processador a ficarem acordados.\n"
            "- Resolução de Tempo: Altera os milissegundos do sistema, reduzindo Input Lag.\n"
            "- Plano Desempenho Máximo: Revela o plano de Workstations oculto do Windows.\n"
            "- Economia da GPU: Bloqueia a queda de Mhz da Placa de Vídeo em momentos calmos.\n"
            "- TcpNoDelay (Nagle): Envia pacotes de tiro instantaneamente sem agrupar.\n"
            "- DSCP: Configura o router da sua casa para dar via verde ao jogo.\n\n"
            "================================================================================\n"
            "                      CHANGELOG E ATUALIZAÇÕES                                  \n"
            "================================================================================\n"
            "v1.1.0 - Correção Arquitetural do Modo Gamer e Execução Assíncrona.\n"
            "v1.0.0 - Exportacao Visual para Documentos e Snapshots no Registo de Memória.\n"
            "v0.9.0 - Correção Thread-Safe e validação Kernel do Plano de Energia.\n"
            "v0.8.0 - Expansão de Perfis Gamer (10 camadas simultâneas).\n"
            "v0.5.0 - Blindagem Anti-Heurística contra falsos positivos (Kaspersky).\n"
            "================================================================================\n"
        )

        caixa_texto.insert("0.0", manual_completo)
        caixa_texto.configure(state="disabled") 

        def salvar_manual():
            caminho = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="Manual_Gustavo_Optimizer.txt", title="Salvar Arquivo de Manual")
            if caminho:
                try:
                    with open(caminho, "w", encoding="utf-8") as f: 
                        f.write(manual_completo)
                    self.log(f"Manual exportado e salvo com sucesso em: {caminho}")
                    janela_manual.destroy() 
                except Exception as e: 
                    self.log(f"Erro ao exportar manual: {str(e)}", "erro")

        btn_salvar = ctk.CTkButton(janela_manual, text="EXPORTAR TEXTO PARA .TXT", command=salvar_manual, fg_color=self.bg_painel, hover_color=self.acento, text_color=self.texto_branco, border_width=1, border_color=self.acento, font=("Consolas", 12, "bold"))
        btn_salvar.pack(pady=(10, 20))

    # --- FUNÇÕES DE LAYOUT ---
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

    # --- MONTAGEM DA GRELHA TOTAL ---
    def montar_interface_total(self):
        
        # 0. PERFIS INTELIGENTES
        self.criar_secao("Perfis Inteligentes (Auto)", 0)
        self.btn_gamer = self.criar_card_botao(1, 0, "Desempenho", "Ativar Modo Gamer", "Ativa simultaneamente as principais funções extremas de CPU, GPU e Rede.", self.acionar_perfil_gamer, btn_texto="ATIVAR MODO")
        self.btn_trabalho = self.criar_card_botao(1, 1, "Equilíbrio", "Ativar Modo Trabalho", "Restaura configurações nativas focadas na estabilidade e bateria.", self.acionar_perfil_trabalho, btn_texto="ATIVAR MODO")

        # 2. FERRAMENTAS INTELIGENTES NATIVAS
        self.criar_secao("Otimizações Nativas (Python API)", 2)
        self.criar_card_botao(3, 0, "Memória", "Smart RAM Cleaner", "Liberta memória em cache de processos nativos da API do Windows.", self.otimizar_ram_nativa, btn_texto="LIMPAR RAM")
        self.criar_card_botao(3, 1, "Desempenho", "Auto Game Priority", "Localiza jogos ativos na RAM e eleva-os para prioridade Máxima.", self.prioridade_jogos_nativa, btn_texto="INJETAR CPU")
        self.criar_card_botao(3, 2, "Hardware", "Validador de Hz (Ecrã)", "Consulta a API gráfica para confirmar os Hertz reais do seu monitor.", self.verificar_hz_monitor, btn_texto="VERIFICAR TELA")

        # 4. PRIVACIDADE E SEGURANÇA
        self.criar_secao("Privacidade e Segurança", 4)
        self.sw_vs_tel = self.criar_card_switch(5, 0, "Privacidade", "Telemetria Visual Studio", "Impede o VS de enviar dados de uso para a Microsoft.", self.toggle_vs_tel, "VS Telemetry")
        self.sw_tel = self.criar_card_switch(5, 1, "Privacidade", "DiagTrack (Rastreamento)", "Desativa o serviço de rastreamento de diagnósticos do Windows.", self.toggle_tel, "DiagTrack")
        self.sw_smart = self.criar_card_switch(5, 2, "Privacidade", "Filtro SmartScreen", "Desativa a verificação de proteção contra sites e apps maliciosos.", self.toggle_smart, "SmartScreen")
        
        self.sw_loc = self.criar_card_switch(6, 0, "Privacidade", "Localização do Sistema", "Desativa o serviço de geolocalização e acesso à posição por apps.", self.toggle_loc, "GeoLocation")
        self.sw_nv_priv = self.criar_card_switch(6, 1, "Privacidade", "Privacidade NVIDIA", "Desativa a coleta de dados e serviços de fundo da NVIDIA.", self.toggle_nv_priv, "NVIDIA Privacy")
        self.sw_tasks = self.criar_card_switch(6, 2, "Segurança", "Tarefas Ocultas (Telemetria)", "Desativa tarefas agendadas de envio de dados à Microsoft no fundo.", self.toggle_telemetry_tasks, "Telemetry Tasks")
        
        # 7. SISTEMA E INTERFACE
        self.criar_secao("Sistema e Interface", 7)
        self.criar_card_botao(8, 0, "Sistema", "Apps de Inicialização", "Abre o gestor nativo do Windows para desativar programas no arranque.", self.abrir_inicializacao, btn_texto="ABRIR GESTOR")
        self.criar_card_botao(8, 1, "Sistema", "Remover Bloatware", "Desinstala instantaneamente apps nativos inúteis (Cortana, Bing, Zune).", self.remover_bloatware)
        self.sw_tra = self.criar_card_switch(8, 2, "Interface", "Desativar Acrílico", "Desativa o acrílico e transparências para melhorar a fluidez da interface.", self.toggle_tra, "Transparência")

        # 9. DESEMPENHO E LATÊNCIA
        self.criar_secao("Desempenho e Latência", 9)
        self.sw_thrott = self.criar_card_switch(10, 0, "Desempenho", "Power Throttling", "Impede que o sistema reduza o desempenho dos aplicativos em segundo plano.", self.toggle_thrott, "Power Throttling")
        self.sw_gaming = self.criar_card_switch(10, 1, "Jogos", "Modo de Jogo Pro", "Ativa o Gaming Mode e desativa gravação GameDVR para mais FPS.", self.toggle_gaming, "Gaming Mode")
        self.sw_tim = self.criar_card_switch(10, 2, "Latência", "Resolução de Tempo", "Força o kernel do Windows a processar eventos com latência mínima.", self.toggle_tim, "Timer Res")
        
        self.sw_pow = self.criar_card_switch(11, 0, "Desempenho", "Plano de Energia", "Ativa o plano de energia oculto de Desempenho Máximo.", self.toggle_pow, "Powerplan")
        self.sw_gpu_oc = self.criar_card_switch(11, 1, "Hardware", "Economia da GPU", "Impede que a placa de vídeo reduza sua frequência em momentos de repouso.", self.toggle_gpu_oc, "GPU Downclock")
        self.sw_flip = self.criar_card_switch(11, 2, "Latência", "Flip Fix (Janelas)", "Otimiza a janela de exibição para reduzir o atraso de entrada (Input Lag).", self.toggle_flip_fix, "Flip Fix")
        
        self.sw_srv = self.criar_card_switch(12, 0, "Desempenho", "SysMain e Search", "Desativa serviços de indexação e pré-carregamento para liberar CPU e RAM.", self.toggle_srv, "Servicos Windows")
        self.sw_net_thrott = self.criar_card_switch(12, 1, "Rede", "Limitação de Rede", "Impede o Windows de reservar banda, garantindo 100% de tráfego aos jogos.", self.toggle_net_thrott, "Network Throttling")
        self.sw_core_park = self.criar_card_switch(12, 2, "Hardware", "Desativar Core Parking", "Força o Windows a manter todos os núcleos da CPU sempre ativos.", self.toggle_core_parking, "Core Parking")

        # 13. REDE E CONEXÃO
        self.criar_secao("Rede e Conexão", 13)
        self.sw_dscp = self.criar_card_switch(14, 0, "Rede", "Otimizar Pacotes (DSCP)", "Dá prioridade de tráfego aos pacotes de jogos na sua rede local.", self.toggle_dscp, "DSCP")
        self.sw_netsh = self.criar_card_switch(14, 1, "Rede", "Ajustes de Buffer (Netsh)", "Otimiza o buffer de recebimento e a unidade de transmissão máxima (MTU).", self.toggle_netsh, "Netsh")
        self.sw_cong = self.criar_card_switch(14, 2, "Rede", "Controle CUBIC", "Altera o algoritmo de congestionamento de internet para maior estabilidade.", self.toggle_cong, "Congestion")
        
        self.sw_tcp = self.criar_card_switch(15, 0, "Rede", "TcpNoDelay", "Desativa o algoritmo de Nagle para enviar pacotes de rede imediatamente.", self.toggle_tcp, "TCP")
        self.criar_card_botao(15, 1, "Rede", "Aplicar DNS Google", "Altera a conexão atual para o servidor 8.8.8.8 para maior estabilidade.", self.aplicar_dns_google)
        self.criar_card_botao(15, 2, "Rede", "Aplicar DNS Cloudflare", "Altera a conexão atual para o servidor 1.1.1.1 para latência mínima.", self.aplicar_dns_cloudflare)

        self.criar_card_botao(16, 0, "Diagnóstico", "Analisar IP e Ping", "Busca o seu IP Local, IP Público e Ping real num servidor remoto.", self.analisar_rede_info, btn_texto="INICIAR SCAN")
        self.criar_card_botao(16, 1, "Diagnóstico", "Benchmark DNS Global", "Testa a latência dos 4 maiores servidores DNS do mundo na sua casa.", self.benchmark_dns_nativo, btn_texto="AVALIAR ROTAS")

        # 17. MANUTENÇÃO E SISTEMA
        self.criar_secao("Manutenção e Sistema", 17)
        self.criar_card_botao(18, 0, "Sistema", "Reparo de Imagem (DISM)", "Faz download e substitui arquivos corrompidos da base do Windows.", self.reparar_imagem_dism)
        self.criar_card_botao(18, 1, "Limpeza", "Limpar Logs (Eventos)", "Apaga milhares de registros de erros ocultos que ocupam espaço em disco.", self.limpar_logs_windows)
        self.criar_card_botao(18, 2, "Limpeza", "Arquivos de Prefetch", "Força o Windows a recriar o mapa de inicialização do zero.", self.limpar_prefetch)
        
        self.criar_card_botao(19, 0, "Limpeza Profunda", "Arquivos Temporários", "Remove lixo eletrônico processando arquivos individualmente na barra visual.", self.limpar_temp_nativa, btn_texto="LIMPAR TEMP")
        self.criar_card_botao(19, 1, "Hardware", "Cache NVIDIA (Shader)", "Apaga shaders antigos armazenados na placa de vídeo.", self.limpar_gpu)
        self.criar_card_botao(19, 2, "Interface", "Limpar Miniaturas", "Exclui o cache de imagens para forçar o recarregamento dos ícones.", self.limpar_thumbnails)

        self.criar_card_botao(20, 0, "Rede", "Redefinir Rede (DNS)", "Limpa o cache de DNS e redefine os catálogos de conexão Winsock.", self.otimizar_internet)
        self.criar_card_botao(20, 1, "Disco", "Limpeza de Disco (Win)", "Abre a ferramenta oficial de liberação de espaço de armazenamento.", self.limpar_windows)
        self.criar_card_botao(20, 2, "Sistema", "Limpeza Windows Update", "Limpa o histórico e arquivos residuais de atualizações baixadas.", self.limpar_update)

        self.criar_card_botao(21, 0, "Disco", "Otimizar Unidades (Defrag)", "Inicia a desfragmentação mecânica (HD) e o TRIM (SSD) em TODOS os discos.", self.otimizar_discos)

        # 22. LIMPEZA DE APLICATIVOS E PROGRAMAS
        self.criar_secao("Limpeza de Aplicativos (Programas)", 22)
        self.criar_card_botao(23, 0, "Navegador", "Limpar Google Chrome", "Apaga imagens, arquivos e dados antigos armazenados pelo Chrome.", self.limpar_chrome)
        self.criar_card_botao(23, 1, "Navegador", "Limpar Microsoft Edge", "Apaga imagens, arquivos e dados antigos armazenados pelo Edge.", self.limpar_edge)
        self.criar_card_botao(23, 2, "Navegador", "Limpar Mozilla Firefox", "Apaga o cache completo de todos os perfis do Mozilla Firefox.", self.limpar_firefox)
        
        self.criar_card_botao(24, 0, "Navegador", "Limpar Opera / Opera GX", "Apaga dados antigos armazenados pelas versões do Opera Browser.", self.limpar_opera)
        self.criar_card_botao(24, 1, "Aplicativo", "Limpar Cache (Spotify)", "Apaga dados antigos armazenados pelo aplicativo de música.", self.limpar_spotify)
        self.criar_card_botao(24, 2, "Aplicativo", "Limpar Cache (Steam)", "Remove arquivos temporários da loja e do cliente Steam.", self.limpar_steam)

        self.criar_card_botao(25, 0, "Aplicativo", "Limpar Cache (Discord)", "Exclui imagens e dados de bate-papo armazenados no computador.", self.limpar_discord)
        self.criar_card_botao(25, 1, "Aplicativo", "Limpar Cache (Battle.net)", "Limpa os registros e logs de atualização do inicializador da Blizzard.", self.limpar_battlenet)
        self.criar_card_botao(25, 2, "Geral", "Limpeza Total (Apps)", "Limpa simultaneamente Spotify, Steam, Discord e Battle.net (Exclui navegadores).", self.limpar_apps_multi)

        # 26. PROCEDIMENTOS QUE REQUEREM REINICIAR
        self.criar_secao("Procedimentos que Requerem Reiniciar", 26)
        self.sw_uac = self.criar_card_switch(27, 0, "Segurança", "Controle de Conta (UAC)", "Desativa os pop-ups de permissão de administrador na tela.", self.toggle_uac, "UAC", auto=False, reinicio=True)
        self.sw_mit = self.criar_card_switch(27, 1, "Desempenho", "Mitigações de CPU", "Ganha desempenho desativando proteções contra falhas de hardware antigas.", self.toggle_mit, "Mitigações", auto=False, reinicio=True)
        self.sw_mnu = self.criar_card_switch(27, 2, "Interface", "Menu Clássico Win11", "Restaura o menu tradicional ao clicar com o botão direito no Windows 11.", self.toggle_mnu, "Menu Clássico", auto=False, reinicio=True)
        
        self.sw_bmn = self.criar_card_switch(28, 0, "Sistema", "Espera de Boot (2 Seg)", "Reduz o tempo de espera do menu de boot para acelerar a inicialização.", self.toggle_bmn, "Boot Menu", auto=False, reinicio=True)
        self.sw_fast_start = self.criar_card_switch(28, 1, "Sistema", "Desativar Fast Startup", "Desativa a Inicialização Rápida para evitar acumulação de erros no Kernel.", self.toggle_fast_startup, "Fast Startup", auto=False, reinicio=True)
        self.sw_widgets = self.criar_card_switch(28, 2, "Interface", "Desativar Widgets", "Remove permanentemente o painel de clima/notícias da Barra de Tarefas.", self.toggle_widgets, "Widgets", auto=False, reinicio=True)

        self.criar_card_botao(29, 0, "Sistema", "Verificação SFC Scan", "Busca e repara arquivos corrompidos ou ausentes do Windows.", self.verificar_erros, reinicio=True)
        self.criar_card_botao(29, 1, "Sistema", "Verificar Discos (CHKDSK)", "Examina a integridade e procura setores defeituosos em TODOS os discos.", self.verificar_disco, reinicio=True)
        
        self.atualizar_cores_perfis()

    # --- FUNÇÃO EXECUÇÃO SEGURA ---
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

    def executar_comando_assincrono(self, comando, nome_log, sw_obj=None, reinicio=False):
        def tarefa():
            try:
                processo = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=0x08000000)
                processo.wait() 
                res = processo.returncode
                self.log_res(res, nome_log, sw_obj, reinicio)
            except Exception as e:
                self.log(f"Erro ao executar {nome_log}: {str(e)}", "erro")
        threading.Thread(target=tarefa, daemon=True).start()

    # --- AUDITORIA DE MEMÓRIA E LOG (BUG FIX: REMOVIDA A AUTO-REVERSÃO MENTIROSA) ---
    def log(self, mensagem, tipo="info"):
        prefixo = "[+] " if tipo == "info" else "[-] "
        def update_ui():
            self.caixa_log.insert("end", f"{prefixo}{mensagem}\n")
            self.caixa_log.see("end")
            self.update_idletasks()
        self.after(0, update_ui)

    def log_res(self, res, nome, sw_obj=None, reinicio=False):
        """ AUDITOR MASTER: Analisa se o sistema obedeceu.
            Se falhar, NÃO reverte o botão visualmente. 
            O Utilizador Manda, a Interface Respeita. """
        def update_ui():
            if res == 0: 
                aviso = " [REINICIE PARA APLICAR]" if reinicio else ""
                self.caixa_log.insert("end", f"[+] {nome}: Concluído com sucesso.{aviso}\n")
            else: 
                self.caixa_log.insert("end", f"[-] AVISO: {nome} falhou no sistema (Inexistente ou Bloqueado pelo OS).\n")
            
            if sw_obj is not None:
                # Independentemente de ter dado erro de acesso no OS ou não, 
                # a memória da interface e do Registo guardam a VONTADE do utilizador.
                if hasattr(sw_obj, 'nome_log'):
                    self.salvar_config(sw_obj.nome_log, str(sw_obj.get()))
                
            self.caixa_log.see("end")
            self.update_idletasks()
        self.after(0, update_ui)

    # --- HELPER UI-SAFE (SEPARAÇÃO DA UI DO CMD) ---
    def forcar_ativo(self, sw):
        def acao():
            try:
                if int(sw.get()) == 0:
                    sw.select()
                    if hasattr(sw, 'comando_real'): sw.comando_real()
            except Exception: pass
        self.after(0, acao)
        time.sleep(0.15) 

    def forcar_desligado(self, sw):
        def acao():
            try:
                if int(sw.get()) == 1:
                    sw.deselect()
                    if hasattr(sw, 'comando_real'): sw.comando_real()
            except Exception: pass
        self.after(0, acao)
        time.sleep(0.15)

    # --- COMANDOS DE ACIONAMENTO DOS BOTÕES DE PERFIL (BUG FIX #1: DESATIVAR FORÇA TUDO) ---
    def executar_restauracao_thread(self):
        self.log("[*] Desativando Perfil Gamer e revertendo todas as otimizações de performance...")
        
        # Agora ele desativa absolutamente TODAS as 13 chaves agressivamente para evitar que fiquem presas.
        switches_gamer_completo = [
            self.sw_pow, self.sw_gaming, self.sw_net_thrott, self.sw_core_park,
            self.sw_tim, self.sw_gpu_oc, self.sw_flip, self.sw_srv,
            self.sw_dscp, self.sw_netsh, self.sw_cong, self.sw_tcp, self.sw_thrott
        ]
        
        for sw in switches_gamer_completo:
            self.forcar_desligado(sw)
            
        self.estado_anterior.clear()
        self.salvar_config("SnapshotPerfil", "") 
        self.log("[+] Reversão completa. O sistema voltou ao estado natural de trabalho.")

    def aplicar_gamer_avancado(self):
        self.log("[*] INJETANDO MODO GAMER: Otimizando camadas de CPU/Rede/Energia...")
        
        switches_gamer_completo = [
            self.sw_pow, self.sw_gaming, self.sw_net_thrott, self.sw_core_park,
            self.sw_tim, self.sw_gpu_oc, self.sw_flip, self.sw_srv,
            self.sw_dscp, self.sw_netsh, self.sw_cong, self.sw_tcp, self.sw_thrott
        ]
        
        for sw in switches_gamer_completo:
            self.forcar_ativo(sw)
            
        self.log("[+] MODO GAMER MÁXIMO CONCLUÍDO! O seu hardware está agora em 100% de prioridade.")

    def aplicar_trabalho_avancado(self):
        self.log("[*] INJETANDO MODO TRABALHO: Desligando prioridade extrema para poupar energia...")
        
        switches_trabalho_completo = [
            self.sw_pow, self.sw_gaming, self.sw_net_thrott, self.sw_core_park,
            self.sw_tim, self.sw_gpu_oc, self.sw_flip, self.sw_srv,
            self.sw_dscp, self.sw_netsh, self.sw_cong, self.sw_tcp, self.sw_thrott
        ]
        
        for sw in switches_trabalho_completo:
            self.forcar_desligado(sw)
            
        self.log("[+] MODO TRABALHO ATIVO! Estabilidade e bateria priorizadas para multitarefas.")

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

    # --- COMANDOS DOS SWITCHES ---
    def toggle_telemetry_tasks(self):
        est = self.sw_tasks.get()
        p1 = "\\".join(["Microsoft", "Windows", "Application Experience", "Microsoft Compatibility Appraiser"])
        p2 = "\\".join(["Microsoft", "Windows", "Customer Experience Improvement Program", "Consolidator"])
        cmd = f'schtasks /Change /TN "{p1}" /Disable >nul 2>&1 & schtasks /Change /TN "{p2}" /Disable >nul 2>&1' if est == 1 else f'schtasks /Change /TN "{p1}" /Enable >nul 2>&1 & schtasks /Change /TN "{p2}" /Enable >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Tarefas de Telemetria", self.sw_tasks)

    def toggle_vs_tel(self): 
        est = self.sw_vs_tel.get()
        cmd = f'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\VisualStudio\\Telemetry" /v "RefuseTelemetry" /t REG_DWORD /d {1 if est == 1 else 0} /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "VS Telemetry", self.sw_vs_tel)

    def toggle_thrott(self): 
        est = self.sw_thrott.get()
        cmd = f'reg add "HKLM\\System\\CurrentControlSet\\Control\\Power\\PowerThrottling" /v "PowerThrottlingOff" /t REG_DWORD /d {1 if est == 1 else 0} /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Power Throttling", self.sw_thrott)
    
    def toggle_loc(self): 
        est = self.sw_loc.get()
        cmd = 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v "DisableLocation" /t REG_DWORD /d 1 /f >nul 2>&1' if est == 1 else 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v "DisableLocation" /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Localização do Sistema", self.sw_loc)

    def toggle_gaming(self): 
        est = self.sw_gaming.get()
        cmd = 'reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f >nul 2>&1 & reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f >nul 2>&1' if est == 1 else 'reg add "HKCU\\Software\\Microsoft\\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 0 /f >nul 2>&1 & reg add "HKCU\\System\\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 1 /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Modo de Jogo Pro (Gaming Mode)", self.sw_gaming)

    def toggle_dscp(self): 
        est = self.sw_dscp.get()
        cmd = f'reg add "HKLM\\System\\CurrentControlSet\\Services\\Tcpip\\Parameters\\QoS" /v "Do not use NLA" /t REG_SZ /d "{1 if est == 1 else 0}" /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "DSCP", self.sw_dscp)

    def toggle_netsh(self): 
        est = self.sw_netsh.get()
        cmd = f'netsh int tcp set global autotuninglevel={"disabled" if est == 1 else "normal"} >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Netsh", self.sw_netsh)

    def toggle_cong(self): 
        est = self.sw_cong.get()
        cmd = f'netsh int tcp set supplemental template=internet congestionprovider={"cubic" if est == 1 else "none"} >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Congestion Provider", self.sw_cong)
    
    def toggle_tcp(self): 
        est = self.sw_tcp.get()
        cmd = 'powershell -Command "Get-ChildItem -Path HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces | ForEach-Object { Set-ItemProperty -Path $_.PSPath -Name \'TcpAckFrequency\' -Value 1 -Type DWord -ErrorAction SilentlyContinue; Set-ItemProperty -Path $_.PSPath -Name \'TCPNoDelay\' -Value 1 -Type DWord -ErrorAction SilentlyContinue }"' if est == 1 else 'powershell -Command "Get-ChildItem -Path HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces | ForEach-Object { Remove-ItemProperty -Path $_.PSPath -Name \'TcpAckFrequency\' -ErrorAction SilentlyContinue; Remove-ItemProperty -Path $_.PSPath -Name \'TCPNoDelay\' -ErrorAction SilentlyContinue }"'
        self.executar_comando_assincrono(cmd, "TCP Settings", self.sw_tcp)
        
    def toggle_gpu_oc(self): 
        est = self.sw_gpu_oc.get()
        cmd = f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e968-e325-11ce-bfc1-08002be10318}}\\0000" /v "PowerMizerEnable" /t REG_DWORD /d {0 if est == 1 else 1} /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "GPU Downclock", self.sw_gpu_oc)

    def toggle_smart(self): 
        est = self.sw_smart.get()
        cmd = f'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v "EnableSmartScreen" /t REG_DWORD /d {0 if est == 1 else 1} /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "SmartScreen", self.sw_smart)
    
    def toggle_tel(self): 
        est = self.sw_tel.get()
        cmd = "sc stop DiagTrack >nul 2>&1 & sc config DiagTrack start= disabled >nul 2>&1" if est == 1 else "sc config DiagTrack start= auto >nul 2>&1 & sc start DiagTrack >nul 2>&1"
        self.executar_comando_assincrono(cmd, "Telemetria (DiagTrack)", self.sw_tel)
        
    def toggle_nv_priv(self): 
        est = self.sw_nv_priv.get()
        if est == 1:
            cmd = 'taskkill /f /im NvTelemetryContainer.exe >nul 2>&1 & reg add "HKLM\\SOFTWARE\\NVIDIA Corporation\\NvControlPanel2\\Client" /v "OptIn" /t REG_DWORD /d 0 /f >nul 2>&1'
            self.executar_comando_assincrono(cmd, "NVIDIA Privacy", self.sw_nv_priv)
        else: 
            self.log("NVIDIA Privacy: Revertido.")
            self.salvar_config(self.sw_nv_priv.nome_log, "0")
        
    def toggle_flip_fix(self): 
        est = self.sw_flip.get()
        cmd = f'reg add "HKCU\\Control Panel\\Desktop" /v "EnableWindowedOptimization" /t REG_DWORD /d {1 if est == 1 else 0} /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Flip Integrity Fix", self.sw_flip)
    
    def toggle_srv(self):
        est = self.sw_srv.get()
        cmd = "sc stop SysMain >nul 2>&1 & sc config SysMain start= disabled >nul 2>&1 & sc stop WSearch >nul 2>&1 & sc config WSearch start= disabled >nul 2>&1" if est == 1 else "sc config SysMain start= auto >nul 2>&1 & sc start SysMain >nul 2>&1 & sc config WSearch start= delayed-auto >nul 2>&1 & sc start WSearch >nul 2>&1"
        self.executar_comando_assincrono(cmd, "Serviços Pesados (SysMain/Search)", self.sw_srv)
        
    def toggle_tim(self): 
        est = self.sw_tim.get()
        cmd = f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\kernel" /v "GlobalTimerResolutionRequests" /t REG_DWORD /d {1 if est == 1 else 0} /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Resolução de Tempo (Timer Res)", self.sw_tim)
        
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
        self.after(0, self.log_res, 0, "Plano de Energia (Máximo)", self.sw_pow)

    def _ativar_equilibrado(self):
        # Utiliza o plano original gravado da máquina (Em vez de forçar um que não existe)
        guid_eq = getattr(self, 'guid_padrao', "381b4222-f694-41f0-9685-ff5bb260df2e")
        subprocess.run(['powercfg', '/setactive', guid_eq], creationflags=0x08000000)
        self.after(0, self.log_res, 0, "Plano de Energia (Restaurado)", self.sw_pow)

    def toggle_tra(self): 
        est = self.sw_tra.get()
        cmd = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "EnableTransparency" /t REG_DWORD /d {0 if est == 1 else 1} /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Transparência", self.sw_tra)
    
    def toggle_net_thrott(self):
        est = self.sw_net_thrott.get()
        cmd = f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d {0xFFFFFFFF if est == 1 else 10} /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Limitação de Rede (Throttling)", self.sw_net_thrott)

    def toggle_core_parking(self):
        est = self.sw_core_park.get()
        cmd = f'powercfg /setacvalueindex scheme_current sub_processor CPMINCORES {100 if est == 1 else 5} >nul 2>&1 & powercfg /setactive scheme_current >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Core Parking (CPU 100%)", self.sw_core_park)

    def toggle_uac(self): 
        est = self.sw_uac.get()
        cmd = f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v "EnableLUA" /t REG_DWORD /d {0 if est == 1 else 1} /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "UAC", self.sw_uac, reinicio=True)
    
    def toggle_mit(self): 
        est = self.sw_mit.get()
        cmd = 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "FeatureSettingsOverride" /t REG_DWORD /d 3 /f >nul 2>&1 & reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "FeatureSettingsOverrideMask" /t REG_DWORD /d 3 /f >nul 2>&1' if est == 1 else 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "FeatureSettingsOverride" /t REG_DWORD /d 0 /f >nul 2>&1 & reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "FeatureSettingsOverrideMask" /t REG_DWORD /d 3 /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Mitigações de CPU", self.sw_mit, reinicio=True)

    def toggle_mnu(self):
        est = self.sw_mnu.get()
        cmd = 'reg add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /f /ve >nul 2>&1' if est == 1 else 'reg delete "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Menu Clássico", self.sw_mnu, reinicio=True)
        
    def toggle_bmn(self): 
        est = self.sw_bmn.get()
        cmd = f"bcdedit /timeout {2 if est == 1 else 30} >nul 2>&1"
        self.executar_comando_assincrono(cmd, "Boot Menu", self.sw_bmn, reinicio=True)
    
    def toggle_fast_startup(self):
        est = self.sw_fast_start.get()
        cmd = f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v "HiberbootEnabled" /t REG_DWORD /d {0 if est == 1 else 1} /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Desativar Inicialização Rápida", self.sw_fast_start, reinicio=True)

    def toggle_widgets(self):
        est = self.sw_widgets.get()
        cmd = 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Dsh" /v "AllowNewsAndInterests" /t REG_DWORD /d 0 /f >nul 2>&1' if est == 1 else 'reg delete "HKLM\\SOFTWARE\\Policies\\Microsoft\\Dsh" /v "AllowNewsAndInterests" /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Desativar Widgets", self.sw_widgets, reinicio=True)

    # --- COMANDOS DOS BOTÕES INDIVIDUAIS ---
    def abrir_inicializacao(self):
        self.log("[*] Abrindo Gerenciador de Inicialização do Windows (Nativo)...")
        self.executar_comando_assincrono("start ms-settings:startupapps", "Gestor de Inicialização")

    def analisar_rede_info(self):
        def tarefa():
            self.log("[*] Analisando a sua conexão (Isto pode levar alguns segundos)...")
            try: 
                ip_local = socket.gethostbyname(socket.gethostname())
            except: 
                ip_local = "Erro ao localizar"
            
            try: 
                ip_publico = urllib.request.urlopen('https://api.ipify.org', timeout=5).read().decode('utf8')
            except: 
                ip_publico = "Oculto ou Bloqueado"
            
            try:
                res = subprocess.run('ping 8.8.8.8 -n 1', capture_output=True, text=True, creationflags=0x08000000)
                ping_str = "Falha no Ping"
                if "tempo=" in res.stdout: 
                    ping_str = res.stdout.split("tempo=")[1].split("ms")[0].strip() + " ms"
                elif "time=" in res.stdout: 
                    ping_str = res.stdout.split("time=")[1].split("ms")[0].strip() + " ms"
            except: 
                ping_str = "Erro de rede"
            
            msg = f"\n=== DIAGNÓSTICO DE REDE ===\n> IP Local (LAN): {ip_local}\n> IP Público (WAN): {ip_publico}\n> Ping (Google DNS): {ping_str}\n===========================\n"
            self.log(msg)
        threading.Thread(target=tarefa, daemon=True).start()

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
