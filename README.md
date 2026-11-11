# 🦉 SOVIK

### Offensive Security Platform | Python | Version 2.0.0

O **SOVIK** é uma plataforma modular de segurança ofensiva desenvolvida em Python, criada para transformar conhecimentos teóricos de cibersegurança em ferramentas práticas.

O projeto reúne módulos de reconhecimento, análise web, geração controlada de tráfego, testes de estresse e simulação de exploração em uma aplicação de terminal.

Seu desenvolvimento faz parte de uma jornada prática de estudos em **Análise e Desenvolvimento de Sistemas (ADS), Python, Red Team, Ethical Hacking e desenvolvimento de ferramentas de segurança**.

> Projeto educacional destinado exclusivamente a laboratórios próprios, ambientes isolados e sistemas com autorização expressa.

---

## 🚀 Funcionalidades

Atualmente, o SOVIK possui seis módulos principais:

### 1. 🔎 Reconnaissance — Reconhecimento

Realiza reconhecimento básico de alvos em ambientes autorizados.

- Verificação de portas TCP.
- Identificação básica de serviços.
- Análise de portas abertas e fechadas.
- Validação de alvos por meio do Core Engine.
- Geração de relatórios em JSON.

### 2. 📡 Traffic Generation — Geração de Tráfego

Permite gerar requisições HTTP controladas para observar o comportamento de uma aplicação.

- Envio de requisições HTTP.
- Monitoramento de códigos de resposta.
- Medição de latência.
- Contabilização de requisições e erros.
- Registro das operações executadas.

### 3. ⚡ Stress Testing — Testes de Estresse

Executa testes controlados para analisar como uma aplicação responde a diferentes níveis de carga.

- Testes de carga em ambiente autorizado.
- Monitoramento de respostas.
- Coleta de métricas de execução.
- Limites de duração e frequência.

### 4. 💉 Exploitation Simulation — Simulação de Exploração

Demonstra conceitos de exploração de vulnerabilidades em ambiente educacional.

- Simulação de SQL Injection.
- Utilização de banco SQLite em memória.
- Dados fictícios para demonstração.
- Execução isolada, sem exploração de sistemas externos.

### 5. 🌐 Web Reconnaissance — Reconhecimento Web

Realiza inspeções básicas de aplicações web.

- Verificação de disponibilidade HTTP/HTTPS.
- Análise de cabeçalhos HTTP.
- Identificação de métodos HTTP.
- Inspeção de robots.txt.
- Análise de informações de resposta.
- Geração de relatórios.

### 6. 📊 Reports — Relatórios

Centraliza os resultados das operações realizadas pelos módulos.

- Geração de relatórios JSON.
- Registro de informações das execuções.
- Organização dos resultados por módulo.
- Histórico local das atividades.

---

## 🧠 Core Engine

O SOVIK possui uma estrutura central responsável por organizar e controlar as operações dos módulos.

Entre seus componentes estão:

- **Scope:** validação de alvos e escopo permitido.
- **Operations:** registro e controle das operações.
- **Campaigns:** gerenciamento de campanhas.
- **Database:** persistência de informações.
- **Logger:** registro centralizado de eventos.
- **Execution:** controle de execução.
- **Lab:** configurações do ambiente de laboratório.

A arquitetura modular permite organizar funcionalidades, facilitar a manutenção e ampliar o projeto de maneira estruturada.

---

## 🛡️ Controles e limitações

O projeto possui restrições para reduzir riscos durante os testes:

- Alvos públicos desabilitados por padrão.
- Exigência de escopo explícito.
- Geração de tráfego limitada a até 2 requisições por segundo.
- Duração máxima de 10 segundos para operações de tráfego controlado.
- Testes de estresse restritos a ambientes autorizados.
- Recursos de laboratório distribuído desabilitados por padrão.
- Esta versão não implementa funcionalidades operacionais de DoS ou DDoS.

Essas limitações fazem parte da proposta educacional e de uso controlado do projeto.

---

## 🛠️ Tecnologias utilizadas

- Python
- SQLite
- Requests
- Rich
- Unittest
- Git e GitHub

---

## 📦 Instalação

Clone o repositório:

```bash
git clone https://github.com/vandreysouzat-code/SOVIK.git
```

Entre na pasta:

```bash
cd SOVIK
```

Crie um ambiente virtual:

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

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

O menu principal apresenta os módulos disponíveis. Escolha o número correspondente à funcionalidade desejada.

---

## 🧪 Testes automatizados

O projeto utiliza `unittest`, biblioteca nativa do Python, para validar seus componentes.

Execute os testes com:

**Windows PowerShell:**

```powershell
python -m unittest discover -s tests -v
```

**Linux:**

```bash
python -m unittest discover -s tests -v
```

A suíte de testes possui **181 testes automatizados**, cobrindo componentes como escopo, banco de dados, logger, operações, reconhecimento, tráfego, testes de estresse, exploração simulada e reconhecimento web.

---

## 📁 Estrutura do projeto

```text
SOVIK/
│
├── core/
│   ├── campaigns.py
│   ├── config.py
│   ├── database.py
│   ├── execution.py
│   ├── lab.py
│   ├── logger.py
│   ├── operations.py
│   └── scope.py
│
├── modules/
│   ├── recon.py
│   ├── traffic.py
│   ├── stress.py
│   ├── exploitation.py
│   ├── web_recon.py
│   └── reports.py
│
├── tests/
│   ├── test_campaigns.py
│   ├── test_database.py
│   ├── test_execution.py
│   ├── test_exploitation.py
│   ├── test_lab.py
│   ├── test_logger.py
│   ├── test_operations.py
│   ├── test_recon.py
│   ├── test_reports.py
│   ├── test_scope.py
│   ├── test_stress.py
│   ├── test_traffic.py
│   └── test_web_recon.py
│
├── reports/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

Os relatórios são gerados localmente e os arquivos de saída são ignorados pelo Git.

---

## 🔐 Uso responsável

O SOVIK foi desenvolvido exclusivamente para aprendizado e testes de segurança autorizados.

- Utilize somente sistemas próprios ou com autorização expressa.
- Execute testes de tráfego e estresse em ambientes controlados.
- Não utilize a plataforma para interromper serviços ou prejudicar terceiros.
- Realize simulações de exploração somente em laboratórios educacionais.
- Respeite os limites de escopo e as regras de cada ambiente de testes.

O desenvolvedor não se responsabiliza pelo uso indevido da ferramenta.

---

## 🎯 Objetivo do projeto

O SOVIK nasceu com o objetivo de transformar conhecimentos teóricos em experiências práticas de desenvolvimento e segurança ofensiva.

Mais do que reunir funcionalidades, o projeto representa uma jornada de aprendizado envolvendo Python, reconhecimento, exploração controlada, análise de aplicações web, arquitetura modular e desenvolvimento de ferramentas próprias.

**O projeto continua em evolução, com foco no aprimoramento de suas funcionalidades, qualidade de código e aprendizado em segurança cibernética.**

---

## 👨‍💻 Desenvolvedor

**Victor Andrey**

Estudante de Análise e Desenvolvimento de Sistemas (ADS), interessado em Python, Cybersecurity, Red Team, Ethical Hacking e Cloud Computing.

🔗 **GitHub:** https://github.com/vandreysouzat-code

🔗 **Projeto:** https://github.com/vandreysouzat-code/SOVIK

---

*Aprender construindo. Evoluir testando. Proteger entendendo.* 🦉
