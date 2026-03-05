<div align="center">

<h1 style="font-size: 3em; font-weight: bold;">⚡ Gustavo Optimizer v2.0.6 - Elite Edition</h1>

A mais avançada central de comando de engenharia para Windows, desenvolvida para extrair o máximo de frames (FPS), mitigar a latência de entrada (Input Lag) ao nível do Kernel e gerir a estabilidade do sistema com segurança absoluta.

Potência máxima, latência mínima e estabilidade inquebrável.

</div>

O Gustavo Optimizer não é apenas mais um limpador de ficheiros. É uma ferramenta de engenharia de sistema desenhada para extrair cada gota de desempenho do seu hardware, priorizando sempre a segurança e a estabilidade do Windows.

A nova versão 2.0.6 atinge o ápice do design responsivo, com a introdução do sistema de Smart Profiles (Perfis Inteligentes) que lê o hardware do seu PC para proteger-lhe contra bloqueios e a resolução matemática definitiva para o DPI Scaling em múltiplos monitores.

📑 Índice

1. Principais Funcionalidades

2. Changelog Definitivo

3. Glossário Técnico de Comandos

4. Como Compilar para Desenvolvedores

1. Principais Funcionalidades

👁️ Auditoria em Tempo Real (Single Source of Truth): O programa não confia apenas na sua própria memória. Ao iniciar, ele lê o Kernel e o Registo nativo do Windows em milissegundos. Se você ou uma atualização alterarem alguma configuração "por fora", a interface adapta-se automaticamente ao estado real da máquina.

🤖 Inteligência de Hardware (Smart Profiles): O Modo Gamer é agora capaz de ler a quantidade de RAM e os limites térmicos da sua máquina. Para PCs com mais de 16GB, ele protege serviços como o SysMain para garantir navegação web ultrarrápida, enquanto força 15 camadas de rede e Kernel para latência zero nos jogos, sem superaquecer processadores modernos.

📈 DPI Scaling Nativo (Ecrãs Múltiplos): A API do Windows (DWM) foi forçada a injetar cores obscuras no código nativo, mantendo o redimensionamento elástico (flexbox) perfeito em qualquer monitor e suportando totalmente o Aero Snap do Windows 11.

🧠 Memória Fotográfica Persistente: O programa cria um snapshot de como o seu PC estava antes das otimizações na memória profunda do Registo. Mesmo que reinicie a máquina, ele lembrará exatamente de como reverter tudo.

🐍 Otimizações Nativas (Motor Python & Bandeja): Ferramentas exclusivas que comunicam diretamente com o Kernel do Windows, incluindo um Smart RAM Cleaner, Auto Game Priority para forçar prioridade máxima nos jogos, Validador de Hz do ecrã, Purga da Standby List (nível ISLC) e Minimização Inteligente para o System Tray (Bandeja do Sistema).

📡 Diagnóstico de Rede Avançado: Verifique o seu IP Local, IP Público e Ping real. Faça um Benchmark Global nativo que compara a sua rota atual com os maiores servidores do mundo e permite aplicar o melhor DNS dinamicamente com um clique.

🖥️ Gerenciador Interativo de Apps: Um painel de Debloat bidirecional com interface assíncrona. Ele analisa o status real do sistema, indicando o que está Instalado (Verde) ou Ausente (Vermelho), permitindo desinstalar pacotes ou reinstalá-los via XML nativo.

🛡️ Privacidade e Segurança Ativa: Desativa a telemetria invasiva da Microsoft e da NVIDIA, além de tarefas ocultas que consomem a sua internet e processador em segundo plano. O programa impede proativamente a desativação de barreiras essenciais (UAC/SmartScreen) para manter a integridade contra malwares.

⚙️ Engenharia Anti-Crash e UI-Safe: Blindado contra falsos positivos através de ofuscação avançada. A interface gráfica roda a 60FPS constantes devido à alocação de cargas pesadas (como leituras de Placa Gráfica) em Threads de background.

2. Changelog Definitivo

