function appendTemplate() {
    let html = ` <section class="wrap-noti-content">
                    <div class="noti-content window-click">
                        <div class="tab-noti window-click">
                        <div class="tab-noti-list active window-click" data-tab="announcemain">
                                <div class="window-click">
                                <i class="ic-npa ic-npa-icon-announce window-click"></i>
                                <span class="window-click">ประกาศ</span>
                                </div>
                            </div>
                            <div class="tab-noti-list window-click" data-tab="promotion"></div>
                            <div class="tab-noti-list window-click" data-tab="new">
                                <div class="window-click">
                                    <i class="ic-npa ic-noti-default window-click"></i>
                                    <span class="window-click">ทรัพย์มาใหม่</span>
                                    <i class="noti-inside"></i>
                                </div>
                            </div>
                        </div>

                         <div class="tab-content-noti announce announcemain active window-click"></div>

                        <div class="tab-content-noti promotion window-click"></div>

                        <div class="tab-content-noti new window-click">
                            <div class="content-noti-result"></div>
                            <div>
                                <a href="/th/propertyforsale/search/new-property" class="btn-more">
                                    <span>ดูทรัพย์มาใหม่ทั้งหมด</span>
                                </a>
                            </div>
                        </div>
                    </div>
                </section>`;
    $("main").append(html);

    console.log('appendTemplate fired')
}

function setTimeCookie() {
    console.log("setTimeCookie fired")
    let expDate = new Date();
    expDate.setTime(expDate.getTime() + (1 * 3600 * 1000));
    const valueEXP = new Date().getTime() + (1 * 3600 * 1000);
    // expDate.setTime(expDate.getTime() + (5 * 60 * 1000));
    // const valueEXP = new Date().getTime() + (5 * 60 * 1000);
    document.cookie = "notification_property=" + valueEXP + "; expires=" + expDate + ";path=/";

    recheckTimeCookie();
}

function getCookie(cname) {
    let name = cname + "=";
    let ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
  }

function checkTimeCookie() {
    const _cookie = getCookie("notification_property");

    if (_cookie) {
        recheckTimeCookie();
    } else {
        setTimeout(function(){
            $("body").find(".alert-noti .new-msg").show();
        }, 2000);
    }
}

function recheckTimeCookie() {
    console.log("recheckTimeCookie")
    const _cookie = getCookie("notification_property");

    let _now = new Date().getTime();
    if (_now <  _cookie) {
        $("body").find(".alert-noti .new-msg").hide(); 
    } else {
        $("body").find(".alert-noti .new-msg").show();
    }
    
    let interval = setInterval(function(){
        let now = new Date().getTime();

        if (now < _cookie ) {
            $("body").find(".alert-noti .new-msg").hide();
           
            clearInterval(interval); 
        } else {
            $("body").find(".alert-noti .new-msg").show();
        }
    }, 60000); // 1 min
}


async function fetchAnnouncementMain() {
  const req = new Request("/SiteCollectionDocuments/assets/PFS2022/pages/home/js/tab-main-announcement.txt");
  const res = await fetch(req);
  const json = await res.json();
  return json;
}

function displayDataAnnouncementMain(raw) {
  const elmAppend = $(".tab-content-noti.announcemain");

  const htmlTab = `
    <div class="window-click">
      <i class="ic-npa ${raw.icon || ""} window-click"></i>
      <span class="window-click">${raw.header || ""}</span>
    </div>`;

  const html = `
    <div>
      <div class="tab-promotion-img window-click">
        <img src="${raw.image || ""}" alt="${raw.title || ""}" class="window-click">
      </div>
      ${raw.date  ? `<div class="tab-promotion-date window-click">${raw.date}</div>` : ""}
      ${raw.tag  ? `<div class="tab-promotion-tag window-click">${raw.tag}</div>` : ""}
      ${raw.title ? `<div class="tab-promotion-head window-click">${raw.title}</div>` : ""}
      ${raw.dese  ? `<div class="tab-promotion-detail window-click">${raw.dese}</div>` : ""}
      ${raw.link  ? `<div class="tab-promotion-btn"><a href="${raw.link}" class="btn-more">ทดลองได้เลย!</a></div>` : ""}
    </div>`;

  $(".tab-noti-list[data-tab='announcemain']").html(htmlTab);

  elmAppend.html(html);

  let maxcHeightContent = $(window).height() - $("header").height() - $(".tab-noti").height() - 65;
  $(".tab-content-noti").css("max-height", maxcHeightContent + "px");

  $(window).off("resize.tabNotiMax").on("resize.tabNotiMax", function(){
    maxcHeightContent = $(window).height() - $("header").height() - $(".tab-noti").height() - 65;
    $(".tab-content-noti").css("max-height", maxcHeightContent + "px");
  });
}



async function fetchAnnouncement() {
    let myRequest = new Request("/SiteCollectionDocuments/assets/PFS2022/pages/home/js/tab-announcement.txt");
    const response = await fetch(myRequest);
    const _json = await response.json();
    return _json;
}

