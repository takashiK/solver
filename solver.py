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
                own_available = own_available - set([value])

    #vertical j,m freeze
    for s in range(3):
        for t in range(3):
            if s == i and t == l:
                continue
            value = selectors[s][j][t][m].value()
            if value is not None:
                disables.add(value)
                own_available = own_available - set([value])

    available = set(number.available())

    if len(available & disables) == 0:
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
        self.features['uniqueness'] = True
        self.features['number_group'] = True
        self.features['uniqueness_line'] = True
        self.features['uniqueness_grid'] = True

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
        if self.features['uniqueness'] and len(own_available) == 1:
            number.setValue(list(own_available)[0]) #uniqueness
            return True
        return False

    def single_solve(self,selectors,i,j,l,m):
        number = selectors[i][j][l][m]
        if number.value() is not None:
            return False

        disables = set()

        #group
        selector_part = [None]*3
        availables = []
        own_available = set(number.available())
        for s in range(3):
            selector_part[s] = [None]*3
            for t in range(3):
                if s == l and t == m:
                    continue
                selector_part[s][t] = selectors[i][j][s][t]
        if self.single_solve_part(number,selector_part,disables):
            return True

        #horizon i,l freeze
        selector_part = [None]*3
        availables = []
        own_available = set(number.available())
        for s in range(3):
            selector_part[s] = [None]*3
            for t in range(3):
                if s == j and t == m:
                    continue
                selector_part[s][t] = selectors[i][s][l][t]
        if self.single_solve_part(number,selector_part,disables):
            return True

        #vertical j,m freeze
        selector_part = [None]*3
        availables = []
        own_available = set(number.available())
        for s in range(3):
            selector_part[s] = [None]*3
            for t in range(3):
                if s == i and t == l:
                    continue
                selector_part[s][t] = selectors[s][j][t][m]
        if self.single_solve_part(number,selector_part,disables):
            return True
        
        old_availables = number.available()
        number.disable(disables)
        if len(number.available()) == 1:
            val = number.available()[0]
            number.setValue(val)

        if old_availables != number.available():
            return True

        return False

    def reflect_solve(self,selectors):
        update = False
        #uniqueness horizontal line
        for i in range(3):
            for l in range(3):
                for j in range(3):
                    available = set()
                    disable = set()
                    #target block line available numbers
                    for m in range(3):
                        disable = disable | selectors[i,j,l,m].available()
                    #remain block lines available numbers
                    for s in range(3):
                        if s != l:
                            for t in range(3):
                                available = available | selectors[i,j,s,t].available()
                    disable = disable - available
                    if len(available) > 0:
                        for s in range(3):
                            if s != j:
                                for t in range(3):
                                    old_available = selectors[i,s,l,t].available()
                                    selectors[i,s,l,t].disable(disable)
                                    if old_available != selectors[i,s,l,t].available():
                                        update = True

        #uniqueness vartical line
        for j in range(3):
            for m in range(3):
                for i in range(3):
                    available = set()
                    disable = set()
                    #target block line available numbers
                    for l in range(3):
                        disable = disable | selectors[i,j,l,m].available()
                    #remain block lines available numbers
                    for s in range(3):
                        if s != m:
                            for t in range(3):
                                available = available | selectors[i,j,s,t].available()
                    disable = disable - available
                    if len(available) > 0:
                        for s in range(3):
                            if s != i:
                                for t in range(3):
                                    old_available = selectors[s,j,t,m].available()
                                    selectors[s,j,t,m].disable(disable)
                                    if old_available != selectors[s,j,t,m].available():
                                        update = True

        return update

    def solve(self,selectors):
        while True:
            update = False
            for i in range(3):
                for j in range(3):
                    for l in range(3):
                        for m in range(3):
                            update = update or self.single_solve(selectors,i,j,l,m)
#            if update == False:
#                update = update or self.reflect_solve(selectors)
            if update == False:
                break

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
        self.solve()
        return True
    
    # store user selection to file
    def store(self, filename):
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

class SolverApp(App):
    def __init__(self, **kwargs):
        super(SolverApp, self).__init__(**kwargs)
        self.title = 'Solver'
    def build(self):
        vb = BoxLayout(orientation="vertical")

        hb = BoxLayout(orientation="horizontal", size_hint=(1,0.05))
        textBox = TextInput(hint_text='filename', multiline=False, size_hint=(1,0.05))
        solver = Number_grid()

        vb.add_widget(hb)
        vb.add_widget(textBox)
        vb.add_widget(solver)

        btn = Button(text="Clear")
        btn.bind(on_release=solver.clear_solve)
        hb.add_widget(btn)
        btn = Button(text="Undo")
        btn.bind(on_release=solver.undo_solve)
        hb.add_widget(btn)
        btn = Button(text="Load")
        btn.bind(on_release=lambda button:solver.load(textBox.text))
        hb.add_widget(btn)
        btn = Button(text="Save")
        btn.bind(on_release=lambda button:solver.store(textBox.text))
        hb.add_widget(btn)
        
        return vb

if __name__ == '__main__':
    Config.set('graphics', 'width', '600')
    Config.set('graphics', 'height', '600')

    SolverApp().run()
