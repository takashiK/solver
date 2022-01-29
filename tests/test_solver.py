import pytest,glob,filecmp
from solver import Number_grid

def solve_check(filepath):
    solve_file = "./tst_solve.csv"
    solver = Number_grid()
    solver.load(filepath)
    solver.store(solve_file)
    assert filecmp.cmp(filepath,solve_file,False)


def test_sudoku_samples():
    test_files = glob.glob("./tests/data/*.tst")
    for filepath in test_files:
        solve_check(filepath)