<details open>
<summary><b>💎 v2.0.6 - Elite Edition (Atual)</b></summary>

Resolução Definitiva de DPI (Multi-Monitor): Remoção da Titlebar Customizada e devolução do controlo de geometria ao Desktop Window Manager (DWM). Garante maximização milimétrica em ecrãs secundários e restaura a funcionalidade Aero Snap.

Injeção de Dark Mode Nativo: Implementação da API Win32 (DWMWA_USE_IMMERSIVE_DARK_MODE), forçando a barra de título nativa a adotar a paleta escura Premium.

Inteligência de Hardware (Smart Profiles): O Modo Gamer agora analisa fisicamente o PC. Se a máquina possuir mais de 16GB de RAM, ele bloqueia a desativação do SysMain (Superfetch), impedindo lentidão.

Fix de Vídeo em Browsers (TCP/IP): O comando de rede foi ajustado de disabled para normal com algoritmo CUBIC. Permite streams 4K em segundo plano enquanto mantém Input Lag baixo nos jogos competitivos.

Bandeja do Sistema Nativa (System Tray): Ao clicar no minimizar padrão (_) do Windows, o programa oculta-se inteligentemente ao lado do relógio através da captação do evento <Unmap>.

</details>

<details>
<summary><b>✨ v2.0.5 - Elite Edition</b></summary>

Efeito Mica / Transparência Dinâmica: Integração de slider no painel lateral permitindo ajustar a opacidade global da ferramenta, criando um efeito de vidro elegante sobre o wallpaper do utilizador.

Sistema Inteligente de Hover: Cartões de otimização acendem as suas bordas de acordo com a paleta de cores ativada no momento ao passar o rato por cima.

</details>

<details>
<summary><b>🎨 v2.0.4 - Elite Edition</b></summary>

Modernização de Layout: Adoção de Soft UI (Bordas arredondadas corner_radius=12) e alteração da tipografia para a elegante Segoe UI.

Sistema de Abas (Tabview): Fim do scroll infinito. As mais de 60 opções foram divididas cirurgicamente em abas (Desempenho, Rede, Privacidade, Limpeza e Root).

Dashboard Visual de Hardware: Criação de um painel lateral interativo com barras de progresso reais.

</details>

<details>
<summary><b>🔍 v2.0.3 - Elite Edition</b></summary>

Auditoria de Registo em Tempo Real: O programa passou a ler o estado real do Windows no momento de arranque (Single Source of Truth).

Unificação de Desempenho Visual Máximo: Combinadas as chaves de Acrílico e Efeitos Visuais num único Master Switch.

Otimização Global TCP/IP: Fusão de três ferramentas antigas (TcpNoDelay, Buffers Netsh e Controle CUBIC).

Desbloqueio de Menus (Bypass GPO): Função para remover restrições de "Gerenciado por sua Organização" no Microsoft Edge.

</details>

<details>
<summary><b>🛡️ v2.0.2 - Security Patch</b></summary>

Remoção de Funções Críticas de Risco: Remoção permanente das opções de desativação do UAC, Filtro SmartScreen e Mitigações de Segurança de CPU (Spectre/Meltdown) para manter a integridade anti-malware da máquina.

</details>

<details>
<summary><b>👑 v2.0.1 - Patch de Estabilidade Sênior</b></summary>

Integração Ctypes 64-bits (Fix WinError 6): Declaração explícita de argtypes na API C++ nativa para suporte irrestrito a sistemas de 64-bits na purga de RAM.

Gerenciador Interativo Bidirecional: O painel de Debloat passou a rastrear o status real e a suportar a reinstalação de aplicações via manifesto XML.

Filtro Inteligente de Placa de Rede (NIC): A rotina de Moderação focou-se exclusivamente em adaptadores físicos (-Physical), cortando bugs com VPNs/VMs.

Proteção de Sessão Avançada: Chaves Root de reinício passaram a ser ignoradas pelo Modo Gamer automático.

</details>

<details>
<summary><b>🛠️ v2.0 - Elite Edition (A Atualização de Kernel)</b></summary>

