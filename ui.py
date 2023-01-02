import sys
if sys.platform == "win32" or sys.platform == "cygwin":
    import win32clipboard
    from io import BytesIO
import index
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton, QLineEdit, QLabel, QCheckBox, QGridLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PIL import Image
from functools import partial

X = 600
Y = 400

searchMode = "Search by String"
searchResults = []
selectedTags = []

# Improvement: Implement Tag Type

def win_send_to_clipboard(clip_type, data):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(clip_type, data)
    win32clipboard.CloseClipboard()


def copyToClip(name, direc = "./Repo-Chan/", resize = False):
    if resize:
        path = direc + name
        image = Image.open(path).resize((100,100))
        # Improvement: implement with thumbnail
        path = direc + "Re-" + name
        image.save(path)
    else:
        path = direc + name

    if sys.platform == "linux" or sys.platform == "darwin":
        os.system(f"xclip -selection clipboard -t image/png -i {path}")
    elif sys.platform == "win32" or sys.platform == "cygwin":
        image = Image.open(path)

        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()

        win_send_to_clipboard(win32clipboard.CF_DIB, data)
        

class PictureWidget(QLabel):
    def __init__(self, name):
        super(PictureWidget, self).__init__()
        self.name = name

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.MouseButton.RightButton:
            copyToClip(self.name)
        elif QMouseEvent.button() == Qt.MouseButton.MiddleButton:
            copyToClip(self.name, resize=True)

class TagSelectLayout(QGridLayout):
    def __init__(self, tagArray = selectedTags):
        super(TagSelectLayout, self).__init__() 
        self.tagArray = tagArray
        self.update()

    def update(self):
        clearLayout(self)
        count = 0
        for i in list(index.tags.keys()):
            checkbox = QCheckBox(i)
            checkbox.stateChanged.connect(partial(self.change, checkbox, self.tagArray))
            self.addWidget(checkbox, int(count/3), count % 3, alignment=Qt.AlignmentFlag.AlignCenter)
            count += 1        

    def change(self, box, array):
        if box.isChecked():
            array.append(box.text())
        else:
            array.remove(box.text())

class TagsWidget(QWidget):
    def __init__(self, image, checkbox = False):
        super(TagsWidget, self).__init__()
        self.image = image
        self.tags = index.images[image]
        self.layout = QGridLayout()
        count = 0
        for i in self.tags[1:]:
            if checkbox and i != "No Tags":
                checkbox = QCheckBox(i)
                checkbox.setChecked(True)
                checkbox.stateChanged.connect(partial(self.change, checkbox))
                self.layout.addWidget(checkbox, int(count/3), count % 3, alignment=Qt.AlignmentFlag.AlignCenter)
            else:
                self.layout.addWidget(QLabel(i), int(count/3), count % 3, alignment=Qt.AlignmentFlag.AlignCenter)
            count += 1
        self.setLayout(self.layout)

    def change(self, box):
        if not box.isChecked():
            index.delImgTag(self.image, box.text())
        else:
            index.addImgTag(self.image, box.text())

def clearLayout(layout):
    i = 0
    while i < layout.count():
        item = layout.itemAt(i).widget()
        item.deleteLater()
        # Check for memory leak? (Probably no leak here?)
        i += 1

def updateSearchMode():
    global searchMode
    searchMode = searchBox.currentText()

def search():
    global searchResults
    clearLayout(ResultsLayout)

    ResultsBox.setLayout(ResultsLayout)

    if searchMode == "Search by String":
        searchResults = index.searchByName(stringBox.text())
    elif searchMode == "Search by Tags":
        searchResults = index.searchByTags(selectedTags)
    elif searchMode == "Search by String and Tags":
        searchResults = index.searchByNameAndTags(stringBox.text(), selectedTags)


    count = 0
    for r in searchResults:
        picture = PictureWidget(r)
        picture.setPixmap(QPixmap("./Repo-Chan/" + r).scaled(100,100))
        ResultsLayout.addWidget(picture, 0 + 3 * int(count/5), count % 5)
        ResultsLayout.addWidget(QLabel(r), 1 + 3 * int(count/5), count % 5)
        ResultsLayout.addWidget(TagsWidget(r), 2 + 3 * int(count/5), count % 5) 
        count += 1
    if count == 0:
        ResultsLayout.addWidget(QLabel("No Results!"))
    ResultsBox.setLayout(ResultsLayout)

app = QApplication([])
window = QWidget()
window.setWindowTitle("AniPhoto Tagger")
window.setGeometry(100, 100, 600, 400)

