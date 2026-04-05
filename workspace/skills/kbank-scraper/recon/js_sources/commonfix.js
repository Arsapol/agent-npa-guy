//v1.1.1

$(document).ready(function () {

    if (window.location.href.toLowerCase().endsWith(".com/creditcardform")) {
        window.location = "https://www.kasikornbank.com/th/download/Pages/result.aspx?type=7&group=1";
    }

    if (window.location.href.toLowerCase().endsWith(".com/xpresscashform")) {
        window.location = "https://www.kasikornbank.com/th/download/Pages/result.aspx?type=8&group=1";
    }

    if (window.location.href.toLowerCase().endsWith(".com/xpressloanform")) {
        window.location = "https://www.kasikornbank.com/th/download/Pages/result.aspx?type=59&group=1";
    }

    var _overAction = null,
        _counterx = null,
        _clsx = false;
    
    var chkReadyStateCOMMONFIX = setInterval(function () {
        if (document.readyState === "complete") {
            if (window.location.search.toLowerCase().indexOf("?type=57&group=2") != -1) {
                console.log(">> CommonFix: active");
                //
                _overAction = setInterval(function(){
                    _counterx++;
                    if($("#tbodyfill").length){
                        overwriteLink();
                        _clsx = true;
                    }
                    if(_counterx >= 200){
                        _clsx = true;
                    }
                    //
                    if(_clsx){
                        clearInterval(_counterx);
                    }
                }, 100)
            }
            if (_spPageContextInfo.serverRequestPath.toLowerCase().indexOf("blackpink") != -1) {
                $("div#page").attr("data-campaign-id", "DEBIT_BLACKPINK");
            }
            clearInterval(chkReadyStateCOMMONFIX);
            //page load complete
        }
    }, 100);
    
    function overwriteLink(){
        console.log(">> CommonFix: overwrite link...");
        // Link 01
        $("a[href='/th/Download/Level4_doc/EDC_ApplicationForm_TH.pdf']").attr("href", "/th/business/sme/financial-services/collection-solutions/Documents/EDC_ApplicationForm_TH.pdf");
        // Link 02
        $("a[href='/th/Download/Level4_doc/TC-KMerchant_th.pdf']").attr("href", "/th/business/sme/financial-services/collection-solutions/Documents/TC-KMerchant_th.pdf");
    }
    
    var ts_fix01 = setInterval(function () {
        $("a[href='tel:']").each(function (i, v) {
            try {
                $(v).attr('href', 'tel:' + $(v).attr('title').replace(/-/g, ''));
                clearInterval(ts_fix01);
            } catch (e) {
                console.log('exception-trans-href-tel');
            }
        });
    }, 500);

    //var ts_fix02 = setInterval(function () {
    //    try {
    //        //new case -> support for SME link
    //        $("a[href*='/businesscontact/online-application-selected?']").each(function (i, v) {
    //            var oref = $(v).attr("href");
    //            $(v).attr("href", oref + window.location.search.replace("?","&"));
    //        });
    //
    //        $("a[href$='aspx']:contains('สมัคร')").each(function (i, v) {
    //            var oref = $(v).attr("href");
    //            $(v).attr("href", oref + window.location.search);
    //        });
    //        $("a[href$='aspx']:contains('รายละเอียด')").each(function (i, v) {
    //            var oref = $(v).attr("href");
    //            $(v).attr("href", oref + window.location.search);
    //        });
    //        $("a[href$='aspx']:contains('สนใจ')").each(function (i, v) {
    //            var oref = $(v).attr("href");
    //            $(v).attr("href", oref + window.location.search);
    //        });
    //        $("a[href$='aspx']:contains('Apply')").each(function (i, v) {
    //            var oref = $(v).attr("href");
    //            $(v).attr("href", oref + window.location.search);
    //        });
    //        $("a[href$='aspx']:contains('ดูโปรโมชั่น')").each(function (i, v) {
    //            var oref = $(v).attr("href");
    //            $(v).attr("href", oref + window.location.search);
    //        });
    //		$("a[href$='aspx'][class*='catalog_credit_card']").each(function (i, v) {
    //            var oref = $(v).attr("href");
    //            $(v).attr("href", oref + window.location.search);
    //        });
    //		clearInterval(ts_fix02);
    //    } catch (e) {
    //        console.log('exception-fix-utm-catch');
    //    }
    //}, 500);

    var ts_fix_03 = setInterval(function () {
        try {

            //link 1
            if (_spPageContextInfo.serverRequestPath.toLowerCase() == "/th/promotion/pages/nobledebentures2562.aspx") {
                $("ul.lang-box").html('<li class="noindex langlink" data-link="/en/promotion/Pages/NobleDebentures2562.aspx">EN</li>');
                $("#DDLLang").html('<option value="/TH/promotion/Pages/NobleDebentures2562.aspx" selected="">TH</option><option value="/EN/promotion/Pages/NobleDebentures2562.aspx">EN</option>')
                $("li.langlink").click(function () {
                    window.location = $(this).attr("data-link")
                });
                clearInterval(ts_fix_03);
            }
            if (_spPageContextInfo.serverRequestPath.toLowerCase() == "/en/promotion/pages/nobledebentures2562.aspx") {
                $("ul.lang-box").html('<li class="noindex langlink" data-link="/th/promotion/Pages/NobleDebentures2562.aspx">TH</li>');
                $("#DDLLang").html('<option value="/TH/promotion/Pages/NobleDebentures2562.aspx">TH</option><option value="/EN/promotion/Pages/NobleDebentures2562.aspx" selected="">EN</option>');
                $("li.langlink").click(function () {
                    window.location = $(this).attr("data-link")
                });
                clearInterval(ts_fix_03);
            }

            //link 2
            if (_spPageContextInfo.serverRequestPath.toLowerCase() == "/th/promotion/pages/mtc-debentures-4.aspx") {
                $("ul.lang-box").html('<li class="noindex langlink" data-link="/en/promotion/Pages/mtc-debentures-4.aspx">EN</li>');
                $("#DDLLang").html('<option value="/TH/promotion/Pages/mtc-debentures-4.aspx" selected="">TH</option><option value="/EN/promotion/Pages/mtc-debentures-4.aspx">EN</option>')
                $("li.langlink").click(function () {
                    window.location = $(this).attr("data-link")
                });
                clearInterval(ts_fix_03);
            }
            if (_spPageContextInfo.serverRequestPath.toLowerCase() == "/en/promotion/pages/mtc-debentures-4.aspx") {
                $("ul.lang-box").html('<li class="noindex langlink" data-link="/th/promotion/Pages/mtc-debentures-4.aspx">TH</li>');
                $("#DDLLang").html('<option value="/TH/promotion/Pages/mtc-debentures-4.aspx">TH</option><option value="/EN/promotion/Pages/mtc-debentures-4.aspx" selected="">EN</option>');
                $("li.langlink").click(function () {
                    window.location = $(this).attr("data-link")
                });
                clearInterval(ts_fix_03);
            }
            //link 3
            if (_spPageContextInfo.serverRequestPath.toLowerCase() == "/th/promotion/pages/sansiridebentures-3.aspx") {
                $("ul.lang-box").html('<li class="noindex langlink" data-link="/en/promotion/pages/sansiridebentures-3.aspx">EN</li>');
                $("#DDLLang").html('<option value="/th/promotion/pages/sansiridebentures-3.aspx" selected="">TH</option><option value="/en/promotion/pages/sansiridebentures-3.aspx">EN</option>')
                $("li.langlink").click(function () {
                    window.location = $(this).attr("data-link")
                });
                clearInterval(ts_fix_03);
            }
            if (_spPageContextInfo.serverRequestPath.toLowerCase() == "/en/promotion/pages/sansiridebentures-3.aspx") {
                $("ul.lang-box").html('<li class="noindex langlink" data-link="/th/promotion/pages/sansiridebentures-3.aspx">TH</li>');
                $("#DDLLang").html('<option value="/th/promotion/pages/sansiridebentures-3.aspx">TH</option><option value="/en/promotion/pages/sansiridebentures-3.aspx" selected="">EN</option>');
                $("li.langlink").click(function () {
                    window.location = $(this).attr("data-link")
                });
                clearInterval(ts_fix_03);
            }

            //link 4
            if (_spPageContextInfo.serverRequestPath.toLowerCase() == "/th/personal/digital-banking/kbankcyberrisk/pages/index.aspx") {
                $("ul.lang-box").html('<li class="noindex langlink" data-link="/en/personal/digital-banking/kbankcyberrisk/pages/index.aspx">EN</li>');
                $("#DDLLang").html('<option value="/th/personal/digital-banking/kbankcyberrisk/pages/index.aspx" selected="">TH</option><option value="/en/personal/digital-banking/kbankcyberrisk/pages/index.aspx">EN</option>')
                $("li.langlink").click(function () {
                    window.location = $(this).attr("data-link")
                });
                clearInterval(ts_fix_03);
            }
            if (_spPageContextInfo.serverRequestPath.toLowerCase() == "/en/personal/digital-banking/kbankcyberrisk/pages/index.aspx") {
                $("ul.lang-box").html('<li class="noindex langlink" data-link="/th/personal/digital-banking/kbankcyberrisk/pages/index.aspx">TH</li>');
                $("#DDLLang").html('<option value="/th/personal/digital-banking/kbankcyberrisk/pages/index.aspx">TH</option><option value="/en/personal/digital-banking/kbankcyberrisk/pages/index.aspx" selected="">EN</option>');
                $("li.langlink").click(function () {
                    window.location = $(this).attr("data-link")
                });
                clearInterval(ts_fix_03);
            }


        } catch (e) {
            console.log('exception-try-fix-variation-c03');
            clearInterval(ts_fix_03);
        }
    }, 500);


    var ts_fix04 = setInterval(function () {
        $('.share-google-plus').each(function (i, v) {
            try {
                $('.share-google-plus').addClass("hidden");
                clearInterval(ts_fix04);
            } catch (e) {
                console.log('share-google-plus');
                clearInterval(ts_fix04);
            }
        });
    }, 500);

});

