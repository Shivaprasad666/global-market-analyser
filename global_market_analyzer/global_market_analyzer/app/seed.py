import csv, os
from . import db
from .models import Product, Country, MarketData

def seed_database():
    if Product.query.first(): return
    base = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'market_sample.csv')
    with open(base, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            p = Product.query.filter_by(name=row['product']).first()
            if not p:
                p = Product(name=row['product'], hs_code=row['hs_code'], category=row['category']); db.session.add(p); db.session.flush()
            c = Country.query.filter_by(name=row['country']).first()
            if not c:
                c = Country(name=row['country'], iso2=row['iso2']); db.session.add(c); db.session.flush()
            db.session.add(MarketData(product_id=p.id, country_id=c.id, year=int(row['year']), import_value_usd=float(row['import_value_usd']), import_quantity_tonnes=float(row['import_quantity_tonnes']), avg_price_usd_tonne=float(row['avg_price_usd_tonne']), competition_index=float(row['competition_index']), source='Synthetic demonstration dataset'))
    db.session.commit()
