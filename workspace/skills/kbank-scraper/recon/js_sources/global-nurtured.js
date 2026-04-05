/* Core Media Application */
window.matchMedia || (window.matchMedia = function () {
    "use strict";

    var styleMedia = (window.styleMedia || window.media);
    if (!styleMedia) {
        var style = document.createElement('style'),
            script = document.getElementsByTagName('script')[0],
            info = null;

        style.type = 'text/css';
        style.id = 'matchmediajs-test';

        script.parentNode.insertBefore(style, script);
        info = ('getComputedStyle' in window) && window.getComputedStyle(style, null) || style.currentStyle;

        styleMedia = {
            matchMedium: function (media) {
                var text = '@media ' + media + '{ #matchmediajs-test { width: 1px; } }';

                if (style.styleSheet) {
                    style.styleSheet.cssText = text;
                } else {
                    style.textContent = text;
                }

                return info.width === '1px';
            }
        };
    }

    return function (media) {
        return {
            matches: styleMedia.matchMedium(media || 'all'),
            media: media || 'all'
        };
    };
}());


let countTimeTooltip = 0;
let timerTooltip = "";
let minuteTooltip = 1;
let checkSesstionTooltip = getCookie("openTooltip");

(function () {
    if (window.matchMedia && window.matchMedia('all').addListener) {
        return false;
    }

    var localMatchMedia = window.matchMedia,
        hasMediaQueries = localMatchMedia('only all').matches,
        isListening = false,
        timeoutID = 0,
        queries = [],
        handleChange = function (evt) {
            clearTimeout(timeoutID);

            timeoutID = setTimeout(function () {
                for (var i = 0, il = queries.length; i < il; i++) {
                    var mql = queries[i].mql,
                        listeners = queries[i].listeners || [],
                        matches = localMatchMedia(mql.media).matches;

                    if (matches !== mql.matches) {
                        mql.matches = matches;

                        for (var j = 0, jl = listeners.length; j < jl; j++) {
                            listeners[j].call(window, mql);
                        }
                    }
                }
            }, 30);
        };

    window.matchMedia = function (media) {
        var mql = localMatchMedia(media),
            listeners = [],
            index = 0;

        mql.addListener = function (listener) {
            if (!hasMediaQueries) return;

            if (!isListening) {
                isListening = true;
                window.addEventListener('resize', handleChange, true);
            }
            if (index === 0) {
                index = queries.push({
                    mql: mql,
                    listeners: listeners
                });
            }

            listeners.push(listener);
        };
        mql.removeListener = function (listener) {
            for (var i = 0, il = listeners.length; i < il; i++) {
                if (listeners[i] === listener) {
                    listeners.splice(i, 1);
                }
            }
        };
        return mql;
    };

}());

function getCookie(name) {
    function escape(s) { return s.replace(/([.*+?\^$(){}|\[\]\/\\])/g, '\\$1'); }
    var match = document.cookie.match(RegExp('(?:^|;\\s*)' + escape(name) + '=([^;]*)'));
    return match ? match[1] : null;
}

function countSessionTimer() {
    $(".tooltip-search").show();
    if (countTimeTooltip === minuteTooltip) {
        stopTimer()
        $(".tooltip-search").hide();
    }
    countTimeTooltip++
}
    
function stopTimer() {
  clearInterval(timerTooltip);
}


// Sharer //
function addQS(d, c) {
    var a = [];
    for (var b in c)
        if (c[b]) a.push(b.toString() + '=' + encodeURIComponent(c[b]));
    return d + '?' + a.join('&')
}

function getMETAContent(attr, data) {
    var meta = document.getElementsByTagName("META"),
        max = meta.length;
    for (var i = 0; i < max; i++) {
        if (meta[i].getAttribute(attr) == data) {
            return meta[i].content;
        }
    }
    return -1;
}

function fbShare() {
    var g = {
        u: document.URL,
        t: document.title
    };
    var a = addQS('https://www.facebook.com/sharer.php', g);
    window.open(a, 'sharer', 'toolbar=0,status=0,width=626,height=436');
    return false
}

function fbIMGShare(img) {
    var g = {
        u: document.URL + "?fbimg=" + img,
        t: document.title
    };
    var a = addQS('https://www.facebook.com/sharer.php', g);
    window.open(a, 'sharer', 'toolbar=0,status=0,width=626,height=436');
    return false
}

function fbURLShare(u) {
    var g = {
        u: u,
        t: document.title
    };
    var a = addQS('https://www.facebook.com/sharer.php', g);
    window.open(a, 'sharer', 'toolbar=0,status=0,width=626,height=436');
    return false;
}

function tweetShare() {
    var g = {
        url: document.URL,
        text: document.title + ' - '
    };
    var a = addQS('http://twitter.com/share', g);
    window.open(a, 'tweet', 'toolbar=0,status=0,width=626,height=436');
    return false;
}

function tweetURLShare(u) {
    var g = {
        url: u,
        text: document.title + ' - '
    };
    var a = addQS('http://twitter.com/share', g);
    window.open(a, 'tweet', 'toolbar=0,status=0,width=626,height=436');
    return false;
}

function gpShare() {
    var g = {
        url: document.URL,
        hl: "th"
    };
    var a = addQS('https://plus.google.com/share', g);
    window.open(a, 'sharer', 'menubar=no,toolbar=no,resizable=yes,status=0,width=600,height=600');
    return false;
}

