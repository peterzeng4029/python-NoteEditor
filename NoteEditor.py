#!/usr/bin/env python
# coding=utf-8

# 该实例使用python 2.7编译

import os
import Tkinter as tk
import ttk as ttk
from tkFileDialog import *
import tkMessageBox
from Tkconstants import *
from editor_config import Themes_Config, Font_Config


class NoteEditor(tk.Tk):
    mContentView = None
    mFileName = None
    bModifyState = False
    mLastMoveArgs = None
    mTextContent = ""

    # 查找功能
    mSearchDlg = None
    mInputEntry = None
    mSearchList = []
    mSearchCount = 0
    mSearchString = None

    # 替换功能
    mReplaceEntry = None
    mReplaceString = None
    mReplaceCount = 0
    mReplacePos = 1.0

    def __init__(self):
        tk.Tk.__init__(self)  # python 2.7

        self.initLayout()
        self.initMenuBar()
        self.initShortCutTools()
        self.initTextEditor()
        self.initPopupMenu()
        self.initQuickKey()

        self.initOtherComman()
        self.updateLineView()

    def initLayout(self):
        self.setMainTitle()
        self.geometry("800x600")

    def initTextEditor(self):
        # 左边行号
        self.mLineView = tk.Text(self, width=4, takefocus=0, border=0, background='#cccdd2', state='disabled')
        self.mLineView.pack(side='left', fill='y')

        # 文本内容
        self.mContentView = tk.Text(self, wrap='word', undo=True)
        self.mContentView.pack(expand='yes', fill='both')
        self.mContentView['yscrollcommand'] = self.onContentScrollY

        # 滚动条
        self.mScrollBar = tk.Scrollbar(self.mContentView)
        self.mScrollBar.pack(side='right', fill='y')
        self.mScrollBar['command'] = self.onScrollBarCommand

    # 设置顶部菜单
    def initMenuBar(self):
        self.mMenuBar = tk.Menu(self)
        # 文件菜单
        fileMenu = tk.Menu(self.mMenuBar, tearoff=0)
        self.mMenuBar.add_cascade(label='文件', menu=fileMenu)
        fileMenu.add_command(label="新建", accelerator="Ctrl+n", command=self.doNewFile)
        fileMenu.add_command(label="打开", accelerator="Ctrl+o", command=self.doOpenFile)
        fileMenu.add_command(label="保存", accelerator="Ctrl+s", command=self.doSaveFile)
        fileMenu.add_command(label="另存为", command=self.doSaveOtherFile)  # accelerator="Shift+Ctrl+S"
        fileMenu.add_separator()
        fileMenu.add_command(label="关闭", accelerator="Ctrl+w", command=self.doExit)

        # 编辑菜单
        editMenu = tk.Menu(self.mMenuBar, tearoff=0)
        self.mMenuBar.add_cascade(label='编辑', menu=editMenu)
        editMenu.add_command(label="撤销", accelerator="Ctrl+z", command=lambda: self.doEditMenu("undo"))
        editMenu.add_command(label="重做", accelerator="Ctrl+y", command=lambda: self.doEditMenu("redo"))
        editMenu.add_separator()
        editMenu.add_command(label="剪切", accelerator="Ctrl+x", command=lambda: self.doEditMenu("cut"))
        editMenu.add_command(label="复制", accelerator="Ctrl+c", command=lambda: self.doEditMenu("copy"))
        editMenu.add_command(label="粘贴", accelerator="Ctrl+v", command=lambda: self.doEditMenu("paste"))
        editMenu.add_separator()
        editMenu.add_command(label="查找", accelerator="Ctrl+f", command=lambda: self.doOpenFindDlg("find"))
        editMenu.add_command(label="替换", accelerator="Ctrl+r", command=lambda: self.doOpenFindDlg("replace"))
        editMenu.add_separator()
        editMenu.add_command(label="全选", accelerator="Ctrl+a", command=self.doSelectAll)

        # 显示
        viewMenu = tk.Menu(self.mMenuBar, tearoff=0)
        self.mMenuBar.add_cascade(label='显示', menu=viewMenu)
        self.showLineNum = tk.IntVar()
        self.showLineNum.set(1)
        viewMenu.add_checkbutton(label='行号', variable=self.showLineNum, command=self.updateLineView)

        self.fontMenu = tk.Menu(self.mMenuBar, tearoff=0)
        viewMenu.add_cascade(label='字体', menu=self.fontMenu)
        self.fontChoice = tk.StringVar()
        for item in Font_Config:
            self.fontMenu.add_radiobutton(label=item['name'], variable=self.fontChoice, command=self.updateFont)

        self.themesMenu = tk.Menu(self.mMenuBar, tearoff=0)
        viewMenu.add_cascade(label='模式', menu=self.themesMenu)
        self.themesChoice = tk.StringVar()
        for item in Themes_Config:
            self.themesMenu.add_radiobutton(label=item['name'], variable=self.themesChoice, command=self.updateThemes)

        self.myMenu = tk.Menu(self.mMenuBar, tearoff=0)
        self.mMenuBar.add_cascade(label='用户', menu=self.myMenu)
        self.myMenu.add_command(label='登录', command=self.onLoginMenu)

        self.config(menu=self.mMenuBar)

    # 设置右键弹出菜单
    def initPopupMenu(self):
        if self.mContentView:
            self.popMenu = tk.Menu(self.mContentView, tearoff=0)
            self.popMenu.add_command(label="剪切", command=lambda: self.doEditMenu("cut"))
            self.popMenu.add_command(label="复制", command=lambda: self.doEditMenu("copy"))
            self.popMenu.add_command(label="粘贴", command=lambda: self.doEditMenu("paste"))
            self.popMenu.add_command(label="撤销", command=lambda: self.doEditMenu("undo"))
            self.popMenu.add_command(label="重做", command=lambda: self.doEditMenu("redo"))
            self.mContentView.bind("<3>", lambda e: self.handPopupMenu(e))
            self.mContentView.bind("<Control-Button-1>", lambda e: self.handPopupMenu(e))

    def handPopupMenu(self, event):
        if self.popMenu:
            self.popMenu.tk_popup(event.x_root, event.y_root)

    # 设置快捷键
    def initQuickKey(self):
        quick_config = [
            {'key': ["<Control-N>", "<Control-n>"], 'func': lambda e: self.doNewFile()},
            {'key': ["<Control-O>", "<Control-o>"], 'func': lambda e: self.doOpenFile()},
            {'key': ["<Control-Shift-S>", "<Control-Shift-s>"], 'func': lambda e: self.doSaveOtherFile()},
            {'key': ["<Control-S>", "<Control-s>"], 'func': lambda e: self.doSaveFile()},
            {'key': ["<Control-F>", "<Control-f>"], 'func': lambda e: self.doOpenFindDlg("find")},
            {'key': ["<Control-R>", "<Control-r>"], 'func': lambda e: self.doOpenFindDlg("replace")},
            {'key': ["<Control-A>", "<Control-a>"], 'func': lambda e: self.doSelectAll()},
            {'key': ["<Control-Z>", "<Control-z>"], 'func': lambda e: self.doEditMenu("undo")},
            {'key': ["<Control-Y>", "<Control-y>"], 'func': lambda e: self.doEditMenu("redo")},
            {'key': ["<Control-W>", "<Control-w>"], 'func': lambda e: self.doExit()},
        ]
        if self.mContentView:
            for item in quick_config:
                keyList = item['key']
                func = item["func"]
                for k in keyList:
                    if k and func:
                        self.mContentView.bind(k, func)

    # 快捷工具栏
    def initShortCutTools(self):
        short_cut_config = [
            {'image': 'new_file', 'func': lambda: self.doNewFile()},
            {'image': 'open_file', 'func': lambda: self.doOpenFile()},
            {'image': 'save', 'func': lambda: self.doSaveFile()},
            {'image': 'cut', 'func': lambda: self.doEditMenu("cut")},
            {'image': 'copy', 'func': lambda: self.doEditMenu("copy")},
            {'image': 'paste', 'func': lambda: self.doEditMenu("paste")},
            {'image': 'undo', 'func': lambda: self.doEditMenu("undo")},
            {'image': 'redo', 'func': lambda: self.doEditMenu("redo")},
            {'image': 'find_text', 'func': lambda: self.doOpenFindDlg("find")},
        ]
        self.imaglist = []  # 注意要把PhotoImage实例添加到数组，否则显示空白
        frame = tk.Frame(self, height=30)
        frame.pack(fill='x')

        for item in short_cut_config:
            image = item['image']
            func = item['func']
            if image and func:
                photo = tk.PhotoImage(file=('img/%s.gif' % item["image"]))
                btn = ttk.Button(frame, image=photo, command=func)
                btn.pack(side='left')
                self.imaglist.append(photo)

    # 滚动条滑动响应
    def onScrollBarCommand(self, *args):
        # print("onScrollBarCommand args22=", args)
        self.mContentView.yview(*args)
        self.mLineView.yview(*args)

    # 编辑框上下滑动的处理
    def onContentScrollY(self, *args):
        # print("onContentScroll args=", args)
        # 滑动到顶部 ('0.0', '0.07815181518151815'))
        # 滑动到底部 ('0.9218481848184819', '1.0'))

        # 设置滚动条
        if self.mScrollBar:
            self.mScrollBar.set(*args)

        # 设置行号的滑动
        scType = 0
        if self.mLastMoveArgs is None:
            self.mLastMoveArgs = args
        else:
            if args[0] > self.mLastMoveArgs[0]:
                scType = 1  # 下滑
            elif args[0] < self.mLastMoveArgs[0]:
                scType = 2  # 上滑
            else:
                scType = 0
        if self.mLineView and scType > 0:
            self.mLastMoveArgs = args
            if scType == 1:
                # 向下滑动
                self.mLineView.yview_moveto(args[1])
            else:
                self.mLineView.yview_moveto(args[0])

    # 处理其它按键命令
    def initOtherComman(self):
        self.bind('<Any-KeyPress>', lambda e: self.onModify())

    # 是否编辑了文本
    def onModify(self):
        if self.mContentView:
            preLen = self.mTextContent and len(self.mTextContent) or 0
            text = self.mContentView.get(1.0, 'end')
            curLen = len(text)
            # 判断文本长度是否相等，不相等则认为是修改
            # print("preLen=%s, curLen=%s" % (preLen, curLen))
            if curLen != preLen:
                self.mTextContent = text
                if not self.getModifyState():
                    self.setModifyState(True)
                    self.setMainTitle()
                self.updateLineView()

    # 设置修改状态
    def setModifyState(self, state):
        self.bModifyState = state

    def getModifyState(self):
        return self.bModifyState or False

    def updateFont(self):
        config = None
        selFont = self.fontChoice.get()
        for item in Font_Config:
            name = item['name']
            if name:
                if selFont == name.decode('utf-8'):
                    config = item
                    break
        # print("config =", config)
        if config:
            fontSize = config['fontSize']
            if self.mContentView and fontSize:
                # 获取原文字配置
                fc = self.mContentView.cget("font")
                # print("fc=", fc)
                if fc:
                    splist = fc.split(" ")
                    if splist and len(splist) > 0:
                        self.mContentView.config(font=(splist[0], fontSize, ''))

    def updateThemes(self):
        selected_theme = self.themesChoice.get()
        config = None
        for item in Themes_Config:
            name = item['name']
            if name:
                if selected_theme == name.decode('utf-8'):  # 中文字需要解析
                    config = item
                    break
        # print("config =", config)
        if config:
            fgColor = config['fgcolor']
            bgColor = config['bgcolor']
            if self.mContentView and fgColor and bgColor:
                self.mContentView.config(bg=bgColor, fg=fgColor)

    # 更新行号
    def updateLineView(self):
        if self.mContentView and self.mLineView:
            if self.showLineNum.get():
                index = self.mContentView.index('end')
                # print("initLineView: index=", index)
                if index and len(index) > 0:
                    row, col = index.split('.')
                    if row and len(row) > 0:
                        lineContent = ""
                        for i in range(1, int(row)):  # range[1, n)左闭右开
                            lineContent += str(i) + '\n'
                        self.mLineView.config(state='normal')
                        self.mLineView.delete('1.0', 'end')
                        self.mLineView.insert('1.0', lineContent)
                        self.mLineView.config(state='disabled')
            else:
                self.mLineView.config(state='normal')
                self.mLineView.delete('1.0', 'end')
                self.mLineView.config(state='disabled')

    def doEditMenu(self, editType):
        # print("doEditMenu: editType=%s" % editType)
        if editType == "undo":
            if self.mContentView:
                self.mContentView.edit_undo()
            # 也可以使用消息的方法
            # self.mContentView.event_generate("<<Undo>>")
        elif editType == "redo":
            if self.mContentView:
                self.mContentView.edit_redo()
        elif editType == "cut":
            self.doCut()
        elif editType == "copy":
            self.doCopy()
        elif editType == "paste":
            self.doPaste()

    # 处理剪切
    def doCut(self):
        if self.mContentView:
            # 起始和结束光标分别在选择数组[0],[1]
            selList = self.mContentView.tag_ranges('sel')
            if selList and len(selList) == 2:
                startItem = selList[0]
                endItem = selList[1]
                if startItem and endItem:
                    strSel = self.mContentView.get(startItem, endItem)
                    print("doCut: strSel=", strSel)
                    if strSel and len(strSel) > 0:
                        # 设置剪贴板
                        self.clipboard_clear()
                        self.clipboard_append(strSel)
                        # 删除选择的内容
                        self.mContentView.delete(startItem, endItem)
                        # 更新修改状态
                        self.onModify()

    # 处理复制
    def doCopy(self):
        if self.mContentView:
            selList = self.mContentView.tag_ranges('sel')
            if selList and len(selList) == 2:
                # 起始和结束光标分别在选择数组[0],[1]
                startItem = selList[0]
                endItem = selList[1]
                if startItem and endItem:
                    strSel = self.mContentView.get(startItem, endItem)
                    print("doCopy: strSel=", strSel)
                    if strSel and len(strSel) > 0:
                        # 设置剪贴板
                        self.clipboard_clear()
                        self.clipboard_append(strSel)

    # 处理粘贴
    def doPaste(self):
        # 获取粘贴板的内容
        if self.mContentView:
            clipData = self.clipboard_get()
            # 获取光标位置
            cursorPos = self.mContentView.index('insert')
            if cursorPos and clipData:
                # 写入文本
                self.mContentView.insert(cursorPos, clipData)
                self.onModify()

    # 打开查找或替换窗口
    def doOpenFindDlg(self, showType):
        # 初始化
        self.mSearchList = []
        self.mSearchString = None
        self.mSearchCount = 0
        self.mReplacePos = 1.0
        self.mReplaceCount = 0
        self.mReplaceString = None

        # 创建窗口
        self.mSearchDlg = tk.Toplevel(self)
        self.mSearchDlg.title("查找文本")
        # self.mSearchDlg.geometry('450x200')  # 设置大小
        self.mSearchDlg.minsize(420, 120)  # 设置最小宽高
        self.mSearchDlg.resizable(False, False)  # 不可调节大小
        self.mSearchDlg.transient(self)  # 置于顶总
        self.mSearchDlg.config()

        print("doOpenFindDlg() start")
        # 查找容器
        inputFrame = tk.Frame(self.mSearchDlg)
        inputFrame.pack(side=TOP, anchor=W, ipady=2, expand=False, padx=10, pady=5, fill=NONE)

        # 显示标签
        label = tk.Label(inputFrame, text="查找文本")
        label.pack(side=LEFT, padx=10, pady=5)
        # 显示查找输入框
        self.mInputEntry = tk.Entry(inputFrame, width=30)
        self.mInputEntry.pack(side=LEFT, padx=10, pady=5)
        self.mInputEntry.focus_get()

        # 替换容器
        if showType == "replace":
            replaceFrame = tk.Frame(self.mSearchDlg)
            replaceFrame.pack(side=TOP, anchor=W, ipady=2, expand=False, padx=10, pady=2, fill=NONE)

            rep = tk.Label(replaceFrame, text="替换文本")
            rep.pack(side=tk.LEFT, padx=10, pady=2)

            self.mReplaceEntry = tk.Entry(replaceFrame, width=30)
            self.mReplaceEntry.pack(side=LEFT, padx=10, pady=2)
            self.mReplaceEntry.focus_get()

        # 查找按钮容器
        frame2 = tk.Frame(self.mSearchDlg)  # bg='#ff3399', width=360
        frame2.pack(side=TOP, anchor=CENTER, ipady=2, expand=False, padx=5, pady=2)

        prevBtn = ttk.Button(frame2, text="上一个", command=self.doFindPrev)
        prevBtn.pack(side=LEFT, anchor=N, padx=10)

        nextBtn = ttk.Button(frame2, text="下一个", command=self.doFindNext)
        nextBtn.pack(side=tk.LEFT, anchor=N, padx=10)

        findBtn = ttk.Button(frame2, text="查找", command=self.doFindResult)
        findBtn.pack(side=LEFT, anchor=N, padx=10)

        if showType == "replace":
            btnReplaceFrame = tk.Frame(self.mSearchDlg)
            btnReplaceFrame.pack(side=TOP, anchor=CENTER, ipady=2, expand=True, padx=5, pady=5)

            replaceMenu = ttk.Button(btnReplaceFrame, text="替换", command=self.doReplaceSingle)
            replaceMenu.pack(side=LEFT, anchor=N, padx=30)

            replaceAll = ttk.Button(btnReplaceFrame, text="替换所有", command=self.doReplaceAll)
            replaceAll.pack(side=RIGHT, anchor=N, padx=30)

    # 查找结果
    def doFindResult(self):
        if self.mInputEntry:
            inputText = self.mInputEntry.get()
            # 是否已查找过
            if self.mSearchString is None or self.mSearchString != inputText:
                self.doFindTextResult()
            else:
                self.doFindNext()

    # 重新查找
    def doFindTextResult(self):
        if (self.mSearchDlg is None) or (self.mInputEntry is None):
            return
        inputText = self.mInputEntry.get()
        if inputText:
            startPos = '1.0'
            findCnt = 0
            self.mSearchString = inputText
            self.mSearchCount = 0

            while True:
                startPos = self.mContentView.search(inputText, startPos, nocase=False, stopindex="end")
                if not startPos:
                    break
                # 查找格式:"index + Nc", 如果位置是2.6和字符长度是9, 则最后的位置是2.6+9c
                endPos = "%s+%sc" % (startPos, len(inputText))
                # 添加查找位置到列表
                self.mSearchList.append(startPos)
                # 设置匹配项, 用于后续高亮
                self.mContentView.tag_add('match', startPos, endPos)
                findCnt += 1
                startPos = endPos
            if findCnt == 0:
                self.mSearchDlg.title("没有查找到匹配项")
            else:
                # 高亮匹配项
                self.mContentView.tag_config('match', foreground='red', background='yellow')
                # 光标定位
                self.mContentView.mark_set('insert', self.mSearchList[0])
                # 聚焦到文本框
                self.mContentView.focus_set()
                # 显示标题
                self.mSearchDlg.title("查找到%s个匹配项" % findCnt)

    # 查找前一个
    def doFindPrev(self):
        if self.mSearchList and len(self.mSearchList) > 0:
            if self.mSearchCount > 0:
                self.mSearchCount -= 1
            else:
                self.mSearchCount = len(self.mSearchList) - 1

            if self.mContentView:
                # 光标置于查找的位置
                self.mContentView.mark_set('insert', self.mSearchList[self.mSearchCount])
                self.mContentView.focus_set()
        else:
            self.doFindTextResult()

    # 查找下一个
    def doFindNext(self):
        if self.mSearchList and len(self.mSearchList) > 0:
            self.mSearchCount += 1
            if self.mSearchCount >= len(self.mSearchList):
                self.mSearchCount = 0

            if self.mContentView:
                # 光标置于查找的位置
                self.mContentView.mark_set('insert', self.mSearchList[self.mSearchCount])
                self.mContentView.focus_set()
        else:
            self.doFindTextResult()

    # 替换一个
    def doReplaceSingle(self):
        ret = self.replaceOne()
        if not ret:
            tip = ""
            if self.mReplaceCount == 0:
                tip = "没有可替换的内容"
            else:
                tip = "已完成全部的替换"
            self.mReplacePos = 1.0
            self.mReplaceCount = 0
            tkMessageBox.askokcancel("提示", tip)

    # 替换所有
    def doReplaceAll(self):
        while True:
            ret = self.replaceOne()
            if not ret:
                break
        tip = ""
        if self.mReplaceCount == 0:
            tip = "没有替换内容"
        else:
            tip = "已替换%d处文本" % self.mReplaceCount
        self.mReplacePos = 1.0
        self.mReplaceCount = 0
        tkMessageBox.askokcancel("提示", tip)

    # 处理替换
    def replaceOne(self):
        if self.mInputEntry is None or self.mReplaceEntry is None:
            return False

        findText = self.mInputEntry.get()
        replaceText = self.mReplaceEntry.get()

        # 重新搜索替换
        if (replaceText != self.mReplaceString) or (findText != self.mSearchString):
            self.mReplaceCount = 0
            self.mReplacePos = 1.0

        if findText and len(findText) > 0:
            startPos = self.mReplacePos
            self.mSearchString = findText
            self.mReplaceString = replaceText

            startPos = self.mContentView.search(findText, startPos, nocase=False, stopindex="end")
            if startPos:
                endPos = "%s+%sc" % (startPos, len(findText))
                # 删除原内容
                self.mContentView.delete(startPos, endPos)
                # 添加替换内容
                if replaceText and len(replaceText):
                    self.mContentView.insert(startPos, replaceText)
                # 设置下次替换的起始位置
                self.mReplacePos = "%s+%sc" % (startPos, len(replaceText))
                # 统计替换的次数
                self.mReplaceCount += 1

                # 更新修改状态
                self.onModify()
                return True
        return False

    # 全选
    def doSelectAll(self):
        if self.mContentView:
            self.mContentView.tag_add("sel", 1.0, 'end')

    # 新建文件
    def doNewFile(self):
        print("doNewFile")
        if self.mContentView:
            self.mContentView.delete(1.0, 'end')
        self.mFileName = None
        self.mTextContent = ""
        self.setMainTitle()
        self.updateLineView()

    def setFileName(self, path):
        if path:
            self.mFileName = path

    # 设置标题
    def setMainTitle(self):
        strMod = self.getModifyState() and " * " or ""
        if self.mFileName and len(self.mFileName) > 0:
            fileName = os.path.basename(self.mFileName)
            self.title("%s - 记事本 %s" % (fileName, strMod))
        else:
            self.title("记事本 %s" % strMod)

    # 打开文件
    def doOpenFile(self):
        print("doOpenFile")
        openPath = askopenfilename(filetypes=[("All Files", "*.*"), ("文本文档", "*.txt")])
        if openPath:
            out = self.openTextFile(openPath)
            if out is not None:
                # 设置编辑框
                self.mTextContent = out

                if self.mContentView:
                    self.mContentView.delete(1.0, 'end')
                    self.mContentView.insert(1.0, out)

                # 保存路径
                self.setFileName(openPath)
                self.setModifyState(False)
                # 设置标题
                self.setMainTitle()
                self.updateLineView()

    # 保存文件
    def doSaveFile(self):
        print ("doSaveFile")
        if self.mFileName:
            self.writeTextFile(self.mFileName)
            self.setModifyState(False)
            self.setMainTitle()
        else:
            savePath = asksaveasfilename(filetypes=[("All Files", "*.*"), ("文本文档", "*.txt")])
            if savePath:
                if self.writeTextFile(savePath):
                    self.setFileName(savePath)
                    self.setModifyState(False)
                    self.setMainTitle()

    # 另存为
    def doSaveOtherFile(self):
        print ("doSaveOtherFile")
        savePath = asksaveasfilename(filetypes=[("All Files", "*.*"), ("文本文档", "*.txt")])
        if savePath:
            print("doSaveOtherFile(): OK savePath=", savePath)
            if self.writeTextFile(self.mFileName):
                self.setModifyState(False)
                self.setFileName(savePath)
                self.setMainTitle()

    # 读取文件
    def openTextFile(self, path):
        print("openTextFile: path=", path)
        out = ""
        fd = None
        try:
            fd = open(path, "r")
            lines = fd.readlines()
            for item in lines:
                out += item
        except IOError:
            print("保存失败")
            return None
        finally:
            if fd:
                fd.close()
        return out

    # 写入文件
    def writeTextFile(self, path):
        print("writeTextFile: path=", path)
        if self.mContentView:
            strText = self.mContentView.get(1.0, 'end')
            if strText:
                fd = None
                try:
                    fd = open(path, "w")
                    fd.write(strText)
                    print("writeTextFile ok")
                    return True
                except IOError:
                    print("保存失败")
                finally:
                    if fd:
                        fd.close()
        return False

    def onLoginMenu(self):
        dialog = tk.Toplevel(self)
        dialog.title("登录")
        dialog.geometry('400x300')

        canvas = tk.Canvas(dialog, width=450, height=150, bg="yellow")
        self.imageFile = tk.PhotoImage(file='img/head.gif')
        createImage = canvas.create_image(200, 0, anchor='n', image=self.imageFile)
        canvas.pack(side='top')
        tk.Label(dialog, text="欢迎使用记事本!", font=('Arial', 14)).pack()

        tk.Label(dialog, text='名称：', font=('Arial', 14)).place(x=30, y=180)
        tk.Label(dialog, text='密码：', font=('Arial', 14)).place(x=30, y=220)

        self._username = tk.StringVar()
        self._username.set("example@test.com")
        self._entry_user_name = tk.Entry(dialog, textvariable=self._username, font=('Arial', 14), width=30)
        self._entry_user_name.place(x=80, y=180)

        self._password = tk.StringVar()
        self._entry_pwd = tk.Entry(dialog, textvariable=self._password, show='*', font=('Arial', 14), width=30)
        self._entry_pwd.place(x=80, y=220)

        loginBtn = ttk.Button(dialog, text='登录', command=lambda: self.doUserLogin("login"))
        loginBtn.place(x=90, y=260)
        registerBtn = ttk.Button(dialog, text='注册', command=lambda: self.doUserLogin("register"))
        registerBtn.place(x=230, y=260)

    def onAboutMenu(self):
        print("onAboutMenu")

    def doUserLogin(self, useType):
        print("doUserLogin")
        userName = self._username.get()
        pwd = self._password.get()
        print("userName=", userName)
        print("pwd=", pwd)

        if userName and pwd and len(userName) > 0 and len(pwd) > 0:
            if tkMessageBox.askokcancel("登录/注册", "确定要登录吗"):
                # 处理登录服务器，略
                pass
        else:
            tkMessageBox.askokcancel("登录/注册", "请输出正确的用户名和密码")

    # 关闭文件
    def doExit(self):
        if tkMessageBox.askokcancel("关闭", "确定关闭文件吗？"):
            self.destroy()


if __name__ == '__main__':
    app = NoteEditor()
    app.mainloop()
