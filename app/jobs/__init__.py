from .index import job_registry

# Import all job modules to ensure they register themselves
from . import print_job
from . import mitsui_job

__all__ = ['job_registry']