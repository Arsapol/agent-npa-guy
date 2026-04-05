var htmlPage = $('html');

/* Panel */
$(function(){    
    $(".panel-ctrl").click(function(){
        var dataPanel = $(this).data('panel-ctrl');
        htmlPage.addClass("panel-enabled");
        $('*[data-panel='+ dataPanel +']').addClass("active");
    });
    
    $(".panel-close").click(function(){
        htmlPage.removeClass("panel-enabled");
        $(this).parents(".panel").removeClass("active");
    });
});

/* Hamburger Menu Sub */
//$('.panel-body .menu-group').each(function(){
//    var dir = $(this).find('.item');
//    dir.each(function(){
//        var dirTitle = $(this).find('.item-title'),
//            dirLinks = $(this).find('.item-list'),
//            dirSiblings = $('.panel-body .menu-group').find('.item').not($(this)),
//            dirSiblingsTitle = dirSiblings.find('.item-title'),
//            dirSiblingsLinks = dirSiblings.find('.item-list');
//
//        dirTitle.click(function(){
//            dirTitle.parent('.item').toggleClass('active');
//            dirLinks.slideToggle(300);
//            dirSiblings.removeClass('active');
//            dirSiblingsLinks.slideUp(300);
//        });
//    });
//});

/* Device Mobile */
$(function () {
    var _isTouch = 'ontouchstart' in document.documentElement; $(function () { var _ua = (navigator.userAgent || navigator.vendor || window.opera), _device = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i; $("body").addClass((_isTouch) ? "isTouch" : "no-touch"); if (_device.test(_ua)) { $("body").addClass("device-mobile"); } else { $('a[href^="tel:"]').removeAttr("href"); } });
});


/* Header */
$(function () {
    if(!$("html").hasClass("ie8")){
        window.addEventListener('scroll', function (e) {
            var distanceY = window.pageYOffset || document.documentElement.scrollTop,
                shrinkOn = 100,
                header = $(".header");
            if (distanceY > shrinkOn) {
                header.addClass("smaller");
            } else {
                if (header.hasClass("smaller")) {
                    header.removeClass("smaller")
                }
            }
        });
    }
});

/* Sign Out */
$(function(){ 
    if($(".sc-sign-out").length){
        $(".header .right-menu .user").click(function(){
            $(".sc-sign-out").slideToggle(500);
        });
    }
});

/* Highlight */
$(function(){ 
    if($(".sc-highlight").length){
        var swiper = new Swiper('.sc-highlight .swiper-container', {
            pagination: {
            el: '.swiper-pagination',
            clickable: true,
            },
        });
    }
 });

if($(".sc-highlight").length){
    var slides = document.querySelectorAll('.sc-highlight .swiper-slide');
    var pagination = document.querySelector('.swiper-pagination');

    if (slides.length < 2) {
       pagination.style.display = 'none';
    }
}

/* Business Online */
$(function(){
    if($(".business-online-slider").length){
        var swiper_business_online = new Swiper('.swiper-container.business-online-slider', {
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            init: false
        });
        
        enquire.register("screen and (max-width: 991px)", {
            match : function() {
                swiper_business_online.init();
            },
            unmatch : function() {
                swiper_business_online.destroy();
            }
        }, true);
    }
});

/* Dot */
$(function(){
    var txt = $(".dot"),
        txtDestroy = $(".destroy");
    if(txt.length){
        txt.dotdotdot({
            ellipsis: '...',
            wrap: 'word',
            fallbackToLetter: true,
            watch: true,
            //after: '.ic'
        });
    }
    if(txtDestroy.length){
        txtDestroy.trigger("destroy");
    }
});

