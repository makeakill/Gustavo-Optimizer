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

        self.title("Gustavo Optimizer v2.0 - Elite Edition")
        self.geometry("1400x900")
        
        # Lock de segurança para escrita Thread-Safe no Registo
        self.reg_lock = threading.Lock()
        
        # Variáveis de Estado para os Perfis Inteligentes
        self.estado_anterior = {}
        self.gpu_cache = "A calcular..."
        
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

        self.combo_temas = ctk.CTkOptionMenu(self.sidebar, values=list(PALETAS.keys()), command=self.mudar_tema, fg_color=self.bg_painel, button_color=self.borda, button_hover_color=self.acento, dropdown_fg_color=self.bg_painel, text_color=self.texto_branco, font=("Consolas", 11, "bold"))
        self.combo_temas.set(tema_salvo)
        self.combo_temas.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="w")

        self.lbl_cpu = ctk.CTkLabel(self.sidebar, text="⚙️ CPU: Calc...", font=("Consolas", 14, "bold"), text_color=self.texto_branco)
        self.lbl_cpu.grid(row=8, column=0, padx=20, pady=5, sticky="w")
        
        self.lbl_ram = ctk.CTkLabel(self.sidebar, text="💾 RAM: Calc...", font=("Consolas", 14, "bold"), text_color=self.texto_branco)
        self.lbl_ram.grid(row=9, column=0, padx=20, pady=5, sticky="w")
        
        self.lbl_gpu = ctk.CTkLabel(self.sidebar, text="🎮 GPU: Calc...", font=("Consolas", 14, "bold"), text_color=self.texto_branco)
        self.lbl_gpu.grid(row=10, column=0, padx=20, pady=5, sticky="nw")

        self.sw_sidebar_dark = ctk.CTkSwitch(self.sidebar, text="FORÇAR MODO ESCURO", command=self.acao_dark_mode, font=("Consolas", 12, "bold"), progress_color=self.acento, fg_color=self.borda)
        self.sw_sidebar_dark.grid(row=11, column=0, padx=20, pady=(20, 5), sticky="w")
        estado_dark = self.carregar_config("DarkModeSidebar", "0")
        if estado_dark == "1":
            self.sw_sidebar_dark.select()

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
        
        # Iniciando Thread separada de GPU para evitar micro-stuttering na interface
        threading.Thread(target=self.thread_atualizar_gpu, daemon=True).start()
        self.atualizar_hardware_ui()
        
        self.after(500, self.iniciar_verificacao_energia)

    # --- MONITORAMENTO DE HARDWARE OTIMIZADO ---
    def atualizar_hardware_ui(self):
        """ Atualiza apenas a UI na thread principal com dados rápidos ou em cache """
        uso_cpu = psutil.cpu_percent(interval=None)
        uso_ram = psutil.virtual_memory().percent
        
        self.lbl_cpu.configure(text=f"⚙️ CPU: {uso_cpu}%")
        self.lbl_ram.configure(text=f"💾 RAM: {uso_ram}%")
        self.lbl_gpu.configure(text=f"🎮 GPU: {self.gpu_cache}")
        self.after(1500, self.atualizar_hardware_ui)

    def thread_atualizar_gpu(self):
        """ Processo super pesado isolado do mainloop para garantir fluidez a 60fps na UI """
        while True:
            try:
                res = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], capture_output=True, text=True, creationflags=0x08000000)
                if res.returncode == 0: 
                    self.gpu_cache = f"{res.stdout.strip()}%"
                else:
                    self.gpu_cache = "Erro/AMD"
            except Exception: 
                self.gpu_cache = "Erro/AMD"
            time.sleep(2) # Pausa de 2 segundos para não asfixiar o CPU

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
            self.log_res(res, nome_tarefa)
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
            self.after(0, self.progress_bar.set, 0.2)
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

                # Fix for 64-bit pointers [WinError 6] Invalid Handle
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

                self.after(0, self.progress_bar.set, 0.6)
                
                command = ctypes.c_int(MemoryPurgeStandbyList)
                status = ntdll.NtSetSystemInformation(SystemMemoryListInformation, ctypes.byref(command), ctypes.sizeof(command))

                if status == 0: 
                    self.log("[+] Standby List esvaziada com sucesso! Stuttering de RAM mitigado.")
                else: 
                    self.log(f"[-] Erro NTSTATUS ao tentar purgar a memória: {hex(status)}", "erro")
                    
                kernel32.CloseHandle(hToken)
            except Exception as e: 
                self.log(f"[-] Erro Grave na Aplicação Ctypes (Standby List): {str(e)}", "erro")
            finally: 
                self.after(0, self.progress_bar.set, 1)
                time.sleep(1.5)
                self.after(0, self.progress_bar.set, 0)
        threading.Thread(target=tarefa, daemon=True).start()

    def otimizar_ram_nativa(self):
        def tarefa():
            self.log("[*] Esvaziando Working Set de processos ativos na memória RAM...")
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
                            if psapi.EmptyWorkingSet(h_process): 
                                count += 1
                            kernel32.CloseHandle(h_process)
                    except Exception: 
                        pass
                        
                    if i % max(1, total // 10) == 0: 
                        self.after(0, self.progress_bar.set, 0.2 + (i/total)*0.8)
                
                self.after(0, self.progress_bar.set, 1)
                self.log(f"[+] Smart RAM Cleaner concluído. Memória de cache ociosa libertada em {count} aplicações.")
                time.sleep(1.5)
                self.after(0, self.progress_bar.set, 0)
            except Exception as e: 
                self.log(f"[-] Erro Crítico na API do Kernel: {str(e)}", "erro")
                self.after(0, self.progress_bar.set, 0)
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
                for jogo in set(encontrados): 
                    self.log(f"[+] Jogo detetado e otimizado com sucesso: {jogo.upper()} (Prioridade ALTA)")
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
                    self.log(f"[+] Leitura de Hardware concluída: O seu ecrã está a rodar a {hz}Hz no momento.")
                    if hz <= 60: 
                        self.log("[-] Dica de Ouro: Se o seu monitor suportar mais de 60Hz, você está a perder frames. Altere isso nas configurações do Windows!", "erro")
                else: 
                    self.log("[-] Falha ao tentar ler as informações da placa de vídeo.", "erro")
            except Exception as e: 
                self.log(f"[-] Erro inesperado na leitura de hardware: {str(e)}", "erro")
                
            self.after(0, self.progress_bar.set, 1)
            time.sleep(1.5)
            self.after(0, self.progress_bar.set, 0)
        threading.Thread(target=tarefa, daemon=True).start()

    # --- NOVO BENCHMARK DE DNS (COM TELA DE SELEÇÃO E APLICADOR NATIVO) ---
    def benchmark_dns_nativo(self):
        def tarefa():
            self.log("[*] Buscando DNS Atual configurado na sua placa de rede...")
            self.after(0, self.progress_bar.set, 0)
            
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
            passo = 1.0 / len(servidores)
            progresso = 0.0
            
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
                    
                progresso += passo
                self.after(0, self.progress_bar.set, progresso)
            
            self.after(0, self.progress_bar.set, 1)
            time.sleep(0.5)
            self.after(0, self.progress_bar.set, 0)
            
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
        
        ctk.CTkLabel(janela_dns, text="[ RESULTADO DO BENCHMARK DNS ]", font=("Consolas", 16, "bold"), text_color=self.acento).pack(pady=(20, 10))
        
        frame_res = ctk.CTkFrame(janela_dns, fg_color=self.bg_painel, border_width=1, border_color=self.borda)
        frame_res.pack(expand=True, fill="both", padx=20, pady=10)
        
        opcoes_dropdown = []
        melhor_opcao = None
        
        for i, (nome, (ping, ip)) in enumerate(resultados_ordenados):
            cor = "#2ecc71" if i == 0 and ping != 999 else self.texto_branco
            texto_ping = f"{ping} ms" if ping != 999 else "Falha/TimeOut"
            texto_exibicao = f"{nome} ({ip}) - {texto_ping}"
            
            lbl_res = ctk.CTkLabel(frame_res, text=texto_exibicao, font=("Consolas", 12, "bold" if i == 0 else "normal"), text_color=cor)
            lbl_res.pack(anchor="w", padx=20, pady=5)
            
            if ping != 999:
                opcao = f"{nome} ({ip})"
                opcoes_dropdown.append(opcao)
                if i == 0: 
                    melhor_opcao = opcao
                    
        ctk.CTkLabel(janela_dns, text="Selecione o DNS para aplicar na sua placa de rede ativa:", font=("Roboto", 12), text_color=self.texto_cinza).pack(pady=(10, 5))
        
        combo_dns = ctk.CTkOptionMenu(janela_dns, values=opcoes_dropdown, fg_color=self.bg_painel, button_color=self.borda, button_hover_color=self.acento, text_color=self.texto_branco)
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
            
        btn_aplicar = ctk.CTkButton(janela_dns, text="APLICAR DNS", command=aplicar_dns_selecionado, fg_color=self.bg_painel, hover_color=self.acento, text_color=self.texto_branco, border_width=1, border_color=self.acento, font=("Consolas", 12, "bold"))
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
                    
                if total > 0 and i % max(1, total // 50) == 0: 
                    self.after(0, self.progress_bar.set, i / total)
                    
            self.after(0, self.progress_bar.set, 1)
            self.log(f"[+] Limpeza Profunda Concluída: {apagados} ficheiros apagados de forma permanente.")
            time.sleep(1.5)
            self.after(0, self.progress_bar.set, 0)
            
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
            cmd_on = 'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "AppsUseLightTheme" /t REG_DWORD /d 0 /f >nul 2>&1 & reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "SystemUsesLightTheme" /t REG_DWORD /d 0 /f >nul 2>&1'
            res = self.executar_comando(cmd_on)
        else:
            cmd_off = 'reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "AppsUseLightTheme" /t REG_DWORD /d 1 /f >nul 2>&1 & reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "SystemUsesLightTheme" /t REG_DWORD /d 1 /f >nul 2>&1'
            res = self.executar_comando(cmd_off)
            
        self.log_res(res, "Modo Escuro Forçado no Sistema")
        self.salvar_config("DarkModeSidebar", str(self.sw_sidebar_dark.get()))

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
            'pow': self.sw_pow.get(), 
            'gaming': self.sw_gaming.get(),
            'net_thrott': self.sw_net_thrott.get(), 
            'core_park': self.sw_core_park.get(),
            'tim': self.sw_tim.get(), 
            'gpu_oc': self.sw_gpu_oc.get(),
            'flip': self.sw_flip.get(), 
            'dscp': self.sw_dscp.get(),
            'tcp': self.sw_tcp.get(), 
            'thrott': self.sw_thrott.get(),
            'srv': self.sw_srv.get(), 
            'netsh': self.sw_netsh.get(),
            'cong': self.sw_cong.get(), 
            'nic_int': self.sw_nic_int.get(), 
            'visualfx': self.sw_visualfx.get()
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
        self.log(f"Perfil de cores de engenharia alterado para: {novo_tema}")

    def atualizar_cores_perfis(self):
        if not hasattr(self, 'btn_gamer') or not hasattr(self, 'btn_trabalho'): 
            return
            
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
        
        lbl_titulo = ctk.CTkLabel(janela_manual, text="[ MANUAL DE INSTRUÇÕES E DOCUMENTAÇÃO V2.0 ]", font=("Consolas", 18, "bold"), text_color=self.acento)
        lbl_titulo.pack(pady=(20, 10))
        
        caixa_texto = ctk.CTkTextbox(janela_manual, font=("Consolas", 13), fg_color=self.bg_painel, text_color=self.texto_branco, border_width=1, border_color=self.borda)
        caixa_texto.pack(expand=True, fill="both", padx=20, pady=10)

        manual_completo = (
            "================================================================================\n"
            "                 GUSTAVO OPTIMIZER v2.0 - ELITE EDITION                           \n"
            "================================================================================\n\n"
            "Bem-vindo à ferramenta definitiva de engenharia de software para Windows.\n"
            "Este manual contém a documentação técnica de todas as funções do sistema.\n\n"
            "================================================================================\n"
            "1. PERFIS E SISTEMA MASTER (PROTEÇÃO DE SESSÃO)\n"
            "================================================================================\n"
            "- MODO GAMER ELITE: Aplica 15 camadas dinâmicas de otimização em tempo real (CPU, Rede,\n"
            "  Energia). Para total extração de FPS, aplique também as funções da secção ROOT.\n"
            "- MODO TRABALHO: Reverte o sistema para as configurações de fábrica/estabilidade.\n"
            "- MASTER SISTEMA: Ativa as chaves dinâmicas da grelha de forma segura, ignorando\n"
            "  intencionalmente funções que forçam o reinício da máquina.\n\n"
            "================================================================================\n"
            "2. OTIMIZAÇÕES NATIVAS (API KERNEL)\n"
            "================================================================================\n"
            "- Purgar Standby List (ISLC): Invoca NtSetSystemInformation para esvaziar a RAM em\n"
            "  espera, aniquilando o 'Micro-Stuttering' nos jogos pesados.\n"
            "- Smart RAM Cleaner: Força processos em segundo plano a devolverem memória ociosa.\n"
            "- Auto Game Priority: Deteta jogos abertos (CS2, Valorant, etc.) e eleva o uso do CPU.\n"
            "- Benchmark DNS Global: Testa rotas e sugere o servidor com menor latência real.\n\n"
            "================================================================================\n"
            "3. DESEMPENHO PROFUNDO E LATÊNCIA\n"
            "================================================================================\n"
            "- Timer Resolution (0.5ms): Reduz o ciclo de relógio do Windows para resposta rápida.\n"
            "- Bloquear Economia GPU: Impede flutuações de Mhz (PowerMizer) que causam quedas de FPS.\n"
            "- Plano de Energia Máxima: Desbloqueia o plano de energia oculto para Workstations.\n"
            "- Core Parking: Obriga todos os núcleos lógicos do processador a manterem-se acordados.\n\n"
            "================================================================================\n"
            "4. INTERNET E REDE E-SPORTS\n"
            "================================================================================\n"
            "- Interrupt Moderation (NIC): Impede a placa de agrupar pacotes; dispara os dados na hora.\n"
            "- TCP NoDelay (Algoritmo de Nagle): Elimina o atraso TCP. Os seus tiros registam logo.\n"
            "- Controle CUBIC: Adota o algoritmo avançado de servidores Linux contra congestionamento.\n"
            "- DSCP: Define os pacotes de jogos como prioridade máxima de tráfego no router local.\n\n"
            "================================================================================\n"
            "5. COMANDOS DE ROOT (REQUEREM REINÍCIO)\n"
            "================================================================================\n"
            "- Forçar MSI Mode (GPU): Conecta a Placa Gráfica diretamente ao CPU, evitando a fila\n"
            "  da Motherboard. Reduz severamente a Latência DPC.\n"
            "- Desligar HPET & Ticks: Corta o relógio de alta precisão antigo, estabilizando FPS.\n"
            "- Mira Perfeita Raw (Rato): Remove a aceleração de ponteiro nativa oculta no Registo.\n"
            "- Mitigações de CPU: Desativa defesas antigas do Kernel que reduzem a performance.\n"
            "- Fast Startup e Boot: Impede o PC de hibernar a RAM (evitando bugs acumulados).\n\n"
            "================================================================================\n"
            "6. SISTEMA, DEBLOAT E MANUTENÇÃO\n"
            "================================================================================\n"
            "- Gerir Apps do Windows: Painel interativo para desinstalar (vermelho) ou reinstalar\n"
            "  (verde) aplicações nativas do sistema operativo em tempo real.\n"
            "- Limpezas Profundas: Rotinas automatizadas e ofuscadas para exterminar lixo do Registo,\n"
            "  Caches de Jogos (Steam, Battle.net, Discord) e Navegadores com tolerância a falhas.\n"
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
                
        btn_salvar = ctk.CTkButton(janela_manual, text="EXPORTAR TEXTO PARA .TXT", command=salvar_manual, fg_color=self.bg_painel, hover_color=self.acento, text_color=self.texto_branco, border_width=1, border_color=self.acento, font=("Consolas", 12, "bold"))
        btn_salvar.pack(pady=(10, 20))

    def abrir_painel_debloat(self):
        janela_db = ctk.CTkToplevel(self)
        janela_db.title("Painel Interativo de Debloat e Restauro")
        janela_db.geometry("550x750")
        janela_db.transient(self)
        janela_db.grab_set()
        janela_db.configure(fg_color=self.bg_main)

        lbl_titulo = ctk.CTkLabel(janela_db, text="[ GERENCIADOR DE APPS DO WINDOWS ]", font=("Consolas", 16, "bold"), text_color=self.acento)
        lbl_titulo.pack(pady=(20, 10))

        # --- LEGENDA DE IDENTIFICAÇÃO DE STATUS ---
        frame_legenda = ctk.CTkFrame(janela_db, fg_color="transparent")
        frame_legenda.pack(pady=(0, 10))
        
        cor_instalado = "#2ecc71"
        cor_ausente = "#e74c3c"
        
        ctk.CTkLabel(frame_legenda, text="■ INSTALADO", font=("Consolas", 12, "bold"), text_color=cor_instalado).pack(side="left", padx=10)
        ctk.CTkLabel(frame_legenda, text="■ NÃO INSTALADO", font=("Consolas", 12, "bold"), text_color=cor_ausente).pack(side="left", padx=10)

        scroll_db = ctk.CTkScrollableFrame(janela_db, fg_color=self.bg_painel, border_width=1, border_color=self.borda)
        scroll_db.pack(expand=True, fill="both", padx=20, pady=5)

        lbl_loading = ctk.CTkLabel(scroll_db, text="A analisar o sistema... Por favor aguarde.", font=("Consolas", 12, "italic"), text_color=self.texto_cinza)
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
                        
                    cb = ctk.CTkCheckBox(scroll_db, text=texto_exibicao, variable=var, text_color=cor_texto, fg_color=self.acento, font=("Roboto", 12, "bold"))
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
                self.after(0, self.progress_bar.set, 0)
                
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
                    self.after(0, self.progress_bar.set, prog)
                    
                self.log(f"[+] Operação de {texto_acao} (Apps) concluída com sucesso no Kernel!")
                self.after(0, self.progress_bar.set, 1)
                time.sleep(1.5)
                self.after(0, self.progress_bar.set, 0)
                self.after(0, janela_db.destroy)

            threading.Thread(target=tarefa, daemon=True).start()

        frame_botoes = ctk.CTkFrame(janela_db, fg_color="transparent")
        frame_botoes.pack(pady=(10, 20), fill="x", padx=20)
        
        btn_remover = ctk.CTkButton(frame_botoes, text="DESINSTALAR", command=lambda: executar_acao("remover"), fg_color="#FF4444", hover_color="#CC0000", font=("Consolas", 12, "bold"), width=150)
        btn_remover.pack(side="left", padx=10, expand=True)
        
        btn_reinstalar = ctk.CTkButton(frame_botoes, text="REINSTALAR", command=lambda: executar_acao("reinstalar"), fg_color="#2ecc71", hover_color="#27ae60", font=("Consolas", 12, "bold"), width=150)
        btn_reinstalar.pack(side="right", padx=10, expand=True)

    def remover_bloatware(self):
        self.log("[*] Redirecionando para o Gerenciador de Apps Avançado do Windows...")
        self.abrir_painel_debloat()

    # --- FUNÇÕES DE LAYOUT (A FUNDAÇÃO DA INTERFACE) ---
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
            # A execução da lógica despacha a tarefa através da variável 'cmd'
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
        
        # Secção 0: Perfis de Utilização
        self.criar_secao("Perfis Inteligentes V2.0", 0)
        self.btn_gamer = self.criar_card_botao(1, 0, "Desempenho", "Ativar Modo Gamer", "Aplica simultaneamente as 15 chaves dinâmicas de CPU, GPU, Rede e RAM.", self.acionar_perfil_gamer, btn_texto="ATIVAR MODO")
        self.btn_trabalho = self.criar_card_botao(1, 1, "Equilíbrio", "Ativar Modo Trabalho", "Desliga agressivamente todas as otimizações, forçando estabilidade.", self.acionar_perfil_trabalho, btn_texto="ATIVAR MODO")

        # Secção 1: Ferramentas Nativas em Python
        self.criar_secao("Otimizações Nativas (Kernel e RAM)", 2)
        self.criar_card_botao(3, 0, "Memória", "Smart RAM Cleaner", "Liberta memória em cache de processos nativos da API do Windows.", self.otimizar_ram_nativa, btn_texto="LIMPAR RAM")
        self.criar_card_botao(3, 1, "Memória", "Purgar Standby List (ISLC)", "Nível Elite: Usa a API Ntdll para exterminar Stuttering por falta de RAM.", self.purgar_standby_list_nativa, btn_texto="PURGAR STANDBY")
        self.criar_card_botao(3, 2, "Desempenho", "Auto Game Priority", "Localiza jogos ativos na RAM e eleva-os para prioridade Máxima.", self.prioridade_jogos_nativa, btn_texto="APLICAR CPU")
        
        self.criar_card_botao(4, 0, "Hardware", "Validador de Hz (Ecrã)", "Consulta a API gráfica para confirmar os Hertz reais do seu monitor.", self.verificar_hz_monitor, btn_texto="VERIFICAR TELA")
        self.criar_card_botao(4, 1, "Diagnóstico", "Benchmark DNS Global", "Testa a rota do seu DNS e os 4 mundiais, abrindo seleção para aplicar.", self.benchmark_dns_nativo, btn_texto="TESTAR E APLICAR")
        self.criar_card_botao(4, 2, "Limpeza Profunda", "Pasta Temporária Visual", "Destrói lixo eletrónico mapeando ficheiros individualmente sem CMD.", self.limpar_temp_nativa, btn_texto="LIMPAR TEMP")

        # Secção 2: Privacidade e Segurança do Utilizador
        self.criar_secao("Privacidade e Segurança", 5)
        self.sw_vs_tel = self.criar_card_switch(6, 0, "Privacidade", "Telemetria Visual Studio", "Impede o VS de enviar dados de uso para a Microsoft.", self.toggle_vs_tel, "VS Telemetry")
        self.sw_tel = self.criar_card_switch(6, 1, "Privacidade", "DiagTrack (Rastreamento)", "Desativa o serviço de rastreamento de diagnósticos do Windows.", self.toggle_tel, "DiagTrack")
        self.sw_nv_priv = self.criar_card_switch(6, 2, "Privacidade", "Privacidade NVIDIA", "Desativa a coleta de dados e serviços de fundo da NVIDIA.", self.toggle_nv_priv, "NVIDIA Privacy")
        
        self.sw_loc = self.criar_card_switch(7, 0, "Privacidade", "Localização do Sistema", "Desativa o serviço de geolocalização e acesso à posição por apps.", self.toggle_loc, "GeoLocation")
        self.sw_smart = self.criar_card_switch(7, 1, "Privacidade", "Filtro SmartScreen", "Desativa as verificações pesadas de ficheiros que abrandam o PC.", self.toggle_smart, "SmartScreen")
        self.sw_tasks = self.criar_card_switch(7, 2, "Segurança", "Tarefas Ocultas (Microsoft)", "Mata os agendadores secretos que enviam dados na calada da noite.", self.toggle_telemetry_tasks, "Telemetry Tasks")

        # Secção 3: Modificações de Sistema e Efeitos Visuais
        self.criar_secao("Sistema e Interface Visual", 8)
        self.criar_card_botao(9, 0, "Sistema", "Gerir Apps do Windows", "Abre janela Elite para apagar ou reinstalar apps nativos do Windows.", self.abrir_painel_debloat, btn_texto="ABRIR PAINEL")
        self.criar_card_botao(9, 1, "Sistema", "Apps de Inicialização", "Abre o gestor nativo do Windows para impedir programas no arranque.", self.abrir_inicializacao, btn_texto="ABRIR GESTOR")
        self.criar_card_botao(9, 2, "Sistema", "Remover Bloatware (Rápido)", "Atalho para o painel avançado de gestão das aplicações do sistema.", self.remover_bloatware, btn_texto="GERIR APPS")
        
        self.sw_tra = self.criar_card_switch(10, 0, "Interface", "Desativar Acrílico", "Para PCs fracos: Retira os efeitos de borrão pesado do Windows.", self.toggle_tra, "Transparência")
        self.sw_visualfx = self.criar_card_switch(10, 1, "Interface", "Desativar Efeitos Visuais", "Corta animações e sombras inúteis, ajustando para Desempenho Máximo.", self.toggle_visualfx, "Visual Effects")

        # Secção 4: Alterações Profundas de Desempenho e Latência
        self.criar_secao("Desempenho Profundo", 11)
        self.sw_thrott = self.criar_card_switch(12, 0, "Desempenho", "Desligar Power Throttling", "Impede o Windows de cortar energia dos programas minimizados.", self.toggle_thrott, "Power Throttling")
        self.sw_gaming = self.criar_card_switch(12, 1, "Jogos", "Modo de Jogo Pro", "Aplica o Gaming Mode e assassina as gravações Xbox GameDVR.", self.toggle_gaming, "Gaming Mode")
        self.sw_tim = self.criar_card_switch(12, 2, "Latência", "Resolução de Tempo (0.5ms)", "Força o Timer do Kernel para precisão cirúrgica de Input.", self.toggle_tim, "Timer Res")
        
        self.sw_pow = self.criar_card_switch(13, 0, "Desempenho", "Plano de Energia Máxima", "Revela e aplica o plano de Workstation escondido (Ultimate).", self.toggle_pow, "Powerplan")
        self.sw_gpu_oc = self.criar_card_switch(13, 1, "Hardware", "Bloquear Economia GPU", "A Placa de Vídeo não vai baixar os Mhz quando estiver em repouso.", self.toggle_gpu_oc, "GPU Downclock")
        self.sw_flip = self.criar_card_switch(13, 2, "Latência", "Flip Fix (Janelas)", "Altera o modo de apresentação para tirar delay de Jogos em Janela.", self.toggle_flip_fix, "Flip Fix")
        
        self.sw_srv = self.criar_card_switch(14, 0, "Desempenho", "SysMain e Search", "Apaga o Superfetch. Liberta RAM brutal desativando indexação.", self.toggle_srv, "Servicos Windows")
        self.sw_net_thrott = self.criar_card_switch(14, 1, "Rede", "Limitação de Rede (Throttling)", "Destrói a restrição de rede que o Windows impõe aos jogos.", self.toggle_net_thrott, "Network Throttling")
        self.sw_core_park = self.criar_card_switch(14, 2, "Hardware", "Desativar Core Parking", "Processador a 100%: Nenhum núcleo volta a adormecer.", self.toggle_core_parking, "Core Parking")

        # Secção 5: Modificações de Placa de Rede (E-Sports)
        self.criar_secao("Internet e Rede E-Sports", 15)
        self.sw_nic_int = self.criar_card_switch(16, 0, "Rede", "Interrupt Moderation (NIC)", "Elite: Impede a placa de rede de agrupar pacotes. Envia os tiros NA HORA.", self.toggle_nic_interrupt, "NIC Interrupt")
        self.sw_tcp = self.criar_card_switch(16, 1, "Rede", "TcpNoDelay (Nagle's Algorithm)", "Obriga o adaptador a disparar dados de TCP sem consolidação (No Delay).", self.toggle_tcp, "TCP")
        self.sw_dscp = self.criar_card_switch(16, 2, "Rede", "Otimizar Pacotes (DSCP)", "Pede ao seu router para dar prioridade de realeza aos pacotes do Jogo.", self.toggle_dscp, "DSCP")
        
        self.sw_netsh = self.criar_card_switch(17, 0, "Rede", "Ajustes de Buffer (Netsh)", "Otimiza a leitura máxima (MTU) ao nível do interpretador de comandos.", self.toggle_netsh, "Netsh")
        self.sw_cong = self.criar_card_switch(17, 1, "Rede", "Controle CUBIC", "Adota a estabilidade CUBIC de servidores Linux na sua placa de rede.", self.toggle_cong, "Congestion")
        
        self.criar_card_botao(18, 0, "Diagnóstico", "Analisar IP Privado e Ping", "Varre a sua LAN e faz request remoto à API IPify para o seu WAN.", self.analisar_rede_info, btn_texto="INICIAR SCAN")
        self.criar_card_botao(18, 1, "Rede", "Redefinir Placa (Winsock/DNS)", "Apaga o DNS Cache e aplica reset severo ao IPConfig do adaptador.", self.otimizar_internet)

        # Secção 6: Diagnósticos de Máquina e Discos
        self.criar_secao("Manutenção e Verificação", 19)
        self.criar_card_botao(20, 0, "Sistema", "Reparo de Imagem (DISM)", "Puxa pacotes sãos da Microsoft para curar corrupção no núcleo.", self.reparar_imagem_dism)
        self.criar_card_botao(20, 1, "Limpeza", "Limpar Logs de Eventos", "Executa Wevtutil para eliminar milhares de falsos erros ocultos no Disco.", self.limpar_logs_windows)
        self.criar_card_botao(20, 2, "Limpeza", "Arquivos de Prefetch", "Destrói a memória morta do arranque para forçar recriação veloz.", self.limpar_prefetch)
        
        self.criar_card_botao(21, 0, "Hardware", "Limpar Cache NVIDIA (Shader)", "Apaga shaders gráficos obsoletos diretamente do LocalAppData.", self.limpar_gpu)
        self.criar_card_botao(21, 1, "Disco", "Limpeza de Disco Avançada", "Aplica o Cleanmgr do Windows no seu nível máximo e silencioso.", self.limpar_windows)
        self.criar_card_botao(21, 2, "Sistema", "Limpar Windows Update", "Estripa o SoftwareDistribution, matando updates emperrados.", self.limpar_update)
        
        self.criar_card_botao(22, 0, "Interface", "Limpar Miniaturas", "Exclui o cache de imagens para forçar o recarregamento dos ícones.", self.limpar_thumbnails)
        self.criar_card_botao(22, 1, "Disco", "Otimizar Unidades (Defrag)", "Executa rotina TRIM em todos os SSDs e desfragmenta mecânicos.", self.otimizar_discos)

        # Secção 7: Ofuscação e Limpeza Isolada de Softwares
        self.criar_secao("Ofuscação e Limpeza de Aplicações", 23)
        self.criar_card_botao(24, 0, "Navegador", "Exterminar Cache Google", "Apaga rastros de pesquisa temporária no Chrome sem desinstalar.", self.limpar_chrome)
        self.criar_card_botao(24, 1, "Navegador", "Exterminar Cache Edge", "Força a exclusão do diretório User Data do MS Edge da sua máquina.", self.limpar_edge)
        self.criar_card_botao(24, 2, "Navegador", "Limpar Mozilla Firefox", "Apaga o cache completo de todos os perfis do Mozilla Firefox do PC.", self.limpar_firefox)

        self.criar_card_botao(25, 0, "Navegador", "Limpar Opera / Opera GX", "Apaga dados antigos armazenados pelas versões do Opera Browser.", self.limpar_opera)
        self.criar_card_botao(25, 1, "Aplicativo", "Limpar Cache Steam", "Limpa pasta AppCache. Pode resolver bugs de não atualizar jogos.", self.limpar_steam)
        self.criar_card_botao(25, 2, "Aplicativo", "Limpar Cache Discord", "Mata a árvore inteira de cache do Discord que se esconde no disco.", self.limpar_discord)
        
        self.criar_card_botao(26, 0, "Aplicativo", "Limpar Cache Spotify", "Apaga dados antigos e músicas em cache armazenadas pelo aplicativo.", self.limpar_spotify)
        self.criar_card_botao(26, 1, "Aplicativo", "Limpar Cache Battle.net", "Abre caminho livre apagando os agentes da Blizzard que ficam presos.", self.limpar_battlenet)
        self.criar_card_botao(26, 2, "Geral", "Limpeza Total (Apps)", "Limpa simultaneamente Spotify, Steam, Discord e Battle.net (Exclui navegadores).", self.limpar_apps_multi)

        # Secção 8: O Agrupamento Final (Requerem Reinício Mandatório do Computador)
        self.criar_secao("Comandos de Root (Requer Reiniciar o Computador)", 27)
        
        self.sw_msi = self.criar_card_switch(28, 0, "Latência", "Modo MSI (Para GPU)", "Força a Placa de Vídeo a comunicar sem interrupções com o CPU (DPC Baixa).", self.toggle_msi, "Modo MSI", auto=False, reinicio=True)
        self.sw_hpet = self.criar_card_switch(28, 1, "Latência", "Desligar HPET & Ticks", "Desliga o relógio lento da Motherboard para dar fluidez absurda aos FPS.", self.toggle_hpet, "HPET Ticks", auto=False, reinicio=True)
        self.sw_mouse = self.criar_card_switch(28, 2, "Hardware", "Mira Perfeita Raw (Rato)", "Mata os parâmetros invisíveis de aceleração de rato aplicados no Registo.", self.toggle_mouse, "Raw Mouse", auto=False, reinicio=True)
        
        self.sw_uac = self.criar_card_switch(29, 0, "Segurança", "Controle de Conta (UAC)", "Acaba para sempre com os escudos azuis e pop-ups irritantes de permissão.", self.toggle_uac, "UAC", auto=False, reinicio=True)
        self.sw_mit = self.criar_card_switch(29, 1, "Desempenho", "Mitigações de CPU", "Mata as proteções de hardware (Spectre) que cortam FPS. Ganho absurdo.", self.toggle_mit, "Mitigações", auto=False, reinicio=True)
        self.sw_mnu = self.criar_card_switch(29, 2, "Interface", "Menu Clássico Win11", "Extermina o design novo de 2 cliques e traz de volta o Menu Gigante antigo.", self.toggle_mnu, "Menu Clássico", auto=False, reinicio=True)
        
        self.sw_bmn = self.criar_card_switch(30, 0, "Sistema", "Espera de Boot (2 Seg)", "Acelera a tela de Dual-Boot para não ficar à espera que o sistema avance.", self.toggle_bmn, "Boot Menu", auto=False, reinicio=True)
        self.sw_fast_start = self.criar_card_switch(30, 1, "Sistema", "Desativar Fast Startup", "Protege a RAM contra corrupção ao impedir o PC de fingir que desligou.", self.toggle_fast_startup, "Fast Startup", auto=False, reinicio=True)
        self.sw_widgets = self.criar_card_switch(30, 2, "Interface", "Desativar Widgets", "Remove completamente do sistema os blocos de Notícias e Clima que sugam RAM.", self.toggle_widgets, "Widgets", auto=False, reinicio=True)

        self.criar_card_botao(31, 0, "Sistema", "Verificação SFC Scan", "Busca nos servidores Microsoft e repara arquivos corrompidos ou ausentes.", self.verificar_erros, reinicio=True)
        self.criar_card_botao(31, 1, "Sistema", "Verificar Discos (CHKDSK)", "Examina a integridade e procura setores mecânicos defeituosos em TODOS os discos.", self.verificar_disco, reinicio=True)
        
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
                self.log_res(res, nome_log, None, reinicio)
            except Exception as e: 
                self.log(f"Erro ao executar e desenhar janela de CMD {nome_log}: {str(e)}", "erro")
                
        threading.Thread(target=tarefa, daemon=True).start()

    def executar_comando_assincrono(self, comando, nome_log, sw_obj=None, reinicio=False):
        def tarefa():
            try:
                processo = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=0x08000000)
                processo.wait() 
                res = processo.returncode
                self.log_res(res, nome_log, sw_obj, reinicio)
            except Exception as e: 
                self.log(f"Erro assíncrono ao processar a chave {nome_log}: {str(e)}", "erro")
                
        threading.Thread(target=tarefa, daemon=True).start()

    # --- AUDITORIA DE MEMÓRIA (FLIP-FLOP CORRIGIDO DEFINITIVAMENTE) ---
    def log(self, mensagem, tipo="info"):
        prefixo = "[+] " if tipo == "info" else "[-] "
        
        def update_ui():
            self.caixa_log.insert("end", f"{prefixo}{mensagem}\n")
            self.caixa_log.see("end")
            self.update_idletasks()
            
        self.after(0, update_ui)

    def log_res(self, res, nome, sw_obj=None, reinicio=False):
        def update_ui():
            aviso = " [O SISTEMA REQUER REINÍCIO PARA APLICAR]" if reinicio else ""
            
            if res == 0: 
                self.caixa_log.insert("end", f"[+] {nome}: Aplicado e consolidado no sistema com sucesso.{aviso}\n")
            else: 
                self.caixa_log.insert("end", f"[-] AVISO: {nome} retornou falha a nível de sistema, mas a memória visual foi gravada e protegida.\n")
                
            if sw_obj is not None and hasattr(sw_obj, 'nome_log'): 
                self.salvar_config(sw_obj.nome_log, str(sw_obj.get()))
                
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

    def restaurar_sw(self, sw, val):
        def acao():
            try:
                if int(sw.get()) != int(val):
                    if int(val) == 1:
                        sw.select()
                    else:
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
            self.sw_dscp, self.sw_netsh, self.sw_cong, self.sw_tcp, self.sw_thrott,
            self.sw_nic_int, self.sw_visualfx
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
            self.sw_dscp, self.sw_netsh, self.sw_cong, self.sw_tcp, self.sw_thrott,
            self.sw_nic_int, self.sw_visualfx
        ]
        
        for sw in switches_gamer_dinamicos: 
            self.forcar_ativo(sw)
            
        self.log("[+] MODO GAMER MÁXIMO CONCLUÍDO! (As opções que requerem reinício foram ignoradas para proteger a sua sessão).")

    def aplicar_trabalho_avancado(self):
        self.log("[*] APLICANDO MODO TRABALHO: Desligando a prioridade extrema agressivamente...")
        
        switches_trabalho_dinamicos = [
            self.sw_pow, self.sw_gaming, self.sw_net_thrott, self.sw_core_park,
            self.sw_tim, self.sw_gpu_oc, self.sw_flip, self.sw_srv,
            self.sw_dscp, self.sw_netsh, self.sw_cong, self.sw_tcp, self.sw_thrott,
            self.sw_nic_int, self.sw_visualfx
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
            # Seleciona apenas adaptadores de rede físicos ativos para evitar erros com VPNs ou Máquinas Virtuais
            cmd = 'powershell -Command "$net = Get-NetAdapter -Physical | Where-Object { $_.Status -eq \'Up\' }; if ($net) { $net | Disable-NetAdapterInterruptModeration -ErrorAction SilentlyContinue; exit 0 } else { exit 1 }"'
        else:
            cmd = 'powershell -Command "$net = Get-NetAdapter -Physical | Where-Object { $_.Status -eq \'Up\' }; if ($net) { $net | Enable-NetAdapterInterruptModeration -ErrorAction SilentlyContinue; exit 0 } else { exit 1 }"'
            
        self.executar_comando_assincrono(cmd, "Moderação de Interrupção de Rede Pura (Adaptador NIC)", self.sw_nic_int)

    def toggle_visualfx(self):
        est = self.sw_visualfx.get()
        val = 2 if est == 1 else 0
        
        cmd = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d {val} /f >nul 2>&1'
        self.executar_comando_assincrono(cmd, "Supressão de Efeitos Visuais de Desempenho", self.sw_visualfx)

    # --- COMANDOS E SWITCHES ORIGINAIS (EXPANDIDOS E NÃO OMITIDOS) ---
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

    def toggle_netsh(self): 
        est = self.sw_netsh.get()
        comando = f'netsh int tcp set global autotuninglevel={"disabled" if est == 1 else "normal"} >nul 2>&1'
        self.executar_comando_assincrono(comando, "Manipulação de Buffers de Rede Netsh", self.sw_netsh)

    def toggle_cong(self): 
        est = self.sw_cong.get()
        comando = f'netsh int tcp set supplemental template=internet congestionprovider={"cubic" if est == 1 else "none"} >nul 2>&1'
        self.executar_comando_assincrono(comando, "Algoritmo Estável de Congestionamento (CUBIC Server)", self.sw_cong)
    
    def toggle_tcp(self): 
        est = self.sw_tcp.get()
        
        if est == 1:
            cmd = 'powershell -Command "Get-ChildItem -Path HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces | ForEach-Object { Set-ItemProperty -Path $_.PSPath -Name \'TcpAckFrequency\' -Value 1 -Type DWord -ErrorAction SilentlyContinue; Set-ItemProperty -Path $_.PSPath -Name \'TCPNoDelay\' -Value 1 -Type DWord -ErrorAction SilentlyContinue }"'
        else:
            cmd = 'powershell -Command "Get-ChildItem -Path HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces | ForEach-Object { Remove-ItemProperty -Path $_.PSPath -Name \'TcpAckFrequency\' -ErrorAction SilentlyContinue; Remove-ItemProperty -Path $_.PSPath -Name \'TCPNoDelay\' -ErrorAction SilentlyContinue }"'
            
        self.executar_comando_assincrono(cmd, "Regras de Otimização Estrita TCP Settings", self.sw_tcp)
        
    def toggle_gpu_oc(self): 
        est = self.sw_gpu_oc.get()
        comando = f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e968-e325-11ce-bfc1-08002be10318}}\\0000" /v "PowerMizerEnable" /t REG_DWORD /d {0 if est == 1 else 1} /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Força Bruta e Bloqueio de Economia da GPU", self.sw_gpu_oc)

    def toggle_smart(self): 
        est = self.sw_smart.get()
        comando = f'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v "EnableSmartScreen" /t REG_DWORD /d {0 if est == 1 else 1} /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Filtros Nativos de Avaliação SmartScreen", self.sw_smart)
    
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

    def toggle_tra(self): 
        est = self.sw_tra.get()
        comando = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "EnableTransparency" /t REG_DWORD /d {0 if est == 1 else 1} /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Destruidor de Efeitos Acrílicos e Transparência", self.sw_tra)
    
    def toggle_net_thrott(self):
        est = self.sw_net_thrott.get()
        comando = f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d {0xFFFFFFFF if est == 1 else 10} /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Estrangulamento Zero: Limitação de Rede Completamente Apagada", self.sw_net_thrott)

    def toggle_core_parking(self):
        est = self.sw_core_park.get()
        comando = f'powercfg /setacvalueindex scheme_current sub_processor CPMINCORES {100 if est == 1 else 5} >nul 2>&1 & powercfg /setactive scheme_current >nul 2>&1'
        self.executar_comando_assincrono(comando, "Bloqueador Físico de Core Parking (100% de CPU Acordada)", self.sw_core_park)

    def toggle_uac(self): 
        est = self.sw_uac.get()
        comando = f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v "EnableLUA" /t REG_DWORD /d {0 if est == 1 else 1} /f >nul 2>&1'
        self.executar_comando_assincrono(comando, "Aniquilador de Filtros de Segurança do Sistema UAC Admin", self.sw_uac, reinicio=True)
    
    def toggle_mit(self): 
        est = self.sw_mit.get()
        
        if est == 1:
            cmd = 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "FeatureSettingsOverride" /t REG_DWORD /d 3 /f >nul 2>&1 & reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "FeatureSettingsOverrideMask" /t REG_DWORD /d 3 /f >nul 2>&1'
        else:
            cmd = 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "FeatureSettingsOverride" /t REG_DWORD /d 0 /f >nul 2>&1 & reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v "FeatureSettingsOverrideMask" /t REG_DWORD /d 3 /f >nul 2>&1'
            
        self.executar_comando_assincrono(cmd, "Desligador Completo de Mitigações Nativas do Processador", self.sw_mit, reinicio=True)

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
