import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QTableWidget, QTableWidgetItem, QPushButton, 
                            QMessageBox, QInputDialog, QLineEdit, QLabel, 
                            QComboBox, QFormLayout, QDialog, QHBoxLayout, QHeaderView,
                            QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QIcon, QFont, QPixmap
import psycopg2

class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            "dbname": "mydb",
            "user": "postgres",
            "password": "123",
            "host": "localhost",
            "client_encoding": "utf8"
        }
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        if self.connection is None:
            try:
                self.connection = psycopg2.connect(**self.connection_params)
                self.cursor = self.connection.cursor()
                # Устанавливаем кодировку для текущей сессии
                self.cursor.execute("SET client_encoding TO 'UTF8';")
                self.connection.commit()
            except Exception as e:
                print(f"Error connecting to database: {e}")
                raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None

    def get_materials(self):
        try:
            self.connect()
            self.cursor.execute("""
                SELECT m.material_name, mt.material_type, m.unit_price, 
                       m.stock_qty, m.min_qty, m.pack_qty, m.unit
                FROM materials m
                JOIN material_type mt ON m.material_type = mt.material_type
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting materials: {e}")
            raise

    def add_material(self, name, type_id, price, quantity, min_quantity, package_quantity, unit):
        self.cursor.execute(
            "INSERT INTO materials (material_name, material_type, unit_price, stock_qty, min_qty, pack_qty, unit) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name, type_id, price, quantity, min_quantity, package_quantity, unit)
        )
        self.connection.commit()

    def update_material(self, material_name, type_id, price, quantity, min_quantity, package_quantity, unit):
        self.cursor.execute(
            "UPDATE materials SET material_type = %s, unit_price = %s, stock_qty = %s, min_qty = %s, pack_qty = %s, unit = %s WHERE material_name = %s",
            (type_id, price, quantity, min_quantity, package_quantity, unit, material_name)
        )
        self.connection.commit()

    def delete_material(self, material_name):
        self.cursor.execute("DELETE FROM materials WHERE material_name = %s", (material_name,))
        self.connection.commit()

    def get_material_types(self):
        self.cursor.execute("SELECT material_type, defect_percent FROM material_type")
        return self.cursor.fetchall()

    def get_products(self):
        self.cursor.execute("""
            SELECT p.product_name, pt.product_type, p.sku, p.min_price, p.roll_width
            FROM products p
            JOIN product_type pt ON p.product_type = pt.product_type
        """)
        return self.cursor.fetchall()

    def add_product(self, name, product_type, sku, min_price, roll_width):
        self.cursor.execute(
            "INSERT INTO products (product_name, product_type, sku, min_price, roll_width) VALUES (%s, %s, %s, %s, %s)",
            (name, product_type, sku, min_price, roll_width)
        )
        self.connection.commit()

    def update_product(self, old_name, name, product_type, sku, min_price, roll_width):
        self.cursor.execute(
            "UPDATE products SET product_name = %s, product_type = %s, sku = %s, min_price = %s, roll_width = %s WHERE product_name = %s",
            (name, product_type, sku, min_price, roll_width, old_name)
        )
        self.connection.commit()

    def delete_product(self, product_name):
        self.cursor.execute("DELETE FROM products WHERE product_name = %s", (product_name,))
        self.connection.commit()

    def get_product_types(self):
        self.cursor.execute("SELECT product_type, coef FROM product_type")
        return self.cursor.fetchall()

    def get_materials_by_product(self, product_name):
        self.cursor.execute("""
            SELECT m.material_name, pm.qty_needed 
            FROM product_materials pm 
            JOIN materials m ON pm.material_name = m.material_name 
            WHERE pm.product_name = %s
        """, (product_name,))
        return self.cursor.fetchall()

    def calculate_material_quantity(self, product_type_id, material_type_id, product_qty, param1, param2, stock_qty):
        try:
            # Get product type coefficient
            self.cursor.execute("SELECT coef FROM product_type WHERE product_type = %s", (product_type_id,))
            product_coef = self.cursor.fetchone()
            if not product_coef:
                return -1

            # Get material defect percent
            self.cursor.execute("SELECT defect_percent FROM material_type WHERE material_type = %s", (material_type_id,))
            defect_percent = self.cursor.fetchone()
            if not defect_percent:
                return -1

            # Calculate base quantity needed
            base_qty = param1 * param2 * product_coef[0]
            
            # Calculate total quantity needed with defect percentage
            total_qty = base_qty * product_qty * (1 + defect_percent[0]/100)
            
            # Calculate final quantity needed considering stock
            final_qty = max(0, total_qty - stock_qty)
            
            return int(final_qty)
        except:
            return -1

class MaterialDialog(QDialog):
    def __init__(self, material=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить материал" if not material else "Редактировать материал")
        self.material = material
        self.db = DatabaseManager()
        self.init_ui()
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #2D6033;
                font-weight: bold;
                font-size: 12px;
                font-family: Gabriola, serif;
            }
            QLineEdit, QComboBox {
                border: 2px solid #BBD9B2;
                border-radius: 6px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #2D6033;
                font-size: 12px;
                font-family: Gabriola, serif;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #2D6033;
            }
            QPushButton {
                background-color: #2D6033;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                font-family: Gabriola, serif;
            }
            QPushButton:hover {
                background-color: #1D4B2A;
            }
        """)

    def init_ui(self):
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Material name
        self.name_input = QLineEdit()
        layout.addRow("Наименование:", self.name_input)

        # Material type
        self.type_combo = QComboBox()
        types = self.db.get_material_types()
        for type_name, defect_percent in types:
            self.type_combo.addItem(type_name, type_name)
        layout.addRow("Тип материала:", self.type_combo)

        # Unit price
        self.price_input = QLineEdit()
        self.price_input.setValidator(QDoubleValidator(0, 999999, 2))
        layout.addRow("Цена единицы:", self.price_input)

        # Stock quantity
        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QDoubleValidator(0, 999999, 2))
        layout.addRow("Количество на складе:", self.quantity_input)

        # Minimum quantity
        self.min_quantity_input = QLineEdit()
        self.min_quantity_input.setValidator(QDoubleValidator(0, 999999, 2))
        layout.addRow("Минимальное количество:", self.min_quantity_input)

        # Package quantity
        self.package_input = QLineEdit()
        self.package_input.setValidator(QDoubleValidator(0, 999999, 2))
        layout.addRow("Количество в упаковке:", self.package_input)

        # Unit of measure
        self.unit_input = QLineEdit()
        layout.addRow("Единица измерения:", self.unit_input)

        # Fill fields if editing
        if self.material:
            self.name_input.setText(self.material[0])
            self.type_combo.setCurrentIndex(self.type_combo.findData(self.material[1]))
            self.price_input.setText(str(self.material[2]))
            self.quantity_input.setText(str(self.material[3]))
            self.min_quantity_input.setText(str(self.material[4]))
            self.package_input.setText(str(self.material[5]))
            self.unit_input.setText(self.material[6])

        # Save button
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_material)
        layout.addRow(self.save_button)

        self.setLayout(layout)

    def save_material(self):
        try:
            name = self.name_input.text()
            type_id = self.type_combo.currentData()
            price = float(self.price_input.text())
            quantity = float(self.quantity_input.text())
            min_quantity = float(self.min_quantity_input.text())
            package_quantity = float(self.package_input.text())
            unit = self.unit_input.text()

            if not name or not type_id or not unit:
                raise ValueError("Не все обязательные поля заполнены")

            if price < 0 or quantity < 0 or min_quantity < 0 or package_quantity < 0:
                raise ValueError("Значения не могут быть отрицательными")

            if self.material:
                self.db.update_material(
                    self.material[0], type_id, price, 
                    quantity, min_quantity, package_quantity, unit
                )
            else:
                self.db.add_material(
                    name, type_id, price, quantity, 
                    min_quantity, package_quantity, unit
                )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить материал: {str(e)}")