/* Upload File */
$(function(){
    // Browser supports HTML5 multiple file?
    var multipleSupport = typeof $('<input/>')[0].multiple !== 'undefined',
        isIE = /msie/i.test( navigator.userAgent );

    $.fn.customFile = function() {

        return this.each(function() {

            var $file = $(this).addClass('custom-file-upload-hidden'), // the original file input
                $wrap = $('<div class="file-upload-wrapper">'),
                $input = $('<input type="text" class="file-upload-input" placeholder="อัพโหลดรูปภาพโปรไฟล์ส่วนตัว..." readonly />'),
                // Button that will be used in non-IE browsers
                $button = $('<div class="file-upload-action"><button type="button" class="btn outline-white file-upload-button">เลือกไฟล์</button></div>'),
                // Hack for IE
                $label = $('<div class="file-upload-action"><label class="btn outline-white file-upload-button" for="'+ $file[0].id +'">เลือกไฟล์</label></div>');

            // Hide by shifting to the left so we
            // can still trigger events
            $file.css({
                position: 'absolute',
                left: '-9999px'
            });

            $wrap.insertAfter( $file )
                .append( $file, $input, ( isIE ? $label : $button ) );

            // Prevent focus
            $file.attr('tabIndex', -1);
            $button.attr('tabIndex', -1);

            // Open dialog
            $button.click(function () {
                $file.focus().click(); 
            });

            $input.click(function () {
                $file.focus().click();
            });

            $file.change(function() {

                var files = [], fileArr, filename;

                // If multiple is supported then extract
                // all filenames from the file array
                if ( multipleSupport ) {
                    fileArr = $file[0].files;
                    for ( var i = 0, len = fileArr.length; i < len; i++ ) {
                        files.push( fileArr[i].name );
                    }
                    filename = files.join(', ');

                // If not supported then just take the value
                // and remove the path to just show the filename
                } else {
                    filename = $file.val().split('\\').pop();
                }

                $input.val( filename ) // Set the value
                    .attr('title', filename) // Show filename in title tootlip
                    .focus(); // Regain focus

                $input.closest('.input').addClass('filled');
            });

            $input.on({
                blur: function() { $file.trigger('blur'); },
                keydown: function( e ) {
                    if ( e.which === 13 ) { // Enter
                        if ( !isIE ) { $file.trigger('click'); }
                    } else if ( e.which === 8 || e.which === 46 ) { // Backspace & Del
                        // On some browsers the value is read-only
                        // with this trick we remove the old input and add
                        // a clean clone with all the original events attached
                        $file.replaceWith( $file = $file.clone( true ) );
                        $file.trigger('change');
                        $input.val('');
                    } else if ( e.which === 9 ) { // TAB
                        return;
                    } else { // All other keys
                        return false;
                    }
                }
            });

        });

    };

    // Old browser fallback
    if ( !multipleSupport ) {
        $( document ).on('change', 'input.customfile', function() {

      var $this = $(this),
          // Create a unique ID so we
          // can attach the label to the input
          uniqId = 'customfile_'+ (new Date()).getTime(),
          $wrap = $this.parent(),

          // Filter empty input
          $inputs = $wrap.siblings().find('.file-upload-input')
            .filter(function(){ return !this.value }),

          $file = $('<input type="file" id="'+ uniqId +'" name="'+ $this.attr('name') +'"/>');

      // 1ms timeout so it runs after all other events
      // that modify the value have triggered
      setTimeout(function() {
        // Add a new input
        if ( $this.val() ) {
          // Check for empty fields to prevent
          // creating new inputs when changing files
          if ( !$inputs.length ) {
            $wrap.after( $file );
            $file.customFile();
          }
        // Remove and reorganize inputs
        } else {
          $inputs.parent().remove();
          // Move the input so it's always last on the list
          $wrap.appendTo( $wrap.parent() );
          $wrap.find('input').focus();
        }
      }, 1);

    });
    }

    $('input[type=file]').customFile();
});

/* Popup Modal */
$(function () {
	$('.popup-content').magnificPopup({
		type: 'inline',
		preloader: false,
        mainClass: 'popup-content-style',
		focus: '#username',
		modal: true
	});
	$(document).on('click', '.popup-modal-dismiss', function (e) {
		e.preventDefault();
		$.magnificPopup.close();
	});
});

