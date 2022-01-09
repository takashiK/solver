import pandas as pd
import numpy as np
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

def single_verify(selectors,i,j,l,m):
    number = selectors[i][j][l][m]

    disables = set()

    #group
    for s in range(3):
        for t in range(3):
            if s == l and t == m:
                continue
            value = selectors[i][j][s][t].value()
            if value is not None:
                disables.add(value) #singleton

    #horizon i,l freeze
    for s in range(3):
        for t in range(3):
            if s == j and t == m:
                continue
            value = selectors[i][s][l][t].value()
            if value is not None:
                disables.add(value)

    #vertical j,m freeze
    for s in range(3):
        for t in range(3):
            if s == i and t == l:
                continue
            value = selectors[s][j][t][m].value()
            if value is not None:
                disables.add(value)

    available = set(number.available())

    if len(available - disables) > 0:
        return True
    return False

def verify(selectors):
    valid = True
    for i in range(3):
        for j in range(3):
            for l in range(3):
                for m in range(3):
                    valid = valid and single_verify(selectors,i,j,l,m)
    return valid

class Solver():
    def __init__(self):
        self.features = {}
        self.features['singleton'] = True
        self.features['number_group'] = True
        self.features['uniqueness'] = True
        self.features['uniqueness_line'] = True
        self.features['uniqueness_Multi'] = True

    def get_features(self):
        return self.features.copy()

    def set_features(self,feat):
        for key in self.features:
            v = feat[key]
            if (v is not None) and (type(v) is bool):
                self.features[key] = feat[key]

    def single_solve_part(self,number,selectors,disables):
        availables = []
        own_available = set(number.available())
        for s in range(3):
            for t in range(3):
                if selectors[s][t] is None:
                    continue
                value = selectors[s][t].value()
                if value is not None:
                    if self.features['singleton']:
                        disables.add(value) #singleton
                    own_available = own_available - set([value])
                else:
                    availables.append(selectors[s][t].available())
        for ava in availables:
            own_available = own_available - set(ava)
            if self.features['number_group']:
                length = len(ava)
                count  = 0
                for rel in availables:
                    if ava == rel:
                        count = count + 1
                if count == length:
                    for value in ava:
                        disables.add(value) # number group
        return own_available

    def single_solve(self,selectors,i,j,l,m):
        number = selectors[i][j][l][m]
        if number.value() is not None:
            return False

        disables = set()
        own_available = set()

        #group
        selector_part = [None]*3
        for s in range(3):
            selector_part[s] = [None]*3
            for t in range(3):
                if s == l and t == m:
                    continue
                selector_part[s][t] = selectors[i][j][s][t]
        own_available = own_available | self.single_solve_part(number,selector_part,disables)

        #horizon i,l freeze
        selector_part = [None]*3
        for s in range(3):
            selector_part[s] = [None]*3
            for t in range(3):
                if s == j and t == m:
                    continue
                selector_part[s][t] = selectors[i][s][l][t]
        own_available = own_available | self.single_solve_part(number,selector_part,disables)

        #vertical j,m freeze
        selector_part = [None]*3
        for s in range(3):
            selector_part[s] = [None]*3
            for t in range(3):
                if s == i and t == l:
                    continue
                selector_part[s][t] = selectors[s][j][t][m]
        own_available = own_available | self.single_solve_part(number,selector_part,disables)
        
        old_availables = number.available()
        number.disable(disables)
        own_available = own_available - disables
        if len(number.available()) == 1:
            val = number.available()[0]
            number.setValue(val)
        if (len(own_available) == 1) and self.features['uniqueness']:
            number.setValue(list(own_available)[0])

        if old_availables != number.available():
            return True

        return False

    def partial_selectors(self,type,selectors,s,t):
        result = []
        if type == 'block':
            i = s
            j = t
            for l in range(3):
                for m in range(3):
                    result.append(selectors[i][j][l][m])
        elif type == 'horizontal':
            i = s
            l = t
            for j in range(3):
                for m in range(3):
                    result.append(selectors[i][j][l][m])
        elif type == 'vertical':
            j = s
            m = t
            for i in range(3):
                for l in range(3):
                    result.append(selectors[i][j][l][m])
        return result

    def line_disabler(self,direction,line,selectors,i,j,num):
        update = False
        if direction == 'h':
            for s in range(3):
                if s == j:
                    continue
                for t in range(3):
                    selector = selectors[i][s][line][t]
                    if (selector.value() is None) and (num in selector.available()):
                        selector.disable([num])
                        update = True
        elif direction == 'v':
            for s in range(3):
                if s == i:
                    continue
                for t in range(3):
                    selector = selectors[s][j][t][line]
                    if (selector.value() is None) and (num in selector.available()):
                        selector.disable([num])
                        update = True
        return update

    def make_blockdetectors(self):
        detectors = []
        detectors.append([set([0,1,2]),lambda selectors,i,j,num:self.line_disabler('h',0,selectors,i,j,num)])
        detectors.append([set([3,4,5]),lambda selectors,i,j,num:self.line_disabler('h',1,selectors,i,j,num)])
        detectors.append([set([6,7,8]),lambda selectors,i,j,num:self.line_disabler('h',2,selectors,i,j,num)])
        detectors.append([set([0,3,6]),lambda selectors,i,j,num:self.line_disabler('v',0,selectors,i,j,num)])
        detectors.append([set([1,4,7]),lambda selectors,i,j,num:self.line_disabler('v',1,selectors,i,j,num)])
        detectors.append([set([2,5,8]),lambda selectors,i,j,num:self.line_disabler('v',2,selectors,i,j,num)])
        return detectors

    def available_solve(self,selectors):
        update = False
        detectors = self.make_blockdetectors()
        for i in range(3):
            for j in range(3):
                available = []
                for s in range(9):
                    available.append(set())
                partial = self.partial_selectors('block',selectors,i,j)
                # create number ⇒ positions available list
                for s in range(9):
                    tmp = partial[s].available()
                    for num in partial[s].available():
                        available[num-1].add(s)
                for num in range(1,10):
                    tgt = available[num-1]
                    same_pos_nums = []
                    for num2 in range(num,10):
                        if tgt == available[num2-1]:
                            same_pos_nums.append(num2)
                    if len(tgt) == len(same_pos_nums):
                        #target number pos disabler
                        disables = set(range(1,10)) - set(same_pos_nums)
                        if len(disables) > 0:
                            for pos in tgt:
                                part = partial[pos]
                                if (part.value() is None) and (len(set(part.available()) & disables) > 0):
                                    part.disable(disables)
                                    update = True
                    #line disabler
                    for detector in detectors:
                        if len(detector[0] & tgt) == len(tgt):
                            update = update or detector[1](selectors,i,j,num)

        return update

    def solve(self,selectors):
        while True:
            update_part = False
            while True:
                update = False
                for i in range(3):
                    for j in range(3):
                        for l in range(3):
                            for m in range(3):
                                update = update or self.single_solve(selectors,i,j,l,m)
                update_part = update_part or update
                if update == False:
                    break
            while True:
                update = self.available_solve(selectors)
                update_part = update_part or update
                if update == False:
                    break
            if update_part == False:
                break
        print(verify(selectors))
        self.available_solve(selectors)