def startupRoutine():
    index.readJsonRules()
    index.readJsonIndex()
    index.index()

startupRoutine()


vbox = QGridLayout()

searchBox = QComboBox()
searchBox.addItem("Search by String")
searchBox.addItem("Search by Tags")
searchBox.addItem("Search by String and Tags")
searchBox.activated.connect(updateSearchMode)

vbox.addWidget(QLabel("Search Mode:"), 0, 0, alignment=Qt.AlignmentFlag.AlignTop)

vbox.addWidget(searchBox, 0, 1, alignment=Qt.AlignmentFlag.AlignTop)

vbox.addWidget(QLabel(""), 0, 3, 1, 2)

searchButton = QPushButton("Search!")
searchButton.setEnabled(True)
searchButton.clicked.connect(search)

vbox.addWidget(searchButton, 0, 5, alignment=Qt.AlignmentFlag.AlignTop)

#TBD: Fix Regex
vbox.addWidget(QLabel("String Matching:"), 1, 0, alignment=Qt.AlignmentFlag.AlignTop)

stringBox = QLineEdit()
vbox.addWidget(stringBox, 1, 1, alignment=Qt.AlignmentFlag.AlignTop)

vbox.addWidget(QLabel("Tag Matching:"), 2, 0, alignment=Qt.AlignmentFlag.AlignTop)
TagsBox = QWidget()
TagsLayout = TagSelectLayout()
TagsBox.setLayout(TagsLayout)
vbox.addWidget(TagsBox, 2, 0, alignment=Qt.AlignmentFlag.AlignTop)

# add a class for the tag image window
def popWindow():
    secondWindow.show()
    secondWindow.update()

def callIndex():
    index.index()
    index.saveIndex()
    secondWindow.update()

def save():
    index.saveIndex()
    index.saveRule()

