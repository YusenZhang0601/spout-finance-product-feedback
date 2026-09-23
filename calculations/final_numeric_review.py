#!/usr/bin/env python3
"""Independent arithmetic review of AntiGravity's final Spout draft.
No network, wallets or product execution. Python 3.10+, scipy and mpmath.
Numeric agreement is not validation of a protocol mechanism or a prose claim.
"""
from __future__ import annotations
import csv, hashlib, json, math, sys
from pathlib import Path
from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo
import mpmath as mp
from scipy.optimize import brentq

OUT=Path(__file__).resolve().parent/'final_results'
OUT.mkdir(parents=True,exist_ok=True)

def bsm(S: float,K: float,T: float,r: float,v: float,q: float=0.) -> dict[str,float]:
    if min(S,K,T,v)<=0 or not all(map(math.isfinite,(S,K,T,r,v,q))):
        raise ValueError('Finite values and positive S,K,T,v required')
    N=lambda x:.5*(1+math.erf(x/math.sqrt(2)))
    phi=lambda x:math.exp(-x*x/2)/math.sqrt(2*math.pi)
    d1=(math.log(S/K)+(r-q+.5*v*v)*T)/(v*math.sqrt(T));d2=d1-v*math.sqrt(T)
    C=S*math.exp(-q*T)*N(d1)-K*math.exp(-r*T)*N(d2)
    delta=math.exp(-q*T)*N(d1)
    return dict(d1=d1,d2=d2,call=C,call_delta=delta,covered_delta=1-delta,
      call_gamma=math.exp(-q*T)*phi(d1)/(S*v*math.sqrt(T)),
      call_vega=S*math.exp(-q*T)*math.sqrt(T)*phi(d1))

a=bsm(200,220,30/365,.05,.4); b=bsm(250,220,15/365,.05,.4)
rows=[]
def compare(id: str,reported: float,actual: float,tol: float,scope: str):
    rows.append(dict(id=id,reported=reported,recalculated=actual,absolute_error=abs(actual-reported),
      rounding_tolerance=tol,numeric_agreement=abs(actual-reported)<=tol,scope=scope))
for k,reported,tol in [('d1',-.738096,5e-7),('d2',-.852624,5e-7),('call',2.906852,5e-7),
 ('call_delta',.230273,5e-7),('covered_delta',.769727,5e-7),('call_gamma',.013248,5e-7),('call_vega',17.4222,5e-5)]:
    compare('baseline_'+k,reported,a[k],tol,'Hypothetical European BSM, not a Spout execution')
for k,reported,tol in [('d1',1.642352,5e-7),('d2',1.560946,5e-7),('call',30.890983,5e-7),
 ('call_delta',.949741,5e-7),('covered_delta',.050259,5e-7)]:
    compare('postshock_'+k,reported,b[k],tol,'Hypothetical path: price and time-to-expiry both change')
