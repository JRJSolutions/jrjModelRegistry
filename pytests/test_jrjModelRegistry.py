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


def test_test():
    from jrjModelRegistry import JrjMlModelRegistry
    jrjMlReg = JrjMlModelRegistry({})
    res = jrjMlReg.test(1)
    assert res == 1
