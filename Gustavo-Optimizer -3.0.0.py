

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\juntar_codigo.py
================================================================================

import os

# Caminho da pasta principal do seu projeto
diretorio_projeto = r"c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro"
# Nome do arquivo final que vai conter todo o texto
arquivo_saida = "codigo_fonte_completo.txt"

# Abrindo o arquivo de saída no modo de escrita
with open(arquivo_saida, "w", encoding="utf-8") as outfile:
    # Percorrendo todas as pastas e subpastas do projeto
    for root, dirs, files in os.walk(diretorio_projeto):
        for file in files:
            # Pegar apenas os arquivos que são código Python (.py)
            if file.endswith(".py"):
                caminho_completo = os.path.join(root, file)
                
                # Criando um cabeçalho para separar visualmente cada arquivo
                outfile.write(f"\n\n{'='*80}\n")
                outfile.write(f"ARQUIVO: {caminho_completo}\n")
                outfile.write(f"{'='*80}\n\n")
                
                # Lendo o conteúdo do arquivo e escrevendo no arquivo final
                try:
                    with open(caminho_completo, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Erro ao ler o arquivo: {e}\n")

print(f"Sucesso! Todo o código fonte foi copiado para: {arquivo_saida}")


================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\main.py
================================================================================

import sys
import os
import ctypes
import multiprocessing
import traceback
from pathlib import Path

def iniciar_aplicacao():
    # 1. Injeção segura de Path
    project_root = Path(__file__).resolve().parent
    root_path_str = str(project_root)
    
    if root_path_str not in sys.path:
        sys.path.insert(0, root_path_str)
    os.chdir(root_path_str)

    # 2. Importações Locais (Se faltar algum ficheiro, o erro rebenta aqui e é capturado)
    from core.logger import setup_logger
    from ui.main_window import OptimizerApp

    logger = setup_logger()
    
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        is_admin = False

    if not is_admin:
        logger.warning("Iniciado sem permissões de Administrador.")
    
    # 3. Arranque da Interface Gráfica
    app = OptimizerApp()
    app.mainloop()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    
    # MOTOR DE CAPTURA DE FALHAS SILENCIOSAS
    try:
        iniciar_aplicacao()
    except Exception as e:
        print("\n" + "="*70)
        print(" 🚨 FALHA CRÍTICA DE SISTEMA DETETADA (CRASH CATCHER) 🚨")
        print("="*70)
        
        # Imprime o erro exato na tela
        traceback.print_exc()
        
        print("="*70)
        
        # Guarda o erro no disco rígido para análise
        try:
            with open("ERRO_FATAL.txt", "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
        except: pass
            
        print(f"\n[!] O programa falhou ao abrir. A causa exata está detalhada acima.")
        print(f"[!] Se for um 'ModuleNotFoundError', verifique o nome dos ficheiros criados.")
        
        # PAUSA O TERMINAL PARA VOCÊ CONSEGUIR LER O ERRO
        input("\nPressione ENTER para fechar a janela...")
        sys.exit(1)

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\core\engine.py
================================================================================

from core.logger import get_logger
import time

logger = get_logger()

class OptimizationEngine:
    def __init__(self, hardware_info):
        self.optimizations = {}
        self.hardware_info = hardware_info

    def register(self, opt_obj):
        self.optimizations[opt_obj.id] = opt_obj

    def apply_optimization(self, opt_id):
        if opt_id not in self.optimizations:
            logger.error(f"Status: Otimização {opt_id} não encontrada no registro.")
            return False

        opt = self.optimizations[opt_id]

        if not opt.check_condition(self.hardware_info):
            logger.warning(f"Status [{opt.name}]: Operação bloqueada. Hardware incompatível.")
            return False

        logger.info(f"Progresso [{opt.name}]: Iniciando injeção no sistema...")
        success = opt.apply()

        if success:
            opt.mark_as_active(True)
            logger.info(f"Status [{opt.name}]: Otimização aplicada e validada com sucesso.")
        else:
            logger.error(f"Status [{opt.name}]: Falha na aplicação. Operação abortada.")

        return success

    def rollback_optimization(self, opt_id):
        if opt_id not in self.optimizations:
            return False

        opt = self.optimizations[opt_id]
        logger.info(f"Progresso [{opt.name}]: Restaurando parâmetros originais do sistema...")
        success = opt.rollback()

        if success:
            opt.mark_as_active(False)
            logger.info(f"Status [{opt.name}]: Reversão concluída com sucesso.")
        else:
            logger.error(f"Status [{opt.name}]: Falha crítica no rollback.")

        return success

    def get_all_optimizations(self):
        return list(self.optimizations.values())

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\core\logger.py
================================================================================

import logging
import os

def setup_logger():
    """Configura o sistema de logging persistente e para a consola."""
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logger = logging.getLogger("GustavoOptimizer")
    logger.setLevel(logging.DEBUG)

    # Formatação padrão de engenharia
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%H:%M:%S')

    # Handler para ficheiro (Auditoria do Sistema)
    file_handler = logging.FileHandler("logs/system_audit.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

def get_logger():
    """Retorna a instância ativa do logger."""
    return logging.getLogger("GustavoOptimizer")

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\core\optimization_model.py
================================================================================

from abc import ABC, abstractmethod
from rollback.snapshot_manager import SnapshotManager
from core.logger import get_logger

logger = get_logger()

class Optimization(ABC):
    def __init__(self, obj_id, name, category, description, risk_level="Baixo", requires_restart=False, is_reversible=True):
        self.id = obj_id
        self.name = name
        self.category = category
        self.description = description
        self.risk_level = risk_level
        self.requires_restart = requires_restart 
        self.is_reversible = is_reversible

    @abstractmethod
    def check_condition(self, hw) -> bool:
        """Verifica se o Hardware do PC suporta a otimização."""
        pass

    @abstractmethod
    def apply(self) -> bool:
        """Executa a injeção da otimização no Windows."""
        pass

    @abstractmethod
    def rollback(self) -> bool:
        """Reverte a otimização para o padrão do Windows."""
        pass
        
    def check_os_state(self) -> bool:
        """
        NOVO MÉTODO ARQUITETURAL (LEITURA VIVA DO SO)
        Deve ser sobrescrito em cada classe para ler o Registo ou BCD
        e confirmar se a funcionalidade ESTÁ ATIVA NESTE MOMENTO NO WINDOWS.
        
        Como estamos na transição para o Nível 3, devolvemos o valor do JSON 
        como fallback temporário para evitar quebrar classes que ainda não 
        implementaram esta leitura viva.
        """
        return SnapshotManager.is_active(self.id)

    def is_active(self) -> bool:
        """
        A Fonte da Verdade passa a ser o Windows (check_os_state) 
        em vez de um ficheiro JSON morto.
        """
        return self.check_os_state()

    def save_original_state(self, data):
        """Salva a apólice de seguro do estado original."""
        logger.info(f"Progresso [{self.name}]: Guardando backup do estado original (True Rollback).")
        # Mantemos o "True" aqui apenas para compatibilidade legada com a função SnapshotManager.
        SnapshotManager.save_state(self.id, True, data)

    def get_original_state(self):
        """Devolve a apólice de seguro."""
        return SnapshotManager.get_original_data(self.id)

    def mark_as_active(self, state: bool):
        """Guarda o estado de Backup no cofre."""
        SnapshotManager.save_state(self.id, state, self.get_original_state())

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\core\power_manager.py
================================================================================

import subprocess
from core.logger import get_logger

logger = get_logger()

class PowerPlanManager:
    ULTIMATE_PERFORMANCE_BASE_GUID = "e9a42b02-d5df-448d-aa00-03f14749eb61"
    
    @staticmethod
    def get_active_plan() -> str:
        """Lê diretamente do SO qual é o GUID do plano de energia atualmente em uso."""
        try:
            result = subprocess.run(["powercfg", "/getactivescheme"], capture_output=True, text=True, creationflags=0x08000000)
            if "GUID" in result.stdout:
                partes = result.stdout.split()
                for parte in partes:
                    if len(parte) == 36 and "-" in parte:
                        return parte.strip()
            return ""
        except Exception:
            return ""

    @staticmethod
    def get_installed_plans() -> dict:
        """Retorna um dicionário com todos os planos instalados {GUID: Nome Limpo}."""
        try:
            result = subprocess.run(["powercfg", "/list"], capture_output=True, text=True, creationflags=0x08000000)
            plans = {}
            for line in result.stdout.splitlines():
                if "GUID" in line:
                    partes = line.split()
                    for parte in partes:
                        if len(parte) == 36 and "-" in parte:
                            guid = parte.strip()
                            # Extrai o nome do plano (tudo entre o primeiro e o último parênteses)
                            nome = line[line.find("(")+1:line.rfind(")")]
                            plans[guid] = nome.strip()
            return plans
        except Exception:
            return {}

    @staticmethod
    def ensure_ultimate_performance() -> bool:
        """Idempotência com Filtro Anti-ExitLag."""
        plans = PowerPlanManager.get_installed_plans()
        target_guid = None
        
        # 1. Procura o plano NATIVO puro, ignorando planos adulterados (ex: ExitLag)
        for guid, name in plans.items():
            nome_limpo = name.lower()
            if nome_limpo == "desempenho máximo" or nome_limpo == "ultimate performance" or guid == PowerPlanManager.ULTIMATE_PERFORMANCE_BASE_GUID:
                target_guid = guid
                break
                
        # 2. Se não existir um plano puro, duplica a base original da Microsoft
        if not target_guid:
            logger.info("Progresso: Plano NATIVO 'Desempenho Máximo' não encontrado. Criando base limpa...")
            subprocess.run(["powercfg", "-duplicatescheme", PowerPlanManager.ULTIMATE_PERFORMANCE_BASE_GUID], capture_output=True, creationflags=0x08000000)
            
            novos_planos = PowerPlanManager.get_installed_plans()
            for guid, name in novos_planos.items():
                nome_limpo = name.lower()
                # Localiza o GUID gerado que não estava na lista anterior
                if (nome_limpo == "desempenho máximo" or nome_limpo == "ultimate performance") and guid not in plans:
                    target_guid = guid
                    break

        if not target_guid:
            # Fallback forçado caso o Windows esteja noutro idioma que não Pt ou En
            target_guid = PowerPlanManager.ULTIMATE_PERFORMANCE_BASE_GUID

        # 3. Ativa o plano assegurando a mudança no Kernel
        try:
            subprocess.run(["powercfg", "/setactive", target_guid], check=True, creationflags=0x08000000)
            return True
        except Exception as e:
            logger.error(f"Status: Erro ao ativar plano de energia: {e}")
            return False

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\core\system_safety.py
================================================================================

import subprocess
from core.logger import get_logger

logger = get_logger()

class SystemSafety:
    @staticmethod
    def delete_previous_restore_point(description):
        # SEGURANÇA: Remove aspas simples para evitar escape e injeção de comandos no PS
        safe_desc = description.replace("'", "")
        logger.info(f"Progresso: Verificando e limpando pontos de restauro anteriores ('{safe_desc}')...")
        
        ps_script = f"""
        $pts = Get-WmiObject -Namespace root\\default -Class SystemRestore | Where-Object {{$_.Description -eq '{safe_desc}'}}
        if ($pts) {{
            $code = '[DllImport("srclient.dll")] public static extern int SRRemoveRestorePoint(int index);'
            $type = Add-Type -MemberDefinition $code -Name "SR" -Namespace "Win32" -PassThru
            foreach ($pt in $pts) {{
                $type::SRRemoveRestorePoint($pt.SequenceNumber)
            }}
        }}
        """
        try:
            subprocess.run(["powershell.exe", "-ExecutionPolicy", "Bypass", "-NoProfile", "-Command", ps_script], shell=False, capture_output=True, creationflags=0x08000000)
        except Exception as e:
            logger.debug(f"Falha ao tentar remover ponto antigo silenciosamente: {e}")

    @staticmethod
    def create_restore_point(description="Gustavo Optimizer Backup"):
        safe_desc = description.replace("'", "")
        SystemSafety.delete_previous_restore_point(safe_desc)
        
        logger.info(f"Progresso: A criar novo Ponto de Restauro do Sistema: '{safe_desc}'...")
        try:
            cmd = ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-NoProfile', '-Command', f"Checkpoint-Computer -Description '{safe_desc}' -RestorePointType 'MODIFY_SETTINGS'"]
            process = subprocess.run(cmd, shell=False, capture_output=True, text=True, creationflags=0x08000000)
            
            if process.returncode == 0:
                logger.info("Status: Ponto de Restauro criado com sucesso. O sistema está blindado.")
                return True
            else:
                logger.warning("Status: A Proteção do Sistema (Restauro) está desativada no Windows deste PC ou excedeu o limite diário.")
                return False
        except Exception as e:
            logger.error(f"Status: Falha na comunicação com o serviço de Restauro: {e}")
            return False

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\core\task_runner.py
================================================================================

import winreg
import subprocess
from core.logger import get_logger

logger = get_logger()

class CommandRunner:
    
    @staticmethod
    def run_cmd(command_list):
        """
        Executa comandos de terminal de forma assíncrona, segura e invisível.
        SEGURANÇA: shell=False obriga a passagem de uma lista explícita, bloqueando injeção de shell.
        Retorna uma tupla: (Sucesso (bool), Stdout (str), Stderr (str))
        """
        if isinstance(command_list, str):
            logger.error("FALHA DE SEGURANÇA: run_cmd exige uma lista de argumentos, não uma string.")
            return False, "", "Security Violation: Expected list, got str."

        try:
            result = subprocess.run(
                command_list, 
                shell=False, # BLOQUEIO DE INJEÇÃO
                capture_output=True, 
                text=True, 
                creationflags=0x08000000
            )
            
            if result.returncode == 0:
                logger.info(f"Progresso: Comando executado -> {' '.join(command_list)}")
                return True, result.stdout, result.stderr
            else:
                logger.debug(f"Aviso no comando -> {' '.join(command_list)}\nDetalhe: {result.stderr}")
                return False, result.stdout, result.stderr
        except Exception as e:
            logger.error(f"Falha crítica ao executar comando [{' '.join(command_list)}]: {e}")
            return False, "", str(e)

    @staticmethod
    def read_registry_value(hkey_str, path, name):
        hkeys = {"HKLM": winreg.HKEY_LOCAL_MACHINE, "HKCU": winreg.HKEY_CURRENT_USER, "HKU": winreg.HKEY_USERS, "HKCR": winreg.HKEY_CLASSES_ROOT}
        hkey = hkeys.get(hkey_str.upper())
        if not hkey: return None, None
        try:
            with winreg.OpenKey(hkey, path, 0, winreg.KEY_READ) as key:
                val, reg_type = winreg.QueryValueEx(key, name)
                return val, reg_type
        except FileNotFoundError: return None, None
        except Exception as e:
            logger.debug(f"Falha ao ler registo {path}\\{name}: {e}")
            return None, None

    @staticmethod
    def write_registry_value(hkey_str, path, name, reg_type, value):
        current_val, _ = CommandRunner.read_registry_value(hkey_str, path, name)
        if current_val == value:
            logger.info(f"Idempotência: Chave [{name}] já possui o valor correto. Escrita no disco ignorada.")
            return True 
            
        hkeys = {"HKLM": winreg.HKEY_LOCAL_MACHINE, "HKCU": winreg.HKEY_CURRENT_USER}
        hkey = hkeys.get(hkey_str.upper())
        if not hkey: return False

        try:
            with winreg.CreateKeyEx(hkey, path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, name, 0, reg_type, value)
            logger.info(f"Progresso: Injetando nativamente no registo -> {hkey_str}\\{path}\\{name}")
            return True
        except Exception as e:
            logger.error(f"Erro ao injetar no registo ({name}): {e}")
            return False

    @staticmethod
    def delete_registry_value(hkey_str, path, name):
        hkeys = {"HKLM": winreg.HKEY_LOCAL_MACHINE, "HKCU": winreg.HKEY_CURRENT_USER}
        hkey = hkeys.get(hkey_str.upper())
        if not hkey: return False

        try:
            with winreg.OpenKey(hkey, path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, name)
            logger.info(f"Progresso: Removendo chave do registo -> {hkey_str}\\{path}\\{name}")
            return True
        except FileNotFoundError:
            return True 
        except Exception as e:
            logger.error(f"Erro ao remover chave ({name}): {e}")
            return False

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\core\theme_manager.py
================================================================================

import winreg
from core.task_runner import CommandRunner
from core.logger import get_logger

logger = get_logger()

class ThemeManager:
    @staticmethod
    def is_dark_mode_active():
        """Verifica de forma nativa se o Modo Escuro do Windows está ativo."""
        val, _ = CommandRunner.read_registry_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme")
        # No registo do Windows: 0 = Escuro, 1 = Claro
        return val == 0

    @staticmethod
    def set_dark_mode(enable: bool):
        """Injeta nativamente no registo a preferência de Tema do SO."""
        value = 0 if enable else 1
        estado_str = "Escuro" if enable else "Claro"
        logger.info(f"Progresso: Alterando o Tema do Windows para o Modo {estado_str}.")
        
        c1 = CommandRunner.write_registry_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "AppsUseLightTheme", winreg.REG_DWORD, value)
        c2 = CommandRunner.write_registry_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "SystemUsesLightTheme", winreg.REG_DWORD, value)
        
        return c1 and c2

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\core\__init__.py
================================================================================



================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\hardware\detector.py
================================================================================

import psutil
import subprocess
import threading
import time
from core.logger import get_logger

logger = get_logger()

class HardwareInfo:
    def __init__(self):
        self.ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)
        self.cpu_cores = psutil.cpu_count(logical=True)
        self.has_ssd = self._check_if_ssd()
        self.gpu_usage = "0%"

        threading.Thread(target=self._poll_gpu, daemon=True).start()

    def _check_if_ssd(self):
        try:
            # Adicionado timeout=2 para evitar que um driver de disco danificado congele o arranque
            cmd = 'powershell -Command "Get-PhysicalDisk | Select-Object -ExpandProperty MediaType"'
            res = subprocess.run(cmd, shell=False, capture_output=True, text=True, creationflags=0x08000000, timeout=2)
            return "SSD" in res.stdout.upper() or "UNSPECIFIED" in res.stdout.upper()
        except subprocess.TimeoutExpired:
            logger.warning("Status: Deteção de SSD excedeu o tempo limite. Assumindo SSD por segurança.")
            return True
        except Exception as e:
            logger.error(f"Status: Falha ao detetar tipo de disco - {e}")
            return True

    def _poll_gpu(self):
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            logger.info("Progresso: API pynvml conectada para telemetria de GPU.")
            while True:
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                self.gpu_usage = f"{util.gpu}%"
                time.sleep(2)
        except Exception as e:
            logger.debug("Status: pynvml ausente. Usando WMI/subprocesso com salvaguardas.")
            while True:
                try:
                    # Adicionado timeout=2 para impedir bloqueio eterno do processo nvidia-smi
                    res = subprocess.run(
                        ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'], 
                        capture_output=True, text=True, creationflags=0x08000000, timeout=2
                    )
                    if res.returncode == 0:
                        self.gpu_usage = f"{res.stdout.strip()}%"
                    else:
                        self.gpu_usage = "N/A"
                except subprocess.TimeoutExpired:
                    self.gpu_usage = "N/A"
                except Exception:
                    self.gpu_usage = "N/A"
                
                # Aumentado para 5s para preservar estabilidade da CPU em sistemas genéricos
                time.sleep(5)

    def get_realtime_stats(self):
        return {
            "cpu": psutil.cpu_percent(interval=None),
            "ram": psutil.virtual_memory().percent,
            "gpu": self.gpu_usage
        }

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\hardware\__init__.py
================================================================================



