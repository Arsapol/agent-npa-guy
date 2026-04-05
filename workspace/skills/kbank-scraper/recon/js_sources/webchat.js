var lc_formatURL = "";
var lc_page_url = "";
var lc_tooltip_delay = 5000;
var lc_tooltip_delay_fade = 1000;

var charConfig = {};
var urlConfig = [];


var urlConfig_Hide = [];

var c_lc_URL = "";

$(document).ready(function() {

    try {
        lc_page_url = (_spPageContextInfo.webAbsoluteUrl + _spPageContextInfo.serverRequestPath).toLowerCase();
    } catch (e) {
        lc_page_url = window.location.href.toLowerCase();
    }

    lc_formatURL = "http://m.me/KBankLive";

    urlConfig.push({ key: "/th/personal/Pages/index.aspx", lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
    urlConfig.push({ key: "/th/personal/CreditCard/Pages/CreditCard.aspx", lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
	urlConfig.push({ key: "/th/personal", lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
	urlConfig.push({ key: "/th/personal/Pages/Home.aspx", lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
	urlConfig.push({ key: "/th/promotion", lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig.push({ key: "/th", lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig.push({ key: "/en", lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });



urlConfig_Hide.push({ key: "/th/propertyforsale/detail", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
//urlConfig_Hide.push({ key: "/en/propertyforsale", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/non-life/Pages/cyberprotection.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/non-life/Pages/covidvaccine.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/non-life/Pages/cancer-insurance.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/non-life/Pages/dengue-insurance.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/elitehealthplus.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/dhealthplus.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/un-glooming.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/pro-life-80-4.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/whole-life-99-5.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/pro-annuity-a85-5.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/retirement-60-5.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/pro-saving-1525.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/muangthai-life-insurance.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/sickbutsafe.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/life/Pages/perfect-business-shield.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/life/Pages/perfect-business-smart.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/mrta-home.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/non-life/Pages/auto-comprehensive.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/non-life/Pages/auto-thrid-party.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/non-life/Pages/auto-thrid-party-plus.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/non-life/Pages/auto-compulsory.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/non-life/Pages/accident-senior.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/life/Pages/perfect-business-shield.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/life/Pages/perfect-business-smart.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/fire.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/all-property-risk.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/business-interuption.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/fidelity-guarantee.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/contractor-risks.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/erection-risks.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/plant-and-machinery.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/boiler-and-pressure-vessel.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/machinery-breakdown.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/electronic-equipment.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/marine-cargo.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/inland-transit.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/carriers-liability.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/trade-credit.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/jewellers-block.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/directors-and-officers-liability.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/product-liability.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/non-life/Pages/fleet-motor.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/sme/insure/perfect-employee-care", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });


urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/credit-shield.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/life/Pages/mrta-home-max.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/non-life/Pages/k-cancer.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/personal/Insure/non-life/Pages/accident-executive.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/life/Pages/perfect-business-shield.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/life/Pages/perfect-business-smart.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/fire.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/all-property-risk.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/business-interuption.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/fidelity-guarantee.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/contractor-risks.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/erection-risks.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/plant-and-machinery.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/boiler-and-pressure-vessel.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/machinery-breakdown.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/electronic-equipment.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/marine-cargo.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/inland-transit.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/carriers-liability.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/trade-credit.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/jewellers-block.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/directors-and-officers-liability.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/product-liability.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/non-life/Pages/fleet-motor.aspx", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });
urlConfig_Hide.push({ key: "/th/business/insure/perfect-employee-care", except: [], lblTH_1: "<span class='text'>กรุณาเลือกช่องทางติดต่อ</span>", lblEN_1: "<span class='text'>Please select a contact method</span>", lblTH_2: "<span class='text'>มีคำถาม? แชทกับ KBank Live</span>", lblEN_2: "<span class='text'>Have questions? Chat with KBank Live</span>" });

    //urlConfig.push({ key: "", lblTH_1: "", lblEN_1: "", lblTH_2: "", lblEN_2: "" });

    //$("#livechat").css("display", "none");

    setTimeout(function() { setChat(); }, 0);

});

function langIsTH() {
    try {
        return (_spPageContextInfo.currentCultureName.substr(0, 2) == "th" ? true : false);
    } catch (e) {
        return true;
    }
}

function setChat() {
    var popup_url = "";

    var urlConfig_filter = urlConfig.filter(function(el) { return lc_page_url.indexOf(el.key.toLowerCase()) != -1 });
	
	var urlConfig_filter_Hide = urlConfig_Hide.filter(function(el) { 
        var matchKey = lc_page_url.indexOf(el.key.toLowerCase()) != -1;
        var matchExcept = false;

        if(el.except !== undefined){
            var i = 0;
            var exceptCount = el.except.length;
            var exceptEl;

            while(i < exceptCount){
                exceptEl = el.except[i];

                if(lc_page_url.indexOf(exceptEl.toLowerCase()) != -1){
                    matchExcept = true;
                    break;
                }

                i++;
            }
        }

        return matchKey && !matchExcept;
    });
	
	
	
    if (urlConfig_filter.length > 0 && urlConfig_filter_Hide.length == 0) {
        urlConfig_filter = urlConfig_filter[0];
        popup_url = lc_formatURL;
        c_lc_URL = popup_url;

        var htmlChat = "<div class='webchatbox' style='cursor:pointer;'>" +
            "<div class='chat-tooltip-info'>" +
            "<div class='chat-hover-tooltip'>" +
            "<div class='tooltip-web content-mb2'>" +
            "<span class='tooltip-txt-intro txt1'>" + (langIsTH() ? urlConfig_filter.lblTH_2 : urlConfig_filter.lblEN_2) + "</span>" +
            "<span class='tooltip-close-btn' id='tooltip-close'>" +
            "<img src='/SiteCollectionDocuments/assets/webchat/img/close-mb.png' width='25' alt='close'>" +
            "</span>" +
            "</div>" +
            "</div>" +
            "<div class='btn-chatweb-choose'>" +
            "<div class='webchatbox-inner'>" +
            "<div class='chat-list'>" +
            "<a id='chatline' href='https://kbank.co/LINEfriend' target='_blank'>" +
            "<img src='/SiteCollectionDocuments/assets/webchat/img/icon_line.png' alt='icon_line'>" +
            "</a>" +
            "</div>" +
            "</div>" +
            "</div>" +
            "</div>" +
            "</div>";

        $("body").append(htmlChat);

        $("#chatbox").click(function() {
            window.open('http://m.me/KBankLive', '_blank');
            ga('send', 'event', 'KBank', 'KBank_PrintR', 'Click:PrintR');
        });

        // $("#chatline").click(function() {
        //     window.open('https://kbank.co/LINEfriend', '_blank');
            //ga('send', 'event', 'KBank', 'KBank_PrintR', 'Click:PrintR');
        // });

        // $(".webchatbox-inner").delay(1000).fadeOut(1000);

        try{
            let searchParam = new URLSearchParams(window.location.search);
            let getParamAPP = searchParam.get("app");
        
            if (getParamAPP === "kplus") {
                $('.webchatbox').hide();
            }
        }catch(e){
            // empty
        }

        $(function() {
            var kb_webchat = $(".webchatbox"),
                kb_webchat_close = kb_webchat.find("#tooltip-close");

            console.log("run...");

            // $(".webchatbox-inner").hide();

            // mobile
            var __Device = (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase()));

            // close func
            kb_webchat_close.click(function(e) {
                e.preventDefault();
                $('.tooltip-web.content-mb2').fadeOut();
            });

            // view Device 
            // if (!__Device == true) {
                // $('.tooltip-web.content-mb2').hide();
                $('.tooltip-web').delay(5000).fadeOut();
                // hover
                $(".btn-chatweb-choose").hover(function() {
                    $('.tooltip-web').fadeIn();
                }, function() {
                    $('.tooltip-web').fadeOut();
                });
                
            // } else {
                // $('.tooltip-web.content-pc1').hide();
                // $('.tooltip-web.content-mb2').show();
            // }

            // click func
            $('#chooseChat').on('click', function ChatMenu(e) {
                e.preventDefault();
                if ($('#menu_icon').hasClass('open-tabs')) {
                    $('#menu_icon').removeClass('open-tabs');
                    // $(".webchatbox-inner").slideToggle("down");
                    $('#menu_icon').attr('src', '/SiteCollectionDocuments/assets/webchat/img/icon_webchat.png');
                    if (__Device == true) {
                        $('.tooltip-web.content-pc1').hide();
                        $('.tooltip-web.content-mb2').fadeIn();
                    }
                } else {
                    $('#menu_icon').addClass('open-tabs');
                    // $(".webchatbox-inner").slideToggle("up");
                    $('#menu_icon').attr('src', '/SiteCollectionDocuments/assets/webchat/img/icon_close.png');
                    if (__Device == true) {
                        $('.tooltip-web.content-mb2').hide();
                        $('.tooltip-web.content-pc1').fadeIn();
                    }
                }
            });
        });

    }
}