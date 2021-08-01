from os.path import join, exists, splitext, isfile
from os import listdir
from nltk.corpus import stopwords
import re
import pickle
import string

import spacy
import gensim


import nltk
nltk.download('punkt')
nltk.download('stopwords')


def lemmatization(text, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']):
    nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    doc = nlp(text)
    new_text = []
    for token in doc:
        if token.pos_ in allowed_postags:
            new_text.append(token.lemma_)
    final = " ".join(new_text)
    return final


class Email:
    def __init__(self) -> None:
        self.to = []
        self.From = ''
        self.date = ''
        self.cc = []
        self.bcc = []
        self.subject = ''
        self.body = []
        self.file = ''

    def __str__(self) -> str:
        return ''.join(("File: {0}\n".format(self.file),
                        "From: {0}\n".format(self.From),
                        "To: {0}\n".format(self.to),
                        "Date: {0}\n".format(self.date),
                        "Cc: {0}\n".format(self.cc),
                        "Bcc: {0}\n".format(self.bcc),
                        "Subject: {0}\n".format(self.subject),
                        "Body:\n",
                        "".join(self.body)))

    def get_body_str(self) -> str:
        return ''.join(self.body)

    def get_body_bow(self):
        return self.bow

    def get_body_processed(self):
        return self.body_processed

    def set_body_bow(self, bow):
        self.bow = bow

    def set_body(self, body):
        self.body = body
        self.process_body()

    def process_body(self):
        body_processed = self.get_body_str()

        # 1. remove punctuation
        exclude = set(string.punctuation)
        body_processed = ''.join(
            ch for ch in body_processed if ch not in exclude)

        # 2. lemmatize
        body_processed = lemmatization(body_processed)

        # 3. pre_process
        body_processed = gensim.utils.simple_preprocess(
            body_processed, deacc=True)

        # 4. make all words lower case
        body_processed = [word.lower() for word in body_processed]

        # 5. remove stop words
        stop_words = set(stopwords.words('english'))
        body_processed = [
            word for word in body_processed if word not in stop_words]

        # 6. remove words with any digits
        body_processed = [word for word in body_processed if not any(
            c.isdigit() for c in word)]

        # 7. remove words of 1 or 2 chars
        body_processed = [word for word in body_processed if len(word) > 2]

        # 8. remove custom stop words
        custom_stop_words = ['www', 'http', 'com']
        body_processed = [
            word for word in body_processed if word not in custom_stop_words]

        # 9. remove duplicates
        body_processed = list(set(body_processed))

        self.body_processed = body_processed


class Person:
    def __init__(self, sname, name, email1, email2) -> None:
        self.sname = sname
        self.name = name
        self.email1 = email1
        self.email2 = email2
        self.inbox = []
        self.deleted_mail = []

    def set_inbox(self, inbox):
        self.inbox = inbox

    def set_deleted_mail(self, deleted_mail):
        self.deleted_mail = deleted_mail

    def set_inbox_mail(self, inbox_mail):
        self.inbox_mail = inbox_mail

    def get_deleted_mail(self):
        return self.deleted_mail

    def get_inbox_mail(self):
        return self.inbox_mail

    def get_deleted_mail_count(self):
        return len(self.deleted_mail)

    def get_inbox_mail_count(self):
        return len(self.inbox_mail)

    def get_total_mail_count(self):
        return self.get_inbox_mail_count() + self.get_deleted_mail_count()

    def __str__(self):
        return 'sname: {0}, name: {1}, email1: {2}, email2: {3}'.format(self.sname, self.name, self.email1, self.email2)


class Dataset:
    def __init__(self) -> None:
        self.all = []
        self.dict = None

    @staticmethod
    def parse_dataset(dataset_path, inboxes):
        dataset = Dataset()
        dataset.parse(dataset_path, inboxes)
        return dataset

    @staticmethod
    def load_processed_dataset(processed_dataset_path, include_filter):
        dataset = Dataset()
        for f in listdir(processed_dataset_path):
            if splitext(f)[0] in include_filter:
                with open(join(processed_dataset_path, f), 'rb') as processed_dataset_file:
                    dataset.all.append(pickle.load(processed_dataset_file))

        return dataset

    def save_processed_dataset(self, processed_dataset_path):
        print('saving processed data...')
        for p in self.all:
            print('saving {0}...'.format(p.sname))
            with open(join(processed_dataset_path, p.sname + '.pkl'), 'wb') as processed_dataset_file:
                pickle.dump(p, processed_dataset_file)
        print('done saving processed data!')

    def save_dictionary(self, processed_dataset_path):
        print('saving dictionary...')
        with open(join(processed_dataset_path, 'word-dict.pkl'), 'wb') as word_dict_file:
            pickle.dump(self.dict, word_dict_file)
        print('done saving dictionary!')

    def load_dictionary(self, processed_dataset_path):
        print('loading dictionary...')
        with open(join(processed_dataset_path, 'word-dict.pkl'), 'rb') as word_dict_file:
            self.dict = pickle.load(word_dict_file)
        print('done loading dictionary!')

    def get_individuals_count(self):
        return len(self.all)

    def get_mails_count(self):
        mails_count = 0
        for p in self.all:
            mails_count += p.get_total_mail_count()
        return mails_count

    def get_all(self):
        return self.all

    def parse(self, dataset_path, include_filter):

        for f in listdir(dataset_path):

            if f in include_filter:

                person = self.get_person(dataset_path, f)

                deleted_mail = self.get_mails(
                    dataset_path, f, 'deleted_items', 200)
                person.set_deleted_mail(deleted_mail)

                inbox_mail = self.get_mails(dataset_path, f, 'inbox', 200)
                person.set_inbox_mail(inbox_mail)

                self.all.append(person)

    def get_mails(self, dataset_path, f, folder, maxl):

        emails = []
        mails_path = join(dataset_path, f, folder)
        processed_count = 0

        if exists(mails_path):
            for s_mail_path in listdir(mails_path):
                if processed_count == maxl:
                    break

                if isfile(join(mails_path, s_mail_path)):
                    s_mail_file = open(join(mails_path, s_mail_path), "r")
                    s_mail_text = s_mail_file.readlines()

                    email = Email()
                    email_body = []
                    email.file = s_mail_path
                    email_body_started = False
                    reading_section = ''
                    # process headers
                    for line in s_mail_text:
                        if email_body_started:
                            email_body.append(line)
                        elif line.startswith('Date:'):
                            email.date = line.split(" ", 1)[1].strip()
                        elif line.startswith('From:'):
                            email.From = line.split(" ", 1)[1].strip()
                        elif line.startswith('To:'):
                            emailTo = line.split(" ", 1)[1].strip()
                            email.to = [x.strip() for x in emailTo.split(',')]
                            reading_section = 'to'
                        elif line.startswith('Subject:'):
                            email.subject = line.split(" ", 1)[1].strip()
                            reading_section = ''
                        elif line.startswith('Cc:'):
                            emailCc = line.split(" ", 1)[1].strip()
                            email.cc = [x.strip() for x in emailCc.split(',')]
                        elif line.startswith('Bcc:'):
                            emailBcc = line.split(" ", 1)[1].strip()
                            email.bcc = [x.strip()
                                         for x in emailBcc.split(',')]
                        elif reading_section == 'to':
                            moreTo = line.strip()
                            moreTo = [x.strip() for x in moreTo.split(',')]
                            email.to += moreTo
                        elif line in ['\n', '\r\n']:
                            email_body_started = True

                    email.set_body(email_body)
                    emails.append(email)
                    processed_count += 1
        else:
            print('path is not found'.format(mails_path))

        return emails

    def get_person(self, dataset_path, f):

        sname = f
        name = ''
        email1 = ''
        email2 = ''

        # find name and 1st email
        if exists(join(dataset_path, f, 'sent_items')):

            for s_mail_path in listdir(join(dataset_path, f, 'sent_items')):
                s_mail_file = open(
                    join(dataset_path, f, 'sent_items', s_mail_path), "r")
                s_mail_text = s_mail_file.readlines()

                for line in s_mail_text:
                    if line.startswith('X-From:'):
                        name = line.split(" ", 1)[1].strip()
                        name = re.sub('<.*?>', '',  name).strip()
                    if line.startswith('From:'):
                        email1 = line.split(" ", 1)[1].strip()
                    if name != '' and email1 != '':
                        break

                if name != '' and email1 != '':
                    break

        # override name if found here and take the 2nd email
        if exists(join(dataset_path, f, '_sent_mail')):

            for s_mail_path in listdir(join(dataset_path, f, '_sent_mail')):
                s_mail_file = open(
                    join(dataset_path, f, '_sent_mail', s_mail_path), "r")
                s_mail_text = s_mail_file.readlines()

                for line in s_mail_text:
                    if line.startswith('X-From:'):
                        name = line.split(" ", 1)[1].strip()
                        name = re.sub('<.*?>', '',  name).strip()
                    if line.startswith('From:'):
                        email2 = line.split(" ", 1)[1].strip()
                    if name != '' and email2 != '':
                        break

                if name != '' and email2 != '':
                    break

        return Person(sname, name, email1, email2)

    def generate_dict(self):
        print('new generating dict...')

        if len(self.all) == 0:
            print("Can't generate dict .. no data in the dataset!")

        all_inboxes = [mail.get_body_processed()
                       for p in self.all for mail in p.get_inbox_mail()]

        all_deleted = [mail.get_body_processed()
                       for p in self.all for mail in p.get_deleted_mail()]

        all_mail = all_inboxes + all_deleted

        self.dict = gensim.corpora.Dictionary(all_mail)

        print('done generating dict!')

    def get_dict(self):
        return self.dict

    def get_dict_size(self):
        if self.dict is not None:
            return len(self.dict)
        else:
            return 0

    def generate_doc_bow(self):
        print('generating doc bows...')

        for p in self.all:
            for m in p.get_inbox_mail():
                m.set_body_bow(self.dict.doc2bow(m.get_body_processed()))
            for m in p.get_deleted_mail():
                m.set_body_bow(self.dict.doc2bow(m.get_body_processed()))

        print('done generating bows!')