$(window).on("load", function () {
    addRL();
    // toggleRLOnScroll();
  });
  
  $(window).resize(function () {
    addRL();
  });
  
  function addRL() {
    const pageName = location.pathname.toLowerCase();
    const pageList = [
      "/th/personal/credit-card/pages/gold.aspx",
      "/en/personal/credit-card/pages/gold.aspx",
      "/th/personal/credit-card/pages/k-home-smile-club.aspx",
      "/en/personal/credit-card/pages/k-home-smile-club.aspx",
      "/th/personal/credit-card/pages/k-wave-nfc.aspx",
      "/en/personal/credit-card/pages/k-wave-nfc.aspx",
      "/th/personal/credit-card/pages/k-wave.aspx",
      "/en/personal/credit-card/pages/k-wave.aspx",
      "/th/personal/credit-card/pages/classic.aspx",
      "/en/personal/credit-card/pages/classic.aspx",
      "/th/personal/credit-card/pages/the-wisdom-infinite.aspx",
      "/en/personal/credit-card/pages/the-wisdom-infinite.aspx"
    ];
    if (
      window.location.search.toLowerCase().indexOf("?type=7&group=1") != -1 ||
      pageList.includes(pageName)
    ) {
      if (pageName.includes("/th/")) {
        if ($(".section-rl")) {
          $(".section-rl").remove();
        }
        const html = `<div class="section-rl" style="bottom: 0px;">
                                <p>ใช้เท่าที่จำเป็น และชำระคืนได้เต็มจำนวนตามกำหนด จะได้ไม่เสียดอกเบี้ย 16% ต่อปี / <span style="white-space: nowrap;">อัตราดอกเบี้ย 0% </span>เมื่อลูกค้าชำระเต็มจำนวนภายในวันครบกำหนดชำระ </p>
                            </div>`;
        $("#page").append(html);
        setTimeout(function () {
          $("#navigation-footer").css(
            "margin-bottom",
            $(".section-rl").innerHeight()
          );
          $("#navigation-widgets").css(
            "bottom",
            $(".section-rl").innerHeight() + 8
          );
        }, 500);
      } else if (pageName.includes("/en/")) {
        if ($(".section-rl")) {
          $(".section-rl").remove();
        }
        const html = `<div class="section-rl" style="bottom: 0px;">
                              <p>Use when necessary and pay back full amount on time 
                              to avoid 16% p.a. interest rate. / 0% Interest rate when pay back 
                              full amount on time.</p>
                          </div>`;
        $("#page").append(html);
        setTimeout(function () {
          $("#navigation-footer").css(
            "margin-bottom",
            $(".section-rl").innerHeight()
          );
          $("#navigation-widgets").css(
            "bottom",
            $(".section-rl").innerHeight() + 8
          );
        }, 500);
      } else {
        $("#navigation-footer").css("margin-bottom", "0px");
      }
    }
  }
  
  function toggleRLOnScroll() {
    $(window).scroll(function () {
      if ($(window).scrollTop() === 0) {
        $(".section-rl").hide();
      } else {
        $(".section-rl").show();
      }
    });
  }