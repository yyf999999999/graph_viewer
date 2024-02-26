import sys
import PySide6.QtCore as Qc
import PySide6.QtWidgets as Qw
import PySide6.QtGui as Qg
import random as r
import numpy as np
import sympy

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# レイアウト設定用変数
sp_exp = Qw.QSizePolicy.Policy.Expanding

class Chart(FigureCanvas):

    def __init__(self):

        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def clear(self):
        self.ax.cla()
        self.ax.grid(True)
        self.fig.canvas.draw()

    def redraw(self,formula):
        xlim=self.ax.get_xlim()
        x=np.linspace(xlim[0],xlim[1],round(xlim[1]-xlim[0])*20)
        x=x[x!=0]
        formula_sympy=sympy.sympify(formula[2:])
        vectorized_formula=np.vectorize(lambda xi:formula_sympy.subs(sympy.symbols("x"),xi))
        y=vectorized_formula(x)
        try:
            y=y.astype(float)
        except (TypeError):
            i=0
            while True:                
                if "I" in str(y[i]):
                    y=np.delete(y,i)
                    x=np.delete(x,i)
                else:
                    i+=1
                if i==len(y):
                    break
        self.ax.plot(x,y,marker='')
        self.ax.grid(True)
        self.fig.canvas.draw()

class CustomNavigationToolbar(NavigationToolbar):

    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)

        # 新しいアクションを作成
        self.action_custom = Qg.QAction('reload', self)
        self.action_custom.triggered.connect(self.custom_action_triggered)

        # ツールバーにアクションを追加
        self.addAction(self.action_custom)

    def custom_action_triggered(self):
        parent_mainwindow = self.get_mainwindow_parent()
        if parent_mainwindow:
            parent_mainwindow.reload()

    def get_mainwindow_parent(self):
        parent = self.parent()
        while parent and not isinstance(parent, MainWindow):
            parent = parent.parent()
        return parent

