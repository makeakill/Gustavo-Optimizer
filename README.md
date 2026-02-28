<div align="center">
<h1>⚡ Gustavo Optimizer v2.0.1 - Elite Edition</h1>
<p>A mais avançada central de comando de engenharia para Windows, desenvolvida para extrair o máximo de frames (FPS), mitigar a latência de entrada (Input Lag) ao nível do Kernel e gerir a estabilidade do sistema com segurança absoluta.</p>
</div>

**Potência máxima, latência mínima e estabilidade inquebrável.**

O **Gustavo Optimizer** não é apenas mais um limpador de ficheiros. É uma ferramenta de engenharia de sistema desenhada para extrair cada gota de desempenho do seu hardware, priorizando sempre a segurança e a estabilidade do Windows. 

Criado com uma interface moderna e intuitiva, ele automatiza otimizações avançadas que normalmente exigiriam horas de edição manual no Registo do Windows. Tudo à distância de um clique, e **100% reversível**.

---

📜 Changelog Definitivo (Histórico de Versões)

👑 v2.0.1 - Elite Edition (Patch de Estabilidade e Segurança Sênior)

Integração Ctypes 64-bits (Fix WinError 6): Declaração explícita de argtypes na API C++ nativa, garantindo que o limpador de Standby List não quebre em sistemas de 64-bits.

Gerenciador Interativo Bidirecional: A aba de Debloat visualiza agora o estado nativo (Instalado/Ausente) e permite reinstalação e restauro visual por pacotes XML.

Filtro Inteligente de Placa de Rede (NIC): O comando de moderação isola placas puramente virtuais, prevenindo crashes com VPNs e Máquinas Virtuais através do switch -Physical.

Proteção de Sessão Avançada: O "Modo Gamer" passou a evitar as funções raízes que afetam drivers essenciais, blindando a sessão e impedindo reboots forçados durante o uso.

Segurança Reforçada (Funções Removidas): Remoção de opções de alto risco para o OS, como UAC, SmartScreen e Mitigações de Segurança, blindando o PC do usuário. Otimização da grade de UX para compensar a ausência e remoção da opção isolada DNS Google.

🛠️ v2.0 - Elite Edition

Purga da Standby List (Nível ISLC): Libertação extrema da RAM em espera comunicando com a ntdll.dll.

Forçar Modo MSI (GPU): Injeção local no Root PCI de Message Signaled Interrupts diretos à CPU, anulando o Delay da Motherboard (DPC).

Otimizações E-Sports: Remoção do arcaico Relógio HPET, dos Dynamic Ticks e acelerações de mouse nativas (Raw Input).

Performance UI: Separação do monitorizador da GPU numa Thread assíncrona garantindo 60FPS na ferramenta gráfica.

🚀 v1.1.1 - Patch de Correção Crítica

Reestruturação 100% Assíncrona.

Correção de Assimetria de Perfis (Master Switch).

Captura Dinâmica de Plano OEM (Bateria/Equilibrado).

Prevenção de Falsos Positivos de Memória (Registo Condicional).

🧠 v1.1.0 e Anteriores

Adição de Otimizações nativas em Python (Smart RAM Cleaner, Game Priority, Hz).

Memória Fotográfica Persistente via Registo (Snapshots v1.0.0).

Ofuscação de cadeias de cache para bypass de Antivírus.

⚙️ Glossário Técnico de Comandos (Engenharia do Sistema)

Uma visão transparente de como o Gustavo Optimizer interage com a máquina em baixo nível.

1. Ferramentas Nativas (API Python) e Kernel

Purga da Standby List: Utiliza privilégios C++ em ntdll para forçar o esvaziamento do cache de sistema, evitando Stuttering.

Smart RAM Cleaner: Utiliza ctypes.WinDLL('psapi.dll') para abrir processos ativos via OpenProcess e aplica a função EmptyWorkingSet.

Auto Game Priority: Mapeia PIDs ativos via psutil.process_iter, identifica executáveis de jogos pesados e aplica o comando process.nice(psutil.HIGH_PRIORITY_CLASS).

Validador de Monitor: Estrutura um objeto DEVMODE em C via ctypes e chama ctypes.windll.user32.EnumDisplaySettingsW para ler dmDisplayFrequency.

Benchmark DNS Global: Testa latência multirrota (ping IP -n 4) via Python Subprocess com Regex.

2. Rede e Latência (TCP/IP)

Interrupt Moderation (NIC): Comando: Disable-NetAdapterInterruptModeration -Physical. Obriga o Windows a não reter pacotes físicos.

TCP NoDelay (Nagle's Algorithm): Chave: TcpAckFrequency = 1 e TCPNoDelay = 1. Obriga o Windows a disparar pacotes instantaneamente.

Network Throttling: Chave: NetworkThrottlingIndex = 0xFFFFFFFF (Desativado). Remove limite de banda multimédia.

Controle CUBIC: Algoritmo Linux de estabilidade para perdas de pacote em netsh.

3. CPU, Energia e Hardware

Modo MSI (Message Signaled Interrupts): Altera a MSISupported para 1. A GPU sinaliza direto para o CPU.

Desligar HPET & Ticks: Usa bcdedit /deletevalue useplatformclock para impedir cálculos exaustivos da placa-mãe.

Desativar Core Parking: powercfg sub_processor CPMINCORES 100 mantém os núcleos do processador sempre ativos.

Plano Desempenho Máximo: Injeta e aplica o UUID original e9a42b02-d5df... de Workstation.

Resolução de Tempo: GlobalTimerResolutionRequests = 1 aperta o clock interno de latência do SO para 0.5ms.

4. Privacidade e Telemetria

Gerenciador de Apps: Interface GUI que coordena interações nativas bidirecionais de powershell (XML e AppxPackage).

Tarefas Ocultas (Agendador): Comando: schtasks /Change /TN "... \Microsoft Compatibility Appraiser" /Disable.

Telemetria DiagTrack: Interrompe rastreamentos nativos sc stop DiagTrack.

Geolocalização: Adiciona chaves às Políticas do Sistema proibindo partilha de dados GPS.

5. Manutenção do Sistema

CHKDSK Inteligente: Iteração via Python psutil.disk_partitions() para programar verificações de segurança em unidades de armazenamento válidas.

Reparos de Imagem e Registos: Ordens root DISM /RestoreHealth e sfc /scannow acopladas ao limpador recursivo de instâncias Wevtutil.

Ofuscação de Cache: Navegadores e aplicações (Chrome, Discord, Spotify) sofrem taskkill /f seguido da exclusão forçada das pastas de Cache, cujos caminhos (\\) são montados dinamicamente na RAM para não alarmar firewalls de segurança.
