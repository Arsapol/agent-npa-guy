/* KBank Global Search  */
// Create by Guitarx
// Version 0.5.2
// - Require jQuery dependency

// Log : 13/02/68 | Set first random card and search keyword for มาตรการชื่อเดียวกัน by add data to the array before pushing random data.

(function () {
  //
  var prefix_domain = /\/kbank\-navigation\-2023/i.test(location.pathname)
    ? "/kbank-navigation-2023"
    : "";
  //
  const _version = "0.5.2";
  let checkError = false;
  let overStep = 0;
  let popularSearch = [];

  const checkCookieKeyword = getCookie("popularSearch");

  var headerSearch = null;
  var searchSection = null;
  var searchFill = null;

  var keysuggest = [],
    html_template = "";

  window.addEventListener("load", () => {
    constructorSearch();
  });

  async function constructorSearch() {
    // 01 >> Load Suggestion
    let resp_suggestion = await fetch(
      prefix_domain +
        "/SiteCollectionDocuments/assets/search-navigation/cms/suggestion-keyword.txt"
    );
    if (!resp_suggestion.ok) {
      throw new Error(resp_suggestion.status);
    }
    keysuggest = await resp_suggestion.text();
    keysuggest = keysuggest
      .replace(/\n/g, "")
      .replace(/\s+/g, " ")
      .split(",")
      .filter((s) => s.length && s != " ");
    // 02 >> Load Template
    let resp_template = await fetch(
      prefix_domain +
        "/SiteCollectionDocuments/assets/search-navigation/cms/template-global-search.html"
    );
    if (!resp_template.ok) {
      throw new Error(resp_template.status);
    }
    html_template = await resp_template.text();
    html_template = html_template.replace(/\n|\s{3,}/g, "");
    // 03 >>Start Program
    initializeSearch();
  }

  function initializeSearch() {
    $(document).ready(function () {
      console.log(
        "%c>>>> Build : %cGlobal Search v." + _version + " 🔍🔍🔍",
        "color: #00a950",
        "color: #f762f6"
      );
      $(".g-mic").hide();
      if ($("#navigation-header").length > 0) {
        appendTemplate(html_template);
      }

      headerSearch = $("#g-nav-search");
      searchSection = $(".search-section");
      searchFill = $("#search-fill");

      $(".g-nav-close, .g-nav-back").on("click", function (e) {
        e.preventDefault();
        $("#g-nav-search").removeClass("open");
      });

      $(".main_nav_header.search").on("click", function (e) {
        e.preventDefault();

        headerSearch.find(".g-flex-row").removeClass("hide");

        $("#g-nav-search").addClass("open");
        headerSearch.find(".g-autosuggest").addClass("hide");

        headerSearch.find(".g-text-start").removeClass("hide");
        headerSearch.find(".g-pulse-ring").removeClass("hide");
        headerSearch.find(".g-recorder").addClass("hide");
        headerSearch.find(".g-text-start.error-mode").addClass("hide");
        headerSearch.find(".btn-record-agin").addClass("hide");
      });

      headerSearch.find(".g-clear-input").on("click", function () {
        $("#g-type-serach-nav").val("");
        $(this).addClass("hide");
      });

      $("#g-type-serach-nav").on("focus", function (e) {
        $(this).removeClass("valid");
      });

      $("#g-type-serach-nav").on("keyup", function (e) {
        const txt = $(this).val();

        if (e.which == 13) {
          e.target.blur();

          if (txt) {
            window.location = "/th/search?k=" + txt;

            dataLayer.push({
              event: "submitSearch",
              event_category: "search",
              eventAction: "submit",
              eventLabel: "search_text",
              search_text: `${txt}`,
            });

            console.log("event submitSearch, search_text ===> ", search_text);
          } else {
            $(this).addClass("valid");
          }
        } else {
          headerSearch.find(".g-clear-input").removeClass("hide");
          const result = filterKeyword(txt, keysuggest);

          let html = "";
          if (result && result.length > 0) {
            headerSearch.find(".g-flex-row").addClass("hide");
            headerSearch.find(".g-recorder").addClass("hide");

            headerSearch.find(".g-autosuggest").removeClass("hide");

            for (i = 0; i < 5; i++) {
              if (result[i]) {
                html += ` <a href="/th/search?k=${result[i]}">
                                        <span>${result[i]}</span>
                                    </a>`;
              }
            }
          } else {
            html = ` <a href="#">
                                <span>ไม่พบข้อมูล</span>
                            </a>`;
          }

          headerSearch.find(".g-list-autosuggest").html(html);
        }
      });

      randomCard();

      if (!checkCookieKeyword) {
        document.cookie = "popularSearch=true; path=/";
        popularSearch = randomKeywordPopular();

        document.cookie =
          "randomKeyword" + "=" + JSON.stringify(popularSearch) + "; path=/";
      } else {
        const getKeyword = getCookie("randomKeyword");
        popularSearch = JSON.parse(getKeyword);
      }

      showPopuplarSearch(popularSearch);

      let heightHeader = $("header").innerHeight();
      let heightFooter = $("footer").innerHeight();
      let _contentHeight =
        $(window).height() - heightHeader - heightFooter - 80;

      $("#g-content-recorder").css("height", _contentHeight + "px");

      const chkPermissionMic = checkMicrophonePermission();

      if (chkPermissionMic) {
        if ("webkitSpeechRecognition" in window) {
          $(".g-mic").show();
          const recognition = new webkitSpeechRecognition();
          recognition.lang = "th-TH";

          recognition.interimResults = true;

          recognition.onstart = function () {
            overStep++;
            console.log("Speech recognition started");
          };

          recognition.onresult = function (event) {
            overStep++;

            let finalTranscript = "";
            let interimTranscript = "";

            for (let i = event.resultIndex; i < event.results.length; i++) {
              const transcript = event.results[i][0].transcript;

              if (event.results[i].isFinal) {
                finalTranscript += transcript + " ";
              } else {
                interimTranscript += transcript;
              }
            }

            console.log("Final transcript:", finalTranscript);
            console.log("Interim transcript:", interimTranscript);

            headerSearch
              .find("#g-type-serach-nav")
              .val(`${finalTranscript ? finalTranscript : interimTranscript}`);
            headerSearch.find(".g-clear-input").removeClass("hide");
          };

          function stopRecognition() {
            searchFill.find("#VoiceSearch").removeClass("disable");
            let _val = $("#g-type-serach-nav").val().trim();

            recognition.stop();
            if (overStep === 1) {
              //fail

              headerSearch.find(".g-pulse-ring").addClass("hide");
              headerSearch.find(".g-text-start").addClass("hide");
              headerSearch.find(".g-sound-wave").addClass("hide");

              headerSearch.find(".g-text-start.error-mode").removeClass("hide");
              headerSearch.find(".btn-record-agin").removeClass("hide");
            } else {
              searchSection.find(".pulse-ring").hide();
              searchSection.find(".sound-wave").hide();

              if (checkError) {
                searchSection.find(".voice-fail").show();
              } else {
                headerSearch.find(".g-recorder").addClass("hide");

                headerSearch.find(".g-autosuggest").removeClass("hide");
                headerSearch.find(".g-clear-input").removeClass("hide");

                window.location = "/th/search?k=" + _val;

                dataLayer.push({
                  event: "submitSearch",
                  event_category: "search",
                  eventAction: "submit",
                  eventLabel: "search_voice",
                  search_text: `${_val}`,
                });

                console.log("event submitSearch, search_text ===> ", _val);
              }
            }
            overStep = 0;
            console.log("Speech recognition stopped");
          }

          recognition.onerror = function (event) {
            checkError = true;
            if (event.error === "not-allowed") {
              headerSearch.find(".g-pulse-ring").addClass("hide");
              headerSearch
                .find(".g-text-start.error-mode")
                .text("ฟังก์ชันไม่สามารถใช้งานได้")
                .removeClass("hide");
              headerSearch.find(".g-sound-wave").addClass("hide");
            }

            console.error("Speech recognition error:", event.error);
          };

          headerSearch.find(".g-mic").on("click", function () {
            checkWhoIsClick = "nav";
            checkError = false;
            recognition.start();
            setTimeout(stopRecognition, 5000);

            headerSearch.find(".g-flex-row").addClass("hide");
            headerSearch.find(".g-autosuggest").addClass("hide");

            headerSearch.find(".g-recorder").removeClass("hide");

            headerSearch.find(".g-pulse-ring").removeClass("hide");
            headerSearch.find(".g-sound-wave ").removeClass("hide");
            headerSearch.find(".g-text-start.error-mode").addClass("hide");
            headerSearch.find(".btn-record-agin").addClass("hide");
            headerSearch.find(".g-text-start").addClass("hide");
          });

          headerSearch.find(".btn-record-agin").on("click", function () {
            checkWhoIsClick = "nav";
            checkError = false;
            recognition.start();
            setTimeout(stopRecognition, 5000);

            headerSearch.find(".g-sound-wave").removeClass("hide");
            headerSearch.find(".g-pulse-ring").removeClass("hide");

            headerSearch.find(".g-text-start").addClass("hide");
            headerSearch.find(".btn-record-agin").addClass("hide");
          });
        } else {
          $(".g-mic").hide();
          console.error("Web Speech API is not supported in this browser");
        }
      } else {
        $(".g-mic").hide();
        console.error("Microphone is denied permission");
      }
    });
  }

  function randomKeywordPopular() {
    let arrPopularSearch = [
      "บัตรเครดิต",
      "บัตรเดบิต",
      "บัญชีธนาคาร",
      "บัตรเงินด่วน",
      "สินเชื่อเงินด่วน",
      "สินเชื่อ SME",
      "สินเชื่อบ้าน",
      "สินเชื่อรถยนต์",
      "สินเชื่อธุรกิจ",
      "กองทุนแนะนำ",
      "ทรัพย์ธนาคาร",
      "K Plus",
      "K BIZ",
      "K Shop",
      "ประกันสุขภาพ",
      "ประกันชีวิต",
      "อัตราและค่าธรรมเนียมแลกเปลี่ยน",
      "โปรโมชั่นและสิทธิพิเศษ",
      "โอนเงินและชำระเงิน",
      "ลงทุนผ่าน Wealth PLUS",
    ];

    let _newArr = ["มาตรการชื่อเดียวกัน"];

    const _shuffle = shuffle(arrPopularSearch);
    for (i = 0; i < 4; i++) {
      _newArr.push(_shuffle[i]);
    }

    return _newArr;
  }

  function getCookie(name) {
    function escape(s) {
      return s.replace(/([.*+?\^$(){}|\[\]\/\\])/g, "\\$1");
    }
    var match = document.cookie.match(
      RegExp("(?:^|;\\s*)" + escape(name) + "=([^;]*)")
    );
    return match ? match[1] : null;
  }

  function checkMicrophonePermission() {
    var permission = navigator.permissions.query({
      name: "microphone",
    });
    let _permissions = true;
    permission.then(function (data) {
      if (data.state === "denied") {
        _permissions = false;
      } else {
        _permissions = true;
      }
    });

    return _permissions;
  }

  function showPopuplarSearch(popularSearch) {
    let html = "";
    $.each(popularSearch, function (key, value) {
      html += ` <a href="/th/search?k=${value}" class="pxtm-click-linkClick" title="rec_${value}">${value}</a>`;
    });

    headerSearch.find(".g-list-popular").html(html);
    headerSearch.find(".g-list-autosuggest").html(html);
  }

  function filterKeyword(txt, keysuggest) {
    return (_filter = keysuggest.filter(function (i) {
      return i.indexOf(txt) != -1;
    }));
  }

  function randomCard() {
    let arrCard = [
      {
        name: "สินเชื่อบุคคล",
        img: "01",
        url: "/th/personal/loan/personal-loan",
      },
      {
        name: "บัตรเดบิต",
        img: "02",
        url: "/th/personal/debit-card",
      },
      {
        name: "บัตรเครดิต",
        img: "03",
        url: "/th/personal/creditcard/Pages/creditcard.aspx",
      },
      {
        name: "สินเชื่อรถ",
        img: "04",
        url: "/th/personal/loan/car-loan",
      },
      {
        name: "บัญชีธนาคาร",
        img: "05",
        url: "/th/personal/loan/car-loan",
      },
      {
        name: "หุ้น",
        img: "06",
        url: "/th/personal/invest/pages/stock.aspx",
      },
      {
        name: "K PLUS",
        img: "07",
        url: "/th/kplus",
      },
      {
        name: "mPOS",
        img: "08",
        url: "/th/business/sme/digital-banking/kshop/pages/index.aspx",
      },
      {
        name: "K BIZ",
        img: "09",
        url: "/th/kbiz/pages/index.aspx",
      },
      {
        name: "ทรัพย์มือสอง",
        img: "10",
        url: "/th/propertyforsale",
      },
      {
        name: "K SHOP",
        img: "11",
        url: "/th/business/sme/digital-banking/kshop/pages/index.aspx",
      },
      {
        name: "เครื่องรูดบัตร",
        img: "12",
        url: "/th/business/sme/digital-banking/kshop/pages/index.aspx",
      },
    ];

    let newArrCard = [
      {
        name: "มาตรการชื่อเดียวกัน",
        img: "13",
        url: "/th/announcement/pages/same-registered-name.aspx",
      },
    ];

    const _shuffle = shuffle(arrCard);
    for (i = 0; i < 5; i++) {
      newArrCard.push(_shuffle[i]);
    }

    let html = "";
    let htmlOnpage = "";

    $.each(newArrCard, function (key, value) {
      html += ` <a href="${value.url}" class="pxtm-click-linkClick" title="${value.name}">
                          <span>${value.name}</span>
                          <img class="visible-w767" src="${prefix_domain}/SiteCollectionDocuments/assets/search-navigation/img/product-recommend/mobile/product${value.img}-m.png" width="120" alt="บริการแนะนำ" loading="lazy">
                          <img class="hidden-w767" src="${prefix_domain}/SiteCollectionDocuments/assets/search-navigation/img/product-recommend/desktop/product${value.img}.png" width="210" alt="บริการแนะนำ" loading="lazy">
                      </a>`;

      htmlOnpage += `<a href="${value.url}" class="g-link-thumb pxtm-click-linkClick" title="${value.name}">
                            <span class="g-img-thumb">
                                <img src="${prefix_domain}/SiteCollectionDocuments/assets/search-navigation/img/default/icon-not-found${value.img}.png" alt="${value.name}" loading="lazy">
                            </span>
                            <span class="g-text-thumb">${value.name}</span>
                        </a>`;
    });

    headerSearch.find(".g-list-recommend").html(html);
    $("#g-page-search").find(".g-list-thumb").html(htmlOnpage);

    $("#g-page-search")
      .find(".g-link-thumb")
      .on("click", function () {
        const link = $(this).attr("href");
        window.location.href = link;
      });
  }

  function shuffle(array) {
    let currentIndex = array.length,
      randomIndex;

    while (currentIndex != 0) {
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex--;

      [array[currentIndex], array[randomIndex]] = [
        array[randomIndex],
        array[currentIndex],
      ];
    }

    return array;
  }

  function appendTemplate(s) {
    $("body").append(s);
  }
})();
