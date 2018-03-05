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

import hashlib
import pyasn1.codec.der.decoder
from .Tools import PEMDataTools

class PEMDERObject(object):
	_PEM_MARKER = None
	_ASN1_MODEL = None

	def __init__(self, der_data, source = None):
		assert(isinstance(der_data, bytes))
		self._der_data = der_data
		(self._asn1, tail) = pyasn1.codec.der.decoder.decode(der_data, asn1Spec = self._ASN1_MODEL)
		if len(tail) > 0:
			raise Exception("Trailing DER data found.")
		self._hashval = hashlib.sha256(self._der_data).digest()
		self._source = source

	@property
	def source(self):
		return self._source

	@property
	def hashval(self):
		return self._hashval

	@property
	def der_data(self):
		return self._der_data

	@property
	def asn1(self):
		return self._asn1

	@classmethod
	def from_pem_data(cls, pem_data, source = None):
		if cls._PEM_MARKER is None:
			raise Exception(NotImplemented)

		result = [ ]
		for (number, der_data) in enumerate(PEMDataTools.pem2data(pem_data, cls._PEM_MARKER), 1):
			if source is None:
				pem_source = None
			else:
				if number == 1:
					pem_source = source
				else:
					pem_source = "%s #%d" % (source, number)
			instance = cls(der_data, source = pem_source)
			result.append(instance)
		return result

	def to_pem_data(self):
		if self._PEM_MARKER is None:
			raise Exception(NotImplemented)
		return PEMDataTools.data2pem(self.der_data, self._PEM_MARKER)

	@classmethod
	def read_derfile(cls, filename):
		with open(filename, "rb") as f:
			return cls(f.read(), source = filename)

	def write_derfile(self, filename):
		with open(filename, "wb") as f:
			f.write(self.der_data)

	@classmethod
	def read_pemfile(cls, filename):
		with open(filename, "r") as f:
			return cls.from_pem_data(f.read(), source = filename)

	def write_pemfile(self, filename):
		with open(filename, "w") as f:
			print(self.to_pem_data(), file = f)

	def __eq__(self, other):
		return (type(self) == type(other)) and (self.der_data == other.der_data)

	def __neq__(self, other):
		return not (self == other)

	def __lt__(self, other):
		return (type(self) == type(other)) and (self.der_data < other.der_data)

	def __hash__(self):
		return hash(self._hashval)