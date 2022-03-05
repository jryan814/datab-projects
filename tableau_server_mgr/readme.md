# Tableau Server Mgr

### toc:
- Overview of purpose
- User's guide
- Upcoming development


## Purpose/functionality:
- Access Tableau Server documents
- Easily download all or selected workbooks
- Extract data such as field names, dtypes, etc from workbooks
- Extract and catalogue SQL queries
- Bulk update workbooks
- Manage users, subscriptions, groups etc.

# User's Guide

## Initial config required
- Currently setup etc is not automated
- Dependencies in requirements.txt need to be installed
- Update the credentials:
    - all tableau server info and credentials
    - Database connection and credentials
    - Oracle is currently the only database option, however, several others would be easy to add with just a couple code changes.
- 