function lineMSG() {
    window.location = "line://msg/text/" + encodeURIComponent(document.URL);
}

function pinShare(m) {
    var ogimg = getMETAContent("property", "og:image");
    ogimg = ogimg.replace("480x250", "full");

    var g = {
        url: document.URL,
        description: document.title + '\n' + $("meta[property=og\\:description]").attr('content'),
        media: ogimg
    };

    if (m != undefined) g.media = m;
    var a = addQS('https://www.pinterest.com/pin/create/button/', g);
    window.open(a, 'sharer', 'menubar=no,toolbar=no,resizable=yes,status=0,width=750,height=331');
    return false;
}

function mailShare() {
    var g = 'mailto:';
    g += '?subject=' + encodeURIComponent(document.title) + ' %2D KASIKORNBANK';
    g += '&body=' + $("meta[property=og\\:description]").attr('content') + '\n\n' + encodeURIComponent(document.URL);
    win = window.open(g, 'emailWindow');
}

function onScroll(event) {
    var scrollPos = $(document).scrollTop();
    $('a.moveScroll').each(function () {
        var currLink = $(this),
            refElement = $(currLink.attr("href")),
            localNav = $('#localnav-fixed').outerHeight(),
            headerDevice = $('.header-device').outerHeight(),
            h = localNav + headerDevice - 1;
        if (refElement.length) {
            if (refElement.position().top - h <= scrollPos && refElement.position().top - h + refElement.height() > scrollPos) {
                $('a.moveScroll').removeClass("active");
                currLink.addClass("active");
            } else {
                currLink.removeClass("active");
            }
        }
    });
}
// Manipulate how original renderers are loaded.
(window.jQuery) && (function ($) {
    function PageUtil_isInEditMode() {
        var n = document.getElementById('MSOSPWebPartManager_DisplayModeName');
        var v = n.value;
        return (v === 'Edit' || v === 'Design') ? true : false;
    }

    var loadEveryViews = [],
        loadOnlyUserView = [];

    /*
    Usage:

    loadEveryViews.push(function () {
    });

    */

    loadEveryViews.push(function () {
        // Anchor tel //
        var a = navigator.userAgent || navigator.vendor || window.opera;
        if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0, 4))) {
            document.body.className += " device-mobile";
        } else {
            $("a[href^=tel]").click(function (e) {
                e.preventDefault();
            });
        }
    });
    // Render menu
    $('.submenu-bottom').hide();
    loadEveryViews.push(function () {
        $(".header").each(function () {
            $('.submenu-bottom').appendTo($('.submenu'));
            $('.submenu').parent().addClass('has-submenu');

            var hover = false;
            var submenu;
            $('.has-submenu').mouseover(function () {
                submenu = $(this);
                hover = true;
                setTimeout(function () {
                    if (hover) {
                        submenu.addClass('mouseenter');
                    }
                }, 300);
            }).mouseleave(function () {
                hover = false;
                try {
                    submenu.removeClass('mouseenter');
                } catch (err) {}
            });

            $('nav#menu').each(function () {
                var _API = $('nav#menu').mmenu({
                    extensions: ["effect-listitems-fade", 'effect-menu-slide', "multiline"],
                    navbar: {
                        title: ""
                    },
                    setSelected: {
                        parent: true
                    }
                }, {
                    offCanvas: {
                        pageSelector: "#s4-workspace"
                    },
                    classNames: {
                        fixedElements: {
                            fixed: "header-fixed"
                        }
                    }
                }).data('mmenu');

                var $burger = $('#hamburger').on('click', function (e) {
                    e.preventDefault();
                    if ($('html').hasClass('mm-opened')) {
                        _API.close();
                    } else {
                        _API.open();
                    }
                });

                _API.bind('closed', function () {
                    $burger.removeClass('is-active');
                });
                _API.bind('opened', function () {
                    $burger.addClass('is-active');
                });
            });

            $(".kb-language").each(function () {
                var kb_Lang = $(this),
                    kb_lang_selected = kb_Lang.find(".lang-selected"),
                    kb_lang_box = kb_Lang.find(".lang-box");

                kb_lang_selected.on('click', function () {
                    kb_lang_box.slideToggle(150);
                });
            });

        });
    });
    loadEveryViews.push(function () {
        if ($("#box-login").length) {

            var _API = $('#box-login').mmenu({
                extensions: ["pagedim-black"],
                navbar: {
                    title: ""
                },
                dropdown: true
            }).data('mmenu');

            function handleMQL(mql) {
                if (mql.matches) {
                    $('.header-device .tool-login').on('click', function (e) {
                        e.preventDefault();
                        if ($('html').hasClass('mm-opened')) {
                            _API.close();
                        } else {
                            _API.open();
                        }
                    });
                } else {
                    _API.close();
                }
            }

            var mql = window.matchMedia("(max-width: 1024px)");
            mql.addListener(handleMQL);
            handleMQL(mql);
        }
    });
    loadEveryViews.push(function () {
        if (_spPageContextInfo.currentCultureName.substr(0, 2).toUpperCase() == "EN") {
            var css_link = $("<link>", {
                rel: "stylesheet",
                type: "text/css",
                href: "/_catalogs/masterpage/KWeb2016/assets/css/style-en.css"
            });
            css_link.appendTo('head');
        }
    });
    /*
    Usage:

    loadOnlyUserView.push(function () {
    });

    */






    loadOnlyUserView.push(function () {
        if ($("#localnav-fixed").length) {
            var fixToSel = '#s4-workspace',
                ribbonHeight = $('#ms-designer-ribbon').height();

            var localNav = $("#localnav-fixed"),
                slickNav = $(".slicknav");

            //localNav.fixTo('body', { mind: '.header-device' });
            localNav.fixTo(fixToSel, {
                mind: '.header-device',
                useNativeSticky: false
            });
            //$('#s4-bodyContainer').css('margin-top', ribbonHeight);
            //localNav.fixTo(fixToSel, { mind: '.header-device', useNativeSticky: false, top: ribbonHeight });

            slickNav.each(function () {
                var navbtn = $(this).find(".slicknav-btn"),
                    navmenu = $(this).find(".slicknav-menu");
                if (navmenu.find("li a").length) {
                    navbtn.click(function (e) {
                        e.preventDefault();
                        $(this).toggleClass("slicknav-open");
                        navmenu.slideToggle(300);
                    });
                } else {
                    navbtn.hide();
                }
            });


            function handleMQL(mql) {
                if (mql.matches) {
                    localNav.fixTo('stop');
                    sidebarNav.fixTo('start');
                } else {
                    localNav.fixTo('start');
                    sidebarNav.fixTo('stop');
                }
            }

            if ($("#sidebar-fixed").length) {
                var mql = window.matchMedia("(max-width: 991px)"),
                    sidebarNav = $("#sidebar-fixed");

                //sidebarNav.fixTo('body', { mind: '.header-device', zIndex: 10 });
                sidebarNav.fixTo(fixToSel, {
                    mind: '.header-device',
                    zIndex: 10
                });
                mql.addListener(handleMQL);
                handleMQL(mql);
            }
        }

        if ($('.localnav-links').length) {
            $('.localnav-links').perfectScrollbar();
        }

        if ($('.ps-active-x').length) {
            $('.ps-active-x.pull-right').wrap('<div class="localnav-links-wrap pull-right"></div>');
            $('.ps-active-x.pull-left').wrap('<div class="localnav-links-wrap pull-left"></div>');
        }

        if ($('.sidebar-fixed').length) {
            $('.sidebar-fixed .sidebar-inner').perfectScrollbar();
        }
    });
    loadOnlyUserView.push(function () {


        var thingToMove = 'html,body,#s4-bodyContainer';
        $(document).on("scroll", onScroll);

        $('a.moveScroll').on('click', function (e) {
            e.preventDefault();
            $(document).off("scroll");

            $('.localnav a.moveScroll').each(function () {
                $(this).removeClass('active');
            });
            $(this).addClass('active');

            var target = $(this.hash),
                localNav = $('#localnav-fixed').outerHeight(),
                headerDevice = $('.header-device').outerHeight(),
                h = localNav + headerDevice - 1;
            target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
            if (target.length) {
                $('html,body').animate({
                    scrollTop: target.offset().top - h
                }, 800, 'swing', function () {
                    $(document).on("scroll", onScroll);
                });
            }

        });
    });
    // HighLight //
    loadOnlyUserView.push(function () {
        if ($("#highlight-slider .master-slider .ms-slide").length > 0 && window.disableNurturedHighlightSliderSetup !== true) {
            var slider = new MasterSlider();

            var _host = $("#highlight-slider"),
                msslider = _host.find(".master-slider"),
                items = _host.find(".ms-slide"),
                total = items.length,
                loop = items.length > 2;

            if (window.screen.width < 768) {
                // Mobile
                _host.find(".px-masterslider-imgx").each(function () {
                    $(this).data('src', $(this).data('altMobile'));
                })
                slider.setup(msslider, {
                    width: 640,
                    height: 320,
                    autoHeight: true,
                    layout: 'fullwidth',
                    view: 'parallaxMask',
                    space: 0,
                    autoplay: true,
                    loop: loop
                });
            } else {
                // Desktop
                slider.setup(msslider, {
                    width: 1500,
                    height: 500,
                    autoHeight: true,
                    layout: 'fullwidth',
                    view: 'fadeBasic',
                    space: 0,
                    autoplay: true,
                    loop: loop
                });
            }
            if (total > 1) {
                slider.control('bullets');
            }
            slider.control('slideinfo', {
                insertTo: ".ms-inner-controls-cont",
                autohide: false,
                align: 'bottom',
                size: 150
            });
        }
    });
    loadOnlyUserView.push(function () {
        //Remove By By for Slidernews
        //       if($(".news-slider").length){
        //        $(".news-slider").each(function() {
        //            var hlslider = $(this),
        //                msslider = $(this).find(".master-slider"),
        //                items = $(this).find(".ms-slide"),
        //                total = items.length,
        //                slider = new MasterSlider();

        //            slider.setup(msslider , {
        //                width:366,
        //                height:175,
        //                view:'fade',
        //                layout:'fillwidth',
        //                space:0,
        //                autoplay:true,
        //                loop:(total > 2),
        //                speed:10
        //            });
        //            if(total > 1) {
        //                slider.control('bullets');
        //            }
        //            slider.control('slideinfo',{insertTo:".ms-container" , align:'bottom'});
        //        });
        //    }
    });
    loadOnlyUserView.push(function () {
        if ($("#card-slider").length) {
            $("#card-slider").each(function () {
                var hlslider = $(this),
                    msslider = $(this).find(".master-slider"),
                    items = $(this).find(".ms-slide"),
                    total = items.length,
                    slider = new MasterSlider();

                slider.setup(msslider, {
                    width: 428,
                    height: 270,
                    view: "fade",
                    mouse: false,
                    loop: (total > 2)
                });
                slider.control('slideinfo', {
                    insertTo: '.card-slider-info'
                });
                slider.control('thumblist', {
                    autohide: false,
                    insertTo: '.card-slider-thumb'
                });
            });
        }
    });
    loadOnlyUserView.push(function () {
        $("#recommend-video").each(function () {
            var hlslider = $(this),
                msslider = $(this).find(".master-slider"),
                items = $(this).find(".ms-slide"),
                total = items.length,
                slider = new MasterSlider();

            slider.setup(msslider, {
                width: 1000,
                height: 565,
                space: 1,
                //layout: 'fullwidth',
                loop: true,
                preload: 0,
                instantStartLayers: true,
                swipe: false,
                mouse: false,
                view: "mask"
            });
        });
    });
    loadOnlyUserView.push(function () {
        if ($(".carousel-slider").length) {
            $(".carousel-slider").each(function () {
                var hlslider = $(this),
                    msslider = $(this).find(".master-slider"),
                    items = $(this).find(".ms-slide"),
                    total = items.length,
                    slider = new MasterSlider();

                slider.setup(msslider, {
                    loop: true,
                    width: 1140,
                    height: 500,
                    speed: 20,
                    view: 'fadeBasic',
                    preload: 0,
                    autoplay: true,
                    space: 0
                });
                if (total > 1) {
                    slider.control('arrows');
                    slider.control('bullets', {
                        autohide: false,
                        align: "bottom"
                    });
                }
                if(items.find(".ms-info").length){
                    slider.control('slideinfo',{
                        insertTo:'.ms-inner-controls-cont'
                    });
                }
            });
        }
    });
    loadOnlyUserView.push(function () {
        $(".tabs-group").each(function () {
            var tabContent = $(this).find(".tab-content"),
                tabList = $(this).find(".tabs-list"),
                tabTrigger = $(tabList).find(".tab-trigger");
            tabTrigger.click(function (e) {
                e.preventDefault();
                $(this).parent().addClass("current");
                $(this).parent().siblings().removeClass("current");
                var tab = $(this).attr("href");
                $(tab).stop(true).fadeIn(800).addClass("tab-content-current");
                $(tabContent).not(tab).css("display", "none").removeClass("tab-content-current");
            });
        });
    });
    loadOnlyUserView.push(function () {
        if ($('.select-tabs-group').length) {
            $(".select-tabs-group").each(function () {
                var select_tabs = $(this).find(".select-tabs"),
                    select_tabContent = $(this).find(".select-tab-content");
                select_tabs.on('change', function (e) {
                    var valId = $(this).val();
                    $(valId).stop(true).fadeIn(800).addClass("active");
                    $(select_tabContent).not(valId).css("display", "none").removeClass("active");
                });
            });
        }
    });
    loadOnlyUserView.push(function () {
       // $(".accordion").each(function () {
         //   var title = $(this).find(">.accordion-title"),
          //      content = $(this).find(">.accordion-content");
//
          //  content.hide();
//
          //  if (title.hasClass('active')) {
          //      $(this).parent().find(content).slideDown(300);
          //  }
//
          //  title.click(function () {
           //     if ($(this).hasClass('active')) {
           //         $(this).removeClass('active').parent().find(content).slideUp(300);
           //     } else {
           //         $(this).toggleClass('active').parent().find(content).slideDown(300);
           //     }
           //     return false;
           // });
        //});
		$(".accordion").each(function () {
    
			if($(this).hasClass("ck-func")){
				return;
			}
			
			$(this).addClass("ck-func");
			
			var title = $(this).find(">.accordion-title"),
				content = $(this).find(">.accordion-content");

			content.hide();
			
			if (title.hasClass('active')) {
				$(this).parent().find(content).slideDown(300);
			}

			title.click(function () {
				if ($(this).hasClass('active')) {
					$(this).removeClass('active').parent().find(content).slideUp(300);
				} else {
					$(this).toggleClass('active').parent().find(content).slideDown(300);
				}
				return false;
			});
		});

    });
    loadOnlyUserView.push(function () {
        if ($("#section-filters").length) {
            var _loc = $("#section-filters");
            var filterBtn = _loc.find(".filter-btn"),
                filtersContainer = _loc.find(".sc-filters-container"),
                searchFilters = _loc.find(".search-filters");
            filterBtn.on('click', function (e) {
                e.preventDefault();

                filtersContainer.toggleClass("filter-open");

                if (filtersContainer.hasClass("filter-open")) {
                    window.setTimeout(function () {
                        searchFilters.css("position", "relative");
                    }, 600);
                } else {
                    searchFilters.css("position", "absolute");
                }
            });
        }
    });
    loadOnlyUserView.push(function () {
        if ($("#search-filters").length) {
            $('.popup-search-filters').magnificPopup({
                type: 'inline',
                preloader: false,
                mainClass: 'mfp-fade',
                disableOn: function () {
                    if ($(window).width() < 768) {
                        return true;
                    }
                    return false;
                }
            });

            var _desktop = $("#search-filters"),
                _mobile = $("#search-filters-mobile"),
                _content = _desktop.find(">.search-filter-container"),
                _magnificPopup = $.magnificPopup.instance;

            function handleMQL(mql) {
                if (mql.matches) {
                    _content.appendTo(_mobile);
                } else {
                    _magnificPopup.close();
                    _content.appendTo(_desktop);
                }
            }
            var mql = window.matchMedia("(max-width: 768px)");
            mql.addListener(handleMQL);
            handleMQL(mql);
        }
    });
    // Control Action  //
    /*loadOnlyUserView.push(function () {
    $(".icw-actionControl").click(function (e) {
    if ($($(this).data('actionRef')).length) {
    e.preventDefault();
    var _ref = $(this).data('actionRef'),
    _act = (/(\w+)\[(.+)\]/ig).exec($(this).data('actionClass'));
    eval('$(_ref).' + _act[1] + 'Class("' + _act[2] + '")');
    }
    })
    });*/
    // Form //
    loadOnlyUserView.push(function () {
        $(".select").each(function () {
            var config = {
                '.chosen-select': {
                    width: "100%",
                    //disable_search_threshold: 10
                    disable_search: true
                }
            }
            for (var selector in config) {
                $(selector).chosen(config[selector]);
            }
            if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
                $(selector).chosen("destroy");
            }
        });
    });
    //    loadOnlyUserView.push(function () {
    //        $('[placeholder]').focus(function () {
    //            var input = $(this);
    //            if (input.val() == input.attr('placeholder')) {
    //                input.val('');
    //                input.removeClass('placeholder');
    //            }
    //        }).blur(function () {
    //            var input = $(this);
    //            if (input.val() == '' || input.val() == input.attr('placeholder')) {
    //                input.addClass('placeholder');
    //                input.val(input.attr('placeholder'));
    //            }
    //        }).blur();
    //    });
    loadOnlyUserView.push(function () {
        $('.icw-form input[type="text"], .icw-form textarea').focusin(function () {
            $(this).parents('.icw-input').addClass('filled');
        });
        $('.icw-form input[type="text"], .icw-form textarea').focusout(function () {
            if (!$(this).val()) {
                $(this).parents('.icw-input').removeClass('filled');
            } else {}
        });
    });
    loadOnlyUserView.push(function () {
        // Datepicker : file include jquery-ui.min.js
        !$("body").hasClass("device-mobile") && $(".px-datepicker-device").attr("type", "text").addClass("px-datepicker").removeClass("px-datepicker-device");

        if ($(".px-datepicker-device").length) {
            $(".px-datepicker-device").parents('.datepicker').addClass('datepicker-device');
        }
        if ($(".px-datepicker").length) {
            var inputDatepicker = $(".px-datepicker");
            inputDatepicker.datepicker({
                dateFormat: "dd/mm/yy",
                changeMonth: true,
                changeYear: true,
                showOn: "both",
                buttonText: ""
            });

            $(window).resize(function () {
                inputDatepicker.datepicker('hide');
                inputDatepicker.blur();
            });
        }

    });

    loadOnlyUserView.push(function () {
        //Remove By By for Slidernews
        if ($("#News-Slider22 #master-slider_News").length) {
            $("#News-Slider22").each(function () {
                var hlslider = $(this),
                    msslider = $(this).find("#master-slider_News"),
                    items = $(this).find(".ms-slide"),
                    total = items.length,
                    slider = new MasterSlider();

                slider.setup(msslider, {
                    width: 366,
                    height: 175,
                    view: 'fade',
                    layout: 'fillwidth',
                    space: 0,
                    autoplay: true,
                    loop: (total > 2),
                    speed: 10
                });
                if (total > 1) {
                    slider.control('bullets');
                }
                slider.control('slideinfo', {
                    insertTo: ".ms-container",
                    align: 'bottom'
                });
            });
        }
    });

    loadOnlyUserView.push(function () {
        if ($('.open-popup-content').length) {
            $('.open-popup-content').magnificPopup({
                type: 'inline',
                midClick: true,
                alignTop: true,
                mainClass: 'icw-popup-content',
                closeOnBgClick: false
            });
        }

        if ($('.open-popup-share').length) {
            $('.open-popup-share').magnificPopup({
                type: 'inline',
                midClick: true,
                alignTop: true,
                mainClass: 'icw-popup-function',
                closeOnBgClick: false,
                fixedContentPos: true
            });
        }
        //        // Remove By dev
        //        if ($('.open-popup-search').length) {
        //            $('.open-popup-search').magnificPopup({
        //                type: 'inline',
        //                midClick: true,
        //                alignTop: true,
        //                mainClass: 'icw-popup-function',
        //                closeOnBgClick: false,
        //                fixedContentPos: true
        //                //focus: '#search'
        //            });
        //        }
        //        // End Remove
        if ($('.open-popup-iframe').length) {
            $('.open-popup-iframe').magnificPopup({
                //disableOn: 767,
                type: 'iframe',
                mainClass: 'mfp-fade',
                preloader: false,
                fixedContentPos: true
            });
        }

        let htmlTooltip = `<a class="open-popup-search" href="/th/search/">
                                <i class="ic ic-search"></i>
                            </a>
                            <div class="tooltip-search">
                                <img src="https://www.kasikornbank.com/SiteCollectionDocuments/header-footer/img/icon/new.png" width="26">
                                หาอะไรไม่เจอใช้ Search ได้เลย
                            </div>`

        $(".tool.tool-search").html(htmlTooltip);

        if (!checkSesstionTooltip) {
            timerTooltip = setInterval(countSessionTimer, (5 * 1000));
            document.cookie = "openTooltip=ture; path=/";
            countSessionTimer()
        }
    
        $(".tooltip-search").on("click", function () {
            $(this).hide();
            stopTimer();
        })
    });
    loadOnlyUserView.push(function () {
        if ($('.condition-detail').length) {
            $(".condition-detail").each(function () {
                var c_box = $(this).find('.condition-box'),
                    c_link = $(this).find('.condition-link');

                c_link.click(function (e) {
                    e.preventDefault();
                    c_box.slideToggle();
                    $(this).toggleClass('active');
                });
            });
        }
    });

    // owlCarousel for Product Detail //
    loadOnlyUserView.push(function () {
        if ($(".items-slider").length) {

            function buildSlideOwl() {
                //console.log('buildSlideOwl');
                $('.items-slider').each(function () {
                    var owl = $(this).find('.owl-carousel'),
                        items = $(this).find('.item'),
                        max = items.length;
                    owl.owlCarousel({
                        navigation: true,
                        navigationText: ["<i class='left'></i>", "<i class='right'></i>"],
                        items: 1,
                        itemsMobile: [991, 1],
                        pagination: (max > 1)
                    });
                });
            }

            function destroySlideOwl() {
                //console.log('destroySlideOwl');
                $('.items-slider').each(function () {
                    var owlCarousel = $(this).find('.owl-carousel');
                    if (typeof owlCarousel.data('owlCarousel') != 'undefined') {
                        owlCarousel.data('owlCarousel').destroy();
                    }
                });
            }

            enquire.register("screen and (max-width: 991px)", {
                match: function () {
                    buildSlideOwl();
                },
                unmatch: function () {
                    destroySlideOwl();
                }
            }, true);

        }
    });



    loadOnlyUserView.push(function () {
        if ($(".solution-slider").length) {

            $('.solution-slider').each(function () {

                var slick = $(this).find('.slick-slider'),
                    items = $(this).find('.item'),
                    item_wrap = $(this).find('.item-wrap'),
                    max = items.length,
                    heading = $(this).find('.sc-headline');

                heading.prependTo(item_wrap);

                slick.slick({
                    dots: true,
                    arrows: false,
                    //infinite: true,
                    speed: 500,
                    fade: true,
                    cssEase: 'linear',
                    pauseOnFocus: false,
                    pauseOnHover: false,
                    //autoplay: true,
                    autoplaySpeed: 6000,
                    adaptiveHeight: true
                });

                if (!$("html").hasClass("touch")) {
                    slick.slick('slickPause')
                    $('.solution-slider').on("mouseenter", function (e) {
                        if (max > 1) {
                            slick.slick('slickPlay');
                        }
                    });
                } else {
                    if (max > 1) {
                        slick.slick('slickPlay');
                    }
                }

            });

        }
    });
    loadOnlyUserView.push(function () {
        if ($(".thumbnails-slider").length) {

            $('.thumbnails-slider').each(function () {
                var owl = $(this).find('.owl-carousel'),
                    items = $(this).find('.item'),
                    max = items.length;
                owl.owlCarousel({
                    items: 4,
                    itemsDesktopSmall: [991, 3],
                    itemsTablet: [767, 2],
                    itemsMobile: [480, 1],
                    pagination: (max > 1),
                    navigation: true,
                    navigationText: false,
                    scrollPerPage: true
                });
            });

        }
    });
    loadOnlyUserView.push(function () {
        if ($(".showmore-box").length) {
            $('.showmore-box').each(function () {
                var trHide = $(this).find(".hide"),
                    actionShowmore = $(this).find(".showmore-action"),
                    btnShowmore = $(this).find(".btn-showmore");

                btnShowmore.click(function (e) {
                    e.preventDefault();
                    trHide.addClass("show");
                    actionShowmore.hide();
                });

            });
        }
    });
    loadOnlyUserView.push(function () {
        if ($(".icw-alert").length) {
            $('.icw-alert').each(function () {
                var icwAlert = $(this),
                    icwClose = icwAlert.find('.icw-close');
                icwClose.click(function (e) {
                    e.preventDefault();
                    icwAlert.fadeOut(300);
                });
            });
        }
    });
    /* Fn Sitemap */
    loadOnlyUserView.push(function () {
        $(".kb-sitemap").find("li").each(function () {
            var _loc = $(this);

            if (!_loc.find(">ul").length) return true;

            var _ul = $(_loc.find(">ul")[0]),
                _a = $(_loc.find(">a")[0]);
            _ul.hide();
            var _span = $('<span class="collapsed"></span>').appendTo(this);
            _span.click(function () {
                _ul.toggle();
                $(this).toggleClass("expanded");
            });
            if (!_a[0].hasAttribute("href")) {
                _a.click(function (e) {
                    e.preventDefault();
                    _ul.toggle();
                    _span.toggleClass("expanded");
                });
            }
            //
            if (_loc.hasClass("expanded")) _loc.parentsUntil(".kb-sitemap", "li").addClass("expanded");
        });
        $(".kb-sitemap").find("li.expanded").each(function () {
            $(this).find(">.collapsed").addClass("expanded");
            $(this).find(">ul").show();
            $(this).removeClass("expanded");
        });

        function setCookie(key, value, days) {
            var expires = new Date();
            expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
            document.cookie = key + '=' + value + ';expires=' + expires.toUTCString();
        }

        function getCookie(key) {
            var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');
            return keyValue ? keyValue[2] : null;
        }
        if ($(".kb-notify").length) {
            var Check = getCookie("kb-notify");
            if (Check == "1")
                $('.kb-notify').hide();
            else {
                $('.kb-notify').show();
                setCookie("kb-notify", "1", 7);
                $('.kb-notify').each(function () {
                    var kbNotify = $(this),
                        kbClose = kbNotify.find('.icw-close');
                    kbClose.click(function (e) {
                        e.preventDefault();
                        kbNotify.fadeOut(300);
                    });
                });
            }
        }

    });


    //    loadOnlyUserView.push(function () {
    //        /* Fn Tour */
    //        (function () {
    //            var lang = _spPageContextInfo.currentCultureName.substr(0,2).toLowerCase();
    //            if ($(".tour-step").length & $(".tour-step-segment").length && lang == "th") {

    //                // Instance the tour
    //                var tour = new Tour({
    //                    backdrop: true,
    //                    steps: [
    //                                {
    //                                    element: "#tour-step-login",
    //                                    title: "เข้าสู่ระบบ",
    //                                    content: "สะดวกขึ้น กับการเข้าสู่ระบบ K-Cyber, K-Cyber for SME และ K-Corporate Connect ได้จากที่เดียว",
    //                                    backdropContainer: ".header",
    //                                    placement: "auto",
    //                                    backdropPadding: {
    //                                        top: 13,
    //                                        right: 15,
    //                                        bottom: 15,
    //                                        left: 15
    //                                    },
    //                                    template: "<div class='popover tour popover-login'><div class='arrow'></div><div class='btn-close' data-role='end'></div><h3 class='popover-title'></h3><div class='popover-content'></div><div class='popover-navigation'><button class='btn btn-default' data-role='next'>ถัดไป</button></div></div>"
    //                                },
    //                                {
    //                                    element: "#tour-step-segment",
    //                                    title: "กลุ่มลูกค้า",
    //                                    content: "เข้าถึงข้อมูลง่ายขึ้น ด้วยการจัดหมวดหมู่ข้อมูลให้เหมาะกับแต่ละกลุ่มลูกค้า",
    //                                    backdropContainer: ".navtop",
    //                                    placement: "auto",
    //                                    backdropPadding: {
    //                                        top: 0,
    //                                        right: 20,
    //                                        bottom: 0,
    //                                        left: 20
    //                                    },
    //                                    template: "<div class='popover tour popover-segment'><div class='arrow'></div><div class='btn-close' data-role='end'></div><h3 class='popover-title'></h3><div class='popover-content'></div><div class='popover-navigation'><button class='btn btn-default' data-role='next'>ถัดไป</button></div></div>"
    //                                },
    //                                {
    //                                    element: "#tour-step-shortcut",
    //                                    title: "ช่องทางลัด",
    //                                    content: "เร็วขึ้น กับช่องทางลัด ไปหน้าที่ใช้บ่อยได้อย่างรวดเร็ว",
    //                                    backdropContainer: ".main-container-home",
    //                                    placement: "left",
    //                                    backdropPadding: 15,
    //                                    template: "<div class='popover tour popover-shortcut'><div class='arrow'></div><div class='btn-close' data-role='end'></div><h3 class='popover-title'></h3><div class='popover-content'></div><div class='popover-navigation'><button class='btn btn-default' data-role='end'>เริ่มต้นใช้งาน</button></div></div>"
    //                                }
    //                            ],
    //                    onEnd: function (tour) {
    //                        //location.reload();
    //                        $(window).scrollTop(0);
    //                    }
    //                });

    //                function handleMQL(mql) {
    //                    if (mql.matches) {

    //                        tour.pause();

    //                    } else {

    //                        // Initialize the tour
    //                        tour.init();

    //                        // Start the tour
    //                        tour.start();

    //                    }
    //                }

    //                var mql = window.matchMedia("(max-width: 1024px)");
    //                mql.addListener(handleMQL);
    //                handleMQL(mql);

    //            }

    //            if ($(".tour-step").length & $(".tour-step-segment").length  && lang == "en") {

    //                // Instance the tour
    //                var tourEN = new Tour({
    //                    backdrop: true,
    //                    steps: [
    //                                {
    //                                    element: "#tour-step-login",
    //                                    title: "Log-in",
    //                                    content: "Log in to K-Cyber, K-Cyber for SME and K-Corporate Connect from one place",
    //                                    backdropContainer: ".header",
    //                                    placement: "auto",
    //                                    backdropPadding: {
    //                                        top: 13,
    //                                        right: 15,
    //                                        bottom: 15,
    //                                        left: 15
    //                                    },
    //                                    template: "<div class='popover tour popover-login'><div class='arrow'></div><div class='btn-close' data-role='end'></div><h3 class='popover-title'></h3><div class='popover-content'></div><div class='popover-navigation'><button class='btn btn-default' data-role='next'>Next</button></div></div>"
    //                                },
    //                                {
    //                                    element: "#tour-step-segment",
    //                                    title: "Customer Segment",
    //                                    content: "Useful information to suit the customer's needs",
    //                                    backdropContainer: ".navtop",
    //                                    placement: "auto",
    //                                    backdropPadding: {
    //                                        top: 0,
    //                                        right: 20,
    //                                        bottom: 0,
    //                                        left: 20
    //                                    },
    //                                    template: "<div class='popover tour popover-segment'><div class='arrow'></div><div class='btn-close' data-role='end'></div><h3 class='popover-title'></h3><div class='popover-content'></div><div class='popover-navigation'><button class='btn btn-default' data-role='next'>Next</button></div></div>"
    //                                },
    //                                {
    //                                    element: "#tour-step-shortcut",
    //                                    title: "Shortcuts",
    //                                    content: "Faster access to frequently used pages.",
    //                                    backdropContainer: ".main-container-home",
    //                                    placement: "left",
    //                                    backdropPadding: 15,
    //                                    template: "<div class='popover tour popover-shortcut'><div class='arrow'></div><div class='btn-close' data-role='end'></div><h3 class='popover-title'></h3><div class='popover-content'></div><div class='popover-navigation'><button class='btn btn-default' data-role='end'>Done</button></div></div>"
    //                                }
    //                            ],
    //                    onEnd: function (tour) {
    //                        //location.reload();
    //                        $(window).scrollTop(0);
    //                    }
    //                });

    //                function handleMQL(mql) {
    //					try{
    //                        if (mql.matches) {

    //                            tourEN.pause();

    //                        } else {
    //					
    //                            // Initialize the tour
    //                            tourEN.init();

    //                            // Start the tour
    //                            tourEN.start();
    //						
    //                        }
    //					}catch(err)
    //					{
    //						
    //						
    //					}
    //					
    //					 
    //                }

    //                var mql = window.matchMedia("(max-width: 1024px)");
    //                mql.addListener(handleMQL);
    //                handleMQL(mql);

    //            }

    //        })();



    //    });
    _spBodyOnLoadFunctions.push(function () {
        // ICWeb component should run when DOM ready!
        // _spBodyOnLoadFunctions runs before $(document).ready
        $(function () {
            // Global component
            [].forEach.call(loadEveryViews, function (e, i, a) {
                e();
            });
            // Design component
            if (!PageUtil_isInEditMode()) {
                [].forEach.call(loadOnlyUserView, function (e, i, a) {
                    e();
                });
            }
        });
    });
})(window.jQuery);

