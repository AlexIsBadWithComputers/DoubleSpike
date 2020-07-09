# Double Spike Isotope Analysis Program

This is the program which reads isotope data from multiple files, performs analysis
and spits out some results. This only works with THERMO export files or a `.csv` that
you've made yourself. If you need a copy of the manual or some sample THERMO data
to play with the program please email alexpattennant@gmail.com and I'll provide you
with any support you may need to get rolling. 

## Requirements
* Python version 3.5 
* `scipy` and `numpy`
* `mysqldb` (if you're using the data base connection)

## Note
If you're using the database, you'll almost certainly need to 
update the commands to enter the data as your database probably isn't labeled the 
same as what this is designed to conncet to. If you're not using data base 
you can just comment out the line :
```python
from DoubleSpikeDataBaseCommit import *
```
 in `DoubleSpikeGUI.py`. 
## Note 2
 
 You will need to supply and create your own constant files to get this rolling. I have 
 included one for molybdenum for SRM 3134, but I would advice you to use your own values. If 
 you require a different element you will need to use the software to create the
 file yourself.
