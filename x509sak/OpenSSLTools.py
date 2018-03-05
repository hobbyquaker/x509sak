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

import tempfile
from x509sak.SubprocessExecutor import SubprocessExecutor

class OpenSSLTools(object):
	@classmethod
	def create_private_key(cls, filename, keyspec):
		if keyspec.cryptosystem == keyspec.Cryptosystem.RSA:
			cmd = [ "openssl", "genrsa", "-out", filename, str(keyspec.bitlen) ]
		elif keyspec.cryptosystem == keyspec.Cryptosystem.ECC:
			cmd = [ "openssl", "ecparam", "-name", keyspec.curve, "-genkey", "-out", filename ]
		else:
			raise Exception(NotImplemented)
		SubprocessExecutor.run(cmd)

	@classmethod
	def write_extension_file(cls, f, options = None, subject_alternative_dns_names = None, subject_alternative_ip_addresses = None):
		option_count = 0
		print("[req]", file = f)
		print("distinguished_name = default", file = f)
		print(file = f)
		print("[default]", file = f)
		if options is not None:
			for (key, value) in sorted(options.items()):
				print("%s = %s" % (key, value), file = f)
				option_count += 1

		alt_names = [ ]
		if subject_alternative_dns_names is not None:
			alt_names += [ "DNS:%s" % (value) for value in sorted(subject_alternative_dns_names) ]
		if subject_alternative_ip_addresses is not None:
			alt_names += [ "IP:%s" % (value) for value in sorted(subject_alternative_ip_addresses) ]
		if len(alt_names) > 0:
			print("subjectAltName = %s" % (",".join(alt_names)), file = f)
			option_count += 1
		f.flush()
		return option_count

	@classmethod
	def create_selfsigned_certificate(cls, private_key_filename, certificate_filename, subject_dn, validity_days, options = None, subject_alternative_dns_names = None, subject_alternative_ip_addresses = None, signing_hash = None, serial = None):
		with tempfile.NamedTemporaryFile("w", prefix = "config_", suffix = ".cnf") as f:
			cls.write_extension_file(f, options = options, subject_alternative_dns_names = subject_alternative_dns_names, subject_alternative_ip_addresses = subject_alternative_ip_addresses)
			cmd = [ "openssl", "req", "-new", "-x509", "-key", private_key_filename, "-days", str(validity_days), "-subj", subject_dn, "-config", f.name, "-extensions", "default", "-out", certificate_filename ]
			if signing_hash is not None:
				cmd += [ "-%s" % (signing_hash) ]
			if serial is not None:
				cmd += [ "-set_serial", "%d" % (serial) ]
			SubprocessExecutor.run(cmd)

	@classmethod
	def create_csr(cls, private_key_filename, csr_filename, subject_dn, options = None, subject_alternative_dns_names = None, subject_alternative_ip_addresses = None):
		with tempfile.NamedTemporaryFile("w", prefix = "config_", suffix = ".cnf") as f:
			option_count = cls.write_extension_file(f, options = options, subject_alternative_dns_names = subject_alternative_dns_names, subject_alternative_ip_addresses = subject_alternative_ip_addresses)
			if option_count > 0:
				cmd = [ "openssl", "req", "-new", "-key", private_key_filename, "-subj", subject_dn, "-config", f.name, "-reqexts", "default", "-out", csr_filename ]
			else:
				# If no options are present, OpenSSL will otherwise terminate
				# with "Error Loading extension section default"
				cmd = [ "openssl", "req", "-new", "-key", private_key_filename, "-subj", subject_dn, "-out", csr_filename ]
			SubprocessExecutor.run(cmd)