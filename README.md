<div align="center">

<h1 style="font-size: 3em; font-weight: bold;">⚡ Gustavo Optimizer v2.1.0 - Elite Edition</h1>

A central de comando de engenharia definitiva para Windows. Desenvolvida para extrair frames (FPS), liquidar a latência de entrada (Input Lag) e blindar a estabilidade do seu sistema operativo com o uso de lógicas inteligentes e código assíncrono.

Poder absoluto, latência zero e segurança inquebrável.

</div>

O Gustavo Optimizer abandonou os scripts frágeis. A nova versão 2.1.0 é uma ferramenta robusta, equipada com uma grelha elástica totalmente responsiva, um quebra-ciclos inteligente para contornar escudos de antivírus e algoritmos Smart Profiles que se moldam à capacidade térmica e quantidade de memória RAM da sua máquina.

🔥 Principais Funcionalidades

👁️ Auditoria em Tempo Real (Single Source of Truth): O programa não confia apenas na sua própria memória. Ao arrancar, ele lê o Kernel e o Registo nativo do Windows em milissegundos. Se o utilizador ou uma atualização alterarem alguma configuração "por fora", a interface adapta-se automaticamente ao estado real da máquina.

🤖 Inteligência de Hardware (Smart Profiles): O Modo Gamer é capaz de ler a quantidade de RAM e os limites térmicos da sua máquina. Para PCs com mais de 16GB, ele protege serviços como o SysMain para garantir navegação web ultrarrápida, enquanto força 14 camadas de rede e Kernel para latência zero nos jogos.

📈 DPI Scaling Nativo e Grelha Elástica: A ferramenta abandonou as janelas frameless inseguras e larguras fixas. A API do Windows (DWM) foi forçada a injetar cores no código, mantendo o redimensionamento elástico (flexbox) perfeito. Os cartões ajustam-se e esticam simetricamente, independentemente do monitor, resolução ou zoom aplicado.

🧠 Sistema Anti-Loop (Quebra-Ciclos): A arquitetura base possui agora defesas contra os escudos do Windows 11. Se tentar desativar uma função e o seu PC ou antivírus negar o acesso (PermissionDenied), o programa limpa as suas memórias de forma inteligente e liberta a interface, impedindo encravamentos.

🐍 Otimizações Nativas (Motor Python & Bandeja): Ferramentas exclusivas que comunicam diretamente com o Kernel do Windows, incluindo um Smart RAM Cleaner, Auto Game Priority para forçar prioridade máxima nos jogos, Validador de Hz do ecrã, Purga da Standby List (nível ISLC) e Minimização Inteligente para o System Tray (Bandeja do Sistema).

📡 Diagnóstico de Rede Avançado: Verifique o seu IP Local, IP Público e Ping real. Faça um Benchmark Global nativo que compara a sua rota atual com os maiores servidores do mundo e permite aplicar o melhor DNS dinamicamente com um clique.

🖥️ Gerenciador Interativo de Apps: Um painel de Debloat bidirecional com interface assíncrona. Ele analisa o status real do sistema, indicando o que está Instalado (Verde) ou Ausente (Vermelho), permitindo desinstalar pacotes ou reinstalá-los via XML nativo.

🛡️ Privacidade e Segurança Ativa: Desativa a telemetria invasiva da Microsoft e da NVIDIA, além de tarefas ocultas que consomem a sua internet e processador em segundo plano. O programa impede proativamente a desativação de barreiras essenciais (UAC/SmartScreen) para manter a integridade contra malwares.

📜 Changelog Definitivo (Histórico de Versões)

<details open>
<summary><b>💎 v2.1.0 - Elite Edition (Atual)</b></summary>

Grelha Responsiva e Elástica (Fix Multi-Monitor): Os cartões da interface foram reduzidos para 280px e receberam pesos de geometria elásticos. A interface agora estica e encolhe fluidamente em qualquer ecrã.