class ProductDialog(QDialog):
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить продукт" if not product else "Редактировать продукт")
        self.product = product
        self.db = DatabaseManager()
        self.init_ui()
        self.setMinimumWidth(500)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #2D6033;
                font-weight: bold;
                font-size: 12px;
                font-family: Gabriola, serif;
            }
            QLineEdit, QComboBox {
                border: 2px solid #BBD9B2;
                border-radius: 6px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #2D6033;
                font-size: 12px;
                font-family: Gabriola, serif;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #2D6033;
            }
            QPushButton {
                background-color: #2D6033;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                font-family: Gabriola, serif;
            }
            QPushButton:hover {
                background-color: #1D4B2A;
            }
        """)

    def init_ui(self):
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Product name
        self.name_input = QLineEdit()
        layout.addRow("Наименование:", self.name_input)

        # Product type
        self.type_combo = QComboBox()
        types = self.db.get_product_types()
        for type_name, coef in types:
            self.type_combo.addItem(type_name, type_name)
        layout.addRow("Тип продукта:", self.type_combo)

        # SKU
        self.sku_input = QLineEdit()
        layout.addRow("Артикул:", self.sku_input)

        # Minimum price
        self.price_input = QLineEdit()
        self.price_input.setValidator(QDoubleValidator(0, 999999, 2))
        layout.addRow("Минимальная цена:", self.price_input)

        # Roll width
        self.width_input = QLineEdit()
        self.width_input.setValidator(QDoubleValidator(0, 999999, 2))
        layout.addRow("Ширина рулона:", self.width_input)

        # Fill fields if editing
        if self.product:
            self.name_input.setText(self.product[0])
            self.type_combo.setCurrentIndex(self.type_combo.findData(self.product[1]))
            self.sku_input.setText(self.product[2])
            self.price_input.setText(str(self.product[3]))
            self.width_input.setText(str(self.product[4]))

        # Save button
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_product)
        layout.addRow(self.save_button)

        self.setLayout(layout)

    def save_product(self):
        try:
            name = self.name_input.text()
            product_type = self.type_combo.currentData()
            sku = self.sku_input.text()
            min_price = float(self.price_input.text())
            roll_width = float(self.width_input.text())

            if not name or not product_type or not sku:
                raise ValueError("Не все обязательные поля заполнены")

            if min_price < 0 or roll_width < 0:
                raise ValueError("Цена и ширина рулона не могут быть отрицательными")

            if self.product:
                self.db.update_product(
                    self.product[0], name, product_type, sku, min_price, roll_width
                )
            else:
                self.db.add_product(
                    name, product_type, sku, min_price, roll_width
                )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить продукт: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система управления производством")
        self.setWindowIcon(QIcon('icon.png'))
        self.db = DatabaseManager()
        self.init_ui()
        self.setMinimumSize(1000, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
                font-family: Gabriola, serif;
            }
            QTableWidget {
                background-color: #FFFFFF;
                gridline-color: #BBD9B2;
                border: 1px solid #BBD9B2;
                border-radius: 8px;
                font-family: Gabriola, serif;
            }
            QTableWidget::item {
                padding: 8px;
                font-size: 12px;
                color: #333333;
                font-family: Gabriola, serif;
            }
            QTableWidget::item:selected {
                background-color: #2D6033;
                color: white;
            }
            QHeaderView::section {
                background-color: #2D6033;
                color: white;
                padding: 10px;
                border: none;
                font-size: 13px;
                font-weight: bold;
                font-family: Gabriola, serif;
            }
            QPushButton {
                background-color: #2D6033;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
                min-width: 120px;
                font-family: Gabriola, serif;
            }
            QPushButton:hover {
                background-color: #1D4B2A;
            }
            QPushButton:pressed {
                background-color: #1D4B2A;
            }
            QLabel {
                color: #2D6033;
                font-family: Gabriola, serif;
            }
            QDialog {
                background-color: #FFFFFF;
                font-family: Gabriola, serif;
            }
            QLineEdit, QComboBox {
                border: 2px solid #BBD9B2;
                border-radius: 6px;
                padding: 8px;
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #2D6033;
                font-size: 12px;
                font-family: Gabriola, serif;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #2D6033;
            }
            QMessageBox {
                background-color: #FFFFFF;
                font-family: Gabriola, serif;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                font-family: Gabriola, serif;
            }
            QTabWidget::pane {
                border: 1px solid #BBD9B2;
                background: #FFFFFF;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #BBD9B2;
                color: #333333;
                padding: 12px 20px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-weight: bold;
                font-family: Gabriola, serif;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                color: #2D6033;
            }
        """)

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Add logo
        logo_label = QLabel()
        pixmap = QPixmap('logo.png')
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaledToHeight(80, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)

        # Add title
        title_label = QLabel("Система управления производством")
        title_label.setStyleSheet("""
            font-size: 24px;
            color: #2D6033;
            font-weight: bold;
            padding: 16px 0;
            background-color: #BBD9B2;
            border-radius: 10px;
            font-family: Gabriola, serif;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Create tab widget
        self.tabs = QTabWidget()
        
        # Materials tab
        self.materials_tab = QWidget()
        self.init_materials_tab()
        self.tabs.addTab(self.materials_tab, "📦 Материалы")
        
        # Products tab
        self.products_tab = QWidget()
        self.init_products_tab()
        self.tabs.addTab(self.products_tab, "🛋️ Продукция")
        
        layout.addWidget(self.tabs)
        self.central_widget.setLayout(layout)

    def init_materials_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(6)
        self.materials_table.setHorizontalHeaderLabels(["Наименование", "Тип", "Цена", "Количество", "Мин. количество", "Ед. измерения"])
        self.materials_table.verticalHeader().setVisible(False)
        self.materials_table.setAlternatingRowColors(True)
        header = self.materials_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.materials_table)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.add_material_btn = QPushButton("➕ Добавить материал")
        self.add_material_btn.clicked.connect(self.add_material)
        button_layout.addWidget(self.add_material_btn)

        self.edit_material_btn = QPushButton("✏️ Редактировать")
        self.edit_material_btn.clicked.connect(self.edit_material)
        button_layout.addWidget(self.edit_material_btn)

        self.delete_material_btn = QPushButton("❌ Удалить")
        self.delete_material_btn.clicked.connect(self.delete_material)
        button_layout.addWidget(self.delete_material_btn)

        self.show_materials_btn = QPushButton("🔍 Показать материалы")
        self.show_materials_btn.clicked.connect(self.show_materials)
        button_layout.addWidget(self.show_materials_btn)

        layout.addLayout(button_layout)
        self.materials_tab.setLayout(layout)
        self.load_materials()

    def init_products_tab(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(["Наименование", "Тип", "Артикул", "Мин. цена", "Ширина рулона"])
        self.products_table.verticalHeader().setVisible(False)
        self.products_table.setAlternatingRowColors(True)
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.products_table)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.add_product_btn = QPushButton("➕ Добавить продукт")
        self.add_product_btn.clicked.connect(self.add_product)
        button_layout.addWidget(self.add_product_btn)

        self.edit_product_btn = QPushButton("✏️ Редактировать")
        self.edit_product_btn.clicked.connect(self.edit_product)
        button_layout.addWidget(self.edit_product_btn)

        self.delete_product_btn = QPushButton("❌ Удалить")
        self.delete_product_btn.clicked.connect(self.delete_product)
        button_layout.addWidget(self.delete_product_btn)

        self.show_materials_btn = QPushButton("🔍 Показать материалы")
        self.show_materials_btn.clicked.connect(self.show_product_materials)
        button_layout.addWidget(self.show_materials_btn)

        layout.addLayout(button_layout)
        self.products_tab.setLayout(layout)
        self.load_products()

    def load_materials(self):
        materials = self.db.get_materials()
        self.materials_table.setRowCount(len(materials))
        for row, material in enumerate(materials):
            for col, value in enumerate(material):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.materials_table.setItem(row, col, item)

    def load_products(self):
        products = self.db.get_products()
        self.products_table.setRowCount(len(products))
        for row, product in enumerate(products):
            for col, value in enumerate(product):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.products_table.setItem(row, col, item)

    def add_material(self):
        dialog = MaterialDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.load_materials()

    def edit_material(self):
        selected = self.materials_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите материал для редактирования!")
            return

        material_name = self.materials_table.item(selected[0].row(), 0).text()
        materials = self.db.get_materials()
        material = next((m for m in materials if m[0] == material_name), None)

        if material:
            dialog = MaterialDialog(material)
            if dialog.exec_() == QDialog.Accepted:
                self.load_materials()

    def delete_material(self):
        selected = self.materials_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите материал для удаления!")
            return

        material_name = self.materials_table.item(selected[0].row(), 0).text()
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этот материал?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_material(material_name)
            self.load_materials()

    def show_materials(self):
        selected = self.materials_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите материал!")
            return

        material_name = self.materials_table.item(selected[0].row(), 0).text()
        products = self.db.get_materials_by_product(material_name)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Продукция, использующая {material_name}")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Продукция", "Количество"])
        table.setRowCount(len(products))
        
        for row, (product, quantity) in enumerate(products):
            table.setItem(row, 0, QTableWidgetItem(product))
            table.setItem(row, 1, QTableWidgetItem(str(quantity)))
        
        table.resizeColumnsToContents()
        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec_()

    def add_product(self):
        dialog = ProductDialog()
        if dialog.exec_() == QDialog.Accepted:
            self.load_products()

    def edit_product(self):
        selected = self.products_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите продукт для редактирования!")
            return

        product_name = self.products_table.item(selected[0].row(), 0).text()
        products = self.db.get_products()
        product = next((p for p in products if p[0] == product_name), None)

        if product:
            dialog = ProductDialog(product)
            if dialog.exec_() == QDialog.Accepted:
                self.load_products()

    def delete_product(self):
        selected = self.products_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите продукт для удаления!")
            return

        product_name = self.products_table.item(selected[0].row(), 0).text()
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этот продукт?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_product(product_name)
            self.load_products()

    def show_product_materials(self):
        selected = self.products_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите продукт!")
            return

        product_name = self.products_table.item(selected[0].row(), 0).text()
        materials = self.db.get_materials_by_product(product_name)

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Материалы для {product_name}")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Материал", "Количество"])
        table.setRowCount(len(materials))
        
        for row, (material, quantity) in enumerate(materials):
            table.setItem(row, 0, QTableWidgetItem(material))
            table.setItem(row, 1, QTableWidgetItem(str(quantity)))
        
        table.resizeColumnsToContents()
        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.exec_()

    def closeEvent(self, event):
        self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Установка шрифта для всего приложения
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())