#startup

##Committees
Notice that the committees are bienniel and oddnumbered years. We are currently in the 2015 year, but soon switching to 2017.

[Wisconsin Committees](http://docs.legis.wisconsin.gov/2015/committees)

View source on each of those 4 committee types (Senate, Assembly, Joint, Other) to find the "feed" links

* [Senate](http://docs.legis.wisconsin.gov/feed/2015/committees/senate)
* [Assembly](http://docs.legis.wisconsin.gov/feed/2015/committees/assembly)
* [Joint](http://docs.legis.wisconsin.gov/feed/2015/committees/joint)
* [Other](http://docs.legis.wisconsin.gov/feed/2015/committees/other)

I extract the committee metadata from these sites. Note that for the Joint Committees, there's a lot of reports and extra stuff that has to be edited out. This is done with get_data.edit_JointCommittee(). In the future, every time the data is updated, check that the information skipped is reasonable.

###Files
* get_data.py / get_data.ipynb has code
* committee_list.txt is a list of all the committee names
* committees.csv is all committee information

###In progress
From the metadata, I link to committee sites, and extract information on each of those.

I output to committees.csv

