#	x509sak - The X.509 Swiss Army Knife white-hat certificate toolkit
#	Copyright (C) 2017-2017 Johannes Bauer
#
#	This file is part of x509sak.
#
#	x509sak is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	x509sak is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with x509sak; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import logging
from x509sak.SubprocessExecutor import SubprocessExecutor

class BaseAction(object):
	def __init__(self, cmdname, args):
		self._cmdname = cmdname
		self._args = args

		logging.root.setLevel(logging.DEBUG)
		formatter = logging.Formatter("{asctime} [{levelname:.1s}]: {name} {message}", style = "{")

		handler = logging.StreamHandler()
		if self._args.verbose:
			handler.setLevel(logging.DEBUG)
		else:
			handler.setLevel(logging.INFO)
		handler.setFormatter(formatter)
		logging.root.addHandler(handler)

		self._log = logging.getLogger("x509sak." + __class__.__name__)