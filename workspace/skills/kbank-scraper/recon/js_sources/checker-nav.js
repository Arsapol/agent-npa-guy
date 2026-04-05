$(document).ready(function(){
    setTimeout(function(){
        const idNav = $("#navigation-header");
        const onetrustBanner = $("#onetrust-banner-sdk").length;

        if (idNav.length > 0 && onetrustBanner > 0) {
            $("body").css("padding-top", "88px");
        }

        $("#onetrust-accept-btn-handler, .save-preference-btn-handler").on("click", function(){
            $("body").css("padding-top", 0);
        });
    }, 2000)
});