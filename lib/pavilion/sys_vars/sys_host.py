import subprocess
from .base_classes import SystemPlugin


class SystemHost(SystemPlugin):

    def __init__(self):
        super().__init__(
            name='sys_host',
            description="The system (kickoff) hostname.",
            priority=self.PRIO_CORE)

    def _get( self):
        """Base method for determining the system name."""

        name = subprocess.check_output(['hostname', '-s'])
        return name.strip().decode('UTF-8')
