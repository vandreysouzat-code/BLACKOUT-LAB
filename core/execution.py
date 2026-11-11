
"""
Controlador central de execução do SOVIK 2.0.

Gerencia duração, cancelamento e estado de experimentos.
Não executa operações de rede.
"""

import threading
import time


class ExecutionController:
    """Controla o ciclo de vida de uma execução limitada."""

    def __init__(self, duration, max_duration):
        if isinstance(duration, bool) or not isinstance(duration, int):
            raise ValueError("A duração deve ser um número inteiro.")

        if isinstance(max_duration, bool) or not isinstance(max_duration, int):
            raise ValueError("O limite máximo deve ser um número inteiro.")

        if max_duration < 1:
            raise ValueError("O limite máximo deve ser positivo.")

        if not 1 <= duration <= max_duration:
            raise ValueError(
                f"A duração deve estar entre 1 e {max_duration} segundos."
            )

        self.duration = duration
        self.max_duration = max_duration

        self._stop_event = threading.Event()
        self._started_at = None
        self._deadline = None
        self._lock = threading.Lock()

    @property
    def started(self):
        """Indica se a execução foi iniciada."""

        return self._started_at is not None

    @property
    def cancelled(self):
        """Indica se houve solicitação de cancelamento."""

        return self._stop_event.is_set()

    @property
    def remaining_seconds(self):
        """Retorna o tempo restante da execução."""

        if not self.started:
            return self.duration

        if self.cancelled:
            return 0

        remaining = self._deadline - time.monotonic()

        return max(0, remaining)

    @property
    def active(self):
        """Indica se a execução pode continuar."""

        if not self.started or self.cancelled:
            return False

        return self.remaining_seconds > 0

    def start(self):
        """Inicia o controle de tempo uma única vez."""

        with self._lock:
            if self.started:
                raise RuntimeError(
                    "Esta execução já foi iniciada."
                )

            self._started_at = time.monotonic()
            self._deadline = self._started_at + self.duration

        return self

    def stop(self):
        """Solicita o encerramento da execução."""

        self._stop_event.set()

    def wait(self, interval=0.1):
        """
        Aguarda um intervalo ou até o cancelamento.

        Retorna True quando o intervalo termina.
        Retorna False quando a execução deve parar.
        """

        if not self.started:
            raise RuntimeError(
                "A execução precisa ser iniciada antes da espera."
            )

        if isinstance(interval, bool) or not isinstance(interval, (int, float)):
            raise ValueError("O intervalo deve ser numérico.")

        if interval <= 0:
            raise ValueError("O intervalo deve ser positivo.")

        if not self.active:
            return False

        wait_time = min(interval, self.remaining_seconds)

        if self._stop_event.wait(wait_time):
            return False

        return self.active

    def raise_if_stopped(self):
        """Interrompe o fluxo quando a execução não está ativa."""

        if not self.active:
            raise RuntimeError(
                "Execução encerrada, cancelada ou não iniciada."
            )
