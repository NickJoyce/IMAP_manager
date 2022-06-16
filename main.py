from imaplib import IMAP4_SSL
from email import message
from email.parser import BytesParser
from email.policy import default


class MailBox():
    def __init__(self, host: str, login: str, password: str):
        self.host = host
        self.login = login
        self.password = password
        self.imap = IMAP4_SSL(self.host)
        self.login_status = self.imap.login(self.login, self.password)
        self.numbered_folders: dict = {n+1:folder.decode().split()[-1] for n, folder in enumerate(self.imap.list()[1])}

    def show_folder_list(self):
        """display numbered mailbox folders"""
        for n, i in enumerate(self.imap.list()[1]):
            print(f'[{n+1}]> {i.decode()}')

    def select_folder_by_num(self, num):
        """select mailbox folder by num in numbered_folders dict"""
        self.imap.select(self.numbered_folders[num])
        print(f"[ {self.numbered_folders[num]} ] is selected")

    @staticmethod
    def formating_msg_ids(msg_ids):
        return msg_ids[0].split()

    def search_all(self) -> list:
        """returns all message ids of selected folder"""
        status, msg_ids = self.imap.search(None, 'ALL')
        return self.formating_msg_ids(msg_ids)

    def search_before(self, date: str) -> list:
        """returns the message IDs of the selected folder up to the specified date"""
        status, msg_ids = self.imap.search(None, f'(BEFORE "{date}")')
        return self.formating_msg_ids(msg_ids)

    def search_since(self, date: str) -> list:
        """returns the message IDs of the selected folder since the specified date"""
        status, msg_ids = self.imap.search(None, f'(SINCE "{date}")')
        return self.formating_msg_ids(msg_ids)

    def search_on(self, date: str) -> list:
        """returns the message IDs of the selected folder on the specified date"""
        status, msg_ids = self.imap.search(None, f'(ON "{date}")')
        return self.formating_msg_ids(msg_ids)

    def search_date_range(self, since_date: str, before_date: str) -> list:
        """returns the message IDs of the selected folder inside the date range"""
        status, msg_ids = self.imap.search(None, f'(SINCE "{since_date}" BEFORE "{before_date}")')
        return self.formating_msg_ids(msg_ids)

    def search_subject(self, search_request: str) -> list:
        """returns the message IDs of the selected folder where the message subject contains search request"""
        status, msg_ids = self.imap.search('utf-8', f'(SUBJECT "{search_request}")'.encode('utf-8'))
        return self.formating_msg_ids(msg_ids)

    def search_body(self, search_request: str) -> list:
        """returns the message IDs of the selected folder where the message body contains search request """
        status, msg_ids = self.imap.search('utf-8', f'(BODY "{search_request}")'.encode('utf-8'))
        return self.formating_msg_ids(msg_ids)

    def search_text(self, search_request: str) -> list:
        """returns the message IDs of the selected folder where msg subject or msg body contains search request"""
        status, msg_ids = self.imap.search('utf-8', f'(TEXT "{search_request}")'.encode('utf-8'))
        return self.formating_msg_ids(msg_ids)

    def search_from(self, address: str) -> list:
        """returns the message IDs of the selected folder where FROM header is the address"""
        status, msg_ids = self.imap.search(None, f'FROM {address}')
        return self.formating_msg_ids(msg_ids)

    def search_to(self, address: str) -> list:
        """returns the message IDs of the selected folder where TO header is the address"""
        status, msg_ids = self.imap.search(None, f'TO {address}')
        return self.formating_msg_ids(msg_ids)

    def search_seen(self) -> list:
        status, msg_ids = self.imap.search(None, "SEEN")
        return self.formating_msg_ids(msg_ids)

    def search_unseen(self) -> list:
        status, msg_ids = self.imap.search(None, "UNSEEN")
        return self.formating_msg_ids(msg_ids)

    def get_msg_by_uid(self, uid: str) -> message:
        """get message data, parse it, return object message from email module"""
        status2, data = self.imap.fetch(uid, '(RFC822)')
        parser = BytesParser(policy=default)
        msg = parser.parsebytes(data[0][1])
        return msg

    def logout(self):
        self.imap.logout()


if __name__ =='__main__':
    # create mailbox object
    print('-'*30, 'connection and login test','-'*30,)
    mailbox = MailBox("imap.yandex.ru", 'login', 'password')

    # display numbered folder list
    print('\n', '-'*30, 'show_folder_list method test','-'*30,)
    mailbox.show_folder_list()

    # display the results of work search methods
    print('\n','-'*30, 'search methods tests','-'*30,)
    mailbox.select_folder_by_num(1)
    for k, v in {'search_all:': mailbox.search_all(),
                 'search_before:': mailbox.search_before('1-Jun-2022'),
                 'search_since:': mailbox.search_since('1-Jun-2022'),
                 'search_on:': mailbox.search_on('14-Jun-2022'),
                 'search_date_range:': mailbox.search_date_range('1-Jun-2022', '15-Jun-2022'),
                 'search_subject:': mailbox.search_subject('Похолодало за окном?'),
                 'search_body:': mailbox.search_body('можете'),
                 'search_text:': mailbox.search_text('приобрести'),
                 'search_from:': mailbox.search_from('noreply@id.yandex.ru'),
                 'search_to:': mailbox.search_to('elenkhomchenk@yandex.ru'),
                 'search_seen:': mailbox.search_seen(),
                 'search_unseen:': mailbox.search_unseen()
                 }.items():
        print(k, v)

    # parsing and handling messages
    print('\n','-'*30, 'get_msg_by_uid method test','-'*30,)
    mailbox.select_folder_by_num(1)
    for i in mailbox.search_all():
        msg = mailbox.get_msg_by_uid(i)

        # display message subject
        print(f"\n[uid: {int(i)}]>>>", msg['Subject'], f"<<<[uid: {int(i)}]")

        # display content type of the message
        print('-' * 30, f'CONTENT TYPES', '-' * 30)
        for n, part in enumerate(msg.walk()):
            print(f"[part №:{n+1}]: ", part.get_content_type())

        # display the parts of the payload where content type 'text/html' or 'text/plain'
        for n, part in enumerate(msg.walk()):
            print('-' * 30, f'[part №:{int(n+1)}]', '-' * 30)
            if part.get_content_type() in ['text/html', 'text/plain']:
                print(part.get_payload(decode='utf-8').decode('utf-8'))
            else:
                print('...')

    mailbox.logout()