Purga da Standby List (Nível ISLC): Ligação direta em C/C++ via API nativa (ntdll.dll) para esvaziar a memória RAM em espera.

Forçar Modo MSI (GPU): Algoritmo que altera o registo PCI da Placa Gráfica para comunicar sem interrupções com o CPU.

Otimizações E-Sports (Latência Zero): Desativação do relógio HPET, aniquilação de Dynamic Ticks e Raw Mouse Input.

Thread Assíncrona (Hardware): Dedicada à leitura da GPU (nvidia-smi), destravando 60FPS na UI principal.

</details>

<details>
<summary><b>📦 Versões Clássicas (v1.1.1 a v0.1.0)</b></summary>

<blockquote>

<details>
<summary><b>🛠️ v1.1.1 - Patch de Correção Crítica</b></summary>

Correção de Assimetria nos Perfis: O "Modo Trabalho" foi reescrito para atuar como um verdadeiro Master Switch e desligar toda a agressividade.

Prevenção de Falsos Positivos de Memória: O Registo reflete o estado visual final e real do botão apenas após a consolidação do SO.

Execução 100% Assíncrona: Desacoplamento da interface gráfica (UI) das ações de sistema (CMD/PowerShell) evitando congelamentos.

Captura Dinâmica do Plano de Energia: Registo do plano de energia de fábrica (OEM) no primeiro arranque.

</details>

<details>
<summary><b>🚀 v1.1.0 - Otimizações Nativas e Integração</b></summary>

Manual Interativo adicionado com capacidade de exportação em .txt.

Barras de Progresso visuais reativas implementadas.

Implementação do Smart RAM Cleaner, Auto Game Priority e Validador de Hz.

Limpeza Temp transformada numa rotina mapeada recursivamente (os.walk).

</details>

<details>
<summary><b>🧠 v1.0.0 - A Versão "Pro Edition" Definitiva</b></summary>

Memória Profunda no Registo: Implementação de Snapshots (winreg), permitindo reverter o PC ao estado exato pré-otimização.

Correção "Botões Fantasma": Resolvido problema de Race Conditions nas renderizações do CustomTkinter.

</details>

<details>
<summary><b>⚡ v0.9.0 - Validação e Energia Extrema</b></summary>

Otimização do Plano de Energia: Cria e aplica o plano oculto "Desempenho Máximo" (Ultimate Performance).

Verificação de Execução: Consultas de Loop-back para confirmar a obediência do SO.

</details>

<details>
<summary><b>🛡️ v0.8.0 a v0.1.0 - Fundações</b></summary>

Criação de UI CustomTkinter, bypass Antivírus via Ofuscação de Strings na memória e aplicação de otimizações de rede base.

</details>

</blockquote>

</details>

4. Como Compilar para Desenvolvedores

O Gustavo Optimizer v2.0.6 Elite requer compilação com privilégios de Administrador e a injeção do ícone. Devido ao recurso de bandeja e interface premium, há pré-requisitos adicionais de bibliotecas.

1. Instale todas as Dependências de Sistema, Compilação e Imagem:

py -m pip install pyinstaller customtkinter psutil pystray Pillow


2. Navegue até à pasta do projeto:

cd "INSIRA_AQUI_O_CAMINHO_DO_ARQUIVO"


(Ajuste o caminho inserindo o local exato onde se encontra o script e o ícone).

3. Execute a compilação absoluta com PyInstaller:

py -m PyInstaller --clean --noconfirm --onefile --windowed --uac-admin --icon "icone.ico" --add-data "icone.ico;." --collect-all customtkinter --collect-all psutil --collect-all pystray --collect-all PIL "Programa dos Bats.py"


Nota Crítica: Certifique-se de que o ficheiro icone.ico se encontra na mesma pasta do script antes de iniciar a compilação, para que a injeção de ID de Processo (AppUserModelID) tenha êxito visual na barra de tarefas do Windows.

<div align="center">
<i>Engenharia desenvolvida para performance máxima e estabilidade intocável.</i>
</div>
