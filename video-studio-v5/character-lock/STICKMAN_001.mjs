// Canonical STICKMAN_001 from the user's Character Engine V3. Only pose attributes may change.
export const CHARACTER_ID="STICKMAN_001";
export const VERSION="1.0.0";
export const MASTER="<g id=\"root\" transform=\"translate(100 195)\"><ellipse id=\"shadow\" cy=\"178\" rx=\"66\" ry=\"10\" fill=\"#000\" opacity=\".15\"/><g id=\"body\" stroke=\"#141414\" stroke-width=\"3.5\" stroke-linejoin=\"round\" stroke-linecap=\"round\"><g id=\"legL\" transform=\"translate(-20 50)\"><g id=\"shinL\" transform=\"translate(0 55)\"><path d=\"M0 0V65\" stroke-width=\"13\"/><path d=\"M0 0V65\" stroke=\"white\" stroke-width=\"6\"/><path d=\"M-6 61Q-25 62 -29 77L9 77Q15 72 7 61Z\" fill=\"white\"/><path d=\"M-27 72H9\" fill=\"none\"/></g><path d=\"M-20 -5H15L17 55H-20Z\" fill=\"#547ba0\"/><path d=\"M-20 47H17V55H-20Z\" fill=\"#81a0b9\"/></g><g id=\"legR\" transform=\"translate(20 50)\"><g id=\"shinR\" transform=\"translate(0 55)\"><path d=\"M0 0V65\" stroke-width=\"13\"/><path d=\"M0 0V65\" stroke=\"white\" stroke-width=\"6\"/><path d=\"M-7 61Q12 60 25 74L25 78H-10Z\" fill=\"white\"/><path d=\"M-8 73H24\" fill=\"none\"/></g><path d=\"M-15 -5H20L22 55H-17Z\" fill=\"#547ba0\"/><path d=\"M-17 47H22V55H-17Z\" fill=\"#81a0b9\"/></g><g id=\"armL\" transform=\"translate(-35 -48)\"><path d=\"M0 0V49\" stroke-width=\"14\"/><path d=\"M0 0V49\" stroke=\"white\" stroke-width=\"7\"/><g id=\"foreL\" transform=\"translate(0 49)\"><path d=\"M0 0V43\" stroke-width=\"14\"/><path d=\"M0 0V43\" stroke=\"white\" stroke-width=\"7\"/><ellipse cy=\"45\" rx=\"6\" ry=\"9\" fill=\"white\"/></g><path d=\"M-10 -5H12L14 28H-14Z\" fill=\"#242424\"/></g><g id=\"armR\" transform=\"translate(35 -48)\"><path d=\"M0 0V49\" stroke-width=\"14\"/><path d=\"M0 0V49\" stroke=\"white\" stroke-width=\"7\"/><g id=\"foreR\" transform=\"translate(0 49)\"><path d=\"M0 0V43\" stroke-width=\"14\"/><path d=\"M0 0V43\" stroke=\"white\" stroke-width=\"7\"/><ellipse cy=\"45\" rx=\"6\" ry=\"9\" fill=\"white\"/></g><path d=\"M-12 -5H10L14 28H-14Z\" fill=\"#242424\"/></g><path d=\"M-30 -58Q0 -70 30 -58L43 43Q0 67 -43 43Z\" fill=\"#242424\"/><path d=\"M-8 -82V-60Q0 -53 8 -60V-82\" fill=\"white\"/><g id=\"head\" transform=\"translate(0 -113)\"><ellipse cx=\"-46\" rx=\"11\" ry=\"16\" fill=\"white\"/><ellipse cx=\"46\" rx=\"11\" ry=\"16\" fill=\"white\"/><ellipse rx=\"47\" ry=\"49\" fill=\"white\"/><path d=\"M-48 -8Q-58 -32 -65 -37Q-49 -36 -56 -53Q-32 -46 -17 -66Q-12 -56 7 -62Q27 -63 31 -73Q43 -59 40 -52Q61 -54 65 -40L50 -42Q55 -20 45 -7L36 -31Q7 -18 -14 -34Q-25 -11 -48 -8Z\" fill=\"#181818\"/><g id=\"eyes\" fill=\"#101010\" stroke=\"none\"><ellipse cx=\"-17\" cy=\"1\" rx=\"5.5\" ry=\"9\"/><ellipse cx=\"17\" cy=\"1\" rx=\"5.5\" ry=\"9\"/></g><path id=\"brows\" d=\"M-25 -15Q-17 -21 -9 -15M9 -15Q17 -21 25 -15\" fill=\"none\"/><path id=\"mouth\" d=\"M-13 23Q0 35 13 23\" fill=\"none\"/></g></g></g>";
export const FINGERPRINT="4f963f7b";
export function verifyMaster(){
 let h=2166136261;for(const c of MASTER)h=Math.imul(h^c.charCodeAt(0),16777619)>>>0;
 if(h.toString(16).padStart(8,"0")!==FINGERPRINT)throw Error("Character Lock mismatch");
 return true;
}
export const MOTIONS=Object.freeze(["idle","walk","run","sit","talk","wave"]);
export const EXPRESSIONS=Object.freeze(["happy","sad","angry","surprised"]);
export function characterSVG({id=CHARACTER_ID,frame=0,fps=60,motion="idle",expression="happy"}={}){
 verifyMaster();if(id!==CHARACTER_ID||!MOTIONS.includes(motion)||!EXPRESSIONS.includes(expression)||!Number.isFinite(frame)||frame<0||!Number.isFinite(fps)||fps<=0)throw Error("Invalid character pose");
 const t=frame/fps,move=motion==="walk"||motion==="run",run=motion==="run",sit=motion==="sit",talk=motion==="talk";
 const p=t*(run?12:6),c=Math.cos(p),a=move?(run?40:24)*Math.sin(p):0;
 let svg=MASTER;
 const rot=(id,x,y,angle)=>{svg=svg.replace(new RegExp('(<g id="'+id+'" transform=")[^"]+(")'),(_,a,b)=>a+'translate('+x+' '+y+') rotate('+angle.toFixed(4)+')'+b)};
 rot("legL",-20,50,sit?-65:a);rot("legR",20,50,sit?-65:-a);
 rot("shinL",0,55,sit?75:move?Math.max(0,-c)*35:0);rot("shinR",0,55,sit?75:move?Math.max(0,c)*35:0);
 rot("armL",-35,-48,move?-a:8);rot("armR",35,-48,motion==="wave"?-145+12*Math.sin(t*7):move?a:-8);
 rot("foreL",0,49,move?-20:0);rot("foreR",0,49,motion==="wave"||move?-20:0);rot("head",0,-113,Math.sin(t*2)*2);
 const bob=sit?45:move?-Math.abs(c)*8:Math.sin(t*2)*1.5;
 svg=svg.replace('<g id="body"','<g id="body" transform="translate(0 '+bob.toFixed(4)+') rotate('+(run?-5:move?-2:0)+')"');
 if(t%4.2>4.04)svg=svg.replaceAll('rx="5.5" ry="9"','rx="5.5" ry="0.8"');
 const mouth=talk?'M-11 23Q0 '+(23-5*Math.abs(Math.sin(t*13)))+' 11 23Q0 '+(25+15*Math.abs(Math.sin(t*13)))+' -11 23Z':expression==="sad"||expression==="angry"?'M-13 30Q0 17 13 30':expression==="surprised"?'M0 17C-12 17 -12 35 0 35S12 17 0 17Z':'M-13 23Q0 35 13 23';
 svg=svg.replace(/(<path id="mouth" d=")[^"]+(" fill=")[^"]+(")/,(_,a,b,c)=>a+mouth+b+(talk||expression==="surprised"?"#222":"none")+c);
 const brows=expression==="angry"?'M-25 -20L-9 -12M9 -12L25 -20':expression==="sad"?'M-25 -12L-9 -20M9 -20L25 -12':'M-25 -15Q-17 -21 -9 -15M9 -15Q17 -21 25 -15';
 svg=svg.replace(/(<path id="brows" d=")[^"]+(")/,(_,a,b)=>a+brows+b);
 return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-45 -10 290 415" data-character="'+CHARACTER_ID+'" data-version="'+VERSION+'">'+svg+'</svg>';
}