########################################################################
##
##  Number Selector
##
class Number_selector(GridLayout):
    def __init__(self,position):
        super(Number_selector, self).__init__()
        self.register_event_type('on_selected')   # register event : number is selected by user. (not caused by solver) 
        self.padding = [2,2] # layout value
        self.numbers = []    # number selectors bottons
        self.selected_value = None  # user selected or solver solved value.
        self.selected = False # True if it is selected by user.
        self.grid_position = position # grid position (y,x)
        for i in range(9):
            number = Button(text=str(i+1))
            number.bind(on_release=self.button_callback)
            self.numbers.append(number)
        self.build_selector()

    def position(self):
        return self.grid_position

    def on_selected(self, *args, **kwargs):
        pass

    # build selector ui
    def build_selector(self):
        self.clear_widgets()
        self.cols = 3
        self.rows = 3
        self.selected_value = None
        self.selected = False
        for number in self.numbers:
            number.disabled = False
            self.add_widget(number)

    # build selected value ui
    def build_represent(self, value):
        self.clear_widgets()
        self.cols = 1
        self.rows = 1
        self.selected_value = value
        label = Label(text=str(value))
        self.add_widget(label)
        if self.selected:
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
            self.setValue(int(number.text),True)
            self.dispatch('on_selected')
    
    def is_user_select(self):
        return self.selected

    # set selected value. mean of None is deselection.
    def setValue(self,value,user=False):
        if value is None:
            self.build_selector()
        else:
            self.selected = user
            self.build_represent(value)
 
    # int value of selected number.
    def value(self):
        return self.selected_value

    # Ture : value is selected by user
    def isFixed(self):
        return self.selected

    # available values. it is result of solver.
    def available(self):
        values = []
        if self.selected_value is None:
            for number in self.numbers:
                if not number.disabled:
                    values.append(int(number.text))
        else:
            values.append(self.selected_value)
        return values

    # set disabled values by solver.
    def disable(self,dsel):
        for i in dsel:
            self.numbers[i-1].disabled = True

    # reset result of solver.
    def reset_solve(self):
        if self.selected:
            for number in self.numbers:
                number.disabled = False
        else:
            self.clear_solve()

    # clear result of solver and user selection.
    def clear_solve(self):
        self.setValue(None)

