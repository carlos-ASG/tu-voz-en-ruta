"""Admin package initializer: importa los módulos de admin para que Django los cargue.

Cada submódulo usa el decorador @admin.register, por lo que basta importarlos
para que sus clases se registren en el sitio de admin.
"""
from . import question_admin  # noqa: F401
from . import question_option_admin  # noqa: F401
from . import answer_admin  # noqa: F401
from . import survey_submission_admin  # noqa: F401
from . import complaint_reason_admin  # noqa: F401
from . import complaint_admin  # noqa: F401
