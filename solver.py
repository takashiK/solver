import pandas as pd
from kivy.app import App
from kivy.config import Config
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

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

    def single_solve(self,selectors,i,j,l,m):
        number = selectors[i][j][l][m]
        if number.value() is not None:
            return False

        disables = set()

        #group
        availables = []
        own_available = set(number.available())
        for s in range(3):
            for t in range(3):
                if s == l and t == m:
                    continue
                value = selectors[i][j][s][t].value()
                if value is not None:
                    if self.features['singleton']:
                        disables.add(value) #singleton
                    own_available = own_available - set([value])
                else:
                    availables.append(selectors[i][j][s][t].available())
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

        #horizon i,l freeze
        availables = []
        own_available = set(number.available())
        for s in range(3):
            for t in range(3):
                if s == j and t == m:
                    continue
                value = selectors[i][s][l][t].value()
                if value is not None:
                    if self.features['singleton']:
                        disables.add(value) #singleton
                    own_available = own_available - set([value])
                else:
                    availables.append(selectors[i][s][l][t].available())
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
                        disables.add(value)
        if self.features['uniqueness'] and len(own_available) == 1:
            number.setValue(list(own_available)[0])
            return True

        #vertical j,m freeze
        availables = []
        own_available = set(number.available())
        for s in range(3):
            for t in range(3):
                if s == i and t == l:
                    continue
                value = selectors[s][j][t][m].value()
                if value is not None:
                    if self.features['singleton']:
                        disables.add(value) #singleton
                    own_available = own_available - set([value])
                else:
                    availables.append(selectors[s][j][t][m].available())
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
                        disables.add(value)
        if self.features['uniqueness'] and len(own_available) == 1:
            number.setValue(list(own_available)[0])
            return True
        
        old_availables = number.available()
        number.disable(disables)
        if len(number.available()) == 1:
            val = number.available()[0]
            number.setValue(val)

        if old_availables != number.available():
            return True

        return False


    def solve(self,selectors):
        while True:
            update = False
            for i in range(3):
                for j in range(3):
                    for l in range(3):
                        for m in range(3):
                            update = update or self.single_solve(selectors,i,j,l,m)
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
            self.selected = True
            self.setValue(int(number.text))
            self.dispatch('on_selected')
    
    # set selected value. mean of None is deselection.
    def setValue(self,value):
        if value is None:
            self.build_selector()
        else:
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
        if filename is not None:
            db = pd.read_csv(filename)
    
    # store user selection to file
    def store(self, filename):
        if filename is not None:
            db = pd.to_csv(filename)

    # callback point for Number selector's on_selected
    def change_select(self,solver):
        self.history.append(solver)
        self.solve()

class SolverApp(App):
    def __init__(self, **kwargs):
        super(SolverApp, self).__init__(**kwargs)
        self.title = 'Solver'
    def build(self):
        vb = BoxLayout(orientation="vertical")
        hb = BoxLayout(orientation="horizontal", size_hint=(1,0.05))
        vb.add_widget(hb)
        solver = Number_grid()
        vb.add_widget(solver)
        btn = Button(text="Clear")
        btn.bind(on_release=solver.clear_solve)
        hb.add_widget(btn)
        btn = Button(text="Undo")
        btn.bind(on_release=solver.undo_solve)
        hb.add_widget(btn)
        btn = Button(text="Load")
        btn.bind(on_release=solver.load)
        hb.add_widget(btn)
        btn = Button(text="Save")
        btn.bind(on_release=solver.store)
        hb.add_widget(btn)
        return vb

if __name__ == '__main__':
    Config.set('graphics', 'width', '600')
    Config.set('graphics', 'height', '600')

    SolverApp().run()
