"""
these models define a template for a given program.
A program template consists of weeks, which contain days, which contain a sequence
of tasks to execute on a given day. The tasks specify the lift or cardio thing, which contain
task-type specific instructions for it such as reps and sets or distance.
"""
from liftz._models._template._exercise import *
from liftz._models._template._program import *
