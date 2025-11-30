"""Prosta, zegarowa symulacja przepływu zgłoszeń w sieci BCMP.

Symulacja ma charakter ilustracyjny – na podstawie konfiguracji sieci
zamyka określoną populację zgłoszeń w obiegu i co takt przesuwa je zgodnie
z macierzami routingu oraz czasami obsługi wynikającymi z intensywności
obsługi.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from bcmp.network import BCMPNetwork
from bcmp.metrics import NodePerformanceSummary


@dataclass
class Ticket:
    """Reprezentuje pojedyncze zgłoszenie w symulacji."""

    id: int
    class_id: str
    current_node: str
    remaining_service: float = 0.0
    enqueued_at: float = 0.0
    started_at: float = 0.0


@dataclass
class NodeRuntimeState:
    """Stan węzła w trakcie symulacji."""

    in_service: List[Ticket] = field(default_factory=list)
    queue: List[Ticket] = field(default_factory=list)
    queue_history: List[Tuple[float, int]] = field(default_factory=list)
    total_time: float = 0.0
    queue_area: float = 0.0
    system_area: float = 0.0
    busy_area: float = 0.0
    waiting_time_total: float = 0.0
    system_time_total: float = 0.0
    completed: int = 0


@dataclass
class SimulationSnapshot:
    """Agregat stanu przekazywany do GUI."""

    node_states: Dict[str, Tuple[int, int]]
    events: List[str]
    queue_history: Dict[str, List[Tuple[float, int]]]
    empirical_metrics: Dict[str, NodePerformanceSummary]


class TicketSimulation:
    """Symulator tickowy na potrzeby wizualizacji GUI."""

    def __init__(self, network: BCMPNetwork, seed: int | None = None) -> None:
        self.network = network
        self.random = random.Random(seed)
        self._ticket_counter = 0
        self._events: List[str] = []
        self.running = False
        self.current_time = 0.0

        self.node_state: Dict[str, NodeRuntimeState] = {
            node_id: NodeRuntimeState() for node_id in self.network.nodes
        }
        self.tickets: List[Ticket] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def reset(self) -> None:
        self._ticket_counter = 0
        self._events.clear()
        self.tickets.clear()
        self.current_time = 0.0
        for state in self.node_state.values():
            state.in_service.clear()
            state.queue.clear()
            state.queue_history.clear()
            state.total_time = 0.0
            state.queue_area = 0.0
            state.system_area = 0.0
            state.busy_area = 0.0
            state.waiting_time_total = 0.0
            state.system_time_total = 0.0
            state.completed = 0

    def start(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False

    def toggle(self) -> None:
        self.running = not self.running

    def step(self, elapsed_seconds: float) -> None:
        """Wykonuje pojedynczy krok symulacji.

        - Wstrzykuje nowe zgłoszenia, gdy populacja jest mniejsza niż zadana.
        - Rozdziela zgłoszenia na dostępne serwery.
        - Dekrementuje czasy obsługi i przenosi zgłoszenia do kolejnych węzłów.
        """

        if not self.running:
            return

        self._spawn_missing_tickets()
        self._assign_servers()
        self._record_interval(elapsed_seconds)
        end_time = self.current_time + elapsed_seconds
        self._progress_service(elapsed_seconds, end_time)
        self.current_time = end_time

    def snapshot(self, max_events: int = 15) -> SimulationSnapshot:
        node_states = {
            node_id: (
                len(state.queue),
                len(state.in_service),
            )
            for node_id, state in self.node_state.items()
        }
        events = self._events[-max_events:]
        return SimulationSnapshot(
            node_states=node_states,
            events=events,
            queue_history={node_id: state.queue_history for node_id, state in self.node_state.items()},
            empirical_metrics=self.empirical_performance(),
        )

    def empirical_performance(self) -> Dict[str, NodePerformanceSummary]:
        """Zwraca empiryczne metryki kolejki na podstawie zebranych danych."""

        metrics: Dict[str, NodePerformanceSummary] = {}
        for node_id, state in self.node_state.items():
            total_time = state.total_time if state.total_time > 0 else max(self.current_time, 1e-6)
            mean_queue_length = state.queue_area / total_time if total_time > 0 else 0.0
            mean_system_length = state.system_area / total_time if total_time > 0 else 0.0
            servers = self.network.nodes[node_id].config.servers
            server_capacity = servers if servers is not None else 0
            busy = state.busy_area / total_time if total_time > 0 else 0.0
            utilization = busy / server_capacity if server_capacity else 0.0

            arrival_rate = state.completed / total_time if total_time > 0 else 0.0
            mean_waiting = (
                state.waiting_time_total / state.completed
                if state.completed > 0
                else (mean_queue_length / arrival_rate if arrival_rate > 0 else 0.0)
            )
            mean_system = (
                state.system_time_total / state.completed
                if state.completed > 0
                else (mean_system_length / arrival_rate if arrival_rate > 0 else 0.0)
            )

            metrics[node_id] = NodePerformanceSummary(
                mean_queue_length=mean_queue_length,
                mean_system_length=mean_system_length,
                mean_waiting_time=mean_waiting,
                mean_system_time=mean_system,
                utilization=utilization,
            )

        return metrics

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _spawn_missing_tickets(self) -> None:
        for class_config in self.network.config.classes:
            current = sum(1 for t in self.tickets if t.class_id == class_config.id)
            missing = class_config.population - current
            for _ in range(max(0, missing)):
                ticket = self._create_ticket(class_config.id)
                self.tickets.append(ticket)
                self._enqueue("INTAKE", ticket)
                self._log(
                    f"{ticket.class_id}#{ticket.id} trafił do INTAKE (nowe zgłoszenie)"
                )

    def _create_ticket(self, class_id: str) -> Ticket:
        self._ticket_counter += 1
        return Ticket(id=self._ticket_counter, class_id=class_id, current_node="INTAKE")

    def _enqueue(self, node_id: str, ticket: Ticket) -> None:
        ticket.current_node = node_id
        ticket.enqueued_at = self.current_time
        self.node_state[node_id].queue.append(ticket)

    def _assign_servers(self) -> None:
        for node_id, state in self.node_state.items():
            config = self.network.nodes[node_id].config
            servers = config.servers or len(state.queue) + len(state.in_service)
            available = max(0, servers - len(state.in_service))
            if available <= 0:
                continue

            for _ in range(available):
                if not state.queue:
                    break
                ticket = state.queue.pop(0)
                service_rate = config.service_rates_per_class.get(ticket.class_id)
                if service_rate is None or service_rate <= 0:
                    continue
                ticket.remaining_service = self.random.expovariate(service_rate)
                state.waiting_time_total += max(self.current_time - ticket.enqueued_at, 0.0)
                ticket.started_at = self.current_time
                state.in_service.append(ticket)
                self._log(
                    f"{ticket.class_id}#{ticket.id} rozpoczął obsługę w {node_id}"
                )

    def _progress_service(self, elapsed_seconds: float, end_time: float) -> None:
        for node_id, state in self.node_state.items():
            completed: List[Ticket] = []
            for ticket in state.in_service:
                ticket.remaining_service -= elapsed_seconds
                if ticket.remaining_service <= 0:
                    completed.append(ticket)

            for ticket in completed:
                state.in_service.remove(ticket)
                state.system_time_total += max(end_time - ticket.enqueued_at, 0.0)
                state.completed += 1
                next_node = self._choose_next_node(ticket)
                if next_node is None:
                    self._log(
                        f"{ticket.class_id}#{ticket.id} zakończył cykl i wraca do INTAKE"
                    )
                    self._enqueue("INTAKE", ticket)
                else:
                    self._log(
                        f"{ticket.class_id}#{ticket.id} przechodzi z {node_id} do {next_node}"
                    )
                    self._enqueue(next_node, ticket)

    def _choose_next_node(self, ticket: Ticket) -> str | None:
        routing_matrix = self.network.routing_matrices.get(ticket.class_id, {})
        outgoing = routing_matrix.get(ticket.current_node, {})
        if not outgoing:
            return None

        edges = list(outgoing.items())
        cumulative = []
        total = 0.0
        for _, prob in edges:
            total += prob
            cumulative.append(total)

        roll = self.random.random() * total
        for idx, threshold in enumerate(cumulative):
            if roll <= threshold:
                return edges[idx][0]

        return edges[-1][0]

    def _record_interval(self, elapsed_seconds: float) -> None:
        """Akumuluje pola powierzchni potrzebne do obliczeń empirycznych."""

        snapshot_time = self.current_time + elapsed_seconds
        for node_id, state in self.node_state.items():
            queue_len = len(state.queue)
            system_len = queue_len + len(state.in_service)
            servers = self.network.nodes[node_id].config.servers
            busy = min(len(state.in_service), servers) if servers is not None else 0

            state.total_time += elapsed_seconds
            state.queue_area += queue_len * elapsed_seconds
            state.system_area += system_len * elapsed_seconds
            state.busy_area += busy * elapsed_seconds

            state.queue_history.append((snapshot_time, queue_len))
            if len(state.queue_history) > 300:
                state.queue_history.pop(0)

    def _log(self, message: str) -> None:
        self._events.append(message)
        if len(self._events) > 200:
            self._events = self._events[-200:]