================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\optimizations\cpu_opts.py
================================================================================

import winreg
from core.optimization_model import Optimization
from core.task_runner import CommandRunner
from core.logger import get_logger

logger = get_logger()

class CoreParkingOpt(Optimization):
    def __init__(self):
        super().__init__("cpu_core_parking", "Desativar Core Parking", "CPU", "Impede a suspensão dos núcleos lógicos.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['powercfg', '/query', 'scheme_current', 'sub_processor', 'CPMINCORES'])
        # Busca o valor hexadecimal puro (100 = 64 em Hex), ignorando o idioma do Windows
        return sucesso and "0x00000064" in stdout
    def apply(self) -> bool:
        if self.check_os_state(): return True 
        CommandRunner.run_cmd(['powercfg', '/setacvalueindex', 'scheme_current', 'sub_processor', 'CPMINCORES', '100'])
        CommandRunner.run_cmd(['powercfg', '/setdcvalueindex', 'scheme_current', 'sub_processor', 'CPMINCORES', '100'])
        CommandRunner.run_cmd(['powercfg', '/setactive', 'scheme_current'])
        return self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        CommandRunner.run_cmd(['powercfg', '/setacvalueindex', 'scheme_current', 'sub_processor', 'CPMINCORES', '5'])
        CommandRunner.run_cmd(['powercfg', '/setdcvalueindex', 'scheme_current', 'sub_processor', 'CPMINCORES', '5'])
        CommandRunner.run_cmd(['powercfg', '/setactive', 'scheme_current'])
        return not self.check_os_state()

class PowerThrottlingOpt(Optimization):
    def __init__(self):
        super().__init__("cpu_power_throttling", "Desativar Power Throttling", "CPU", "Impede o corte de voltagem em background.", "Baixo", True, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"System\CurrentControlSet\Control\Power\PowerThrottling", "PowerThrottlingOff")
        return val == 1
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"System\CurrentControlSet\Control\Power\PowerThrottling", "PowerThrottlingOff", winreg.REG_DWORD, 1)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"System\CurrentControlSet\Control\Power\PowerThrottling", "PowerThrottlingOff", winreg.REG_DWORD, 0)
        return sucesso and not self.check_os_state()

