from trezor import ui
from trezor.utils import unimport


@unimport
async def layout_cipher_key_value(session_id, msg):
    from trezor.messages.CipheredKeyValue import CipheredKeyValue
    from ..common import seed
    from trezor.crypto.hashlib import sha512
    from trezor.crypto import hmac
    from trezor.crypto.aes import AES_CBC_Encrypt, AES_CBC_Decrypt

    if len(msg.value) % 16 > 0:
        raise ValueError('Value length must be a multiple of 16')

    ui.display.clear()
    ui.display.text(10, 30, 'CipherKeyValue',
                    ui.BOLD, ui.LIGHT_GREEN, ui.BLACK)
    ui.display.text(10, 60, msg.key, ui.MONO, ui.WHITE, ui.BLACK)

    node = await seed.get_node(session_id, msg.address_n)
    seckey = node.private_key()

    data = msg.key
    data += 'E1' if msg.ask_on_encrypt else 'E0'
    data += 'D1' if msg.ask_on_decrypt else 'D0'
    data = hmac.new(seckey, data, sha512).digest()
    key = data[:32]
    if msg.iv and len(msg.iv) == 16:
        iv = msg.iv
    else:
        iv = data[32:48]

    if msg.encrypt:
        aes = AES_CBC_Encrypt(key=key, iv=iv)
    else:
        aes = AES_CBC_Decrypt(key=key, iv=iv)

    value = aes.update(msg.value)

    return CipheredKeyValue(value=value)