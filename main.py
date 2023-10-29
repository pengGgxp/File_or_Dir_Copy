import atexit
import datetime
import json
import os
import shutil
import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QListWidget

from untitled import Ui_MainWindow


def exceptOutConfig(exceptype, value, tb):
    print('错误信息：')
    print('Type:', exceptype)
    print('Value:', value)
    print('Traceback:', tb)


class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))


class ProCessfilemaneger(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(ProCessfilemaneger, self).__init__()
        self.setupUi(self)

        self.MainDirList = []
        self.SonDirList = []
        # 选择模式
        self.selectmod = True

        # 启动被操作文件夹多重选择
        self.selectsonfile_listWidget.setSelectionMode(QListWidget.ExtendedSelection)

        # 将输出流定义到textbrower
        sys.stdout = EmittingStr(textWritten=self.showout)
        sys.stderr = EmittingStr(textWritten=self.showout)

        # 将选择绑定到选择文件夹函数
        self.selectmainfile.clicked.connect(self.SelectMainDir)
        self.selectsonfile.clicked.connect(self.SelectSonDir)

        # 将删除按钮绑定
        self.delButton.clicked.connect(self.delSonDir)

        # 将启动按钮绑定
        self.pushButton.clicked.connect(self.processcopy)

        # 模式选择按钮绑定
        self.dirmod.clicked.connect(self.selectmod_Dir)
        self.filemod.clicked.connect(self.selectmod_File)

        # 程序开启时自动加载配置文件
        if os.path.exists('config'):
            if os.path.exists('config/config.json'):
                self.load_config()

        # 注册退出自动保存各方法
        atexit.register(self.auto_save_config)

    # 显示输出流到logtestbrower
    def showout(self, text):
        cursor = self.log_textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.log_textBrowser.setTextCursor(cursor)
        self.log_textBrowser.ensureCursorVisible()

    # 模式选择
    def selectmod_Dir(self):
        self.selectmod = True
        print('已更改为目录模式')

    def selectmod_File(self):
        self.selectmod = False
        print('已更改为文件模式')

    # 选择文件夹或者文件
    def selectDir_file(self, file_Dir):
        if file_Dir:
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.Directory)
            dirname = dialog.getExistingDirectory()
            return dirname
        else:
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.ExistingFiles)
            dialog.setOption(QFileDialog.ShowDirsOnly, False)  # 允许选择文件
            dialog.setNameFilter("All Files (*)")  # 设置文件过滤器
            dirname, _ = dialog.getOpenFileNames()
            return dirname[0]

    # 选择主文件夹
    def SelectMainDir(self):
        dirname = self.selectDir_file(self.selectmod)
        if len(self.MainDirList) < 10:
            self.MainDirList.insert(0, dirname)
        else:
            self.MainDirList.insert(0, dirname)
            self.MainDirList.pop(-1)
        self.mainfile_showurl.clear()
        while '' in self.MainDirList:
            self.MainDirList.remove('')
        self.mainfile_showurl.addItems(self.MainDirList)

    # 选择被操作文件夹
    def SelectSonDir(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dirname = dialog.getExistingDirectory()
        self.SonDirList.insert(0, dirname)
        self.selectsonfile_listWidget.clear()
        while '' in self.SonDirList:
            self.SonDirList.remove('')
        self.selectsonfile_listWidget.addItems(self.SonDirList)

    # 删除选定Qlistwidgets项
    def delSonDir(self):
        selectitems = self.selectsonfile_listWidget.selectedIndexes()
        for i in selectitems:
            self.SonDirList.pop(i.row())
        self.selectsonfile_listWidget.clear()
        self.selectsonfile_listWidget.addItems(self.SonDirList)

    # 加载配置文件
    def load_config(self):
        with open('config/config.json', 'r', encoding='utf-8') as file:
            config_data = json.load(file)
            self.MainDirList = config_data.get('MainDirList', [])
            self.SonDirList = config_data.get('SonDirList', [])
            self.selectmod = config_data.get('selectmod', bool)
        while '' in self.MainDirList:
            self.MainDirList.remove('')
        while '' in self.SonDirList:
            self.SonDirList.remove('')

        self.mainfile_showurl.addItems(self.MainDirList)
        self.selectsonfile_listWidget.addItems(self.SonDirList)

    # 程序退出时自动保存设置文件
    def auto_save_config(self):
        config_data = {
            'MainDirList': self.MainDirList,
            'SonDirList': self.SonDirList,
            'selectmod': self.selectmod
        }

        if not os.path.exists('config'):
            os.mkdir('config')
        with open('config/config.json', 'w', encoding='utf-8') as file:
            json.dump(config_data, file, sort_keys=True, indent=4, separators=(',', ': '))

        timeer = datetime.datetime.utcnow()
        timeer = timeer.strftime('%Y-%m-%d-%H-%M-%S')
        if not os.path.exists('log'):
            os.mkdir('log')
        with open('log/' + timeer + '.log', 'w', encoding='utf-8') as file:
            ttt = self.log_textBrowser.toPlainText()
            file.write(ttt)

    # 复制方法
    def processcopy(self):
        son = self.selectsonfile_listWidget.selectedItems()
        father = self.mainfile_showurl.currentText()
        sonsfather = self.get_parent_directories(son)

        # 将q值变为字符串
        for i in son:
            son.append(i.text())
            son.pop(0)
        # 保证没有重复项
        set(son)
        list(son)

        if son:
            if father not in son:

                if os.path.isdir(father):
                    for i in son:
                        self.delDir_file(i)
                        print('正在删除' + i)
                    print('删除完毕')
                    for i in sonsfather:
                        folder_name = os.path.basename(father)
                        shutil.copytree(father, i + '/' + folder_name)
                        print('正在复制' + father + '到' + i + '/' + folder_name)
                else:
                    for i in son:
                        file_name = os.path.basename(father)
                        shutil.copy(father, i + '/' + file_name)
                        print('正在复制' + father + '到' + i + '/' + file_name)
                print('复制完毕')
            else:
                print('要复制的主文件夹和被操作文件夹不要重复！')
        else:
            print('请选择一项被操作的文件夹！')

    # 获取父级目录
    def get_parent_directories(self, paths):
        parent_directories = []
        for path in paths:
            parent_dir = os.path.dirname(path.text())
            parent_directories.append(parent_dir)
        return parent_directories

    # 删除路径
    def delDir_file(self, path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


if __name__ == '__main__':
    sys.excepthook = exceptOutConfig
    app = QApplication(sys.argv)

    win = ProCessfilemaneger()
    win.show()
    sys.exit(app.exec_())
