<div align="center">

<h1 style="font-size: 3em; font-weight: bold;">🛡️ Gustavo Optimizer v2.2.0 - Stable Edition</h1>

A central de comando de engenharia definitiva para Windows. Refinada e estabilizada para manter a integridade absoluta da máquina, enquanto gere latências lógicas, liberta recursos pesados e proporciona uma Interface Gráfica de nível corporativo.

Foco em Heurística, Estabilidade do Kernel e Proteção do Utilizador.

</div>

O Gustavo Optimizer atingiu a sua maturidade. Na versão 2.2.0 Stable, abandonámos agressões inseguras aos controladores de Placas de Vídeo e adaptadores de rede, e introduzimos um Motor Heurístico de Leitura de Erros. Ele sabe agora exatamente quando um erro é um "falso positivo" (ex: uma pasta vazia a ser limpa) ou um risco real (falta de permissões de sistema).

🔥 Principais Funcionalidades

🤖 Motor Heurístico Avançado (Anti-Falsos Positivos): Substituindo scripts opacos antigos, o Python agora captura o stderr em tempo real. Se mandar limpar a cache do navegador e a pasta já não existir, a IA do código assume "Sucesso", em vez de alarmar o utilizador com uma reversão visual abrupta na interface.

👁️ Auditoria em Tempo Real (Single Source of Truth): O programa não confia apenas na sua própria memória. Ao arrancar, ele lê o Kernel e o Registo nativo do Windows em milissegundos. A interface adapta-se automaticamente ao estado real da máquina.

📈 DPI Scaling Nativo e Grelha Elástica: A API do Windows (DWM) foi forçada a injetar cores no código, mantendo o redimensionamento elástico (flexbox) perfeito. Os cartões ajustam-se e esticam simetricamente em qualquer configuração Multi-Monitor.

🧠 Sistema Anti-Loop de Acesso Negado: A arquitetura base possui agora defesas contra os escudos do Windows 11. Se o seu PC ou antivírus negar o acesso (PermissionDenied), o programa limpa as suas memórias de forma inteligente e liberta a interface, impedindo encravamentos de botões.

🐍 Otimizações Nativas de Engenharia (Python): Ferramentas que comunicam diretamente com o Kernel do Windows: um Smart RAM Cleaner (via PSAPI), Auto Game Priority, Validador de Hz, Purga da Standby List (via ISLC / ntdll) e Minimização Inteligente para o System Tray (Bandeja do Sistema).

💽 Gestão Profunda de Hardware (Hibernação): Otimiza o armazenamento instantaneamente com rotinas que interagem com o powercfg, desativando a hibernação e removendo o pesado ficheiro hiberfil.sys, somadas a Benchmarks Globais de Latência (DNS).

🖥️ Gerenciador Interativo de Apps (Debloat): Um painel bidirecional que analisa o status real do sistema, indicando o que está Instalado (Verde) ou Ausente (Vermelho), permitindo desinstalar pacotes ou reinstalá-los via XML nativo.

📜 Histórico de Versões e Evolução

<details open>
<summary><b>🛡️ v2.2.0 - Stable Edition (Instabilidade Zero & Heurística) [ATUAL]</b></summary>

Motor Heurístico de Erros Reais: Remoção da camuflagem >nul 2>&1 || exit 0. O Python lê stderr e os códigos do Windows para interpretar "Falsos Positivos", deixando apenas erros de permissão real passarem.

Estabilidade Absoluta (Instabilidade Zero): Remoção definitiva de injeções (TCP Global, HPET, PowerMizer GPU, Moderação NIC e Flip Fix) que causavam o bloqueio/glitch da aceleração de vídeo e redes sociais na web.

Gestão de Armazenamento: Adicionado switch para Desativar Hibernação (hiberfil.sys), poupando espaço de disco instantaneamente.

</details>

<details>
<summary><b>💎 v2.1.0 - Elite Edition (Smart Profiles & UX Responsiva)</b></summary>

Grelha Responsiva e Elástica (Fix Multi-Monitor): Os cartões da interface ganharam pesos elásticos. A interface estica e encolhe fluidamente.

Sistema Anti-Loop (Quebra-Ciclo): A função mestre de logs (log_res) foi reescrita.

Remoção Segura do Modo MSI: O protocolo de segurança rígido PCI do Windows 11 passou a ser respeitado pela ferramenta.

</details>

<details>
<summary><b>🌟 v2.0.6 - Elite Edition (Smart Profiles & DPI Native)</b></summary>

Resolução Definitiva de DPI: Devolução do controlo ao Desktop Window Manager (DWM). Maximiza as janelas perfeitamente e restaura o Aero Snap.

Injeção de Dark Mode Nativo: API Win32 forçando a barra padrão do Windows a ficar escura.

Inteligência de Hardware: Proteção do SysMain em PCs High-End (>16GB RAM) e da gestão de núcleo do Core Parking.

Bandeja do Sistema Nativa: O app oculta-se perfeitamente ao lado do relógio através da captação <Unmap>.

</details>

<details>
<summary><b>🛠️ Versões Clássicas (v2.0 a v1.0)</b></summary>

Integração Ctypes 64-bits (ntdll.dll) e ofuscação avançada.

Remoção de riscos à integridade (UAC e SmartScreen mantidos ativos).

Introdução de lógica 100% Assíncrona (Threading).

Memória Persistente de Perfil (Snapshots via winreg).

</details>

💻 Como Compilar (Para Desenvolvedores)

O projeto depende de ferramentas gráficas e leituras sistêmicas de bibliotecas externas.

1. Instale todas as Dependências:

py -m pip install pyinstaller customtkinter psutil pystray Pillow


2. Vá até a diretoria raiz e compile com o PyInstaller:

py -m PyInstaller --clean --noconfirm --onefile --windowed --uac-admin --icon "icone.ico" --add-data "icone.ico;." --collect-all customtkinter --collect-all psutil --collect-all pystray --collect-all PIL "Programa dos Bats.py"
