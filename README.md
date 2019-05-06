Descripcion
===========

This program makes a partial anonymization of mbox inbox files. It preserves most of the content, but, in most cases and to avoid a deeper analysis, it replaces major parts of the text and may lead to loss of information. 

It uses regular expressions to identify pieces of text that may affect the privacy. There is none natural language processing elements.

Main:

- It does not recognise personal names 
- It does not regonise physical addresses

The python program does a partial anonymization of an inbox as follows:

- removing from headers or the email content the different emails. These are replaced homogeneously with anonymized versions namely "email0", "email1", and so on. An email is anything matching this regular expression "([a-zA-Z0-9_.+-]+(@|(=40.)|(=[\n]*@))[a-zA-Z0-9-]+(\.[a-zA-Z0-9-.])*)"
- removing skype identifiers. These are strings that start with this regular expression "[s | S][k | K][y | Y][p | P][e | E]. *"
- remove long number sequences suspect of being a telephone number "\+[0-9|\W]*"
- removing twitter ids or any other missed email with "\w*@\w*"
- the only headers maintained are the following: 'to', 'from', 'message-id', 'in-reply-to', 'mime-version', 'content-type','content-transfer-encoding', 'encode',  'date','title'



Dependencies
============
Made to work with python3.

Need to install the following dependencies:

- mailbox
- html2text

To use it
=========
The program is executed from the comand line as follows:

	python3 anonymize.py FileToBeAnonymized.mbox NewAnonymizedFile.mbox




