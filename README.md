# 🚀 Gustavo Optimizer Pro v3.0.0

**Gustavo Optimizer Pro** é uma ferramenta avançada de tuning e otimização de performance para Windows 10 e 11. Diferente de scripts genéricos, este software utiliza uma arquitetura baseada em **Leitura Viva de Kernel**, garantindo que as mudanças sejam seguras, validadas e 100% reversíveis.

![Version](https://img.shields.io/badge/version-3.3.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![Admin](https://img.shields.io/badge/privileges-Required-red.svg)

## 💎 Diferenciais da Versão Pro

* **Arquitetura Nível 3:** O programa não depende de arquivos de configuração. Ele interroga o Windows em tempo real para exibir o estado real do sistema.
* **Idempotência Rígida:** Zero escritas desnecessárias no disco. Se uma otimização já está ativa, o programa ignora a execução para poupar o ciclo de vida do seu SSD/NVMe.
* **Segurança Anti-BSOD:** Todas as otimizações perigosas que alteravam o bootloader ou clocks sensíveis foram removidas por um painel de engenharia de elite.
* **System Tray:** Minimize para a bandeja e mantenha o monitoramento de telemetria sem poluir sua barra de tarefas.

## 🛠️ Funcionalidades Principais

* **Modo Gamer Extremo:** Macro automatizada que calibra Latência, CPU, GPU e Rede para máxima performance em jogos competitivos.
* **Modo Trabalho Seguro:** Foca na estabilidade e limpeza de memória para produtividade.
* **Telemetria em Tempo Real:** Monitoramento de carga de CPU, RAM e GPU integrada.
* **Deep Clean:** Purga de caches de shaders (DirectX), arquivos temporários e lixo de sistema.
* **Power Management:** Ativação do plano "Desempenho Máximo" nativo, oculto por padrão no Windows.

## 🚀 Como Compilar

1. Instale as dependências:
   ```bash
   pip install customtkinter Pillow psutil pynvml pystray pyinstaller
   
2. Execute o comando de compilação:
   pyinstaller --noconsole --onefile --uac-admin --icon=icon.ico --add-data "icon.ico;." main.py

   ⚠️ Aviso Legal
Este software executa comandos de nível administrativo. Embora tenha sido projetado para máxima segurança, utilize por sua conta e risco. Sempre crie um ponto de restauração antes de grandes alterações.

---

# 2. CHANGELOG (Histórico de Mudanças)

**Versão 2.2.0 (Atual)**
* **NOVO:** Sistema de **System Tray** (Bandeja) com ícone dinâmico.
* **NOVO:** Função `resource_path` para compatibilidade total com executáveis `.exe`.
* **NOVO:** Scanner Heurístico de Perfil: O programa agora detecta se o "Modo Gamer" está ativo ao abrir, analisando o estado do SO.
* **CORREÇÃO:** Erradicação de "Botões Fantasmas" através da validação dupla no Registro.
* **SEGURANÇA:** Migração de `shell=True` para `shell=False` em todos os subprocessos para prevenir injeções maliciosas.
* **SEGURANÇA:** Remoção de otimizações obsoletas (WinXP/7) e perigosas (BCD/Timers).
* **ESTABILIDADE:** Tratamento de erro `KeyError: 'danger'` na UI através de fallbacks de cores.

---

# 3. GLOSSÁRIO TÉCNICO

* **Idempotência:** Propriedade de uma ação que pode ser executada várias vezes sem alterar o resultado além da primeira aplicação. No Optimizer, isso significa não gravar no Registro o que já está gravado.
* **Kernel Scraping:** Técnica de ler as saídas brutas do terminal do Windows (`netsh`, `powercfg`) para entender como o "coração" do sistema está configurado.
* **UAC Admin Manifest:** Código embutido no executável que obriga o Windows a pedir permissão de administrador ao iniciar.
* **Core Parking:** Recurso do Windows que "desliga" núcleos da CPU para poupar energia. O Optimizer desativa isso para evitar latência ao "acordar" o núcleo durante o jogo.
* **HAGS (Hardware Accelerated GPU Scheduling):** Permite que a placa de vídeo gerencie sua própria memória, reduzindo a carga no processador.
* **FSO (Fullscreen Optimizations):** Recurso que cria uma camada híbrida entre janela e tela cheia. Desativar pode melhorar o *input lag* em jogos antigos.

---

# 4. MANUAL DE OPERAÇÃO (PARA O USUÁRIO)

1.  **Primeira Execução:** Ao abrir, o programa demorará cerca de 3 segundos para fazer o scan inicial. É normal ver o log "Comando executado" várias vezes; é o programa conhecendo seu PC.
2.  **Criação de Backup:** Antes de clicar em "Modo Gamer", clique em **CRIAR PONTO DE RESTAURO**. Isso utiliza o serviço VSS do Windows para garantir uma volta segura.
3.  **Reinício do Sistema:** Otimizações marcadas com "REINÍCIO NECESSÁRIO" só terão efeito após você desligar e ligar o PC. O Modo Gamer ignora estas por padrão para evitar que o PC reinicie sozinho.
4.  **Minimizar:** Ao clicar em minimizar, o programa vai para o lado do relógio. Clique com o botão direito no ícone para restaurar ou sair.

---