class ImageTagDisplay(QWidget):
    def __init__(self, mode = True):
        super(ImageTagDisplay, self).__init__()
        self.setWindowTitle("Image and Tag View")
        self.mode = mode # True = View by Image; False = View by Tag
        self.layout = QGridLayout() # Main layout
        
        self.layout.addWidget(QLabel("View Mode:"), 0, 0, alignment= Qt.AlignmentFlag.AlignTop)
        
        self.selector = QComboBox()
        self.selector.addItem("Image View")
        self.selector.addItem("Tag View")
        self.selector.activated.connect(self.updateViewMode)
        self.layout.addWidget(self.selector, 0, 1, alignment= Qt.AlignmentFlag.AlignTop)
        
        self.indexBtn = QPushButton("Refresh")
        self.saveBtn = QPushButton("Save Current Configuration")

        self.indexBtn.clicked.connect(callIndex)
        self.saveBtn.clicked.connect(save)

        self.layout.addWidget(self.indexBtn, 1, 1, alignment= Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.saveBtn, 1, 2, alignment= Qt.AlignmentFlag.AlignTop)
        
        self.layout.addWidget(QLabel("Add new tag:"), 2, 0, alignment= Qt.AlignmentFlag.AlignTop)

        self.newTagBox = QLineEdit()
        self.newTagBtn = QPushButton("Add me!")
        self.newTagBtn.clicked.connect(self.addTagBtn)
        self.layout.addWidget(self.newTagBox, 2, 1, alignment= Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.newTagBtn, 2, 2, alignment= Qt.AlignmentFlag.AlignTop)

        self.rulesWidget = QWidget()
        self.rulesLayout = QGridLayout()
        self.rulesWidget.setLayout(self.rulesLayout)
        self.applyAllRuleBtn = QPushButton()
        self.unapplyAllRuleBtn = QPushButton()

        self.addRuleBtn = AddRuleBtn()

        self.results = QWidget() # Display Layout
        self.resultslayout = QGridLayout()
        self.results.setLayout(self.resultslayout)

        self.layout.addWidget(self.results, 3, 0, alignment=Qt.AlignmentFlag.AlignTop)

        self.setLayout(self.layout)
          
    def addTagBtn(self):
        addTagDisplay(self.newTagBox.text())

    def updateViewMode(self):
        if self.selector.currentText() == "Image View":
            self.mode = True
        else:
            self.mode = False
        self.update()

    def update(self):
        count = 0
        clearLayout(self.resultslayout)
        if self.mode:
            for r in list(index.images.keys()):
                picture = PictureWidget(r)
                picture.setPixmap(QPixmap("./Repo-Chan/" + r).scaled(100,100))
                self.resultslayout.addWidget(picture, 0 + 4 * int(count/5), count % 5)
                self.resultslayout.addWidget(QLabel(r), 1 + 4 * int(count/5), count % 5)
                self.resultslayout.addWidget(TagsWidget(r, True), 2 + 4 * int(count/5), count % 5) 
                self.resultslayout.addWidget(TagMeBtn(r), 3 + 4 * int(count/5), count % 5)
                count += 1
        else:
            self.rulesWidget = QWidget()
            self.rulesLayout = QGridLayout()
            self.rulesWidget.setLayout(self.rulesLayout)
            self.applyAllRuleBtn = QPushButton("Apply all tagging rules")
            self.unapplyAllRuleBtn = QPushButton("Unapply all tagging rules")

            self.resultslayout.addWidget(QLabel("Tagging Rules:"), 0, 0)
            
            self.addRuleBtn = AddRuleBtn()
            self.resultslayout.addWidget(self.addRuleBtn, 0, 1)

            self.applyAllRuleBtn.clicked.connect(applyAllRule)
            self.resultslayout.addWidget(self.applyAllRuleBtn, 1, 0)
            self.unapplyAllRuleBtn.clicked.connect(unapplyAllRule)
            self.resultslayout.addWidget(self.unapplyAllRuleBtn, 1, 1)

            countRules = 0
            for r in index.rules:
                self.rulesLayout.addWidget(RuleWidget(r), countRules*2, 0, alignment=Qt.AlignmentFlag.AlignTop)
                delRuleBtn = QPushButton("Delete this rule!")
                self.rulesLayout.addWidget(delRuleBtn, countRules*2 + 1, 0, alignment=Qt.AlignmentFlag.AlignTop)
                delRuleBtn.clicked.connect(partial(deleteRule, r))
                applyRuleBtn = QPushButton("Apply this rule!")
                self.rulesLayout.addWidget(applyRuleBtn, countRules*2 + 1, 4, alignment=Qt.AlignmentFlag.AlignTop)
                applyRuleBtn.clicked.connect(partial(applyOneRule, r))
                unapplyRuleBtn = QPushButton("Unapply this rule!")
                self.rulesLayout.addWidget(unapplyRuleBtn, countRules*2 + 1, 5, alignment=Qt.AlignmentFlag.AlignTop)
                unapplyRuleBtn.clicked.connect(partial(unapplyOneRule, r))
                countRules += 1

            self.resultslayout.addWidget(self.rulesWidget, 2, 0)

            self.resultslayout.addWidget(QLabel("Tags:"), 3, 0)

            for r in list(index.tags.keys()):
                tagView = TagViewWidget(r)
                self.resultslayout.addWidget(tagView, 4 + count, 0)
                count += 1
        self.results.setLayout(self.resultslayout)
        save()


def applyAllRule():
    index.indexByRule()
    TagsLayout.update()
    secondWindow.update()

def unapplyAllRule():
    index.undoIndexByRule()
    TagsLayout.update()
    secondWindow.update()

def applyOneRule(rule):
    index.applyRule(rule)
    TagsLayout.update()
    secondWindow.update()

def unapplyOneRule(rule):
    index.unapplyRule(rule)
    TagsLayout.update()
    secondWindow.update()

def deleteRule(rule):
    index.removeRule(rule)
    secondWindow.update()

class RuleWidget(QWidget):
    def __init__(self, string):
        super(RuleWidget, self).__init__()
        self.layout = QHBoxLayout()
        self.string = string
        self.tags = index.rules[string]
        self.tagsAppliedLayout = QGridLayout()
        self.editRuleBtn = EditRuleBtn(self.string)
        self.update()

    def update(self):
        clearLayout(self.layout)
        clearLayout(self.tagsAppliedLayout)
        self.layout.addWidget(QLabel("String:"))
        self.layout.addWidget(QLabel(self.string))
        self.layout.addWidget(QLabel("Tags:"))
        self.updateTags()
        self.tagsWidget = QWidget()
        self.tagsWidget.setLayout(self.tagsAppliedLayout)   
        self.layout.addWidget(self.tagsWidget)
        self.layout.addWidget(self.editRuleBtn)
        self.setLayout(self.layout)
    

    def updateTags(self):
        clearLayout(self.tagsAppliedLayout)
        self.tags = index.rules[self.string]
        count = 0
        for t in self.tags:
            self.tagsAppliedLayout.addWidget(QLabel(t), int(count/3), count % 3)
            count += 1
        
