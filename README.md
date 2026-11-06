# 🖤 BLACKOUT LAB

### Plataforma Modular de Segurança Ofensiva | Python

O **BLACKOUT LAB** é uma plataforma educacional de segurança cibernética desenvolvida em Python, criada para praticar conceitos de programação, reconhecimento de redes, análise de tráfego, testes de desempenho e simulação de vulnerabilidades.

O projeto reúne diferentes ferramentas em uma única aplicação de terminal, permitindo executar testes controlados, analisar resultados e gerar relatórios para estudo.

> Projeto desenvolvido para fins educacionais e testes em ambientes próprios, autorizados e isolados.

\---

## 🚀 Funcionalidades

O BLACKOUT LAB possui cinco módulos principais:

### 1. 🔎 Reconnaissance — Reconhecimento

Realiza reconhecimento básico de alvos em ambientes autorizados.

\- Verificação de portas TCP.

\- Identificação básica de serviços.

\- Análise de portas abertas e fechadas.

\- Geração de relatórios em JSON.

### 2. 📡 Traffic Generation — Geração de Tráfego

Permite gerar requisições HTTP controladas para observar o comportamento de uma aplicação.

\- Envio de requisições HTTP.

\- Monitoramento de códigos de resposta.

\- Medição de latência.

\- Contabilização de requisições e erros.

### 3. ⚡ Stress Testing — Testes de Estresse

Executa testes controlados para analisar como uma aplicação responde a diferentes níveis de carga.

Perfis disponíveis:

\- **Load Test:** aumento gradual da carga.

\- **Spike Test:** simulação de um pico temporário de requisições.

\- **Endurance Test:** execução de carga constante durante um período definido.

Apresenta métricas como quantidade de requisições, erros, tempo de execução e latência média.

### 4. 🧪 Exploitation Simulation — Simulação de Exploração

Demonstra, em um laboratório local e isolado, como uma consulta SQL vulnerável pode permitir manipulação de autenticação.

\- Simulação educacional de SQL Injection.

\- Comparação entre consultas vulneráveis e consultas parametrizadas.

\- Demonstração de possível bypass de autenticação.

\- Registro das evidências em JSON.

O módulo utiliza um banco SQLite temporário em memória e dados fictícios.

### 5. 📊 Campaign Reports — Relatórios de Campanha

Centraliza os resultados gerados pelos módulos.

\- Listagem de relatórios.

\- Visualização de resultados.

\- Consulta de métricas.

\- Exibição de evidências da simulação de exploração.

\- Armazenamento dos resultados em arquivos JSON.

\---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Finalidade |

|---|---|

| Python | Linguagem principal |

| Requests | Requisições HTTP |

| Rich | Interface visual no terminal |

| SQLite | Simulação de consultas SQL |

| JSON | Armazenamento de relatórios |

\---

## 📋 Requisitos

Antes de instalar, você precisa ter:

\- Python instalado.

\- Git instalado (opcional, mas recomendado).

\- Terminal ou PowerShell.

\- Conexão com a internet para instalar as dependências.

\---

## 📥 Instalação

### 1. Clonar o repositório

```bash

git clone https://github.com/vandreysouzat-code/BLACKOUT-LAB.git

```

### 2. Acessar a pasta

```bash

cd BLACKOUT-LAB

```

### 3. Criar um ambiente virtual

**Windows:**

```powershell

python -m venv .venv

```

**Linux:**

```bash

python3 -m venv .venv

```

### 4. Ativar o ambiente virtual

**Windows PowerShell:**

```powershell

.\\.venv\\Scripts\\Activate.ps1

```

**Windows CMD:**

```cmd

.venv\\Scripts\\activate.bat

```

**Linux:**

```bash

source .venv/bin/activate

```

### 5. Instalar as dependências

```bash

pip install -r requirements.txt

```

\---

## ▶️ Como executar

Com o ambiente virtual ativado, execute:

```bash

python main.py

```

No Windows, também é possível executar diretamente:

```powershell

.\\.venv\\Scripts\\python.exe .\\main.py

```

Após iniciar, o menu principal apresentará os módulos disponíveis. Escolha o número correspondente à funcionalidade que deseja utilizar.

\---

## 📁 Estrutura do projeto

```text

BLACKOUT-LAB/

│

├── core/

│   └── \_\_init\_\_.py

│

├── modules/

│   ├── \_\_init\_\_.py

│   ├── recon.py

│   ├── traffic.py

│   ├── stress.py

│   ├── exploitation.py

│   └── reports.py

│

├── reports/

│

├── main.py

├── requirements.txt

├── README.md

└── .gitignore

```

\---

## 🔐 Uso responsável

O BLACKOUT LAB foi desenvolvido exclusivamente para aprendizado e testes de segurança autorizados.

\- Utilize somente sistemas próprios ou com autorização expressa.

\- Execute os testes de tráfego e estresse em ambientes controlados.

\- Não utilize a plataforma para interromper serviços ou prejudicar terceiros.

\- Realize simulações de exploração somente em laboratórios educacionais.

O desenvolvedor não se responsabiliza pelo uso indevido da ferramenta.

\---

## 🎯 Objetivo do projeto

O BLACKOUT LAB nasceu com o objetivo de transformar conhecimentos teóricos em experiências práticas de desenvolvimento e segurança cibernética.

Mais do que reunir funcionalidades, o projeto representa uma jornada de aprendizado envolvendo programação Python, segurança ofensiva, análise de vulnerabilidades, testes e desenvolvimento de ferramentas próprias.

**O projeto continua em evolução e novas funcionalidades poderão ser adicionadas.**

\---

## 👨‍💻 Desenvolvedor

**Victor Andrey**

Estudante de Engenharia de Software | Interessado em Cybersecurity, Ethical Hacking, Python e Cloud Computing.

🔗 **GitHub:** https://github.com/vandreysouzat-code

🔗 **Projeto:** https://github.com/vandreysouzat-code/BLACKOUT-LAB

\---

*Aprender construindo. Evoluir testando. Proteger entendendo.* 🖤


