<div align="center">

⚡ Gustavo Optimizer v2.0.6 - Elite Edition

A mais avançada central de comando de engenharia para Windows, desenvolvida para extrair o máximo de frames (FPS), mitigar a latência de entrada (Input Lag) ao nível do Kernel e gerir a estabilidade do sistema com segurança absoluta.

Potência máxima, latência mínima e estabilidade inquebrável.

</div>

O Gustavo Optimizer não é apenas mais um limpador de ficheiros. É uma ferramenta de engenharia de sistema desenhada para extrair cada gota de desempenho do seu hardware, priorizando sempre a segurança e a estabilidade do Windows.

Criado com uma interface moderna e intuitiva, ele automatiza otimizações avançadas que normalmente exigiriam horas de edição manual no Registo do Windows. Tudo à distância de um clique, e 100% reversível.

📑 Índice

Principais Funcionalidades

Changelog Definitivo

Glossário Técnico de Comandos

Como Compilar para Desenvolvedores

🔥 Principais Funcionalidades

👁️ Auditoria em Tempo Real (Single Source of Truth): O programa não confia apenas na sua própria memória. Ao iniciar, ele lê o Kernel e o Registo nativo do Windows em milissegundos. Se você ou uma atualização alterarem alguma configuração "por fora", a interface adapta-se automaticamente ao estado real da máquina.

🎮 Perfis Inteligentes Automáticos: Transforme o seu PC numa máquina de jogos com o Modo Gamer, que aplica 15 camadas dinâmicas de otimização extremas simultâneas em tempo real. Volte ao normal com um clique usando o Modo Trabalho. O sistema protege a sua sessão ao ignorar configurações que exijam reinício de máquina nestes modos.

🧠 Memória Fotográfica Persistente: O programa cria um snapshot de como o seu PC estava antes das otimizações na memória profunda do Registo. Mesmo que reinicie a máquina, ele lembrará exatamente de como reverter tudo.

🐍 Otimizações Nativas (Motor Python & Bandeja): Ferramentas exclusivas que comunicam diretamente com o Kernel do Windows, incluindo um Smart RAM Cleaner, Auto Game Priority para forçar prioridade máxima nos jogos, Validador de Hz do ecrã, Purga da Standby List (nível ISLC) e Minimização Inteligente para o System Tray (Bandeja do Sistema).

📡 Diagnóstico de Rede Avançado: Verifique o seu IP Local, IP Público e Ping real. Faça um Benchmark Global nativo que compara a sua rota atual com os maiores servidores do mundo e permite aplicar o melhor DNS dinamicamente com um clique.

🖥️ Gerenciador Interativo de Apps: Um painel de Debloat bidirecional com interface assíncrona. Ele analisa o status real do sistema, indicando o que está Instalado (Verde) ou Ausente (Vermelho), permitindo desinstalar pacotes ou reinstalá-los via XML nativo.

🛡️ Privacidade e Segurança Ativa: Desativa a telemetria invasiva da Microsoft e da NVIDIA, além de tarefas ocultas que consomem a sua internet e processador em segundo plano. O programa impede proativamente a desativação de barreiras essenciais (UAC/SmartScreen) para manter a integridade contra malwares.

⚙️ Engenharia Anti-Crash e UI-Safe: Blindado contra falsos positivos através de ofuscação avançada. A interface gráfica roda a 60FPS constantes devido à alocação de cargas pesadas (como leituras de Placa Gráfica) em Threads de background.

🎨 Personalização Visual Nível Premium: 8 Temas integrados, Efeito Mica (transparência de vidro do Windows 11), Dashboard Interativo de Hardware, Titlebar 100% desenhada do zero e Sistema de Hover inteligente.

📜 Changelog Definitivo (Histórico de Versões)

<details open>
<summary><b>💎 v2.0.6 - Elite Edition (Atual)</b></summary>

Integração de System Tray (Bandeja do Sistema): Resolvido o conflito de janelas frameless. Ao minimizar, o programa oculta-se perfeitamente na bandeja do Windows, com um menu customizado via clique direito para "Restaurar" ou "Encerrar".

Identidade de Processo (AppUserModelID): Injeção profunda via Ctypes para forçar o Windows 11 a reconhecer o Gustavo Optimizer como um software independente, exibindo o nosso icone.ico nativo na barra de tarefas em vez do ícone azul padrão do Python/Tkinter.

Fallback Seguro de Interface: Implementada rota de fuga visual caso as bibliotecas de imagem (pystray, Pillow) não estejam instaladas na máquina do desenvolvedor, evitando crashes instantâneos.

</details>

<details>
<summary><b>✨ v2.0.5 - Elite Edition</b></summary>

Titlebar Customizada Absoluta: Ocultação da barra padrão branca/preta do Windows via overrideredirect. A barra de título foi redesenhada do zero para se integrar perfeitamente à paleta de cores do programa, com botões Hover-Safe.

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

Purga da Standby List (Nível ISLC) via API nativa (ntdll.dll).

Modo MSI para forçar interrupção direta da GPU sobre a CPU.

Otimizações E-Sports: HPET, Dynamic Ticks e Raw Mouse Input.

Thread Assíncrona dedicada à leitura da GPU (nvidia-smi), destravando 60FPS na UI principal.

</details>