########################################################################
##
##  Number Grid
##
class Number_grid(GridLayout):
    def __init__(self):
        super(Number_grid, self).__init__()
        self.cols = 3 # layout value
        self.rows = 3 # layout value
        self.selectors = [] # selectors grid (3,3) in (3,3) "Sudoku shape"
        self.selectors_flat = [] # selectors 1 dim array
        self.history = [] # history of user selection
        self.solver = Solver()

        for i in range(self.cols):
            jdim = []
            self.selectors.append(jdim)
            for j in range(self.rows):
                grid = GridLayout(cols=3,rows=3,padding=[3,3])
                self.add_widget(grid)
                ldim = []
                jdim.append(ldim)
                for l in range(grid.cols):
                    mdim = []
                    ldim.append(mdim)
                    for m in range(grid.rows):
                        selector = Number_selector((i*3+l,j*3+m))
                        selector.bind(on_selected=self.change_select)
                        grid.add_widget(selector)
                        mdim.append(selector)
                        self.selectors_flat.append(selector)

    def solve(self):
        self.solver.solve(self.selectors)

    # reset result of solver
    def reset_solve(self):
        for solver in self.selectors_flat:
            solver.reset_solve()

    # clear alldata (include user selection)
    def clear_solve(self, *args, **kwargs):
        self.history.clear()
        for solver in self.selectors_flat:
            solver.clear_solve()

    # undo user selection
    def undo_solve(self, *args, **kwargs):
        if len(self.history) > 0:
            solver = self.history.pop()
            solver.clear_solve()
            self.reset_solve()
            self.solve()

    # load selection from file
    def load(self, filename):
        print(filename)
        self.clear_solve()

        if not filename:
            return False
        if not os.path.exists(filename):
            return False

        df = pd.read_csv(filename)
        data_type = df['type']
        x_pos = df['x_pos']
        y_pos = df['y_pos']
        value = df['value']

        if x_pos.dtype != np.int64 or y_pos.dtype != np.int64 or value.dtype != np.int64:
            return False

        for s in range(len(data_type)):
            if data_type[s] != 'U':
                continue
            else:
                x = int(x_pos[s])
                y = int(y_pos[s])
                v = int(value[s])
                j,m = divmod(x,3)
                i,l = divmod(y,3)
                selector = self.selectors[i][j][l][m]
                selector.setValue(v,True)
                self.history.append(selector)
        self.solve()
        return True
    
    # store user selection to file
    def store(self, filename):
        print(filename)
        if filename:
            data_type = []
            x_pos = []
            y_pos = []
            value = []
            for sel in self.history:
                data_type.append('U')
                y_pos.append(sel.position()[0])
                x_pos.append(sel.position()[1])
                value.append(sel.value())
            for sel in self.selectors_flat:
                if (not sel.is_user_select()) and (sel.value() is not None):
                    data_type.append('S')
                    y_pos.append(sel.position()[0])
                    x_pos.append(sel.position()[1])
                    value.append(sel.value())
            df = pd.DataFrame({'type':data_type,'x_pos':x_pos,'y_pos':y_pos,'value':value})
            df.to_csv(filename)

    # callback point for Number selector's on_selected
    def change_select(self,selector):
        self.history.append(selector)
        self.solve()

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
        solver = Number_grid()

        vb.add_widget(hb)
        vb.add_widget(solver)

        btn = Button(text="Clear")
        btn.bind(on_release=solver.clear_solve)
        hb.add_widget(btn)
        btn = Button(text="Undo")
        btn.bind(on_release=solver.undo_solve)
        hb.add_widget(btn)
        btn = Button(text="Load")
        btn.bind(on_release=lambda button:self.load(solver))
        hb.add_widget(btn)
        btn = Button(text="Save")
        btn.bind(on_release=lambda button:self.save(solver))
        hb.add_widget(btn)
        
        return vb
    
    def dismiss_popup(self):
        if self._popup is not None:
            self._popup.dismiss()

    def load(self,solver):
        dlg = FileDialog()
        dlg.bind(on_ok=lambda fileDlg,filename:self.dismiss_popup() or solver.load(filename))
        dlg.bind(on_cancel=lambda fileDlg:self.dismiss_popup())
        self._popup = Popup(title="Load", content=dlg,size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self,solver):
        dlg = FileDialog()
        dlg.bind(on_ok=lambda fileDlg,filename:self.dismiss_popup() or solver.store(filename))
        dlg.bind(on_cancel=lambda fileDlg:self.dismiss_popup())
        self._popup = Popup(title="Save", content=dlg,size_hint=(0.9, 0.9))
        self._popup.open()

if __name__ == '__main__':
    Config.set('graphics', 'width', '600')
    Config.set('graphics', 'height', '600')

    SolverApp().run()