$(function () {
	$('.popup-content-bg').magnificPopup({
		type: 'inline',
		preloader: false,
        mainClass: 'popup-content-style hv-bg',
		focus: '#username',
		modal: true
	});
	$(document).on('click', '.popup-modal-dismiss', function (e) {
		e.preventDefault();
		$.magnificPopup.close();
	});
});

/* Seminar Slider */
$(function(){ 
    if($(".seminar-slider").length){
        var swiper = new Swiper('.seminar-slider .swiper-container', {
            slidesPerView: 'auto',
            loop: true,
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
        });
    }
});

/* Popup Bottom Bar */
if($("#popup-bottom-bar").length){
    var lastScrollTop = 0;
    $(window).scroll(function(event){
      var st = $(this).scrollTop();
      if (st > lastScrollTop){
          // downscroll code
           if($(document).scrollTop() > $('.sc-what-madhub').offset().top){ $('a[href="#popup-bottom-bar"]').click(); $('.bottom-bar').hide(); }
           //console.log('down: '+$(document).scrollTop());

      } else {
         // upscroll code
       //console.log('top: '+$(document).scrollTop());
      }
      lastScrollTop = st;
    });
}

$(function(){
    if($("#popup-bottom-bar").length){
        $('#popup-bottom-bar .popup-modal-dismiss').click(function(){
            $('a[href="#popup-bottom-bar"]').remove();
        });
    }
});

/* Social Share */
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
        title: document.title
    };
    var a = addQS('https://www.facebook.com/sharer.php', g);
    window.open(a, 'sharer', 'toolbar=0,status=0,width=626,height=436');
    return false
}

function fbIMGShare(img) {
    var g = {
        u: document.URL + "?fbimg=" + img,
        title: document.title
    };
    var a = addQS('https://www.facebook.com/sharer.php', g);
    window.open(a, 'sharer', 'toolbar=0,status=0,width=626,height=436');
    return false
}

