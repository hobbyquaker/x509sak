#	x509sak - The X.509 Swiss Army Knife white-hat certificate toolkit
#	Copyright (C) 2018-2018 Johannes Bauer
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

import enum
import collections
import pyasn1.codec.der.decoder
from pyasn1_modules import rfc2459, rfc2437
from x509sak.OID import OID, OIDDB
from x509sak.PEMDERObject import PEMDERObject
from x509sak.Tools import ASN1Tools, ECCTools
from x509sak.KeySpecification import KeySpecification, Cryptosystem

class PublicKey(PEMDERObject):
	_PEM_MARKER = "PUBLIC KEY"
	_ASN1_MODEL = rfc2459.SubjectPublicKeyInfo
	_ECPoint = collections.namedtuple("ECPoint", [ "curve", "x", "y" ])

	@property
	def keytype(self):
		return self._keytype

	@property
	def key(self):
		return self._key

	@property
	def keyspec(self):
		if self.keytype == Cryptosystem.RSA:
			return KeySpecification(cryptosystem = self.keytype, parameters = { "bitlen": self.key.n.bit_length() })
		elif self.keytype == Cryptosystem.ECC:
			return KeySpecification(cryptosystem = self.keytype, parameters = { "curve": self.key.curve })
		else:
			raise LazyDeveloperException(NotImplemented, self.keytype)

	def _post_decode_hook(self):
		alg_oid = OID.from_asn1(self.asn1["algorithm"]["algorithm"])
		if alg_oid not in OIDDB.KeySpecificationAlgorithms:
			raise UnknownAlgorithmException("Unable to determine public algorithm for OID %s." % (alg_oid))
		alg_name = OIDDB.KeySpecificationAlgorithms[alg_oid]
		self._keytype = Cryptosystem(alg_name)

		inner_key = ASN1Tools.bitstring2bytes(self.asn1["subjectPublicKey"])
		if self.keytype == Cryptosystem.RSA:
			(self._key, tail) = pyasn1.codec.der.decoder.decode(inner_key, asn1Spec = rfc2437.RSAPublicKey())
		elif self.keytype == Cryptosystem.ECC:
			(x, y) = ECCTools.decode_enc_pubkey(inner_key)
			(alg_oid, tail) = pyasn1.codec.der.decoder.decode(self.asn1["algorithm"]["parameters"])
			alg_oid = OID.from_asn1(alg_oid)
			if alg_oid not in OIDDB.EllipticCurves:
				raise UnknownAlgorithmException("Unable to determine curve name for curve OID %s." % (alg_oid))
			self._key = self._ECPoint(curve = OIDDB.EllipticCurves[alg_oid], x = x, y = y)
		else:
			raise LazyDeveloperException(NotImplemented, self.keytype)