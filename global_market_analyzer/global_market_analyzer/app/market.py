import pandas as pd
from .models import Product, MarketData

WEIGHTS = {'demand': .35, 'growth': .25, 'price': .20, 'competition': .20}

def analyze_product(product_name):
    product = Product.query.filter(Product.name.ilike(product_name)).first()
    if not product: return None
    rows = MarketData.query.filter_by(product_id=product.id).order_by(MarketData.year).all()
    if not rows: return []
    df = pd.DataFrame([{'country':r.country.name,'year':r.year,'value':r.import_value_usd,'quantity':r.import_quantity_tonnes,'price':r.avg_price_usd_tonne,'competition':r.competition_index} for r in rows])
    out=[]
    for country,g in df.groupby('country'):
        g=g.sort_values('year'); latest=g.iloc[-1]; previous=g.iloc[-2] if len(g)>1 else latest
        growth=((latest.value-previous.value)/previous.value*100) if previous.value else 0
        out.append({'country':country,'year':int(latest.year),'import_value_usd':round(float(latest.value),2),'demand_tonnes':round(float(latest.quantity),2),'avg_price_usd_tonne':round(float(latest.price),2),'growth_pct':round(float(growth),2),'competition_index':round(float(latest.competition),2),'history':[{'year':int(x.year),'quantity':float(x.quantity),'value':float(x.value)} for x in g.itertuples()]})
    if not out: return []
    def norm(vals, reverse=False):
        lo,hi=min(vals),max(vals)
        scores=[50.0 if hi==lo else (v-lo)/(hi-lo)*100 for v in vals]
        return [100-s for s in scores] if reverse else scores
    demand=norm([x['demand_tonnes'] for x in out]); growth=norm([x['growth_pct'] for x in out]); price=norm([x['avg_price_usd_tonne'] for x in out]); competition=norm([x['competition_index'] for x in out], reverse=True)
    for i,x in enumerate(out):
        score=demand[i]*WEIGHTS['demand']+growth[i]*WEIGHTS['growth']+price[i]*WEIGHTS['price']+competition[i]*WEIGHTS['competition']
        x['score']=round(score,1)
        x['recommendation']='High opportunity' if score>=70 else ('Moderate opportunity' if score>=40 else 'Low opportunity')
    return sorted(out,key=lambda x:x['score'],reverse=True)
