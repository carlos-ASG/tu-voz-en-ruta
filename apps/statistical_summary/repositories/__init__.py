"""
Repositories para acceso a datos.

Los repositories encapsulan todas las queries a la base de datos,
proporcionando una capa de abstracción entre la lógica de negocio
y el ORM de Django.
"""
from . import complaint_repository
from . import survey_repository
from . import question_repository
from . import transport_repository

__all__ = [
    'complaint_repository',
    'survey_repository',
    'question_repository',
    'transport_repository',
]