function displayDataAnnouncement(raw) {
    const elmAppend = $(".tab-content-noti.promotion");

    let htmlTab = `<div class="window-click">
                        <i class="ic-npa ${raw.icon} window-click"></i>
                        <span class="window-click">${raw.header}</span>
                    </div>`;

    let html = ` <div>
                    <div class="tab-promotion-img window-click">
                        <img src="${raw.image}" alt="${raw.title}" class="window-click">
                    </div>
                    ${raw.date ? `<div class="tab-promotion-date window-click">${raw.date}</div>` : ""}
                    ${raw.title ? `<div class="tab-promotion-head window-click">${raw.title}</div>` : ""}
                    ${raw.dese ? `<div class="tab-promotion-detail window-click">${raw.dese}</div>` : ""}
                    ${raw.link ? `<div class="tab-promotion-btn">
                                    <a href="${raw.link}" class="btn-more">รายละเอียดเพิ่มเติม</a>
                                    </div>` : ""}
                </div>`;

    $(".tab-noti-list[data-tab='promotion']").html(htmlTab);
    elmAppend.html(html);

    let maxcHeightContent = $(window).height() - $("header").height() - $(".tab-noti").height() - 65;
    $(".tab-content-noti").css("max-height", maxcHeightContent + "px");

    $(window).on('resize', function(){
        maxcHeightContent = $(window).height() - $("header").height() - $(".tab-noti").height() - 65;
        $(".tab-content-noti").css("max-height", maxcHeightContent + "px");
    });

}

function appendNewProp() {
    let filterPayload = {
        "CurrentPageIndex": 1,
        "PageSize": 5,
        "SearchPurposes": [
            "AllProperties"
        ],
        "Ordering": "new"
    }

    $.ajax({
        url: configs.backendPFSURL + "/GetProperties",
        type: "POST",
        data: JSON.stringify({
            filter: filterPayload,
        }),
        contentType: "application/json",
        success: function(result) {
            if (result && JSON.parse(result.d)) {
                let resData = JSON.parse(result.d);
                let data = resData && resData.Data;
                let item = data && data.Items;
                
                let html = ""
        
                if (item) {
                    let sum = item.length;
                    Object.keys(item).forEach(function(i) {
                        let typeProp = item[i].PropertyTypeName ? item[i].PropertyTypeName.split(" ")[1] : "";
                        let nameProp = typeProp + " " + item[i].ProvinceName;
        
                        let pathImage = "https://pfsapp.kasikornbank.com/pfs-frontend-api/property-images";
                        let img = "/SiteCollectionDocuments/assets/PFS2022/image/default_thumbnail.jpg";
        
                        $.each(item[i].PropertyMediaes, function (idx) {
                            let MediaType = item[i].PropertyMediaes[idx] && item[i].PropertyMediaes[idx].MediaType;
                            if (MediaType && MediaType === "IMAGE-THUMBNAIL") {
                                img = pathImage + item[i].PropertyMediaes[idx].MediaPath;
                            } 
                        })
        
                        html += `<div class="box-tab-new">
                                    <a href="/th/propertyforsale/detail/${item[i].PropertyID}.html" class="tab-new-head">${nameProp}</a>
                                    <div class="tab-new-detail">
                                        <a href="/th/propertyforsale/detail/${item[i].PropertyID}.html" class="tab-new-img">
                                            <img src="${img}" alt="${nameProp}">
                                        </a>
                                        <div>
                                            <div class="tab-new-location">
                                                <i class="ic-npa ic-npa-icon-populararea"></i>
                                                <span>${item[i].AmphurName} ${item[i].ProvinceName}</span>
                                            </div>
                                            <div class="tab-new-type">${typeProp}</div>
                                            <div class="tab-new-price"><strong>${item[i].PromotionPrice ? numberFormat(item[i].PromotionPrice) : numberFormat(item[i].SellPrice)}</strong>บาท</div>
                                        </div>
                                    </div>
                                </div>`;
                    });
                }
                $(".content-noti-result").html(html);
            }
        },
        error: function (jqXHR, exception) {
            console.log(jqXHR.status,exception);
        }
    });
}

function numberFormat(num) {
    return num ? num.toLocaleString() : "-";
}

function eventClickNoti(_this) {
    _this.find(".new-msg").hide();
    _this.find(".ic-npa").removeClass("ic-noti-default");
    _this.find(".ic-npa").addClass("ic-noti-active");

    const elmNotiConternt = $(".wrap-noti-content");
    if(elmNotiConternt.hasClass("active")) {
        $("body").removeClass("lock");
        elmNotiConternt.removeClass("active");

        _this.find(".ic-npa").addClass("ic-noti-default");
        _this.find(".ic-npa").removeClass("ic-noti-active");
    } else {
        $("body").addClass("lock");
        elmNotiConternt.addClass("active");
    }

    document.cookie = 'notification_property=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
}

function unbindNoti(event) {
    if (!$(event.target).is(".window-click, a")) {
        $("body").removeClass("lock");
        $(".wrap-noti-content").removeClass("active");

        $(".alert-noti").find(".ic-npa").addClass("ic-noti-default");
        $(".alert-noti").find(".ic-npa").removeClass("ic-noti-active");
    }
}

$(document).ready(function(){
    console.log('property-noti.js loaded')
    if(!$('.wrap-noti-content').length > 0) {
        checkTimeCookie();
        appendTemplate();
        const callNewProp = appendNewProp();
        const jsonAnnouncement = fetchAnnouncement();
        const jsonAnnouncementMain = fetchAnnouncementMain();
        jsonAnnouncement.then((raw) => {
            displayDataAnnouncement(raw);
        });
        jsonAnnouncementMain.then((raw) => {
            displayDataAnnouncementMain(raw);
        });
    
        const elmTab = $(".tab-noti-list");
        elmTab.on("click", function(){
            const activeTab = $(this).data("tab");
    
            elmTab.removeClass("active");
            $(this).addClass("active");
    
            $(".tab-content-noti").removeClass("active");
            $(".tab-content-noti." + activeTab).addClass("active");
        });
    
        
        $("body").on("click", ".alert-noti", function(){
            eventClickNoti($(this));
            setTimeCookie();
    
            dataLayer.push({
                event: "track_event",
                event_category: "header",
                event_action: "click",
                event_label: "alert-noti",
            });
        })
    
        $(document).click(function(event) {
            unbindNoti(event);
        });
    }

})
