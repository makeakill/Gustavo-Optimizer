# 🚀 Gustavo Optimizer Pro v2.2.0

**Gustavo Optimizer Pro** é uma ferramenta avançada de tuning e otimização de performance para Windows 10 e 11. Diferente de scripts genéricos, este software utiliza uma arquitetura baseada em **Leitura Viva de Kernel**, garantindo que as mudanças sejam seguras, validadas e 100% reversíveis.

![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)
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