class MainWindow(Qw.QMainWindow):

    def __init__(self):

        super().__init__()
        self.setWindowTitle('GraphViewer')
        self.setGeometry(100, 50, 640, 300)

        #数式欄
        self.formulas=[]

        # メインレイアウトの設定
        central_widget = Qw.QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = Qw.QHBoxLayout(central_widget)  # 水平レイアウト

        #左側欄の垂直レイアウトを作成します
        left_layout=Qw.QVBoxLayout()
        left_layout.setAlignment(Qc.Qt.AlignmentFlag.AlignTop) # 上寄せ
        main_layout.addLayout(left_layout)  # メインレイアウトに左側欄レイアウトを追加

        #右側欄の垂直レイアウトを作成します
        right_layout=Qw.QVBoxLayout()
        right_layout.setAlignment(Qc.Qt.AlignmentFlag.AlignTop) # 上寄せ
        main_layout.addLayout(right_layout)  # メインレイアウトに左側欄レイアウトを追加

        #数式入力欄の水平レイアウトを作成します
        formula_layout=Qw.QHBoxLayout()
        left_layout.addLayout(formula_layout)  # 左側欄レイアウトに数式入力欄レイアウトを追加

        # ボタン配置の水平レイアウトを作成します。
        button_layout=Qw.QHBoxLayout()
        left_layout.addLayout(button_layout)  # 左側欄レイアウトにボタンレイアウトを追加

        #数式入力欄ラベルの生成
        self.lb_tb_formula=Qw.QLabel("y=")
        self.lb_tb_formula.setFixedSize(15,20)
        self.lb_tb_formula.setSizePolicy(sp_exp,sp_exp)
        formula_layout.addWidget(self.lb_tb_formula)

        #数式入力欄の生成
        self.tb_formula=Qw.QLineEdit()
        self.tb_formula.setMinimumSize(150,20)
        self.tb_formula.setMaximumSize(250,20)
        self.tb_formula.setSizePolicy(sp_exp,sp_exp)
        self.tb_formula.setPlaceholderText('数式を入力')
        formula_layout.addWidget(self.tb_formula)

        # 「追加」ボタンの生成と設定
        self.btn_add = Qw.QPushButton('追加')
        self.btn_add.setMinimumSize(75, 20)
        self.btn_add.setMaximumSize(130, 20)
        self.btn_add.setSizePolicy(sp_exp, sp_exp)
        button_layout.addWidget(self.btn_add)
        self.btn_add.clicked.connect(self.btn_add_clicked)

        # 「クリア」ボタンの生成と設定
        self.btn_clear = Qw.QPushButton('クリア')
        self.btn_clear.setMinimumSize(75, 20)
        self.btn_clear.setMaximumSize(130, 20)
        self.btn_clear.setSizePolicy(sp_exp, sp_exp)
        button_layout.addWidget(self.btn_clear)
        self.btn_clear.clicked.connect(self.btn_clear_clicked)

        #検証ラベルの生成
        self.lb_formula_vm = Qw.QLabel("")
        self.lb_formula_vm.setMinimumSize(165,20)
        self.lb_formula_vm.setMaximumSize(265,20)
        self.lb_formula_vm.setSizePolicy(sp_exp, sp_exp)
        self.lb_formula_vm.setStyleSheet('color: red;')
        self.lb_formula_vm.setVisible(False)
        left_layout.addWidget(self.lb_formula_vm)

        #数式表示欄の生成
        self.lb_formula=[None]*5
        for i in range(5):
            self.lb_formula[i]=Qw.QLabel("")
            self.lb_formula[i].setMinimumSize(165,20)
            self.lb_formula[i].setMaximumSize(265,20)
            self.lb_formula[i].setSizePolicy(sp_exp, sp_exp)
            left_layout.addWidget(self.lb_formula[i])

        # グラフ
        self.plot = Chart()
        #self.plot.redraw()
        right_layout.addWidget(self.plot)
        self.plot.clear()

        # ナビゲーションツールバーの追加
        toolbar=CustomNavigationToolbar(self.plot, self)
        right_layout.addWidget(toolbar)

        # ステータスバー
        self.sb_status = Qw.QStatusBar()
        self.setStatusBar(self.sb_status)
        self.sb_status.setSizeGripEnabled(False)
        self.sb_status.showMessage('プログラムを起動しました。')

    # 「追加」ボタンの押下処理
    def btn_add_clicked(self):
        if self.lb_formula[4].text()=="" and self.tb_formula.text()!="" and self.is_sympifiable(self.tb_formula.text()):
            self.sb_status.showMessage('数式を追加しました。')
            for i in self.lb_formula:
                if i.text()=="":
                    i.setText(f"y={self.tb_formula.text()}")
                    self.tb_formula.setText("")
                    self.plot.redraw(i.text())
                    self.lb_formula_vm.setVisible(False)
                    break
        else:
            self.sb_status.showMessage('数式の追加に失敗しました。')
            if self.lb_formula[4].text()!="":
                self.lb_formula_vm.setText("数式がいっぱいです")
            elif self.tb_formula.text()=="":
                self.lb_formula_vm.setText("数式が入力されていません")
            elif not self.is_sympifiable(self.tb_formula.text()):
                self.lb_formula_vm.setText("数式の入力形式が正しくありません")
            else:
                self.lb_formula_vm.setText("予期しないエラーが発生しました")
            self.lb_formula_vm.setVisible(True)

    # 「クリア」ボタンの押下処理
    def btn_clear_clicked(self):
        self.sb_status.showMessage('数式を削除しました。')
        self.plot.clear()
        for i in self.lb_formula:
            i.setText("")

    #数式が変換可能か調べる処理
    def is_sympifiable(self,formula):
        try:
            float(sympy.sympify(formula).subs(sympy.symbols("x"),1))
            return True
        except (sympy.SympifyError,TypeError):
            return False

    #再読み込みされたとき
    def reload(self):
        self.sb_status.showMessage('数式を再読み込みしました。')
        plot_size=(self.plot.ax.get_xlim(),self.plot.ax.get_ylim())
        self.plot.ax.cla()
        self.plot.ax.set_xlim(plot_size[0])
        self.plot.ax.set_ylim(plot_size[1])
        for i in self.lb_formula:
            if i.text()!="":
                self.plot.redraw(i.text())

# 本体
if __name__ == '__main__':
    app = Qw.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())