import numpy as np
from sklearn.ensemble import RandomForestRegressor
from .models import Product, MarketData

def predict_demand(product_name, country_name, years=3):
    p=Product.query.filter(Product.name.ilike(product_name)).first()
    if not p: return None
    rows=MarketData.query.filter_by(product_id=p.id).join(MarketData.country).filter_by(name=country_name).order_by(MarketData.year).all()
    if len(rows)<3: return {'error':'At least three historical observations are required for this product and country.'}
    X=np.array([[r.year] for r in rows]); y=np.array([r.import_quantity_tonnes for r in rows])
    model=RandomForestRegressor(n_estimators=100,random_state=42); model.fit(X,y)
    future=[int(max(r.year for r in rows)+i) for i in range(1,years+1)]
    vals=model.predict(np.array(future).reshape(-1,1))
    return {'country':country_name,'product':product_name,'historical':[{'year':r.year,'quantity':r.import_quantity_tonnes} for r in rows],'predictions':[{'year':yr,'quantity':round(max(0,float(v)),2)} for yr,v in zip(future,vals)],'model':'Random Forest Regression','data_label':'DEMONSTRATION ONLY — trained on synthetic sample data; not a real-world forecast.'}
