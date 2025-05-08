# test_mlModelSaver.py

import sys
import os


sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..'
        )
    )
)


from jrjModelRegistry import JrjMlModelRegistry

def test_test():
    jrjMlReg = JrjMlModelRegistry({})
    res = jrjMlReg.test(1)
    assert res == 1
