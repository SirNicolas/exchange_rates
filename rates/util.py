import binascii
import datetime
import hashlib
import os

from aiohttp import ClientSession

iterations = 100000
hash_name = 'sha512'
password_encode = 'utf-8'
salt_encode = 'ascii'


def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode(salt_encode)
    pwdhash = hashlib.pbkdf2_hmac(
        hash_name,
        password.encode(password_encode),
        salt,
        iterations
    )
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode(salt_encode)


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac(
        hash_name,
        provided_password.encode(password_encode),
        salt.encode(salt_encode),
        iterations
    )
    pwdhash = binascii.hexlify(pwdhash).decode(salt_encode)
    return pwdhash == stored_password


def timestamp_to_date(timestamp: int) -> datetime:
    """ Convert timestamp im ms to datetime format """
    return datetime.datetime.fromtimestamp(timestamp / 1000)


async def request(url):
    async with ClientSession(raise_for_status=True) as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
