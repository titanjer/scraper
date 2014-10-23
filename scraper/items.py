# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field


class ProductItem(Item):
    ''' '''  # {{{

    # Constant
    # {{{

    # Not In Options
    NIO = 0

    # Categroy
    CG_PATH_SEP = ' >> '
    CG_PATHS_SEP = ' || '

    # Availability
    # 'Discontinued', 'In Stock', 'In Store Only', 'Out Of Stock',
    # 'Available To Order', 'Pre Order'
    NUM_AVAIL_OPTS = 6
    AVAIL_DC, AVAIL_IS, AVAIL_ISO, AVAIL_OOS, AVAIL_ATO, AVAIL_PO = \
        range(1, NUM_AVAIL_OPTS+1)

    # Product Condition
    # 'Damaged', 'New', 'Used', 'Refurbished'
    NUM_PC_OPTS = 4
    PC_DMG, PC_NEW, PC_USED, PC_RFB = range(1, NUM_PC_OPTS+1)

    # }}}

    # Validtions
    # {{{
    VALIDATION_LEN = {
        # {{{
        'source': 128,
        'product_number': 128,
        'product_name': 512,
        'category_name': 2048,
        'product_url': 2048,
        'image_url': 2048,
        'currency': 32,
        'manufacturer': 128,
        'mpn': 128,
        'product_sku': 128,
    }  # }}}

    VALIDATION_REQUIRED = set((
        # {{{
        'source',
        'product_number',
        'product_name',
        'description',
        'category_name',
        'product_url',
        'image_url',
        'product_condition',
        'availability',
        'sale_price',
        'on_sale',
        'currency',
        'manufacturer',
        'shipping_cost',
    ))  # }}}

    VALIDATION_NON_REQUIRED = set((
        # {{{
        'gtin',
        'mpn',
        'product_sku',
        'product_spec',
        'cost_price',
        'num_reviews',
        'avg_reviews_points',
        'keywords',
    ))  # }}}

    # }}}

    # Required Fields, pls note the VALIDATION_REQUIRED
    # {{{
    source = Field()
    product_number = Field()
    product_name = Field()
    description = Field()
    category_name = Field()  # Seperate by CG_PATH_SEP and CG_PATHS_SEP
    product_url = Field()
    image_url = Field()
    product_condition = Field()  # Constant for Product Condition

    availability = Field()  # Constant for Availability
    sale_price = Field()
    on_sale = Field()
    currency = Field()

    manufacturer = Field()

    shipping_cost = Field()
    # }}}

    # Optional Field
    # {{{
    gtin = Field()
    mpn = Field()
    product_sku = Field()
    product_spec = Field()

    cost_price = Field()

    num_reviews = Field()
    avg_reviews_points = Field()

    keywords = Field()

    # }}}

    no_sale_price = Field()
    no_shipping_cost = Field()

    # hash_value = Field()
    # version = Field()
    # id = Field()
    # crawl_date = Field()
    store_id = Field()

    # }}}
