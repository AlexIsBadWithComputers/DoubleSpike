This is the program which reads isotope data from multiple files, performs analysis
and spits out some results. This only works with THERMO export files or a .csv that
you've made yourself. If you need a copy of the manual or some sample THERMO data
to play with the program please email alexpattennant@gmail.com and I'll provide you
with any support you may need to get rolling. 

Requirements::
Python version 3+ 
scipy and numpy support
mysqldb if you're using the data base

if you're using the database, you'll probably need to 
update the commands to enter the data as your database probably isn't labeled the 
same as what this one is meant to conncet to. If you're not using adata base 
you can just comment out the line :

from DoubleSpikeDataBaseCommit import *

 in DoubleSpikeGUI.py. 

 NOTE: You will need to supply and create your own constant files to get this rolling. I have 
 included one for molybdenum for SRM 3134, but I would advice you to use your own values. If 
 you require a different element you will need to use the software to create the
 file yourself.