function fbURLShare(u,title) {
    var g = {
        u: u,
        title: (title != '' ? title : document.title)
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

function lineMSG() {
    window.location = "line://msg/text/" + encodeURIComponent(document.URL);
}

function lineURLMSG(u) {
    window.location = "line://msg/text/" + encodeURIComponent(u);
}

function linkinShare() {
    var a = 'https://www.linkedin.com/shareArticle?mini=true&url=' + document.URL + '&title=' + document.title;
    window.open(a, 'sharer', 'toolbar=0,status=0,width=626,height=436');
}

function linkinURLShare(u) {
    var a = 'https://www.linkedin.com/shareArticle?mini=true&url=' + u;
    window.open(a, 'sharer', 'toolbar=0,status=0,width=626,height=436');
}

/* Form */
$(function(){
    
    // Select
    $(".select").each(function() {
        var selectParent = $(this),
            select = $(this).find(".select2"),
            selectFilter = $(this).find(".select2-filter");
        
        var query = {};
        function markMatch (text, term) {
            var match = text.toUpperCase().indexOf(term.toUpperCase());
            
            var $result = $('<span></span>');

            if (match < 0) {
                return $result.text(text);
            }

            $result.text(text.substring(0, match));

            var $match = $('<span class="select2-rendered__match"></span>');
            $match.text(text.substring(match, match + term.length));

            $result.append($match);

            $result.append(text.substring(match + term.length));

            return $result;
        }
        
        select.select2({
            width: '100%',
            minimumResultsForSearch: -1,
            dropdownParent: selectParent,
            templateResult: function (item) {
                if (item.loading) {
                    return item.text;
                }

                var term = query.term || '';
                var $result = markMatch(item.text, term);

                return $result;
            },
            language: {
                searching: function (params) {
                    query = params;
                    return 'Searching...';
                }
            }
        });
        
        selectFilter.select2({
            width: '100%',
            allowClear: true,
            dropdownParent: selectParent,
            templateResult: function (item) {
                if (item.loading) {
                    return item.text;
                }

                var term = query.term || '';
                var $result = markMatch(item.text, term);

                return $result;
            },
            language: {
                searching: function (params) {
                    query = params;
                    return 'Searching...';
                }
            }
        }).on("select2:unselecting", function(e) {
            $(this).data('state', 'unselected');
        }).on("select2:open", function(e) {
            if ($(this).data('state') === 'unselected') {
                $(this).removeData('state'); 
                var self = $(this);
                self.select2('close');
            } 
        });
        
        select.parent(".select").addClass("select2-parent");
        selectFilter.parent(".select").addClass("select2-parent");
        
        if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
            select.select2("destroy");
            select.parent(".select").removeClass("select2-parent");
        }
    });
    
    // Datepicker : file include jquery-ui-datepicker.min.css, jquery-ui-datepicker.min.js
    !$("html").hasClass("is-device") && $(".px-datepicker-device").attr("type","text").addClass("px-datepicker").removeClass("px-datepicker-device");
    
    if($(".px-datepicker-device").length) {
        $(".px-datepicker-device").parents('.datepicker').addClass('datepicker-device');
    }
    if($(".px-datepicker").length) {
        var inputDatepicker = $(".px-datepicker");
        inputDatepicker.datepicker({ 
            dateFormat: "dd/mm/yy",
            //changeMonth: true,
            //changeYear: true,
            showOn: "both",
            buttonText: "",
            onSelect: function(selected,evnt) {
                console.log("test");
                $(this).parents('.input').addClass('filled');
            }
        });

        $(window).resize(function() {
          inputDatepicker.datepicker('hide');
          inputDatepicker.blur();
        });
    }
    
    // Choice
    $('.choice-other').each(function(){
        var label = $(this).find('.choice-label input[type="checkbox"], .choice-label input[type="radio"]'),
            input = $(this).find('.input > input');

        label.click(function(){
            if( $(this).prop("checked") == true ) {
                input.attr( "disabled", false ).focus();
                input.parent(".input").removeClass("disabled");
            } else {
                input.attr( "disabled", true );
                input.parent(".input").addClass("disabled");
            }
        });
    });
});

/* Add Email to Friend */
$(function(){ 
    if($("#email-to-friend-fields-group").length){
        var masterClone = $('#masterClone').html();
        $('#email-to-friend-fields-group').append( masterClone );
        $("#add-email-to-friend").click(function(e) {
            $('#email-to-friend-fields-group').append( masterClone );
            e.preventDefault();
        });
    }
});

/* Article Tabs */
$(function(){ 
    if($(".container-tabs").length){
        $('ul.tabs-nav li').click(function(){
            var tab_id = $(this).attr('data-tab');
            $('ul.tabs-nav li').removeClass('current');
            $('.tab-content').removeClass('current');
            $(this).addClass('current');
            $("#"+tab_id).addClass('current');
        });
    }
});

/* Fn Video */
$(document).on('click','.js-videoPoster',function(e) {
  e.preventDefault();
  var poster = $(this);
  var wrapper = poster.closest('.js-videoWrapper');
  videoPlay(wrapper);
});

function videoPlay(wrapper) {
  var iframe = wrapper.find('.js-videoIframe');
  var src = iframe.data('src');
  wrapper.addClass('videoWrapperActive');
  iframe.attr('src',src);
}

/* Inner Banner */
$(function(){ 
    if($(".sc-banner").length){
        var swiper = new Swiper('.sc-banner .swiper-container', {
            spaceBetween: 25,
            pagination: {
            el: '.swiper-pagination',
            clickable: true,
            },
        });
    }
 });

if($(".sc-banner").length){
    var slides = document.querySelectorAll('.sc-banner .swiper-slide');
    var pagination = document.querySelector('.swiper-pagination');

    if (slides.length < 2) {
       pagination.style.display = 'none';
    }
}

/* Grid Lists Slider */
$(function(){
    if($(".grid-lists-slider").length){
        var swiper_grid_lists = new Swiper('.swiper-container.grid-lists-slider', {
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            init: false
        });
        
        enquire.register("screen and (max-width: 991px)", {
            match : function() {
                swiper_grid_lists.init();
            },
            unmatch : function() {
                swiper_grid_lists.destroy();
            }
        }, true);
    }
});

/* Course Lists Slider */
$(function(){
    if($(".course-lists-slider").length){
        var swiper_course_lists = new Swiper('.swiper-container.course-lists-slider', {
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            init: false
        });
        
        enquire.register("screen and (max-width: 991px)", {
            match : function() {
                swiper_course_lists.init();
            },
            unmatch : function() {
                swiper_course_lists.destroy();
            }
        }, true);
    }
});

/* Fn matchHeight */
$(function() {
    if($(".matchHeight-group").length){
        $('.matchHeight-group').each(function() {
            $(this).find('.matchHeight').matchHeight({
                byRow: false,
                property: 'height',
                target: null,
                remove: false
            });
        });
    }
});

/* Select With Icon */
/* https://codepen.io/webrajendra/pen/VvjgYY */
$(function() {
    $(".select-wt-icon-01").on("click", ".init", function() {
        $(this).closest(".select-wt-icon-01").children('li:not(.init)').toggle();
    });

    var allOptions = $(".select-wt-icon-01").children('li:not(.init)');
    $(".select-wt-icon-01").on("click", "li:not(.init)", function() {
        allOptions.removeClass('selected');
        $(this).addClass('selected');
        $(".select-wt-icon-01").children('.init').html($(this).html());
        allOptions.toggle();
    });
});

$(function() {
    $(".select-wt-icon-02").on("click", ".init", function() {
        $(this).closest(".select-wt-icon-02").children('li:not(.init)').toggle();
    });

    var allOptions_02 = $(".select-wt-icon-02").children('li:not(.init)');
    $(".select-wt-icon-02").on("click", "li:not(.init)", function() {
        allOptions_02.removeClass('selected');
        $(this).addClass('selected');
        $(".select-wt-icon-02").children('.init').html($(this).html());
        allOptions_02.toggle();
    });
});

/* Tab */
if($(".tab-content-madcourse").length){
    function showTab( elem ){
        $(elem).parents('.tab-group').find('.tab-content-madcourse').removeClass('active');
        $(elem + '.tab-content-madcourse').addClass('active');
    }
    function selectDestroyMobile(Obj){
        if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
            Obj.select2("destroy");
            Obj.parent(".select").removeClass("select2-parent");
        }
    }
    $(function(){
        var tabGroupParent = null;
        var Selec2Options = null;

        $('.tab-group').each(function(){
            var obj = $(this);
            Selec2Options = {
                width: '100%',
                minimumResultsForSearch: -1,
                dropdownParent: obj.find('select.tab-select2').parents('.select')
            };

            var mySelect2 = obj.find('select.tab-select2');
            mySelect2.select2( Selec2Options );
            mySelect2.parents(".select").addClass("select2-parent");
            selectDestroyMobile(mySelect2);
        });

        $('.tab-group .control a').click(function( e ){
            var tabGroupParent = $(this).parents('.tab-group');
            var _id = $(this).attr('href');
            Selec2Options.dropdownParent = tabGroupParent.find('select.tab-select2').parents('.select')

            tabGroupParent.find('.control a').removeClass('active');
            tabGroupParent.find('select option').prop('selected', false).removeAttr('selected');
            $(this).addClass('active');
            showTab( _id );
            tabGroupParent.find('select option[value="'+ _id +'"]').prop('selected', true).attr('selected', true);
            tabGroupParent.find('select.tab-select2').select2('destroy');
            tabGroupParent.find('select.tab-select2').select2( Selec2Options );

            selectDestroyMobile( tabGroupParent.find('select.tab-select2') );

            e.preventDefault();
        });

        $('.tab-group select.tab-select2').change(function(){
            $(this).parents('.tab-group')
            $(this).parents('.tab-group').find('.control a').removeClass('active');
            $('.tab-group .control a[href="'+ $(this).val() +'"]').addClass('active')
            showTab( $(this).val() );
        });
    });
}

