#startup

##Committees
Notice that the committees are bienniel and oddnumbered years. We are currently in the 2015 year, but soon switching to 2017.

[Wisconsin Committees](http://docs.legis.wisconsin.gov/2015/committees)

View source on each of those 4 committee types (Senate, Assembly, Joint, Other) to find the "feed" links

* [Senate](http://docs.legis.wisconsin.gov/feed/2015/committees/senate)
* [Assembly](http://docs.legis.wisconsin.gov/feed/2015/committees/assembly)
* [Joint](http://docs.legis.wisconsin.gov/feed/2015/committees/joint)
* [Other](http://docs.legis.wisconsin.gov/feed/2015/committees/other)

I extract the committee metadata from these sites. Note that for the Joint Committees, there's a lot of reports and extra stuff that has to be edited out. This is done with get_data.edit_JointCommittee(). Every time the data is updated, check that the information skipped is reasonable.

For each committee, I extract a personal committee website from the metadata. The source is put through an HTML parser and sent to be edited at get_data.edit_committee_info(). This consists mainly of string and regex operations to extract relevant committee info. This function can definitely do with some slimming, but it returns all the other info we want.

Our data structure is

            [str CommitteeName, 
             str CommitteeType, 
             str URL, 
             str Header, 
             list Chair, 
             list CoChair, 
             list ViceChair, 
             list CommitteeClerk, 
             list LegislativeCouncilStaff, 
             list Members, 
             list OtherMembers, 
             list Hearings]
             
with default NoneType.

The code takes about half a minute to run on 81 separate committees (2016-12-21).

###Files
* getcommittee.py / getcommittee.ipynb has code
* committee_list.txt is a list of all the committee names
* committees.csv is all committee information

###In the future
* Check that data skipped in get_data.edit_JointCommittee() can be skipped.
* get_data.edit_JointCommittee()
** slim / break up
** Look into exceptions for names when adding spaces before capital letters 
** This info doesn't include Hearing Documents/In/Out/All/Proposals
* Follow more links? Get more research? as I've skipped links for ease.

I also need to send to MySQL (instead of csv) once I run it on the server.

##Assembly

