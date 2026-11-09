import json, io, csv
from flask import Blueprint, request, jsonify, make_response
from flask_login import login_required, current_user
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from . import db
from .models import Product, Country, AnalysisHistory, Prediction, ExportCalculation
from .market import analyze_product, WEIGHTS
from .predictor import predict_demand
api_bp=Blueprint('api',__name__)
def err(message,status=400): return jsonify({'error':message}),status
@api_bp.get('/products')
@login_required
def products():
    q=request.args.get('q','').strip(); items=Product.query.filter(Product.name.ilike(f'%{q}%')).order_by(Product.name).limit(30).all()
    return jsonify([{'id':p.id,'name':p.name,'hs_code':p.hs_code} for p in items])
@api_bp.post('/analyze')
@login_required
def analyze():
    data=request.get_json(silent=True) or {}; name=str(data.get('product','')).strip()[:120]
    if not name: return err('Product is required.')
    result=analyze_product(name)
    if result is None: return err('Product not found. Try one of the seeded products or add it to the dataset.',404)
    db.session.add(AnalysisHistory(user_id=current_user.id,product_name=name,result_json=json.dumps(result))); db.session.commit()
    return jsonify({'product':name,'results':result,'weights':WEIGHTS,'data_label':'Synthetic demonstration dataset — not official trade statistics.'})
@api_bp.post('/predict')
@login_required
def predict():
    d=request.get_json(silent=True) or {}; product=str(d.get('product','')).strip()[:120]; country=str(d.get('country','')).strip()[:100]
    if not product or not country: return err('Product and country are required.')
    result=predict_demand(product,country)
    if result is None: return err('Product not found.',404)
    if 'error' in result: return err(result['error'])
    for item in result['predictions']:
        db.session.add(Prediction(user_id=current_user.id,product_name=product,country_name=country,target_year=item['year'],predicted_quantity=item['quantity'],model_label=result['data_label']))
    db.session.commit(); return jsonify(result)
@api_bp.post('/profit')
@login_required
def profit():
    d=request.get_json(silent=True) or {}
    try:
        product=str(d.get('product','Custom product')).strip()[:120]
        quantity=float(d.get('quantity',0)); purchase=float(d.get('purchase_cost',0)); packaging=float(d.get('packaging',0)); shipping=float(d.get('shipping',0)); customs=float(d.get('customs',0)); selling=float(d.get('selling_price',0))
        vals=[quantity,purchase,packaging,shipping,customs,selling]
        if any(not (0<=v<=1e12) for v in vals) or quantity<=0: return err('Enter non-negative values and a quantity greater than zero.')
        investment=quantity*purchase+packaging+shipping+customs; revenue=quantity*selling; profit=revenue-investment
        result={'investment':round(investment,2),'revenue':round(revenue,2),'profit':round(profit,2),'margin_pct':round(profit/revenue*100,2) if revenue else 0,'currency':'USD'}
        db.session.add(ExportCalculation(user_id=current_user.id,product_name=product,inputs_json=json.dumps(d),result_json=json.dumps(result))); db.session.commit(); return jsonify(result)
    except (ValueError,TypeError): return err('All calculator inputs must be valid numbers.')
@api_bp.get('/report.csv')
@login_required
def csv_report():
    h=AnalysisHistory.query.filter_by(user_id=current_user.id).order_by(AnalysisHistory.created_at.desc()).first()
    if not h: return err('Run an analysis before exporting.',404)
    rows=json.loads(h.result_json); s=io.StringIO(); w=csv.DictWriter(s,fieldnames=['rank','country','score','demand_tonnes','growth_pct','avg_price_usd_tonne','competition_index','recommendation']); w.writeheader()
    for i,r in enumerate(rows,1): w.writerow({'rank':i,**{k:r.get(k) for k in w.fieldnames if k!='rank'}})
    res=make_response(s.getvalue()); res.headers['Content-Type']='text/csv'; res.headers['Content-Disposition']='attachment; filename=market-analysis.csv'; return res
@api_bp.get('/report.pdf')
@login_required
def pdf_report():
    h=AnalysisHistory.query.filter_by(user_id=current_user.id).order_by(AnalysisHistory.created_at.desc()).first()
    if not h: return err('Run an analysis before exporting.',404)
    rows=json.loads(h.result_json); buf=io.BytesIO(); c=canvas.Canvas(buf,pagesize=A4); width,height=A4; y=height-55
    c.setFont('Helvetica-Bold',18); c.drawString(45,y,'GLOBAL MARKET ANALYZER'); y-=28
    c.setFont('Helvetica',10); c.drawString(45,y,f'Product: {h.product_name}'); y-=18; c.drawString(45,y,'Synthetic demonstration dataset — not official trade statistics.'); y-=30
    c.setFont('Helvetica-Bold',9); c.drawString(45,y,'Rank   Country                 Score    Demand (tonnes)    Growth (%)'); y-=18; c.setFont('Helvetica',9)
    for i,r in enumerate(rows,1):
        if y<55: c.showPage(); y=height-55; c.setFont('Helvetica',9)
        c.drawString(45,y,f"{i:<6} {r['country'][:20]:<22} {r['score']:<8} {r['demand_tonnes']:<18} {r['growth_pct']}"); y-=16
    c.save(); res=make_response(buf.getvalue()); res.headers['Content-Type']='application/pdf'; res.headers['Content-Disposition']='attachment; filename=market-analysis.pdf'; return res
