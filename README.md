# 🚀 Gustavo Optimizer Pro v3.0.0

**Gustavo Optimizer Pro** é uma ferramenta avançada de tuning e otimização de performance para Windows 10 e 11. Diferente de scripts genéricos, este software utiliza uma arquitetura baseada em **Leitura Viva de Kernel**, garantindo que as mudanças sejam seguras, validadas e 100% reversíveis.

![Version](https://img.shields.io/badge/version-3.3.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![Admin](https://img.shields.io/badge/privileges-Required-red.svg)

💎 Diferenciais da Versão 3.0
Kernel Engine 3.0: O programa não depende de ficheiros de configuração estáticos. Ele interroga o Windows em tempo real para exibir o estado real e absoluto do sistema.

Zero-Write Idempotency: Proteção extrema contra desgaste do seu SSD. Nenhuma chave de registo é escrita ou alterada se o valor atual no sistema já for o otimizado.

Segurança Anti-BSOD: Todas as otimizações perigosas que alteravam o bootloader ou relógios sensíveis do sistema (como Dynamic Ticks e HPET) foram removidas por um painel de engenharia.

Intelligent Profile Detection: Ao abrir, o programa analisa heuristicamente se o seu PC já está em "Modo Gamer" e adapta a interface de forma automática.

Tray Persistence: Minimize o programa para a bandeja do sistema (System Tray) e mantenha a telemetria a correr sem ocupar espaço na barra de tarefas.

🛠️ Funcionalidades Principais
Modo Gamer Extremo: Macro automatizada que calibra a Latência, CPU, GPU e Rede para a máxima performance em jogos competitivos.

Modo Trabalho Seguro: Foca-se na estabilidade e na limpeza de memória RAM para máxima produtividade.

Telemetria em Tempo Real: Monitorização precisa da carga de CPU, RAM e GPU integrada.

Deep Clean: Expulsa caches de shaders corrompidos (DirectX), ficheiros temporários e resíduos do sistema.

Power Management: Desbloqueio e ativação do plano "Desempenho Máximo" nativo, oculto por defeito no Windows.

📜 CHANGELOG (Histórico de Alterações)
Versão 3.0.0 (Atual)

ARQUITETURA: Migração total para o motor de Leitura Viva (V2.x -> V3.0). Erradicação do "Paradoxo do Botão Fantasma".

NOVO: Inclusão de System Tray com suporte a restauro inteligente através de um duplo clique.

NOVO: Função estrutural de mapeamento de caminhos (resource_path) para compatibilidade total do ícone com executáveis .exe.

SEGURANÇA: Todos os comandos de shell foram blindados contra injeção de código, utilizando listas de argumentos nativas (shell=False).

SEGURANÇA: Remoção cirúrgica de 23 otimizações obsoletas (da era WinXP/7) e perigosas para garantir 100% de estabilidade nos processadores modernos.

ESTABILIDADE: Tratamento de erros de UI com contingências (fallbacks) hexadecimais de cor para evitar falhas visuais.

📚 GLOSSÁRIO TÉCNICO
Idempotência: Propriedade de uma ação que pode ser executada múltiplas vezes sem alterar o resultado para além da primeira aplicação. No Optimizer, significa poupar escritas (I/O) no disco.

Kernel Scraping: A técnica de ler as saídas brutas do terminal do Windows (como netsh, powercfg) para compreender exatamente como o "coração" do sistema operativo está configurado.

UAC Admin Manifest: Código embutido no executável final que obriga o Windows a apresentar o escudo de segurança e pedir permissões de administrador no momento do arranque.

Core Parking: Recurso do Windows que "adormece" núcleos do processador para poupar energia. O Optimizer bloqueia esta função para evitar a latência de "despertar" durante o jogo.

HAGS (Hardware Accelerated GPU Scheduling): Permite que a placa gráfica faça a gestão da sua própria memória, aliviando a carga no processador central.

FSO (Fullscreen Optimizations): Recurso que cria uma camada híbrida entre o modo de janela e o ecrã inteiro. Desativá-lo pode melhorar drasticamente o input lag em jogos competitivos.

📖 MANUAL DE OPERAÇÃO (Para o Utilizador Final)
Primeira Execução: Ao abrir o Gustavo Optimizer Pro, ele demorará cerca de 2 a 3 segundos a realizar o scan inicial. É normal ver o registo "Comando executado" a disparar dezenas de vezes; é o programa a fazer um "Raio-X" ao seu PC.

Criação de Backup: Antes de acionar o "Modo Gamer" pela primeira vez, clique em CRIAR PONTO DE RESTAURO. O programa utilizará o serviço nativo do Windows para criar um ponto de segurança instantâneo.

Reinício do Sistema: Otimizações marcadas com um selo laranja "REINÍCIO NECESSÁRIO" alteram ficheiros do núcleo e só terão efeito após reiniciar a máquina.

Modo Silencioso: Para não poluir o seu ecrã, clique no botão de minimizar (-). O programa ficará oculto ao lado do relógio do Windows. Dê dois cliques no ícone para o trazer de volta.

⚙️ GUIA DO DESENVOLVEDOR (Como Compilar o Projeto)
Para gerar o executável final (.exe) a partir do código fonte, siga estes passos:

1. Instale as dependências obrigatórias:

Bash
pip install customtkinter Pillow psutil pynvml pystray pyinstaller
2. Script de Compilação Automática:
Crie um ficheiro chamado compilar.bat na raiz do projeto, junto ao main.py e ao icon.ico, com o seguinte código:

Snippet de código
@echo off
title Compilador Gustavo Optimizer Pro v3.0
echo Instalando/Atualizando dependencias do Kernel...
pip install customtkinter Pillow psutil pynvml pystray pyinstaller
echo.
echo Iniciando compilacao estrutural OneFile com Privilegios Admin...
pyinstaller --noconsole --onefile --uac-admin --icon=icon.ico --add-data "icon.ico;." main.py
echo.
echo =========================================================
echo Compilacao concluida com sucesso!  
echo O seu executavel final encontra-se dentro da pasta "dist".
echo =========================================================
pause
Basta executar este ficheiro .bat sempre que quiser gerar uma nova versão do seu executável!
