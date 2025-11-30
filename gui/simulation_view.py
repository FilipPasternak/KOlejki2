"""Widok odpowiedzialny za wizualizację symulacji zgłoszeń."""

from __future__ import annotations

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from bcmp.network import BCMPNetwork
from bcmp.simulation import TicketSimulation


class SimulationView(QWidget):
    """Prosty panel prezentujący w czasie rzeczywistym przepływ zgłoszeń."""

    def __init__(self, network: BCMPNetwork, simulation: TicketSimulation) -> None:
        super().__init__()
        self.network = network
        self.simulation = simulation

        self._timer = QTimer(self)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start()

        layout = QVBoxLayout()
        self.setLayout(layout)

        controls = QGroupBox("Sterowanie symulacją")
        controls_layout = QGridLayout()
        controls.setLayout(controls_layout)

        self.start_button = QPushButton("Start/Pauza")
        self.start_button.clicked.connect(self.simulation.toggle)
        controls_layout.addWidget(self.start_button, 0, 0)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self._on_reset)
        controls_layout.addWidget(self.reset_button, 0, 1)

        layout.addWidget(controls)

        self.node_table = QTableWidget()
        self.node_table.setColumnCount(3)
        self.node_table.setHorizontalHeaderLabels(["Węzeł", "W kolejce", "W obsłudze"])
        layout.addWidget(self.node_table)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMinimumHeight(200)
        layout.addWidget(QLabel("Dziennik zdarzeń"))
        layout.addWidget(self.log_box)

        self.refresh()

    def _on_tick(self) -> None:
        self.simulation.step(0.5)
        self.refresh()

    def _on_reset(self) -> None:
        self.simulation.reset()
        self.refresh()

    def refresh(self) -> None:
        snapshot = self.simulation.snapshot()
        node_ids = [node.id for node in self.network.config.nodes]
        self.node_table.setRowCount(len(node_ids))

        for row, node_id in enumerate(node_ids):
            queue_len, in_service = snapshot.node_states.get(node_id, (0, 0))
            self.node_table.setItem(row, 0, QTableWidgetItem(node_id))
            self.node_table.setItem(row, 1, QTableWidgetItem(str(queue_len)))
            self.node_table.setItem(row, 2, QTableWidgetItem(str(in_service)))
        self.node_table.resizeColumnsToContents()

        self.log_box.setPlainText("\n".join(snapshot.events))
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())
