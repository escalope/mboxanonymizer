import os
import re
import sys
from os.path import join, getsize, isfile
import mailbox
import html2text

notdelete = ['to', 'from', 'message-id', 'in-reply-to', 'mime-version', 'content-type',
             'content-transfer-encoding', 'encode',  'date','title']

def getEmail(line):
    return re.findall(r"([a-zA-Z0-9_.+-]+(@|(=40.)|(=[\n]*@))[a-zA-Z0-9-]+(\.[a-zA-Z0-9-.])*)", line)


# based on code from https://mail.python.org/pipermail/tutor/2008-September/064272.html
def appendEmails(msg, anonymizedEmails):
    payload = msg.get_payload()

    if msg.is_multipart():
        for subMsg in payload:
            appendEmails(subMsg,anonymizedEmails)
    else:
        if (msg.get_content_type() == "text/html"
                or msg.get_content_type() == "text/plain"
                or msg.get_content_type()== "message/rfc822"):
            anonymizedEmails.extend(getEmail(payload))
            return True
        return False

# based on code from https://mail.python.org/pipermail/tutor/2008-September/064272.html
def replacePayload(msg, anonymizedEmails):
    payload = msg.get_payload()
    if msg.is_multipart():
        npayload = []
        for subMsg in payload:
            if (replacePayload(subMsg, anonymizedEmails)):
                npayload.append(subMsg)
        msg.set_payload(npayload)
        return True
    else:
        if (msg.get_content_type() == "text/html" or
                msg.get_content_type() == "text/plain" or
                msg.get_content_type()== "message/rfc822"):
            cleanMessage(anonymizedEmails, msg)
            if (msg.get_content_type() == "text/html"):
                charset = msg.get_charset()
                msg.__delitem__("content-type")
                msg["content-type"] = "text/plain"
                payload = html2text.html2text(payload)
            for key, val in anonymizedEmails.items():
                if isinstance(key,tuple):
                    longest=""
                    longestsize=0
                    for val in key:
                        if len(val)>longestsize:
                            longest=val
                            longestsize=len(val)
                    key=longest
                payload = payload.replace(key, val)
            payload = re.sub(r'\+[0-9|\W]*', '', payload)
            payload = re.sub(r'\w*@\w*', '', payload)

            payload = re.sub(r' [s | S][k | K][y | Y][p | P][e | E]. *', 'skype', payload)
            msg.set_payload(payload.encode('utf-8'))
            msg.set_charset("UTF-8")
            return True
        return False


def testmailbox(filename):
    mbox = mailbox.mbox(filename)
    i = 0
    print("Testing produced mbox");
    for message in mbox:
        if (not message['from'] is None):
            print("Read message number " + str(i) + " from   :" + message['from'])
        i += 1


def main(filenameorig, filenamedest):
    mbox = mailbox.mbox(filenameorig)
    os.remove(filenamedest)
    nmbox = mailbox.mbox(filenamedest)
    mbox.lock()
    try:
        i = 0
        emails = []
        print("Reading original mbox")
        for message in mbox:
            if (not message['from'] is None):
                emails.extend(getEmail(message['from'].lower()))
            if (not message['to'] is None):
                emails.extend(getEmail(message['to'].lower()))
            appendEmails(message,emails)
            i += 1
            if (i % 10 == 0):
                print("Read " + str(i) + " emails");

        anonymizedEmails = {}
        anoncounter = 0
        emails = list(dict.fromkeys(emails))
        print("Number of original messages: " + str(i) + "; number collected emails:" + str(len(emails)))

        for email in emails:
            anonymizedEmails[email] = "email" + str(anoncounter)
            anoncounter = anoncounter + 1

        print("Anonimizing emails .....")
        j = 0
        for message in mbox:
            cleanMessage(anonymizedEmails, message)
            replacePayload(message, anonymizedEmails)
            j = j + 1
            if (j % 10 == 0):
                print("Processed " + str(j) + " emails")
                nmbox.flush()
            nmbox.add(message)
        print(emails)
        print("Conversion complete. Converted " + str(j) + " emails");
        nmbox.close()
    finally:
        mbox.unlock()


def cleanMessage(anonymizedEmails, message):
    if (not message['From'] is None):
        oldcontent = message['from'].lower()
        message.__delitem__('From')
        if (len(getEmail(oldcontent))>0):
         message['From'] = anonymizedEmails[getEmail(oldcontent)[0]]
    if (not message['To'] is None):
        oldcontent = message['to'].lower()
        message.__delitem__('To')
        if (len(getEmail(oldcontent)) > 0):
         message['To'] = anonymizedEmails[getEmail(oldcontent)[0]]
    toDelete = []
    for i in reversed(range(len(message._headers))):
        hdrName = message._headers[i][0].lower()
        if hdrName not in notdelete:
            toDelete.append(hdrName)
    for name in toDelete:
        message.__delitem__(name)


# Call the main function.
# sys.argv[1] is the filepath to the input mbox file
# sys.argv[2] is the filepath to the output anonymized mbox file
main(sys.argv[1], sys.argv[2])  # sys.argv[1])
testmailbox(sys.argv[2])
