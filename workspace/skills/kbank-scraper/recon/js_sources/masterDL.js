var logDL = [];

function writeLog(text) {
  logDL.push(text);
};

_spBodyOnLoadFunctions.push(function () {
  try {
    function getDefaultValueMas() {
      var digitalData = {
        platform: "Website(K Web)",
        page: {
          category: {
            pageType: "Home",
            subCategory1: "Home",
            subCategory2: "N/A",
            subCategory3: "N/A",
            businessUnit: "Kasikorn Bank Website"
          }
        }
      };
      digitalData["page"]["pageInfo"] = {
        pageName: "Home",
        pageLanguage: $("#kb-language").find(".lang-selected").text().toLowerCase()
      };
      return digitalData;
    };

    $("#navmain ul .li-menu ul a").click(function (e) {
      writeLog("==== Adobe Event Navigation Click ====");
      try {
        digitalData = getDefaultValueMas();
        var linkName = $(this).parents(".li-menu").find(".link-menu").text() + ":" + $(this).parents(".box-links").find(".heading").text() + ":" + $(this).text();
        var linkPosition = "R" + ($(this).parents(".box-links").parent().index() + 1) + ":C" + ($(this).parent().index() + 1);
        var interactionPosition = "R0:C" + ($(this).parents(".li-menu").index() + 1);
        digitalData["page"]["linkClick"] = {
          customLinkName: linkName,
          customLinkPosition: linkPosition,
          customLinkType: "Header Click"
        };
        digitalData["navigation"] = {
          navigationType: "Header Click",
          interactionSection: "Header",
          interactionPosition: interactionPosition
        };
        writeLog(digitalData);
        _satellite.track("homeLinkClick");
      } catch (error) {
        writeLog(error.message);
      }
    });

    $("footer div.navfooter li").click(function (e) {
      try {
        writeLog("==== Adobe Event NavFooter Click ====");
        digitalData = getDefaultValueMas();
        var linkName = "Homepage:" + $(this).text();
        var linkPosition = "R1:C" + ($(this).parent().index() + 1);
        digitalData["page"]["linkClick"] = {
          customLinkName: linkName,
          customLinkPosition: linkPosition,
          customLinkType: "legalFooter"
        };
        digitalData["navigation"] = {
          navigationType: "Footer Click",
          interactionSection: "Footer",
          interactionPosition: "R1:C1"
        };
        writeLog(digitalData);
        _satellite.track("homeLinkClick");
      } catch (error) {
        writeLog(error.message);
      }
    });

    $("footer div.footer-directory li").click(function (e) {
      try {
        writeLog("==== Adobe Event Footer Directory Click ====");
        digitalData = getDefaultValueMas();
        var linkName = "Homepage:" + $(this).text();
        var linkPosition = "R" + ($(this).index() + 1) + ":C" + ($(this).parents(".col-xs-4.noindex").index() + 1);
        digitalData["page"]["linkClick"] = {
          customLinkName: linkName,
          customLinkPosition: linkPosition,
          customLinkType: "legalFooter"
        };
        digitalData["navigation"] = {
          navigationType: "Footer Click",
          interactionSection: "Footer",
          interactionPosition: "R2:C1"
        };
        writeLog(digitalData);
        _satellite.track("homeLinkClick");
      } catch (error) {
        writeLog(error.message);
      }
    });

    $("footer div.footer-utility li a").click(function (e) {
      try {
        writeLog("==== Adobe Event Footer Utility Link Click ====");
        digitalData = getDefaultValueMas();
        var imgNameSp = $(this).find("img").attr("src").split("/");
        var imgName = imgNameSp[imgNameSp.length - 1];
        imgName = imgName.substr(0, imgName.length - 4);
        var linkName = "Homepage:" + imgName;
        var linkPosition = "R1:C" + ($(this).parent().index() + 1);
        digitalData["page"]["linkClick"] = {
          customLinkName: linkName,
          customLinkPosition: linkPosition,
          customLinkType: "UtilityFooter"
        };
        digitalData["navigation"] = {
          navigationType: "Footer Click",
          interactionSection: "Footer",
          interactionPosition: "R3:C1"
        };
        writeLog(digitalData);
        _satellite.track("homeLinkClick");
      } catch (error) {
        writeLog(error.message);
      }
    });
    writeLog("Load Script Master DL Complete !!");
  } catch (error) {
    writeLog(error.message);
  }

});