/* fullPage.js */
$(function(){
    if($(".fullpage").length) {
        var fullPage = $('#fullpage'),
        aside = $('#aside');
        if(aside.length) {
            function asideMove() {
                1025 < $(window).width() ? ($("#aside").insertBefore("#fullpage")) : ($("#aside").insertAfter('[data-anchor="main"]'));
            }
            asideMove();
            $(window).resize(function() {
                asideMove();
            });
        }
        
        enquire.register("screen and (min-width: 1025px)", {
            match : function() {
                if(fullPage.length) {
                    $('.bg-vdo .vdo').each(function(i,v){
                        $(v).attr('data-keepplaying', ''); 
                        v.play();
                    });
                    fullPage.fullpage({
                        lockAnchors: true,
                        navigation: true,
                        navigationPosition: 'right',
                        showActiveTooltip: false,
                        slidesNavigation: true,
                        //scrollBar: true,
                        scrollOverflow: true,
                        scrollingSpeed: 900,
                        easing: 'easeOutCubic',
                        afterRender: function(){
                            setTimeout(function(){
                                if( window.location.hash == '' ){
                                    $.fn.fullpage.silentMoveTo(1);
                                }
                                if($(".wow").length){
                                    var wow = new WOW();
                                    wow.init();
                                }
                            },10);
                        }
                    });
                    $(document).on('click', '.moveto-qualified-contestant', function(){
                        $.fn.fullpage.moveTo('qualified-contestant');
                    });
                }
            },
            unmatch : function() {
                if(fullPage.length){
                    fullPage.fullpage.destroy('all');
                }
            }
        }, true);
    }
});

