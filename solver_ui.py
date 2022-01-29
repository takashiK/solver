import os
from kivy.app import App
from kivy.config import Config
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.graphics import Line
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup

from solver import Number_grid,Number_selector

########################################################################
##
##  Number Selector
##
class Number_selector_ui(GridLayout):
    def __init__(self,selector:Number_selector):
        super(Number_selector_ui, self).__init__()
        self.register_event_type('on_selected')   # register event : number is selected by user. (not caused by solver) 
        self.padding = [2,2] # layout value
        self.numbers = []    # number selectors bottons
        self.mode = 'undefined'

        self.selector:Number_selector = selector

        for i in range(9):
            number = Button(text=str(i+1))
            number.bind(on_release=self.button_callback)
            self.numbers.append(number)
        self.build_selector()

    def position(self):
        return self.selector.grid_position

    def on_selected(self, *args, **kwargs):
        pass

    # build selector ui
    def build_selector(self):
        if self.mode == 'select':
            for (number,enabled) in zip(self.numbers,self.selector.numbers):
                number.disabled = not enabled
        else:
            self.mode = 'select'
            self.clear_widgets()
            self.cols = 3
            self.rows = 3
            for (number,enabled) in zip(self.numbers,self.selector.numbers):
                number.disabled = not enabled
                self.add_widget(number)

    # build selected value ui
    def build_represent(self):
        self.mode = 'represent'
        self.clear_widgets()
        self.cols = 1
        self.rows = 1
        label = Label(text=str(self.selector.value()))
        self.add_widget(label)
        if self.selector.is_user_select():
            lines = []
            lines.append([self.pos[0],self.pos[1]])
            lines.append([self.pos[0]+self.size[0],self.pos[1]])
            lines.append([self.pos[0]+self.size[0],self.pos[1]+self.size[1]])
            lines.append([self.pos[0],self.pos[1]+self.size[1]])
            with label.canvas.before:
                Color(0.2,0.2,0.2)
                Rectangle(pos=self.pos,size=self.size)
                Color(0.5,0.5,0.5)
                Line(points=lines, close='True')


    # action for selection button (number button)
    def button_callback(self,number):
        if not number.disabled :
            self.selector.setValue(int(number.text),True)
            self.update_ui()
            self.dispatch('on_selected')

    def update_ui(self):
        if self.selector.value() is None:
            self.build_selector()
        else:
            self.build_represent()
 
########################################################################
##
##  Number Grid
##
class Number_grid_ui(GridLayout):
    def __init__(self):
        super(Number_grid_ui, self).__init__()
        self.number_grid = Number_grid()
        self.selectors_ui = []
        self.cols = 3 # layout value
        self.rows = 3 # layout value

        for i in range(self.cols):
            for j in range(self.rows):
                grid = GridLayout(cols=3,rows=3,padding=[3,3])
                self.add_widget(grid)
                for l in range(grid.cols):
                    for m in range(grid.rows):
                        selector = self.number_grid.selector(i,j,l,m)
                        selector_ui = Number_selector_ui(selector)
                        selector_ui.bind(on_selected=self.change_select)
                        grid.add_widget(selector_ui)
                        self.selectors_ui.append(selector_ui)

    def solve(self):
        self.number_grid.solve()
        self.update_ui()

    # clear alldata (include user selection)
    def clear_solve(self, *args, **kwargs):
        self.number_grid.clear_solve()
        self.update_ui()

    # undo user selection
    def undo_solve(self, *args, **kwargs):
        self.number_grid.undo_history()
        self.update_ui()

    # load selection from file
    def load(self, filename):
        result = self.number_grid.load(filename)
        self.update_ui()
        return result
    
    # store user selection to file
    def store(self, filename):
        self.number_grid.store(filename)

    # callback point for Number selector's on_selected
    def change_select(self,selector_ui:Number_selector_ui):
        self.number_grid.append_history(selector_ui.selector)
        self.solve()

    def update_ui(self):
        for selector_ui in self.selectors_ui:
            selector_ui.update_ui()

######################################################
##
## File Dialog
##
class FileDialog(BoxLayout):
    def __init__(self):
        super(FileDialog, self).__init__()
        self.orientation="vertical"

        self.register_event_type('on_ok')
        self.register_event_type('on_cancel')

        file = FileChooserIconView(path=os.getcwd())
        self.add_widget(file)
        
        text = TextInput(hint_text='Input filename', size_hint=(1,0.1))
        def update_selection(instance,sel):
            if not file.selection:
                text.text = ''
            else:
                text.text = file.selection[0][len(file.path)+1:]
        file.bind(selection=update_selection)
        self.add_widget(text)

        hb = BoxLayout(orientation="horizontal", size_hint=(1,0.1))
        self.add_widget(hb)

        btn = Button(text="OK")
        btn.bind(on_release=lambda button: self.dispatch('on_ok', file.path + os.sep + text.text if text.text else ''))
        hb.add_widget(btn)

        btn = Button(text="Cancel")
        btn.bind(on_release=lambda button: self.dispatch('on_cancel'))
        hb.add_widget(btn)

    def on_ok(self, *args, **kwargs):
        pass

    def on_cancel(self, *args, **kwargs):
        pass

######################################################
##
## Main App
##
class SolverApp(App):
    def __init__(self, **kwargs):
        super(SolverApp, self).__init__(**kwargs)
        self.title = 'Solver'
    def build(self):
        vb = BoxLayout(orientation="vertical")

        hb = BoxLayout(orientation="horizontal", size_hint=(1,0.05))
        solver_ui = Number_grid_ui()

        vb.add_widget(hb)
        vb.add_widget(solver_ui)

        btn = Button(text="Clear")
        btn.bind(on_release=solver_ui.clear_solve)
        hb.add_widget(btn)
        btn = Button(text="Undo")
        btn.bind(on_release=solver_ui.undo_solve)
        hb.add_widget(btn)
        btn = Button(text="Load")
        btn.bind(on_release=lambda button:self.load(solver_ui))
        hb.add_widget(btn)
        btn = Button(text="Save")
        btn.bind(on_release=lambda button:self.save(solver_ui))
        hb.add_widget(btn)
        
        return vb
    
    def dismiss_popup(self):
        if self._popup is not None:
            self._popup.dismiss()

    def load(self,solver_ui):
        dlg = FileDialog()
        dlg.bind(on_ok=lambda fileDlg,filename:self.dismiss_popup() or solver_ui.load(filename))
        dlg.bind(on_cancel=lambda fileDlg:self.dismiss_popup())
        self._popup = Popup(title="Load", content=dlg,size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self,solver_ui):
        dlg = FileDialog()
        dlg.bind(on_ok=lambda fileDlg,filename:self.dismiss_popup() or solver_ui.store(filename))
        dlg.bind(on_cancel=lambda fileDlg:self.dismiss_popup())
        self._popup = Popup(title="Save", content=dlg,size_hint=(0.9, 0.9))
        self._popup.open()

if __name__ == '__main__':
    Config.set('graphics', 'width', '600')
    Config.set('graphics', 'height', '600')

    SolverApp().run()
