🛡️ Gustavo Optimizer Pro v3.1.0 - Enterprise Edition
A central de comando de engenharia definitiva para Windows. Refinada e elevada ao nível Enterprise para manter a integridade absoluta da máquina, enquanto gere latências lógicas, liberta recursos pesados e proporciona uma Interface Gráfica de nível corporativo.

Foco em Arquitetura Limpa, Estabilidade do Kernel, Idempotência e Proteção do Usuário.

O Gustavo Optimizer atingiu a sua maturidade máxima. Na versão 3.1.0 Enterprise, abandonamos scripts opacos e chamadas diretas não seguras, introduzindo um Motor de Execução Desacoplado, Painéis Interativos de Diagnóstico e uma Caixa-Preta de Auditoria em tempo real. O sistema sabe exatamente o que está instalado no seu PC e nunca subscreve configurações originais com valores genéricos.

🔥 Principais Funcionalidades
🧠 Motor Heurístico e Idempotência: Substituindo scripts antigos, o Python agora lê o Registo e o Kernel nativamente antes de agir. Se um recurso já estiver otimizado, o motor ignora a escrita, poupando a vida útil do seu SSD e evitando processamento inútil.

👁️ Single Source of Truth (Auditoria em Tempo Real): O programa não confia em achismos. Ao inicializar furtivamente em milissegundos, ele lê o Kernel do Windows. A interface adapta-se automaticamente ao estado real da máquina. Todas as mudanças geram um log estruturado (system_changes_audit.json).

🔄 True Rollback (Snapshot de Estado Real): Ao contrário de otimizadores comuns que aplicam valores padrão, o Optimizer Pro tira uma "fotografia" da configuração exata da sua máquina antes de aplicar qualquer alteração. Reverter significa voltar cirurgicamente ao seu estado original.

🛡️ Blindagem de Memória e Permissões: O código Win32 API (ctypes) usa assinaturas de 64-bits estritas, prevenindo corrupção de memória (Segfaults). Funções críticas são bloqueadas automaticamente se o programa não possuir privilégios de Administrador.

📈 Painéis Interativos de Diagnóstico:

Smart DNS Benchmark: Avalia o Ping dos maiores servidores mundiais (Cloudflare, Google, Quad9, etc.) em tempo real e injeta a rota vencedora diretamente no adaptador físico de rede.

Debloat Avançado: Analisa o pacote de aplicativos nativos do Windows (UWP) e permite desinstalar ou reinstalar bloatwares de forma segura e visual.

🖥️ UI Enterprise Responsiva: Interface desenvolvida em CustomTkinter, com DPI Scaling nativo, suporte perfeito a múltiplos monitores e temas (incluindo integração com o Modo Escuro nativo do Windows).

⚡ Telemetria Singleton de Custo Zero: Monitoramento contínuo de CPU, RAM e GPU em tempo real na interface, executado de forma paralela e em cache para não gerar quedas de FPS.

📜 Histórico de Versões e Evolução
👑 v3.1.0 - Enterprise Edition [ATUAL]
Painéis Interativos: Introdução da classe visual Toplevel para o Smart DNS Benchmark e o Debloat Avançado.

Cofre de Comandos (SystemCommandExecutor): Proteção contra Command Injection e travamentos infinitos (Timeouts).

Fix de Memory Leak/Segfault: Assinaturas argtypes aplicadas nas chamadas nativas de Kernel.

Boot Silencioso: Remoção completa de terminais na inicialização; leitura de estado 100% via API Nativa.

🧱 v3.0.0 - Enterprise Foundation
Arquitetura MVC: Desacoplamento total entre a Interface Gráfica e o Motor de Otimização.

Auditoria de Segurança: Implementação do SystemChangeGuard e logs rotativos profissionais de 5MB.

Cache de Hardware: Sistema Singleton para evitar gargalos de CPU durante varreduras de SSD/Cores.

🛡️ v2.2.0 - Stable Edition (Instabilidade Zero & Heurística)
Motor Heurístico de Erros Reais: Leitura de stderr e códigos do Windows para interpretar "Falsos Positivos".

Estabilidade Absoluta: Remoção definitiva de injeções antigas (HPET, PowerMizer GPU) que causavam bloqueio de aceleração de vídeo.

💎 v2.1.0 - Elite Edition (Smart Profiles & UX Responsiva)
Grelha Responsiva: Cartões da interface ganharam pesos elásticos (Flexbox).

Sistema Anti-Loop: A função mestre de logs foi reescrita contra escudos do Windows 11.

Remoção Segura do Modo MSI: O protocolo de segurança PCI passou a ser respeitado pela ferramenta.

🌟 Versões Clássicas (v2.0 a v1.0)
Resolução Definitiva de DPI (Aero Snap restaurado).

Proteção de SysMain para PCs High-End (>16GB RAM).

Integração base com ctypes e lógica 100% Assíncrona (Threading).

💻 Como Compilar (Para Desenvolvedores)
O projeto possui uma arquitetura modular moderna e depende de bibliotecas gráficas e de sistema avançadas.

1. Instale todas as dependências:

Bash
py -m pip install pyinstaller customtkinter psutil pystray Pillow pynvml
2. Vá até o diretório raiz do projeto e compile com o PyInstaller:

Bash
py -m PyInstaller --clean --noconfirm --onefile --windowed --uac-admin --icon "icon.ico" --add-data "icon.ico;." --collect-all customtkinter --collect-all psutil --collect-all pystray --collect-all PIL "main.py"
(Nota: Certifique-se de que possui o ficheiro icon.ico na mesma pasta antes de rodar a compilação).
