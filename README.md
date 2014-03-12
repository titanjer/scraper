scraper
============
   
If you have any question, please contant to @Anfernee Chang
   
  - GTalk: anfernee@getpentagon.com.au
  - Skype: anfernee-chang


### Product Database Schema

- Must read carefully - [Product Database Schema v3.5 (last updated 02/07/13)](https://docs.google.com/file/d/0BwBtbldsfq-3LVh3UTRIVERiVHM/edit?usp=sharing)
- We define the product item in the items.py, please follow it.

### Validation
- Please run your spider and make sure it passes **scraper/pipelines/validation.py** before sending it.
- Please make sure the spider doesn't raise any errors with **'scrapy crawl spider'** before sending it.
- Any spiders sent without checking will result in **'penalties!'**

### Notes
1. Please follow **PEP8** style. 
1. Please use **'pasre_product'** to be the parsing method for **A** product and pass **no meta** in if you can.
1. Please add node's XPath in the spider class variable **'xpaths'** dict. We will use these information to check your spider.
1. Please raises ValueError('XXX!') if the page have no data for the XPath to any **Required Fields**.
1. Please use **'copy.deepcopy'** or **'new ProductItem()'** to re-generate a item for each different product variation(colors etc.).
1. Since we use Duplicate Filter to save the carwled url, please use **'dont_filter'** carefully.
1. To complete the job, we'd only be requiring the **spiders/store.py** file from you. Please send it by email.