Sistema Anti-Loop (Quebra-Ciclo): A função mestre de logs (log_res) foi reescrita para impedir bloqueios quando o Windows nega leitura de chaves protegidas de hardware.

Remoção Segura do Modo MSI: Remoção integral da função e interface gráfica do "Modo MSI", respeitando os protocolos de segurança do Windows 11 que barram modificações severas na árvore PCI.

</details>

<details>
<summary><b>🌟 v2.0.6 - Elite Edition (Smart Profiles & DPI Native)</b></summary>

Resolução Definitiva de DPI: Remoção da Titlebar Customizada e devolução do controlo ao Desktop Window Manager (DWM). Garante maximização milimétrica e restaura o Aero Snap.

Injeção de Dark Mode Nativo: API Win32 DWMWA_USE_IMMERSIVE_DARK_MODE forçando a barra de título padrão do Windows a ficar escura e premium.

Inteligência de Hardware: Leitura de RAM para proteger o SysMain em PCs High-End (>16GB), impedindo lentidão no uso diário do sistema.

Fix de Vídeos / Streaming: Restauro do TCP Auto-Tuning para normal acoplado ao poderoso algoritmo CUBIC. Resolve a página preta em links do Google (aclk) e carregamento de ícones.

Bandeja do Sistema Nativa: Interceção profunda do evento <Unmap>. O app oculta-se ao lado do relógio.

</details>

<details>
<summary><b>✨ v2.0.5 - Elite Edition (UX Premium)</b></summary>

Efeito Mica / Transparência Dinâmica: Integração de slider de opacidade (-alpha) na barra lateral e Hover Effects ligados às paletas de cores nativas.

</details>

<details>
<summary><b>🔍 v2.0.4 e v2.0.3 - Auditoria Real e Tabviews</b></summary>

Auditoria de Registo em Tempo Real: Leitura direta em HKEY_LOCAL_MACHINE das políticas estritas do SO.

Organização em Tabview: Fim do scroll infinito com seções especializadas e criação do Painel Visual de Hardware com Threads dedicadas de monitorização de GPU (nvidia-smi).

Desbloqueio de Menus (Edge): Remoção de Policies organizacionais impeditivas nos navegadores.

</details>

<details>
<summary><b>🛡️ v2.0.2 - Security Patch</b></summary>

Remoção de Funções Críticas de Risco: Remoção das opções de desativação do UAC e do Filtro SmartScreen. Otimizadores não devem expor a máquina do utilizador a ataques virtuais.

</details>

<details>
<summary><b>👑 v2.0.1 e Anteriores (A Fundação do Kernel)</b></summary>

Integração Ctypes 64-bits: Parâmetros absolutos na ntdll.dll para compatibilidade com ponteiros avançados de RAM.

Standby List Nativa e Filtros de Rede Físicos: Criação do ambiente isento de Stutterings de hardware para E-Sports.

</details>

💻 Como Compilar (Para Desenvolvedores)

O Gustavo Optimizer v2.1.0 Elite requer compilação com privilégios de Administrador e a injeção do ícone. Devido ao recurso de bandeja e interface premium, há pré-requisitos adicionais de bibliotecas.

1. Instale todas as Dependências:

py -m pip install pyinstaller customtkinter psutil pystray Pillow


2. Navegue até à pasta do projeto:

cd "C:\Seu\Caminho\Para\O\Script"


3. Execute a compilação absoluta com PyInstaller:

py -m PyInstaller --clean --noconfirm --onefile --windowed --uac-admin --icon "icone.ico" --add-data "icone.ico;." --collect-all customtkinter --collect-all psutil --collect-all pystray --collect-all PIL "Programa dos Bats.py"


Nota Crítica: Certifique-se de que o ficheiro icone.ico se encontra na mesma pasta do script antes de iniciar a compilação, para que a injeção de ID de Processo (AppUserModelID) tenha êxito visual na barra de tarefas do Windows.
