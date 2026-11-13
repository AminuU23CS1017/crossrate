// Public hosting adapter. The original FastAPI/SQL project is preserved separately.
export const currencies = {USD:'US Dollar',NGN:'Nigerian Naira',EUR:'Euro',GBP:'British Pound',GHS:'Ghanaian Cedi',KES:'Kenyan Shilling',ZAR:'South African Rand',CAD:'Canadian Dollar',AUD:'Australian Dollar',JPY:'Japanese Yen',CHF:'Swiss Franc',CNY:'Chinese Yuan'};
const fail=(message,status=422)=>{throw Object.assign(new Error(message),{status});};
const code=value=>{value=(value||'').toUpperCase();if(!Object.hasOwn(currencies,value))fail('Choose a supported currency.');return value;};
const day=()=>new Date().toISOString().slice(0,10);
const validDate=s=>/^\d{4}-\d{2}-\d{2}$/.test(s||'') && Number.isFinite(Date.parse(s)) && new Date(s).toISOString().slice(0,10)===s;
export function range(start,end){if(!validDate(start)||!validDate(end)||start>end||end>day()||(Date.parse(end)-Date.parse(start))/86400000>366)fail('Choose an ordered range of at most 366 days ending today or earlier.');}
function decimal(s){s=String(s);if(!/^\d+(\.\d+)?$/.test(s)||s.length>60)fail('Invalid decimal value.');const [a,b='']=s.split('.');return [BigInt(a+b),b.length];}
export function multiply(amount,rate,digits){const[a,ad]=decimal(amount),[b,bd]=decimal(rate);const scale=ad+bd-digits;let n=a*b;if(scale>0){const d=10n**BigInt(scale);n=(n+d/2n)/d;}else n*=10n**BigInt(-scale);const s=n.toString().padStart(digits+1,'0');return digits?s.slice(0,-digits)+'.'+s.slice(-digits):s;}
export function amountValue(value){if(!/^\d+(\.\d{1,8})?$/.test(value||'')||value.length>19||Number(value)>1e9)fail('Enter an amount from 0 to one billion, with up to 8 decimal places.');return value;}
export function createAPI(fetcher=fetch,cache=null){
 async function rates(base,quotes,start,end){
  const url=new URL('https://api.frankfurter.dev/v2/rates');url.searchParams.set('base',base);url.searchParams.set('quotes',quotes.join(','));if(start){url.searchParams.set('from',start);url.searchParams.set('to',end);}
  const key=new Request('https://crossrate-cache.invalid/'+encodeURIComponent(url.search));let saved;
  try{const hit=await cache?.match(key);if(hit)saved=await hit.json();}catch{}
  const age=saved?Date.now()-Date.parse(saved.fetched_at):Infinity;
  if(age>=0&&age<3600000)return {...saved,cache_status:'cached'};
  try{
   const response=await fetcher(url,{signal:AbortSignal.timeout(12000)});if(!response.ok)throw Error('Upstream error');const data=await response.json();if(!Array.isArray(data)||!data.length)throw Error('No rates');
   const rows=data.map(r=>{if(!validDate(r.date)||r.date>day()||r.base!==base||!quotes.includes(r.quote)||!Number.isFinite(Number(r.rate))||Number(r.rate)<=0||(start&&(r.date<start||r.date>end)))throw Error('Invalid rate');const value=String(r.rate);decimal(value);return {date:r.date,base,quote:r.quote,rate:value};}).sort((a,b)=>a.date.localeCompare(b.date)||a.quote.localeCompare(b.quote));
   if(new Set(rows.map(r=>r.quote)).size!==quotes.length)throw Error('Missing currency');
   const result={rates:rows,source:'Frankfurter blended reference rates',source_url:'https://frankfurter.dev/',fetched_at:new Date().toISOString(),cache_status:'fresh',warning:null};
   try{await cache?.put(key,new Response(JSON.stringify(result),{headers:{'Cache-Control':'public, max-age=604800','Content-Type':'application/json'}}));}catch{}
   return result;
  }catch{if(age>=0&&age<=604800000)return {...saved,cache_status:'stale',warning:'Provider unavailable. Showing previously saved data.'};fail('Rate provider is temporarily unavailable. Please try again.',503);}
 }
 return async request=>{
  try{
   const u=new URL(request.url),p=u.searchParams;if(request.method!=='GET')fail('Method not allowed.',405);
   if(u.pathname==='/api/health')return Response.json({status:'ok',project:'SP-050',edition:'hosted-worker'});
   if(u.pathname==='/api/currencies')return Response.json(currencies);
   const base=code(p.get('base')||'USD');let result;
   if(u.pathname==='/api/rates'){
    const quotes=[...new Set((p.get('quotes')||'NGN,EUR,GBP,GHS').split(',').map(s=>code(s.trim())))].filter(c=>c!==base).sort();if(!quotes.length||quotes.length>11)fail('Choose 1–11 different target currencies.');result=await rates(base,quotes);
   }else if(u.pathname==='/api/convert'){
    const quote=code(p.get('quote')||'NGN'),amount=amountValue(p.get('amount')||'100'),digits=quote==='JPY'?0:2;
    if(base===quote)result={base,quote,amount,rate:'1',converted:multiply(amount,'1',digits),date:null,source:'Identity conversion; no external rate used',cache_status:'identity'};
    else{const data=await rates(base,[quote]),row=data.rates.at(-1);result={...data,...row,amount,converted:multiply(amount,row.rate,digits)};}
   }else if(['/api/history','/api/export'].includes(u.pathname)){
    const quote=code(p.get('quote')||'NGN'),end=p.get('end')||day();if(!validDate(end))fail('Choose a valid end date.');const start=p.get('start')||new Date(Date.parse(end)-30*86400000).toISOString().slice(0,10);if(base===quote)fail('Choose different currencies for historical trends.');range(start,end);result=await rates(base,[quote],start,end);
    if(u.pathname==='/api/export'){const cell=v=>'"'+String(v??'').replaceAll('"','""')+'"';const rows=[['date','base','quote','rate','source','cache_status','fetched_at'],...result.rates.map(r=>[r.date,r.base,r.quote,r.rate,result.source,result.cache_status,result.fetched_at])];return new Response(rows.map(r=>r.map(cell).join(',')).join('\r\n'),{headers:{'Content-Type':'text/csv;charset=utf-8','Content-Disposition':'attachment; filename="exchange-rates.csv"'}});}
   }else fail('Not found.',404);
   return Response.json(result);
  }catch(e){return Response.json({detail:e.status?e.message:'Unable to process this request.'},{status:e.status||503});}
 };
}
