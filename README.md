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

🛠️ v1.1.1 - Patch de Correção Crítica

Esta atualização focou-se em resolver anomalias estruturais de baixo nível e garantir a sincronia absoluta entre a interface visual (CustomTkinter), o Kernel do Windows e o Registo de Memória.

Correção de Assimetria nos Perfis (Modo Gamer/Trabalho): * Problema: Ao desativar o "Modo Gamer", o sistema apenas revertia 6 das 13 chaves de otimização ativadas.

Solução: O array de reversão do "Modo Trabalho" foi reescrito. Agora atua como um verdadeiro Master Switch, varrendo e forçando agressivamente a desativação das 13 chaves de hardware e rede, garantindo o retorno ao estado original de fábrica.

Prevenção de Falsos Positivos de Memória (Bug do Flip-Flop):

Problema: Comandos bloqueados pelo Windows por falta de permissões causavam dessincronização: o botão voltava para "OFF" visualmente, mas o Registo gravava "ON".

Solução: O auditor log_res foi reestruturado para ser a "dona da memória". A chave no Registo só é atualizada para refletir o estado visual final e real do botão após a tentativa de execução do comando no sistema operativo.

Execução 100% Assíncrona (Anti-Freeze UI):

Problema: Ativar múltiplas chaves simultaneamente asfixiava a Thread Principal do programa, causando o congelamento silencioso da interface (os botões não alteravam visualmente).

Solução: Desacoplamento total da interface gráfica (UI) das ações de sistema (CMD/PowerShell). As rotinas de otimização correm agora em Threads de fundo silenciosas e utilizam contentores self.after com delays milimétricos (0.15s) para garantir animações fluidas.

Captura Dinâmica do Plano de Energia (OEM Fix):

Problema: Forçar o GUID do plano "Equilibrado" padrão falhava em máquinas OEM (Dell, Lenovo, HP) que utilizam planos de energia customizados de fábrica.

Solução: Implementada a rotina guid_padrao que "tira uma fotografia" do plano de energia nativo do computador no primeiro arranque do programa, garantindo que o "Modo Trabalho" restaura a energia para o plano exato da máquina do utilizador.
