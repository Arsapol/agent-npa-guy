/* =========== ### =========== */
/* Cookies Controller */
// Version 2.3.4
// Latest update 13/03/2025

; (async function (embed_code) {
    if (typeof window._cookiesplc != 'undefined') {
        if (window._cookiesplc) {
            console.log("%cCookies Policy >>>> %cduplicate protected.", 'color: #00a950', 'color: #cddc39');
            return;
        }
    }
    const displayLog = !0,
        _t0 = performance.now(),
        _server = await nsLocation(location.hostname),
        _params = new URL(window.location.href).searchParams,
        _version = '2.3.3';

    let _loc = location.pathname.toLowerCase(),
        _host = {
            localhost: '49960de5880e8c687434170f6476605b8fe4aeb9a28632c7995cf3ba831d9763' === _server,
            uat: ('29f5d989b7514448290491d68798d98fb08384cc9b055b1a400de488b8aa4100' === _server)
                || ('09c964b20d56201969d74a59b405bd6bccd7e14aac3880c48daf3c8f0b715439' === _server)
                || ('a4f2e6ef2595b93687725bb1200edb106d2ab82a7c2b1404fb5299f5c9aa6a87' === _server),
            uatinsure:('890ad41d2d54224186bba46fd22b9e59e5a95c92f8fcfc5c80c7949c78625c44' === _server),
            prod: ('bf208c05294f70ba4eeec4eaeaec41e3841cbc65f416af0774a68a12f5b1f5ee' === _server),
            prodinsure:('325f197d88d8de8095250776a563405a30ba077254c9b99cfb666518a4973d7b' === _server),
        },
        url_checker = {
            personal_index: /\/(?:th|en)\/personal(\/)?(pages\/home\.aspx)?$/gi.test(_loc),
            business_index: /\/(?:th|en)\/business(\/)?(pages\/business\.aspx)?$/gi.test(_loc),
            wealth_index: /\/(?:th|en)\/wealth(\/)?(pages\/index\.aspx)?$/gi.test(_loc),
            kbiz_index: /\/(?:th|en)\/kbiz(?:\/apply)?\/pages\/index\.aspx/ig.test(_loc),
            kbiz_article: /\/(?:th|en)\/kbiz\/article\/*/ig.test(_loc),
            kshop_digital_banking: /\/(?:th|en)\/business\/sme\/digital\-banking\/kshop\/pages\/index\.aspx/ig.test(_loc),
            appkplus_landing: /\/(?:th|en)\/appkplus\/pages\/landingpage\.aspx/ig.test(_loc),
            ktl_thankyou: /\/(?:th|en)\/personal\/loan\/homeloan\/pages\/ktl-thankyou\.aspx/ig.test(_loc)
        };

    var embedScript = (o, ns, ck, p) => {
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
                console.log(`%ccookies ctr loaded >>>> %c${o.name} %c(${get_performance()}ms)`, 'color: #ff5722', 'color: #cddc39', 'font-style:italic; color: #778922');
            }
            _script.onload = function () {
                console.log(`%ccookies ctr loaded >>>> %c${o.name} %c(${get_performance()}ms)`, 'color: #ff5722', 'color: #cddc39', 'font-style:italic; color: #778922');
            }
        }
        if (o.callback != undefined) {
            _script.addEventListener("readystatechange", o.callback);
            _script.addEventListener("load", o.callback);
        }
        _head.appendChild(_script);
    };
    //
    displayLog && console.log(`%c>> [cookies controller v.${_version}] <<`, 'color: #e8c91c');
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
    //
    window._cookiesplc = true;
})([
    {
        // Adobe DTM (UAT and UAT insure)
        // ทาง Kbank แจ้งให้ Add เมื่อ 20/11/2024
        disable: false,
        name: 'Adobe DTM (UAT)',
        url: 'https://assets.adobedtm.com/launch-EN31ba7d43525d4548be5ad09f049aee43-development.min.js',
        condition: function (_ns, _page, _params) {
            if (_ns.uat || _ns.localhost || _ns.uatinsure) {
                if(_params.get('_cid') != null) return true;
                TestCase_KBank_Check_Consent_params();
                return KBank_Check_Consent_params().adobe;
            }
            return false;
        },
        callback: function () {
            console.log("%cCookies Policy Run (Adobe UAT) >> %c_satellite.pageBottom()", 'color: #00a950', 'color: #e8c91c');
            try {
                _satellite.pageBottom();
            } catch (e) {
                console.log(e.message);
            }
        }
    },
    {
        // Adobe DTM (PROD) and (PROD Insure)
        disable: false,
        name: 'Adobe DTM',
        url: 'https://assets.adobedtm.com/launch-EN61699a09a933489699c016595b86f9f3.min.js',
        condition: function (_ns, _page, _params) {
            if(_ns.prod || _ns.prodinsure){
                if(_params.get('_cid') != null) return true;
                TestCase_KBank_Check_Consent_params();
                return KBank_Check_Consent_params().adobe;
            }
            return false;
        },
        callback: function () {
            console.log("%cCookies Policy Run (Adobe) >> %c_satellite.pageBottom()", 'color: #00a950', 'color: #e8c91c');
            try {
                _satellite.pageBottom();
            } catch (e) {
                console.log(e.message);
            }
        }
    },
    {
        // OneTrust Cookies OTAutoBlock for UAT
        disable: false,
        name: 'One Trust OTAutoBlock (UAT)',
        url: 'https://cdn-apac.onetrust.com/consent/bc8fd97f-ebeb-468f-adc2-00366c28cd30/OtAutoBlock.js',
        condition: function (_ns, _page) {
            if (_ns.uat || _ns.localhost) {
                // UAT
                return KBank_Check_Consent_params().one_trust;
            }
            return false;
        }
    },
    {
        // OneTrust Cookies Consent (UAT)
        disable: false,
        name: 'One Trust (UAT)',
        url: 'https://cdn-apac.onetrust.com/scripttemplates/otSDKStub.js',
        opt: { charset: 'UTF-8', 'data-document-language': "true", 'data-domain-script': "018eccdc-169d-7ee0-8291-a08a764c3469" },
        condition: function (_ns, _page) {
            if (_ns.localhost) return false;
            if (_ns.uat) {
                // UAT
                return KBank_Check_Consent_params().one_trust;
            }
            return false;
        },
        callback: function () {
            callBack_Onetrust_SDK();
        }
    },
      {
        // OneTrust Cookies Consent (UAT-insure)
        disable: false,
        name: 'One Trust (UAT)',
        url: 'https://cdn-apac.onetrust.com/scripttemplates/otSDKStub.js',
        opt: { charset: 'UTF-8', 'data-document-language': "true", 'data-domain-script': "019324b3-7810-7f82-ab1f-b8acbf625749" },
        condition: function (_ns, _page) {
            if (_ns.localhost) return false;
            // UAT insure
            if (_ns.uatinsure) {
                return KBank_Check_Consent_params().one_trust;
            }
            return false;
        },
        callback: function () {
            callBack_Onetrust_SDK();
        }
    },
    {
        // OneTrust Cookies OTAutoBlock for PROD
        disable: false,
        name: 'One Trust OTAutoBlock (PROD)',
        url: 'https://cdn-apac.onetrust.com/consent/b3b17bb1-a2a8-4a01-a561-0c7b657b4e8e/OtAutoBlock.js"',
        condition: function (_ns, _page) {
            if (_ns.uat) {
                // UAT
                return false
            }
            return KBank_Check_Consent_params().one_trust;
        }
    },
    {
        // OneTrust Cookies Consent (PROD)
        disable: false,
        name: 'One Trust (PROD)',
        url: 'https://cdn-apac.onetrust.com/scripttemplates/otSDKStub.js',
        opt: { charset: 'UTF-8', 'data-document-language': "true", 'data-domain-script': "b3b17bb1-a2a8-4a01-a561-0c7b657b4e8e" },
        condition: function (_ns, _page) {
            
            if (_ns.uat) {
                // UAT
                return false
            }
            if (_ns.prod) {
                return KBank_Check_Consent_params().one_trust;
            }
            return false;
        },
        callback: function () {
            callBack_Onetrust_SDK();
        }
    },
    {
        // OneTrust Cookies Consent (PROD Insure)
        disable: false,
        name: 'One Trust (PROD)',
        url: 'https://cdn-apac.onetrust.com/scripttemplates/otSDKStub.js',
        opt: { charset: 'UTF-8', 'data-document-language': "true", 'data-domain-script': "019324b4-de61-7bf2-86a9-13e4270ae171" },
        condition: function (_ns, _page) {

            
            
            if (_ns.uat || _ns.uatinsure) {
                // UAT
                return false
            }
            if (_ns.prodinsure) {
                return KBank_Check_Consent_params().one_trust;
            }
            return false;
        },
        callback: function () {
            callBack_Onetrust_SDK();
        }
    },
    {
        // Event Tracking Script - Abandon Form
        name: '*ETS* Abandon Form',
        url: '/SiteCollectionDocuments/js/tracking-abandon-script.js',
        opt: { defer: '' },
        condition: function () {
            if (/xpressloan|xpresscash|creditcard|new\-car|used\-car/ig.test(location.pathname.toLowerCase())) return true;

            return false;
        }
    }
]);

// ---- Utilities Function ---- //

// KBank Consent Logic
// เงื่อนไขการแสดงผล Consent จากทาง KBank 26/04/2024
function TestCase_KBank_Check_Consent_params(){
    let test_case = KBank_Check_Consent_params();
    console.group(`%c===== Cookies Controller : CONSENT CASE ${test_case.case} ======`, 'color: #ff9900');
    console.log(`%c- One Trust >>> ${test_case.one_trust ? "YES": "NO"}`, 'font-style:italic; color: #cddc39;');
    console.log(`%c- ADOBE DTM >>> ${test_case.adobe ? "YES": "NO"}`, 'font-style:italic; color: #cddc39;');
    console.groupEnd();
}
function KBank_Check_Consent_params(){
    let _path = (window.location.pathname).toLowerCase(),
        _qs = new URL(window.location.href).searchParams;

    // params >> _scc
    if(_qs.get("_scc") == 'gyay') return { "case": 1, "one_trust": true, "adobe": true };
    if(_qs.get("_scc") == 'gyan') return { "case": 2, "one_trust": true, "adobe": false };
    if(_qs.get("_scc") == 'gnay') return { "case": 3, "one_trust": false, "adobe": true };
    if(_qs.get("_scc") == 'gnan') return { "case": 4, "one_trust": false, "adobe": false };
    
    // params >> app
    if(_qs.get("app") == 'kplus') return { "case": 4, "one_trust": false, "adobe": false };
    if(_qs.get("app") == 'kplus_info') return { "case": 4, "one_trust": false, "adobe": false };
    if(_qs.get("app") == 'KWEB') return { "case": 4, "one_trust": false, "adobe": false };
    if(_qs.get("app") == 'kplus_dup') return { "case": 3, "one_trust": false, "adobe": true };

    // params >> deeplink2020
    if(_qs.get("deeplink2020") != null) return { "case": 4, "one_trust": false, "adobe": false };

    // params >> UTMsource
    if(_qs.get("UTMsource") == 'EAPP') return { "case": 4, "one_trust": false, "adobe": false };

    // PDPA path
    if(/\/th\/pdpa\-reconsent\-kplus\/pages\/pdpa_(a|b)\.aspx/ig.test(_path)) return { "case": 3, "one_trust": false, "adobe": true };

    // APP KPlus
    if(/\/(?:th|en)\/appkplus\/pages\/landingpage\.aspx/ig.test(_path)) return { "case": 4, "one_trust": false, "adobe": false };

    // ktl_thankyou
    if(/\/(?:th|en)\/personal\/loan\/homeloan\/pages\/ktl-thankyou\.aspx/ig.test(_path)) return { "case": 4, "one_trust": false, "adobe": false };

    return { "case": 1, "one_trust": true, "adobe": true };
}

// Callback Condition ตัวเดิม 
function callBack_Onetrust_SDK() {
    // Condition 01
    let _styles = `#onetrust-consent-sdk { display: none !important; } .f-consent-paddingTop { padding-top: 0px !important; }`,
        _path = window.location.pathname,
        _qs = new URL(window.location.href).searchParams;

    const condition_list = [
        /\/th\/pdpa\-reconsent\-kplus\/Pages\/pdpa_b\.aspx/ig.test(_path),
        /\/en\/personal\/digital\-banking\/kplus\/kpoint\/pages\/index\.html/ig.test(_path),
        /\/th\/personal\/digital\-banking\/kplus\-kpoint\/pages\/tc\.html/ig.test(_path),
        (_qs.get("app") == 'kplus') || (_qs.get("app") == 'kplus_info') || (_qs.get("app") == 'KWEB'),
        _qs.get("deeplink2020") != null,
        _qs.get("UTMsource") == 'EAPP'
    ]
    let _chkCondition = condition_list.some((a) => a);

    if (_chkCondition) {
        //console.log("%cCookies Policy Run >>>> %ccondition 1 ",'color: #00a950','color: #cddc39');
        var _styleSheet = document.createElement("style")
        _styleSheet.innerText = _styles;
        document.head.appendChild(_styleSheet);
        window.addEventListener('load', () => {
            if (document.querySelector('#s4-workspace') != null) {
                document.querySelector('#s4-workspace').classList.add('f-consent-paddingTop');
            }
        })
        document.body.classList.add('f-consent-paddingTop');
    }
    // Auto Run
    window.OptanonWrapper = function () {
        console.log('>> Run OptanonWrapper');
        // Req.
        var otPCAcceptAll = document.getElementById('accept-recommended-btn-handler'),
            targetContainer = document.getElementsByClassName('ot-btn-container')[0];
        targetContainer.append(otPCAcceptAll);
        // Force Style
        document.querySelector('.save-preference-btn-handler.onetrust-close-btn-handler').style.maxWidth = '60%';
        document.getElementsByClassName('banner-actions-container')[0]?.prepend(document.getElementById('onetrust-pc-btn-handler'));
        // Custom Style by ICW
        let _styleSheet = document.createElement('style'),
            _styles = '';

        _styles += '#onetrust-pc-sdk .ot-pc-footer { width: calc(100% - 32px); padding: 16px 0px 25px 0px; bottom: 0px; }';
        _styles += '#onetrust-pc-sdk.otPcCenter .ot-btn-container { display: flex; width: 100%; justify-content: center; align-items: center; flex-wrap: wrap; margin: 0px; gap: 15px 10px; }';
        _styles += '#onetrust-pc-sdk.otPcCenter .ot-pc-footer button { display: inline-block; width: auto; margin: 0px; }';
        _styles += '#onetrust-pc-sdk .save-preference-btn-handler { margin-right: 0px !important; }';
        _styles += '#onetrust-pc-sdk #accept-recommended-btn-handler { margin: 0px; }';
        _styles += '@media only screen and (max-width: 440px){ #onetrust-banner-sdk .banner-actions-container { display: flex; flex-direction: column-reverse; align-items: center; } }'
            
        _styleSheet.id = "onetrust-style-custom";
        _styleSheet.innerText = _styles;
        document.head.appendChild(_styleSheet);
    }
}