import os
import sys
import re
import yaml as yml

from pathlib import Path
from loguru import logger
from subprocess import Popen, PIPE

class project:
	name 			 = None
	top  			 = None
	root 			 = None
	submodules = None

	## Constructor
	def __init__(self, src_file):
		if ('PROJ_DIR' in os.environ):
			self.root = Path(os.environ['PROJ_DIR'])
			logger.info(f"Project path is {os.environ['PROJ_DIR']}")
		else:
			logger.critical(f"Project path is not set, please launch configuration")
		print(self.root)
