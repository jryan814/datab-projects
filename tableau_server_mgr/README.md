# Tableau Server ETL and Automation

> Data consumers need to know what they are consuming. 
> Analysts receive the same inquiries about "what does this \[field\] mean?" far to frequently.
> The goal here is to increase understanding for those consuming the data. Generating data about data/reports seems funny, but is actually incredibly useful for everyone.

Initially the goal was to build a data dictionary based on the fields across a bunch of Tableau workbooks (140+). It then evolved into a full suite of use cases and applications. _It is still under development_, but it's base functionality of extracting fields and transforming the data for loading into 3 database tables is already complete, tested, and working.
#### Overview:

- Written in Python (and SQL executed from within Python)
- Utilizes 2 Tableau APIs (Tableau Server Client API and Tableau Document API)
- Originally written for working with an Oracle database (for the data dictionary component)
- Requires Site Admin Explorer or higher permissions on a Tableau Server site
- 2 authentication options via personal access token (or user credential login)
- Working on developing a UI, but currently only CLI


#### Code will be committed soon - in process of refactoring and anonymizing
