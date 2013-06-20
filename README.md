cpi_scrapers
============
   
If you have any question, please contant to @Anfernee Chang
   
  - GTalk: innovotech.hr@gmail.com
  - Skype: anfernee-chang


### Product Database Schema

- Please refer to [Product Database Schema v3.4 (last updated 20/06/13)](https://docs.google.com/file/d/0BwBtbldsfq-3LVh3UTRIVERiVHM/edit?usp=sharing)
- We define the product item in the items.py, please follow it.

### Notes

- Please use **'pasre_product'** to be the parsing method for product.
- Please add node's XPath in the spider class variable **'xpaths'** dict. We will use these information to check your spider.
- Please raises ValueError if the page have no data for the XPath to any **Required Fields**.
- Please make sure your spider can run and passe the cpi_scrapers/pipelines/validation.py before emailling it to us.
- To complete the job, we'd only be requiring the **spiders/store.py** file from you. Please send it by email.