/* Form Step */
/* https://codepen.io/atakan/pen/gqbIz */
$(function(){
    if($("#msform").length) {
        //jQuery time
        var current_fs, next_fs, previous_fs; //fieldsets
        var left, opacity, scale; //fieldset properties which we will animate
        var animating; //flag to prevent quick multi-click glitches

        $("#msform .next").click(function(){
            if(animating) return false;
            animating = true;

            current_fs = $(this).parent();
            next_fs = $(this).parent().next();

            //activate next step on progressbar using the index of next_fs
            $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");
            $("#progressbar li").eq($("fieldset").index()).addClass("done");
            $("#progressbar li").eq($("fieldset").index(current_fs)).addClass("done");

            //show the next fieldset
            next_fs.show(); 
            //hide the current fieldset with style
            current_fs.animate({opacity: 0}, {
                step: function(now, mx) {
                    //as the opacity of current_fs reduces to 0 - stored in "now"
                    //1. scale current_fs down to 80%
                    scale = 1 - (1 - now) * 0.2;
                    //2. bring next_fs from the right(50%)
                    left = (now * 50)+"%";
                    //3. increase opacity of next_fs to 1 as it moves in
                    opacity = 1 - now;
                    current_fs.css({
                'transform': 'scale('+scale+')',
                'position': 'absolute'
              });
                    next_fs.css({'left': left, 'opacity': opacity});
                }, 
                duration: 800, 
                complete: function(){
                    current_fs.hide();
                    animating = false;
                }, 
                //this comes from the custom easing plugin
                easing: 'easeInOutBack'
            });
        });
    }
});   

/* Flip Slider */
//$(function(){
//    if($(".flip-slider").length){
//        var swiper_flip_slider = new Swiper('.flip-slider .swiper-container', {
//            slidesPerView: 'auto',
//            loop: false,
//            navigation: {
//                nextEl: '.swiper-button-next',
//                prevEl: '.swiper-button-prev',
//            },
//            init: false
//        });
//        
//        enquire.register("screen and (max-width: 1365px)", {
//            match : function() {
//                swiper_flip_slider.init();
//            },
//            unmatch : function() {
//                swiper_flip_slider.destroy();
//            }
//        }, true);
//    }
//});

$(function(){ 
    if($(".flip-slider").length){
        var swiper = new Swiper('.flip-slider .swiper-container', {
            slidesPerView: 'auto',
            loop: false,
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
        });
    }
});