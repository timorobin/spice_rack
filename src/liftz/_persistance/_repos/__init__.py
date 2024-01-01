from liftz._persistance._repos._record_base import *
from liftz._persistance._repos._strength_exercise import *
from liftz._persistance._repos._program_template import *
# from liftz._persistance._repos._program_active import *
# from liftz._persistance._repos._program_finalized import *
from liftz._persistance._repos._user import *


# for tortoise
__models__ = [
    UserRecord,
    StrengthExerciseRecord,

    ProgramTemplateIndividualSet,
    ProgramTemplateRecord
]
