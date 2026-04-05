

            var cookieKeys = "showNoti";
            var divNotiRender = "";

            function closeNoti() {
                $("#kb-notify").fadeOut();
                setCookie(cookieKeys, "hide", 7);
            }

            function setCookie(cname, cvalue, exdays) {
                var d = new Date();
                d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
                var expires = "expires=" + d.toUTCString();
                document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
            }

            function getCookie(cname) {
                var name = cname + "=";
                var ca = document.cookie.split(';');
                for (var i = 0; i < ca.length; i++) {
                    var c = ca[i];
                    while (c.charAt(0) == ' ') {
                        c = c.substring(1);
                    }
                    if (c.indexOf(name) == 0) {
                        return c.substring(name.length, c.length);
                    }
                }
                return "";
            }

            function checkPageActiveNoti() {
                var nt_real_pageURL = _spPageContextInfo.serverRequestPath.toLowerCase();
                var nt_lang = GetCurrentLang().toLowerCase();
                if (nt_real_pageURL.indexOf("/" + nt_lang + "/" + "personal") != -1 || nt_real_pageURL.indexOf("/" + nt_lang + "/" + "business/sme") != -1 || nt_real_pageURL.indexOf("/" + nt_lang + "/" + "business") != -1 || nt_real_pageURL.indexOf("/" + nt_lang + "/" + "international-business") != -1) {
                    return true;
                }
                return false;
            }

            //var _spBodyOnLoadFunctions2 = _spBodyOnLoadFunctions;

 
            $(document).ready(function () {

                var divNoti = '<div class="container" style="padding-left: 0;padding-right: 0"><div class="msg" style="text-align: center;"><i class="ic ic-exclamation-circle" style="padding-left: 2px;"></i>{0} <a href="{1}">{2}</a></div><a onclick="closeNoti()" class="icw-close"></a></div>';
                var divNoti_NoLink = '<div class="container" style="padding-left: 0;padding-right: 0"><div class="msg" style="text-align: center;"><i class="ic ic-exclamation-circle" style="padding-left: 2px;"></i>{0}</div><a onclick="closeNoti()" class="icw-close"></a></div>';

                //var sysSize = _spBodyOnLoadFunctions2.length;

                //for (var i = 0; i < sysSize; i += 1) {
                //    _spBodyOnLoadFunctions2[i]();
                //}

                $(window).trigger('resize');

                setTimeout(function () {
                    try {
                        if (checkPageActiveNoti()) {
                            if ($("#kb-notify-template").html().trim() != "") {
                                if ($("#kb-notify-template").html().trim().toLowerCase().indexOf("err:") == -1) {
                                    var d_ms_p_txt1 = $("#kb-notify-template").html().split("$")[0].trim();
                                    var d_ms_p_txt2 = $("#kb-notify-template").html().split("$")[1].trim();
                                    var d_ms_p_txt3 = $("#kb-notify-template").html().split("$")[2].trim();
                                    var d_ms_p_txt4 = $("#kb-notify-template").html().split("$")[3].trim();

                                    cookieKeys = d_ms_p_txt1;
                                    if (d_ms_p_txt3 == "") {
                                        //no detail
                                        divNotiRender = String.format(divNoti_NoLink, d_ms_p_txt2);
                                    } else {
                                        divNotiRender = String.format(divNoti, d_ms_p_txt2, "https://www.kasikornbank.com" + d_ms_p_txt4, d_ms_p_txt3);
                                    }

                                }
                                if (getCookie(cookieKeys) == null || getCookie(cookieKeys) == "") {

                                    //var nt_notimsg = "";
                                    //var nt_notimsg_debug = "";
                                    //if (GetCurrentLang().toLowerCase() == "th") {
                                    //    nt_notimsg = String.format(divNoti, "ธนาคารขอแจ้งงดให้บริการชั่วคราว เพื่อพัฒนาระบบและเพิ่มประสิทธิภาพการบริการให้ดียิ่งขึ้น เวลา 01:00 – 11:00 น. วันอาทิตย์ที่ 16 ก.ค. 60 ", "https://www.kasikornbank.com/th/News/Pages/DevelopSystem_16Jul17.aspx", "รายละเอียดเพิ่มเติม");
                                    //    nt_notimsg_debug = divNotiRender;
                                    //} else {
                                    //    nt_notimsg = String.format(divNoti, "KASIKORNBANK will suspend our services temporarily for system and service efficiency improvement, during 01.00 a.m.-11.00 a.m. on Sunday, July 16, 2017. ", "https://www.kasikornbank.com/en/News/Pages/DevelopSystem_16Jul17.aspx", "See the details");
                                    //    nt_notimsg_debug = divNotiRender;
                                    //}
                                    $("#kb-notify").html(divNotiRender);
                                    $("#kb-notify").addClass("kb-notify");
                                    $("#kb-notify").fadeIn();
                                }
                            }
                        }
                    } catch (e) {
                        //console.log('notify_err');
                    }


                }, 1500);
            });
        