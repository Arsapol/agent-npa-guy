//extension , alternate used for fixed typically bug under web page


//appSetings

var activePageEx = [
{ url: "/th/promotion/Pages/KPLUS_linecoin.aspx", app: "k+" },
{ url: "/th/promotion/pages/travelinsuranceq4.aspx", app: "k+" },
{ url: "/personal/Pages/Home.aspx", app: "k+" },
{ url: "/business/sme/Pages/SME.aspx", app: "k+sme" },
{ url: "/personal/digital-banking/Pages/k-mobile-banking-plus.aspx", app: "k+" },
{ url: "/business/sme/Digital-banking/Pages/k-plus-sme.aspx", app: "k+sme" },
{ url: "/business/sme/Digital-banking/Pages/KPLUS_SME.aspx", app: "k+sme" },
{ url: "/promotion/Pages/K-PLUS_CreditCard.aspx", app: "k+" },
{ url: "/promotion/Pages/KPLUS_WaterworksBill.aspx", app: "k+" },
{ url: "/promotion/Pages/KPLUS-Shop.aspx", app: "k+" },
{ url: "/promotion/Pages/LeasingBillPayment_CashBack30.aspx", app: "k+" },
{ url: "/promotion/Pages/TopUpViaKPLUSMyByCAT.aspx", app: "k+" },
{ url: "/promotion/Pages/SMSAlertNow.aspx", app: "k+" },
{ url: "/promotion/Pages/TopupTrueMove-H.aspx", app: "k+" },
{ url: "/promotion/Pages/EasyTopUpAisUpTo3GB.aspx", app: "k+" },
{ url: "/promotion/Pages/SecurityTips_TripleLocks.aspx", app: "k+" },
{ url: "/promotion/Pages/PTTCashback6.aspx", app: "k+" },
{ url: "/th/business/sme/kplusshop/Pages/kplusshop.aspx", app: "k+shop" }
];

var url_kp_android = "https://play.google.com/store/apps/details?id=com.kasikorn.retail.mbanking.wap";
var url_kp_ios = "https://itunes.apple.com/th/app/k-plus/id361170631?mt=8";
var url_kp_sme_android = "https://play.google.com/store/apps/details?id=com.kasikorn.sme.mbanking";
var url_kp_sme_ios = "https://itunes.apple.com/th/app/k-plus-sme/id1181844280?mt=8";
var url_kp_shop_android = "https://play.google.com/store/apps/details?id=com.kasikornbank.kpaymerchant";
var url_kp_shop_ios = "https://itunes.apple.com/th/app/k-plus-shop-k-shop/id1142974848?l=th&mt=8";
var day_reAlert = 1; //0 is always alert

var K_PLUS_LABEL = "K PLUS";
var K_PLUS_SME_LABEL = "K PLUS SME";
var K_PLUS_SHOP_LABEL = "K PLUS SHOP";
var K_PLUS_IMAGE = "/SiteCollectionDocuments/icon-kplus.png";
var K_PLUS_SME_IMAGE = "/SiteCollectionDocuments/icon-kplus-sme.png";
var K_PLUS_SHOP_IMAGE = "/th/personal/Digital-banking/PublishingImages/QR/apply-icon-02.png";

var ACTIVE_LABEL = "";
var ACTIVE_IMAGE = "";

function getMobileOperatingSystem() {
    var userAgent = navigator.userAgent || navigator.vendor || window.opera;
    if (/windows phone/i.test(userAgent)) {
        return "windowsphone";
    }
    if (/android/i.test(userAgent)) {
        return "android";
    }
    if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
        return "ios";
    }
    return "desktop";
}