compare('option_value_change',27.984130,b['call']-a['call'],5e-7,'Short-leg MTM loss, not automatic bad debt')
compare('combined_stock_short_change',22.02,50-(b['call']-a['call']),.005,'Includes retained premium; ignores carry and costs')
compare('vega_per_vol_point',.1742,a['call_vega']/100,5e-5,'Dollar sensitivity per 0.01 absolute IV')
N0,K,ST,D=100.,220.,250.,10000.
residual=N0*K-D; shares=residual/ST; uncapped=(N0*ST-D)/ST
compare('residual_cash',12000.,residual,.005,'Full assignment, no additional cash/premium/fees')
compare('rebought_shares',48.,shares,.005,'Illustrative only: not observed in Beta')
compare('share_count_reduction_percent',52.,100*(N0-shares)/N0,.005,'Not a wealth-loss rate')
HF=.588/.5;drop=1-.5/.588;ltv18=.5/.82
compare('initial_health_factor',1.176,HF,.0005,'Constant single-asset debt/quantity/threshold')
compare('rounded_health_factor',1.18,HF,.005,'Display rounding only')
compare('price_cushion_percent',14.97,drop*100,.005,'Use exact HF, not rounded 1.18')
compare('post_18pct_drop_ltv_percent',60.98,ltv18*100,.005,'Eligible for liquidation, not evidence of over-liquidation')
compare('hypothetical_1000_floor',850.34,1000*.5/.588,.005,'Requires explicitly assumed initial price $1000')
T=14/365;target=.5*200*.09*T
root=brentq(lambda v:bsm(200,210,T,.05,v)['call']-target,.01,1,xtol=1e-14)
compare('gross_budget_root_percent',18.542463,root*100,5e-7,'Numerical root of a toy gross-premium budget, not solvency threshold')
compare('hypothetical_tx_per_slot',15.,12000000//800000,0,'Assumed total scheduling cost and shared account; not measured throughput')
compare('hypothetical_tx_per_second',37.5,(12000000//800000)/.4,0,'Further assumes every slot is 0.4 seconds and reaches capacity')
partial=(6000-.5*100*102)/(102*(1-.088-.5))
compare('partial_liquidation_shares',21.4163,partial,5e-5,'Fee on sale proceeds, fractional quantity model')

mp.mp.dps=65
mpN=lambda x:(1+mp.erf(x/mp.sqrt(2)))/2
high_precision={}
for key,spot,days in [('baseline',200,30),('postshock',250,15)]:
    S=mp.mpf(spot); KK=mp.mpf(220);t=mp.mpf(days)/365;r=mp.mpf('.05');v=mp.mpf('.4')
    d1=(mp.log(S/KK)+(r+v*v/2)*t)/(v*mp.sqrt(t));d2=d1-v*mp.sqrt(t)
    C=S*mpN(d1)-KK*mp.exp(-r*t)*mpN(d2)
    z=a if key=='baseline' else b
    assert abs(float(C)-z['call'])<1e-11
    assert abs(float(d1)-z['d1'])<1e-12
    assert abs(float(d2)-z['d2'])<1e-12
    high_precision[key]={k:str(vv) for k,vv in [('d1',d1),('d2',d2),('call',C)]}
assert abs((N0-shares)-(D/ST+N0*(ST-K)/ST))<1e-12
assert abs((uncapped-shares)-12)<1e-12
assert abs(bsm(200,210,T,.05,root)['call']-target)<1e-10
claim_deadline=datetime(2026,9,23,22,59,59,tzinfo=timezone.utc)
capture=datetime(2026,9,22,15,58,53,tzinfo=timezone.utc)
result={
 'scope':'Offline review of supplied illustrative arithmetic; no live protocol or UI testing',
 'baseline':a,'postshock':b,'high_precision':high_precision,
 'numeric_comparisons':{'total':len(rows),'agree':sum(x['numeric_agreement'] for x in rows),'disagree':sum(not x['numeric_agreement'] for x in rows)},
 'comparisons':rows,
 'assignment':{'remaining_shares':shares,'shares_equivalent_of_debt_repayment':D/ST,
  'shares_equivalent_of_capped_upside':N0*(ST-K)/ST,'uncapped_after_same_debt_shares':uncapped,
  'same_debt_equity_benchmark':N0*ST-D,'covered_residual_equity':residual,
  'equity_difference_before_premium_fees_interest':N0*(ST-K),
  'difference_fraction_of_same_debt_benchmark':(N0*(ST-K))/(N0*ST-D)},
 'health_factor':{'exact':HF,'price_decline':drop,'price_decline_if_exact_HF_were_1_18':1-1/1.18,
   'official_example_initial_120_floor':6000/(100*.588),'hypothetical_initial_1000_floor':1000*.5/.588},
 'root':{'toy_annual_rates':[.08,.01],'outflow_per_share':target,'root':root,
  'warning':'Not actual Spout fee/yield parameters; 14-day tenor is illustrative'},
 'margin_comparison':{'assumed_14d_debt_at_8pct_simple':10000*(1+.08*14/365),
  'assumed_30d_debt_at_8pct_simple':10000*(1+.08*30/365),
  'warning':'The reviewed 10031 dollar debt comparison omitted a duration'},
 'calendar':{'claimed_deadline_utc':claim_deadline.isoformat(),'deadline_independently_verified':False,
   'if_claim_true_Beijing':claim_deadline.astimezone(ZoneInfo('Asia/Shanghai')).isoformat(),
   'if_claim_true_Los_Angeles':claim_deadline.astimezone(ZoneInfo('America/Los_Angeles')).isoformat(),
   'historical_time_remaining_from_reported_capture_seconds':(claim_deadline-capture).total_seconds(),
   '2026_09_26_weekday':date(2026,9,26).strftime('%A')},
}
(OUT/'numeric_review.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
with (OUT/'numeric_comparisons.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps(result['numeric_comparisons']))
for row in rows:
    if not row['numeric_agreement']:print('DISAGREEMENT',row['id'],row['reported'],'->',row['recalculated'])
print('High-precision BSM cross-checks and accounting identities passed. This is not a protocol audit.')
