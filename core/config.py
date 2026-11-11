
"""
Configurações centrais do SOVIK 2.0.

Centraliza caminhos, parâmetros de rede e limites
de execução dos módulos da plataforma.
"""

from pathlib import Path


# ============================================================
# IDENTIDADE DA PLATAFORMA
# ============================================================

APP_NAME = "SOVIK"
APP_VERSION = "2.0.0"


# ============================================================
# CAMINHOS DO PROJETO
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
LOGS_DIR = PROJECT_ROOT / "logs"


# ============================================================
# CONFIGURAÇÕES GERAIS DE REDE
# ============================================================

DEFAULT_TIMEOUT = 3
USER_AGENT = "SOVIK/2.0"

MAX_HTTP_RESPONSE_BYTES = 500_000

FOLLOW_HTTP_REDIRECTS = False


# ============================================================
# RECONNAISSANCE
# ============================================================

MAX_RECON_PORTS = 20
MAX_RECON_WORKERS = 20


# ============================================================
# TESTES COMUNS DE TRÁFEGO
# ============================================================

MAX_TRAFFIC_RPS = 2
MAX_TRAFFIC_DURATION = 10

MAX_STRESS_RPS = 2
MAX_STRESS_DURATION = 10


# ============================================================
# LABORATÓRIO DE DISPONIBILIDADE E RESILIÊNCIA
# ============================================================

# O laboratório permanece desabilitado por padrão.
# Experimentos prolongados devem ocorrer em ambiente
# local, isolado e explicitamente autorizado.

DOS_LAB_ENABLED = False

DOS_LAB_REQUIRE_ISOLATED_NETWORK = True
DOS_LAB_REQUIRE_EXPLICIT_SCOPE = True

# Duração máxima administrativa do experimento.
# Aumentar o tempo não aumenta a taxa de requisições.
DOS_LAB_MAX_DURATION = 3600

# Limite de concorrência para instrumentação local.
DOS_LAB_MAX_WORKERS = 2

# Execução distribuída permanece desabilitada.
DOS_LAB_DISTRIBUTED_ENABLED = False

# Intervalo mínimo entre verificações de disponibilidade.
DOS_LAB_MONITOR_INTERVAL = 5

# Tempo máximo de espera por resposta do serviço local.
DOS_LAB_REQUEST_TIMEOUT = 3

# Limite de registros mantidos em memória por experimento.
DOS_LAB_MAX_RESULTS = 10000


# ============================================================
# SEGURANÇA E ESCOPO
# ============================================================

ALLOW_PUBLIC_TARGETS = False
REQUIRE_EXPLICIT_SCOPE = True
