#copyright ReportLab Europe Limited. 2000-2012
#see license.txt for license details
'''
Arciv Stream  ciphering
'''
__version__=''' $Id: arciv.py 3959 2012-09-27 14:39:39Z robin $ '''
from types import StringType
class ArcIV:
	'''
	performs 'ArcIV' Stream Encryption of S using key
	Based on what is widely thought to be RSA's ArcIV algorithm.
	It produces output streams that are identical.

	NB there is no separate decoder arciv(arciv(s,key),key) == s
	'''
	def __init__(self,key):
		self._key = key
		self.reset()

	def reset(self):
		'''restore the cipher to it's start state'''
		#Initialize private key, k With the values of the key mod 256.
		#and sbox With numbers 0 - 255. Then compute sbox
		key = self._key
		sbox = range(256)
		k = range(256)
		lk = len(key)
		for i in sbox:
			k[i] = ord(key[i % lk]) % 256

		#Re-order sbox using the private key, k.
		#Iterating each element of sbox re-calculate the counter j
		#Then interchange the elements sbox[a] & sbox[b]
		j = 0
		for i in xrange(256):
			j = (j+sbox[i]+k[i]) % 256
			sbox[i], sbox[j] = sbox[j], sbox[i]
		self._sbox, self._i, self._j = sbox, 0, 0

	def _encode(self, B):
		'''
		return the list of encoded bytes of B, B might be a string or a
		list of integers between 0 <= i <= 255
		'''
		sbox, i, j = self._sbox, self._i, self._j

		C = type(B) is StringType and map(ord,B) or B[:]
		n = len(C)
		p = 0
		while p<n:
			#update the variables i, j.
			self._i = i = (i + 1) % 256
			self._j = j = (j + sbox[i]) % 256
			#swap sbox[i] and sbox[j]
			sbox[i], sbox[j] = sbox[j], sbox[i]
			#overwrite the plaintext with the ciphered byte
			C[p] = C[p] ^ sbox[(sbox[i] + sbox[j]) % 256]
			p = p + 1
		return C

	def encode(self,S):
		'ArcIV encode string S'
		return "".join(map(chr,self._encode(S)))