class IdleStateMaxOpt(Optimization):
    def __init__(self):
        super().__init__("cpu_idle_state", "Desativar Idle State", "CPU", "Reduz a profundidade do sono C-State.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['powercfg', '/query', 'scheme_current', 'sub_processor', 'IDLESTATEMAX'])
        return sucesso and "0x00000000" in stdout
    def apply(self) -> bool:
        if self.check_os_state(): return True
        CommandRunner.run_cmd(['powercfg', '/setacvalueindex', 'scheme_current', 'sub_processor', 'IDLESTATEMAX', '0'])
        CommandRunner.run_cmd(['powercfg', '/setdcvalueindex', 'scheme_current', 'sub_processor', 'IDLESTATEMAX', '0'])
        CommandRunner.run_cmd(['powercfg', '/setactive', 'scheme_current'])
        return self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        CommandRunner.run_cmd(['powercfg', '/setacvalueindex', 'scheme_current', 'sub_processor', 'IDLESTATEMAX', '1'])
        CommandRunner.run_cmd(['powercfg', '/setdcvalueindex', 'scheme_current', 'sub_processor', 'IDLESTATEMAX', '1'])
        CommandRunner.run_cmd(['powercfg', '/setactive', 'scheme_current'])
        return not self.check_os_state()

class CpuEnergyPerfOpt(Optimization):
    def __init__(self):
        super().__init__("cpu_epp", "Desempenho EPP", "CPU", "Altera política EPP para performance máxima (0).", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['powercfg', '/query', 'scheme_current', 'sub_processor', 'PERFEPP'])
        return sucesso and "0x00000000" in stdout
    def apply(self) -> bool:
        if self.check_os_state(): return True
        CommandRunner.run_cmd(['powercfg', '/setacvalueindex', 'scheme_current', 'sub_processor', 'PERFEPP', '0'])
        CommandRunner.run_cmd(['powercfg', '/setdcvalueindex', 'scheme_current', 'sub_processor', 'PERFEPP', '0'])
        CommandRunner.run_cmd(['powercfg', '/setactive', 'scheme_current'])
        return self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        CommandRunner.run_cmd(['powercfg', '/setacvalueindex', 'scheme_current', 'sub_processor', 'PERFEPP', '50'])
        CommandRunner.run_cmd(['powercfg', '/setdcvalueindex', 'scheme_current', 'sub_processor', 'PERFEPP', '50'])
        CommandRunner.run_cmd(['powercfg', '/setactive', 'scheme_current'])
        return not self.check_os_state()

class NduOpt(Optimization):
    def __init__(self):
        super().__init__("cpu_ndu", "Desativar NDU", "CPU", "Pára o monitoramento NDU para evitar memory leaks.", "Baixo", True, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Services\Ndu", "Start")
        return val == 4
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Services\Ndu", "Start", winreg.REG_DWORD, 4)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Services\Ndu", "Start", winreg.REG_DWORD, 2)
        return sucesso and not self.check_os_state()

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\optimizations\gaming_opts.py
================================================================================

import winreg
import os
from core.optimization_model import Optimization
from core.task_runner import CommandRunner
from core.logger import get_logger

logger = get_logger()

class EnableGameModeOpt(Optimization):
    def __init__(self):
        super().__init__("game_mode_native", "Modo de Jogo Nativo", "Jogos", "Ativa Game Mode oficial da Microsoft.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKCU", r"Software\Microsoft\GameBar", "AutoGameModeEnabled")
        return val == 1
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Software\Microsoft\GameBar", "AutoGameModeEnabled", winreg.REG_DWORD, 1)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Software\Microsoft\GameBar", "AutoGameModeEnabled", winreg.REG_DWORD, 0)
        return sucesso and not self.check_os_state()

class DisableGameDvrOpt(Optimization):
    def __init__(self):
        super().__init__("game_disable_dvr", "Desativar Game DVR", "Jogos", "Destrói gravação em background do Xbox.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKCU", r"System\GameConfigStore", "GameDVR_Enabled")
        return val == 0
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"System\GameConfigStore", "GameDVR_Enabled", winreg.REG_DWORD, 0)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"System\GameConfigStore", "GameDVR_Enabled", winreg.REG_DWORD, 1)
        return sucesso and not self.check_os_state()

class HagsOpt(Optimization):
    def __init__(self):
        super().__init__("game_hags", "Hardware Accelerated GPU", "Jogos", "Passa controlo de memória da CPU para GPU.", "Médio", True, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode")
        return val == 2
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode", winreg.REG_DWORD, 2)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode", winreg.REG_DWORD, 1)
        return sucesso and not self.check_os_state()

class DisableFsoGlobalOpt(Optimization):
    def __init__(self):
        super().__init__("game_disable_fso", "Desativar FSO", "Jogos", "Desliga Fullscreen Optimizations globais.", "Médio", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKCU", r"System\GameConfigStore", "GameDVR_FSEBehaviorMode")
        return val == 2
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"System\GameConfigStore", "GameDVR_FSEBehaviorMode", winreg.REG_DWORD, 2)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"System\GameConfigStore", "GameDVR_FSEBehaviorMode", winreg.REG_DWORD, 0)
        return sucesso and not self.check_os_state()

class CleanDirectXCacheOpt(Optimization):
    def __init__(self):
        super().__init__("game_clean_dx", "Limpar Cache DirectX", "Jogos", "Expurga Shaders corrompidos.", "Baixo", False, False)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool: return False
    def apply(self) -> bool:
        target = os.path.expandvars(r"%LocalAppData%\NVIDIA\DXCache\*.*")
        CommandRunner.run_cmd(['cmd.exe', '/c', 'del', '/s', '/f', '/q', target])
        return True
    def rollback(self) -> bool: return True

class DisableGameBarPresenceOpt(Optimization):
    def __init__(self):
        super().__init__("game_presence_writer", "Desativar Presence", "Jogos", "Remove o monitor da Xbox de tempo jogado.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameUI", "GameBarPresenceWriterEnabled")
        return val == 0
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameUI", "GameBarPresenceWriterEnabled", winreg.REG_DWORD, 0)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameUI", "GameBarPresenceWriterEnabled", winreg.REG_DWORD, 1)
        return sucesso and not self.check_os_state()

class DisableXboxLiveAuthOpt(Optimization):
    def __init__(self):
        super().__init__("game_xbox_auth", "Parar Xbox Auth", "Jogos", "Pára o serviço de autenticação da Xbox.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['sc', 'qc', 'XblAuthManager'])
        if sucesso: 
            return "DEMAND_START" in stdout.upper() or "DISABLED" in stdout.upper()
        return False
    def apply(self) -> bool:
        if self.check_os_state(): return True
        CommandRunner.run_cmd(['sc', 'config', 'XblAuthManager', 'start=', 'demand'])
        return self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        CommandRunner.run_cmd(['sc', 'config', 'XblAuthManager', 'start=', 'auto'])
        return not self.check_os_state()

class EnableGpuHighPerfOpt(Optimization):
    def __init__(self):
        super().__init__("game_pci_power", "Poupança PCI-E", "Jogos", "Desativa o Link State Power Management.", "Médio", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['powercfg', '/query', 'scheme_current', 'sub_pciexpress', 'aspm'])
        return sucesso and "0x00000000" in stdout
    def apply(self) -> bool:
        if self.check_os_state(): return True
        CommandRunner.run_cmd(['powercfg', '/setacvalueindex', 'scheme_current', 'sub_pciexpress', 'aspm', '0'])
        CommandRunner.run_cmd(['powercfg', '/setdcvalueindex', 'scheme_current', 'sub_pciexpress', 'aspm', '0'])
        CommandRunner.run_cmd(['powercfg', '/setactive', 'scheme_current'])
        return self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        CommandRunner.run_cmd(['powercfg', '/setacvalueindex', 'scheme_current', 'sub_pciexpress', 'aspm', '2'])
        CommandRunner.run_cmd(['powercfg', '/setdcvalueindex', 'scheme_current', 'sub_pciexpress', 'aspm', '2'])
        CommandRunner.run_cmd(['powercfg', '/setactive', 'scheme_current'])
        return not self.check_os_state()

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\optimizations\latency_opts.py
================================================================================

import winreg
from core.optimization_model import Optimization
from core.task_runner import CommandRunner
from core.logger import get_logger

logger = get_logger()

class RawMouseInputOpt(Optimization):
    def __init__(self):
        super().__init__("lat_raw_mouse", "Mira Perfeita (Raw)", "Latência", "Esmaga curvas preditivas do rato.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        s, _ = CommandRunner.read_registry_value("HKCU", r"Control Panel\Mouse", "MouseSpeed")
        t1, _ = CommandRunner.read_registry_value("HKCU", r"Control Panel\Mouse", "MouseThreshold1")
        t2, _ = CommandRunner.read_registry_value("HKCU", r"Control Panel\Mouse", "MouseThreshold2")
        return s == "0" and t1 == "0" and t2 == "0"
    def apply(self) -> bool:
        c1 = CommandRunner.write_registry_value("HKCU", r"Control Panel\Mouse", "MouseSpeed", winreg.REG_SZ, "0")
        c2 = CommandRunner.write_registry_value("HKCU", r"Control Panel\Mouse", "MouseThreshold1", winreg.REG_SZ, "0")
        c3 = CommandRunner.write_registry_value("HKCU", r"Control Panel\Mouse", "MouseThreshold2", winreg.REG_SZ, "0")
        return (c1 and c2 and c3) and self.check_os_state()
    def rollback(self) -> bool:
        c1 = CommandRunner.write_registry_value("HKCU", r"Control Panel\Mouse", "MouseSpeed", winreg.REG_SZ, "1")
        c2 = CommandRunner.write_registry_value("HKCU", r"Control Panel\Mouse", "MouseThreshold1", winreg.REG_SZ, "6")
        c3 = CommandRunner.write_registry_value("HKCU", r"Control Panel\Mouse", "MouseThreshold2", winreg.REG_SZ, "10")
        return (c1 and c2 and c3) and not self.check_os_state()

class DisableUsbSelectiveSuspendOpt(Optimization):
    def __init__(self):
        super().__init__("lat_usb_suspend", "Desligar Poupança USB", "Latência", "Impede que porta USB adormeça.", "Baixo", True, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Services\USB", "DisableSelectiveSuspend")
        return val == 1
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Services\USB", "DisableSelectiveSuspend", winreg.REG_DWORD, 1)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.delete_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Services\USB", "DisableSelectiveSuspend")
        return sucesso and not self.check_os_state()

class DisableStickyKeysOpt(Optimization):
    def __init__(self):
        super().__init__("lat_sticky_keys", "Desativar Sticky Keys", "Latência", "Acaba com o interrupção do Shift.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKCU", r"Control Panel\Accessibility\StickyKeys", "Flags")
        return val == "506"
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Control Panel\Accessibility\StickyKeys", "Flags", winreg.REG_SZ, "506")
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Control Panel\Accessibility\StickyKeys", "Flags", winreg.REG_SZ, "510")
        return sucesso and not self.check_os_state()

class DisablePointerPrecisionOpt(Optimization):
    def __init__(self):
        super().__init__("lat_pointer_precis", "Desligar Precisão", "Latência", "Anula alteração virtual de DPI.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKCU", r"Control Panel\Mouse", "MouseSpeed")
        return val == "0"
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Control Panel\Mouse", "MouseSpeed", winreg.REG_SZ, "0")
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Control Panel\Mouse", "MouseSpeed", winreg.REG_SZ, "1")
        return sucesso and not self.check_os_state()

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\optimizations\memory_opts.py
================================================================================

import winreg
from core.optimization_model import Optimization
from core.task_runner import CommandRunner
from core.logger import get_logger

logger = get_logger()

class DisableSysMainOpt(Optimization):
    def __init__(self):
        super().__init__("mem_sysmain", "Desativar SysMain", "Memória", "Pára pré-carregamento (Apenas SSD).", "Baixo", False, True)
    def check_condition(self, hw): return hw.has_ssd and hw.ram_gb <= 16.5
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['sc', 'qc', 'SysMain'])
        if sucesso: return "DISABLED" in stdout or "DESATIVADO" in stdout or "DESABILITADO" in stdout
        return False
    def apply(self) -> bool:
        if self.check_os_state(): return True
        CommandRunner.run_cmd(['sc', 'stop', 'SysMain'])
        sucesso, _, _ = CommandRunner.run_cmd(['sc', 'config', 'SysMain', 'start=', 'disabled'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        CommandRunner.run_cmd(['sc', 'config', 'SysMain', 'start=', 'auto'])
        CommandRunner.run_cmd(['sc', 'start', 'SysMain'])
        return not self.check_os_state()

class DisablePrefetchOpt(Optimization):
    def __init__(self):
        super().__init__("mem_prefetch", "Desativar Prefetcher", "Memória", "Impede caches de boot no SSD.", "Baixo", True, True)
    def check_condition(self, hw): return hw.has_ssd
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters", "EnablePrefetcher")
        return val == 0
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters", "EnablePrefetcher", winreg.REG_DWORD, 0)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters", "EnablePrefetcher", winreg.REG_DWORD, 3)
        return sucesso and not self.check_os_state()

class ClearPageFileAtShutdownOpt(Optimization):
    def __init__(self):
        super().__init__("mem_clear_pagefile", "Otimizar PageFile", "Memória", "Acelera shutdown pulando limpeza de disco.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "ClearPageFileAtShutdown")
        return val == 0
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "ClearPageFileAtShutdown", winreg.REG_DWORD, 0)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "ClearPageFileAtShutdown", winreg.REG_DWORD, 1)
        return sucesso and not self.check_os_state()

class DisableMemoryCompressionOpt(Optimization):
    def __init__(self):
        super().__init__("mem_compression", "Desativar Compressão", "Memória", "Reduz uso pesado de CPU descompactando RAM.", "Médio", True, True)
    def check_condition(self, hw): return hw.ram_gb >= 16.0
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['powershell.exe', '-NoProfile', '-Command', '(Get-MMAgent).MemoryCompression'])
        if sucesso: return "False" in stdout
        return False
    def apply(self) -> bool:
        if self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['powershell.exe', '-NoProfile', '-Command', 'Disable-MMAgent -mc'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['powershell.exe', '-NoProfile', '-Command', 'Enable-MMAgent -mc'])
        return sucesso and not self.check_os_state()

