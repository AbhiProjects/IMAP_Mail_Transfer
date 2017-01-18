#!/usr/bin/env python
# -*- coding: utf-8 -*-
import imaplib

OPTION_DICT = {
	'source_imap_server': 'imap.gmail.com',
	'source_imap_port_ssl':993,
	'source_ssl_yes_no':True,
	'source_login':'',
	'source_password':'',
	'source_folder':'INBOX',
	
	'target_imap_server': 'imap.gmail.com',
	'target_imap_port_ssl':993,
	'target_ssl_yes_no':True,
	'target_login':'',
	'target_password':'',
	'target_folder':'INBOX',

	'mark_source_items_as_deleted_upon_move':True,
	
	'move_only_when_field_from_contains_these_keywords':
														[
															'sender@domain1.com',
															'sender@domain2.com',
															'senders surname2',
															'senders surname2'
														]
}
# List of Source Folders Allowed on Gmail
# INBOX		"[Gmail]/All Mail"		"[Gmail]/Sent Mail"		"[Gmail]/Starred"	"[Gmail]/Drafts"	"[Gmail]/Spam"		"[Gmail]/Trash"

def loginIMAP(Username,Password,Folder,Server,Port,SSL):
	try:
		if SSL == True:
			imap_conn = imaplib.IMAP4_SSL(Server,Port)
		else:
			imap_conn = imaplib.IMAP4(Server)

		imap_conn.login(Username,Password)
		print 'IMAP User',Username,' Credentials Authenticated'
		SET = imap_conn.select(Folder)
		if SET[0] == 'NO':
			imap_conn.select('INBOX')
			print 'Unknown Mail Box.Please Select a Correct Mailbox'
			print 'INBOX is the selected Mailbox'
			return None
	except:
		print 'Error Occuured In IMAP Section'
		return None
	
	return imap_conn

def searchEmail(imap_conn,SET_SEARCH):
	Data=[]
	if SET_SEARCH == False:
		type, msg_id = imap_conn.search(None, 'ALL')
		if type != 'OK':
			return Data
		Data = msg_id[0].split()
	else:
		for Keywords in OPTION_DICT['move_only_when_field_from_contains_these_keywords']:
			type, msg_id = imap_conn.search(None, "From",Keywords)
			if type != 'OK':
				continue
			for item in msg_id[0].split():
				Data.append(item)
				
	return Data

def emailCreator(source_imap_conn,destination_imap_conn,Data,Folder):
	count = 0;
	for msg_id in Data:		
		type,IndiviualMessages = source_imap_conn.fetch(msg_id, '(RFC822 FLAGS)')
		if type == 'OK' :
			# Sending The Email To The Target IMAP Server
			destination_imap_conn.append(Folder,None,None,IndiviualMessages[0][1])

			# Mark The Email UnRead
			source_imap_conn.store(msg_id, '-FLAGS', '\Seen')
		
			if OPTION_DICT['mark_source_items_as_deleted_upon_move'] == True:
				# Mark The Email for Deletion
				source_imap_conn.store(msg_id, '+FLAGS', '\\Deleted')
				count+=1
	
	return count
	
def allMailDelete(imap_conn,Data):
	count = 0;
	for msg_id in Data:
		imap_conn.store(msg_id, '+FLAGS', '\\Deleted')
		count+=1
	return count

def deleteAllMailFolder(imap_conn,Folder):
	count = 0
	SET = imap_conn.select(Folder)
	if SET[0] == 'NO':
		imap_conn.select('INBOX')
		print 'Unknown Mail Box.Please Select a Correct Mailbox'
		print 'INBOX is the selected Mailbox'
		return -1
	Data = searchEmail(imap_conn,False)
	count = allMailDelete(imap_conn,Data)
	return count

def closeIMAP(imap_conn):
	# Delete All Emails Marked For Deletion
	imap_conn.expunge()
	imap_conn.close()
	imap_conn.logout()
	
def search_main(SEARCH_SETTER=False,DELETE_ON=False):
	source_imap_conn = loginIMAP(OPTION_DICT['source_login'],OPTION_DICT['source_password'],OPTION_DICT['source_folder'],
										OPTION_DICT['source_imap_server'],OPTION_DICT['source_imap_port_ssl'],
										OPTION_DICT['source_ssl_yes_no'])
	
	if source_imap_conn == None :
		print 'Source Authentication Failure'
		return

	destination_imap_conn = loginIMAP(OPTION_DICT['target_login'],OPTION_DICT['target_password'],OPTION_DICT['target_folder'],
										OPTION_DICT['target_imap_server'],OPTION_DICT['target_imap_port_ssl'],
										OPTION_DICT['target_ssl_yes_no'])
	
	if destination_imap_conn == None :
		print 'Destination Authentication Failure'
		return
		
	# If SEARCH_SETTER is False Then All Emails Are To Be Searched Else True If Emails From Option Dictionary Are To Be Searched
	Data = searchEmail(source_imap_conn,SEARCH_SETTER) 
	
	# If DELETE_ON Is False Then All Mail In The Folder Delete Option is Disabled Else True Then All Mail In The Folder Delete Option is Enabled
	if DELETE_ON == False :
		if Data == [] :
			count = -1
			print 'No Emails Found on the Server'
		else:	
			count = emailCreator(source_imap_conn,destination_imap_conn,Data,OPTION_DICT['target_folder'])
	else :
		count = allMailDelete(source_imap_conn,Data)
		
	if count > 0 :
		print count,'Email was Deleted'
	else:
		print 'No Emails were Deleted'
	
	# Deleting The Trash Folder Of The Source Account 
	print 'Deleting The Trash Folder'
	count = deleteAllMailFolder(source_imap_conn,'"[Gmail]/Trash"')
	
	if count > 0 :
		print count,'Email was Deleted'
	else:
		print 'No Emails were Deleted'
	
	closeIMAP(source_imap_conn)
	closeIMAP(destination_imap_conn)
		
if __name__ == "__main__":
	# First Parameter Is Search Setter And The Second Parameter Is Delete On
	# If SEARCH_SETTER is False Then All Emails Are To Be Searched Else True If Emails From Option Dictionary Are To Be Searched
	# If DELETE_ON Is False Then All Mail In The Folder Delete Option is Disabled Else True Then All Mail In The Folder Delete Option is Enabled
	# True  False For SCRIPT #1: "IMAP_SELECT_MOVER.PY"
	# False False For SCRIPT #2: "IMAP_MOVER.PY"
	# False True For SCRIPT #3 "IMAP_FOLDER_CLEANER.PY"
	search_main(False,False)

# For Lamda Function Remove the if __name__ == "__main__": section and add the below function	
# def lambda_handler(event, context):
    # search_main(False,False)
