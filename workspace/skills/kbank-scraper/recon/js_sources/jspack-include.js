/* =========== ### =========== */
/* JS-Files Loading */
// Version 3.2.0
// Latest update 22/11/2024

// Revised Version 2024.11.28
// - update _host
// Last edited by Nati

; (async function (embed_code) {
    
    if (typeof window._jspack != 'undefined') {
        if (window._jspack) {
            console.log("%cjspack >>>> %cduplicate protected.", 'color: #00a950', 'color: #cddc39');
            return;
        }
    }
    const displayLog = !0,
        _t0 = performance.now(),
        _server = await nsLocation(location.hostname),
        _params = new URL(window.location.href).searchParams,
        _rev = '2024.11.22',
        _version = '3.2.0';
        

    let _loc = location.pathname.toLowerCase(),
        _host = {
            localhost: '49960de5880e8c687434170f6476605b8fe4aeb9a28632c7995cf3ba831d9763' === _server,
            uat: ('29f5d989b7514448290491d68798d98fb08384cc9b055b1a400de488b8aa4100' === _server)
                || ('09c964b20d56201969d74a59b405bd6bccd7e14aac3880c48daf3c8f0b715439' === _server)
                || ('890ad41d2d54224186bba46fd22b9e59e5a95c92f8fcfc5c80c7949c78625c44' === _server)
                || ('a4f2e6ef2595b93687725bb1200edb106d2ab82a7c2b1404fb5299f5c9aa6a87' === _server),
            prod: ('bf208c05294f70ba4eeec4eaeaec41e3841cbc65f416af0774a68a12f5b1f5ee' === _server)
                || ('325f197d88d8de8095250776a563405a30ba077254c9b99cfb666518a4973d7b' === _server)
            
        },
        url_checker = {
            personal_index: /\/(?:th|en)\/personal(\/)?(pages\/home\.aspx)?$/gi.test(_loc),
            business_index: /\/(?:th|en)\/business(\/)?(pages\/business\.aspx)?$/gi.test(_loc),
            wealth_index: /\/(?:th|en)\/wealth(\/)?(pages\/index\.aspx)?$/gi.test(_loc),
            kbiz_index: /\/(?:th|en)\/kbiz(?:\/apply)?\/pages\/index\.aspx/ig.test(_loc),
            kbiz_article: /\/(?:th|en)\/kbiz\/article\/*/ig.test(_loc),
            kshop_digital_banking: /\/(?:th|en)\/business\/sme\/digital\-banking\/kshop\/pages\/index\.aspx/ig.test(_loc),
            appkplus_landing: /\/(?:th|en)\/appkplus\/pages\/landingpage\.aspx/ig.test(_loc)
        };

    async function embedScript(o, ns, ck, p){
        if (o.hasOwnProperty('disable') && o.disable) return;
        if (o.hasOwnProperty('condition') && !o.condition(ns, ck, p)) return;

        let _prefix = "";
        if (ns.localhost) {
            if (!(o.url).startsWith('https://')) {
                _prefix = '/kbank-navigation-2023';
            }
        }

        var _head = document.head,
            _script = document.createElement('script');
        _script.type = 'text/javascript';
        _script.src = _prefix + o.url;

        if (o.opt != undefined) {
            Object.keys(o.opt).forEach((a, i) => _script.setAttribute(a, o.opt[a]))
        }
        if (displayLog) {
            _script.onreadystatechange = function () {
                console.log(`%cjspack loaded >>>> %c${o.name} %c(${get_performance()}ms)`, 'color: #00a950', 'color: #cddc39', 'font-style:italic; color: #778922');
            }
            _script.onload = function () {
                console.log(`%cjspack loaded >>>> %c${o.name} %c(${get_performance()}ms)`, 'color: #00a950', 'color: #cddc39', 'font-style:italic; color: #778922');
            }
        }
        if (o.callback != undefined) {
            _script.addEventListener("readystatechange", o.callback);
            _script.addEventListener("load", o.callback);
        }

        _head.appendChild(_script);
    };
    //
    displayLog && console.log(`%c>> [jspack v.${_version} rev.${_rev}] <<`, 'color: #e8c91c');
    //
    embed_code.forEach((obj, i) => embedScript(obj, _host, url_checker, _params));

    async function nsLocation(x) {
        const msgUint8 = new TextEncoder().encode(x);
        const hashBuffer = await crypto.subtle.digest("SHA-256", msgUint8);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
        return hashHex;
    }
    function get_performance() {
        return Math.round((performance.now() - _t0) * 1e3) / 1e3;
    }

    window.jspack = window.jspack || {};
    window.jspack.host = _host
    window.jspack.url_checker = url_checker;
    //
    window._jspack = true;
})([
    {
        // Checker-Nav
        disable: false,
        name: 'Checker-Nav',
        url: '/SiteCollectionDocuments/assets/js/checker-nav.js'
    },
    {
        // KBank Global Search
        disable: false,
        name: 'KBank Global Search',
        url: '/SiteCollectionDocuments/assets/search-navigation/js/g-search-core.js',
        opt: { defer: '' }
    },
    {
        // ICW Standard Common Javascript
        name: 'ICW commonJS',
        url: '/SiteCollectionDocuments/assets/js/common.js',
        opt: { defer: '' },
        condition: function () {
            return true;
        }
    }
]);




