cpi_scrapers
============
   
If you have any question, please contant to @Anfernee Chang
   
  - GTalk: innovotech.hr@gmail.com
  - Skype: anfernee-chang


### Product Database Schema

- Must read carefully - [Product Database Schema v3.5 (last updated 02/07/13)](https://docs.google.com/file/d/0BwBtbldsfq-3LVh3UTRIVERiVHM/edit?usp=sharing)
- We define the product item in the items.py, please follow it.

### Validation
- Please run your spider and pass **cpi_scrapers/pipelines/validation.py** before emailling it to us.
- Please make sure the spider doesn't raise any errors with **scrapy crawl spider** before sending it.

### Notes
- Please use **'pasre_product'** to be the parsing method for **A** product and pass no **meta** in if you can.
- Please add node's XPath in the spider class variable **'xpaths'** dict. We will use these information to check your spider.
- Please raises ValueError if the page have no data for the XPath to any **Required Fields**.
- Please use **'copy.deepcopy'** or **'new ProductItem()'** to re-generate a item for each different product variation.
- Since we use Duplicate Filter to save the carwled url, please use **'dont_filter'** carefully.
- To complete the job, we'd only be requiring the **spiders/store.py** file from you. Please send it by email.
