"""Widoki związane z prezentacją struktury sieci BCMP.

Np. tabele/listy węzłów i klas, prosty graficzny rysunek sieci, itp.
"""

from typing import Dict, List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from bcmp.config_schema import RoutingEntry
from bcmp.network import BCMPNetwork
from bcmp.routing import build_routing_matrix


class NetworkView(QWidget):
    """Widok prezentujący aktualną konfigurację sieci."""

    def __init__(self, network: BCMPNetwork) -> None:
        super().__init__()
        self.network = network
        self._loading = False

        self.node_ids: List[str] = [node.id for node in self.network.config.nodes]
        self.class_ids: List[str] = [cls.id for cls in self.network.config.classes]

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self._init_classes_tab()
        self._init_nodes_tab()
        self._init_routing_tab()

        self.refresh()

    # --- Initialization helpers -------------------------------------------------
    def _init_classes_tab(self) -> None:
        container = QWidget()
        tab_layout = QVBoxLayout()
        container.setLayout(tab_layout)

        self.class_table = QTableWidget()
        self.class_table.setColumnCount(3)
        self.class_table.setHorizontalHeaderLabels(["ID", "Name", "Population"])
        self.class_table.cellChanged.connect(self._on_class_changed)

        tab_layout.addWidget(QLabel("Customer classes"))
        tab_layout.addWidget(self.class_table)

        self.tabs.addTab(container, "Classes")

    def _init_nodes_tab(self) -> None:
        container = QWidget()
        tab_layout = QVBoxLayout()
        container.setLayout(tab_layout)

        self.node_table = QTableWidget()
        self.node_table.setColumnCount(4)
        self.node_table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Servers"])
        self.node_table.cellChanged.connect(self._on_node_changed)

        self.service_rate_table = QTableWidget()
        self.service_rate_table.cellChanged.connect(self._on_service_rate_changed)

        tab_layout.addWidget(QLabel("Service centers"))
        tab_layout.addWidget(self.node_table)
        tab_layout.addWidget(QLabel("Service rates per class"))
        tab_layout.addWidget(self.service_rate_table)

        self.tabs.addTab(container, "Nodes")

    def _init_routing_tab(self) -> None:
        self.routing_tab = QTabWidget()
        self.routing_tables: Dict[str, QTableWidget] = {}

        for class_id in self.class_ids:
            table = QTableWidget()
            table.cellChanged.connect(lambda row, col, cid=class_id: self._on_routing_changed(cid, row, col))
            self.routing_tables[class_id] = table
            wrapper = QWidget()
            wrapper_layout = QVBoxLayout()
            wrapper.setLayout(wrapper_layout)
            wrapper_layout.addWidget(QLabel(f"Routing for class {class_id}"))
            wrapper_layout.addWidget(table)
            self.routing_tab.addTab(wrapper, class_id)

        self.tabs.addTab(self.routing_tab, "Routing")

    # --- Refresh helpers --------------------------------------------------------
    def refresh(self) -> None:
        self._loading = True
        try:
            self._refresh_classes()
            self._refresh_nodes()
            self._refresh_service_rates()
            self._refresh_routing()
        finally:
            self._loading = False

    def _refresh_classes(self) -> None:
        classes = self.network.config.classes
        self.class_table.setRowCount(len(classes))

        for row, cls in enumerate(classes):
            for col, value in enumerate([cls.id, cls.name, str(cls.population)]):
                item = QTableWidgetItem(value)
                if col == 0:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.class_table.setItem(row, col, item)

        self.class_table.resizeColumnsToContents()

    def _refresh_nodes(self) -> None:
        nodes = self.network.config.nodes
        self.node_table.setRowCount(len(nodes))

        for row, node in enumerate(nodes):
            values = [node.id, node.name, node.node_type, str(node.servers or "")]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col == 0:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.node_table.setItem(row, col, item)

        self.node_table.resizeColumnsToContents()

    def _refresh_service_rates(self) -> None:
        nodes = self.network.config.nodes
        classes = self.network.config.classes

        self.service_rate_table.setColumnCount(len(classes) + 1)
        headers = ["Node "] + [cls.id for cls in classes]
        self.service_rate_table.setHorizontalHeaderLabels(headers)
        self.service_rate_table.setRowCount(len(nodes))

        for row, node in enumerate(nodes):
            node_id_item = QTableWidgetItem(node.id)
            node_id_item.setFlags(node_id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.service_rate_table.setItem(row, 0, node_id_item)

            for col, cls in enumerate(classes, start=1):
                rate = node.service_rates_per_class.get(cls.id, 0.0)
                item = QTableWidgetItem(str(rate))
                self.service_rate_table.setItem(row, col, item)

        self.service_rate_table.resizeColumnsToContents()

    def _refresh_routing(self) -> None:
        nodes = self.node_ids

        for class_id, table in self.routing_tables.items():
            table.blockSignals(True)
            table.setRowCount(len(nodes))
            table.setColumnCount(len(nodes))
            table.setHorizontalHeaderLabels(nodes)
            table.setVerticalHeaderLabels(nodes)

            routing_matrix = self.network.routing_matrices.get(class_id, {})
            for row, from_node in enumerate(nodes):
                outgoing = routing_matrix.get(from_node, {})
                for col, to_node in enumerate(nodes):
                    value = outgoing.get(to_node, 0.0)
                    table.setItem(row, col, QTableWidgetItem(str(value)))
            table.resizeColumnsToContents()
            table.blockSignals(False)

    # --- Change handlers --------------------------------------------------------
    def _on_class_changed(self, row: int, column: int) -> None:
        if self._loading or column != 2:
            return
        try:
            population = int(self.class_table.item(row, column).text())
        except ValueError:
            return

        cls_config = self.network.config.classes[row]
        cls_config.population = population
        self.network.classes[cls_config.id].config.population = population

    def _on_node_changed(self, row: int, column: int) -> None:
        if self._loading:
            return

        node_config = self.network.config.nodes[row]
        item = self.node_table.item(row, column)
        if item is None:
            return

        text = item.text()
        if column == 1:
            node_config.name = text
        elif column == 2:
            node_config.node_type = text  # free-form to keep editing simple
        elif column == 3:
            try:
                node_config.servers = int(text) if text else None
            except ValueError:
                return
        self.network.nodes[node_config.id].config = node_config

    def _on_service_rate_changed(self, row: int, column: int) -> None:
        if self._loading or column == 0:
            return

        node_id_item = self.service_rate_table.item(row, 0)
        if node_id_item is None:
            return

        node_id = node_id_item.text()
        class_id = self.service_rate_table.horizontalHeaderItem(column).text()

        try:
            value = float(self.service_rate_table.item(row, column).text())
        except (TypeError, ValueError):
            return

        node = self.network.nodes.get(node_id)
        if node:
            node.config.service_rates_per_class[class_id] = value

        for config_node in self.network.config.nodes:
            if config_node.id == node_id:
                config_node.service_rates_per_class[class_id] = value

    def _on_routing_changed(self, class_id: str, row: int, column: int) -> None:
        if self._loading:
            return

        table = self.routing_tables[class_id]
        from_node = self.node_ids[row]
        to_node = self.node_ids[column]

        try:
            probability = float(table.item(row, column).text())
        except (TypeError, ValueError):
            probability = 0.0

        # Aktualizacja konfiguracji
        entries = self.network.config.routing_per_class.get(class_id, [])
        updated: Dict[str, Dict[str, float]] = {}
        for entry in entries:
            updated.setdefault(entry.from_node_id, {})[entry.to_node_id] = entry.probability

        updated.setdefault(from_node, {})[to_node] = probability

        new_entries: List[RoutingEntry] = []
        for f_node, outgoing in updated.items():
            for t_node, prob in outgoing.items():
                new_entries.append(RoutingEntry(f_node, t_node, prob))

        self.network.config.routing_per_class[class_id] = new_entries
        self.network.routing_matrices[class_id] = build_routing_matrix(new_entries)
