#!/usr/bin/python

import subprocess

cmd = ['/usr/bin/mysqldump',
       '--add-drop-database',
       '-h',
       'mysql-read-us-east-1a-02.c16cpzmyddrq.us-east-1.rds.amazonaws.com',
       '-u',
       'sbuser',
       '-ps7cJHdr$',
       '--databases',
       'sb-vold']

f = open('/mnt/sb-vold.sql', 'w')
mysqldump_p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
sed_p = subprocess.Popen(['sed', '-e', "'s/DEFINER[ ]*=[ ]*[^*]*\*/\*/'"], stdin=mysqldump_p.stdout, stdout=f)
mysqldump_p.communicate()
f.close()
if mysqldump_p.returncode != 0:
  print "Error backing up database. Details: %s" % (mysqldump_p.stderr.readlines())
else:
  print "Backup completed successfully"