class EditRuleBtn(QPushButton):
    def __init__(self, ruleString):
        super(EditRuleBtn, self).__init__()
        self.setText("Edit this Rule")
        self.string = ruleString
        self.clicked.connect(self.editRule)

        self.window = EditRuleWindow(ruleString)

    def editRule(self):
        self.window.show()

class EditRuleWindow(QWidget):
    def __init__(self, ruleString):
        # Need to Rewrite for tagArray behaviour when categorized
        super(EditRuleWindow, self).__init__() 
        self.layout = QGridLayout()
        self.string = ruleString
        self.setFixedWidth(400)
        self.ruleTags = index.rules[self.string]
        self.setWindowTitle("Edit Rule \"" + self.string + "\"")
        
        self.newStringBox = QLineEdit()
        self.newStringBtn = QPushButton("Change string!")
        self.newStringBtn.clicked.connect(self.updateString)

        self.tagsBox = QWidget()
        self.update()

    def updateString(self):
        newstring = self.newStringBox.text()
        index.editRuleString(self.string, newstring)
        self.string = newstring
        self.setWindowTitle("Edit Rule \"" + self.string + "\"")

    def closeEvent(self, event):
        secondWindow.update()
        QWidget.closeEvent(self, event)

    def update(self):
        clearLayout(self.layout)
        count = 0
        for i in list(index.tags.keys()):
            if i == "No Tags":
                continue
            checkbox = QCheckBox(i)
            if i in self.ruleTags:
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(partial(self.change, checkbox, i))
            self.layout.addWidget(checkbox, int(count/3), count % 3, alignment=Qt.AlignmentFlag.AlignCenter)
            count += 1        
        self.setLayout(self.layout)

    def change(self, box, tag):
        if box.isChecked():
            self.ruleTags.append(tag)
        else:
            if tag in self.ruleTags:
                self.ruleTags.remove(tag)

class AddRuleBtn(QPushButton):
    def __init__(self):
        super(AddRuleBtn, self).__init__()
        self.setText("Add Rule")
        self.window = AddRuleWindow()
        self.clicked.connect(self.addRule)

    def addRule(self):
        self.window.show()

class AddRuleWindow(QWidget):
    def __init__(self):
        super(AddRuleWindow, self).__init__() 
        self.layout = QVBoxLayout()
        self.setWindowTitle("Add Rule")
        self.stringBox = QLineEdit()
        self.setFixedWidth(400)
        self.array = []

        self.layout.addWidget(QLabel("Matching string:"))
        self.layout.addWidget(self.stringBox)

        self.layout.addWidget(QLabel("Matching tags:"))
        self.tagBox = QWidget()
        self.tagLayout = QGridLayout()
        self.tagBox.setLayout(self.tagLayout)

        self.layout.addWidget(self.tagBox)
        count = 0
        # To implement category
        for i in index.tags.keys():
            if i == "No Tags":
                continue
            checkbox = QCheckBox(i)
            checkbox.stateChanged.connect(partial(self.change, checkbox, i))
            self.tagLayout.addWidget(checkbox, int(count/3), count % 3, alignment=Qt.AlignmentFlag.AlignCenter)
            count += 1        
        self.setLayout(self.layout)

    def closeEvent(self, event):
        string = self.stringBox.text()
        if string != "":
            index.addRule(string, self.array)
            secondWindow.update()
        QWidget.closeEvent(self, event)


    def change(self, box, tag):
        if box.isChecked():
            self.array.append(tag)
        else:
            if tag in self.array:
                self.array.remove(tag)

