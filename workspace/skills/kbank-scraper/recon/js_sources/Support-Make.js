$(document).ready(function(){
    var app = getURLQueryParameter("app");

    if (app !== null && app.toLowerCase() == "make") {
        addAppMakeStyle();

        var url = window.location.href.toLowerCase();
        var hideHeader = false;
        var hideFooter = false;
        var hideChatLine = false;
        var hideFreeCall = false;
        var hideShareButton = false;
        var hideSeeMoreCreditCard = false;
        var hideBottomBar = false;

        if (url.indexOf('/th/personal/CreditCard/Pages/platinum.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            hideSeeMoreCreditCard = true;
            hideBottomBar = true;
        } else if (url.indexOf('/th/personal/Insure/life/Pages/sickhealth-ipdopd.aspx'.toLowerCase()) !== -1) {
            hideFreeCall = true;
        } else if (url.indexOf('/th/personal/autoloan/pages/k-ev-shop.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            hideFreeCall = true;
        } else if (url.indexOf('/th/personal/insure/life/pages/oneplus10-1.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
        } else if (url.indexOf('/th/personal/Loan/HomeLoan/Pages/HomeLoanRefinance.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            $('#articles').hide();
        } else if (url.indexOf('/th/personal/CreditCard/Pages/kbank-linepoints.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideSeeMoreCreditCard = true;
            hideBottomBar = true;
        } else if (url.indexOf('/th/personal/CreditCard/pages/ptt-blue.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideSeeMoreCreditCard = true;
            hideBottomBar = true;
        } else if (url.indexOf('/th/personal/CreditCard/Pages/jcb.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideSeeMoreCreditCard = true;
            hideBottomBar = true;
        } else if (url.indexOf('/th/personal/CreditCard/Pages/kbank-onesiam.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideSeeMoreCreditCard = true;
            hideBottomBar = true;
        } else if (url.indexOf('/th/personal/CreditCard/Pages/kbank-shopee.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideSeeMoreCreditCard = true;
            hideBottomBar = true;
        } else if (url.indexOf('/th/personal/CreditCard/Pages/titanium.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideSeeMoreCreditCard = true;
            hideBottomBar = true;
        } else if (url.indexOf('/th/personal/CreditCard/Pages/the-passion.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideSeeMoreCreditCard = true;
            hideBottomBar = true;
        } else if (url.indexOf('/th/personal/CreditCard/pages/bangkok-hospital.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideSeeMoreCreditCard = true;
            hideBottomBar = true;
        } else if (url.indexOf('/th/personal/CreditCard/Pages/king-power.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideSeeMoreCreditCard = true;
            hideBottomBar = true;
        } else if (url.indexOf('/th/personal/CreditCard/Pages/unionpay.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideSeeMoreCreditCard = true;
            hideBottomBar = true;
        } else if (url.indexOf('/th/personal/CreditCard/pages/amway.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideSeeMoreCreditCard = true;
            hideBottomBar = true;
        } else if (url.indexOf('/th/personal/insure/non-life/pages/taonk-plus.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
        } else if (url.indexOf('/th/personal/Insure/life/pages/dhealth-easycare.aspx'.toLowerCase()) !== -1) {
            // hideHeader = true;
            // hideChatLine = true;
            hideFreeCall = true;
        } else if (url.indexOf('/th/personal/Insure/life/pages/cicashback.aspx'.toLowerCase()) !== -1) {
            // hideHeader = true;
            // hideChatLine = true;
            hideFreeCall = true;
        } else if (url.indexOf('/th/personal/insure/non-life/pages/dengue-insurance.aspx'.toLowerCase()) !== -1) {
            // hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
        } else if (url.indexOf('/th/personal/insure/non-life/pages/cancer-insurance.aspx'.toLowerCase()) !== -1) {
            // hideHeader = true;
            // hideChatLine = true;
            hideFreeCall = true;
        } else if (url.indexOf('/th/personal/Insure/life/pages/dhealthplus.aspx'.toLowerCase()) !== -1) {
            // hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
        } else if (url.indexOf('/th/personal/Insure/life/Pages/elitehealthplus.aspx'.toLowerCase()) !== -1) {
            // hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
        } else if (url.indexOf('/th/personal/insure/life/pages/sickbutsafe.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideShareButton = true;
        } else if (url.indexOf('/th/personal/insure/non-life/pages/pa_safe_pack.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
        } else if (url.indexOf('/th/personal/insure/non-life/pages/accident-personal.aspx'.toLowerCase()) !== -1) {
            // hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
        } else if (url.indexOf('/th/personal/insure/non-life/pages/accident-executive.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideShareButton = true;
        } else if (url.indexOf('/th/personal/insure/non-life/pages/accident-senior.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideShareButton = true;
        } else if (url.indexOf('/th/personal/Insure/life/Pages/perfectsaving115.aspx'.toLowerCase()) !== -1) {
            // hideHeader = true;
            // hideChatLine = true;
            hideFreeCall = true;
        } else if (url.indexOf('/th/personal/Insure/life/pages/aomsinsaving113.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
        } else if (url.indexOf('/th/personal/insure/life/pages/pro-saving-1525.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            hideFreeCall = true;
            hideShareButton = true;
            $('#thistitle').hide();
        } else if (url.indexOf('/th/personal/insure/life/pages/pro-annuity-a85-5.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            hideFreeCall = true;
            hideShareButton = true;
            $('#thistitle').hide();
        } else if (url.indexOf('/th/personal/insure/life/pages/retirement-60-5.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            hideFreeCall = true;
            hideShareButton = true;
            $('#thistitle').hide();
        } else if (url.indexOf('/th/personal/Insure/life/pages/garuntee156.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
        } else if (url.indexOf('/th/personal/insure/life/pages/muangthai-life-insurance.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideShareButton = true;
        } else if (url.indexOf('/th/personal/insure/life/pages/un-glooming.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideShareButton = true;
        } else if (url.indexOf('/th/personal/insure/life/pages/mdesignmonths.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
        } else if (url.indexOf('/th/personal/insure/life/pages/pro-life-80-4.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            hideFreeCall = true;
            hideShareButton = true;
            $('#thistitle').hide();
        } else if (url.indexOf('/th/personal/insure/life/pages/life70years.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            // hideChatLine = true;
            hideFreeCall = true;
        } else if (url.indexOf('/th/personal/insure/life/pages/whole-life-99-5.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            // hideChatLine = true;
            hideFreeCall = true;
            hideShareButton = true;
        } else if (url.indexOf('/th/personal/insure/life/pages/pro-life-99-9.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            hideFreeCall = true;
            hideShareButton = true;
            $('#thistitle').hide();
        } else if (url.indexOf('/th/personal/insure/non-life/pages/auto-comprehensive.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideShareButton = true;
        } else if (url.indexOf('/th/personal/insure/non-life/pages/auto-thrid-party.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideShareButton = true;
        } else if (url.indexOf('/th/personal/insure/non-life/pages/auto-thrid-party-plus.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideShareButton = true;
        } else if (url.indexOf('/th/personal/insure/non-life/pages/auto-compulsory.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideShareButton = true;
        } else if (url.indexOf('/th/personal/Loan/HomeLoan/Pages/Home.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            $('#articles').hide();
        } else if (url.indexOf('/th/personal/autoloan/pages/used-car.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            $('#articles').hide();
        } else if (url.indexOf('/th/personal/autoloan/pages/new-car.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
        } else if (url.indexOf('/th/personal/Loan/HomeLoan/Pages/Hometocash.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
        } else if (url.indexOf('/th/personal/loan/homeloan/pages/multi-purposes.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
        } else if (url.indexOf('/th/promotion/Pages/green-homeloan.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideShareButton = true;
        } else if (url.indexOf('/th/promotion/credit-card/reward-points/pages/condition.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            hideFreeCall = true;
        } else if (url.indexOf('/th/promotion/credit-card/reward-points/Pages/index.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            hideFreeCall = true;

            $('#page .main-headline').css('top', '0px');
            $('#page .main-headline .turnback-wrap').hide();
            $('#page .main-headline .right-menu').addClass('make-top-0');
            $('#page .sc-menu-bar-home').css('margin-top', '98px');
        } else if (url.indexOf('/th/branch/pages/index.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            hideFreeCall = true;
            $('#nav-multimenu').hide();
        } else if (url.indexOf('/th/branch'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            hideFreeCall = true;
            $('#nav-multimenu').hide();
        } else if (url.indexOf('/th/personal/digital-banking/sms/pages/k-malert.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            hideShareButton = true;
        } else if (url.indexOf('/th/personal/debit-card/pages/unionpay.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            // hideFreeCall = true;
            // hideShareButton = true;
        } else if (url.indexOf('/th/Apply/CreditCard/Pages/CC_Detail_thankyou.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideChatLine = true;
            hideFreeCall = true;
            // hideShareButton = true;
            hideBottomBar = true;
            $('#backStepBtn').hide();
        } else if (url.indexOf('/th/privacy-policy/Pages/privacy-policy.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideFooter = true;
            hideChatLine = true;
            hideFreeCall = true;
            // hideShareButton = true;

            setTimeout(function(){
                $('#BackToSubmitForm').show();
            }, 0);
        } else if (url.indexOf('/th/disclaimer/pages/disclaimer.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            hideFooter = true;
            hideChatLine = true;
            // hideFreeCall = true;
            // hideShareButton = true;
        } else if (url.indexOf('/th/personal/Loan/PersonalLoan/Pages/XpressLoan.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            // hideFooter = true;
            hideChatLine = true;
            // hideFreeCall = true;
            // hideShareButton = true;
        } else if (url.indexOf('/th/personal/Loan/PersonalLoan/Pages/Xpresscash.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            // hideFooter = true;
            hideChatLine = true;
            // hideFreeCall = true;
            // hideShareButton = true;
        }  else if (url.indexOf('/th/personal/autoloan/pages/new-car-thankyou.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            // hideFooter = true;
            hideChatLine = true;
            hideFreeCall = true;
            // hideShareButton = true;
            $('.main .action a.link').hide();
        } else if (url.indexOf('/th/personal/autoloan/pages/used-car-thankyou.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            // hideFooter = true;
            hideChatLine = true;
            hideFreeCall = true;
            // hideShareButton = true;
            $('.main .action a.link').hide();
        } else if (url.indexOf('/th/personal/Loan/HomeLoan/Pages/home-thankyou.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            // hideFooter = true;
            hideChatLine = true;
            hideFreeCall = true;
            // hideShareButton = true;
            $('#BackForKWeb').hide();
        } else if (url.indexOf('/th/personal/Loan/HomeLoan/Pages/HomeLoanRefinance-thankyou.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            // hideFooter = true;
            hideChatLine = true;
            hideFreeCall = true;
            // hideShareButton = true;
            $('#BackForKWeb').hide();
        } else if (url.indexOf('/th/personal/Loan/HomeLoan/Pages/hometocash-thankyou.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            // hideFooter = true;
            hideChatLine = true;
            hideFreeCall = true;
            // hideShareButton = true;
            $('#BackForKWeb').hide();
        } else if (url.indexOf('/th/personal/Loan/HomeLoan/Pages/multi-purposes-thankyou.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            // hideFooter = true;
            hideChatLine = true;
            hideFreeCall = true;
            // hideShareButton = true;
            $('#BackForKWeb').hide();
        } else if (url.indexOf('/th/promotion/pages/green-homeloan-thankyou.aspx'.toLowerCase()) !== -1) {
            hideHeader = true;
            // hideFooter = true;
            hideChatLine = true;
            hideFreeCall = true;
            // hideShareButton = true;
            $('#BackForKWeb').hide();
        }

        var htmlEl = $('html');

        if (hideHeader) {
            htmlEl.addClass('make-hide-header');
        }

        if (hideFooter) {
            htmlEl.addClass('make-hide-footer');
        }

        if (hideChatLine) {
            htmlEl.addClass('make-hide-chatline');
        }

        if (hideFreeCall) {
            htmlEl.addClass('make-hide-freecall');
        }

        if (hideShareButton) {
            $(".share-alt").hide();
            $('.share').hide();
        }

        if (hideSeeMoreCreditCard) {
            htmlEl.addClass('make-hide-see-more-credit-card');
        }

        if (hideBottomBar) {
            htmlEl.addClass('make-hide-bottom-bar');
        }
    }
});

function addAppMakeStyle() {
    return $(document.head).append(`<style>
                /*Support MAKE*/
                #onetrust-banner-sdk
                , #onetrust-consent-sdk
                , #ot-sdk-btn-floating
                , html.make-hide-header #navigation-header
                , html.make-hide-header header.header-main
                , html.make-hide-footer #navigation-footer
                , html.make-hide-chatline #chatline
                , html.make-hide-freecall #actionGadgets
                , html.make-hide-see-more-credit-card #back-to-main
                , html.make-hide-bottom-bar .sc-bottom-bars {
                    display: none !important;
                }

                html.make-hide-header body {
                    padding-top: 0px !important;
                }

                html.make-hide-see-more-credit-card #page .sc-product-detail {
                    padding-bottom: 0px;
                }

                #page .make-top-0 {
                    top: 0px !important;
                }
            </style>`);
}

function getURLQueryParameter(name) {
    name = name.toLowerCase();
    return decodeURIComponent((new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search.toLowerCase()) || [, ""])[1].replace(/\+/g, '%20')) || null
}