function getExtensionAppLink() {
    var filterActive = activePageEx.filter(function (el) {
        return _spPageContextInfo.serverRequestPath.toLowerCase().indexOf(el.url.toLowerCase()) != -1
    })
    if (filterActive.length > 0) {
        var crros = getMobileOperatingSystem();
        if (filterActive[0].app == "k+") {
            ACTIVE_LABEL = K_PLUS_LABEL;
            ACTIVE_IMAGE = K_PLUS_IMAGE;
            if (crros == "ios") {
                return url_kp_ios;
            } else if (crros == "android") {
                return url_kp_android;
            } else {
                return url_kp_android; //for test
            }
            return "";
        } 
		 else if (filterActive[0].app == "k+shop") {
            ACTIVE_LABEL = K_PLUS_SHOP_LABEL;
            ACTIVE_IMAGE = K_PLUS_SHOP_IMAGE;
            if (crros == "ios") {
                return url_kp_shop_ios;
            } else if (crros == "android") {
                return url_kp_shop_android;
            } else {
                return url_kp_android; //for test
            }
            return "";
        }
		else {
            ACTIVE_LABEL = K_PLUS_SME_LABEL;
            ACTIVE_IMAGE = K_PLUS_SME_IMAGE;
            if (crros == "ios") {
                return url_kp_sme_ios;
            } else if (crros == "android") {
                return url_kp_sme_android;
            } else {
                return url_kp_sme_android; //for test
            }
            return "";
        }
    } else {
        return "";
    }
    return "";
}

function closeExApp() {
    $("#ex-app").fadeOut();
    $("div#s4-workspace").css("margin-top", "0px");
    if (day_reAlert != 0) {
        setCookie("ex_app", "hide", day_reAlert);
    }
}

var ext_force_url = "";
function redirect_ext_force_url_1612() {
    window.location = ext_force_url;
}

$(document).ready(function () {
    window.mobileAndTabletcheck = function () {
        var check = false;
        (function (a) { if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino|android|ipad|playbook|silk/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0, 4))) check = true; })(navigator.userAgent || navigator.vendor || window.opera);
        return check;
    };

    if (window.mobileAndTabletcheck() && getCookie("ex_app") == "") {
        var appurl = getExtensionAppLink();
        if (appurl != "") {
            var t = '<div id="ex-app" style="background-color: #f2f2f2; padding: 10px; overflow: hidden; font-size: 0;">' +
            '<a onclick="closeExApp()" class="a-close " style="display: inline-block; vertical-align: middle; line-height: 1; padding: 0 10px 0 0;"><i class="ic ic-close" style="font-size: 10px; font-weight: 600; color: #6c6c6c;"></i></a>' +
            '<img src="{{image}}" alt="" width="60">' +
            '<span style="display: inline-block; vertical-align: middle; padding-left: 10px; color: #000; font-size: 14px; font-weight: normal;">{{title}}<br><small style="font-size: 80%;">KASIKORNBANK PCL.</small></span>' +
            '<a href="{{url}}" target="_blank" style="font-size: 18px; color: #0072ff; text-decoration: none; float: right; line-height: 63px; padding: 0 5px 0 5px;">Open</a>' +
            '</div>';
            t = t.replace("{{url}}", appurl);
            t = t.replace("{{title}}", ACTIVE_LABEL);
            t = t.replace("{{image}}", ACTIVE_IMAGE);
            $(t).insertBefore($("div.visible-w1024.header-device-fixed").children().first());
            $("div#s4-workspace").css("margin-top", "80px");

        }
    }
    
    //for variation problem
    setTimeout(function () {
        try {
            if (_spPageContextInfo.serverRequestPath.toLowerCase() == "/th/personal/loan/personal-loan/pages/express-cash-card.aspx") {
                ext_force_url = "/en/personal/Loan/personal-loan/Pages/express-cash-card.aspx";
                $("ul.lang-box").html('<li class="noindex langlink" onclick="redirect_ext_force_url_1612()">EN</li>');
                $("#DDLLang").html('<option value="/TH/personal/Loan/personal-loan/Pages/express-cash-card.aspx" selected="">TH</option><option value="/EN/personal/Loan/personal-loan/Pages/express-cash-card.aspx">EN</option>');
            }
            if (_spPageContextInfo.serverRequestPath.toLowerCase() == "/en/personal/loan/personal-loan/pages/express-cash-card.aspx") {
                ext_force_url = "/th/personal/Loan/personal-loan/Pages/express-cash-card.aspx";
                $("ul.lang-box").html('<li class="noindex langlink" onclick="redirect_ext_force_url_1612()">TH</li>');
                $("#DDLLang").html('<option value="/TH/personal/Loan/personal-loan/Pages/express-cash-card.aspx" >TH</option><option value="/EN/personal/Loan/personal-loan/Pages/express-cash-card.aspx" selected="">EN</option>');
            }
        } catch (e) {

        }
    }, 2000);
    

});