class TagViewWidget(QWidget):
    def __init__(self, name, expanded = False):
        super(TagViewWidget, self).__init__()
        self.layout = QGridLayout()
        self.tagName = name
        self.expanded = expanded
        self.expandText = "Expand"
        if self.expanded:
            self.expandText = "Collapse"

        
        if self.tagName != "No Tags":
            self.delTagBtn = QPushButton("Delete this tag")
            self.delTagBtn.clicked.connect(partial(deleteTagDisplay, self.tagName))

        self.expandBtn = QPushButton(self.expandText)
        self.expandBtn.clicked.connect(self.expandCollapse)

        self.update()
    
    def expandCollapse(self):
        if self.expandBtn.text() == "Expand":
            self.expanded = True
            self.expandText = "Collapse"
            self.expandBtn.setText(self.expandText)
            self.update()
        
        else:
            self.expandText = "Expand"
            self.expandBtn.setText(self.expandText)
            self.expanded = False
            self.update()
            

    def update(self):
        clearLayout(self.layout)
 
        self.layout.addWidget(QLabel(self.tagName), 0, 0, alignment=Qt.AlignmentFlag.AlignTop)
        
        if self.tagName != "No Tags":
            self.delTagBtn = QPushButton("Delete this tag")
            self.delTagBtn.clicked.connect(partial(deleteTagDisplay, self.tagName))
            self.layout.addWidget(self.delTagBtn, 0, 1, alignment=Qt.AlignmentFlag.AlignTop)

        self.expandBtn = QPushButton(self.expandText)
        self.expandBtn.clicked.connect(self.expandCollapse)
        self.layout.addWidget(self.expandBtn, 0, 2, alignment=Qt.AlignmentFlag.AlignTop)

        self.setLayout(self.layout)

        if self.expanded:
            count = 0
            for i in index.tags[self.tagName]:
                picture = PictureWidget(i)
                picture.setPixmap(QPixmap("./Repo-Chan/" + i).scaled(100,100))
                self.layout.addWidget(picture, 1 + 4 * int(count/5), count % 5)
                self.layout.addWidget(QLabel(i), 2 + 4 * int(count/5), count % 5)

                taggingBtn = TagMeBtn(i)
                self.layout.addWidget(taggingBtn, 3 + 4 * int(count/5), count % 5)
                
                if self.tagName != "No Tags":
                    untagBox = QPushButton("untag this image")
                    untagBox.clicked.connect(partial(self.untag, i))
                    self.layout.addWidget(untagBox, 4 + 4 * int(count/5), count % 5) 

                count += 1

    def untag(self, image):
        index.delImgTag(image, self.tagName)
        self.update()

def addTagDisplay(name):
    index.addTag(name)
    secondWindow.update()
    TagsLayout.update()
    ResultsLayout.update()


def deleteTagDisplay(name):
    index.delTag(name)
    secondWindow.update()
    TagsLayout.update()
    ResultsLayout.update()

class TagMeBtn(QPushButton):
    def __init__(self, image):
        super(TagMeBtn, self).__init__()
        self.setText("Tag me!")
        self.clicked.connect(partial(self.tagMe, image))

        self.tagAddWindow = TagAddWindow(image)

    def tagMe(self, image):
        self.tagAddWindow.update()
        self.tagAddWindow.show()

class TagAddWindow(QWidget):
    def __init__(self, image):
        # Need to Rewrite for tagArray behaviour when categorized
        super(TagAddWindow, self).__init__() 
        self.layout = QGridLayout()
        self.setWindowTitle("Add Tags for " + image)
        self.setFixedWidth(400)
        self.tagArray = list(index.tags.keys())
        if "No Tags" in self.tagArray:
            self.tagArray.remove("No Tags")
        self.image = image
        self.update()

    def refreshArray(self):
        # Rewrite some things here if not fetch all tags
        # For Improvement
        self.tagArray = list(index.tags.keys())
        if "No Tags" in self.tagArray:
            self.tagArray.remove("No Tags")


    def closeEvent(self, event):
        secondWindow.update()
        TagsLayout.update()
        ResultsLayout.update()
        QWidget.closeEvent(self, event)

    def update(self):
        clearLayout(self.layout)
        self.refreshArray()
        count = 0
        for i in self.tagArray:
            checkbox = QCheckBox(i)
            if i in index.images[self.image]:
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(partial(self.change, checkbox, i))
            self.layout.addWidget(checkbox, int(count/3), count % 3, alignment=Qt.AlignmentFlag.AlignCenter)
            count += 1        
        self.setLayout(self.layout)

    def change(self, box, tag):
        if box.isChecked():
            index.addImgTag(self.image, tag)
        else:
            index.delImgTag(self.image, tag)


        
         
secondWindow = ImageTagDisplay()
btn = QPushButton("Show Tags and Images")
btn.clicked.connect(popWindow)

vbox.addWidget(btn, 2, 1) 


vbox.addWidget(QLabel("Results:"), 4, 0, alignment=Qt.AlignmentFlag.AlignTop)

ResultsBox = QWidget()
ResultsLayout = QGridLayout()
ResultsBox.setLayout(ResultsLayout)
vbox.addWidget(ResultsBox, 5, 0, alignment=Qt.AlignmentFlag.AlignTop)

window.setLayout(vbox)

window.show()

save()

sys.exit(app.exec())