$(document).ready(function () {
    //$(".submenu-bottom").find(".affiliate-websites").append('<li class="noindex"><a href="/MADHUB" target="_blank"><img src="/SiteCollectionDocuments/img/logoMADtran-01.png" alt="MADHUB" class="img"></a></li>');


    if (GetCurrentLang() == "en") $(".visible-w767 span.shortcut-title").html("Share");
    else $(".visible-w767 span.shortcut-title").html("แชร์");

    try {
        if (!$('.localnav.slicknav .h2.heading a').text().endsWith("        "))
            $('.localnav.slicknav .h2.heading a').css("visibility", "visible");
    } catch (e) {

    }

});


// Disclaimer Policy //
function generateDisclaimerLinker(gl){
    var _refLink = "/th/disclaimer/Pages/disclaimers.aspx?redirect=",
        Base64={_keyStr:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",encode:function(e){var t="";var n,r,i,s,o,u,a;var f=0;e=Base64._utf8_encode(e);while(f<e.length){n=e.charCodeAt(f++);r=e.charCodeAt(f++);i=e.charCodeAt(f++);s=n>>2;o=(n&3)<<4|r>>4;u=(r&15)<<2|i>>6;a=i&63;if(isNaN(r)){u=a=64}else if(isNaN(i)){a=64}t=t+this._keyStr.charAt(s)+this._keyStr.charAt(o)+this._keyStr.charAt(u)+this._keyStr.charAt(a)}return t},decode:function(e){var t="";var n,r,i;var s,o,u,a;var f=0;e=e.replace(/\\+\\+[++^A-Za-z0-9+/=]/g,"");while(f<e.length){s=this._keyStr.indexOf(e.charAt(f++));o=this._keyStr.indexOf(e.charAt(f++));u=this._keyStr.indexOf(e.charAt(f++));a=this._keyStr.indexOf(e.charAt(f++));n=s<<2|o>>4;r=(o&15)<<4|u>>2;i=(u&3)<<6|a;t=t+String.fromCharCode(n);if(u!=64){t=t+String.fromCharCode(r)}if(a!=64){t=t+String.fromCharCode(i)}}t=Base64._utf8_decode(t);return t},_utf8_encode:function(e){e=e.replace(/\r\n/g,"n");var t="";for(var n=0;n<e.length;n++){var r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r)}else if(r>127&&r<2048){t+=String.fromCharCode(r>>6|192);t+=String.fromCharCode(r&63|128)}else{t+=String.fromCharCode(r>>12|224);t+=String.fromCharCode(r>>6&63|128);t+=String.fromCharCode(r&63|128)}}return t},_utf8_decode:function(e){var t="";var n=0;var r=c1=c2=0;while(n<e.length){r=e.charCodeAt(n);if(r<128){t+=String.fromCharCode(r);n++}else if(r>191&&r<224){c2=e.charCodeAt(n+1);t+=String.fromCharCode((r&31)<<6|c2&63);n+=2}else{c2=e.charCodeAt(n+1);c3=e.charCodeAt(n+2);t+=String.fromCharCode((r&15)<<12|(c2&63)<<6|c3&63);n+=3}}return t}}
    return _refLink+encodeURIComponent(Base64.encode(gl));
}
$(function(){
    // Set External Link Redirect Path to Disclaimer Page
    $(".px-disclaimerLink").each(function(){
        this.href = generateDisclaimerLinker($(this).attr('href'));
    });
})
