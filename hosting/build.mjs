import {readFileSync,writeFileSync} from 'node:fs';
const assets={};for(const file of ['index.html','app.js','features.js','style.css'])assets[file]=readFileSync('ui/'+file,'utf8');
const api=readFileSync('worker/api.mjs','utf8').replaceAll('export ','');
writeFileSync('worker/index.js',api+'\nconst assets='+JSON.stringify(assets)+';\n'+`
export default {async fetch(request,env,ctx){
 const url=new URL(request.url);let response;
 if(url.pathname.startsWith('/api/'))response=await createAPI(fetch,typeof caches!=='undefined'?caches.default:null)(request);
 else{const name=url.pathname==='/'?'index.html':url.pathname.startsWith('/static/')?url.pathname.slice(8):null;
 response=name&&Object.hasOwn(assets,name)?new Response(assets[name],{headers:{'Content-Type':name.endsWith('.html')?'text/html;charset=utf-8':name.endsWith('.css')?'text/css':'text/javascript'}}):new Response('Not found',{status:404});}
 response=new Response(response.body,response);response.headers.set('X-Content-Type-Options','nosniff');response.headers.set('Referrer-Policy','strict-origin-when-cross-origin');response.headers.set('Cache-Control','no-store');return response;
}};
`);
