import asyncio
import threading
import sys
from aiosmtpd.controller import Controller

class MailHandler:
    def __init__(self, return_message):
        self._return_message = return_message
        print(self._return_message)
    
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        print('Message from %s' % envelope.mail_from)
        print('Message for %s' % envelope.rcpt_tos)
        print('Message data:\n')
        for ln in envelope.content.decode('utf8', errors='replace').splitlines():
            print(f'> {ln}'.strip())
        print()
        print('End of message')
        return self._return_message

def main(return_message):
    controller = Controller(MailHandler(return_message))
    controller.port = 25
    controller.start()
    print(controller.port)

def InterruptableEvent():
    e = threading.Event()

    def patched_wait():
        while not e.is_set():
            e._wait(3)

    e._wait = e.wait
    e.wait = patched_wait
    return e
    
if __name__ == '__main__':
    return_message = '250 Message accepted for delivery'
    if len(sys.argv) > 0 and not sys.argv[1].startswith('-'):
        return_message = sys.argv[1]

    main(return_message)
    event = InterruptableEvent()
    
    try:
        event.wait()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)