"""Widoki do prezentacji wyników obliczeń MVA (metoda SUM)."""

from PyQt6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from bcmp.network import BCMPNetwork
from bcmp.simulation import TicketSimulation


class ResultsView(QWidget):
    """Widok prezentujący wyniki obliczeń sieci BCMP."""

    def __init__(self, network: BCMPNetwork, simulation: TicketSimulation | None = None) -> None:
        super().__init__()
        self.network = network
        self.simulation = simulation

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Throughput per class"))
        self.throughput_table = QTableWidget()
        self.throughput_table.setColumnCount(2)
        self.throughput_table.setHorizontalHeaderLabels(["Class", "Throughput"])
        layout.addWidget(self.throughput_table)

        layout.addWidget(QLabel("Node metrics (średnie wartości per klasa)"))
        self.node_table = QTableWidget()
        self.node_table.setColumnCount(7)
        self.node_table.setHorizontalHeaderLabels(
            [
                "Node",
                "Class",
                "L",
                "Lq",
                "W",
                "Wq",
                "ρ",
            ]
        )
        layout.addWidget(self.node_table)

        layout.addWidget(QLabel("Metryki kolejki – analiza vs symulacja"))
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(7)
        self.queue_table.setHorizontalHeaderLabels(["Źródło", "Węzeł", "Lq", "L", "Wq", "W", "ρ"])
        layout.addWidget(self.queue_table)

        self.refresh()

    def refresh(self) -> None:
        self._refresh_throughput()
        self._refresh_nodes()
        self._refresh_queue_summaries()

    def _refresh_throughput(self) -> None:
        metrics = self.network.metrics.throughput_per_class
        self.throughput_table.setRowCount(len(metrics))

        for row, (class_id, throughput) in enumerate(metrics.items()):
            self.throughput_table.setItem(row, 0, QTableWidgetItem(class_id))
            self.throughput_table.setItem(row, 1, QTableWidgetItem(f"{throughput:.4f}"))

        self.throughput_table.resizeColumnsToContents()

    def _refresh_nodes(self) -> None:
        metrics = self.network.metrics.per_node
        rows = []
        for node_id, node_metrics in metrics.items():
            for class_id, class_metrics in node_metrics.per_class.items():
                rows.append(
                    (
                        node_id,
                        class_id,
                        class_metrics.mean_customers,
                        class_metrics.mean_queue_length,
                        class_metrics.mean_response_time,
                        class_metrics.mean_waiting_time,
                        class_metrics.utilization,
                    )
                )

        self.node_table.setRowCount(len(rows))
        for row_idx, (node_id, class_id, mean_customers, mean_queue, mean_response, mean_waiting, utilization) in enumerate(rows):
            self.node_table.setItem(row_idx, 0, QTableWidgetItem(node_id))
            self.node_table.setItem(row_idx, 1, QTableWidgetItem(class_id))
            self.node_table.setItem(row_idx, 2, QTableWidgetItem(f"{mean_customers:.4f}"))
            self.node_table.setItem(row_idx, 3, QTableWidgetItem(f"{mean_queue:.4f}"))
            self.node_table.setItem(row_idx, 4, QTableWidgetItem(f"{mean_response:.4f}"))
            self.node_table.setItem(row_idx, 5, QTableWidgetItem(f"{mean_waiting:.4f}"))
            self.node_table.setItem(row_idx, 6, QTableWidgetItem(f"{utilization:.4f}"))

        self.node_table.resizeColumnsToContents()

    def _refresh_queue_summaries(self) -> None:
        analytic_rows = []
        for node_id, node_metrics in self.network.metrics.per_node.items():
            if node_metrics.summary:
                analytic_rows.append(("Analiza", node_id, node_metrics.summary))

        empirical_rows = []
        if self.simulation is not None:
            for node_id, summary in self.simulation.empirical_performance().items():
                empirical_rows.append(("Symulacja", node_id, summary))

        rows = analytic_rows + empirical_rows
        self.queue_table.setRowCount(len(rows))

        for row_idx, (source, node_id, summary) in enumerate(rows):
            self.queue_table.setItem(row_idx, 0, QTableWidgetItem(source))
            self.queue_table.setItem(row_idx, 1, QTableWidgetItem(node_id))
            self.queue_table.setItem(row_idx, 2, QTableWidgetItem(f"{summary.mean_queue_length:.4f}"))
            self.queue_table.setItem(row_idx, 3, QTableWidgetItem(f"{summary.mean_system_length:.4f}"))
            self.queue_table.setItem(row_idx, 4, QTableWidgetItem(f"{summary.mean_waiting_time:.4f}"))
            self.queue_table.setItem(row_idx, 5, QTableWidgetItem(f"{summary.mean_system_time:.4f}"))
            self.queue_table.setItem(row_idx, 6, QTableWidgetItem(f"{summary.utilization:.4f}"))

        self.queue_table.resizeColumnsToContents()
