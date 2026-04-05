/* ============= :: UTM PassThrough :: ============ */
// Version 5.0.11 on 17/02/2025
// - Add UTM expire duration (1 hr.)
// - Add _cid parameter (not expire)
// - pass all utm to input[type="hidden"]
// - Call back function use >>> initUTMPassthrough({"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "_cid"})
// - User hashtag #icwUTMChecker in url for check utmPassthrough
// - showUTMPassthrough() for check utmPassthrough
// - Use a.px-getUTMXParams for get utmPassthrough values
// - Use a.px-forwardURLParams to forward url query string only
// - Generate User ID Cookies _utmx=UTMX2.1.2.12345678.2543842842
// - Add _utmx instance with method chaining >> _utmx.setURL({url}).addUTM().addCID().addParams().clean().href
// - Add condition utm from url referer
// - Add Fixed URL automate forward utm cache 
// - Update Fixed URL automate forward utm cache 
// - Remove debug log, edit log text incorrectly rendered
// - update _host
// - edit encode_redirectUTM to change %20 back to space (cancel on v5.0.9)
// - edit getUTMXCache with encodeURI value for _search (cancel on v5.0.10)
// - add _host uatinsure and prodinsure


// Revamp-function
var _sessionStorage = {
    duration: 3600,
    setItem (cName, cValue) {
        let _utmArray = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "_cid"],
            _isUTM = _utmArray.some( a => a == cName),
            _checkExpireExist = this.getCookie("utmx_expire");
        //
        if(_checkExpireExist == null){
            this.setCookie(cName, cValue, this.duration);
        }else{
            this.setCookieDate(cName, cValue, _checkExpireExist);
        }
        //
        sessionStorage.setItem(cName, cValue);
    },
    getItem (cName) {
        return this.getCookie(cName);
    },
    removeItem (cName) {
        document.cookie = `${cName}=; max-age=0; path=/`;
        sessionStorage.removeItem(cName);
    },
    setCookie (cName, cValue, expMinutes){
        var _expires = "";
        if (expMinutes) {
            let date = new Date();
            date.setTime(date.getTime()+(expMinutes*1000));
            _expires = `; expires=${date.toGMTString()}`;
        }
        document.cookie = `${cName}=${cValue}${_expires}; path=/`;
    },
    setCookieDate (cName, cValue, expDatetime){
        var _expires = "";
        let date = new Date(+expDatetime);
        _expires = `; expires=${date.toGMTString()}`;
        document.cookie = `${cName}=${cValue}${_expires}; path=/`;
    },
    getCookie(cName) {
        var _na = cName+"=",
            _ca = document.cookie.split('; ').find(function(s){ return s.startsWith(_na)}) || null;
        if(_ca == null) return null;
        return _ca.split("=")[1];
    }
}

