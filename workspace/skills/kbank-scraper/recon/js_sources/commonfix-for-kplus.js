var getQueryString = function (name) {
    name = name.toLowerCase();
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search.toLowerCase()) || [, ""])[1].replace(/\+/g, '%20')) || null
}

var activateLink_KMaster = ["/th/personal/loan/homeloan/pages/home.aspx", "/th/personal/loan/homeloan/pages/homeloanrefinance.aspx", "/th/personal/loan/homeloan/pages/hometocash.aspx", "/th/personal/loan/homeloan/pages/multi-purposes.aspx", "/th/personal/loan/car-loan/car-to-cash/pages/car-to-cash.aspx", "/th/personal/autoloan/pages/new-car.aspx", "/th/personal/autoloan/pages/used-car.aspx", "/th/personal/autoloan/pages/k-ev-shop.aspx", "/th/pdpa-reconsent-kplus/pages/howto.aspx","/th/promotion/pages/homeloanplus-targeted2023.aspx","/th/promotion/pages/wealthplus-migrate.aspx","/th/promotion/pages/blue-connect-targeted-oct22.aspx","/th/promotion/pages/kpoint-billpaytopupqr.aspx","/th/personal/Digital-banking/Pages/k-esavings-account.aspx","/th/promotion/pages/debit-ewallet.aspx","/th/personal/Digital-banking/Pages/blue-connect/paylater.aspx","/th/personal/Digital-banking/Pages/blue-connect.aspx", "/th/promotion/credit-card/others/Pages/KpointTransfer10112021.aspx", "/th/promotion/pages/kplusshop-newfeature-qrscan.aspx", "/th/promotion/pages/peanuts.aspx", "/th/personal/debit-card/pages/debit-peanuts.aspx", "/th/personal/digital-banking/pages/k-esavings-peanuts.aspx", "/th/personal/account/pages/taweesup-peanuts.aspx", "/th/promotion/Pages/kbank-grab-lmwn.aspx", "/th/personal/insure/life/pages/sickhealth-ipdopd.aspx", "/Pages/PageNotFoundError.aspx", "/th/Apply/Pages/Expire.aspx", "/th/promotion/Pages/kbank-visa-e-commerce.aspx", "/th/promotion/credit-card/shopping/Pages/TheMallCNY29012021C.aspx", "/th/promotion/credit-card/home-decor/Pages/Furnitures01022021C.aspx", "/th/promotion/credit-card/home-decor/Pages/HomeDecorAll01022021C.aspx", "/th/promotion/credit-card/shopping/Pages/CentralCYN29012021C.aspx", "/th/promotion/credit-card/shopping/Pages/RobinsonCYN29012021C.aspx", "/th/promotion/credit-card/shopping/Pages/CentralEMCNY022021C.aspx", "/th/promotion/credit-card/shopping/Pages/wewillwinC.aspx", "/th/promotion/credit-card/shopping/Pages/CENTRALWOWWEEKEND191220C.aspx", "/th/promotion/credit-card/shopping/Pages/RobinsonCelebrationSale141220C.aspx", "/th/promotion/credit-card/shopping/Pages/ROBINSON1212WEEK12122020C.aspx", "/th/promotion/credit-card/home-decor/Pages/HomeDecor103112020C.aspx", "/th/promotion/credit-card/home-decor/Pages/HomeDecor03112020C.aspx", "/th/promotion/credit-card/shopping/Pages/CENTRALPaycation14122020C.aspx", "/th/promotion/credit-card/shopping/Pages/TheMallHappiertogether30112020C.aspx", "/th/personal/Insure/non-life/Pages/cancer-insurance.aspx", "/th/promotion/credit-card/shopping/Pages/RobinsonBlackFridayMadnessSale26112020C.aspx", "/th/promotion/credit-card/shopping/Pages/CentralBlackMidnightSale26112020C.aspx", "/th/promotion/credit-card/shopping/Pages/CENTRALBLACKMIDNIGHTSALE28112020C.aspx", "/special/pages/OfferXpressLoan25.aspx", "/special/pages/OfferXpressLoan26.aspx", "/special/pages/OfferXpressLoan27.aspx", "/special/pages/OfferXpressLoan28.aspx", "/th/promotion/credit-card/health/Pages/Insurance22102020.aspx", "/th/promotion/credit-card/travel/Pages/OnlineTravel01112020C.aspx", "/th/promotion/credit-card/shopping/Pages/ShopFest29102020C.aspx", "/th/promotion/credit-card/shopping/Pages/ECommerce30102020C.aspx", "/th/promotion/credit-card/shopping/Pages/robinson11112020C.aspx", "/th/promotion/credit-card/shopping/Pages/central11112020C.aspx", "/th/promotion/credit-card/shopping/Pages/ShopDMeeKeun23102020C.aspx", "/th/promotion/credit-card/shopping/Pages/BlackWeekend29102020C.aspx", "/PTTBlueCONNECT5", "/th/personal/the-wisdom/Privileges/localized-experiences/phuket/Pages/index.aspx", "/th/personal/the-wisdom/Privileges/special-privileges/Recommended/Pages/KING-POWER_oct_2020.aspx", "/th/promotion/credit-card/shopping/Pages/KingPower01102020.aspx", "/special/pages/OfferXpressLoan21.aspx", "/special/pages/OfferXpressLoan22.aspx", "/special/pages/OfferXpressLoan23.aspx", "/special/pages/OfferXpressLoan24.aspx", "/th/promotion/credit-card/shopping/Pages/RewardThe115092020.aspx", "/special/pages/OfferXpressLoan1.aspx", "/special/pages/OfferXpressLoan2.aspx", "/special/pages/OfferXpressLoan3.aspx", "/special/pages/OfferXpressLoan4.aspx", "/special/pages/OfferXpressLoan5.aspx", "/special/pages/OfferXpressLoan6.aspx", "/special/pages/OfferXpressLoan7.aspx", "/special/pages/OfferXpressLoan8.aspx", "/special/pages/OfferXpressLoan9.aspx", "/special/pages/OfferXpressLoan10.aspx", "/special/pages/OfferXpressLoan11.aspx", "/special/pages/OfferXpressLoan12.aspx", "/special/pages/OfferXpressLoan13.aspx", "/special/pages/OfferXpressLoan14.aspx", "/special/pages/OfferXpressLoan15.aspx", "/special/pages/OfferXpressLoan16.aspx", "/special/pages/OfferXpressLoan17.aspx", "/special/pages/OfferXpressLoan18.aspx", "/special/pages/OfferXpressLoan19.aspx", "/special/pages/OfferXpressLoan20.aspx", "/th/personal/Insure/non-life/Pages/dengue-insurance.aspx", "/th/promotion/pages/shop-jukjuk.aspx", "/th/personal/Insure/life/Pages/SickButSafe.aspx", "/th/personal/Digital-banking/Pages/youtrip.aspx", "/th/financial-conglomerate", "/en/financial-conglomerate", "/en/privacy-policy", "/th/privacy-policy", "/en/about/Pages/financial-conglomerate.aspx", "/th/about/Pages/financial-conglomerate.aspx", "/en/privacy-policy/Pages/privacy-policy.aspx", "/th/privacy-policy/Pages/privacy-policy.aspx", "/th/promotion/Pages/overseaq4cashback.aspx", "/th/personal/credit-card/pages/ptt-blue.aspx", "/th/apply/creditcard/pages/ptt-blue.aspx", "/th/promotion/pages/addcardget1000pts.aspx", "/th/promotion/pages/samyan-midtown.aspx", "/th/promotion/pages/kpluspointtransfer.aspx", "/th/promotion/pages/kingpower-disney.aspx", "/th/promotion/credit-card/travel/Pages/GrabSUV151119.aspx", "/th/Apply/PersonalLoan/Pages/k-personal.aspx", "/th/promotion/Pages/onesiamthemagicaltale.aspx", "/th/promotion/credit-card/shopping/Pages/ChineseNewYear2020.aspx", "/th/promotion/Pages/Tax.aspx", "/th/promotion/Pages/Promote-Feature-3in1.aspx", "/th/promotion/Pages/Promote-Feature-4in1.aspx", "/th/promotion/pages/transfer-point.aspx", "/th/promotion/pages/heng_heng_heng.aspx", "/th/promotion/pages/up-spending.aspx"];
var activateLink_MSKPLUS = ["/th/personal/digital-banking/kplus/functions/top-up/Pages/index.html", "/th/personal/digital-banking/kplus/functions/credit-card/Pages/TransferPoint.html", "/th/personal/Digital-banking/kplus/functions/debit-card/Pages/Issue-debit-card.html", "/th/personal/digital-banking/kplus/functions/credit-card/Pages/Change-Limit.html", "/th/personal/digital-banking/kplus/functions/credit-card/Pages/Exchange-credit.html"];
var kPayLaterPage = ["/th/personal/loan/personalloan/pages/kpaylater.aspx"];

