const ORIGIN="https://novabytesolucoes.com.br";
const SUPABASE="https://vajlhodqxskozuxxlujv.supabase.co";
const ANON="sb_publishable_uT0b4y0Bex1k1QWZoyIfKg_K0pm-yS3";
const json=(x,status=200,headers={})=>new Response(JSON.stringify(x),{status,headers:{"content-type":"application/json",...headers}});
export default {async fetch(request,env){
 const origin=request.headers.get("Origin");
 const cors={"Access-Control-Allow-Origin":origin===ORIGIN?ORIGIN:"null","Access-Control-Allow-Methods":"GET,POST,PUT,OPTIONS","Access-Control-Allow-Headers":"Authorization,Content-Type","Vary":"Origin"};
 if(request.method==="OPTIONS")return new Response(null,{headers:cors});
 const reply=(x,s=200)=>json(x,s,cors);
 if(new URL(request.url).pathname==="/health")return reply({ok:true,bucket:"nplay-filmes",version:"1"});
 if(origin!==ORIGIN)return reply({error:"Origin não autorizado"},403);
 const token=(request.headers.get("Authorization")||"").replace(/^Bearer /,"");
 if(!token)return reply({error:"Login obrigatório"},401);
 const headers={"apikey":ANON,"Authorization":"Bearer "+token};
 const u=await fetch(SUPABASE+"/auth/v1/user",{headers});
 if(!u.ok)return reply({error:"Sessão inválida"},401);
 const user=await u.json();
 const admin=await fetch(SUPABASE+"/rest/v1/novaplay_admins?user_id=eq."+encodeURIComponent(user.id)+"&select=user_id",{headers});
 if(!admin.ok||!(await admin.json()).length)return reply({error:"Sem permissão administrativa"},403);
 const url=new URL(request.url),path=url.pathname;
 try{
  if(path==="/uploads/start"&&request.method==="POST"){
   const b=await request.json();
   if(!/^[a-z0-9-]{8,80}\.(mp4|webm|ogv)$/i.test(b.filename||""))return reply({error:"Nome de arquivo inválido"},400);
   const key=user.id+"/"+crypto.randomUUID()+"-"+b.filename;
   const m=await env.VIDEOS.createMultipartUpload(key,{httpMetadata:{contentType:b.filename.endsWith(".mp4")?"video/mp4":b.filename.endsWith(".webm")?"video/webm":"video/ogg"}});
   return reply({key,uploadId:m.uploadId});
  }
  if(path==="/uploads/part"&&request.method==="PUT"){
   const key=url.searchParams.get("key"),uploadId=url.searchParams.get("uploadId"),part=Number(url.searchParams.get("part"));
   if(!key?.startsWith(user.id+"/")||!uploadId||!Number.isInteger(part)||part<1||part>10000)return reply({error:"Parâmetros inválidos"},400);
   const upload=env.VIDEOS.resumeMultipartUpload(key,uploadId);
   const result=await upload.uploadPart(part,request.body);
   return reply({partNumber:result.partNumber,etag:result.etag});
  }
  if(path==="/uploads/complete"&&request.method==="POST"){
   const b=await request.json();
   if(!b.key?.startsWith(user.id+"/")||!b.uploadId||!Array.isArray(b.parts)||!b.parts.length)return reply({error:"Parâmetros inválidos"},400);
   const upload=env.VIDEOS.resumeMultipartUpload(b.key,b.uploadId);
   await upload.complete(b.parts);
   return reply({ok:true,key:b.key});
  }
  if(path==="/uploads/abort"&&request.method==="POST"){
   const b=await request.json();
   if(!b.key?.startsWith(user.id+"/")||!b.uploadId)return reply({error:"Parâmetros inválidos"},400);
   await env.VIDEOS.resumeMultipartUpload(b.key,b.uploadId).abort();
   return reply({ok:true});
  }
  if(path==="/processor/source"&&request.method==="GET"){
   const key=url.searchParams.get("key");
   if(!key||!key.startsWith(user.id+"/")||!/(\.mp4|\.webm|\.ogv|\.mov|\.mkv)$/i.test(key))return reply({error:"Arquivo inválido"},400);
   const object=await env.VIDEOS.get(key);
   if(!object)return reply({error:"Arquivo não encontrado"},404);
   return new Response(object.body,{headers:{"Content-Type":object.httpMetadata?.contentType||"application/octet-stream","Cache-Control":"no-store",...cors}});
  }
  if(path==="/processor/output"&&request.method==="PUT"){
   const key=url.searchParams.get("key");
   if(!key||!new RegExp("^hls/"+user.id.replace(/[.*+?^$\{\}()|[\]\\]/g,"\\  return reply({error:"Rota inexistente"},404);")+"/[a-zA-Z0-9_-]+/(index\\.m3u8|segment_[0-9]{5}\\.ts)$").test(key))return reply({error:"Destino inválido"},400);
   const type=key.endsWith(".m3u8")?"application/vnd.apple.mpegurl":"video/mp2t";
   if(Number(request.headers.get("content-length")||0)>25000000)return reply({error:"Segmento muito grande"},413);
   await env.VIDEOS.put(key,request.body,{httpMetadata:{contentType:type,cacheControl:"private, max-age=3600"}});
   return reply({ok:true,key});
  }
  return reply({error:"Rota inexistente"},404);
 }catch(e){return reply({error:"Falha ao processar operação no R2"},500)}
}}