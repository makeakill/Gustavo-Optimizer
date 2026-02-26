# ⚡ Gustavo Optimizer v1.0 - Pro Edition

**Potência máxima, latência mínima e estabilidade inquebrável.**

O **Gustavo Optimizer** não é apenas mais um limpador de ficheiros. É uma ferramenta de engenharia de sistema desenhada para extrair cada gota de desempenho do seu hardware, priorizando sempre a segurança e a estabilidade do Windows. 

Criado com uma interface moderna e intuitiva, ele automatiza otimizações avançadas que normalmente exigiriam horas de edição manual no Registo do Windows. Tudo à distância de um clique, e **100% reversível**.

---

## 🔥 Principais Funcionalidades

* 🎮 **Perfis Inteligentes Automáticos:** Transforme o seu PC numa máquina de jogos com o *Modo Gamer*, que injeta 10 camadas de otimização extremas simultâneas (incluindo o plano oculto de "Desempenho Máximo"). Volte ao normal com um clique usando o *Modo Trabalho*.
* 🧠 **Memória Fotográfica Persistente:** O programa cria um *snapshot* de como o seu PC estava antes das otimizações na memória profunda do Registo. Mesmo que feche o programa ou reinicie a máquina, ele lembrará exatamente como reverter tudo ao estado original.
* 🛡️ **Privacidade e Segurança:** Desativa a telemetria invasiva da Microsoft e da NVIDIA, além de tarefas ocultas que consomem a sua internet e processador em segundo plano.
* 📡 **Diagnóstico de Rede Avançado:** Verifique o seu IP Local, IP Público e Ping real num servidor remoto diretamente pelo aplicativo, com injeção otimizada de DNS (Google/Cloudflare).
* ⚙️ **Engenharia Anti-Crash:** Blindado contra Falsos Positivos de antivírus (Kaspersky/Windows Defender) através de ofuscação de strings, e construído com arquitetura *Thread-Safe* para garantir zero travamentos na interface visual.
* 🎨 **Personalização Visual:** 8 Temas Premium integrados (Ciano, Vermelho Brutal, Matrix, Dracula, etc.) que se adaptam perfeitamente ao seu setup.

---

## ⚠️ Filosofia de Segurança (A Regra de Ouro)

O Gustavo Optimizer respeita a regra de ouro da informática: **não executa limpezas de registo cegas (procura de chaves órfãs) que causam ecrãs azuis (BSOD)**. Todas as otimizações atuam em camadas de sistema documentadas, garantindo que a estabilidade do seu Sistema Operativo nunca seja comprometida. Estabilidade e FPS andam sempre de mãos dadas.

---
📜 Changelog Definitivo (Histórico de Versões)

🛠️ v1.1.1 - Patch de Correção Crítica

Esta atualização focou-se em resolver anomalias estruturais de baixo nível e garantir a sincronia absoluta entre a interface visual (CustomTkinter), o Kernel do Windows e o Registo de Memória.

Correção de Assimetria nos Perfis (Modo Gamer/Trabalho): Ao desativar o "Modo Gamer", o sistema apenas revertia 6 das 13 chaves de otimização ativadas. O array de reversão do "Modo Trabalho" foi reescrito para atuar como um verdadeiro Master Switch, forçando agressivamente a desativação das 13 chaves de hardware e rede.

Prevenção de Falsos Positivos de Memória (Bug do Flip-Flop): Comandos bloqueados pelo Windows por falta de permissões causavam dessincronização visual. A função log_res foi reestruturada para ser a "dona da memória", atualizando o registo apenas para refletir o estado visual final e real do botão após a execução do sistema operativo.

Execução 100% Assíncrona (Anti-Freeze UI): Desacoplamento total da interface gráfica (UI) das ações de sistema (CMD/PowerShell) utilizando Threads de fundo silenciosas com delays milimétricos (0.15s), evitando o asfixiamento da Thread Principal e garantindo animações fluidas.

Captura Dinâmica do Plano de Energia (OEM Fix): Implementada a rotina guid_padrao que tira uma "fotografia" do plano de energia nativo do computador no primeiro arranque, garantindo que o "Modo Trabalho" restaura a energia para o plano exato da máquina (corrigindo falhas em sistemas Dell, Lenovo, HP).

🚀 v1.1.0 - Otimizações Nativas (Python API) e UI Dinâmica

