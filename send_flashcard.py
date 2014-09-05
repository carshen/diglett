#!/usr/bin/python

# Keep this script in the root directory where emailer.sh is. 

import os
import subprocess
import sys
import random
import re

################################ Functions ####################################################

def choose_flashcard(root):
	"""Recursively search directory tree and return a randomly chosen flashcard (question and answer filenames)."""
	dirfiles = os.listdir(root)

	if len(dirfiles) == 0:
		sys.exit("There are no questions to send! Script terminated.")
	f = random.choice(dirfiles);

	while (not os.path.isdir(os.path.join(root,f))) or len(os.listdir(os.path.join(root,f))) == 0:
		f = random.choice(dirfiles)
		if os.path.isdir(os.path.join(root,f)) and len(os.listdir(os.path.join(root,f))) == 2 and q_and_a(root,f):
			break

	full_f_path = os.path.join(root,f)
	if os.path.isfile(f): # Check if f is a file or a folder
		sys.exit("Improper directory format! Script terminated.")
	elif os.path.isdir(full_f_path) and len(os.listdir(full_f_path)) == 2 and q_and_a(root,f):
	# If a folder, see if it has only 2 children files - *.question and *.answer that match.
		[f1,f2] = os.listdir(full_f_path)
		if f1.endswith(".question") and f2.endswith(".answer"):
			return [os.path.join(full_f_path,f1),os.path.join(full_f_path,f2)]
		else:
			return [os.path.join(full_f_path,f2),os.path.join(full_f_path,f1)]
	else:
		return choose_flashcard(os.path.join(root,f))

def q_and_a(root, filename):
	""" Returns True if exactly 1 file is a .question file and 1 file is a .answer file"""
	[f1,f2] = os.listdir(os.path.join(root,filename))
	return (f1.endswith(".question") and f2.endswith(".answer")) or (f2.endswith(".question") and f1.endswith(".answer"))

def txt2html(txt):
	"""Prettifies the text a little bit in HTML form."""
	return '<pre style="font-size:3em;color:green">' + txt + '</pre>' # I could add an xss cleaner but these are my own text files lol.	

def txtfile2html(qfilename):
	"""Return the contents of the file named by qfilename as an HTML string."""
	try:
		qfile = open(qfilename,'r')
		qtext = qfile.read()
		qhtml = txt2html(qtext)
		qfile.close()
		return qhtml
	except Exception as e:
		print e
		sys.exit("Error occurred during parsing question file. Script terminated.")


################################ Script body ##################################################

# Check the script was run properly.
nargs = len(sys.argv)
if nargs != 3:
	sys.exit("Usage: ./send_flashcard.py [subject] [email address]. Script terminated.")

# Remove all the backup *.*~ files.
for dirname, subdirlist, filelist in os.walk('.'):
	for fname in filelist:
		if re.search(r".*\..*~", fname):
			subprocess.Popen(['/bin/rm', os.path.join(dirname,fname)])

# Obtain flashcard files and convert to html.
[qpath, apath] = choose_flashcard('.'); # We start searching from the current directory.

print qpath, apath
qhtml = txtfile2html(qpath)

subj = sys.argv[1]
e_address = sys.argv[2]

# Try sending the email.
try:
	email_flashcard = subprocess.Popen(['/usr/bin/mutt', '-s', subj, '-a', apath, '-e', 'set content_type=text/html', '--', e_address],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	(output, error) = email_flashcard.communicate(qhtml)
	if output:
		print error
		sys.exit("Error occurred during emailing. Double check the text content. Script terminated.")
except Exception as e:
	print e
	sys.exit("Error occurred during emailing. Please ensure mutt is installed in /usr/bin/mutt. Script terminated.")