_TESTS=[{
		'key': "\x01\x23\x45\x67\x89\xab\xcd\xef",
		'input': "\x01\x23\x45\x67\x89\xab\xcd\xef",
		'output': "\x75\xb7\x87\x80\x99\xe0\xc5\x96",
		},

		{
		'key': "\x01\x23\x45\x67\x89\xab\xcd\xef",
		'input': "\x00\x00\x00\x00\x00\x00\x00\x00",
		'output': "\x74\x94\xc2\xe7\x10\x4b\x08\x79",
		},

		{
		'key': "\x00\x00\x00\x00\x00\x00\x00\x00",
		'input': "\x00\x00\x00\x00\x00\x00\x00\x00",
		'output': "\xde\x18\x89\x41\xa3\x37\x5d\x3a",
		},

		{
		'key': "\xef\x01\x23\x45",
		'input': "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
		'output': "\xd6\xa1\x41\xa7\xec\x3c\x38\xdf\xbd\x61",
		},

		{
		'key': "\x01\x23\x45\x67\x89\xab\xcd\xef",
		'input': "\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\
\x01",
	'output': "\x75\x95\xc3\xe6\x11\x4a\x09\x78\x0c\x4a\xd4\
\x52\x33\x8e\x1f\xfd\x9a\x1b\xe9\x49\x8f\
\x81\x3d\x76\x53\x34\x49\xb6\x77\x8d\xca\
\xd8\xc7\x8a\x8d\x2b\xa9\xac\x66\x08\x5d\
\x0e\x53\xd5\x9c\x26\xc2\xd1\xc4\x90\xc1\
\xeb\xbe\x0c\xe6\x6d\x1b\x6b\x1b\x13\xb6\
\xb9\x19\xb8\x47\xc2\x5a\x91\x44\x7a\x95\
\xe7\x5e\x4e\xf1\x67\x79\xcd\xe8\xbf\x0a\
\x95\x85\x0e\x32\xaf\x96\x89\x44\x4f\xd3\
\x77\x10\x8f\x98\xfd\xcb\xd4\xe7\x26\x56\
\x75\x00\x99\x0b\xcc\x7e\x0c\xa3\xc4\xaa\
\xa3\x04\xa3\x87\xd2\x0f\x3b\x8f\xbb\xcd\
\x42\xa1\xbd\x31\x1d\x7a\x43\x03\xdd\xa5\
\xab\x07\x88\x96\xae\x80\xc1\x8b\x0a\xf6\
\x6d\xff\x31\x96\x16\xeb\x78\x4e\x49\x5a\
\xd2\xce\x90\xd7\xf7\x72\xa8\x17\x47\xb6\
\x5f\x62\x09\x3b\x1e\x0d\xb9\xe5\xba\x53\
\x2f\xaf\xec\x47\x50\x83\x23\xe6\x71\x32\
\x7d\xf9\x44\x44\x32\xcb\x73\x67\xce\xc8\
\x2f\x5d\x44\xc0\xd0\x0b\x67\xd6\x50\xa0\
\x75\xcd\x4b\x70\xde\xdd\x77\xeb\x9b\x10\
\x23\x1b\x6b\x5b\x74\x13\x47\x39\x6d\x62\
\x89\x74\x21\xd4\x3d\xf9\xb4\x2e\x44\x6e\
\x35\x8e\x9c\x11\xa9\xb2\x18\x4e\xcb\xef\
\x0c\xd8\xe7\xa8\x77\xef\x96\x8f\x13\x90\
\xec\x9b\x3d\x35\xa5\x58\x5c\xb0\x09\x29\
\x0e\x2f\xcd\xe7\xb5\xec\x66\xd9\x08\x4b\
\xe4\x40\x55\xa6\x19\xd9\xdd\x7f\xc3\x16\
\x6f\x94\x87\xf7\xcb\x27\x29\x12\x42\x64\
\x45\x99\x85\x14\xc1\x5d\x53\xa1\x8c\x86\
\x4c\xe3\xa2\xb7\x55\x57\x93\x98\x81\x26\
\x52\x0e\xac\xf2\xe3\x06\x6e\x23\x0c\x91\
\xbe\xe4\xdd\x53\x04\xf5\xfd\x04\x05\xb3\
\x5b\xd9\x9c\x73\x13\x5d\x3d\x9b\xc3\x35\
\xee\x04\x9e\xf6\x9b\x38\x67\xbf\x2d\x7b\
\xd1\xea\xa5\x95\xd8\xbf\xc0\x06\x6f\xf8\
\xd3\x15\x09\xeb\x0c\x6c\xaa\x00\x6c\x80\
\x7a\x62\x3e\xf8\x4c\x3d\x33\xc1\x95\xd2\
\x3e\xe3\x20\xc4\x0d\xe0\x55\x81\x57\xc8\
\x22\xd4\xb8\xc5\x69\xd8\x49\xae\xd5\x9d\
\x4e\x0f\xd7\xf3\x79\x58\x6b\x4b\x7f\xf6\
\x84\xed\x6a\x18\x9f\x74\x86\xd4\x9b\x9c\
\x4b\xad\x9b\xa2\x4b\x96\xab\xf9\x24\x37\
\x2c\x8a\x8f\xff\xb1\x0d\x55\x35\x49\x00\
\xa7\x7a\x3d\xb5\xf2\x05\xe1\xb9\x9f\xcd\
\x86\x60\x86\x3a\x15\x9a\xd4\xab\xe4\x0f\
\xa4\x89\x34\x16\x3d\xdd\xe5\x42\xa6\x58\
\x55\x40\xfd\x68\x3c\xbf\xd8\xc0\x0f\x12\
\x12\x9a\x28\x4d\xea\xcc\x4c\xde\xfe\x58\
\xbe\x71\x37\x54\x1c\x04\x71\x26\xc8\xd4\
\x9e\x27\x55\xab\x18\x1a\xb7\xe9\x40\xb0\
\xc0",
		},
	]

def encode(text, key):
	"One-line shortcut for making an encoder object"
	return ArcIV(key).encode(text)

def decode(text, key):
	"One-line shortcut for decoding"
	# yes, encode and decode are symmetric - see docstring
	return ArcIV(key).encode(text)

if __name__=='__main__':
	i = 0
	for t in _TESTS:
		o = ArcIV(t['key']).encode(t['input'])
		print 'Forward test %d %s!' %(i,o!=t['output'] and 'failed' or 'succeeded')
		o = ArcIV(t['key']).encode(t['output'])
		print 'Reverse test %d %s!' %(i,o!=t['input'] and 'failed' or 'succeeded')
		i += 1
