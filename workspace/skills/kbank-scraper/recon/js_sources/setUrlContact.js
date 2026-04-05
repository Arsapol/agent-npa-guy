//** Edit for LINE Widget *//
// revised. 2023.11.26

var oldLink = "https://kbank.co/LINEfriend";


// โค้ดเช็คกรณีไม่เจอ default_page
try{
    if(default_page != undefined){
        if (default_page !== "") {
            oldLink = default_page;
        }
    }
}catch(err){
    console.log("** setUrlContact >>> not found default_page variable.")
}

var defaultLink = "";

$(document).ready(function(){
    var windowHight = $(window).height() / 2;
    changeUrl(targetChange, windowHight);
    changeUrlTab(targetChange);

    setTimeout(function(){
        if (imgWebchat) {
            //$("#chatline img").attr("src", imgWebchat);
            $("#chatline").html(`<img src=${imgWebchat} alt="KBank LINE"`)
        }
        if (tooltipText) {
            //$(".webchatbox .text").text(tooltipText);
            $("#chatline").parent()[0].dataset.tooltip = tooltipText;
        }
    } ,1000)

    
});

function changeUrl(targetChange, windowHight) {  
    let setTarget = "";
    let urlUtm = setUrlFromSesstion();

    if (targetChange.length === 1 && targetChange[0].section === "page" ) {
        setTimeout(function(){
            defaultLink = targetChange[0].link + urlUtm;
            $("#chatline").attr("href", defaultLink);
            console.log(11, defaultLink)
        }, 2500);
    } else {
        setTimeout(function(){
            defaultLink = oldLink + urlUtm;
            $("#chatline").attr("href", defaultLink);
            console.log(22, defaultLink)
        }, 2500)

        $(window).scroll(function(){
            let _scroll = $(this).scrollTop();
            let _scrollHeight = $(this).scrollTop() + $(window).height();
            
            $.each(targetChange, function( i, v) {
                if (v && v.section.length > 0) {
                    let elm = document.querySelector("#" + v.section);
                    
                    if(elm == null) return false;
                    
                    let offsetHeight = document.querySelector("#" + v.section).offsetHeight;
    
                    let offsetTop = elm.offsetTop;
                    let point = offsetTop + windowHight;
                    let distance = offsetHeight + offsetTop + windowHight;
                    
                    if (_scrollHeight >= point && _scrollHeight <= distance) {
                        setTarget = v.section;
                       
                        if (v.target) {
                            let fromHref = $("#"+setTarget).find("a.active").attr("href");
                            let fromDataTabTarget = $("#"+setTarget).find("a.active").attr("data-tab-target");
                            let activeTab = (fromHref && fromHref !== "#") ? fromHref : fromDataTabTarget;
                            if (v.target === activeTab) {
                                $("#chatline").attr("href", v.linkTab + urlUtm);
                            }
                        } else {
                            defaultLink = v.link + urlUtm;
                            $("#chatline").attr("href", defaultLink);
                        }
                    } else {
                        if (setTarget === v.section) {
                          $("#chatline").attr("href", oldLink);
                        }
                    }
                }
            });      
        });
    } 
}

function changeUrlTab(targetChange) {
    $(".tab a").on("click", function(){
        let _self = $(this);
        let tabActive = (_self.attr("href") && _self.attr("href") !== "#") ? _self.attr("href") : _self.attr("data-tab-target");
        let urlUtm = setUrlFromSesstion();


        let check = targetChange.filter(a => a.target === tabActive);
        if (check.length > 0) {
            $("#chatline").attr("href", check[0].linkTab + urlUtm);
        } else {
            $("#chatline").attr("href", defaultLink + urlUtm);
        }
        

    });
}


function setUrlFromSesstion() {
    let utm_source =  _sessionStorage.getItem("utm_source") ? `&utm_source=${_sessionStorage.getItem("utm_source")}` : "";
    let utm_medium = _sessionStorage.getItem("utm_medium") ? `&utm_medium=${_sessionStorage.getItem("utm_medium")}` : "";
    let utm_campaign = _sessionStorage.getItem("utm_campaign") ? `&utm_campaign=${_sessionStorage.getItem("utm_campaign")}` : "";
    let utm_id = _sessionStorage.getItem("utm_id") ? `&utm_id=${_sessionStorage.getItem("utm_id")}` : "";
    let utm_term = _sessionStorage.getItem("utm_term") ? `&utm_term=${_sessionStorage.getItem("utm_term")}` : "";
    let utm_content = _sessionStorage.getItem("utm_content") ? `&utm_content=${_sessionStorage.getItem("utm_content")}` : "";
    let urlUtm = utm_source + utm_medium + utm_campaign + utm_id + utm_term + utm_content;
    return urlUtm;
}