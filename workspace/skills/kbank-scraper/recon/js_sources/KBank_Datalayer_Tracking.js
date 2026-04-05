$(document).ready(function() {
    //ใช้แทน settimeout 
    var chkReadyState = setInterval(function() {

        //console.log(document.readyState);
        if (document.readyState == "complete") {
            try {
                //code here
                //variable 
                var lang = GetCurrentLang(); //เช็คภาษา
                var cur_url = $(location).attr('pathname').toLowerCase();
                var spl = cur_url.split("/"); //เช็ค subsite โดยเริ่มจาก 0 ตัวอย่าง https://www.kasikornbank.com/th/personal/loan/home-loan/pages/home-equity.aspx ถ้าจะเอา personal ให้ใส่ spl[2]
                var last = cur_url.substring(cur_url.lastIndexOf("/") + 1, cur_url.length);
                var last_low = last.toLowerCase(); //เช็คชื่อเพจนั้นๆ ตัวอย่าง https://www.kasikornbank.com/th/personal/loan/home-loan/pages/home-equity.aspx ค่าที่ได้ = home-equity.aspx
                var page_name = last_low.split("."); // ให้ใช้ page_name[0] ตัวอย่าง https://www.kasikornbank.com/th/personal/loan/home-loan/pages/home-equity.aspx ค่าที่ได้ = home-equity

                ////////////////////////////////////////////////////////////////////----HOME----//////////////////////////////////////////////////////////////////////

                //--------------------Home Nac Menu------------------------------

                $('.shortcutnav > .shortcut-bottom > li > a').addClass("shortcut_nav");
                $('.tool-login > .box-login > .noindex > a').addClass("nav_header");
                $('.localnav-wrap > .pull-left > li > a').addClass("link_moveScroll");
                $('.localnav-wrap > .pull-right > li > a').addClass("register");

                $('.tbcell > .list-inline > .noindex > a[href*="/th/personal"]').addClass("personal_nav_header");
                $('.tbcell > .list-inline > .noindex > a[href*="/th/business/sme"]').addClass("sme_nav_header");
                $('.tbcell > .list-inline > .noindex > a[href*="/th/business"]').addClass("business-nav-header");
                $('.tbcell > .list-inline > .noindex > a[href*="/th/business/sme"]').removeClass("business-nav-header");
                $('.tbcell > .list-inline > .noindex > a[href*="/th/International-Business"]').addClass("international-business-nav-header");
                $('.tbcell > .list-inline > .noindex > a[href*="/th/ir"]').addClass("investor-nav-header");
		
                //$('.tbcell > .list-inline > .noindex > a[href*="/th/about"]').addClass("nav_header");
				//$('.tbcell > .list-inline > .noindex > a[href*="/th/contact/Pages/contact.aspx"]').addClass("nav_header");
				
				
                

                $('.navfooter > .container .list-group > .noindex > a[href*="/th/personal"]').addClass("personal_nav_footer");
                $('.navfooter > .container .list-group > .noindex > a[href*="/TH/Business/SME"]').addClass("sme_nav_footer");
                $('.navfooter > .container .list-group > .noindex > a[href*="/TH/Business"]').addClass("business-nav-footer");
                $('.navfooter > .container .list-group > .noindex > a[href*="/TH/Business/SME"]').removeClass("business-nav-footer");
                $('.navfooter > .container .list-group > .noindex > a[href*="/th/International-Business"]').addClass("international-business-nav-footer");
                $('.navfooter > .container .list-group > .noindex > a[href*="/th/IR"]').addClass("investor-nav-footer");

                $('.tbcell > .list-inline > .noindex > a[href*="/en/personal"]').addClass("personal_nav_header");
                $('.tbcell > .list-inline > .noindex > a[href*="/en/business/sme"]').addClass("sme_nav_header");

                $('.tbcell > .list-inline > .noindex > a[href*="/en/business"]').addClass("business-nav-header");
                $('.tbcell > .list-inline > .noindex > a[href*="/en/business/sme"]').removeClass("business-nav-header");
                $('.tbcell > .list-inline > .noindex > a[href*="/en/International-Business"]').addClass("international-business-nav-header");
                $('.tbcell > .list-inline > .noindex > a[href*="/en/ir"]').addClass("investor-nav-header");

                $('.tbcell > .list-inline > .noindex > a[href*="/en/about"]').addClass("nav_header");
                $('.tbcell > .list-inline > .noindex > a[href*="/en/contact/Pages/contact.aspx"]').addClass("nav_header");

                $('.navfooter > .container .list-group > .noindex > a[href*="/en/personal"]').addClass("personal_nav_footer");
                $('.navfooter > .container .list-group > .noindex > a[href*="/en/Business/SME"]').addClass("sme_nav_footer");
                $('.navfooter > .container .list-group > .noindex > a[href*="/en/Business"]').addClass("business-nav-footer");
                $('.navfooter > .container .list-group > .noindex > a[href*="/en/Business/SME"]').removeClass("business-nav-footer");
                $('.navfooter > .container .list-group > .noindex > a[href*="/en/international-business"]').addClass("international-business-nav-footer");
                $('.navfooter > .container .list-group > .noindex > a[href*="/en/IR"]').addClass("investor-nav-footer");

                if (spl.length > 2) {
                    if (spl[2].toLowerCase() == "personal") {
                        $('.li-menu > a[class="link-menu"]').addClass("personal_nav_header");
                        $('.box-links > .links > .noindex > a[class="link"]').addClass("personal_nav_header");
                        $('.col-xs-3 > .links > .noindex > a[class="link"]').addClass("personal_nav_footer");
                    }
                    if (spl[2].toLowerCase() == "business" && spl[3].toLowerCase() != "sme") {
                        $('#master-slider_News > .ms-container > .ms-inner-controls-cont > .ms-view > .ms-slide-container > .ms-slide > a[class="ms-slide-link hero_banner"]').addClass("main_highlight_menu");
                        $('.li-menu > a[class="link-menu"]').addClass("business-nav-header");
                        $('.box-links > .links > .noindex > a[class="link"]').addClass("business-nav-header");
                        $('.col-xs-3 > .links > .noindex > a[class="link"]').addClass("business-nav-footer");
                    }
                    if (spl[2].toLowerCase() == "business" && spl[3].toLowerCase() == "sme") {
                        $('.li-menu > a[class="link-menu"]').addClass("sme_nav_header");
                        $('.box-links > .links > .noindex > a[class="link"]').addClass("sme_nav_header");
                        $('.col-xs-3 > .links > .noindex > a[class="link"]').addClass("sme_nav_footer");
                    }
                    if (spl[2].toLowerCase() == "international-business") {
                        $('#master-slider_News > .ms-container > .ms-inner-controls-cont > .ms-view > .ms-slide-container > .ms-slide > a[class="ms-slide-link hero_banner"]').addClass("main_highlight_menu");
                        $('.li-menu > a[class="link-menu"]').addClass("international-business-nav-header");
                        $('.box-links > .links > .noindex > a[class="link"]').addClass("international-business-nav-header");
                        $('.col-xs-4 > .links > .noindex > a[class="link"]').addClass("international-business-nav-footer");
                    }
                    if (spl[2].toLowerCase() == "ir") {
                        $('.li-menu > a[class="link-menu"]').addClass("investor-nav-header");
                        $('.col-xs-3 > .links > .noindex > a[class="link"]').addClass("investor-nav-footer");
                    }

                    var spl = spl[2].toLowerCase();
                    var p = {
                        "p1": "contact",
                        "p2": "k-expert_b",
                        "p3": "rate",
                        "p4": "announcement",
                        "p5": "branch",
                        "p6": "promotion",
                        "p7": "faq",
                        "p8": "apply",
                        "p9": "privacy-policy",
                        "p10": "disclaimer",
                        "p11": "news",
                        "p12": "Holidays",
                        "p13": "PropertyForSale",
                        "p14": "Download"

                    };

                    for (var key in p) {
                        if (spl = p.hasOwnProperty(key)) {
                            $('.li-menu > a[class="link-menu"]').addClass("personal_nav_header");
							console.log("for " + $('.li-menu > a[class="link-menu"]').text());
                            $('.box-links > .links > .noindex > a[class="link"]').addClass("personal_nav_header");
                            $('.col-xs-3 > .links > .noindex > a[class="link"]').addClass("personal_nav_footer");
                        }
                    }
                }
                if (spl.length > 3) {
                    if (spl[3] == "loan" && spl[4] == "personal-loan") {
                        $('.main-container > .row > .filter-result > a').addClass("thumbnail_personal_loan");
                    }
                    if (spl[3] == "loan" && spl[4] == "home-loan") {
                        $('.main-container > .row > .filter-result > a').addClass("thumbnail_home_loan");
                    }
                    if (spl[3] == "sme" && spl[4] == "loan" && spl[5] == "working-capital") {
                        $('.main-container > .row > .filter-result > a').addClass("thumbnail_sme_working_capital_loan");
                    }
                    if (spl[3] == "sme" && spl[4] == "loan" && spl[5] == "special-loan") {
                        $('.main-container > .row > .filter-result > a').addClass("thumbnail_sme_special_loan");
                    }
                    if (spl[3] == "sme" && spl[4] == "loan" && spl[5] == "business-solutions") {
                        $('.main-container > .row > .filter-result > a').addClass("thumbnail_sme_business_solutions_loan");
                    }
                    if (spl[3] == "sme" && spl[4] == "loan" && spl[5] == "credit-guarantee") {
                        $('.main-container > .row > .filter-result > a').addClass("thumbnail_sme_credit_guarantee");
                    }
                }
				
				
				//--------------------Fix Tracking ------------------------------
				
				//1-5
				$('.tbcell > .list-inline > .noindex > a[href*="/th/personal"]').attr('title', 'บุคคล');
				
				//6-7
				$('.tbcell > .list-inline > .noindex > a[href*="/th/about"]').addClass("personal_nav_header");
				$('.tbcell > .list-inline > .noindex > a[href*="/th/about"]').attr('title', 'เกี่ยวกับเรา');				
				$('.tbcell > .list-inline > .noindex > a[href*="/th/contact/Pages/contact.aspx"]').addClass("personal_nav_header");
				$('.tbcell > .list-inline > .noindex > a[href*="/th/contact/Pages/contact.aspx"]').attr('title', 'ติดต่อเรา');
								
				//8-15
				//Logo KBANK
				$(".li-logo a[href='/TH']").addClass("personal_nav_header");
				$(".li-logo a[href='/TH']").attr("title","Kasikornbank logo");				
				$(".li-logo a[href='/th']").addClass("personal_nav_header");
				$(".li-logo a[href='/th']").attr("title","Kasikornbank logo");		

				
				
				$( ".link-menu.personal_nav_header" ).each(function( index ) {				   
					var getText = $(this).text();					
					$(this).attr("title",getText.trim());					  			
				});
				
				//16-19
				$( ".nav_login" ).each(function( index ) {				   
					var getText = $(this).text();					
					$(this).attr("title",getText.replace(",",", ").trim());				   				
				});
				
				//Sub Link
				$( ".link.personal_nav_header" ).each(function( index ) {				   
					var getText = $(this).text();					
					$(this).attr("title",getText.trim());								
				});
				
				//Menu Bottom Image LOGO
				$( ".submenu-bottom .tbcell .img" ).each(function( index ) {
					var getText = $(this).attr('alt');
					$(this).parent().attr("title",getText.trim());		
					$(this).parent().addClass("personal_nav_header");
				  		
				});
				
				$( ".submenu-bottom .tbcell .a-right a" ).each(function( index ) {
					var getText = $(this).find('.ic-label').text();
					$(this).attr("title",getText.trim());		
					$(this).addClass("personal_nav_header");
				  		console.log(getText);
				});
				
				
				
				//Device 1				
				$(".header-device .img-logo").parent().addClass("personal_nav_header");
				$(".header-device .img-logo").parent().attr("title","Kasikornbank logo");				
				$(".header-device .img-logo").parent().addClass("personal_nav_header");
				$(".header-device .img-logo").parent().attr("title","Kasikornbank logo");
				
				//Left Menu
				$( "#mm-57 li" ).each(function( index ) {				   
					var getText = $(this).text();	
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});
				
				
				$( "#mm-0 li"  ).each(function( index ) {				   
					var getText = $(this).find('span').text();	
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});
				
				
				$('.mm-bottom .mm-exclusive a').each(function( index ) {				   
					var getText = $(this).find('img').attr('alt');	
                    $(this).addClass("personal_nav_header");
					$(this).attr("title",getText.trim().replace(",",", ").trim());					  			
				});
				
				
				//หน้าหลัก			
				$('#mm-1 li').each(function( index ) {				   
					var getText = $(this).find('span').text();	
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});				
				
				var getText_Main = $('#mm-1 .mm-listview li.mm-home a').text();
				$('#mm-1 .mm-listview li.mm-home a').addClass("personal_nav_header");
				$('#mm-1 .mm-listview li.mm-home a').attr("title",getText_Main.trim().replace(",",", ").trim());
				
				
				
				$('#mm-2 li').each(function( index ) {				   
					//var getText = $(this).find('noindex').text();	
					var getText = $(this).text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});
				
				$('#mm-3 li').each(function( index ) {				   
					var getText = $(this).find('noindex').text();	
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});
				
				$('#mm-4 li').each(function( index ) {				   
					//var getText = $(this).find('noindex').text();
					var getText = $(this).text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-5 li').each(function( index ) {				   
					//var getText = $(this).find('noindex').text();
					var getText = $(this).text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-6 li').each(function( index ) {				   
					var getText = $(this).find('noindex').text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-7 li').each(function( index ) {				   
					//var getText = $(this).find('noindex').text();
					var getText = $(this).text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});
				
				$('#mm-8 li').each(function( index ) {				   
					var getText = $(this).find('noindex').text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-9 li').each(function( index ) {				   
					//var getText = $(this).find('noindex').text();
					var getText = $(this).text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-10 li').each(function( index ) {				   
					var getText = $(this).find('noindex').text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-11 li').each(function( index ) {				   
					//var getText = $(this).find('noindex').text();
					var getText = $(this).text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-12 li').each(function( index ) {				   
					var getText = $(this).find('noindex').text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-13 li').each(function( index ) {				   
					//var getText = $(this).find('noindex').text();
					var getText = $(this).text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
			
				$('#mm-14 li').each(function( index ) {				   
					var getText = $(this).find('noindex').text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-14 li').each(function( index ) {				   
					var getText = $(this).find('noindex').text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-15 li').each(function( index ) {				   
					//var getText = $(this).find('noindex').text();
					var getText = $(this).text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-16 li').each(function( index ) {				   
					var getText = $(this).find('noindex').text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-17 li').each(function( index ) {				   
					var getText = $(this).find('noindex').text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-18 li').each(function( index ) {				   
					var getText = $(this).find('noindex').text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				$('#mm-55 li').each(function( index ) {				   
					//var getText = $(this).find('noindex').text();
					var getText = $(this).text();
                    $(this).find('a').addClass("personal_nav_header");
					$(this).find('a').attr("title",getText.trim().replace(",",", ").trim());					  			
				});	
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				
				//--------------------End Fix Tracking------------------------------
				
            } catch (e) {
				console.log(e);
            }

            clearInterval(chkReadyState);
            //page load complete
        }
    }, 100);

});