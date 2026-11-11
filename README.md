# 🖤 BLACKOUT LAB

### Offensive Security Platform | Python | Version 2.0.0

O **BLACKOUT LAB** é uma plataforma modular desenvolvida em Python para estudos práticos de segurança ofensiva, reconhecimento e análise de aplicações.

O projeto reúne ferramentas de reconhecimento, geração controlada de tráfego, testes de estresse com limites definidos, simulação de exploração em laboratório e análise web.

A versão 2.0.0 também introduz uma estrutura de gerenciamento de campanhas, histórico de execuções, persistência de dados e testes automatizados.

> Projeto educacional destinado exclusivamente a ambientes próprios, laboratórios controlados e sistemas com autorização expressa.

---

## 🚀 Funcionalidades

### 1. 🔎 Reconnaissance
- Reconhecimento básico de alvos.
- Verificação de portas TCP.
- Identificação de serviços.
- Registro dos resultados em relatórios JSON.

### 2. 📡 Traffic Generation
- Geração controlada de requisições HTTP.
- Monitoramento de códigos de resposta.
- Medição de latência.
- Contabilização de requisições e erros.
- Limites de execução configurados para uso controlado.

### 3. ⚡ Stress Testing
- Perfis Load Test, Spike Test e Endurance Test.
- Métricas de requisições, erros e latência.
- Execução limitada a 2 requisições por segundo e duração máxima de 10 segundos.
- Validação de escopo e restrições para alvos.

### 4. 🧪 Exploitation Simulation
- Simulação educacional de SQL Injection.
- Comparação entre consultas vulneráveis e parametrizadas.
- Demonstração de possível bypass de autenticação.
- Uso de SQLite temporário em memória e dados fictícios.
- Registro de evidências em JSON.

### 5. 📊 Campaign Reports
- Listagem de relatórios.
- Visualização de resultados.
- Consulta de métricas e evidências.
- Tratamento de relatórios inválidos ou incompletos.

### 6. 🌐 Web Reconnaissance
- Identificação de status HTTP.
- Extração do título da página.
- Identificação de servidor e Content-Type.
- Consulta de métodos HTTP anunciados.
- Verificação de cabeçalhos de segurança.
- Consulta ao arquivo robots.txt.
- Limitação da quantidade de conteúdo HTTP lido.
- Geração de relatórios JSON.

As verificações são informativas: cabeçalhos ausentes ou métodos anunciados não representam, isoladamente, vulnerabilidades confirmadas.

---

## 🧩 Gerenciamento e controle

Além dos módulos de análise, o menu disponibiliza:

- **Campaign Manager:** gerenciamento de campanhas.
- **Execution History:** consulta do histórico de execuções.
- **System Information:** informações da aplicação e configurações do laboratório.

A estrutura `core` centraliza configurações, banco de dados, escopo, operações, campanhas, registros e controle de execução.

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python | Linguagem principal |
| Requests | Requisições HTTP |
| Rich | Interface no terminal |
| SQLite | Persistência e simulação SQL |
| JSON | Relatórios |
| Unittest | Testes automatizados |
| Git | Controle de versão |

---

## 📋 Requisitos

- Python 3.
- Git (recomendado).
- PowerShell, CMD ou terminal Linux.
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

O menu principal disponibiliza seis módulos funcionais, além das opções de gerenciamento, histórico e informações do sistema.

---

## 🧪 Testes automatizados

O projeto utiliza `unittest` para validar seus componentes e funcionalidades.

Execute todos os testes:

**Windows PowerShell:**

```powershell
python -m unittest discover -s tests -v
```

**Linux:**

```bash
python -m unittest discover -s tests -v
```

A versão 2.0.0 foi validada com **175 testes automatizados aprovados**.

---

## 📁 Estrutura do projeto

```text
BLACKOUT-LAB/
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
│   ├── exploitation.py
│   ├── recon.py
│   ├── reports.py
│   ├── stress.py
│   ├── traffic.py
│   └── web_recon.py
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
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

Relatórios JSON, bancos de dados locais, logs, ambientes virtuais e arquivos temporários são mantidos fora do controle de versão por meio do `.gitignore`.

---

## 🔐 Uso responsável e segurança

O BLACKOUT LAB foi desenvolvido para aprendizado e testes autorizados.

- Utilize somente sistemas próprios ou com autorização expressa.
- Respeite as regras e os limites de escopo.
- Execute testes de tráfego e estresse em ambientes controlados.
- Não utilize a ferramenta para interromper serviços ou prejudicar terceiros.
- Realize simulações de exploração somente em laboratórios educacionais.

Os testes de tráfego e estresse possuem limites conservadores. O laboratório experimental de longa duração permanece desabilitado por padrão.

**Esta versão não implementa funcionalidade operacional de DoS ou DDoS.**

O desenvolvedor não se responsabiliza pelo uso indevido da ferramenta.

---

## 🎯 Objetivo do projeto

O BLACKOUT LAB nasceu da vontade de transformar conhecimento teórico em experiência prática.

A construção do projeto envolve desenvolvimento Python, organização modular, testes automatizados, reconhecimento, análise web, simulação controlada de exploração e fundamentos de segurança ofensiva.

O projeto continua em evolução, com foco em aprendizado, qualidade de código e desenvolvimento de ferramentas próprias.

---

## 👨‍💻 Desenvolvedor

**Victor Andrey**

Estudante de Engenharia de Software | Cybersecurity | Red Team | Ethical Hacking | Python | Cloud Computing.

GitHub: https://github.com/vandreysouzat-code

Projeto: https://github.com/vandreysouzat-code/BLACKOUT-LAB

---

*Aprender construindo. Evoluir testando. Proteger entendendo. 🖤*