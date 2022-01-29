import pytest

from solver import Solver,Number_grid

def available_singleton(selectors,i,j,l,m):
    number = selectors[i][j][l][m]
    if number.value() is not None:
        return [number.value()]

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

    available = set([1,2,3,4,5,6,7,8,9])
    return list(available - disables)

def available_uniqueness(selectors,i,j,l,m):
    number = selectors[i][j][l][m]
    if number.value() is not None:
        return [number.value()]

    disables = set()
    own_availables = set()

    #group
    availables = []
    own_available = set(number.available())
    for s in range(3):
        for t in range(3):
            if s == l and t == m:
                continue
            value = selectors[i][j][s][t].value()
            if value is not None:
                own_available = own_available - set([value])
            else:
                availables.append(selectors[i][j][s][t].available())
    for ava in availables:
        own_available = own_available - set(ava)

    own_availables = own_availables | own_available

    #horizon i,l freeze
    availables = []
    own_available = set(number.available())
    for s in range(3):
        for t in range(3):
            if s == j and t == m:
                continue
            value = selectors[i][s][l][t].value()
            if value is not None:
                own_available = own_available - set([value])
            else:
                availables.append(selectors[i][s][l][t].available())
    for ava in availables:
        own_available = own_available - set(ava)

    own_availables = own_availables | own_available

    #vertical j,m freeze
    availables = []
    own_available = set(number.available())
    for s in range(3):
        for t in range(3):
            if s == i and t == l:
                continue
            value = selectors[s][j][t][m].value()
            if value is not None:
                own_available = own_available - set([value])
            else:
                availables.append(selectors[s][j][t][m].available())
    for ava in availables:
        own_available = own_available - set(ava)

    own_availables = own_availables | own_available

    if len(own_availables) == 1:
        return list(own_availables)
    return [1,2,3,4,5,6,7,8,9]

def available_number_group(selectors,i,j,l,m):
    number = selectors[i][j][l][m]
    if number.value() is not None:
        return [number.value()]

    disables = set()

    #group
    availables = []
    for s in range(3):
        for t in range(3):
            if s == l and t == m:
                continue
            value = selectors[i][j][s][t].value()
            if value is not None:
                continue
            else:
                availables.append(selectors[i][j][s][t].available())
    for ava in availables:
        length = len(ava)
        count  = 0
        for rel in availables:
            if ava == rel:
                count = count + 1
        if count == length:
            for value in ava:
                disables.add(value) # number group

    #horizon i,l freeze
    availables = []
    for s in range(3):
        for t in range(3):
            if s == j and t == m:
                continue
            value = selectors[i][s][l][t].value()
            if value is not None:
                continue
            else:
                availables.append(selectors[i][s][l][t].available())
    for ava in availables:
        length = len(ava)
        count  = 0
        for rel in availables:
            if ava == rel:
                count = count + 1
        if count == length:
            for value in ava:
                disables.add(value)

    #vertical j,m freeze
    availables = []
    for s in range(3):
        for t in range(3):
            if s == i and t == l:
                continue
            value = selectors[s][j][t][m].value()
            if value is not None:
                continue
            else:
                availables.append(selectors[s][j][t][m].available())
    for ava in availables:
        length = len(ava)
        count  = 0
        for rel in availables:
            if ava == rel:
                count = count + 1
        if count == length:
            for value in ava:
                disables.add(value)
    
    old_availables = number.available()
    number.disable(disables)
    if len(number.available()) == 1:
        val = number.available()[0]
        number.setValue(val)

    available = set([1,2,3,4,5,6,7,8,9])
    return list(available - disables)

def available_uniqueness_line(selectors,i,j,l,m):
    return []

def available_uniqueness_grid(selectors,i,j,l,m):
    return []

def test_solver_singleton():
    solver = Solver()
    features = solver.get_features()
    for feat in features:
        if feat == 'singleton':
            features[feat] = True
        else:
            features[feat] = False
    solver.set_features(features)
    grid = Number_grid()
    grid.selectors[0][0][0][1].setValue(5)
    grid.selectors[0][1][0][1].setValue(6)
    grid.selectors[0][1][2][2].setValue(9)
    grid.selectors[1][0][2][0].setValue(1)
    grid.selectors[1][1][1][0].setValue(4)

    for i in range(3):
        for j in range(3):
            for l in range(3):
                for m in range(3):
                    solver.single_solve(grid.selectors,i,j,l,m)
                    assert grid.selectors[i][j][l][m].available() == available_singleton(grid.selectors,i,j,l,m)


def test_solver_uniqueness():
    solver = Solver()
    features = solver.get_features()
    for feat in features:
        if feat == 'uniqueness':
            features[feat] = True
        else:
            features[feat] = False
    solver.set_features(features)
    grid = Number_grid()

    count = 0
    for j in range(3):
        for m in range(3):
            count = count + 1
            if count != 4:
                grid.selectors[0][j][0][m].setValue(count)

    count = 1
    for j in range(3):
        for m in range(3):
            count = count + 1
            if count < 10 or count != 5:
                grid.selectors[1][j][1][m].setValue(count)

    grid.selectors[0][1][1][0].setValue(1)
    grid.selectors[0][1][2][0].setValue(2)
    grid.selectors[1][1][0][0].setValue(3)
    grid.selectors[1][1][2][0].setValue(8)
    grid.selectors[2][1][0][0].setValue(7)
    grid.selectors[2][1][1][0].setValue(6)
    grid.selectors[2][1][2][0].setValue(9)

    for i in range(3):
        for j in range(3):
            for l in range(3):
                for m in range(3):
                    solver.single_solve(grid.selectors,i,j,l,m)
                    selector = grid.selectors[i][j][l][m]
                    assert grid.selectors[i][j][l][m].available() == available_uniqueness(grid.selectors,i,j,l,m)

def test_solver_number_group():
    solver = Solver()
    features = solver.get_features()
    for feat in features:
        if feat == 'number_group':
            features[feat] = True
        else:
            features[feat] = False
    solver.set_features(features)
    grid = Number_grid()
    grid.selectors[0][0][0][1].disable([3,4,5,6,7,8,9])
    grid.selectors[0][0][0][2].disable([3,4,5,6,7,8,9])

    grid.selectors[1][1][0][1].disable([1,2,5,6,7,8,9])
    grid.selectors[1][1][1][1].disable([1,2,5,6,7,8,9])

    grid.selectors[2][2][0][0].disable([1,2,3,4,5,9])
    grid.selectors[2][2][1][1].disable([1,2,3,4,5,9])
    grid.selectors[2][2][2][2].disable([1,2,3,4,5,9])

    for i in range(3):
        for j in range(3):
            for l in range(3):
                for m in range(3):
                    if (i,j,l,m) == (0,0,0,1) or (i,j,l,m) == (0,0,0,2):
                        continue
                    elif (i,j,l,m) == (1,1,0,1) or (i,j,l,m) == (1,1,1,1):
                        continue
                    elif (i,j,l,m) == (2,2,0,0) or (i,j,l,m) == (2,2,1,1) or (i,j,l,m) == (2,2,2,2):
                        continue
                    else:
                        solver.single_solve(grid.selectors,i,j,l,m)
                        assert grid.selectors[i][j][l][m].available() == available_number_group(grid.selectors,i,j,l,m)

def test_solver_uniqueness_line():
    pass

def test_solver_uniqueness_grid():
    pass

def test_solver_auto_selection():
    pass
