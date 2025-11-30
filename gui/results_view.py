"""Widoki do prezentacji wyników obliczeń MVA (metoda SUM)."""

from PyQt6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from bcmp.network import BCMPNetwork


class ResultsView(QWidget):
    """Widok prezentujący wyniki obliczeń sieci BCMP."""

    def __init__(self, network: BCMPNetwork) -> None:
        super().__init__()
        self.network = network

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Throughput per class"))
        self.throughput_table = QTableWidget()
        self.throughput_table.setColumnCount(2)
        self.throughput_table.setHorizontalHeaderLabels(["Class", "Throughput"])
        layout.addWidget(self.throughput_table)

        layout.addWidget(QLabel("Node metrics (mean customers / mean response time)"))
        self.node_table = QTableWidget()
        self.node_table.setColumnCount(4)
        self.node_table.setHorizontalHeaderLabels(["Node", "Class", "Mean customers", "Mean response time"])
        layout.addWidget(self.node_table)

        self.refresh()

    def refresh(self) -> None:
        self._refresh_throughput()
        self._refresh_nodes()

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
                rows.append((node_id, class_id, class_metrics.mean_customers, class_metrics.mean_response_time))

        self.node_table.setRowCount(len(rows))
        for row_idx, (node_id, class_id, mean_customers, mean_response) in enumerate(rows):
            self.node_table.setItem(row_idx, 0, QTableWidgetItem(node_id))
            self.node_table.setItem(row_idx, 1, QTableWidgetItem(class_id))
            self.node_table.setItem(row_idx, 2, QTableWidgetItem(f"{mean_customers:.4f}"))
            self.node_table.setItem(row_idx, 3, QTableWidgetItem(f"{mean_response:.4f}"))

        self.node_table.resizeColumnsToContents()
