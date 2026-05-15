import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QFileDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class StockNoteSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("股票交易筆記系統")
        self.resize(1100, 700)
        
        # 初始模擬資料
        self.stock_data = [
            {"code": "2330", "name": "台積電", "price": 900, "shares": 1000, "cost": 850},
            {"code": "2454", "name": "聯發科", "price": 1200, "shares": 500, "cost": 1250},
            {"code": "2317", "name": "鴻海", "price": 180, "shares": 2000, "cost": 150}
        ]
        
        self.init_ui()
        self.update_dashboard()

    def init_ui(self):
        # 主佈局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # ================= 左側：輸入與列表區 =================
        left_layout = QVBoxLayout()
        
        # 1. 新增股票表單
        form_group = QGroupBox("新增股票筆記")
        form_layout = QHBoxLayout()
        
        self.input_code = QLineEdit()
        self.input_code.setPlaceholderText("代號 (如: 2330)")
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("名稱 (如: 台積電)")
        self.input_price = QLineEdit()
        self.input_price.setPlaceholderText("現價")
        self.input_shares = QLineEdit()
        self.input_shares.setPlaceholderText("股數")
        self.input_cost = QLineEdit()
        self.input_cost.setPlaceholderText("成本價")
        
        btn_add = QPushButton("新增/更新")
        btn_add.clicked.connect(self.add_stock)
        
        form_layout.addWidget(self.input_code)
        form_layout.addWidget(self.input_name)
        form_layout.addWidget(self.input_price)
        form_layout.addWidget(self.input_shares)
        form_layout.addWidget(self.input_cost)
        form_layout.addWidget(btn_add)
        form_group.setLayout(form_layout)
        left_layout.addWidget(form_group)

        # 2. 股票資料表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["股票代號", "股票名稱", "目前現價", "持有股數", "平均成本", "目前市值"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        left_layout.addWidget(self.table)
        
        # 3. 輸出按鈕
        btn_export = QPushButton("輸出 JSON 檔案")
        btn_export.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; height: 35px;")
        btn_export.clicked.connect(self.export_to_json)
        left_layout.addWidget(btn_export)

        # ================= 右側：儀表板區 =================
        self.right_widget = QWidget()
        right_layout = QVBoxLayout(self.right_widget)
        self.right_widget.setFixedWidth(400)
        
        dash_group = QGroupBox("數據儀表板")
        dash_layout = QVBoxLayout()
        
        # 統計數據標籤
        self.lbl_total_value = QLabel("總市值: $0")
        self.lbl_total_profit = QLabel("總損益: $0")
        for lbl in [self.lbl_total_value, self.lbl_total_profit]:
            lbl.setStyleSheet("font-size: 16px; font-weight: bold; margin: 5px;")
        
        dash_layout.addWidget(self.lbl_total_value)
        dash_layout.addWidget(self.lbl_total_profit)
        
        # Matplotlib 圓餅圖整合
        self.figure = Figure(figsize=(4, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        dash_layout.addWidget(self.canvas)
        
        dash_group.setLayout(dash_layout)
        right_layout.addWidget(dash_group)

        # 組合左右兩側
        main_layout.addLayout(left_layout, stretch=7)
        main_layout.addWidget(self.right_widget, stretch=3)

    # ================= 邏輯處理功能 =================
    
    def update_dashboard(self):
        """更新表格、計算儀表板數據與重新繪製圓餅圖"""
        self.table.setRowCount(0)
        total_market_value = 0
        total_cost_value = 0
        
        labels = []
        sizes = []

        for i, stock in enumerate(self.stock_data):
            # 計算數據
            market_value = stock["price"] * stock["shares"]
            cost_value = stock["cost"] * stock["shares"]
            total_market_value += market_value
            total_cost_value += cost_value
            
            # 用於圓餅圖
            labels.append(f"{stock['name']}({stock['code']})")
            sizes.append(market_value)

            # 填入表格
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(stock["code"]))
            self.table.setItem(i, 1, QTableWidgetItem(stock["name"]))
            self.table.setItem(i, 2, QTableWidgetItem(str(stock["price"])))
            self.table.setItem(i, 3, QTableWidgetItem(str(stock["shares"])))
            self.table.setItem(i, 4, QTableWidgetItem(str(stock["cost"])))
            self.table.setItem(i, 5, QTableWidgetItem(f"${market_value:,}"))

        # 更新儀表板文字
        total_profit = total_market_value - total_cost_value
        self.lbl_total_value.setText(f"總市值: ${total_market_value:,}")
        
        if total_profit >= 0:
            self.lbl_total_profit.setText(f"總損益: +${total_profit:,}")
            self.lbl_total_profit.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        else:
            self.lbl_total_profit.setText(f"總損益: -${abs(total_profit):,}")
            self.lbl_total_profit.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")

        # 重新繪製 Matplotlib 圓餅圖
        self.figure.clear()
        if sizes:
            ax = self.figure.add_subplot(111)
            # 支援中文顯示的設定（若無對應字體可能顯示為方塊，可替換為系統內建中文字體）
            import matplotlib as mpl
            mpl.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial']
            mpl.rcParams['axes.unicode_minus'] = False
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
            ax.set_title("資產配置比例")
        self.canvas.draw()

    def add_stock(self):
        """讀取輸入欄位並新增至資料集中"""
        code = self.input_code.text().strip()
        name = self.input_name.text().strip()
        
        try:
            price = float(self.input_price.text())
            shares = int(self.input_shares.text())
            cost = float(self.input_cost.text())
        except ValueError:
            QMessageBox.warning(self, "輸入錯誤", "請確保現價、股數與成本輸入的是正確數字！")
            return

        if not code or not name:
            QMessageBox.warning(self, "輸入錯誤", "股票代號與名稱不能為空！")
            return

        # 檢查是否已存在，存在就更新，不存在就新增
        existing_stock = next((s for s in self.stock_data if s["code"] == code), None)
        if existing_stock:
            existing_stock.update({"name": name, "price": price, "shares": shares, "cost": cost})
        else:
            self.stock_data.append({"code": code, "name": name, "price": price, "shares": shares, "cost": cost})

        # 清空輸入欄位
        self.input_code.clear()
        self.input_name.clear()
        self.input_price.clear()
        self.input_shares.clear()
        self.input_cost.clear()

        self.update_dashboard()

    def export_to_json(self):
        """將當前的股票資料數據輸出為 JSON 檔案"""
        if not self.stock_data:
            QMessageBox.information(self, "提示", "目前沒有任何股票資料可供輸出。")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "儲存 JSON 檔案", "stock_notes.json", "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.stock_data, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "成功", f"檔案已成功輸出至：\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"輸出檔案時發生錯誤：\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockNoteSystem()
    window.show()
    sys.exit(app.exec())