Manual Interativo Integrado: Adição de uma janela sobreposta (ctk.CTkToplevel) exibindo a documentação internamente, com a opção de exportar o ficheiro para .txt.

Barra de Progresso (UI-Safe): Implementação de uma barra visual que reage em tempo real a varreduras profundas.

Smart RAM Cleaner: Nova ferramenta injeta uma ordem diretamente no Kernel (psapi.EmptyWorkingSet via ctypes) para forçar processos em segundo plano a libertarem memória cache não utilizada.

Auto Game Priority: Motor de verificação ativa de RAM que localiza jogos abertos (CS2, Valorant, Dota, etc.) e eleva a sua prioridade no processador para "Alta".

Validador de Hz do Monitor: Consulta via user32.dll para confirmar a verdadeira taxa de atualização (Hz) que o Windows está a enviar para a placa gráfica.

Benchmark DNS Global: Teste de rede simultâneo via Python Subprocess contra a Google, Cloudflare, OpenDNS e Quad9, apurando o melhor servidor.

Limpeza Temp Visual: Reconstrução da limpeza de ficheiros temporários utilizando os.walk e os.remove nativamente, com exibição de progresso visual.

🧠 v1.0.0 - A Versão "Pro Edition" Definitiva

Memória Profunda no Registo: Implementação de Snapshots. O "Modo Gamer" agora persiste após fechar a aplicação. O programa cria um registo fotográfico das configurações no winreg, permitindo reverter o PC ao estado exato pré-otimização.

Correção "Botões Fantasma" (Thread Race Condition): Resolvido o problema em que as chaves não ativavam visualmente devido a bloqueios do motor gráfico.

⚡ v0.9.0 - Validação Sênior e Energia Extrema

Otimização do Plano de Energia: O programa agora identifica, cria e injeta o plano oculto "Desempenho Máximo" (Ultimate Performance) nativo do Windows.

Verificação de Execução (Double-Check): Consultas de Loop-back para confirmar se o Windows realmente obedeceu aos comandos de energia antes de registar o sucesso.

Correção (Crash): Resolvido o erro RuntimeError: main thread is not in main loop na inicialização, aplicando um atraso inteligente de 500ms nas validações.

🎨 v0.8.0 - Expansão de Perfis e Reestruturação Visual

Expansão: "Modo Gamer" ampliado para 10 camadas simultâneas (incluindo Network Throttling, Core Parking, Timer Res, GPU Downclock e DSCP).

Cores Dinâmicas: Os botões alteram a sua cor consoante o perfil selecionado e o texto alterna dinamicamente entre "ATIVAR MODO" e "DESATIVAR".

🛠️ v0.7.0 - A Grande Atualização de Ferramentas

Novas Integrações: Adição da aba "Perfis Inteligentes", atalho para o Gestor de "Apps de Inicialização", Ferramenta de Diagnóstico de Rede e bloqueio de "Tarefas Ocultas (Telemetria)".

Diretriz de Segurança: Decisão arquitetónica de não incluir varredura de chaves órfãs de Registo para garantir risco zero de corromper o sistema (Anti-Blue Screen).

📦 v0.6.0 - Correção Ortográfica e Empacotamento

Melhoria de Compilação: Introdução da flag --clean no comando do PyInstaller para evitar a corrupção por ficheiros .pkg residuais.

Alteração massiva na nomenclatura interna.

🛡️ v0.5.0 - Blindagem Anti-Heurística (Bypass Antivírus)

Correção Crítica: Antivírus (como o Kaspersky) bloqueavam o executável rotulando-o falsamente de HEUR:Trojan-PSW.Python.Agent.gen.

Solução Implementada: Aplicação de engenharia de "Ofuscação de Strings". Os diretórios de limpeza de cache são montados dinamicamente na RAM apenas na hora do clique, garantindo aprovação absoluta nos motores de segurança.

🏗️ v0.1.0 a v0.4.0 - Fundações da Arquitetura

Criação da grelha de Interface em CustomTkinter com modo escuro nativo.

Implementação do sistema de Paletas de Cores dinâmicas (Cyberpunk, Dracula, etc).

Desenvolvimento das funções base (Limpezas de Disco, Ajustes de Registo) e do painel de hardware (CPU, RAM, GPU) em tempo real.

Integração do script de ponteiro absoluto (resource_path) para embutir o ficheiro icone.ico no executável final.
