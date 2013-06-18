cpi_scrapers
============

scrapy template for online store.

If you have any question, please contant to @Anfernee Chang
  - gtalk: innovotech.hr@gmail.com
  - skype: anfernee-chang


### Product Database Schema

- Please refer to [Product Database Schema v3.3](https://docs.google.com/file/d/0BwBtbldsfq-3a0dEdEs3MFVpam8/edit)
- We define the product item in the items.py, please follow it.

### Notes

- Please add node's XPath in the spider class variable **'xpaths'** dict. We will use these information to check your spider.
- Please raises ValueError if the page have no data for the XPath to any **Required Fields**.
- To complete the job, we'd only be requiring the **spiders/store.py** file from you.
