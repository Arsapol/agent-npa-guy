$(function () {
    $(".webchatbox").css("bottom", "67px");
    // Function for check ie browser
    function msieversion() {
        var ua = window.navigator.userAgent;
        var msie = ua.indexOf("MSIE ");

        if (msie > 0 || !!navigator.userAgent.match(/Trident.*rv\:11\./)) window.location.href = "https://www.kasikornbank.com/th/pages/not-support-browser.aspx";
        return false;
    }

    displaySearch();
    $(window).on("scroll", function (e) {
        let scrollPos = $(window).scrollTop();
        e.preventDefault();
        calPositionIconFooter(scrollPos);

        displaySearch(scrollPos);
        
        $(window).resize(function() {
            calPositionIconFooter(scrollPos);
        });
    });

    msieversion();

    let ic_compare = $(".box-icon-comparision");
    let section_comparision = $("#comparision");
    ic_compare.on("click", function(){
        if (section_comparision.hasClass("active")) {
            section_comparision.removeClass("active");
        } else {
            section_comparision.addClass("active");
        }
    });

    let btn_close = section_comparision.find(".wraper-close");
    btn_close.on("click", function(){
        section_comparision.removeClass("active");
    });
 
    let elm_box_comparision = $(".box-comparision");
    elm_box_comparision.find(".ic-npa-icon-compare").on("click", function(){
        section_comparision.addClass("active");
    });

    calMaxHeightCompareMobile();
    $(window).resize(function(){
        calMaxHeightCompareMobile();
    });

});

function calMaxHeightCompareMobile() {
    let window_height = $(window).height();
    let fixed_btn_height = $(".fixed-btn-compare.show-xs").height();
    let head_height = $(".wrapper-head").height();
    let padding =  90;
    let sum_max_height = window_height - fixed_btn_height - head_height - padding;
    $("#comparision .wraper-card").css("max-height",sum_max_height+"px");
}

function calPositionIconFooter(scrollPos) {
    let windowSize = $(window).width();
    let window_height = $(window).height();
    let document_height = $(document).height();
    let bar_footer_height = $(".bar-footer").height();
    let footer_height = $("#footer").height();

    let elm_ic_comparision = $("#icw .box-icon-comparision");
    let elm_web_chat = $(".webchatbox");

    let comparision_position_old = 130;
    let newPositionMobile = 100;

    if (windowSize <= 1024) {
        if((scrollPos + window_height + bar_footer_height + footer_height) >= document_height) {
            elm_ic_comparision.css("bottom", comparision_position_old + bar_footer_height + 40 + "px");
            elm_web_chat.css("bottom", "185px");
        } else {
            elm_ic_comparision.css("bottom", comparision_position_old + "px");
            elm_web_chat.css("bottom", "67px");
        }
    }

    if (pageName === "search") {
        if (windowSize < 768 ) {
            if((scrollPos + window_height + bar_footer_height + footer_height) >= document_height) {
                elm_ic_comparision.css("bottom", comparision_position_old + newPositionMobile + bar_footer_height + 40 + "px");
                elm_web_chat.css("bottom", "285px");
            }
        }
    }
 
}

function displaySearch(position) {
    const header = $(".header-inner");
    let searchSection = $(".search-section");

    if (pageName === "home") {
        const elmBanner = $("#banner-highlight");
        if ((position + header.innerHeight()) >= elmBanner.innerHeight()) {
            $(".open-search").removeClass("d-none");
        } else {
            $(".open-search").addClass("d-none");
        }
    } else if (pageName === "search") {
        if ($(window).width() <= 1024 ) {
            searchSection.removeClass("d-none");
            $(".open-search").remove();
            $("#header").addClass("bg-grey");
        
            if ((position - header.innerHeight()) >= searchSection.innerHeight() ) {
                console.log(1111);
                $(".search-section").addClass("fixed");
            } else {
                $(".search-section").removeClass("fixed");
            }
        }
    } else {
        $(".open-search").removeClass("d-none");
    }
}
