import pandas as pd
from kivy.app import App
from kivy.config import Config
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '600')

def solve(solvers,i,j,l,m):
    solve = solvers[i][j][l][m]
    if solve.value() is not None:
        return False

    disables = set()

    #group
    availables = []
    own_available = set(solve.available())
    for s in range(3):
        for t in range(3):
            if s == l and t == m:
                continue
            value = solvers[i][j][s][t].value()
            if value is not None:
                disables.add(value)
                own_available = own_available - set([value])
            else:
                availables.append(solvers[i][j][s][t].available())
    for ava in availables:
        own_available = own_available - set(ava)
        length = len(ava)
        count  = 0
        for rel in availables:
            if ava == rel:
                count = count + 1
        if count == length:
            for value in ava:
                disables.add(value)
    if len(own_available) == 1:
        solve.setValue(list(own_available)[0])
        return True

    #horizon i,l freeze
    availables = []
    own_available = set(solve.available())
    for s in range(3):
        for t in range(3):
            if s == j and t == m:
                continue
            value = solvers[i][s][l][t].value()
            if value is not None:
                disables.add(value)
                own_available = own_available - set([value])
            else:
                availables.append(solvers[i][s][l][t].available())
    for ava in availables:
        own_available = own_available - set(ava)
        length = len(ava)
        count  = 0
        for rel in availables:
            if ava == rel:
                count = count + 1
        if count == length:
            for value in ava:
                disables.add(value)
    if len(own_available) == 1:
        solve.setValue(list(own_available)[0])
        return True

    #vertical j,m freeze
    availables = []
    own_available = set(solve.available())
    for s in range(3):
        for t in range(3):
            if s == i and t == l:
                continue
            value = solvers[s][j][t][m].value()
            if value is not None:
                disables.add(value)
                own_available = own_available - set([value])
            else:
                availables.append(solvers[s][j][t][m].available())
    for ava in availables:
        own_available = own_available - set(ava)
        length = len(ava)
        count  = 0
        for rel in availables:
            if ava == rel:
                count = count + 1
        if count == length:
            for value in ava:
                disables.add(value)
    if len(own_available) == 1:
        solve.setValue(list(own_available)[0])
        return True
    
    solve.disable(disables)
    if len(solve.available()) == 1:
        val = solve.available()[0]
        solve.setValue(val)
        return True

    return False

class Solver_selector(GridLayout):
    def __init__(self,position):
        super(Solver_selector, self).__init__()
        self.register_event_type('on_selected') 
        self.padding = [2,2]
        self.btn = []
        self.selected_value = None
        self.selected = False
        self.grid_position = position
        for i in range(9):
            btn = Button(text=str(i+1))
            btn.bind(on_release=self.button_callback)
            self.btn.append(btn)
        self.build_selector()

    def on_selected(self, *args, **kwargs):
        pass

    def build_selector(self):
        self.clear_widgets()
        self.cols = 3
        self.rows = 3
        self.selected_value = None
        self.selected = False
        for btn in self.btn:
            btn.disabled = False
            self.add_widget(btn)

    def build_represent(self, value):
        self.clear_widgets()
        self.cols = 1
        self.rows = 1
        self.selected_value = value
        label = Label(text=str(value))
        self.add_widget(label)

    def button_callback(self,btn):
        if not btn.disabled :
            self.selected = True
            self.setValue(int(btn.text))
            self.dispatch('on_selected')
    
    def setValue(self,value):
        if value is None:
            self.build_selector()
        else:
            self.build_represent(value)
 
    def value(self):
        return self.selected_value

    def available(self):
        values = []
        if self.selected_value is None:
            for btn in self.btn:
                if not btn.disabled:
                    values.append(int(btn.text))
        else:
            values.append(self.selected_value)
        return values

    def disable(self,dsel):
        for i in dsel:
            self.btn[i-1].disabled = True

    def reset_solve(self):
        if self.selected:
            for btn in self.btn:
                btn.disabled = False
        else:
            self.clear_solve()

    def clear_solve(self):
        self.setValue(None)

class Solver_frame(GridLayout):
    def __init__(self):
        super(Solver_frame, self).__init__()
        self.cols = 3
        self.rows = 3
        self.solvers = []
        self.solvers_flat = []
        self.history = []

        for i in range(self.cols):
            jdim = []
            self.solvers.append(jdim)
            for j in range(self.rows):
                grid = GridLayout(cols=3,rows=3,padding=[3,3])
                self.add_widget(grid)
                ldim = []
                jdim.append(ldim)
                for l in range(grid.cols):
                    mdim = []
                    ldim.append(mdim)
                    for m in range(grid.rows):
                        btn = Solver_selector((i*3+l,j*3+m))
                        btn.bind(on_selected=self.change_select)
                        grid.add_widget(btn)
                        mdim.append(btn)
                        self.solvers_flat.append(btn)

    def solve(self):
        while True:
            update = False
            for i in range(self.cols):
                for j in range(self.rows):
                    for l in range(3):
                        for m in range(3):
                            update = update or solve(self.solvers,i,j,l,m)
            if update == False:
                break

    def reset_solve(self):
        for solver in self.solvers_flat:
            solver.reset_solve()

    def clear_solve(self, *args, **kwargs):
        for solver in self.solvers_flat:
            solver.clear_solve()

    def undo_solve(self, *args, **kwargs):
        solver = self.history.pop()
        if solver is not None:
            solver.clear_solve()
            self.reset_solve()
            self.solve()

    def load_solve(self, filename):
        if filename is not None:
            db = pd.read_csv(filename)
    
    def save_solve(self, filename):
        if filename is not None:
            db = pd.to_csv(filename)

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
        solver = Solver_frame()
        vb.add_widget(solver)
        btn = Button(text="Clear")
        btn.bind(on_release=solver.clear_solve)
        hb.add_widget(btn)
        btn = Button(text="Undo")
        btn.bind(on_release=solver.undo_solve)
        hb.add_widget(btn)
        btn = Button(text="Load")
        btn.bind(on_release=solver.load_solve)
        hb.add_widget(btn)
        btn = Button(text="Save")
        btn.bind(on_release=solver.save_solve)
        hb.add_widget(btn)
        return vb

if __name__ == '__main__':
    SolverApp().run()
