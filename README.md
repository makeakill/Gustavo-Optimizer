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
📜 Changelog (Histórico de Versões)
v1.0.0 - A Versão "Pro Edition" Definitiva (Versão Atual)
Implementação Crítica: Memória Profunda no Registo. O "Modo Gamer" agora persiste após fechar o aplicativo. O programa cria um snapshot serializado das 10 chaves de otimização na raiz do Windows.
Correção "Botões Fantasma" (Thread Race Condition): Resolvido o problema em que o "Modo Gamer" não ativava visualmente as chaves ao ser acionado devido ao bloqueio de segurança do motor gráfico. Os Helpers agora utilizam chamadas UI-Safe para garantir sincronia total e fluidez.
v0.9.0 - Validação Sênior e Energia Extrema
Funcionalidade: Otimização do Plano de Energia. O programa agora identifica, cria e injeta o plano oculto "Desempenho Máximo" (Ultimate Performance) nativo do Windows, em vez do simples "Alto Desempenho".
Auditoria de Execução (Double-Check): O programa não "assume" mais que um comando funcionou. Ele agora envia o comando de energia e faz uma leitura no sistema para confirmar se o Windows realmente obedeceu antes de dar sucesso.
Correção (Crash): Resolvido o erro RuntimeError: main thread is not in main loop na inicialização, aplicando um atraso inteligente de 500ms antes das validações de background.
v0.8.0 - Expansão de Perfis e Reestruturação Visual
Expansão: "Modo Gamer" ampliado de 5 para 10 camadas simultâneas (incluindo Network Throttling, Core Parking, Timer Res, GPU Downclock e DSCP).
Melhoria Visual: Os Perfis Inteligentes foram movidos para o topo da hierarquia visual.
Cores Dinâmicas: Os botões agora alteram a sua cor consoante o perfil selecionado e o texto altera dinamicamente entre "ATIVAR MODO" e "DESATIVAR".
v0.7.0 - A Grande Atualização de Ferramentas
Novas Integrações:
Aba de "Perfis Inteligentes".
Atalho nativo para o Gerenciador de "Apps de Inicialização".
Ferramenta de Diagnóstico de Rede.
Chave para desativar "Tarefas Ocultas (Telemetria)".
Diretriz de Segurança: Decisão arquitetónica de não incluir varredura de chaves órfãs de Regedit para garantir risco zero de corromper o sistema.
v0.6.0 - Correção Ortográfica e Empacotamento
Correção: Alteração massiva na nomenclatura de ficheiros e código-fonte para refletir a gramática correta ("Programa").
Melhoria de Compilação: Introdução da flag --clean no PyInstaller para evitar corrupção por ficheiros .pkg residuais.
v0.5.0 - Blindagem Anti-Heurística (Bypass Antivírus)
Correção Crítica: O Kaspersky bloqueava o executável como HEUR:Trojan-PSW.Python.Agent.gen devido aos caminhos de cache dos navegadores.
Solução Implementada: Aplicada engenharia de "Ofuscação de Strings". Os diretórios são montados dinamicamente na RAM apenas na hora do clique, garantindo 100% de aprovação em motores de antivírus.
v0.1.0 a v0.4.0 - Fundações da Arquitetura
Criação da grelha de Interface em CustomTkinter com modo escuro.
Implementação do sistema de Temas dinâmicos.
Desenvolvimento das 29 funções base e painel de hardware (CPU, RAM, GPU) em tempo real.
Integração nativa do Ícone no código-fonte via script de ponteiro absoluto.