<details>
<summary><b>🚀 Versões Clássicas (v1.1.1 a v0.1.0)</b></summary>

Introdução de lógica 100% Assíncrona para evitar ecrãs congelados.

Smart RAM Cleaner, Auto Game Priority e Validador Hz.

Memória Persistente de Perfil (Snapshots Registo).

Interface CustomTkinter e Desempenho Máximo nativo de Workstation.

</details>

⚙️ Glossário Técnico de Comandos (Engenharia do Sistema)

🐍 1. Otimizações Nativas (API Python, UI e Kernel)

Purga da Standby List (Nível ISLC): Método: Chama ntdll.NtSetSystemInformation solicitando privilégios SeProfileSingleProcessPrivilege (com tratamento de ponteiros wintypes.HANDLE). Ação: Esvazia a RAM em espera acumulada.

Smart RAM Cleaner: Método: psapi.EmptyWorkingSet acoplado via ctypes. Ação: Força aplicações minimizadas a devolverem RAM à placa-mãe.

Auto Game Priority: Método: Injeção via psutil.HIGH_PRIORITY_CLASS. Ação: Encontra identificadores de jogos em execução e foca o processador neles.

Identidade de Processo (AppUserModelID): Método: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID. Ação: Dissocia a ferramenta do interpretador Python para forçar o ícone correto na barra de tarefas do Windows.

Minimização Ctypes (Tray): Método: ctypes.windll.user32.ShowWindow(hwnd, 6). Ação: Engana o gestor de janelas do Windows para minimizar de forma estável uma janela sem barra de título (frameless).

Benchmark DNS Nativo: Método: Leituras Regex sobre ping -n 4. Ação: Teste multi-rota real e aplicação paramétrica do IP vencedor.

🌐 2. Rede, Latência e NIC (TCP/IP)

Interrupt Moderation (NIC): Comando: Disable-NetAdapterInterruptModeration -Physical. Ação: Obriga os adaptadores físicos a processarem pacotes unitariamente.

Otimização Global TCP/IP: Método: Unificação de três frentes: aplica TcpAckFrequency e TCPNoDelay (reduzindo delay), desativa o autotuninglevel e adota o algoritmo de congestão CUBIC (padrão de servidores Linux).

Limitação de Rede (Throttling): Ação: Fixa NetworkThrottlingIndex a 0xFFFFFFFF. Cancela limites de banda multimédia.

Pacotes DSCP: Ação: Etiqueta de qualidade de serviço (Do not use NLA = 1) que força os roteadores a darem primazia ao tráfego do jogo.

🚀 3. Hardware Extremo (Ferramentas de Root)

Modo MSI (Message Signaled Interrupts): Ação: Varre a chave MSISupported = 1 no caminho PCI. A Placa Gráfica ignora o controlador antigo e interrompe o CPU de forma direta (Corta Latência DPC).

Desligar HPET & Ticks: Comandos: bcdedit /deletevalue useplatformclock e disabledynamictick yes. Ação: Mata relógios digitais pesados.

Mira Perfeita (Raw Mouse): Ação: Esmaga chaves MouseSpeed e MouseThreshold a 0.

Desbloquear Menus (Edge): Ação: Apaga restrições de Políticas de Grupo (SOFTWARE\Policies\Microsoft\Edge) e força gpupdate.

⚡ 4. Desempenho e Energia Dinâmica

Desempenho Visual Máximo: Ação: Fixa VisualFXSetting = 2 e EnableTransparency = 0. Remove Acrílico e suprime animações pesadas, libertando o dwm.exe.

Core Parking: Ação: powercfg sub_processor CPMINCORES 100. Impede a nível energético que os núcleos lógicos se suspendam.

Power Throttling: Ação: Impede restrições de voltagem aplicadas a processos em background.

Plano Desempenho Máximo (Workstation): Ação: Aplica e9a42b02-d5df-448d-aa00-03f14749eb61. Extração de poder sem limites energéticos.

Resolução de Tempo: Ação: Fixa GlobalTimerResolutionRequests para 1 (Tolerância de ciclo de 0.5 milissegundos).

🛡️ 5. Privacidade, Segurança e Debloat

Painel Interativo de Gerenciador de Apps: Ação: Permite varrer, desinstalar e reinstalar ativamente pacotes oficiais via XML (Ex: Xbox, Cortana).

Telemetria e Tarefas: Ação: Suspende agendamentos ocultos (schtasks) e DiagTrack que enviam dados de uso em background.

Privacidade NVIDIA: Ação: Termina contentores locais de envio estatístico dos drivers de vídeo (OptIn = 0).

Sensor de Localização: Ação: Modifica as Políticas do Windows (DisableLocation = 1) para impedir acessos geográficos de aplicações em background.

🧹 6. Manutenção e Estrutura Limpa

Reparo DISM e Verificação SFC: Ação: Solução de nível Root para consultar imagens sãs nos servidores da Microsoft e reparar arquivos.

Ofuscação de Cache: Ação: Estruturas de diretório ("\\".join(["Steam", "appcache"])) são montadas na RAM e destruídas a seguir à limpeza para impedir deteção heurística por antivírus de terceiros.


<div align="center">
<i>Engenharia desenvolvida para performance máxima e estabilidade intocável.</i>
</div>
