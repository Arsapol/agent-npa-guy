const textSearchValueHeader = [
    {
        "value": "/th/propertyforsale/promotion/pages/npa-specialprice-2024.aspx",
        "text": "โปรโมชันราคาพิเศษ"
    },
    {
        "value": "/th/propertyforsale/search-filter/house/allarea/index.aspx",
        "text": "บ้านมือสอง"
    },
    {
        "value": "/th/propertyforsale/search-filter/land/allarea/index.aspx",
        "text": "ที่ดินราคาถูก"
    },
    {
        "value": "/th/propertyforsale/search/pages/index.aspx?propertyType=02&rangePrice=0,3000000",
        "text": "บ้านเดี่ยว ไม่เกิน 3 ล้าน"
    },
    {
        "value": "/th/propertyforsale/search-filter/townhouse/allarea/index.aspx",
        "text": "ทาวน์เฮ้าส์มือสอง"
    },
    {
        "value": "/th/propertyforsale/search-filter/branch-building/allarea/index.aspx",
        "text": "อาคารสำนักงาน ติดถนนใหญ่"
    }
]

let pageName = "";

$(function () {
    $(".sub-menu-toggle").on("click", function () {
        $(this).next().slideToggle();
        $(this).find(".sub-menu-arrow").toggleClass("active");
    })
    
    setTimeout(function(){
        $('link[href*="/_catalogs/masterpage/KWeb2016/assets/css/style-en.css"]').attr('disabled', 'disabled');
    }, 1000);

    //############################ Detect ipad orientation #########################
    $(window).bind("orientationchange", function (event) {
        if (window.innerWidth == 1366) {
            $("#more-filter-desktop").css({ height: "" });
            $(".more-filter-btn.close").css({ display: "none" });
            $(".more-filter-btn.desktop").css({ display: "" });
        }
    });

    //############################ More filter desktoop #########################
    $(".more-filter-btn.desktop").on("click", function (e) {
        e.preventDefault();
        $("#more-filter-desktop").animate({ height: $("#more-filter-desktop").get(0).scrollHeight });
        $("#icw #header").css({
            height: "100%",
            overflow: "scroll",
        });
        $(".more-filter-btn.close").css({ display: "flex" });
        $(".more-filter-btn.desktop").hide();

        if (window.innerWidth >= 1025) {
            if ($("#header").hasClass("fixed")) {
                // $("#header-placeholder").height($("#header").get(0).scrollHeight);
            }
        }
    });

    $(".more-filter-btn.close").on("click", function (e) {
        e.preventDefault();

        $("#icw #header").css({
            // padding: 0,
            height: "",
            overflow: "hidden",
        });

        $("#more-filter-desktop").animate({ height: 0 });
        $(".more-filter-btn.close").css({ display: "" });
        $(".more-filter-btn.desktop").css({ display: "" });
    });

    //############################ Detect scrolling #########################
    $(window).on("scroll", function (e) {
        e.preventDefault();
        var scrollPos = $(window).scrollTop();
        var _pY = 50;
        if($("#header").length){
            // _pY = $("#header").offset().top
            _pY = 200;
        }

        if (window.innerWidth <= 1024) {            
            if (scrollPos >= _pY) {
                // Check background with search
                if (!$("#header").hasClass("fixed")) {
                    $("#inner-header-placeholder").height($("#inner-header").height());
                    $("#inner-header").addClass("fixed");
                }

                // Check search icon
                if ($(".close-search").hasClass("d-none")) {
                    $(".open-search").removeClass("d-none");
                }
            } else {
                if ($("#header").hasClass("fixed")) {
                    $("#header-placeholder").height(0);
                    $("#header").removeClass("fixed");
                }

                $("#inner-header-placeholder").height(0);
                $("#inner-header").removeClass("fixed");
                if (pageName == "home") {
                    $(".open-search").addClass("d-none");
                }
                $(".close-search").addClass("d-none");
            }
        } else {            
            if (scrollPos >= _pY) {
                // Check background with search
                if (!$("#header").hasClass("fixed")) {
                    if ($("#more-filter-desktop").height() <= 0) {
                        $("#inner-header-placeholder").height(80);
                        $("#inner-header").addClass("fixed");
                    } else {
                        if ($("#header")[0].getBoundingClientRect().bottom < 230) {
                            $("#inner-header-placeholder").height($("#inner-header").height());
                            $("#inner-header").addClass("fixed");
                        } else {
                            $("#inner-header-placeholder").height(0);
                            $("#inner-header").removeClass("fixed");
                        }
                    }
                }

                // Check search icon
                if ($(".close-search").hasClass("d-none")) {
                    $(".open-search").removeClass("d-none");
                }
            } else {
                $("#inner-header-placeholder").height(0);
                $("#inner-header").removeClass("fixed");
                if (pageName == "home") {
                    $(".open-search").addClass("d-none");
                }
            }
        }
    });

    // ############################ Click mobile search after srcolling #########################
    // $(".open-search").on("click", function (e) {
    //     e.preventDefault();
    //     $(".search-section").removeClass("d-none");

    //     // $("#header-placeholder").height($("#header").height());
    //     $("#inner-header-placeholder").height(0);
    //     $("#inner-header").removeClass("fixed");
    //     $("#header").addClass("fixed");
    //     $(".open-search").addClass("d-none");
    //     $(".close-search").removeClass("d-none");

    //     $("#icw").append('<div id="backdrop" style="position: fixed; top: 0; left: 0; width: 100%; height: 100vh; background-color: rgba(0, 0, 0, 0.5); overflow: hidden; z-index: 50;"></div>');
    //     $("body").css({
    //         height: "100%",
    //         overflow: "hidden",
    //         position: "relative",
    //         touchAction: "none",
    //         "-ms-touch-action": "none",
    //     });

    //     dataLayer.push({
    //         event: "track_event",
    //         event_category: "header",
    //         event_action: "click",
    //         event_label: "open-search",
    //     });

    //     return false;
    // });

    const closePopup = document.querySelector(".close-gallery-modal");
    const openSearch = document.querySelector(".open-search");
    const popupSearch = document.querySelector(".popup-search");

    openSearch.addEventListener("click", function() {
        popupSearch.classList.add("active");
    })
    
    closePopup.addEventListener("click", function(){
        popupSearch.classList.remove("active");
    })

    $(".close-search").on("click", function (e) {
        e.preventDefault();
        $(".search-section").addClass("d-none")

        $("#inner-header-placeholder").height($("#inner-header").height());
        // $("#header-placeholder").height(0);
        $("#inner-header").addClass("fixed");
        $("#header").removeClass("fixed");
        $(".open-search").removeClass("d-none");
        $(".close-search").addClass("d-none");

        $("#backdrop").remove();
        $("body").css({
            height: "auto",
            overflow: "auto",
            position: "initial",
            touchAction: "auto",
            "-ms-touch-action": "auto",
        });

        // Close more filter on desktop
        if (window.innerWidth >= 1025) {
            $("#icw #header").css({
                backgroundImage: "",
                // padding: 0,
                height: "",
                overflow: "hidden",
            });

            $("#more-filter-desktop").animate({ height: 0 });
            $(".more-filter-btn.close").css({ display: "" });
            $(".more-filter-btn.desktop").css({ display: "" });
        }

        return false;
    });

    //############################ Submit more filter mobile #########################
    $("#more-filter-m-form").on("submit", function (e) {
        e.preventDefault();
    });

      //############################ Window resize #########################
      window.addEventListener("resize", function () {
        if (window.innerWidth <= 1024) {
            if ($("#more-filter-desktop").height() > 0) {
                $("#more-filter-desktop").css({ height: "" });
                $(".more-filter-btn.close").css({ display: "none" });
                $(".more-filter-btn.desktop").css({ display: "" });
            }
        }
    });


    callSearchTextHeader();    
});

function callSearchTextHeader() {
    if (textSearchValueHeader) {
        let html = `<div id="tag-popular-search">
                        <div class="popular-header">เลือกจากคำค้นหายอดนิยม</div>
                        <div class="all-tag-popular">`;

        $.each(textSearchValueHeader, function(i, v){
            html += `<a href="${v.value}" class="capsule-tag">${v.text}</a>`;
        });

        html += `</div>
        </div>`;

        $(html).insertAfter( "#searchx" );

    }
}

