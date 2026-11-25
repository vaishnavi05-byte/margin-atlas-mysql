"""Grain-safe fields for the additional commerce dashboards.

Item merchandise margin excludes refunds, inventory recovery, marketing and
shared order costs. It is intentionally not called product contribution.
"""

def discount_band(gross, discount):
    gross, discount = int(gross), int(discount)
    if gross < 0 or discount < 0 or discount > gross:
        raise ValueError('Invalid gross/discount relationship')
    if not gross:
        return 'No recognized sales', 5
    if not discount:
        return '0%', 0
    if discount * 100 <= gross * 10:
        return '1-10%', 1
    if discount * 100 <= gross * 20:
        return '11-20%', 2
    if discount * 100 <= gross * 30:
        return '21-30%', 3
    return 'Above 30%', 4


def enrich_items(raw_items, orders, products):
    order_map={r['order_id']:r for r in orders}
    product_ids={r['product_id'] for r in products}
    seen=set(); result=[]
    for raw in raw_items:
        if raw['line_id'] in seen:
            raise ValueError('Duplicate item line')
        seen.add(raw['line_id'])
        if raw['order_id'] not in order_map or raw['product_id'] not in product_ids:
            raise ValueError('Unknown item reference')
        row=dict(raw)
        for name in ['quantity','gross_paise','discount_paise','cogs_paise']:
            row[name]=int(row[name])
        if row['quantity']<1 or min(row['gross_paise'],row['discount_paise'],row['cogs_paise'])<0 or row['discount_paise']>row['gross_paise']:
            raise ValueError('Invalid item quantity or money')
        delivered=int(order_map[row['order_id']]['delivery_eligible'])
        row['recognized_units']=row['quantity']*delivered
        row['sales_before_refund_paise']=row['gross_paise']-row['discount_paise']
        row['merchandise_margin_paise']=row['sales_before_refund_paise']-row['cogs_paise']
        result.append(row)
    return result