class WSearchOpt(Optimization):
    def __init__(self):
        super().__init__("mem_wsearch", "Desativar Windows Search", "Memória", "Pára a indexação constante de ficheiros.", "Médio", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['sc', 'qc', 'WSearch'])
        if sucesso: return "DISABLED" in stdout or "DESATIVADO" in stdout or "DESABILITADO" in stdout
        return False
    def apply(self) -> bool:
        if self.check_os_state(): return True
        CommandRunner.run_cmd(['sc', 'stop', 'WSearch'])
        sucesso, _, _ = CommandRunner.run_cmd(['sc', 'config', 'WSearch', 'start=', 'disabled'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        CommandRunner.run_cmd(['sc', 'config', 'WSearch', 'start=', 'delayed-auto'])
        CommandRunner.run_cmd(['sc', 'start', 'WSearch'])
        return not self.check_os_state()

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\optimizations\network_opts.py
================================================================================

import winreg
from core.optimization_model import Optimization
from core.task_runner import CommandRunner
from core.logger import get_logger

logger = get_logger()

class TcpNoDelayOpt(Optimization):
    def __init__(self):
        super().__init__("net_tcp_nodelay", "TCP NoDelay", "Rede", "Desativa o algoritmo de Nagle.", "Médio", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"SOFTWARE\MSMQ\Parameters", "TCPNoDelay")
        return val == 1
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SOFTWARE\MSMQ\Parameters", "TCPNoDelay", winreg.REG_DWORD, 1)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.delete_registry_value("HKLM", r"SOFTWARE\MSMQ\Parameters", "TCPNoDelay")
        return sucesso and not self.check_os_state()

class TcpAckFrequencyOpt(Optimization):
    def __init__(self):
        super().__init__("net_tcp_ack", "TCP Ack Frequency", "Rede", "Força confirmação de cada pacote recebido.", "Médio", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['powershell.exe', '-NoProfile', '-Command', '(Get-ItemProperty HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\* -Name TcpAckFrequency -ErrorAction SilentlyContinue).TcpAckFrequency'])
        return sucesso and "1" in stdout
    def apply(self) -> bool:
        if self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['powershell.exe', '-NoProfile', '-Command', 'Get-ChildItem HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces | ForEach-Object { New-ItemProperty $_.PSPath -Name TcpAckFrequency -Value 1 -PropertyType DWORD -Force }'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['powershell.exe', '-NoProfile', '-Command', 'Get-ChildItem HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces | ForEach-Object { Remove-ItemProperty $_.PSPath -Name TcpAckFrequency -ErrorAction SilentlyContinue }'])
        return sucesso and not self.check_os_state()

class DisableRscOpt(Optimization):
    def __init__(self):
        super().__init__("net_disable_rsc", "Desativar RSC", "Rede", "Evita que a placa acumule pacotes.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['netsh', 'int', 'tcp', 'show', 'global'])
        if sucesso:
            txt = stdout.lower()
            # Cobertura ampla de idiomas (Inglês e Português)
            if "rsc" in txt or "receive segment coalescing" in txt or "agrupamento de segmentos" in txt:
                return "disable" in txt or "desativ" in txt or "desabilit" in txt
        return False
    def apply(self) -> bool:
        if self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['netsh', 'int', 'tcp', 'set', 'global', 'rsc=disabled'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['netsh', 'int', 'tcp', 'set', 'global', 'rsc=enabled'])
        return sucesso and not self.check_os_state()

class DisableLsoOpt(Optimization):
    def __init__(self):
        super().__init__("net_disable_lso", "Desativar LSO", "Rede", "Garante que pacotes grandes não corrompam a rede.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['netsh', 'int', 'tcp', 'show', 'global'])
        if sucesso:
            txt = stdout.lower()
            # Validação tolerante a idioma
            dma_off = ("netdma" not in txt) or ("netdma" in txt and ("disable" in txt or "desativ" in txt or "desabilit" in txt))
            chimney_off = ("chimney" not in txt) or ("chimney" in txt and ("disable" in txt or "desativ" in txt or "desabilit" in txt))
            return chimney_off and dma_off
        return False
    def apply(self) -> bool:
        if self.check_os_state(): return True
        CommandRunner.run_cmd(['netsh', 'int', 'tcp', 'set', 'global', 'netdma=disabled'])
        sucesso, _, _ = CommandRunner.run_cmd(['netsh', 'int', 'tcp', 'set', 'global', 'chimney=disabled'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        CommandRunner.run_cmd(['netsh', 'int', 'tcp', 'set', 'global', 'netdma=enabled'])
        sucesso, _, _ = CommandRunner.run_cmd(['netsh', 'int', 'tcp', 'set', 'global', 'chimney=enabled'])
        return sucesso and not self.check_os_state()

class TcpAutoTuningOpt(Optimization):
    def __init__(self):
        # AÇÃO IRREVERSÍVEL: Apenas restaura e garante a janela "normal" do Windows
        super().__init__("net_autotuning", "TCP Auto-Tuning", "Rede", "Ajusta janela para o padrão seguro 'normal'.", "Baixo", False, False)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool: return False
    def apply(self) -> bool:
        sucesso, _, _ = CommandRunner.run_cmd(['netsh', 'int', 'tcp', 'set', 'global', 'autotuninglevel=normal'])
        return sucesso
    def rollback(self) -> bool: return True

class TcpCubicOpt(Optimization):
    def __init__(self):
        super().__init__("net_tcp_cubic", "Controlo CUBIC", "Rede", "Aplica algoritmo de estabilidade em pacotes.", "Médio", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['netsh', 'int', 'tcp', 'show', 'supplemental'])
        if sucesso: return "cubic" in stdout.lower()
        return False
    def apply(self) -> bool:
        if self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['netsh', 'int', 'tcp', 'set', 'supplemental', 'template=internet', 'congestionprovider=cubic'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['netsh', 'int', 'tcp', 'set', 'supplemental', 'template=internet', 'congestionprovider=ctcp'])
        return sucesso and not self.check_os_state()

class FlushDnsWinsockOpt(Optimization):
    def __init__(self):
        super().__init__("net_flush_dns", "Reset DNS & Winsock", "Rede", "Expurga rotas mortas.", "Baixo", False, False)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool: return False 
    def apply(self) -> bool:
        c1, _, _ = CommandRunner.run_cmd(['ipconfig', '/flushdns'])
        c2, _, _ = CommandRunner.run_cmd(['netsh', 'winsock', 'reset'])
        return c1 and c2
    def rollback(self) -> bool: return True

class QosDscpGamingOpt(Optimization):
    def __init__(self):
        super().__init__("net_qos_dscp", "Marcação QoS DSCP", "Rede", "Prioriza pacotes do PC no roteador.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Services\Tcpip\QoS", "Do not use NLA")
        return str(val) == "1"
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Services\Tcpip\QoS", "Do not use NLA", winreg.REG_SZ, "1")
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.delete_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Services\Tcpip\QoS", "Do not use NLA")
        return sucesso and not self.check_os_state()

class DisableTeredoOpt(Optimization):
    def __init__(self):
        super().__init__("net_disable_teredo", "Desativar Teredo", "Rede", "Desliga túneis IPv6 obscuros.", "Médio", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['netsh', 'interface', 'teredo', 'show', 'state'])
        if sucesso:
            txt = stdout.lower()
            return "disable" in txt or "desativ" in txt or "desabilit" in txt
        return False
    def apply(self) -> bool:
        if self.check_os_state(): return True
        CommandRunner.run_cmd(['netsh', 'interface', 'teredo', 'set', 'state', 'disabled'])
        sucesso, _, _ = CommandRunner.run_cmd(['netsh', 'interface', 'isatap', 'set', 'state', 'default', 'disabled'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        CommandRunner.run_cmd(['netsh', 'interface', 'teredo', 'set', 'state', 'default'])
        sucesso, _, _ = CommandRunner.run_cmd(['netsh', 'interface', 'isatap', 'set', 'state', 'default'])
        return sucesso and not self.check_os_state()

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\optimizations\storage_opts.py
================================================================================

import winreg
import os
from core.optimization_model import Optimization
from core.task_runner import CommandRunner
from core.logger import get_logger

logger = get_logger()

class DisableHibernationOpt(Optimization):
    def __init__(self):
        super().__init__("stor_hibernation", "Desativar Hibernação", "Armazenamento", "Elimina o hiberfil.sys e liberta dezenas de gigabytes.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"System\CurrentControlSet\Control\Power", "HibernateEnabled")
        return val == 0
    def apply(self) -> bool:
        if self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['powercfg', '-h', 'off'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['powercfg', '-h', 'on'])
        return sucesso and not self.check_os_state()

class DisableNtfsLastAccessOpt(Optimization):
    def __init__(self):
        super().__init__("stor_ntfs_lastaccess", "NTFS Last Access", "Armazenamento", "Impede gravação de data de cada acesso.", "Baixo", True, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['fsutil', 'behavior', 'query', 'disablelastaccess'])
        if sucesso:
            stdout_lower = stdout.lower()
            return " 1" in stdout or " 3" in stdout or "desativado" in stdout_lower or "disabled" in stdout_lower
        return False
    def apply(self) -> bool:
        if self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['fsutil', 'behavior', 'set', 'disablelastaccess', '1'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['fsutil', 'behavior', 'set', 'disablelastaccess', '0'])
        return sucesso and not self.check_os_state()

class DisableNtfs83NameOpt(Optimization):
    def __init__(self):
        super().__init__("stor_ntfs_83", "NTFS 8.3 Name", "Armazenamento", "Desativa nomes MS-DOS (Acelera leitura).", "Baixo", True, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['fsutil', 'behavior', 'query', 'disable8dot3'])
        if sucesso:
            return " 1" in stdout or "desativado" in stdout.lower() or "disabled" in stdout.lower()
        return False
    def apply(self) -> bool:
        if self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['fsutil', 'behavior', 'set', 'disable8dot3', '1'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['fsutil', 'behavior', 'set', 'disable8dot3', '0'])
        return sucesso and not self.check_os_state()

class SSDReTrimOpt(Optimization):
    def __init__(self):
        super().__init__("stor_retrim", "Sinal Retrim (SSD)", "Armazenamento", "Liberta blocos vazios do SSD.", "Baixo", False, False)
    def check_condition(self, hw): return hw.has_ssd
    def check_os_state(self) -> bool: return False 
    def apply(self) -> bool:
        sucesso, _, _ = CommandRunner.run_cmd(['defrag', '/C', '/O', '/U'])
        return sucesso
    def rollback(self) -> bool: return True

class CleanTempFilesOpt(Optimization):
    def __init__(self):
        super().__init__("stor_clean_temp", "Limpar Arquivos Temporários", "Armazenamento", "Exclui lixo do %TEMP%.", "Baixo", False, False)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool: return False 
    def apply(self) -> bool:
        target1 = os.path.expandvars(r"%temp%\*.*")
        target2 = os.path.expandvars(r"%WINDIR%\Temp\*.*")
        CommandRunner.run_cmd(['cmd.exe', '/c', 'del', '/s', '/f', '/q', target1])
        CommandRunner.run_cmd(['cmd.exe', '/c', 'del', '/s', '/f', '/q', target2])
        return True 
    def rollback(self) -> bool: return True

class CleanPrefetchFolderOpt(Optimization):
    def __init__(self):
        super().__init__("stor_clean_prefetch", "Limpar Prefetch", "Armazenamento", "Apaga .pf residuais.", "Baixo", False, False)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool: return False
    def apply(self) -> bool:
        target = os.path.expandvars(r"%WINDIR%\Prefetch\*.*")
        CommandRunner.run_cmd(['cmd.exe', '/c', 'del', '/s', '/f', '/q', target])
        return True
    def rollback(self) -> bool: return True

class CleanWindowsUpdateCacheOpt(Optimization):
    def __init__(self):
        super().__init__("stor_clean_wud", "Limpar WinUpdate", "Armazenamento", "Remove atualizações travadas.", "Baixo", False, False)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool: return False
    def apply(self) -> bool:
        CommandRunner.run_cmd(['net', 'stop', 'wuauserv'])
        target = os.path.expandvars(r"%windir%\SoftwareDistribution\Download\*.*")
        CommandRunner.run_cmd(['cmd.exe', '/c', 'del', '/s', '/f', '/q', target])
        CommandRunner.run_cmd(['net', 'start', 'wuauserv'])
        return True
    def rollback(self) -> bool: return True

class DisableAutoDefragOpt(Optimization):
    def __init__(self):
        super().__init__("stor_disable_defrag", "Desativar Defrag Automático", "Armazenamento", "Impede degradação de SSD.", "Médio", False, True)
    def check_condition(self, hw): return hw.has_ssd
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['schtasks', '/query', '/TN', r'\Microsoft\Windows\Defrag\ScheduledDefrag'])
        if sucesso:
            stdout_lower = stdout.lower()
            return "disabled" in stdout_lower or "desabilitado" in stdout_lower or "desativado" in stdout_lower
        return False
    def apply(self) -> bool:
        if self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['schtasks', '/Change', '/TN', r'\Microsoft\Windows\Defrag\ScheduledDefrag', '/Disable'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        sucesso, _, _ = CommandRunner.run_cmd(['schtasks', '/Change', '/TN', r'\Microsoft\Windows\Defrag\ScheduledDefrag', '/Enable'])
        return sucesso and not self.check_os_state()

class RecycleBinCleanupOpt(Optimization):
    def __init__(self):
        super().__init__("stor_clean_recycle", "Esvaziar Lixeira", "Armazenamento", "Esvazia lixeiras de todos os discos.", "Baixo", False, False)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool: return False
    def apply(self) -> bool:
        target = os.path.expandvars(r"%systemdrive%\$Recycle.bin")
        CommandRunner.run_cmd(['cmd.exe', '/c', 'rd', '/s', '/q', target])
        return True
    def rollback(self) -> bool: return True

class DisableStorageSenseOpt(Optimization):
    def __init__(self):
        super().__init__("stor_disable_sense", "Desativar Storage Sense", "Armazenamento", "Impede apagamentos automáticos.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy", "01")
        return val == 0
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy", "01", winreg.REG_DWORD, 0)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy", "01", winreg.REG_DWORD, 1)
        return sucesso and not self.check_os_state()

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\optimizations\system_opts.py
================================================================================

import winreg
from core.optimization_model import Optimization
from core.task_runner import CommandRunner
from core.power_manager import PowerPlanManager
from core.logger import get_logger

logger = get_logger()

class UltimatePerformancePlanOpt(Optimization):
    def __init__(self):
        super().__init__("sys_ultimate_power", "Desempenho Máximo", "CPU", "Gera e ativa o plano nativo de Workstation (Sem duplicar).", "Médio", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        planos = PowerPlanManager.get_installed_plans()
        guid_ativo = PowerPlanManager.get_active_plan()
        if guid_ativo in planos:
            nome_ativo = planos[guid_ativo].lower()
            return nome_ativo == "desempenho máximo" or nome_ativo == "ultimate performance" or guid_ativo == PowerPlanManager.ULTIMATE_PERFORMANCE_BASE_GUID
        return False
    def apply(self) -> bool:
        if self.check_os_state(): return True
        sucesso = PowerPlanManager.ensure_ultimate_performance()
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        if not self.check_os_state(): return True
        BALANCED_GUID = "381b4222-f694-41f0-9685-ff5bb260df2e"
        sucesso, _, _ = CommandRunner.run_cmd(['powercfg', '/setactive', BALANCED_GUID])
        return sucesso and not self.check_os_state()

class DisableFastStartupOpt(Optimization):
    def __init__(self):
        super().__init__("sys_fast_startup", "Desativar Início Rápido", "Sistema", "Garante Boot real evitando bugs.", "Médio", True, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Power", "HiberbootEnabled")
        return val == 0
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Power", "HiberbootEnabled", winreg.REG_DWORD, 0)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SYSTEM\CurrentControlSet\Control\Session Manager\Power", "HiberbootEnabled", winreg.REG_DWORD, 1)
        return sucesso and not self.check_os_state()

class VisualEffectsPerfOpt(Optimization):
    def __init__(self):
        super().__init__("sys_visual_fx", "Desempenho Visual", "Sistema", "Remove animações e sombras da interface.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting")
        return val == 2
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", winreg.REG_DWORD, 2)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", winreg.REG_DWORD, 0)
        return sucesso and not self.check_os_state()

class DisableTransparencyOpt(Optimization):
    def __init__(self):
        super().__init__("sys_transparency", "Desativar Transparência", "Sistema", "Poupa o GPU para não desenhar vidros.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency")
        return val == 0
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", winreg.REG_DWORD, 0)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", winreg.REG_DWORD, 1)
        return sucesso and not self.check_os_state()

class DisableTelemetryTasksOpt(Optimization):
    def __init__(self):
        super().__init__("sys_telemetry", "Desativar CEIP", "Sistema", "Mata tarefas da MS que leem disco.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['schtasks', '/query', '/TN', r'\Microsoft\Windows\Customer Experience Improvement Program\Consolidator'])
        return sucesso and ("Disabled" in stdout or "Desabilitado" in stdout or "Desativado" in stdout)
    def apply(self) -> bool:
        CommandRunner.run_cmd(['schtasks', '/Change', '/TN', r'\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser', '/Disable'])
        CommandRunner.run_cmd(['schtasks', '/Change', '/TN', r'\Microsoft\Windows\Customer Experience Improvement Program\Consolidator', '/Disable'])
        return self.check_os_state()
    def rollback(self) -> bool:
        CommandRunner.run_cmd(['schtasks', '/Change', '/TN', r'\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser', '/Enable'])
        CommandRunner.run_cmd(['schtasks', '/Change', '/TN', r'\Microsoft\Windows\Customer Experience Improvement Program\Consolidator', '/Enable'])
        return not self.check_os_state()

class DisableCortanaOpt(Optimization):
    def __init__(self):
        super().__init__("sys_cortana", "Desativar Cortana", "Sistema", "Bloqueia a assistente inútil.", "Baixo", True, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana")
        return val == 0
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana", winreg.REG_DWORD, 0)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana", winreg.REG_DWORD, 1)
        return sucesso and not self.check_os_state()

class DisableActivityHistoryOpt(Optimization):
    def __init__(self):
        super().__init__("sys_activity_hist", "Histórico Atividade", "Sistema", "Proíbe envio da timeline para a cloud.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\System", "EnableActivityFeed")
        return val == 0
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\System", "EnableActivityFeed", winreg.REG_DWORD, 0)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SOFTWARE\Policies\Microsoft\Windows\System", "EnableActivityFeed", winreg.REG_DWORD, 1)
        return sucesso and not self.check_os_state()

class ClassicContextMenuOpt(Optimization):
    def __init__(self):
        super().__init__("sys_context_menu", "Menu Clássico (Win11)", "Sistema", "Regressa ao menu do botão direito clássico.", "Baixo", True, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKCU", r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32", "")
        return val is not None
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKCU", r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32", "", winreg.REG_SZ, "")
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        CommandRunner.delete_registry_value("HKCU", r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32", "")
        CommandRunner.delete_registry_value("HKCU", r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}", "")
        return not self.check_os_state()

class BootTimeoutOpt(Optimization):
    def __init__(self):
        super().__init__("sys_boot_timeout", "Espera BCD (2s)", "Sistema", "Acelera o arranque de boot.", "Médio", True, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        sucesso, stdout, _ = CommandRunner.run_cmd(['bcdedit', '/enum'])
        return sucesso and "timeout" in stdout and "2" in stdout
    def apply(self) -> bool:
        sucesso, _, _ = CommandRunner.run_cmd(['bcdedit', '/timeout', '2'])
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso, _, _ = CommandRunner.run_cmd(['bcdedit', '/timeout', '30'])
        return sucesso and not self.check_os_state()

class DisableErrorReportingOpt(Optimization):
    def __init__(self):
        super().__init__("sys_wer", "Desativar WerSvc", "Sistema", "Impede relatórios de erro lentos.", "Baixo", False, True)
    def check_condition(self, hw): return True
    def check_os_state(self) -> bool:
        val, _ = CommandRunner.read_registry_value("HKLM", r"SOFTWARE\Microsoft\Windows\Windows Error Reporting", "Disabled")
        return val == 1
    def apply(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SOFTWARE\Microsoft\Windows\Windows Error Reporting", "Disabled", winreg.REG_DWORD, 1)
        return sucesso and self.check_os_state()
    def rollback(self) -> bool:
        sucesso = CommandRunner.write_registry_value("HKLM", r"SOFTWARE\Microsoft\Windows\Windows Error Reporting", "Disabled", winreg.REG_DWORD, 0)
        return sucesso and not self.check_os_state()

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\optimizations\__init__.py
================================================================================



================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\rollback\snapshot_manager.py
================================================================================

import json
import os
import sys
import threading
from core.logger import get_logger

logger = get_logger()

# DEPLOYMENT PREP: Garante que o ficheiro é salvo ao lado do executável (.exe) final e não na pasta temporária do PyInstaller
def get_persistence_path(filename):
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(".")
    return os.path.join(base_dir, filename)

SNAPSHOT_FILE = get_persistence_path("snapshot_data.json")

class SnapshotManager:
    _lock = threading.RLock()

    @staticmethod
    def load_snapshot():
        with SnapshotManager._lock:
            if not os.path.exists(SNAPSHOT_FILE):
                return {}
            try:
                with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Status: Erro ao carregar snapshot: {e}")
                return {}

    @staticmethod
    def save_state(opt_id, is_active: bool, original_data=None):
        with SnapshotManager._lock:
            data = SnapshotManager.load_snapshot()
            
            if not isinstance(data.get(opt_id), dict):
                data[opt_id] = {}

            data[opt_id]["is_active"] = is_active
            if original_data is not None:
                data[opt_id]["original_data"] = original_data

            try:
                with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Status: Erro crítico ao salvar snapshot no disco: {e}")

    @staticmethod
    def get_original_data(opt_id):
        with SnapshotManager._lock:
            data = SnapshotManager.load_snapshot()
            opt_data = data.get(opt_id, {})
            if isinstance(opt_data, dict):
                return opt_data.get("original_data", None)
            return None 

    @staticmethod
    def is_active(opt_id):
        with SnapshotManager._lock:
            data = SnapshotManager.load_snapshot()
            opt_data = data.get(opt_id, {})
            if isinstance(opt_data, dict):
                return opt_data.get("is_active", False)
            elif isinstance(opt_data, bool):
                return opt_data
            return False

    @staticmethod
    def clear_snapshots():
        with SnapshotManager._lock:
            if os.path.exists(SNAPSHOT_FILE):
                try:
                    os.remove(SNAPSHOT_FILE)
                except Exception as e:
                    logger.error(f"Status: Falha ao limpar ficheiro de snapshots: {e}")

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\rollback\__init__.py
================================================================================



================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\ui\main_window.py
================================================================================

import customtkinter as ctk
import threading
import time
import inspect
import os
import sys
import logging

from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

from core.logger import get_logger
from hardware.detector import HardwareInfo
from core.engine import OptimizationEngine
from ui.widgets import OptimizationSwitch, CATEGORY_COLORS
from core.optimization_model import Optimization
from core.system_safety import SystemSafety
from core.theme_manager import ThemeManager
from rollback.snapshot_manager import SnapshotManager
from ui.theme import THEMES

logger = get_logger()

class TextboxHandler(logging.Handler):
    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox

    def emit(self, record):
        msg = self.format(record) + "\n"
        self.textbox.after(0, lambda m=msg: self.textbox.insert("end", m))
        self.textbox.after(0, lambda: self.textbox.see("end"))

class OptimizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gustavo Optimizer v3.0.0 - Pro Edition")
        self.geometry("1300x850") 
        self.minsize(1100, 750)
        
        self.current_theme = THEMES["Deep Void (Dracula)"]
        self.configure(fg_color=self.current_theme["bg_main"])

        self.hw = HardwareInfo()
        self.engine = OptimizationEngine(self.hw)
        
        self.gamer_mode_active = False
        self.work_mode_active = False

        # --- MAPEAMENTO INTELIGENTE PARA PYINSTALLER ---
        def resource_path(relative_path):
            """ Obtém o caminho absoluto, compatível com o executável final e modo dev """
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)

        self.icon_path = resource_path("icon.ico")
        # -----------------------------------------------

        self.setup_window_icon()
        self.setup_tray_icon_system()
        self.bind("<Unmap>", self.on_window_minimize)

        self.carregar_todas_otimizacoes()
        self.setup_ui()
        self.detect_active_profiles() 
        self.setup_in_memory_logger()
        self.update_telemetry()

    def setup_window_icon(self):
        try:
            if os.path.exists(self.icon_path):
                self.iconbitmap(self.icon_path)
        except Exception as e:
            logger.debug(f"Aviso: Não foi possível carregar o ícone da janela principal. {e}")

    def get_tray_image(self):
        try:
            if os.path.exists(self.icon_path):
                return Image.open(self.icon_path)
        except Exception:
            pass
        img = Image.new('RGB', (64, 64), color=(43, 43, 43))
        d = ImageDraw.Draw(img)
        d.rectangle((16, 16, 48, 48), fill=(0, 120, 215))
        return img

    def setup_tray_icon_system(self):
        image = self.get_tray_image()
        menu = pystray.Menu(
            item('Restaurar Optimizer', self.tray_restore_window, default=True),
            item('Sair do Programa', self.tray_quit_window)
        )
        self.tray_icon = pystray.Icon("GustavoOptimizer", image, "Gustavo Optimizer Pro v3.0", menu)

    def on_window_minimize(self, event):
        if event.widget == self and self.state() == 'iconic':
            self.withdraw()
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def tray_restore_window(self, icon, item):
        self.tray_icon.stop() 
        self.after(0, self.deiconify_safe)

    def deiconify_safe(self):
        self.deiconify()
        self.state('normal')

    def tray_quit_window(self, icon, item):
        self.tray_icon.stop()
        self.after(0, self.destroy)

    # =========================================================================
    # CARREGAMENTO DE PLUGINS (REFATORADO PARA SUPORTAR PYINSTALLER)
    # =========================================================================
    def carregar_todas_otimizacoes(self):
        contador = 0
        
        # 1. Importação explícita: O PyInstaller agora "vê" estes ficheiros e embutirá no .exe
        from optimizations import cpu_opts, gaming_opts, latency_opts, memory_opts, network_opts, storage_opts, system_opts
        
        # 2. Lista de módulos a extrair
        modulos = [cpu_opts, gaming_opts, latency_opts, memory_opts, network_opts, storage_opts, system_opts]
        
        # 3. Extração dinâmica das classes (Motor Inteligente mantido)
        for module in modulos:
            try:
                for nome, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, Optimization) and obj is not Optimization:
                        self.engine.register(obj())
                        contador += 1
            except Exception as e:
                logger.error(f"Status: Falha ao carregar módulo {module.__name__}: {e}")
                
        logger.info(f"Sucesso: {contador} plugins de sistema descobertos e injetados.")

    def setup_ui(self):
        t = self.current_theme
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=340, corner_radius=0, fg_color=t["bg_sidebar"], border_width=1, border_color=t["border"])
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.lbl_title = ctk.CTkLabel(self.sidebar, text="[ GUSTAVO OPTIMIZER ]", font=("Consolas", 22, "bold"), text_color=t["btn_primary"])
        self.lbl_title.pack(pady=(35, 15), padx=20, anchor="w")

        self.frame_theme = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.frame_theme.pack(pady=(0, 10), padx=20, fill="x")
        self.switch_dark_mode = ctk.CTkSwitch(self.frame_theme, text="Modo Escuro (Windows)", font=("Segoe UI", 13, "bold"), text_color=t["text_main"], progress_color=t["btn_primary"], command=self.toggle_windows_theme)
        self.switch_dark_mode.pack(side="left")
        if ThemeManager.is_dark_mode_active(): self.switch_dark_mode.select()

        self.lbl_theme = ctk.CTkLabel(self.sidebar, text="TEMA DA INTERFACE", font=("Segoe UI", 10, "bold"), text_color=t["text_dim"])
        self.lbl_theme.pack(pady=(0, 2), padx=20, anchor="w")
        
        self.theme_selector = ctk.CTkOptionMenu(
            self.sidebar,
            values=list(THEMES.keys()),
            command=self.change_app_theme,
            font=("Segoe UI", 12, "bold"),
            fg_color=t["card_border"],
            button_color=t["border"],
            button_hover_color=t["card_bg"],
            text_color=t["text_main"],
            dropdown_fg_color=t["card_bg"],
            dropdown_text_color=t["text_main"]
        )
        self.theme_selector.pack(pady=(0, 15), padx=20, fill="x")

        self.btn_backup = ctk.CTkButton(self.sidebar, text="CRIAR PONTO DE RESTAURO", command=self.manual_restore_point, fg_color=t["btn_neutral"], hover_color=t["border"], text_color=t["text_main"], font=("Segoe UI", 12, "bold"), height=40, corner_radius=8, border_width=1, border_color=t["border"])
        self.btn_backup.pack(pady=8, padx=20, fill="x")

        self.btn_gamer = ctk.CTkButton(self.sidebar, text="MODO GAMER EXTREMO", command=self.run_gamer_profile, fg_color=t["btn_primary"], text_color=t["accent_text"], font=("Segoe UI", 13, "bold"), height=40, corner_radius=8)
        self.btn_gamer.pack(pady=8, padx=20, fill="x")

        self.btn_work = ctk.CTkButton(self.sidebar, text="MODO TRABALHO SEGURO", command=self.run_work_profile, fg_color="transparent", border_width=2, border_color=t["btn_primary"], text_color=t["btn_primary"], font=("Segoe UI", 13, "bold"), height=40, corner_radius=8)
        self.btn_work.pack(pady=8, padx=20, fill="x")

        self.btn_emergency = ctk.CTkButton(self.sidebar, text="DESFAZER TODAS AS ALTERAÇÕES", command=self.emergency_rollback, fg_color=t["btn_danger"], hover_color=t["warning"], text_color="#FFFFFF", font=("Segoe UI", 12, "bold"), height=40, corner_radius=8)
        self.btn_emergency.pack(pady=(15, 8), padx=20, fill="x")

        self.macro_progress = ctk.CTkProgressBar(self.sidebar, height=6, progress_color=t["btn_primary"], fg_color=t["card_border"])
        self.macro_progress.pack(pady=(0, 15), padx=20, fill="x")
        self.macro_progress.set(0)

        self.lbl_log = ctk.CTkLabel(self.sidebar, text="AUDITORIA EM TEMPO REAL", font=("Segoe UI", 11, "bold"), text_color=t["text_dim"])
        self.lbl_log.pack(pady=(0, 0), padx=20, anchor="w")
        self.txt_log = ctk.CTkTextbox(self.sidebar, fg_color=t["log_bg"], text_color=t["text_main"], font=("Consolas", 12), border_width=1, border_color=t["card_border"], corner_radius=8)
        self.txt_log.pack(pady=(5, 20), padx=20, fill="both", expand=True)

        self.frame_telemetry = ctk.CTkFrame(self, fg_color=t["card_bg"], corner_radius=12, border_width=1, border_color=t["card_border"], height=80)
        self.frame_telemetry.grid(row=0, column=1, sticky="ew", padx=25, pady=(25, 0))
        self.frame_telemetry.grid_columnconfigure((0, 1, 2), weight=1)
        self.frame_telemetry.grid_propagate(False)

        self.lbl_cpu_title = ctk.CTkLabel(self.frame_telemetry, text="PROCESSADOR", font=("Segoe UI", 10, "bold"), text_color=t["text_dim"])
        self.lbl_cpu_title.grid(row=0, column=0, padx=20, pady=(15, 0), sticky="w")
        self.lbl_cpu_val = ctk.CTkLabel(self.frame_telemetry, text="0%", font=("Consolas", 18, "bold"), text_color=t["success"])
        self.lbl_cpu_val.grid(row=0, column=0, padx=20, pady=(15, 0), sticky="e")
        self.bar_cpu = ctk.CTkProgressBar(self.frame_telemetry, height=8, progress_color=t["success"], fg_color=t["card_border"])
        self.bar_cpu.grid(row=1, column=0, padx=20, pady=(5, 15), sticky="ew")

        self.lbl_ram_title = ctk.CTkLabel(self.frame_telemetry, text="MEMÓRIA RAM", font=("Segoe UI", 10, "bold"), text_color=t["text_dim"])
        self.lbl_ram_title.grid(row=0, column=1, padx=20, pady=(15, 0), sticky="w")
        self.lbl_ram_val = ctk.CTkLabel(self.frame_telemetry, text="0%", font=("Consolas", 18, "bold"), text_color=t["success"])
        self.lbl_ram_val.grid(row=0, column=1, padx=20, pady=(15, 0), sticky="e")
        self.bar_ram = ctk.CTkProgressBar(self.frame_telemetry, height=8, progress_color=t["success"], fg_color=t["card_border"])
        self.bar_ram.grid(row=1, column=1, padx=20, pady=(5, 15), sticky="ew")

        self.lbl_gpu_title = ctk.CTkLabel(self.frame_telemetry, text="PLACA GRÁFICA", font=("Segoe UI", 10, "bold"), text_color=t["text_dim"])
        self.lbl_gpu_title.grid(row=0, column=2, padx=20, pady=(15, 0), sticky="w")
        self.lbl_gpu_val = ctk.CTkLabel(self.frame_telemetry, text="0%", font=("Consolas", 18, "bold"), text_color=t["success"])
        self.lbl_gpu_val.grid(row=0, column=2, padx=20, pady=(15, 0), sticky="e")
        self.bar_gpu = ctk.CTkProgressBar(self.frame_telemetry, height=8, progress_color=t["success"], fg_color=t["card_border"])
        self.bar_gpu.grid(row=1, column=2, padx=20, pady=(5, 15), sticky="ew")

        self.tabview = ctk.CTkTabview(self, fg_color=t["bg_main"], bg_color="transparent", segmented_button_selected_color=t["card_border"], segmented_button_unselected_color=t["card_bg"], segmented_button_fg_color=t["bg_sidebar"], text_color=t["text_main"])
        self.tabview.grid(row=1, column=1, sticky="nsew", padx=25, pady=(10, 20))

        categorias_mapeadas = ["CPU", "Memória", "Armazenamento", "Rede", "Jogos", "Sistema", "Latência"]
        self.scrolls = {}
        self.counters = {}

        for cat in categorias_mapeadas:
            tab = self.tabview.add(cat)
            scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
            scroll.pack(expand=True, fill="both")
            scroll.grid_columnconfigure((0, 1), weight=1)
            self.scrolls[cat] = scroll
            self.counters[cat] = {'r': 0, 'c': 0}

        self.apply_tab_colors()

        self.switches = []
        all_opts = self.engine.get_all_optimizations()
        sorted_opts = sorted(all_opts, key=lambda x: (not getattr(x, 'is_reversible', True), getattr(x, 'requires_restart', False)))

        for o in sorted_opts:
            cat = o.category
            if cat not in self.scrolls:
                if "Outros" not in self.scrolls:
                    tab_outros = self.tabview.add("Outros")
                    scroll_outros = ctk.CTkScrollableFrame(tab_outros, fg_color="transparent")
                    scroll_outros.pack(expand=True, fill="both")
                    scroll_outros.grid_columnconfigure((0, 1), weight=1)
                    self.scrolls["Outros"] = scroll_outros
                    self.counters["Outros"] = {'r': 0, 'c': 0}
                    self.apply_tab_colors() 
                cat = "Outros"

            scroll_parent = self.scrolls[cat]
            r = self.counters[cat]['r']
            c = self.counters[cat]['c']

            sw = OptimizationSwitch(scroll_parent, o, theme=self.current_theme, engine=self.engine)
            sw.grid(row=r, column=c, padx=15, pady=15, sticky="nsew")
            self.switches.append(sw)

            self.counters[cat]['c'] += 1
            if self.counters[cat]['c'] > 1:
                self.counters[cat]['c'] = 0
                self.counters[cat]['r'] += 1

    def apply_tab_colors(self):
        for cat_name, color in CATEGORY_COLORS.items():
            try:
                if cat_name in self.tabview._segmented_button._buttons_dict:
                    self.tabview._segmented_button._buttons_dict[cat_name].configure(text_color=color)
            except: pass

    def change_app_theme(self, theme_name):
        self.current_theme = THEMES[theme_name]
        t = self.current_theme
        self.configure(fg_color=t["bg_main"])
        self.sidebar.configure(fg_color=t["bg_sidebar"], border_color=t["border"])
        self.lbl_title.configure(text_color=t["btn_primary"])
        self.switch_dark_mode.configure(progress_color=t["btn_primary"], text_color=t["text_main"])
        self.theme_selector.configure(fg_color=t["card_border"], button_color=t["border"], button_hover_color=t["card_bg"], text_color=t["text_main"])
        self.btn_backup.configure(fg_color=t["btn_neutral"], hover_color=t["border"], text_color=t["text_main"])
        self.btn_emergency.configure(fg_color=t["btn_danger"], hover_color=t["warning"])
        
        if self.gamer_mode_active:
            self.btn_gamer.configure(fg_color=t["btn_action"], text_color="#000000")
        else:
            self.btn_gamer.configure(fg_color=t["btn_primary"], text_color=t["accent_text"])
            
        if self.work_mode_active:
            self.btn_work.configure(fg_color=t["btn_action"], text_color="#000000", border_width=0)
        else:
            self.btn_work.configure(fg_color="transparent", text_color=t["btn_primary"], border_width=2)
        
        self.txt_log.configure(fg_color=t["log_bg"], text_color=t["text_main"], border_color=t["card_border"])
        self.frame_telemetry.configure(fg_color=t["card_bg"], border_color=t["card_border"])
        for sw in self.switches: sw.apply_theme(t)

    def update_telemetry(self):
        stats = self.hw.get_realtime_stats()
        t = self.current_theme
        cpu_val = stats['cpu']
        self.lbl_cpu_val.configure(text=f"{cpu_val:.1f}%")
        self.bar_cpu.set(cpu_val / 100.0)
        ram_val = stats['ram']
        self.lbl_ram_val.configure(text=f"{ram_val:.1f}%")
        self.bar_ram.set(ram_val / 100.0)
        
        gpu_str = stats['gpu'].replace('%', '')
        try:
            gpu_val = float(gpu_str)
            self.lbl_gpu_val.configure(text=f"{gpu_val:.1f}%")
            self.bar_gpu.set(gpu_val / 100.0)
        except:
            self.lbl_gpu_val.configure(text="N/A")
            self.bar_gpu.set(0)
            
        self.after(1000, self.update_telemetry)

    def setup_in_memory_logger(self):
        log_handler = TextboxHandler(self.txt_log)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
        log_handler.setFormatter(formatter)
        get_logger().addHandler(log_handler)

    def detect_active_profiles(self):
        gamer_cats = ["Latência", "Jogos", "CPU", "Rede"]
        gamer_switches = [s for s in self.switches if s.opt.category in gamer_cats and getattr(s.opt, 'is_reversible', True) and not getattr(s.opt, 'requires_restart', False)]
        if gamer_switches:
            active_gamer = sum(1 for s in gamer_switches if s.control.get() == 1)
            if active_gamer / len(gamer_switches) >= 0.6:
                self.gamer_mode_active = True
                self.btn_gamer.configure(fg_color=self.current_theme["btn_action"], text_color="#000000", text="DESATIVAR MODO GAMER")

        work_cats = ["Memória", "Sistema", "Armazenamento", "Rede"]
        work_switches = [s for s in self.switches if s.opt.category in work_cats and getattr(s.opt, 'is_reversible', True) and not getattr(s.opt, 'requires_restart', False)]
        if work_switches:
            active_work = sum(1 for s in work_switches if s.control.get() == 1)
            if active_work / len(work_switches) >= 0.6 and not self.gamer_mode_active:
                self.work_mode_active = True
                self.btn_work.configure(fg_color=self.current_theme["btn_action"], text_color="#000000", border_width=0, text="DESATIVAR MODO TRABALHO")

    def manual_restore_point(self):
        self.btn_backup.configure(state="disabled", text="A CRIAR BACKUP...")
        def worker():
            try: SystemSafety.create_restore_point("Gustavo Optimizer V3 - Backup")
            finally: self.after(0, lambda: self.btn_backup.configure(state="normal", text="CRIAR PONTO DE RESTAURO"))
        threading.Thread(target=worker, daemon=True).start()

    def emergency_rollback(self):
        self.btn_emergency.configure(state="disabled", text="A REVERTER...")
        def worker():
            try:
                reversibles = [s for s in self.switches if getattr(s.opt, 'is_reversible', True) and (s.control.get() == 1 or s.opt.is_active())]
                for s in reversibles: s.force_set(False)
                SnapshotManager.clear_snapshots()
                logger.info("====== SISTEMA RESTAURADO ======")
            finally: 
                self.after(0, lambda: self.btn_emergency.configure(state="normal", text="DESFAZER TODAS AS ALTERAÇÕES"))
                self.after(0, lambda: self.btn_gamer.configure(fg_color=self.current_theme["btn_primary"], text_color=self.current_theme["accent_text"], text="MODO GAMER EXTREMO"))
                self.after(0, lambda: self.btn_work.configure(fg_color="transparent", text_color=self.current_theme["btn_primary"], border_width=2, text="MODO TRABALHO SEGURO"))
                self.gamer_mode_active = False
                self.work_mode_active = False
        threading.Thread(target=worker, daemon=True).start()

    def toggle_windows_theme(self):
        is_dark = (self.switch_dark_mode.get() == 1)
        threading.Thread(target=lambda: ThemeManager.set_dark_mode(is_dark), daemon=True).start()

    def run_gamer_profile(self):
        self.btn_gamer.configure(state="disabled")
        def task():
            try:
                if not self.gamer_mode_active:
                    logger.info("====== INICIANDO PERFIL GAMER V3.0 ======")
                    target_cats = ["Latência", "Jogos", "CPU", "Rede"]
                    sws = [s for s in self.switches if s.opt.category in target_cats and not getattr(s.opt, 'requires_restart', False)]
                    for s in sws: s.force_set(True)
                    self.gamer_mode_active = True
                    self.after(0, lambda: self.btn_gamer.configure(fg_color=self.current_theme["btn_action"], text_color="#000000", text="DESATIVAR MODO GAMER"))
                else:
                    logger.info("====== REVERTENDO PERFIL GAMER V3.0 ======")
                    target_cats = ["Latência", "Jogos", "CPU", "Rede"]
                    sws = [s for s in self.switches if s.opt.category in target_cats and not getattr(s.opt, 'requires_restart', False)]
                    for s in sws: s.force_set(False)
                    self.gamer_mode_active = False
                    self.after(0, lambda: self.btn_gamer.configure(fg_color=self.current_theme["btn_primary"], text_color=self.current_theme["accent_text"], text="MODO GAMER EXTREMO"))
            finally: self.after(0, lambda: self.btn_gamer.configure(state="normal"))
        threading.Thread(target=task, daemon=True).start()

    def run_work_profile(self):
        self.btn_work.configure(state="disabled")
        def task():
            try:
                if not self.work_mode_active:
                    logger.info("====== INICIANDO PERFIL TRABALHO V3.0 ======")
                    if self.gamer_mode_active:
                        self.gamer_mode_active = False
                        self.after(0, lambda: self.btn_gamer.configure(fg_color=self.current_theme["btn_primary"], text_color=self.current_theme["accent_text"], text="MODO GAMER EXTREMO"))

                    target_cats = ["Memória", "Sistema", "Armazenamento", "Rede", "Latência", "Jogos", "CPU"]
                    sws = [s for s in self.switches if s.opt.category in target_cats and not getattr(s.opt, 'requires_restart', False)]
                    
                    for s in sws:
                        if s.opt.category in ["Memória", "Sistema", "Armazenamento", "Rede"]:
                            s.force_set(True) 
                        elif s.opt.category in ["Latência", "Jogos", "CPU"]:
                            s.force_set(False)
                        
                    self.work_mode_active = True
                    self.after(0, lambda: self.btn_work.configure(fg_color=self.current_theme["btn_action"], text_color="#000000", border_width=0, text="DESATIVAR MODO TRABALHO"))
                else:
                    logger.info("====== REVERTENDO PERFIL TRABALHO V3.0 ======")
                    target_cats_revert = ["Memória", "Sistema", "Armazenamento", "Rede"]
                    sws = [s for s in self.switches if s.opt.category in target_cats_revert and not getattr(s.opt, 'requires_restart', False)]
                    for s in sws: s.force_set(False)
                    self.work_mode_active = False
                    self.after(0, lambda: self.btn_work.configure(fg_color="transparent", text_color=self.current_theme["btn_primary"], border_width=2, text="MODO TRABALHO SEGURO"))
            finally:
                self.after(0, lambda: self.btn_work.configure(state="normal"))
        threading.Thread(target=task, daemon=True).start()

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\ui\theme.py
================================================================================

# ui/theme.py

THEMES = {
    "Deep Void (Dracula)": {
        "bg_main": "#0D0D12",
        "bg_sidebar": "#13131A",
        "border": "#1E1E24",
        "card_bg": "#1A1A24",
        "card_border": "#2B2B36",
        "accent1": "#00E5FF",      
        "accent2": "#B388EB",      
        "accent_text": "#000000",  
        "success": "#00E676",
        "warning": "#FF9100",
        "text_main": "#FFFFFF",
        "text_dim": "#A1A1AA",
        "log_bg": "#08080B",
        # CORES SEMÂNTICAS DE BOTÃO (TEMA ESCURO)
        "btn_primary": "#00E5FF",   # Ciano (Principal)
        "btn_action": "#4CAF50",    # Verde suave (Ações construtivas)
        "btn_neutral": "#424242",   # Cinza escuro (Neutro)
        "btn_danger": "#EF5350"     # Vermelho suave (Perigo/Limpeza)
    },
    "Cyberpunk Neon": {
        "bg_main": "#0B0C10",
        "bg_sidebar": "#121218",
        "border": "#2A2A35",
        "card_bg": "#16171F",
        "card_border": "#2A2A35",
        "accent1": "#F3E600",      
        "accent2": "#FF007F",      
        "accent_text": "#000000",
        "success": "#00FF9D",
        "warning": "#FF8C00",
        "text_main": "#E0E0E0",
        "text_dim": "#8A8A93",
        "log_bg": "#050608",
        # CORES SEMÂNTICAS DE BOTÃO
        "btn_primary": "#F3E600",
        "btn_action": "#00FF9D",
        "btn_neutral": "#2A2A35",
        "btn_danger": "#FF003C"
    },
    "Midnight Blue": {
        "bg_main": "#060D1E",
        "bg_sidebar": "#0A142F",
        "border": "#12214A",
        "card_bg": "#0D1B3E",
        "card_border": "#182C5E",
        "accent1": "#4AB3FF",      
        "accent2": "#0078D7",      
        "accent_text": "#000000",
        "success": "#107C10",
        "warning": "#F39C12",
        "text_main": "#FFFFFF",
        "text_dim": "#B0C4DE",
        "log_bg": "#040914",
        # CORES SEMÂNTICAS DE BOTÃO
        "btn_primary": "#4AB3FF",
        "btn_action": "#107C10",
        "btn_neutral": "#182C5E",
        "btn_danger": "#E81123"
    },
    "Light Minimalist (Claro)": {
        "bg_main": "#F3F4F6",
        "bg_sidebar": "#FFFFFF",
        "border": "#E5E7EB",
        "card_bg": "#FFFFFF",
        "card_border": "#D1D5DB",
        "accent1": "#3B82F6",      
        "accent2": "#6366F1",      
        "accent_text": "#FFFFFF",
        "success": "#10B981",
        "warning": "#F59E0B",
        "text_main": "#111827",
        "text_dim": "#4B5563",
        "log_bg": "#F9FAFB",
        # CORES SEMÂNTICAS DE BOTÃO (TEMA CLARO)
        "btn_primary": "#3B82F6",   # Azul (Principal)
        "btn_action": "#10B981",    # Verde (Ação)
        "btn_neutral": "#D1D5DB",   # Cinza claro (Neutro)
        "btn_danger": "#EF4444"     # Vermelho moderado (Perigo)
    }
}

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\ui\widgets.py
================================================================================

import customtkinter as ctk
import threading
from core.logger import get_logger

logger = get_logger()

CATEGORY_COLORS = {
    "CPU": "#FF5252",
    "Memória": "#448AFF",
    "Armazenamento": "#69F0AE",
    "Rede": "#E040FB",
    "Jogos": "#FF4081",
    "Sistema": "#FFD740",
    "Latência": "#18FFFF",
    "Outros": "#B0BEC5"
}

class OptimizationSwitch(ctk.CTkFrame):
    def __init__(self, master, opt, theme, engine=None, **kwargs):
        self.theme = theme
        super().__init__(master, corner_radius=15, height=170, border_width=2, border_color=self.theme["card_border"], fg_color=self.theme["card_bg"], **kwargs)
        self.grid_propagate(False)
        self.opt = opt
        self.engine = engine
        
        self.cat_color = CATEGORY_COLORS.get(opt.category, CATEGORY_COLORS["Outros"])
        self.lbl_cat = ctk.CTkLabel(self, text=f" {opt.category.upper()} ", font=("Segoe UI", 10, "bold"), text_color=self.cat_color, fg_color=self.theme["bg_sidebar"], corner_radius=6)
        self.lbl_cat.place(x=18, y=15)
        
        if getattr(self.opt, 'requires_restart', False):
            self.lbl_restart = ctk.CTkLabel(self, text=" REINÍCIO NECESSÁRIO ", font=("Segoe UI", 9, "bold"), text_color=self.theme["warning"], fg_color=self.theme["bg_sidebar"], corner_radius=6)
            self.lbl_restart.place(x=100, y=15)
        
        self.lbl_tit = ctk.CTkLabel(self, text=opt.name, font=("Segoe UI", 15, "bold"), text_color=self.theme["text_main"])
        self.lbl_tit.place(x=18, y=42)

        self.lbl_desc = ctk.CTkLabel(self, text=opt.description, font=("Segoe UI", 12), text_color=self.theme["text_dim"], wraplength=240, justify="left")
        self.lbl_desc.place(x=18, y=72)

        if getattr(self.opt, 'is_reversible', True):
            switch_text = "ATIVAR (Reinício nec.)" if getattr(self.opt, 'requires_restart', False) else "ATIVAR"
            self.control = ctk.CTkSwitch(self, text=switch_text, font=("Segoe UI", 12, "bold"), progress_color=self.theme["btn_primary"], button_color="#FFFFFF", button_hover_color="#E4E4E7", command=self.toggle)
            if opt.is_active():
                self.control.select()
                self.set_active_visuals()
        else:
            self.control = ctk.CTkButton(self, text="EXECUTAR LIMPEZA", font=("Segoe UI", 12, "bold"), fg_color=self.theme["btn_danger"], hover_color=self.theme["warning"], text_color="#FFFFFF", command=self.execute_once, width=140, corner_radius=8)

        self.control.place(relx=0.95, rely=0.85, anchor="e")

    def apply_theme(self, new_theme):
        self.theme = new_theme
        if getattr(self.opt, 'is_reversible', True) and self.opt.is_active():
            self.set_active_visuals()
        else:
            self.set_inactive_visuals()
            
        self.lbl_cat.configure(fg_color=self.theme["bg_sidebar"])
        if hasattr(self, 'lbl_restart'):
            self.lbl_restart.configure(text_color=self.theme["warning"], fg_color=self.theme["bg_sidebar"])
            
        self.lbl_tit.configure(text_color=self.theme["text_main"])
        self.lbl_desc.configure(text_color=self.theme["text_dim"])
        
        if getattr(self.opt, 'is_reversible', True):
            self.control.configure(progress_color=self.theme["btn_primary"])
        else:
            self.control.configure(fg_color=self.theme["btn_danger"], hover_color=self.theme["warning"])

    def set_active_visuals(self):
        self.configure(border_color=self.theme["btn_primary"], fg_color=self.theme["bg_main"])
        
    def set_inactive_visuals(self):
        self.configure(border_color=self.theme["card_border"], fg_color=self.theme["card_bg"])

    def flash_success(self):
        # Fallback de segurança para evitar crashes se a cor "success" faltar no tema
        success_color = self.theme.get("success", "#4CAF50")
        self.configure(border_color=success_color, fg_color=self.theme["bg_main"])
        self.after(1500, self.set_inactive_visuals)

    def flash_error(self):
        # AQUI ESTAVA O BUG: Fallback inteligente procurando "btn_danger" ou "#FF5252"
        error_color = self.theme.get("btn_danger", self.theme.get("danger", "#FF5252"))
        self.configure(border_color=error_color, fg_color=self.theme["bg_main"])
        self.after(1500, self.set_inactive_visuals)

    def log_restart_warning(self):
        if getattr(self.opt, 'requires_restart', False):
            logger.info(f"[INFO] A otimização ({self.opt.name}) requer reinício do sistema.")

    def toggle(self):
        self.control.configure(state="disabled")
        target_state = (self.control.get() == 1) 
        
        def worker(state):
            try:
                if state:
                    sucesso = self.engine.apply_optimization(self.opt.id) if self.engine else self.opt.apply()
                    if sucesso:
                        self.after(0, self.set_active_visuals)
                        self.after(0, self.log_restart_warning)
                    else:
                        self.after(0, self.flash_error)
                        self.after(0, self.control.deselect)
                        self.after(0, self.set_inactive_visuals)
                else:
                    self.after(0, self.set_inactive_visuals)
                    sucesso = self.engine.rollback_optimization(self.opt.id) if self.engine else self.opt.rollback()
                    if sucesso:
                        self.after(0, self.log_restart_warning)
                    else:
                        self.after(0, self.flash_error)
                        # FIM DO EFEITO CHICOTE: Mantém desligado visualmente, forçando a sincronização do UI com a limpeza do SO.
            finally:
                self.after(0, lambda: self.control.configure(state="normal"))
        threading.Thread(target=worker, args=(target_state,), daemon=True).start()

    def execute_once(self):
        self.control.configure(state="disabled", text="A EXECUTAR...")
        warning_color = self.theme.get("warning", "#FFA000")
        self.configure(border_color=warning_color) 
        
        def worker():
            try:
                sucesso = self.engine.apply_optimization(self.opt.id) if self.engine else self.opt.apply()
                if sucesso:
                    self.after(0, self.flash_success)
                    self.after(0, self.log_restart_warning)
                else:
                    self.after(0, self.flash_error)
            finally:
                self.after(0, lambda: self.control.configure(state="normal", text="CONCLUÍDO!"))
                self.after(2500, lambda: self.control.configure(text="EXECUTAR LIMPEZA"))
        threading.Thread(target=worker, daemon=True).start()

    def force_set(self, state: bool):
        if not getattr(self.opt, 'is_reversible', True): return 

        # Inteligência de Idempotência Visual: Só executa se estiver em estado diferente
        if (state and self.control.get() == 1) or (not state and self.control.get() == 0):
            return

        if state:
            self.after(0, self.control.select) 
            sucesso = self.engine.apply_optimization(self.opt.id) if self.engine else self.opt.apply()
            if sucesso:
                self.after(0, self.set_active_visuals)
                self.after(0, self.log_restart_warning)
            else:
                self.after(0, self.flash_error)
                self.after(0, self.control.deselect)
                self.after(0, self.set_inactive_visuals)
        else:
            self.after(0, self.control.deselect)
            self.after(0, self.set_inactive_visuals)
            sucesso = self.engine.rollback_optimization(self.opt.id) if self.engine else self.opt.rollback()
            if sucesso:
                self.after(0, self.log_restart_warning)
            else:
                self.after(0, self.flash_error)

================================================================================
ARQUIVO: c:\Users\Gustavo M.H\Downloads\GustavoOptimizer_Pro\ui\__init__.py
================================================================================