$(document).ready(function () {
    var chkReadyStateKP = setInterval(function () {
        if (document.readyState === "complete") {
            console.log('page.readyState');
            //code here
            if (getQueryString("app") === "kplus") {
                $(activateLink_KMaster).each(function (i, v) {
                    if (window.location.href.toLowerCase().match(v.toLowerCase())) {
                        $("header").hide();
                        $(".visible-w1024").hide();
                        $(".localnav").hide();
                        $(".share-alt").hide();
                        $("#maincontentBox").css("padding-top", "0px");
                        $(".shortcut_nav").each(function (i, v) {
                            if (!v.toString().toLowerCase().match("/apply/")) {
                                $(v).hide();
                            }
                        });
                        $(".footer-legal").hide();
                        $(".footer").hide();

                        $("#navigation-footer").hide();
                        setTimeout(function() {
                            $("#chatline").hide();
                            $("#navigation-widgets").hide();
                            $(".stickyNav-panelWidgets").css("grid-template-columns", "40px auto")
                            $("#navigation-page-sticky.no-list .stickyNav-panelWidgets").css("grid-template-columns", "auto")
                        },2000)              

                        $(".webchat").hide();
                        $("#kb-notify").hide();
                        $(".captcha-box").css("visibility", "hidden");

                        $("a[title*='k plus']").remove();
                        $("span:contains('พลิเคชัน K PLUS')").remove();
                        $(".art-bottom").remove();
                        $(".section-thumbnails-slider").remove();

                        if (window.location.href.toLowerCase().match("/th/personal/loan/car-loan/car-to-cash/pages/car-to-cash.aspx")) {
                            $(".sc-shortcut .sc-inner").hide();
                            $("#articles").hide();
                        }
                        if (window.location.href.toLowerCase().match("/th/personal/autoloan/pages/new-car.aspx")) {
                            $(".sc-shortcut .sc-inner").hide();
                            $("#articles").hide();
                        }
                        if (window.location.href.toLowerCase().match("/th/personal/autoloan/pages/used-car.aspx")) {
                            // $(".sc-shortcut .sc-inner").hide();
                            $(".service-container a.service").removeAttr('target');
                            $("#articles").hide();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/pages/samyan-midtown.aspx")) {
                            $("a[title='สมัคร']").remove();
                            $("footer").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/pages/kpluspointtransfer.aspx")) {
                            $(".items-slider").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/travel/Pages/GrabSUV151119.aspx".toLowerCase())) {
                            $("#section-filters").remove();
                            $(".shortcutnav").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/ChineseNewYear2020.aspx".toLowerCase())) {
                            $(".section-related").remove();
                            $(".shortcutnav").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/Pages/Tax.aspx".toLowerCase())) {
                            $("header").remove();
                        }

                        if (window.location.href.toLowerCase().match("/th/promotion/Pages/transfer-point.aspx".toLowerCase())) {
                            $(".col-md-12 .btn.pxtm-click-navMenu").remove();
                            $(".col-md-6 .app-bg").remove();
                            $("#main_sd_ed").remove();
                        }

                        if (window.location.href.toLowerCase().match("/th/promotion/Pages/Promote-Feature-3in1.aspx".toLowerCase())) {
                            $("#main_sd_ed").remove();
                            $(".art-headline").remove();
                            $(".art-content").css("margin-top", "-50px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/Pages/Promote-Feature-4in1.aspx".toLowerCase())) {
                            $("#main_sd_ed").remove();
                            $(".art-headline").remove();
                            $(".art-content").css("margin-top", "-50px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/Pages/up-spending.aspx".toLowerCase())) {
                            $("#main_sd_ed").remove();
                            $(".art-banner").remove();
                            $(".art-content").css("margin-top", "-100px");
                        }
                        if (window.location.href.toLowerCase().match("/th/privacy-policy/Pages/privacy-policy.aspx".toLowerCase())) {
                            $("#kb-notify").remove();
                            $(".main").css("padding-top", "20px");
                        }
                        if (window.location.href.toLowerCase().match("/en/privacy-policy/Pages/privacy-policy.aspx".toLowerCase())) {
                            $("#kb-notify").remove();
                            $(".main").css("padding-top", "20px");
                        }
                        if (window.location.href.toLowerCase().match("/th/privacy-policy".toLowerCase())) {
                            $("#kb-notify").remove();
                            $(".main").css("padding-top", "20px");
                        }
                        if (window.location.href.toLowerCase().match("/en/privacy-policy".toLowerCase())) {
                            $("#kb-notify").remove();
                            $(".main").css("padding-top", "20px");
                        }
                        if (window.location.href.toLowerCase().match("/EN/about/Pages/financial-conglomerate.aspx".toLowerCase())) {
                            $("#kb-notify").remove();
                            $("#nav-multimenu").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/about/Pages/financial-conglomerate.aspx".toLowerCase())) {
                            $("#kb-notify").remove();
                            $("#nav-multimenu").remove();
                        }
                        if (window.location.href.toLowerCase().match("/EN/financial-conglomerate".toLowerCase())) {
                            $("#kb-notify").remove();
                            $("#nav-multimenu").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/financial-conglomerate".toLowerCase())) {
                            $("#kb-notify").remove();
                            $("#nav-multimenu").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/personal/Digital-banking/Pages/youtrip.aspx".toLowerCase())) {
                            $("#kb-notify").remove();
                            $(".webchat").remove();
                            $("#s4-titlerow").remove();
                            $(".footer").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/personal/Insure/life/Pages/SickButSafe.aspx".toLowerCase())) {
                            $(".share-alt.open-popup-share").remove();
                            $(".shortcutnav").remove();
                            $(".header-device").remove();
                            $("#btn_link1.fixed").css("top", "-15px!important");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/pages/shop-jukjuk.aspx".toLowerCase())) {
                            $(".share-group").remove();
                            $(".shortcutnav").remove();
                            $(".header-device").remove();
                            $(".main").css("margin-top", "-30px");
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan1.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan2.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan3.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan4.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan5.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan6.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan7.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan8.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan9.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan10.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan11.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan12.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan13.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan14.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan15.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan16.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan17.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan18.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan19.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan20.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/RewardThe115092020.aspx".toLowerCase())) {
                            $('.header-device').remove();
                            $('.main').css("padding-top", "0px");
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main-container').css("padding", "0px");
                            $('.column-main').css("padding-bottom", "0px");
                            $('.column-main').css("padding-bottom", "0px");
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                            $(".sc-headline.theme-shopping").remove();
                            $("#section-filters").remove();
                            $(".shortcutnav").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/personal/the-wisdom/Privileges/localized-experiences/phuket/Pages/index.aspx".toLowerCase())) {
                            $("footer.footer").remove();
                            $(".header-device-fixed").remove();
                            $('#page').css("padding-top", "0px");
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan21.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan22.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan23.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan24.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/KingPower01102020.aspx".toLowerCase())) {
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('.main').css("padding-top", "0px");
                            $('#maincontentBox').css("padding-top", "0px");
                            $(".art-bottom").remove();
                            $("#kb-notify").remove();
                            $(".shortcutnav").remove();
                            $("footer.footer").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/personal/the-wisdom/Privileges/special-privileges/Recommended/Pages/KING-POWER_oct_2020.aspx".toLowerCase())) {
                            $('.art-function').remove();
                            $('.art-content.entrycontent').css("padding-bottom", "0px");
                            $('.sc-inner').css("padding-bottom", "0px");
                            $("a.back").remove();
                            $("footer.footer").remove();
                            $(".header-device-fixed").remove();
                        }
                        if (window.location.href.toLowerCase().match("/PTTBlueCONNECT5".toLowerCase())) {
                            $('div.header-device').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('a.share-alt.open-popup-share.visible-w767').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $(".webchat").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/health/Pages/Insurance22102020.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/travel/Pages/OnlineTravel01112020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/ShopFest29102020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/ECommerce30102020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/robinson11112020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/central11112020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/ShopDMeeKeun23102020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/BlackWeekend29102020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan25.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan26.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan27.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/special/pages/OfferXpressLoan28.aspx".toLowerCase())) {
                            $("#s4-titlerow").remove();
                            $(".footer-docstyle").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/CENTRALBLACKMIDNIGHTSALE28112020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/CentralBlackMidnightSale26112020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/RobinsonBlackFridayMadnessSale26112020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/personal/Insure/non-life/Pages/cancer-insurance.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.header-device').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('a.share-alt.open-popup-share.visible-w767').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/home-decor/Pages/HomeDecor103112020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/home-decor/Pages/HomeDecor03112020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/CENTRALPaycation14122020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/TheMallHappiertogether30112020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/ROBINSON1212WEEK12122020C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/CENTRALWOWWEEKEND191220C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/RobinsonCelebrationSale141220C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/wewillwinC.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/CentralEMCNY022021C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/RobinsonCYN29012021C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/CentralCYN29012021C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/home-decor/Pages/HomeDecorAll01022021C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/home-decor/Pages/Furnitures01022021C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/shopping/Pages/TheMallCNY29012021C.aspx".toLowerCase())) {
                            $('header#s4-titlerow').remove();
                            $('.visible-w1024.icw.header-device-fixed.mm-slideout').remove();
                            $('#maincontentBox').css("padding-top", "0px");
                            $('.main').css("padding-top", "0px");
                            $('.share-group').remove();
                            $("nav.shortcutnav").remove();
                            $("footer.footer").remove();
                            $('.article .art-headline').css("margin-bottom", "0px");
                            $('.entrycontent .one-column .column-main').css("padding-top", "15px");
                        }

                        if (window.location.href.toLowerCase().match("/th/promotion/Pages/kbank-visa-e-commerce.aspx".toLowerCase())) {
                            $('.section-applynow').remove();
                            $('.section-download').remove();
                            $("footer.footer").remove();
                        }

                        if (window.location.href.toLowerCase().match("/th/Apply/Pages/Expire.aspx".toLowerCase())) {
                            $('.header.header-docstyle').remove();
                            $('.footer.footer-docstyle').remove();
                        }

                        if (window.location.href.toLowerCase().match("/Pages/PageNotFoundError.aspx".toLowerCase())) {
                            $('.error-header').remove();
                            $('.error-footer').remove();
                        }

                        if (window.location.href.toLowerCase().match("/th/personal/Debit-Card/Pages/debit-peanuts.aspx".toLowerCase())) {
                            $('#nav').remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/personal/account/pages/taweesup-peanuts.aspx".toLowerCase())) {
                            $('#nav').remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/personal/Digital-banking/Pages/k-esavings-peanuts.aspx".toLowerCase())) {
                            $('#nav').remove();
                        }

                        if (window.location.href.toLowerCase().match("/th/promotion/pages/kplusshop-newfeature-qrscan.aspx".toLowerCase())) {
                            $('.main').css("padding-top", "0px");
                            $('.one-column .column-main').css("padding-bottom", "0px");
                        }

                        if (window.location.href.toLowerCase().match("/th/promotion/credit-card/others/Pages/KpointTransfer10112021.aspx".toLowerCase())) {
                            $('.main').css("padding-top", "0px");
                            $('#section-filters').remove();
                            $('.shortcutnav').remove();

                        }
                        if (window.location.href.toLowerCase().match("/th/personal/Digital-banking/Pages/blue-connect.aspx".toLowerCase())) {
                            $('header').remove();
                            $('footer').remove();
                            $(".wrapper").css("padding-top", "0px");
                            $(".scrollspy-nav-inner").remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/personal/Digital-banking/Pages/blue-connect/paylater.aspx".toLowerCase())) {
                            $('header').remove();
                            $('footer').remove();
                            $(".wrapper").css("padding-top", "0px");
                             $(".scrollspy-nav-inner").remove();
                            
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/pages/debit-ewallet.aspx".toLowerCase())) {
                            $('header').remove();
                            $('footer').remove();
                            $('#localnav-fixed').remove();  
                            $('.shortcutnav').remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/pages/blue-connect-targeted-oct22.aspx".toLowerCase())) {
                            $('.slogan').remove();
                        }
                        if (window.location.href.toLowerCase().match("/th/promotion/pages/wealthplus-migrate.aspx".toLowerCase())) {
                            $('.slogan').remove();
                        }
                        



                        console.log('kp-clear-complete');

                        var icx = 0;
                        var cxxcix = setInterval(function () {
                            if (window.location.href.toLowerCase().match("/th/promotion/pages/kpluspointtransfer.aspx")) {
                                $(".items-slider").remove();
                            }
                            $(".footer").hide();
                            $(".webchat").hide();
                            $("#kb-notify").hide();
                            $(".captcha-box").css("visibility", "hidden");
                            console.log('clear-again');
                            icx++;
                            if (icx === 10) {
                                clearInterval(cxxcix);
                                console.log('all-clear');
                            }
                        }, 1000);
                    }
                });
                $(activateLink_MSKPLUS).each(function (i, v) {
                    if (window.location.href.toLowerCase().match(v.toLowerCase())) {
                        $("header").hide();
                        $(".main").css("padding-top", "0px");
                        $("div.download").hide();
                        $("img[src*='/SiteCollectionDocuments/personal/digital-banking/kplus/functions/img/action-bg-m.jpg']").css("height", "210px");
                        $(".back-to-top").hide();
                        $(".functions-action").hide();
                        $(".footer").hide();
                        $(".webchat").remove();

                        var icx = 0;
                        var cxxcix = setInterval(function () {
                            $(".back-to-top").remove();
                            $(".footer").hide();
                            $(".webchat").remove();
                            console.log('clear-again');
                            icx++;
                            if (icx === 10) {
                                clearInterval(cxxcix);
                                console.log('all-clear');
                            }
                        }, 1000);
                    }
                });
                $(kPayLaterPage).each(function (i, v) {
                    if (window.location.href.toLowerCase().match(v.toLowerCase())) {
                        $('#product-detail-collapse .link.external').hide();
			            $('#menu_map').hide();
                        $('#page').css('padding-bottom', '0px');
                        // $('#navigation-header').hide();
                        // $('#navigation-page-sticky').hide();
                        $(document.head).append('<style>#navigation-header, #navigation-page-sticky { display: none !important; }</style>');
                    }
                });
            }

            clearInterval(chkReadyStateKP);
            //page load complete
        }
    }, 100);
});