// Active UTM Passthrough
;(async function(w, doc, reset, h){
    // Protect
    let _server = await nsLocation(location.hostname),
        _host = [
            'bf208c05294f70ba4eeec4eaeaec41e3841cbc65f416af0774a68a12f5b1f5ee',
            '29f5d989b7514448290491d68798d98fb08384cc9b055b1a400de488b8aa4100',
            '09c964b20d56201969d74a59b405bd6bccd7e14aac3880c48daf3c8f0b715439',
            '49960de5880e8c687434170f6476605b8fe4aeb9a28632c7995cf3ba831d9763',
            '344f847a90468619b7bdb61d2d10dbeeaf40021303e2909419657218c64316df',
            '325f197d88d8de8095250776a563405a30ba077254c9b99cfb666518a4973d7b',
            'a4f2e6ef2595b93687725bb1200edb106d2ab82a7c2b1404fb5299f5c9aa6a87',
            '890ad41d2d54224186bba46fd22b9e59e5a95c92f8fcfc5c80c7949c78625c44',
            '325f197d88d8de8095250776a563405a30ba077254c9b99cfb666518a4973d7b'
        ];
    async function nsLocation(x) {
        const msgUint8 = new TextEncoder().encode(x);
        const hashBuffer = await crypto.subtle.digest("SHA-256", msgUint8);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
        return hashHex;
    }
    if(!_host.some(a => a === _server)) return ">> utmPassthrough has domain protected!";
    if(typeof w._utmx == 'object') return ">> Duplicate utmPassthrough has been protected!";

    const __$ = doc.querySelector.bind(document);
    const __$$ = doc.querySelectorAll.bind(document);

    var _version = "5.0.11",
        _allowLog = !0,
        _utm = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "_cid"], // Default parameters
        _configExpireCID = false, // Use CID Timestamp
        _duration = 3600, // Seconds of duration
        _reset = reset || ![], // Overwrite UTM
        _t0 = performance.now(),
        _params = getSearchParams(w.location.search),
        _stamp = cid_stamp = Date.now(),
        _expire = _stamp + _duration*1e3,
        GET_expired_UTM = _sessionStorage.getItem("utmx_expire"),
        GET_expired_CID = _sessionStorage.getItem("cidx_expire"),
        HAS_session_UTM = _sessionStorage.getItem("utmx_start") != null,
        Base64 = {_keyStr:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",encode:function(r){var t,e,o,a,h,n,c,d="",C=0;for(r=Base64._utf8_encode(r);C<r.length;)a=(t=r.charCodeAt(C++))>>2,h=(3&t)<<4|(e=r.charCodeAt(C++))>>4,n=(15&e)<<2|(o=r.charCodeAt(C++))>>6,c=63&o,isNaN(e)?n=c=64:isNaN(o)&&(c=64),d=d+this._keyStr.charAt(a)+this._keyStr.charAt(h)+this._keyStr.charAt(n)+this._keyStr.charAt(c);return d},decode:function(r){var t,e,o,a,h,n,c="",d=0;for(r=r.replace(/[^A-Za-z0-9\+\/\=]/g,"");d<r.length;)t=this._keyStr.indexOf(r.charAt(d++))<<2|(a=this._keyStr.indexOf(r.charAt(d++)))>>4,e=(15&a)<<4|(h=this._keyStr.indexOf(r.charAt(d++)))>>2,o=(3&h)<<6|(n=this._keyStr.indexOf(r.charAt(d++))),c+=String.fromCharCode(t),64!=h&&(c+=String.fromCharCode(e)),64!=n&&(c+=String.fromCharCode(o));return c=Base64._utf8_decode(c)},_utf8_encode:function(r){r=r.replace(/\r\n/g,"\n");for(var t="",e=0;e<r.length;e++){var o=r.charCodeAt(e);o<128?t+=String.fromCharCode(o):o>127&&o<2048?(t+=String.fromCharCode(o>>6|192),t+=String.fromCharCode(63&o|128)):(t+=String.fromCharCode(o>>12|224),t+=String.fromCharCode(o>>6&63|128),t+=String.fromCharCode(63&o|128))}return t},_utf8_decode:function(r){for(var t="",e=0,o=c1=c2=0;e<r.length;)(o=r.charCodeAt(e))<128?(t+=String.fromCharCode(o),e++):o>191&&o<224?(c2=r.charCodeAt(e+1),t+=String.fromCharCode((31&o)<<6|63&c2),e+=2):(c2=r.charCodeAt(e+1),c3=r.charCodeAt(e+2),t+=String.fromCharCode((15&o)<<12|(63&c2)<<6|63&c3),e+=3);return t}},
        _uid = getCookie("_utmxid") || g_deepUID("_utmxid"),
        _regDomainName = /^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)/i,
        _referrerName = 'kasikornbank',
        _defaults = {
            // When cache is null will return default value
            "utm_source" : "web_own",
            "utm_medium" : "direct_mass",
            "utm_term" : "kbank"
        },
        _automate_forwardCache_URL = [
            '/deeplink2020/',
            'https://www.kasikornasset.com',
            'https://mcb01.kasikornbank.com',
            'https://liff.line.me'
        ],
        _custom_redirect_params = ['flowURL', 'redirect'],
        _config_force_send_empty_utm = true,
        _alloc = false,
        _allowActivateUtilities = true,
        _initialSetup = false;


    let isReferrer = document.referrer;
    let hasSearchEngine;
    if (isReferrer) {
        isReferrer = isReferrer.match(/:\/\/(.[^/]+)/)[1];
        let getHostname = /(google|bing|yahoo)/g;
        hasSearchEngine  = isReferrer.match(getHostname);
    };
    
    if(_uid === null){
        _uid = generateUID(_version);
        setCookie("_utmxid", _uid);
        s_deepUID("_utmxid", _uid);
    }else{
        if(getCookie("_utmxid") == null) setCookie("_utmxid", _uid);
    }
    // Constructor
    initMain();
    /*
    doc.addEventListener("readystatechange", (evt) => {
        if(evt.target.readyState == "complete"){
            initMain();
        }
    })
    */
    

    // Methods
    function initMain(){
        
        // Initial Setup Protect
        if(_initialSetup) return '>>> utmx ready.';
        _initialSetup = true;
        
        // Declare Version
        _sessionStorage.setItem("utmx_version", _version);
        
        /* Custom for KA only */
        if(doc.referrer.length){
            _referrerName = (_regDomainName.exec(doc.referrer)['1']).toLowerCase().replace(/\.com$/ig,'');
        }
        
        // Installing UTM
        _allowLog && console.log(`%c • • • • utmx >> %c01 (compiler runtime) - Store utm value to cookies %c(${ get_performance() }ms)`,'color: #00a950','font-style:italic; color: #cddc39;','font-style:italic; color: #778922');
        if (Object.keys(_params).length && hasFocusParams(_params, _utm)) {
            // Set period timeout
            /utm_(source|medium|campaign|term|content|id)\=/.test(w.location.search) && set_utmTimeStamp(_stamp, _expire);
            _configExpireCID && /_cid\=/.test(w.location.search) && set_cidTimeStamp(_stamp, _expire);
            
            _utm.forEach(function(s, i){
                if (_params.hasOwnProperty(s)) {
                    if (_reset || _sessionStorage.getItem(s) === null) {
                        _sessionStorage.setItem(s, _params[s]);
                        _alloc = true;
                    }
                }
            });
            // Custom "Request. Thank you."
            if(true){
                {
                    // utm_term
                    let _ck = `${_params.hasOwnProperty('utm_term')?_params['utm_term']:"none"}!${w.location.hostname+w.location.pathname}`;
                    _sessionStorage.setItem('utm_term', _ck);
                }
                {
                    // utm_content
                    let _ck = `${_params.hasOwnProperty('utm_content')?_params['utm_content']:"none"}!${w.location.hostname+w.location.pathname}`;
                    _sessionStorage.setItem('utm_content', _ck);
                }
            }
            
            _alloc && _sessionStorage.setItem("utmx_entrance", w.location.hostname+w.location.pathname);
            _alloc && _sessionStorage.setItem("utmx_origin", w.location.pathname);
        }else{
            let _thisURL = w.location.hostname+w.location.pathname;
            if(_sessionStorage.getItem('utmx_start') == null){
                // Entrance Page
                if (hasSearchEngine && hasSearchEngine.length > 0) {
                    // Search Engine
                    let searchEngineName = hasSearchEngine[0];
                    clearAllUTMSession();
                    _sessionStorage.setItem("utm_source", searchEngineName);
                    _sessionStorage.setItem("utm_medium", "organic_seo");
                    // _sessionStorage.setItem("utm_campaign", "non_campaign");
                    _sessionStorage.setItem("utm_term", `kbank!${_thisURL}`);
                    _sessionStorage.setItem("utm_content", `none!${_thisURL}`);
                    _sessionStorage.setItem("utmx_entrance", _thisURL);
                    _sessionStorage.setItem("utmx_origin", w.location.pathname);
                    _sessionStorage.setItem("utmx_start", _stamp);
                    _sessionStorage.setItem("utmx_expire", _expire);
                } else if(_referrerName != 'kasikornbank') {
                    // Referral Configure for K-Main
                    clearAllUTMSession();
                    _sessionStorage.setItem("utm_source", _referrerName+'_earn');
                    _sessionStorage.setItem("utm_medium", "referral_mass");
                    // _sessionStorage.setItem("utm_campaign", "non_campaign");
                    _sessionStorage.setItem("utm_term", `kbank!${_thisURL}`);
                    _sessionStorage.setItem("utm_content", `none!${_thisURL}`);
                    _sessionStorage.setItem("utmx_entrance", _thisURL);
                    _sessionStorage.setItem("utmx_origin", w.location.pathname);
                    _sessionStorage.setItem("utmx_start", _stamp);
                    _sessionStorage.setItem("utmx_expire", _expire);
                } else if((doc.referrer == '') && !HAS_session_UTM){
                    // Direct
                    clearAllUTMSession();
                    _sessionStorage.setItem("utm_source", "web_own");
                    _sessionStorage.setItem("utm_medium", "direct_mass");
                    // _sessionStorage.setItem("utm_campaign", "non_campaign");
                    _sessionStorage.setItem("utm_term", `kbank!${_thisURL}`);
                    _sessionStorage.setItem("utm_content", `none!${_thisURL}`);
                    _sessionStorage.setItem("utmx_entrance", _thisURL);
                    _sessionStorage.setItem("utmx_origin", w.location.pathname);
                    _sessionStorage.setItem("utmx_start", _stamp);
                    _sessionStorage.setItem("utmx_expire", _expire);
                } 
            }else{
                // Internal journey page
                // Clear Expired
                clearExpiredSession(GET_expired_UTM, ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "utmx_entrance", "utmx_origin", "utmx_start", "utmx_expire"]);
                _configExpireCID && clearExpiredSession(GET_expired_CID, ["_cid"]);

                if(hasCookieUTM()){
                    // utm_content
                    if(_sessionStorage.getItem('utm_term') != null){
                        let _ck = `${_sessionStorage.getItem('utm_term').split('!')[0]}!${_thisURL}`;
                        _sessionStorage.setItem('utm_term', _ck);
                    }else{
                        let _ck = `none!${_thisURL}`;
                        _sessionStorage.setItem('utm_term', _ck);
                    }
                    duplicateUTMtoSessionStorage();
                }else{
                    // Reset as Direct
                    clearAllUTMSession();
                    _sessionStorage.setItem("utm_source", "web_own");
                    _sessionStorage.setItem("utm_medium", "direct_mass");
                    _sessionStorage.setItem("utm_term", `kbank!${_thisURL}`);
                    _sessionStorage.setItem("utm_content", `none!${_thisURL}`);
                    _sessionStorage.setItem("utmx_entrance", _thisURL);
                    _sessionStorage.setItem("utmx_origin", w.location.pathname);
                    _sessionStorage.setItem("utmx_start", _stamp);
                    _sessionStorage.setItem("utmx_expire", _expire);
                }
            }
        }
        
        // Data store to hidden fields
        duplicate_UTMtoInput();

        doc.addEventListener("DOMContentLoaded", (evt) => {
            _allowLog && console.group(`%c• • • • utmx >> %c02 (DOMContentLoaded) %c(${ get_performance() }ms)`,'color: #00a950','font-style:italic; color: #cddc39;','font-style:italic; color: #778922');

            // Data store to hidden fields
            duplicate_UTMtoInput();

            _allowLog && console.groupEnd();
        });
        doc.addEventListener("readystatechange", (evt) => {
            if(evt.target.readyState == "complete"){
                _allowLog && console.group(`%c• • • • utmx >> %c04 (complete) %c(${ get_performance() }ms)`,'color: #00a950','font-style:italic; color: #cddc39;','font-style:italic; color: #778922');

                _allowActivateUtilities && activateUtilities();

                _allowLog && console.groupEnd();
            }
        });
        w.addEventListener('load', function(){
            _allowLog && console.group(`%c• • • • utmx >> %c04 (load) %c(${ get_performance() }ms)`,'color: #00a950','font-style:italic; color: #cddc39;','font-style:italic; color: #778922');

            _allowActivateUtilities && activateUtilities();

            _allowLog && console.groupEnd();
        })

        // Callback API
        typeof w.initUTMPassthrough === "function" && w.initUTMPassthrough({
            utm_source: _sessionStorage.getItem("utm_source"),
            utm_medium: _sessionStorage.getItem("utm_medium"),
            utm_campaign: _sessionStorage.getItem("utm_campaign"),
            utm_term: _sessionStorage.getItem("utm_term"),
            utm_content: _sessionStorage.getItem("utm_content"),
            utm_id: _sessionStorage.getItem("utm_id"),
            _cid: _sessionStorage.getItem("_cid")
        });
        
        // Hash Log Display
        (w.location.hash == "#icwUTMChecker") && showUTMPassthrough();
        // $(function(){
        //     $(".px-forwardURLParams").each(function(){
        //         this.setAttribute('href', forwardParams(this.href));
        //     });
        //     $(".px-getUTMXParams").each(function(){
        //         this.setAttribute('href', getUTMXCache(this.href));
        //     });
        //     $(".px-getCIDParams").each(function(){
        //         this.setAttribute('href', getCIDCache(this.href));
        //     });
        //     $(".px-getCID2CParams").each(function(){
        //         this.setAttribute('href', getCIDCache(this.href, "c"));
        //     });
        // })
        
        //
        console.log('%c>>> utmx : %cv.'+_version,'color: #00a950','font-weight:bold; color: #cddc39');
        return '>>> utmx v.'+_version;
    }
    function activateUtilities() {
        

        // Data store to hidden fields
        duplicate_UTMtoInput();
        _allowLog && console.log(`%c- Setup input value %c(${get_performance()}ms)`, 'font-style:italic; color: #cddc39;', 'font-style:italic; color: #778922');

        // Utilities Functions
        __$$(".px-forwardURLParams").forEach(el => el.href = forwardParams(el.href));
        __$$(".px-getUTMXParams").forEach(el => el.href = getUTMXCache(el.href));
        __$$(".px-getCIDParams").forEach(el => el.href = getCIDCache(el.href));
        __$$(".px-getCID2CParams").forEach(el => el.href = getCIDCache(el.href, "c"));
        _allowLog && console.log(`%c- Activate utilities classes %c(${get_performance()}ms)`, 'font-style:italic; color: #cddc39;', 'font-style:italic; color: #778922');

        // Automate Forward UTM by URL
        setTimeout(automate_forwardUTM, 1000)
        _allowLog && console.log(`%c- Automate rewrite <a> tag with utm cache %c(${get_performance()}ms)`, 'font-style:italic; color: #cddc39;', 'font-style:italic; color: #778922');

        //
        _allowActivateUtilities = false;
    }
    function duplicateUTMtoSessionStorage() {
        [
            "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id",
            "utmx_entrance", "utmx_origin", "utmx_start", "utmx_expire"
        ].forEach(s => {
            if(_sessionStorage.getItem(s) == null){
                sessionStorage.removeItem(s);
            }else{
                sessionStorage.setItem(s, _sessionStorage.getItem(s));
            }
        })
        return true;
    }
    function duplicate_UTMtoInput(){
        var hiddenFields = doc.querySelectorAll("input[type=hidden]");
        hiddenFields.length && hiddenFields.forEach(function(el){
            var _utmCookies = _sessionStorage.getItem(el.name);
            if (_utmCookies) doc.getElementById(el.name).value = _utmCookies;
        });
        _allowLog && console.log(`%c- Setup input value %c(${get_performance()}ms)`, 'font-style:italic; color: #cddc39;', 'font-style:italic; color: #778922');
    }
    function get_performance(){
        return Math.round((performance.now() - _t0) * 1e3) / 1e3;
    }
    function automate_forwardUTM(){
        __$$('a:not(.px-getUTMXParams)').forEach(el => {
            let _link = el.getAttribute('href');
            if(_link == null) return;
            _automate_forwardCache_URL.forEach(p => {
              if(_link.includes(p)) {
                el.href = getUTMXCache(el.href);
                el.setAttribute('href', getUTMXCache(el.href))
              
              }
            })
        })
     }
    function generateUID(v){
        var _ckey = [
            "UTMX"+v.split(".")[0],
            deviceType(),
            domainLevel(w.location.hostname),
            uidKey(),
            Math.floor(Date.now() / 1000)
        ].reduce(function(a,b){ return a+"."+b; });
        return _ckey;
    }
    function set_utmTimeStamp(t, e){
        clearAllUTMSession();
        _sessionStorage.setItem("utmx_start", t);
        _sessionStorage.setItem("utmx_expire", e);
        return true;
    }
    function set_cidTimeStamp(t, e){
        _sessionStorage.setItem("cidx_start", t);
        _sessionStorage.setItem("cidx_expire", t);
        return true;
    }
    function isObject(value) {
        return (
          typeof value === 'object' &&
          value !== null &&
          !Array.isArray(value)
        );
    }
    function s_deepUID(k, v){
        // X3V0bXhpZA==
        if(isObject(localStorage)){
            localStorage.setItem("utmx_vars_X3V0bXhpZA", Base64.encode(v));
            return true;
        }
        return false;
    }
    function g_deepUID(k){
        if(isObject(localStorage)){
            var cx = localStorage.getItem("utmx_vars_"+Base64.encode(k).slice(0,-2));
            if(cx == null) return null;
            return Base64.decode(cx);
        }
        return null;
    }
    function new_URL(u){
        if(!/^https?:\/\//i.test(u)){
            u = 'https://'+u;
        }
        return new URL(u);
    }
    
    // Utilities
    
    function hasFocusParams(p, arr){
        var _ts = Object.keys(p).reduce(function(a,i){ return a+","+i }).toLocaleLowerCase();
        return arr.some(function(el){
            return _ts.search(el) > -1;
        })
    }
    function clearExpiredSession(t, arr){
        if(t == null) return false;
        if(t > Date.now()) return false;
        arr.forEach(function(s){ _sessionStorage.removeItem(s); })
        return true;
    }
    function clearAllUTMSession() {
        ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "utmx_entrance", "utmx_origin", "utmx_start", "utmx_expire"]
            .forEach(function(s){ _sessionStorage.removeItem(s);});
        return true;
    }
    function clearAllSession() {
        ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "_cid", "utmx_entrance", "utmx_origin", "utmx_start", "utmx_expire"]
            .forEach(function(s){ _sessionStorage.removeItem(s);});
        return true;
    }
    function getQueryParams(qs) {
        var params = {}, tokens, re = /[?&]?([^=]+)=([^&]*)/g;
        while (tokens = re.exec(qs)) {
            params[decodeURIComponent(tokens[1])] = decodeURIComponent(tokens[2]);
        }
        return params;
    }
    function cleanQueryParams(qs){
        var obj = getQueryParams(qs);
        if(!Object.keys(obj).length) return {};
        return Object
            .keys(obj)
            .map(function(s){ return {[s.replace(/\&+/g,"")]:obj[s]}})
            .reduce(function(a,b){ return Object.assign(a, b); });
    }
    function getSearchParams(qs){
        let _qs = new URLSearchParams(qs.replace(/\+/ig,'${plus}'));
        if(_qs.size == 0) return {};
        return [...Array.from(_qs)]
            .map( s => {return {[s[0].replace(/\$\{plus\}/ig,'+')]:s[1].replace(/\$\{plus\}/ig,'+')}})
            .reduce((a,b) => Object.assign(a,b), {});
    }
    function setCookie(cname,v,m) {
        if (m) {
            var date = new Date();
            date.setTime(date.getTime()+(m*24*60*60*1000));
            var expires = "; expires="+date.toGMTString();
        }
        else var expires = "";
        doc.cookie = cname+"="+v+expires+"; path=/";
    }
    function getCookie(na){
        var _na = na+"=",
            _ca = doc.cookie.split('; ').find(function(s){ return s.startsWith(_na)}) || null;
        if(_ca == null) return null;
        return _ca.split("=")[1];
    }
    function uidKey() {
        return ([1e8]+"")
            .replace(/[018]/g, function(c){
            return (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        });
    }
    function domainLevel(h){
        return h.replace(/w{3}\./,"").split(".").length;
    }
    function deviceType() {
      try{ doc.createEvent("TouchEvent"); return 1; }
      catch(e){ return 0; }
    }
    function getUTMXCache(u, opt) {
        
        if(u == '') return '';
        
        var _url = new_URL(u),
            _search = getSearchParams(_url.search),
            _pathname = _url.pathname,
            _utm = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id"],
            _lastkey = {},
            _default = true,
            _keyIn = false,
            _cache = {};
        
        var _hasUTMCache = _utm.some(function(a){return _sessionStorage.getItem(a) != null; });
        // 20241226 : encodeURI for searchParams object
        // _search = encodeObjectValues(_search)
        
        switch(typeof opt){
            case 'undefined': _default = true; break;
            case 'boolean': _default = opt; break;
            case 'object': _keyIn = _default = (Object.keys(opt).length > 0);break;
            default: _default = false;
        }
        _cache = _utm.map(function(s){
                var s_utm = _sessionStorage.getItem(s);
                if(s_utm == null){
                    if(!_hasUTMCache && _default){
                        // Send default utm value
                        if(_keyIn && (opt[s] != undefined)) return {[s]:opt[s]};
                        if(_defaults[s] != undefined) return {[s]:_defaults[s]};
                    }
                    if(_config_force_send_empty_utm){
                        // 20240325 If there is no UTM value, force it to be sent as 'none' (according to Line conditions).
                        if(s != "utm_id") return {[s]: "none"};
                    }
                    return null;
                }
                return {[s]:s_utm};
        }).reverse().concat({}).reduceRight(function(a,b){
            return Object.assign(a,b);
        });
        
        // No utm session
        if(Object.keys(_cache).length == 0) return _url.href;

        // Custom function for mcb01.kasikornbank.com, mcb01dev.kasikornbank.com
        // 20240228 >> Cancel the redirect UTM function because the system on the Line platform does not support it.
        // 20240423 >> Re-enable the function.™
        if(/mcb01(dev)?\.kasikornbank\.com/ig.test(_url.hostname) || /liff.line.me/ig.test(_url.hostname)){
            if(objHasSomeProperties(_search, _custom_redirect_params)){
  
                _custom_redirect_params.forEach(p => {
                    if(_search[p] != undefined){
                        // Separate the redirect parameter to add it back as the last item in the order.
                        _lastkey[p] = encode_redirectUTM(_search[p], _cache, p == 'flowURL');
                        delete _search[p];
                    }
                    // if(_search[p] != undefined) _search[p] = encode_redirectUTM(_search[p], _cache);
                });
            }
        }
        
        _utm.forEach(function(a){ delete _search[a]; });
        _search = obj2Params(Object.assign(_cache, _search, _lastkey));

        if(_pathname == '/') _pathname = "";
        
        return _url.origin+_pathname+_search+_url.hash;
    }
    function encodeObjectValues(obj) {
        return Object.keys(obj).reduce((acc, key) => {
            acc[key] = encodeURIComponent(obj[key]);
            return acc;
        }, {});
    }
    
    function getCIDCache(u, key){
        var _url = new_URL(u),
            _search = getSearchParams(_url.search),
            _pathname = _url.pathname,
            _key = key || '_cid',
            _cid = _sessionStorage.getItem("_cid");
        
        // No _cid session
        if(_cid == null) return _url.href;

        if(_pathname == '/') _pathname = "";
        
        delete _search._cid;
        _search = obj2Params(Object.assign(_search,{[_key]:_cid}));
        
        return _url.origin+_pathname+_search+_url.hash;
    }
    function obj2Params(obj){
        if(Object.keys(obj).length == 0) return "";
        return "?"+Object
            .keys(obj)
            .map(function(a){ return a+"="+obj[a]; })
            .reduce(function(a,b){ return a+"&"+b; });
    }
    function objHasSomeProperties(obj, arr){
        return arr.some(function(a){return obj[a] != undefined });
    }
    function encode_redirectUTM(u, c, pflag){
        if(u == '') return '';
        let q = new_URL(u);
        Object.keys(c).forEach(k => q.searchParams.append(k, c[k]));

        // For handling the encoded delimiter '%21', revert it back to '!' as before.
        let re_params_delimiter = q.searchParams.toString().replace(/\%21/g, "!");

        if(!!pflag) {
            // encode With protocal
            return q.origin+q.pathname+"?"+encodeURIComponent(re_params_delimiter+q.hash);
        }
        return q.hostname+q.pathname+"?"+encodeURIComponent(re_params_delimiter+q.hash);
    }
    function convertSessionCache(){
        if(!arguments.length) return "";
        
        var _sc = "",
            _hs = u.match(/(\#[-a-z\d_]+)/i),
            arr = [],
            n = arguments.length/2;
        
        for(var i = 0; i < n; i++){
            arr.push(arguments[i+1]+"="+_sessionStorage.getItem(arguments[i]));
        }
        _sc = arr.reduce(function(a,b){ return a+"&"+b; });
        
    }
    function forwardParams(u){
        
        if(u == '') return '';
        var _url = new_URL(u),
            _search = getSearchParams(_url.search),
            _pathname = _url.pathname,
            _params = getSearchParams(w.location.search);
        
        // No url parameters
        if(Object.keys(_params).length == 0) return _url.href;
        
        if(_pathname == '/') _pathname = "";
        _search = obj2Params(Object.assign(_search,_params));
        
        return _url.origin+_pathname+_search+_url.hash;
    }
    
    function hasCookieUTM() {
        return [
            "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id",
            "utmx_entrance", "utmx_origin", "utmx_start", "utmx_expire"
        ].some(s => (_sessionStorage.getItem(s) != null)&&(_sessionStorage.getItem(s) != ""));
    }
    
    w.Base64 = Base64;
    // Global function
    w._utmx = {
        get _version() { return _version; },
        get _uid() { return _uid; },
        get _duration() { return _duration; },
        get _default_utm() { return _defaults; },
        set _settings(o) { _defaults = o; },
        getUTMXCache: getUTMXCache,
        getCIDCache: getCIDCache,
        forwardParams: forwardParams,
        clearAllUTMSession: clearAllUTMSession,
        clearAllSession: clearAllSession,
        setURL: function(u){
            var _uri = u || w.location.href;
            return {
                addUTM: function(o){
                    _uri = getUTMXCache(_uri, o);
                    return this;
                },
                addCID: function(o){
                    _uri = getCIDCache(_uri, o);
                    return this;
                },
                addParams: function(){
                    _uri = forwardParams(_uri);
                    return this;
                },
                clean: function(){
                    var _t = new_URL(_uri),
                        _p = (_t.pathname == '/') ? '' : _t.pathname;
                    _uri = _t.origin + _p;
                    return this;
                },
                get href(){
                    return _uri;
                }
            }
        },
        get _help() {
            return '';
        }
    }
    return '> initial UTMX.';
})(window, document, true, btoa(btoa(window.location.hostname.toLowerCase())))

// Global Function
function showUTMPassthrough() {
    var _utm = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id", "_cid"],
        _ct = '<table><tbody><tr><td style="width:100px;">&gt;&gt; Source: </td><td>{{utm_source}}</td></tr><tr><td>&gt;&gt; Medium: </td><td>{{utm_medium}}</td></tr><tr><td>&gt;&gt; Campaign: </td><td>{{utm_campaign}}</td></tr><tr><td>&gt;&gt; Term: </td><td>{{utm_term}}</td></tr><tr><td>&gt;&gt; Content: </td><td>{{utm_content}}</td></tr><tr><td>&gt;&gt; Ads ID: </td><td>{{utm_id}}</td></tr><tr><td>&gt;&gt; CID: </td><td>{{_cid}}</td></tr><tr><td colspan="2"></td></tr><tr><td colspan="2">Expire Session: </td></tr><tr><td colspan="2" class="s-url">{{utmx_expire}}</td></tr></tbody></table><div>Entrance Page (Landing):</div><div class="s-url">{{utmx_entrance}}</div><div>Path Origin:</div><div class="s-url">{{utmx_origin}}</div><div class="s-key">- {{key}} -</div>',
        _version = _sessionStorage.getItem("utmx_version"),
        readCookie = function(na){
            var _na = na+"=",
                _ca = document.cookie.split('; ').find(function(s){ return s.startsWith(_na)}) || null;
            if(_ca == null) return null;
            return _ca.split("=")[1];
        }
    
    _utm.forEach(function(k){
        var s = _sessionStorage.getItem(k) || "-",
            p = new RegExp("\{\{" + k + "\}\}", "ig");
        _ct = _ct.replace(p, s);
    });
    
    ["utmx_expire"].forEach(function(k){
        var s = _sessionStorage.getItem(k) || "-",
            p = new RegExp("\{\{" + k + "\}\}");
        if(s != "-") s = new Date(+s).toString().replace(/\sGMT.+/,"");
        _ct = _ct.replace(p, s);
    });

    _ct = _ct.replace(/\{\{utmx_entrance\}\}/ig, _sessionStorage.getItem("utmx_entrance") || "-");
    _ct = _ct.replace(/\{\{utmx_origin\}\}/ig, _sessionStorage.getItem("utmx_origin") || "-");
    _ct = _ct.replace(/\{\{key\}\}/ig, readCookie("_utmxid") || "000");
    _ct = '<div id="px-activeUTM"><div><strong>### UTM Passthrough ###</strong></div><div class="s-version">version: ' + _version + '</div>' + _ct + '</div>';
    try{document.getElementById("px-activeUTM").remove();}catch(e){};
    document.body.insertAdjacentHTML('beforeend', _ct);
    var head = document.getElementsByTagName('head')[0];
    var s = document.createElement('style'),
        css = '#px-activeUTM{display:inline-block;position:fixed;top:100px;right:20px;font-family:"Segoe UI",Segoe,Tahoma,Helvetica,Arial,sans-serif;font-size:13px;background-color:rgba(0,0,0,.68);max-width:max(25%, 320px);border-radius:4px;z-index:12000;color:#fff;padding:30px 20px}#px-activeUTM .s-url,#px-activeUTM .s-version,#px-activeUTM .s-key{font-size:10px;font-style:italic;color:#999;word-break:break-word}#px-activeUTM table{margin:10px 0; width:100%}#px-activeUTM .s-key{position:absolute;right:14px;bottom:12px;font-size:8px;color:#666}#px-activeUTM .s-key::selection{color:#fff}#px-activeUTM td{word-break:break-word;vertical-align:top}';
    s.setAttribute('type', 'text/css');
    if (s.styleSheet) {
        s.styleSheet.cssText = css;
    } else {
        s.appendChild(document.createTextNode(css));
    }
    head.appendChild(s);
}
function clearUTMPassthrough() {
    [
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "utm_id",
        "_cid",
        "utmx_entrance", "utmx_origin", "utmx_start", "utmx_expire"
    ].forEach(function(s){ _sessionStorage.removeItem(s);});
}

function cleanQueryParams_custom(qs){
    var obj = getQueryParams_custom(qs);
    if(!Object.keys(obj).length) return {};
    return Object
        .keys(obj)
        .map(function(s){ return {[s.replace(/\&+/g,"")]:obj[s]}})
        .reduce(function(a,b){ return Object.assign(a, b); });
}

function getQueryParams_custom(qs) {
    var params = {}, tokens, re = /[?&]?([^=]+)=([^&]*)/g;
    while (tokens = re.exec(qs)) {
        params[decodeURIComponent(tokens[1])] = decodeURIComponent(tokens[2]);
    }
    return params;
}

function splitANCHOR(url, mode) {
    let arrUTM = [];

    let param = cleanQueryParams_custom(location.search);

    const url_utm_source = param.utm_source ? param.utm_source : "";
    const url_utm_medium = param.utm_medium ? param.utm_medium : "";
    const url_utm_campaign = param.utm_campaign ? param.utm_campaign : "";
    const url_utm_content = param.utm_content ? param.utm_content : "";
    const url_utm_term = param.utm_term ? param.utm_term : "";
    const url_cid = param._cid ? param._cid : "";

    const _utm_source = _sessionStorage.getItem("utm_source") ? arrUTM.push("utm_source=" + _sessionStorage.getItem("utm_source"))  : arrUTM.push("utm_source=" + url_utm_source);
    const _utm_medium = _sessionStorage.getItem("utm_medium") ? arrUTM.push("utm_medium=" + _sessionStorage.getItem("utm_medium")) :  arrUTM.push("utm_medium=" + url_utm_medium);
    const _utm_campaign = _sessionStorage.getItem("utm_campaign") ? arrUTM.push("utm_campaign=" + _sessionStorage.getItem("utm_campaign")) : arrUTM.push("utm_campaign=" + url_utm_campaign);
    const _utm_content = _sessionStorage.getItem("utm_content") ? arrUTM.push("utm_content=" + _sessionStorage.getItem("utm_content")) : arrUTM.push("utm_content=" + url_utm_content);
    const _utm_term = _sessionStorage.getItem("utm_term") ? arrUTM.push("utm_term=" + _sessionStorage.getItem("utm_term")) : arrUTM.push("utm_term=" + url_utm_term);
    const _cid = _sessionStorage.getItem("_cid") ? arrUTM.push("_cid=" + _sessionStorage.getItem("_cid")) : arrUTM.push("_cid=" + url_cid);

    if (url) {
        let paramUTM = "";
        if (arrUTM.length > 0) {
            $.each(arrUTM, function(i, v){
                if (i === 0) {
                    if(url.indexOf("?") == -1) {
                        paramUTM += "?" + v;
                    } else {
                        if (mode === "qr") {
                            paramUTM += "%26" + v;
                        } else {
                            paramUTM += "&" + v;
                        }
                    }
                } else {
                    if (mode === "qr") {
                        paramUTM += "%26" + v;
                    } else {
                        paramUTM += "&" + v;
                    }
                }
            })

            const split = url.split("#");            
            if (split.length > 1) {
                url = split[0] + paramUTM + "#" + split[1];
            } else {
                url = url + paramUTM;
            }
        } 
    }
    return url;
}