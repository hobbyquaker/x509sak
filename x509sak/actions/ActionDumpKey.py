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

from x509sak.BaseAction import BaseAction
from x509sak.RSAPrivateKey import RSAPrivateKey
from x509sak.ECPrivateKey import ECPrivateKey
from x509sak.PublicKey import PublicKey
from x509sak.KeySpecification import Cryptosystem

class ActionDumpKey(BaseAction):
	def __init__(self, cmdname, args):
		BaseAction.__init__(self, cmdname, args)
		if self._args.public_key:
			key = PublicKey.read_pemfile(self._args.key_filename)[0]
			if key.cryptosystem == Cryptosystem.RSA:
				print ("# %d bit RSA public key (ID %s)" % (key.n.bit_length(), key.keyid().hex()))
				print("n = 0x%x" % (key.n))
				print("e = 0x%x" % (key.e))
			elif key.cryptosystem == Cryptosystem.ECC:
				print("# ECC key on %s (key ID %s)" % (key.curve, key.keyid().hex()))
				print("curve_name = \"%s\"" % (key.curve))
				print("(x, y) = (0x%x, 0x%x)" % (key.x, key.y))
			else:
				raise Exception(NotImplemented)
		else:
			if self._args.key_type == "rsa":
				key = RSAPrivateKey.read_pemfile(self._args.key_filename)[0]
				print ("# %d bit RSA private key (ID %s)" % (key.n.bit_length(), key.pubkey.keyid().hex()))
				print("p = 0x%x" % (key.p))
				print("q = 0x%x" % (key.q))
				print("n = p * q")
				print("e = 0x%x" % (key.e))
				print("d = 0x%x" % (key.d))
			elif self._args.key_type == "ecc":
				key = ECPrivateKey.read_pemfile(self._args.key_filename)[0]
				print("# ECC private key on %s (key ID %s)" % (key.curve, key.pubkey.keyid().hex()))
				print("curve_name = \"%s\"" % (key.curve))
				print("d = 0x%x" % (key.d))
				print("(x, y) = (0x%x, 0x%x)" % (key.x, key.y))

			else:
				raise Exception(NotImplemented)
