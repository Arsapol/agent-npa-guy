// CommonJS Version //
(function(){
    let _version = '0.2.2';
    console.log(`>> CommonJS v.${_version} <<`)
})()

// ---- LINE Bot ---- //
// Version 0.1.2
async function genBotlineLink(product, type, keyword, mode, flag_utm) {

    let setKeyWord = keyword;
    if(!keyword){
        setKeyWord = "KBank Web > ปรึกษาเกี่ยวกับประกัน";
    }

    let text = "";
    let link = "https://liff.line.me/1564696848-7Rv6eXEq/commonFlow?commonFlowID=Chatbot_ENC_Ver&source=Chatbot_ENC_Ver&data=";

    if (mode === "qr") {
        link = "https://liff.line.me/1564696848-7Rv6eXEq/commonFlow?commonFlowID=Chatbot_ENC_Ver%26source=Chatbot_ENC_Ver%26data=";
    }

    if(flag_utm != undefined){
        if(flag_utm == 1){
            try{
                link = _utmx.setURL("https://liff.line.me/1564696848-7Rv6eXEq/commonFlow?commonFlowID=Chatbot_ENC_Ver&source=Chatbot_ENC_Ver&data=").addUTM().href;
            }catch(err){
                consolg.err(err)
            }
        }
    }

    if (type.toLowerCase() === "mf") {
        text = `headerText=ตามที่คุณสนใจกองทุน ${product}&body=หากคุณต้องการผู้เชี่ยวชาญมาดูแลและให้คำแนะนำเพิ่มเติม กรุณากดปุ่มด้านล่าง หรือพิมพ์เรื่องที่ต้องการสอบถามได้เลยค่ะ\n\nโดยช่วงเวลาให้บริการของผู้เชี่ยวชาญดังนี้นะคะ\n- วันจันทร์-ศุกร์ เวลา 8.30-17.00 น.\n- วันหยุดเสาร์-อาทิตย์ และนักขัตฤกษ์ เวลา 10.30-17.00 น.\n\nหากนอกเวลาดังกล่าว คุณยังสามารถสอบถามข้อมูลประกันได้ตลอด 24 ชั่วโมงนะคะ โดยจะมีเจ้าหน้าที่ K-Contact Center มาดูแลและให้ข้อมูลลูกค้าผ่านช่องทาง Line KBank Live ค่ะ&buttonLabel=ปรึกษาผู้เชี่ยวชาญ&buttonColor=#00a94f&keyword=KBank Web > ปรึกษาเกี่ยวกับกองทุน (Persona)`;
    } else if (type.toLowerCase() === "wealthplus") {
        text = `body=หากคุณต้องการปรึกษาเกี่ยวกับการลงทุน Wealth PLUS กับผู้เชี่ยวชาญ\n\nกรุณากดปุ่มด้านล่าง\nหรือพิมพ์เรื่องที่ต้องการสอบถามได้เลยค่ะ&buttonLabel=ปรึกษาผู้เชี่ยวชาญ&buttonColor=#00a94f&keyword=KBank Web > Wealth Plus (Persona)`;
    } else if (type.toLowerCase() === "ba") {
        text = `headerText=ตามที่คุณสนใจประกัน\n ${product}&body=หากคุณต้องการผู้เชี่ยวชาญมาดูแล\nและให้คำแนะนำเพิ่มเติม กรุณากดปุ่มด้านล่าง หรือพิมพ์เรื่องที่ต้องการสอบถามได้เลยค่ะ\n\nโดยช่วงเวลาให้บริการของผู้เชี่ยวชาญดังนี้นะคะ\n- วันจันทร์-ศุกร์ เวลา 8.30-17.00 น.\n- วันหยุดเสาร์-อาทิตย์ และนักขัตฤกษ์ เวลา 10.30-17.00 น.\n\nหากนอกเวลาดังกล่าว คุณยังสามารถสอบถามข้อมูลประกันได้ตลอด 24 ชั่วโมงนะคะ โดยจะมีเจ้าหน้าที่\n K-Contact Center มาดูแลและให้ข้อมูลลูกค้าผ่านช่องทาง Line KBank Live ค่ะ&buttonLabel=ปรึกษาผู้เชี่ยวชาญ&buttonColor=#00a94f&keyword=${setKeyWord}`;
    }

    let textEncypt = await encryptAES256(text);
    //let encodeText = encodeURIComponent(textEncypt);
    let genlink = splitANCHOR(link+textEncypt, mode);
   //callback(genlink);
   return genlink;
}
(function (window) {
    async function encryptAES256(plainText) {
        const _iv = new Uint8Array(16);
        const _key = Uint8Array.from(atob('NWVhNDc4ODE1NDNhNDQ3OGE5NjJkNzU0ZGI4OWQ5OTc='), c => c.charCodeAt(0));
        const _algorithm = {
            name: 'AES-CBC',
            iv: _iv
        };
        const _cryptoKey = await crypto.subtle.importKey('raw', _key, _algorithm, false, ['encrypt']);
        const _encrypted = await crypto.subtle.encrypt(_algorithm, _cryptoKey, new TextEncoder().encode(plainText));
        return window.btoa(String.fromCharCode(...new Uint8Array(_encrypted)));
    }
    async function decryptAES256(cipherText) {
        const _iv = new Uint8Array(16);
        const _key = Uint8Array.from(atob('NWVhNDc4ODE1NDNhNDQ3OGE5NjJkNzU0ZGI4OWQ5OTc='), c => c.charCodeAt(0));
        const _algorithm = {
            name: 'AES-CBC',
            iv: _iv
        };
        const _cryptoKey = await crypto.subtle.importKey('raw', _key, _algorithm, false, ['decrypt']);
        const _decrypted = await crypto.subtle.decrypt(_algorithm, _cryptoKey, base64ToArrayBuffer(cipherText));
        return new TextDecoder().decode(_decrypted);
    }

    function base64ToArrayBuffer(base64) {
        const binaryString = atob(base64);
        const binaryLen = binaryString.length;
        const bytes = new Uint8Array(binaryLen);
        for (let i = 0; i < binaryLen; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        return bytes.buffer;
    }
    window.encryptAES256 = encryptAES256;
    window.decryptAES256 = decryptAES256;
})(window);

// ---- QR Code ---- //
// Version 0.1.0
var qrcodegen;!function(t){class e{constructor(t,i,s,o){if(this.version=t,this.errorCorrectionLevel=i,this.modules=[],this.isFunction=[],t<e.MIN_VERSION||t>e.MAX_VERSION)throw RangeError("Version value out of range");if(o<-1||o>7)throw RangeError("Mask value out of range");this.size=4*t+17;let n=[];for(let l=0;l<this.size;l++)n.push(!1);for(let $=0;$<this.size;$++)this.modules.push(n.slice()),this.isFunction.push(n.slice());this.drawFunctionPatterns();let a=this.addEccAndInterleave(s);if(this.drawCodewords(a),-1==o){let h=1e9;for(let u=0;u<8;u++){this.applyMask(u),this.drawFormatBits(u);let _=this.getPenaltyScore();_<h&&(o=u,h=_),this.applyMask(u)}}r(0<=o&&o<=7),this.mask=o,this.applyMask(o),this.drawFormatBits(o),this.isFunction=[]}static encodeText(i,s){let r=t.QrSegment.makeSegments(i);return e.encodeSegments(r,s)}static encodeBinary(i,s){let r=t.QrSegment.makeBytes(i);return e.encodeSegments([r],s)}static encodeSegments(t,s,n=1,l=40,$=-1,a=!0){if(!(e.MIN_VERSION<=n&&n<=l&&l<=e.MAX_VERSION)||$<-1||$>7)throw RangeError("Invalid value");let h,u;for(h=n;;h++){let _=8*e.getNumDataCodewords(h,s),d=o.getTotalBits(t,h);if(d<=_){u=d;break}if(h>=l)throw RangeError("Data too long")}for(let c of[e.Ecc.MEDIUM,e.Ecc.QUARTILE,e.Ecc.HIGH])a&&u<=8*e.getNumDataCodewords(h,c)&&(s=c);let f=[];for(let m of t)for(let g of(i(m.mode.modeBits,4,f),i(m.numChars,m.mode.numCharCountBits(h),f),m.getData()))f.push(g);r(f.length==u);let C=8*e.getNumDataCodewords(h,s);r(f.length<=C),i(0,Math.min(4,C-f.length),f),i(0,(8-f.length%8)%8,f),r(f.length%8==0);for(let E=236;f.length<C;E^=253)i(E,8,f);let N=[];for(;8*N.length<f.length;)N.push(0);return f.forEach((t,e)=>N[e>>>3]|=t<<7-(7&e)),new e(h,s,N,$)}getModule(t,e){return 0<=t&&t<this.size&&0<=e&&e<this.size&&this.modules[e][t]}drawFunctionPatterns(){for(let t=0;t<this.size;t++)this.setFunctionModule(6,t,t%2==0),this.setFunctionModule(t,6,t%2==0);this.drawFinderPattern(3,3),this.drawFinderPattern(this.size-4,3),this.drawFinderPattern(3,this.size-4);let e=this.getAlignmentPatternPositions(),i=e.length;for(let s=0;s<i;s++)for(let r=0;r<i;r++)0==s&&0==r||0==s&&r==i-1||s==i-1&&0==r||this.drawAlignmentPattern(e[s],e[r]);this.drawFormatBits(0),this.drawVersion()}drawFormatBits(t){let e=this.errorCorrectionLevel.formatBits<<3|t,i=e;for(let o=0;o<10;o++)i=i<<1^(i>>>9)*1335;let n=(e<<10|i)^21522;r(n>>>15==0);for(let l=0;l<=5;l++)this.setFunctionModule(8,l,s(n,l));this.setFunctionModule(8,7,s(n,6)),this.setFunctionModule(8,8,s(n,7)),this.setFunctionModule(7,8,s(n,8));for(let $=9;$<15;$++)this.setFunctionModule(14-$,8,s(n,$));for(let a=0;a<8;a++)this.setFunctionModule(this.size-1-a,8,s(n,a));for(let h=8;h<15;h++)this.setFunctionModule(8,this.size-15+h,s(n,h));this.setFunctionModule(8,this.size-8,!0)}drawVersion(){if(this.version<7)return;let t=this.version;for(let e=0;e<12;e++)t=t<<1^(t>>>11)*7973;let i=this.version<<12|t;r(i>>>18==0);for(let o=0;o<18;o++){let n=s(i,o),l=this.size-11+o%3,$=Math.floor(o/3);this.setFunctionModule(l,$,n),this.setFunctionModule($,l,n)}}drawFinderPattern(t,e){for(let i=-4;i<=4;i++)for(let s=-4;s<=4;s++){let r=Math.max(Math.abs(s),Math.abs(i)),o=t+s,n=e+i;0<=o&&o<this.size&&0<=n&&n<this.size&&this.setFunctionModule(o,n,2!=r&&4!=r)}}drawAlignmentPattern(t,e){for(let i=-2;i<=2;i++)for(let s=-2;s<=2;s++)this.setFunctionModule(t+s,e+i,1!=Math.max(Math.abs(s),Math.abs(i)))}setFunctionModule(t,e,i){this.modules[e][t]=i,this.isFunction[e][t]=!0}addEccAndInterleave(t){let i=this.version,s=this.errorCorrectionLevel;if(t.length!=e.getNumDataCodewords(i,s))throw RangeError("Invalid argument");let o=e.NUM_ERROR_CORRECTION_BLOCKS[s.ordinal][i],n=e.ECC_CODEWORDS_PER_BLOCK[s.ordinal][i],l=Math.floor(e.getNumRawDataModules(i)/8),$=o-l%o,a=Math.floor(l/o),h=[],u=e.reedSolomonComputeDivisor(n);for(let _=0,d=0;_<o;_++){let c=t.slice(d,d+a-n+(_<$?0:1));d+=c.length;let f=e.reedSolomonComputeRemainder(c,u);_<$&&c.push(0),h.push(c.concat(f))}let m=[];for(let g=0;g<h[0].length;g++)h.forEach((t,e)=>{(g!=a-n||e>=$)&&m.push(t[g])});return r(m.length==l),m}drawCodewords(t){if(t.length!=Math.floor(e.getNumRawDataModules(this.version)/8))throw RangeError("Invalid argument");let i=0;for(let o=this.size-1;o>=1;o-=2){6==o&&(o=5);for(let n=0;n<this.size;n++)for(let l=0;l<2;l++){let $=o-l,a=(o+1&2)==0,h=a?this.size-1-n:n;!this.isFunction[h][$]&&i<8*t.length&&(this.modules[h][$]=s(t[i>>>3],7-(7&i)),i++)}}r(i==8*t.length)}applyMask(t){if(t<0||t>7)throw RangeError("Mask value out of range");for(let e=0;e<this.size;e++)for(let i=0;i<this.size;i++){let s;switch(t){case 0:s=(i+e)%2==0;break;case 1:s=e%2==0;break;case 2:s=i%3==0;break;case 3:s=(i+e)%3==0;break;case 4:s=(Math.floor(i/3)+Math.floor(e/2))%2==0;break;case 5:s=i*e%2+i*e%3==0;break;case 6:s=(i*e%2+i*e%3)%2==0;break;case 7:s=((i+e)%2+i*e%3)%2==0;break;default:throw Error("Unreachable")}!this.isFunction[e][i]&&s&&(this.modules[e][i]=!this.modules[e][i])}}getPenaltyScore(){let t=0;for(let i=0;i<this.size;i++){let s=!1,o=0,n=[0,0,0,0,0,0,0];for(let l=0;l<this.size;l++)this.modules[i][l]==s?5==++o?t+=e.PENALTY_N1:o>5&&t++:(this.finderPenaltyAddHistory(o,n),s||(t+=this.finderPenaltyCountPatterns(n)*e.PENALTY_N3),s=this.modules[i][l],o=1);t+=this.finderPenaltyTerminateAndCount(s,o,n)*e.PENALTY_N3}for(let $=0;$<this.size;$++){let a=!1,h=0,u=[0,0,0,0,0,0,0];for(let _=0;_<this.size;_++)this.modules[_][$]==a?5==++h?t+=e.PENALTY_N1:h>5&&t++:(this.finderPenaltyAddHistory(h,u),a||(t+=this.finderPenaltyCountPatterns(u)*e.PENALTY_N3),a=this.modules[_][$],h=1);t+=this.finderPenaltyTerminateAndCount(a,h,u)*e.PENALTY_N3}for(let d=0;d<this.size-1;d++)for(let c=0;c<this.size-1;c++){let f=this.modules[d][c];f==this.modules[d][c+1]&&f==this.modules[d+1][c]&&f==this.modules[d+1][c+1]&&(t+=e.PENALTY_N2)}let m=0;for(let g of this.modules)m=g.reduce((t,e)=>t+(e?1:0),m);let C=this.size*this.size,E=Math.ceil(Math.abs(20*m-10*C)/C)-1;return r(0<=E&&E<=9),r(0<=(t+=E*e.PENALTY_N4)&&t<=2568888),t}getAlignmentPatternPositions(){if(1==this.version)return[];{let t=Math.floor(this.version/7)+2,e=32==this.version?26:2*Math.ceil((4*this.version+4)/(2*t-2)),i=[6];for(let s=this.size-7;i.length<t;s-=e)i.splice(1,0,s);return i}}static getNumRawDataModules(t){if(t<e.MIN_VERSION||t>e.MAX_VERSION)throw RangeError("Version number out of range");let i=(16*t+128)*t+64;if(t>=2){let s=Math.floor(t/7)+2;i-=(25*s-10)*s-55,t>=7&&(i-=36)}return r(208<=i&&i<=29648),i}static getNumDataCodewords(t,i){return Math.floor(e.getNumRawDataModules(t)/8)-e.ECC_CODEWORDS_PER_BLOCK[i.ordinal][t]*e.NUM_ERROR_CORRECTION_BLOCKS[i.ordinal][t]}static reedSolomonComputeDivisor(t){if(t<1||t>255)throw RangeError("Degree out of range");let i=[];for(let s=0;s<t-1;s++)i.push(0);i.push(1);let r=1;for(let o=0;o<t;o++){for(let n=0;n<i.length;n++)i[n]=e.reedSolomonMultiply(i[n],r),n+1<i.length&&(i[n]^=i[n+1]);r=e.reedSolomonMultiply(r,2)}return i}static reedSolomonComputeRemainder(t,i){let s=i.map(t=>0);for(let r of t){let o=r^s.shift();s.push(0),i.forEach((t,i)=>s[i]^=e.reedSolomonMultiply(t,o))}return s}static reedSolomonMultiply(t,e){if(t>>>8!=0||e>>>8!=0)throw RangeError("Byte out of range");let i=0;for(let s=7;s>=0;s--)i=i<<1^(i>>>7)*285,i^=(e>>>s&1)*t;return r(i>>>8==0),i}finderPenaltyCountPatterns(t){let e=t[1];r(e<=3*this.size);let i=e>0&&t[2]==e&&t[3]==3*e&&t[4]==e&&t[5]==e;return(i&&t[0]>=4*e&&t[6]>=e?1:0)+(i&&t[6]>=4*e&&t[0]>=e?1:0)}finderPenaltyTerminateAndCount(t,e,i){return t&&(this.finderPenaltyAddHistory(e,i),e=0),e+=this.size,this.finderPenaltyAddHistory(e,i),this.finderPenaltyCountPatterns(i)}finderPenaltyAddHistory(t,e){0==e[0]&&(t+=this.size),e.pop(),e.unshift(t)}}function i(t,e,i){if(e<0||e>31||t>>>e!=0)throw RangeError("Value out of range");for(let s=e-1;s>=0;s--)i.push(t>>>s&1)}function s(t,e){return(t>>>e&1)!=0}function r(t){if(!t)throw Error("Assertion error")}e.MIN_VERSION=1,e.MAX_VERSION=40,e.PENALTY_N1=3,e.PENALTY_N2=3,e.PENALTY_N3=40,e.PENALTY_N4=10,e.ECC_CODEWORDS_PER_BLOCK=[[-1,7,10,15,20,26,18,20,24,30,18,20,24,26,30,22,24,28,30,28,28,28,28,30,30,26,28,30,30,30,30,30,30,30,30,30,30,30,30,30,30],[-1,10,16,26,18,24,16,18,22,22,26,30,22,22,24,24,28,28,26,26,26,26,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28,28],[-1,13,22,18,26,18,24,18,22,20,24,28,26,24,20,30,24,28,28,26,30,28,30,30,30,30,28,30,30,30,30,30,30,30,30,30,30,30,30,30,30],[-1,17,28,22,16,22,28,26,26,24,28,24,28,22,24,24,30,28,28,26,28,30,24,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30,30]],e.NUM_ERROR_CORRECTION_BLOCKS=[[-1,1,1,1,1,1,2,2,2,2,4,4,4,4,4,6,6,6,6,7,8,8,9,9,10,12,12,12,13,14,15,16,17,18,19,19,20,21,22,24,25],[-1,1,1,1,2,2,4,4,4,5,5,5,8,9,9,10,10,11,13,14,16,17,17,18,20,21,23,25,26,28,29,31,33,35,37,38,40,43,45,47,49],[-1,1,1,2,2,4,4,6,6,8,8,8,10,12,16,12,17,16,18,21,20,23,23,25,27,29,34,34,35,38,40,43,45,48,51,53,56,59,62,65,68],[-1,1,1,2,4,4,4,5,6,8,8,11,11,16,16,18,16,19,21,25,25,25,34,30,32,35,37,40,42,45,48,51,54,57,60,63,66,70,74,77,81]],t.QrCode=e;class o{constructor(t,e,i){if(this.mode=t,this.numChars=e,this.bitData=i,e<0)throw RangeError("Invalid argument");this.bitData=i.slice()}static makeBytes(t){let e=[];for(let s of t)i(s,8,e);return new o(o.Mode.BYTE,t.length,e)}static makeNumeric(t){if(!o.isNumeric(t))throw RangeError("String contains non-numeric characters");let e=[];for(let s=0;s<t.length;){let r=Math.min(t.length-s,3);i(parseInt(t.substring(s,s+r),10),3*r+1,e),s+=r}return new o(o.Mode.NUMERIC,t.length,e)}static makeAlphanumeric(t){if(!o.isAlphanumeric(t))throw RangeError("String contains unencodable characters in alphanumeric mode");let e=[],s;for(s=0;s+2<=t.length;s+=2){let r=45*o.ALPHANUMERIC_CHARSET.indexOf(t.charAt(s));i(r+=o.ALPHANUMERIC_CHARSET.indexOf(t.charAt(s+1)),11,e)}return s<t.length&&i(o.ALPHANUMERIC_CHARSET.indexOf(t.charAt(s)),6,e),new o(o.Mode.ALPHANUMERIC,t.length,e)}static makeSegments(t){return""==t?[]:o.isNumeric(t)?[o.makeNumeric(t)]:o.isAlphanumeric(t)?[o.makeAlphanumeric(t)]:[o.makeBytes(o.toUtf8ByteArray(t))]}static makeEci(t){let e=[];if(t<0)throw RangeError("ECI assignment value out of range");if(t<128)i(t,8,e);else if(t<16384)i(2,2,e),i(t,14,e);else if(t<1e6)i(6,3,e),i(t,21,e);else throw RangeError("ECI assignment value out of range");return new o(o.Mode.ECI,0,e)}static isNumeric(t){return o.NUMERIC_REGEX.test(t)}static isAlphanumeric(t){return o.ALPHANUMERIC_REGEX.test(t)}getData(){return this.bitData.slice()}static getTotalBits(t,e){let i=0;for(let s of t){let r=s.mode.numCharCountBits(e);if(s.numChars>=1<<r)return 1/0;i+=4+r+s.bitData.length}return i}static toUtf8ByteArray(t){t=encodeURI(t);let e=[];for(let i=0;i<t.length;i++)"%"!=t.charAt(i)?e.push(t.charCodeAt(i)):(e.push(parseInt(t.substring(i+1,i+3),16)),i+=2);return e}}o.NUMERIC_REGEX=/^[0-9]*$/,o.ALPHANUMERIC_REGEX=/^[A-Z0-9 $%*+.\/:-]*$/,o.ALPHANUMERIC_CHARSET="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:",t.QrSegment=o}(qrcodegen||(qrcodegen={})),function(t){var e;!function(t){class e{constructor(t,e){this.ordinal=t,this.formatBits=e}}e.LOW=new e(0,1),e.MEDIUM=new e(1,0),e.QUARTILE=new e(2,3),e.HIGH=new e(3,2),t.Ecc=e}(e=t.QrCode||(t.QrCode={}))}(qrcodegen||(qrcodegen={})),function(t){var e;!function(t){class e{constructor(t,e){this.modeBits=t,this.numBitsCharCount=e}numCharCountBits(t){return this.numBitsCharCount[Math.floor((t+7)/17)]}}e.NUMERIC=new e(1,[10,12,14]),e.ALPHANUMERIC=new e(2,[9,11,13]),e.BYTE=new e(4,[8,16,16]),e.KANJI=new e(8,[8,10,12]),e.ECI=new e(7,[0,0,0]),t.Mode=e}(e=t.QrSegment||(t.QrSegment={}))}(qrcodegen||(qrcodegen={}));
(function(){
    var head = document.getElementsByTagName('head')[0];
    var s = document.createElement('style'),
        css = `.ezyQR{border-width:20px;border-color:#FFF;border-style:solid;}.ezyQR-wrapper{display:inline-block;font-size:0px;}`;
    s.setAttribute('type', 'text/css');
    if (s.styleSheet) {
        s.styleSheet.cssText = css;
    } else {
        s.appendChild(document.createTextNode(css));
    }
    head.appendChild(s);
})();
function drawCanvas(qr, scale, border, lightColor, darkColor, canvas) {
    if (scale <= 0 || border < 0) throw new RangeError("Value out of range");
    const width = (qr.size + border * 2) * scale;
    canvas.width = width;
    canvas.height = width;
    let ctx = canvas.getContext("2d");
    for (let y = -border; y < qr.size + border; y++) {
        for (let x = -border; x < qr.size + border; x++) {
            ctx.fillStyle = qr.getModule(x, y) ? darkColor : lightColor;
            ctx.fillRect((x + border) * scale, (y + border) * scale, scale, scale);
        }
    }
}
function toSvgString(qr, border, lightColor, darkColor) {
    if (border < 0) throw new RangeError("Border must be non-negative");
    let parts = [];
    for (let y = 0; y < qr.size; y++) {
        for (let x = 0; x < qr.size; x++) {
            if (qr.getModule(x, y))
                parts.push(`M${x + border},${y + border}h1v1h-1z`);
        }
    }
    return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" viewBox="0 0 ${qr.size + border * 2} ${qr.size + border * 2}" stroke="none">
<rect width="100%" height="100%" fill="${lightColor}"/>
<path d="${parts.join(" ")}" fill="${darkColor}"/>
</svg>
`;
}
var KB_QR_Generator = function (elm ,msg, quality) {
    const QRC = qrcodegen.QrCode;
    const segs = qrcodegen.QrSegment.makeSegments(msg);
    
    if(quality == undefined) {
        quality = 1;
    }

    let _quality = {
        1: QRC.Ecc.LOW,
        2: QRC.Ecc.MEDIUM,
        3: QRC.Ecc.QUARTILE,
        4: QRC.Ecc.HIGH
    }[quality];

    //const qr = qrcodegen.QrCode.encodeSegments(segs, ecl, minVer, maxVer, mask, boostEcc);
    const qr = QRC.encodeSegments(segs, _quality, 1, 40, -1, true);
    //
    const elm_canvas = typeof elm === 'string' ? document.querySelector(elm) : elm;
    const scale = 3;
    const border = 0;
    const lightColor = '#FFFFFF';
    const darkColor = '#000000';
    elm_canvas.classList.add('ezyQR');
    if(false){
        let wrapper = document.createElement('div');
        wrapper.classList.add('ezyQR-wrapper')
        elm_canvas.parentNode.insertBefore(wrapper, elm_canvas);
        wrapper.appendChild(elm_canvas);
    }
    //
    drawCanvas(qr, scale, border, lightColor, darkColor, elm_canvas);
}
// Helper
// KB_QR_Generator(element_id, text_message, [quality])

// =============== QR EZY Code =============== //
// elm - ไอดี element
// link - ลิ้งค์ URL ที่ต้องการ
// msg - ข้อความ
// type - ชนิดแคมเปญ
// keyword - คีย์เวิร์ด

// สร้าง QR พร้อมด้วยเก็บค่า UTM จากลิ้งค์ 
var EZYQR_UTM = function (elm, link, quality) {
    try {
        let _link = _utmx.setURL(link).addUTM().href;
        console.log(`EZYQR UTM => ${_link.slice(8)}`);
        KB_QR_Generator(elm, _link, quality);
    } catch (err) {
        console.log(">>>>>>>> UTM QR : Error");
        console.error(err);
    }
}

// สร้าง QR เพื่อนำไปใช้กับ LINE BOT จากข้อมูล
var EZYQR_LINEBOT = function (elm, msg, type, keyword) {
    genBotlineLink(msg, type, keyword).then((resp) => {
        console.log(`EZYQR LINEBOT => (${(new TextEncoder().encode(resp)).length})`);
        KB_QR_Generator(elm, resp, 1);
    });
}

// สร้าง QR พร้อมด้วยเก็บค่า UTM เพื่อนำไปใช้กับ LINE BOT จากข้อมูล
var EZYQR_LINEBOT_UTM = function (elm, msg, type, keyword) {
    try {
        let _link = _utmx.setURL("https://liff.line.me/1564696848-7Rv6eXEq/commonFlow?commonFlowID=Chatbot_ENC_Ver&source=Chatbot_ENC_Ver&data=").addUTM().href;
        genBotlineLink(msg, type, keyword, null, 1).then((resp) => {
            console.log(`EZYQR LINEBOT UTM => (${(new TextEncoder().encode(resp)).length}) https >> ${_link.slice(8)}`);
            KB_QR_Generator(elm, resp, 1);
        });
    } catch (err) {
        console.log(">>>>>>>> UTM LINEBOT QR : Error");
        console.error(err);
    }
}

// Sample //
/*
window.addEventListener('load', function(){
    console.log('==== QR Gen ====');
    // Link UTM
    EZYQR_UTM('#qr-Canvas', 'https://www.kasikornbank.com/th/personal/loan/personalloan/pages/xpressloan.aspx?aa=1&bb=2');
    // LINE BOT
    EZYQR_LINEBOT('#qr-Canvas2', "ประกันชีวิตและสุขภาพป่วยมีจ่าย IPD+OPD", "ba", "");
    // LINE BOT UTM
    EZYQR_LINEBOT_UTM('#qr-Canvas3', "ประกันชีวิตและสุขภาพป่วยมีจ่าย IPD+OPD", "ba", "");
});
*/