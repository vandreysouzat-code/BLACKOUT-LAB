
# 🖤 BLACKOUT LAB

### Offensive Security Platform | Python

O **BLACKOUT LAB** é uma plataforma modular de segurança ofensiva desenvolvida em Python, criada para transformar conhecimentos teóricos de cybersecurity em ferramentas práticas.

O projeto reúne módulos de reconhecimento, análise web, geração controlada de tráfego e simulação de exploração em uma única aplicação de terminal.

Seu desenvolvimento faz parte de uma jornada prática de estudos em **Red Team, Ethical Hacking, Pentest e desenvolvimento de ferramentas próprias**.

> Projeto educacional destinado exclusivamente a laboratórios próprios, ambientes isolados e sistemas com autorização expressa.

---

## 🚀 Funcionalidades

Atualmente, o BLACKOUT LAB possui seis módulos principais.

### 1. 🔎 Reconnaissance — Reconhecimento

Realiza reconhecimento básico de alvos em ambientes autorizados.

- Verificação de portas TCP.
- Identificação básica de serviços.
- Análise de portas abertas e fechadas.
- Geração de relatórios em JSON.

### 2. 📡 Traffic Generation — Geração de Tráfego

Permite gerar requisições HTTP controladas para observar o comportamento de uma aplicação.

- Envio de requisições HTTP.
- Monitoramento de códigos de resposta.
- Medição de latência.
- Contabilização de requisições e erros.

### 3. ⚡ Stress Testing — Testes de Estresse

Executa testes controlados para analisar como uma aplicação responde a diferentes níveis de carga.

Perfis disponíveis:

- **Load Test:** aumento gradual da carga.
- **Spike Test:** simulação de um pico temporário de requisições.
- **Endurance Test:** execução de carga constante durante um período definido.

Apresenta métricas de requisições, erros, duração e latência.

### 4. 🧪 Exploitation Simulation — Simulação de Exploração

Demonstra, em um laboratório local e isolado, como uma consulta SQL vulnerável pode permitir manipulação de autenticação.

- Simulação educacional de SQL Injection.
- Comparação entre consultas vulneráveis e parametrizadas.
- Demonstração de possível bypass de autenticação.
- Registro de evidências em JSON.

O módulo utiliza um banco SQLite temporário em memória e dados fictícios.

### 5. 📊 Campaign Reports — Relatórios de Campanha

Centraliza os resultados gerados pelos módulos.

- Listagem de relatórios.
- Visualização de resultados.
- Consulta de métricas.
- Exibição de evidências das simulações.
- Armazenamento dos resultados em arquivos JSON.

### 6. 🌐 Web Reconnaissance — Reconhecimento Web

Realiza uma análise inicial de aplicações web em laboratórios autorizados.

- Identificação do status HTTP.
- Extração do título da página.
- Identificação do servidor e Content-Type.
- Consulta dos métodos HTTP anunciados pelo servidor.
- Verificação de cabeçalhos de segurança HTTP.
- Consulta ao arquivo robots.txt.
- Limitação da quantidade de conteúdo HTTP lido.
- Geração de relatórios em JSON.

O módulo realiza verificações informativas. Cabeçalhos ausentes ou métodos anunciados não representam, isoladamente, vulnerabilidades confirmadas.

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python | Linguagem principal |
| Requests | Requisições HTTP |
| Rich | Interface visual no terminal |
| SQLite | Simulação de consultas SQL |
| JSON | Armazenamento de relatórios |
| Unittest | Testes automatizados |
| Git | Controle de versão |

---

## 📋 Requisitos

Antes de instalar, você precisa ter:

- Python 3.10 ou superior.
- Git instalado (opcional, mas recomendado).
- Terminal ou PowerShell.
- Conexão com a internet para instalar as dependências.

---

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
.\.venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
.venv\Scripts\activate.bat
```

**Linux:**

```bash
source .venv/bin/activate
```

### 5. Instalar as dependências

```bash
pip install -r requirements.txt
```

---

## ▶️ Como executar

Com o ambiente virtual ativado:

```bash
python main.py
```

No Windows, também é possível executar diretamente:

```powershell
.\.venv\Scripts\python.exe .\main.py
```

O menu principal apresenta os seis módulos disponíveis. Escolha o número correspondente à funcionalidade desejada.

---

## 🧪 Testes automatizados

O projeto utiliza `unittest`, biblioteca nativa do Python, para validar funcionalidades do módulo Web Reconnaissance.

Execute os testes com:

**Windows PowerShell:**

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

**Linux:**

```bash
python -m unittest discover -s tests -v
```

Os testes verificam validação de alvos, análise de cabeçalhos, inspeção HTTP, métodos HTTP, robots.txt e geração de relatórios.

---

## 📁 Estrutura do projeto

```text
BLACKOUT-LAB/
│
├── core/
│   └── __init__.py
│
├── modules/
│   ├── __init__.py
│   ├── recon.py
│   ├── traffic.py
│   ├── stress.py
│   ├── exploitation.py
│   ├── web_recon.py
│   └── reports.py
│
├── tests/
│   └── test_web_recon.py
│
├── reports/
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

Os relatórios JSON são gerados localmente e ignorados pelo Git.

---

## 🔐 Uso responsável

O BLACKOUT LAB foi desenvolvido exclusivamente para aprendizado e testes de segurança autorizados.

- Utilize somente sistemas próprios ou com autorização expressa.
- Execute testes de tráfego e estresse em ambientes controlados.
- Não utilize a plataforma para interromper serviços ou prejudicar terceiros.
- Realize simulações de exploração somente em laboratórios educacionais.
- Respeite os limites de escopo e as regras de cada ambiente de testes.

O desenvolvedor não se responsabiliza pelo uso indevido da ferramenta.

---

## 🎯 Objetivo do projeto

O BLACKOUT LAB nasceu com o objetivo de transformar conhecimentos teóricos em experiências práticas de desenvolvimento e segurança ofensiva.

Mais do que reunir funcionalidades, o projeto representa uma jornada de aprendizado envolvendo Python, reconhecimento, exploração controlada, análise de aplicações web e desenvolvimento de ferramentas próprias.

**O projeto continua em evolução, com foco no desenvolvimento de novas ferramentas e técnicas voltadas ao Red Team.**

---

## 👨‍💻 Desenvolvedor

**Victor Andrey**

Estudante de Engenharia de Software | Interessado em Cybersecurity, Red Team, Ethical Hacking, Python e Cloud Computing.

🔗 **GitHub:** https://github.com/vandreysouzat-code

🔗 **Projeto:** https://github.com/vandreysouzat-code/BLACKOUT-LAB

---

*Aprender construindo. Evoluir testando. Pensar como um atacante. 🖤*
tps://github.com/vandreysouzat-code/BLACKOUT-LAB

\---

*Aprender construindo. Evoluir testando. Proteger entendendo.* 🖤


