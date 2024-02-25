import application as ap

app=ap.Qw.QApplication(ap.sys.argv)
main_window=ap.MainWindow()
main_window.show()
ap.sys.exit(app.exec())