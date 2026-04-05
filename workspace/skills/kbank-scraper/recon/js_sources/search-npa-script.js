//Version 2.3.10

/* 
getContentTab(dataTab, load, clear)
--- Loads the content for a specific tab when switching tabs. It saves the active tab and the current state of the loadMorePage object to the session storage. It constructs a payload for the AJAX request to fetch the content for the specified tab. Depending on the tab and the current page, it either makes an AJAX request to fetch the content or uses the cached data. It also handles the display of loading indicators and the "load more" button.

initPropertySwiper()
--- Initializes a Swiper instance for the property images. It sets up the Swiper with various options such as the number of slides per view, space between slides, navigation buttons, pagination, and lazy loading of images. It also includes event handlers for the initialization and slide change events to update the pagination and handle other UI changes.

resumeScroll()
--- Scrolls the page to a previously saved position. It checks if a scroll position was saved in the session storage and, if so, scrolls the window to that position after a delay.

handleTab(tab, rowNum, condition)
--- Handles the display of tab content based on the specified condition. It updates the active tab content element and shows or hides the "not found" message based on whether the content was found.

splitPropTypeFn(PropertyTypeName, PropertyTypeID, ProvinceName, VillageTH)
--- Splits the property type name and constructs a full property type name based on the provided parameters. It handles special cases for certain property type IDs.

updateTabNumTotal(tab, num)
--- Updates the total number of items displayed in the tab. It updates the text content of elements with the class num-total to show the total number of items.

renderAssets(items, typeExtra)
--- Renders the HTML for the list of assets based on the provided items. It constructs the HTML for each asset, including the property images, details, and price information.

renderPromotionbar(casename)
--- Renders the HTML for the promotion bar based on the provided case name. It returns the appropriate HTML for the specified promotion case.

writeJSONSchema(result, tab)
--- Writes the JSON schema for the specified tab based on the provided result data. It constructs the schema template and creates or updates the JSON schema script element in the document.

createJSONSchema(schemaTemplate, tab)
--- Creates a new JSON schema script element in the document based on the provided schema template and tab.

updateJSONSchema(schemaTemplate, tab)
--- Updates an existing JSON schema script element in the document based on the provided schema template and tab. If the script element does not exist, it creates a new one.

clearJSONSchema()
--- Clears all JSON schema script elements from the document. It removes all script elements with an ID starting with schema_.

getItemListElement(data, tab)
--- Constructs the item list element for the JSON schema based on the provided data and tab. It creates an array of product objects with the necessary properties for the JSON schema.

getNameProp(PropertyTypeName, PropertyTypeID, ProvinceName, VillageTH)
--- Constructs the name of the property based on the provided parameters. It handles special cases for certain property type IDs and constructs the full property name.

These functions are responsible for handling the main functionalities of loading tab content, initializing the Swiper instance, managing scroll positions, handling tab displays, rendering assets, and managing JSON schemas.
*/

console.log("===== NPA Search v.2.3.10 =====");

const currentParams = new URLSearchParams(window.location.search);
const exceptionParams = ['keyword', 'province', 'district', 'propertyType', 'propertyTypeCode', 'price', 'advancedsearch']
const getContentTabException = (exceptionParams.some(e => window.location.search.includes(e)))
console.log('getContentTabException', getContentTabException)

const debugEnabled = true;

/* Debug Async Load */
var _checkIsLoading = false;

if (!debugEnabled) {
    console.log = function() {}
    ;
    // Disable logging
    console.info = function() {}
    ;
    // Disable logging
    console.warn = function() {}
    ;
    // Disable logging
    console.error = function() {}
    ;
    // Disable logging
}

const lastLink = sessionStorage.getItem("npa_nextPage");

var page = "search";
let objPayload = {
    filter: {
        AllCurrentPageIndex: 1,
        CurrentPageIndex: 1,
        // Ordering: "Hot",
        PageSize: 20,
        // propertyList: "newProperty",
    },
};
let searchSession = getSessionObj("npa_search");
let tabActive = currentParams['tabname'] ? currentParams['tabname'] : 'AllProperties';

let currentAssetData;

let payloadMapAdvanceSearch = {};
let objDisplayValue = {};
let schemaData = {};

let objPersonalizedValue = {};
let loadMorePage = {};
let htmlAppend = "";
const perLoad = 20;
let isSearch = false;
let isAdvanceSearchOpen = false;

clearStoredData("npa_fetchedData");
clearStoredData("npa_search");
//clearStoredData("npa_loadMorePage");
clearStoredData("npa_mode");
clearStoredData("npa_activeTab");

if (!lastLink || !lastLink.includes("/th/propertyforsale/detail" || !lastLink.includes("/th/propertyforsale/search"))) {
    clearStoredData("npa_fetchedData");
    clearStoredData("npa_search");
    //clearStoredData("npa_scrollPosition");
    clearStoredData("npa_loadMorePage");
    clearStoredData("npa_mode");
    clearStoredData("npa_activeTab");
}
/* else {
    if(searchSession) {
        objPayload.filter.Search = searchSession.keyword;
        objPayload.filter.Provinces = getOptionValueByLabel(searchSession.province);
        objPayload.filter.Amphurs = getOptionValueByLabel(searchSession.district);
        objPayload.filter.PropertyTypes = getOptionValueByLabel(searchSession.propertyType);
        if(searchSession.Price) {
            const minMax = getOptionValueByLabel(searchSession.Price).split(" - ");
            objPayload.filter.MinPrice = minMax[0];
            objPayload.filter.MaxPrice = minMax[1];
        }

    }
} */

const clickDefaultTab = () => {
    console.log('clickDefaultTab()')
    document.querySelector(`.g-tab-list[data-tab="AllProperties"]`).click()
}

if (getContentTabException) {
    //sessionStorage.clear("npa_scrollPosition");
    //sessionStorage.clear("npa_loadMorePage");
    //sessionStorage.clear("npa_search");
    //sessionStorage.clear("npa_payload");
    //sessionStorage.clear("npa_mode");
    //sessionStorage.clear("npa_activeTab");
    sessionStorage.clear("npa_fetchedData");
}
let minPriceDisplay = "";
let maxPriceDisplay = "";
let minAreaDisplay = "";
let maxAreaDisplay = "";
let minUseableAreaDisplay = "";
let maxUseableAreaDisplay = "";

let stationData = {};
let kblbTab;

let isClearSearch = false;
let isPropertyFetched = false;
let isShowPromotionOnSearch = false;
let TotalRows = {};

const labelToValueMap = {
    บ้านเดี่ยว: "02",
    ที่ดิน: "01",
    ทาวน์เฮ้าส์: "03",
    คอนโดมิเนียม: "05",
    อาคารพาณิชย์: "04",
    โกดัง: "12",
    โรงงาน: "09",
    อพาร์ทเม้นท์: "15",
    อาคารสำนักงาน: "10",
    รีสอร์ท: "20",
    อื่นๆ: "other",
    "02": "บ้านเดี่ยว",
    "01": "ที่ดิน",
    "03": "ทาวน์เฮ้าส์",
    "05": "คอนโดมิเนียม",
    "04": "อาคารพาณิชย์",
    12: "โกดัง",
    "09": "โรงงาน",
    15: "อพาร์ทเม้นท์",
    10: "อาคารสำนักงาน",
    20: "รีสอร์ท",
    other: "อื่นๆ",
    ทรัพย์ธนาคาร: "kbank",
    ทรัพย์ฝากขาย: "npl",
    ทรัพย์ผู้ขาย: "Partner",
    kbank: "ทรัพย์ธนาคาร",
    npl: "ทรัพย์ฝากขาย",
    Partner: "ทรัพย์ผู้ขาย",
};

// --- MAP Variables

var map;
let marker;
let infoWindow;
let infoList = [];
let infoWindowMap = {};
let markerList = [];
let selectedMarker = null;
let initZoomLevel;
let iconMain = "";
let swiperMap;

/* If browser back button was used, flush cache */
$(function() {
    // Replace the current history state when the page is loaded
    history.replaceState({
        page: 1,
    }, null, null);

    // Handle the popstate event
    window.onpopstate = function(event) {
        history.replaceState({
            page: 2,
        }, null, null);
    }
    ;
});

window.addEventListener("load", (event) => {
    console.log('SEARCH-NPA-SCRIPT.JS LOAD')

    const URL = configs.backendPFSURL + "/GetProperties";
    const renovateURL = '/SiteCollectionDocuments/assets/PFS2022/pages/home/js/star-asset-20250225.json';
    const stationURL = configs.backendPFSURL + "/RequestStations";

    const elmSearch = document.querySelector("#header-search");
    const inputSearch = document.querySelector(".input-search-wrapper");
    const headerElement = document.querySelector("header");
    const headerHeight = headerElement ? headerElement.offsetHeight : 0;
    const breadcrumbsHeight = document.querySelector("#breadcrumbs").offsetHeight;
    let contentHeight = document.querySelector(".g-tab-toggle-content").offsetHeight;
    const windowHeight = window.innerHeight;
    const btnSwichMode = document.querySelector(".btn-swich-mode");
    const btnView = document.querySelector(".btn-view");

    const tabContent = document.querySelector(".g-tab-content");
    const mapWrapper = document.querySelector(".map-container");
    const containerBox = document.querySelector(".container-box");

    const searchProperty = document.querySelector("#search-property");
    const searchPropertyAdvance = document.querySelector("#search-property-advance");
    const resetSearchProperty = document.querySelector("#reset-search-property");

    const propertyName = document.querySelector("#input-popup-search");
    const aiCheckbox = document.querySelector("#ai");
    const sourceSaleTypes = document.querySelectorAll('input[name="source-sale-types"]');
    const provinceElement = $("#province-filter");
    const districtElement = $("#district-filter");
    const subDistrictElement = $("#sub-district-filter");

    const propTypeElement = $("#property-type-filter");
    const priceElement = $("#price-filter");
    // const propertyTypeElement = document.querySelectorAll(
    //   'input[name="property-type"]'
    // );
    const areaElement = $("#area");
    const usableAreaElement = $("#usablearea");
    const transportationElement = $("#transportation-filter");

    const _provinceElement = document.getElementById("province-filter");
    const _districtElement = document.getElementById("district-filter");
    const _subDistrictElement = document.getElementById("sub-district-filter");

    const _areaElement = document.getElementById("area");
    const _usableAreaElement = document.getElementById("usablearea");
    const _priceElement = document.getElementById("price-filter");
    const _propTypeElement = document.getElementById("property-type-filter");

    const _transportationElement = document.getElementById("transportation-filter");

    const bedRoomElement = document.querySelectorAll('input[name="bed-room"]');
    const bathRoomElement = document.querySelectorAll('input[name="bath-room"]');
    // const inputDisPlayElement = document.getElementById("input-display-filter");
    const tabDefaultElements = document.querySelectorAll(".tab-default");

    const btnGoToMap = document.querySelector("#goToMap");
    const btnGoToList = document.querySelector("#goTolist");

    let mode = "list";

    let windowWidth = window.innerWidth;
    let desktopWidth = 1024;

    let windowScroll = 0;

    let savedPosition = sessionStorage.getItem("npa_scrollPosition");
    let loadMorePageSession = getSessionObj("npa_loadMorePage");
    let payloadSession = getSessionObj("npa_payload");

    let modeSession = getSessionObj("npa_mode");
    let tabSession = getSessionObj("npa_activeTab");
    let lastUrlPath;
    let lastUrlParam;
    let haveAiParam = getSessionObj("npa_payload")?.filter?.SearchPurposes?.includes('HaveAi') ? true : false;
    if (sessionStorage.getItem("npa_url")) {
        lastUrlPath = sessionStorage.getItem("npa_url").split("?")[0];
        lastUrlParam = sessionStorage.getItem("npa_url").split("?")[1];
    }

    sessionStorage.setItem("npa_url", window.location);
    let currentUrlPath = sessionStorage.getItem("npa_url").split("?")[0];
    let currentUrlParam = sessionStorage.getItem("npa_url").split("?")[1];

    //########################## Advanced Search Element ###################################

    const filterBtn = document.querySelector("#filter-button");
    const searchCloseBtns = document.querySelectorAll(".js-search-close");

    const searchDOM = document.querySelector(".search-container");
    const searchDropdownDOM = document.querySelector(".search-container .npa-dropdown-bar");
    const searchActionDOM = document.querySelector(".search-action-wrapper");
    const searcbMobileHeading = document.querySelector(".search-mb-heading");

    const advanceSearch = document.querySelector(".search-container .option-search-wrapper");

    let currentSearchSession = {}

    //########################## Query URL ###################################

    function parseQuerystring() {
        let dict = {};
        if (window.location.href.includes("?")) {
            let path = window.location.href.replace('#', '').split("?")[1].split("&");
            let elem = [];
            for (let i = path.length - 1; i >= 0; i--) {
                elem = path[i].split("=");
                if (elem[0] !== "" && elem[1] !== "") {
                    dict[elem[0]] = decodeURIComponent(elem[1]);
                }
            }
        }

        // Omit UTM parameters
        delete dict.utm_source;
        return dict;
    }

    const queryObject = parseQuerystring();
    console.log("== SEARCH query");
    console.log(queryObject)
    
    if (Object.keys(queryObject).length > 0) {
        for (let key in queryObject) {
            if (queryObject.hasOwnProperty(key)) {
                const value = queryObject[key];
                const priceValue = () => {
                    const params = new URLSearchParams(queryObject);
                    const priceParams = params.get('price')
                    console.log('priceParams', priceParams)
                    return priceParams.split('-')
                }
                const valuesArray = value.includes(",") ? value.split("-") : [value];
                console.log('PARAMS : ', key, value);

                switch (key.toLowerCase()) {
                case "keyword":
                    objDisplayValue["keyword"] = value;
                    objPayload.filter.Search = value;
                    setTimeout( () => {
                        propertyName.val(value).trigger('change')
                        clickDefaultTab()
                    }
                    , 100)
                    break;
                case "province":
                    const provinceId = parseInt(value);
                    objPayload.filter.Provinces = [provinceId];
                    objDisplayValue["province"] = getProvinceFromValue(provinceId);
                    setTimeout( () => {
                        provinceElement.val(provinceId).trigger("change")
                        clickDefaultTab()
                        //handleProvinceElement()
                    }
                    , 500)
                    break;
                case "district":
                    const province = parseInt(queryObject["province"]);
                    const districtId = parseInt(value);
                    objPayload.filter.Amphurs = [districtId];
                    objDisplayValue["district"] = getDistrictFromValue(province, districtId);
                    setTimeout( () => {
                        districtElement.val(districtId).trigger("change")
                        clickDefaultTab()
                        //handleDistrictElement()
                    }
                    , 500)
                    break;
                case "propertytype":
                case "propertytypecode":
                    objPayload.filter.PropertyTypes = [value];
                    objDisplayValue["propertyType"] = labelPropertyType(value);
                    setTimeout( () => {
                        propTypeElement.val(value).trigger("change")
                        clickDefaultTab()
                        //handlePropTypeElement()
                    }
                    , 100)
                    break;
                case "price":
                    const [minPriceValue,maxPriceValue] = priceValue()
                    console.log('minPriceValue', minPriceValue, 'maxPriceValue', maxPriceValue);
                    minPriceDisplay = minPriceValue;
                    objPayload.filter.MinPrice = minPriceValue ?? 0;
                    maxPriceDisplay = maxPriceValue;
                    objPayload.filter.MaxPrice = maxPriceValue;
                    setTimeout( () => {
                        priceElement.val(`${minPriceValue}-${maxPriceValue}`).trigger("change")
                        clickDefaultTab()
                        //handlePriceElement()
                    }
                    , 100)
                    break;
                case "tabname":
                    //console.clear()
                    tabActive = value;
                    dataTab = value;
                    console.log('tabActive', tabActive);
                    console.log('value', value);
                    switch (value){
                        case "allproperties": 
                            tabActive = "AllProperties"; 
                        break;
                        case "promotionproperties": 
                            tabActive = "PromotionProperties";
                        break;
                        case "outstandingalongtheskytrain": 
                            tabActive = "OutstandingAlongTheSkyTrain";
                        break;
                        case "outerbangkok": 
                            tabActive = "OuterBangkok";
                        break;
                        case "citycenter": 
                            tabActive = "CityCenter";
                        break;
                        case "bungalow": 
                            tabActive = "Bungalow";
                        break;
                        case "doctor":
                            tabActive = "Doctor";
                        break;
                        case "haveai": 
                            tabActive = "HaveAi";
                        break;
                        default: break;
                    }
                    const tabNameActiveElement = document.querySelector(`.g-tab-wrapper [data-tab="${tabActive}"]`);

                    setTimeout( () => {
                        if (tabNameActiveElement) {
                            tabNameActiveElement.click()
                            //getContentTab(tabActive, loadMorePage);
                        } else {
                            console.error(`Tab with data-tab="${tabActive}" not found.`);
                        }
                    }
                    , 500)

                    tabDefaultElements.forEach( (tabDefault) => {
                        tabDefault.style.display = "";
                    }
                    )
                    break;
                case "advancesearch":
                    if (value === "true") {
                        toggleSearch("open", 4);
                    }

                    break;
                default:
                    // console.log(`Key: ${key} not found.`);
                    break;
                }
            }
        }
        toggleAdvancedSearch(objDisplayValue);
    } else {
        // console.log("No querystring found.");
        if (mode === "list") {
            if (!tabActive) {
                tabActive = "AllProperties";
                loadMorePage[tabActive] = 1;
            }
            console.log("BBF 1")
            getContentTab(tabActive, loadMorePage);
        }
    }

    //########################## END Query URL ###################################

    // Detect if URL parameter has changed

    if ((lastUrlPath && currentUrlPath && lastUrlPath === currentUrlPath && lastUrlParam !== currentUrlParam)) {
        //loadMorePageSession = [];
        //modeSession = [];
        //tabSession = [];
        //searchSession = [];
        //payloadSession = [];
        //savedPosition = null;

        //sessionStorage.clear("npa_scrollPosition");
        sessionStorage.clear("npa_loadMorePage");
        sessionStorage.clear("npa_search");
        //sessionStorage.clear("npa_payload");
        sessionStorage.clear("npa_mode");
        sessionStorage.clear("npa_activeTab");
    }

    if (tabSession.length > 0) {
        tabActive = tabSession;
    } else {
        tabActive = "AllProperties";
    }

    /* if (modeSession) {
        mode = modeSession;

        if (mode === "map") {
            goToMap();
        } else {
            goToList();
            mode = "list";
            if (Object.keys(loadMorePageSession).length > 0) {
                loadMorePage = {
                    ...loadMorePage,
                    ...loadMorePageSession,
                };

            } else {
                loadMorePage["AllProperties"] = 1;
            }
            if (searchSession.length > 0 || Object.keys(searchSession).length > 0) {
                isSearch = true;
                toggleAdvancedSearch(searchSession);
            }
        }
    } */
    document.body.addEventListener("click", function(event) {
        // Use closest() to find the nearest <a> ancestor of the clicked element
        let link = event.target.closest("a");
        if (link) {
            let destination = link.href;
            sessionStorage.setItem("npa_nextPage", destination);
        }
    });

    document.addEventListener("scroll", (event) => {
        windowScroll = window.scrollY;
        contentHeight = getHeigtContent();

        fixInputSearch(windowScroll);
    }
    );

    btnView.addEventListener("click", function(e) {
        e.preventDefault();
        toggleViewBtn();
    });

    function toggleViewBtn() {
        document.querySelector(".btn-swich-mode").classList.toggle("active");
        document.querySelector(".btn-view").classList.toggle("active");
    }

    addEventListener("resize", (event) => {
        windowWidth = window.innerWidth;
        contentHeight = getHeigtContent();

        fixInputSearch(windowScroll);
        // fixButton(windowScroll, contentHeight);
    }
    );

    //Init page load
    goToList();

    // -------- Fixed Search --------
    const paddingTop = 24;
    const inputSearchPosition = inputSearch.offsetTop - headerHeight - paddingTop;
    let countPosition = true;

    function fixInputSearch(p) {
        if (p === 0) {
            elmSearch.classList.remove("fixed");
        }
        if (windowWidth > desktopWidth) {
            if (p >= inputSearchPosition) {
                elmSearch.classList.add("fixed");
            }
        } else {
            if (p >= inputSearchPosition - breadcrumbsHeight) {
                elmSearch.classList.add("fixed");
            } else if (p === 0) {}
        }
    }
    // -------- End of Fixed Search -----

    gTabPlugin.TabToggle.init("tab-1");

    // -------- Fixed button switch mode --------
    // function fixButton(p, h) {
    //   const positionExpected =
    //     p + windowHeight - elmSearch.offsetHeight - breadcrumbsHeight;

    //   if (positionExpected <= h) {
    //     btnSwichMode.classList.add("fixed");
    //   } else {
    //     btnSwichMode.classList.remove("fixed");
    //   }
    // }

    function getHeigtContent() {
        return document.querySelector(".g-tab-toggle-content").offsetHeight;
    }
    // -------- End of Fixed button switch mode --------

    function swichMode(mode) {
        containerBox.classList.remove("list");
        containerBox.classList.remove("map");
        containerBox.classList.add(mode);
        //saveToSession("npa_mode", mode);
    }
    btnGoToMap.addEventListener("click", function() {
        goToMap();
        toggleViewBtn();

    });

    function goToMap() {
        btnGoToMap.classList.remove("active");
        btnGoToList.classList.add("active");

        mapWrapper.classList.add("active");
        tabContent.classList.remove("active");

        btnGoToList.addEventListener("click", function() {
            goToList();
            toggleViewBtn();
        });

        mode = "map";
        swichMode(mode);
        hiddenMobileFooter(true);
        contentHeight = getHeigtContent();
        // fixButton(windowScroll, contentHeight);

        clearJSONSchema();

        if (!isSearch) {
            if (mode === "map") {
                console.log("MNX 1")
                let payload = {
                    filter: {
                        CurrentPageIndex: 1,
                        PageSize: 20,
                        SearchPurposes: haveAiParam ? [tabActive, 'HaveAi'] : [tabActive]
                        //Ordering: "New",
                    },
                };

                getPropertyMap(payload, (requestFetch = false));
            } else {
                // loadMorePage[dataTab] = 1;
                console.log("BBF 2")
                getContentTab(dataTab, loadMorePage);
            }
        } else {
            if (mode === "map") {
                payloadMapAdvanceSearch = JSON.parse(JSON.stringify(objPayload));
                payloadMapAdvanceSearch.filter.SearchPurposes = [tabActive];

                getPropertyMap(payloadMapAdvanceSearch, (requestFetch = true));
            } else {// console.log(`>>> search and list mode`);
            }
        }
    }

    function goToList() {
        btnGoToList.classList.remove("active");
        btnGoToMap.classList.add("active");

        mapWrapper.classList.remove("active");
        tabContent.classList.add("active");
        clearJSONSchema();
        mode = "list";
        swichMode(mode);
        hiddenMobileFooter(false);
        contentHeight = getHeigtContent();
        // fixButton(windowScroll, contentHeight);

        if (isSearch) {
            // console.log(">>> goto list with searching");
            searchProperty.click();
        } else {
            // console.log(">>> goto list without searching");
            // Cancel init getContentTab with these paramter 
            if (!getContentTabException) {
                console.log("BBF 3")
                getContentTab(tabActive, loadMorePage);
            }
        }
        //getContentTab(tabActive, loadMorePage);
    }

    function getStationData() {
        if (stationData.length === 0 || !stationData.length) {
            console.log("DDD 5")
            $.ajax({
                url: stationURL,
                type: "GET",
                contentType: "application/json",
            }).done(function(result) {
                // console.log("call stationData");
                stationData = JSON.parse(result.d).Data || [];
                populateDropdown(_transportationElement, stationData);
            }).fail(function(error) {
                console.error("Error fetching station data:", error);
            });
        }
    }

    //########################## Google map ###################################

    function initAllMap(locations, data) {
        initZoomLevel = getZoom(locations);

        let id = "";
        let image = "";
        let PromotionPrice = "";
        let spacialPrice = "";
        let sellPrice = "";
        let location = "";
        let name = "";

        // Check if a map already exists
        if (map) {
            // Clear existing markers and info windows
            for (const marker of markerList) {
                marker.setMap(null);
                // Remove marker from the map
            }
            markerList = [];
            // Clear marker list
            for (const infoWindow of infoList) {
                infoWindow.close();
                // Close any open info windows
            }
            infoList = [];
            // Clear info window list
            infoWindowMap = {};
            // Clear info window map for reference

            // Clear the map container (optional)
            document.getElementById("map-lg").innerHTML = "";

            // Reset map to null for clean initialization
            map = null;
        }

        // ----------- MAP Config ----------- //
        if (data) {
            iconMain = {
                url: "/SiteCollectionDocuments/assets/PFS2022/pages/search/img/pin-map.gif",
                size: new google.maps.Size(32,32),
                scaledSize: new google.maps.Size(32,32),
                anchor: new google.maps.Point(0,50),
            };
            iconSub = {
                url: "/SiteCollectionDocuments/assets/PFS2022/pages/search/img/marker-other_64x64.png",
                size: new google.maps.Size(32,32),
                scaledSize: new google.maps.Size(32,32),
                anchor: new google.maps.Point(0,50),
            };
        }

        let customMapStyles = setMapStyle();
        let mapOptions = {
            zoom: initZoomLevel,
            center: {
                lat: 13.746389,
                lng: 100.535004,
            },
            clickableIcons: true,
            draggable: true,
            zoomControl: false,
            streetViewControl: false,
            fullscreenControl: false,
            disableDefaultUI: true,
            styles: customMapStyles,
        };
        if (window.innerWidth >= 1024) {
            mapOptions.zoomControl = true;
        }

        // ----------- MAP Init ----------- //
        map = new google.maps.Map(document.getElementById("map-lg"),mapOptions);

        let bounds = new google.maps.LatLngBounds();

        // Check if there is no data
        if (locations.length === 0) {
            // console.log("no marker");
            // Optionally, you can clear the map entirely
            if (map) {
                map = null;
                document.getElementById("map-lg").innerHTML = "";
                // Clear the map container
            }
            return;
        }

        for (let i = 0; i < locations.length; i++) {
            let propertyLocation = locations[i];

            let lat = parseFloat(propertyLocation.lat);
            let lng = parseFloat(propertyLocation.lng);
            if (!isValidLatLng(lat, lng)) {
                console.warn(`Lat Long out of area : id : ${propertyLocation.id} : ${lat}, ${lng}`);
                continue;
                // Skip this location if coordinates are invalid
                // continue; // Skip this location if coordinates are invalid
            }
            let contentString = setContentString(data[i]);

            if (data) {
                infowindow = new google.maps.InfoWindow({
                    content: contentString,
                    id: propertyLocation.id,
                });
                infoWindowMap[propertyLocation.id] = infowindow;
                infoList.push(infowindow);
            }

            // --- Init Marker --- //
            marker = new google.maps.Marker({
                position: new google.maps.LatLng(lat,lng),
                map: map,
                store_id: propertyLocation.id,
                icon: iconSub,
            });
            if (i === 0) {
                // Set the first marker as default (optional)
                marker.icon = iconMain;
                // Assuming iconMain is defined with a different style
                selectedMarker = marker;
            }
            markerList.push(marker);
            bounds.extend(marker.position);

            // Add click event listener to open the info window
            marker.addListener("click", () => {
                const assetCard = document.querySelector(`a[data-id="${propertyLocation.id}"]`);
                assetCard.click();

                let assetSlide = document.querySelector(`.map-properties-swiper .swiper-slide:has(a[data-id="${propertyLocation.id}"])`);

                if (assetSlide && swiperMap) {
                    // Ensure Swiper instance exists
                    const slideIndex = swiperMap.slides.findIndex( (slide) => slide === assetSlide);

                    // Handle potential errors and edge cases
                    if (slideIndex !== -1) {
                        try {
                            swiperMap.slideTo(slideIndex /* options */
                            , {
                                speed: 500,
                            });
                            // Smooth scroll with optional speed (default 300ms)
                        } catch (error) {
                            console.error(`Error scrolling to slide: ${error}`);
                        }
                    } else {
                        console.warn(`Slide not found for property ID: ${propertyLocation.id}`);
                    }
                } else {
                    console.warn("Swiper instance not found or asset slide not available");
                }
            }
            );
        }

        if (locations.length > 0) {
            // Adjust the map to fit the bounds of all markers
            map.fitBounds(bounds);
        } else {// console.log("no marker");
        }

        var legend = document.getElementById("legend-lg");
        map.controls[google.maps.ControlPosition.LEFT_BOTTOM].push(legend);
    }

    const selectPropertyMap = (lat, lng, data) => {
        let iconMain = {
            url: "/SiteCollectionDocuments/assets/PFS2022/pages/search/img/pin-map.gif",
            size: new google.maps.Size(32,32),
            scaledSize: new google.maps.Size(32,32),
            anchor: new google.maps.Point(0,50),
        };

        let targetLatLng = new google.maps.LatLng(lat,lng);
        let targetMarker = markerList.find( (m) => m.store_id === data.id);

        // Get infowindow based on property ID
        let infoWindow = infoWindowMap[data.id];

        // Close all info windows
        for (const id in infoWindowMap) {
            if (infoWindowMap.hasOwnProperty(id) && id !== data.id) {
                infoWindowMap[id].close();
            }
        }

        // Reset all marker icons
        for (let i = 0; i < markerList.length; i++) {
            if (i !== markerList.indexOf(targetMarker)) {
                // markerList[i].setIcon(iconSub);
                fadeInMarkerIcon(markerList[i], iconSub);
            }
        }
        if (targetMarker) {
            // Verify that the targetMarker has a valid position
            if (!targetMarker.getPosition || typeof targetMarker.getPosition !== "function") {
                console.error("targetMarker does not have a valid getPosition method");
                return;
            }

            let position = targetMarker.getPosition();
            if (!position) {
                console.error("targetMarker position is invalid:", position);
                return;
            }

            try {
                fadeInMarkerIcon(targetMarker, iconMain);
            } catch (error) {
                console.error("Error setting marker icon:", error);
                return;
            }

            selectedMarker = targetMarker;

            try {
                map.panTo(position);
            } catch (error) {
                console.error("Error panning to marker position:", error);
                return;
            }

            let newZoomLevel = initZoomLevel * 1.1;

            if (newZoomLevel > 12) {
                newZoomLevel = 12;
            } else if (newZoomLevel < 5) {
                newZoomLevel = 5;
            }

            try {
                map.setZoom(newZoomLevel);
            } catch (error) {
                console.error("Error setting map zoom level:", error);
            }
        } else {
            console.error(`Marker not found for property ID: ${data.id}`);
            return;
            // Exit the function if the marker is not found
        }

        if (infoWindow) {
            setTimeout( () => {
                if (!targetMarker.getPosition) {
                    console.error("targetMarker does not have a valid position");
                    return;
                }
                if (!map) {
                    console.error("Map object is not initialized");
                    return;
                }

                infoWindow.setZIndex(1000);
                // Ensure the infoWindow has a higher zIndex
                infoWindow.open(map, targetMarker);
            }
            , 500);
        } else {
            console.error(`InfoWindow not found for property ID: ${data.id}`);
        }
    }
    ;
    function fadeInMarkerIcon(marker, newIcon) {
        let targetOpacity = 1;
        // Desired final opacity (fully visible)
        let currentOpacity = marker.getOpacity() || 0;
        // Get current opacity (default 0)

        let fadeInterval = setInterval( () => {
            currentOpacity += 0.1;
            // Adjust fade step (smaller value for slower fade)
            if (currentOpacity >= targetOpacity) {
                currentOpacity = targetOpacity;
                clearInterval(fadeInterval);
                marker.setIcon(newIcon);
            }
            marker.setOpacity(currentOpacity);
        }
        , 50);
        // Adjust interval for fade speed (lower value for faster fade)
    }

    function fadeOutMarkerIcon(marker, newIcon) {
        let currentOpacity = marker.getOpacity() || 1;
        // Get current opacity (default 1)
        let fadeInterval = setInterval( () => {
            currentOpacity -= 0.1;
            // Adjust fade step (smaller value for slower fade)
            if (currentOpacity <= 0) {
                currentOpacity = 0;
                clearInterval(fadeInterval);
                marker.setIcon(newIcon);
            }
            marker.setOpacity(currentOpacity);
        }
        , 50);
        // Adjust interval for fade speed (lower value for faster fade)
    }

    function isValidLatLng(lat, lng) {
        if (lat < -90 || lat > 90 || lng < -180 || lng > 180) {
            // console.log(`Invalid coordinates: (${lat}, ${lng})`);
            return false;
        }
        return true;
    }

    function setMapStyle() {
        stylingArray = [{
            featureType: "administrative.land_parcel",
            elementType: "labels",
            stylers: [{
                visibility: "off",
            }, ],
        }, {
            featureType: "poi",
            elementType: "labels.text",
            stylers: [{
                visibility: "off",
            }, ],
        }, {
            featureType: "poi.business",
            stylers: [{
                visibility: "off",
            }, ],
        }, {
            featureType: "poi.park",
            elementType: "labels.text",
            stylers: [{
                visibility: "off",
            }, ],
        }, {
            featureType: "road.arterial",
            elementType: "labels",
            stylers: [{
                visibility: "off",
            }, ],
        }, {
            featureType: "road.highway",
            elementType: "labels",
            stylers: [{
                visibility: "off",
            }, ],
        }, {
            featureType: "road.local",
            stylers: [{
                visibility: "off",
            }, ],
        }, {
            featureType: "road.local",
            elementType: "labels",
            stylers: [{
                visibility: "off",
            }, ],
        }, ];
        return stylingArray;
    }

    function setContentString(data) {
        try {
            let name = "Asset Name";
            let imagePath = `https://pfsapp.kasikornbank.com/pfs-frontend-api/property-images`;
            let image = "/SiteCollectionDocuments/assets/PFS2022/image/default_thumbnail.jpg";
            let location = `Asset location`;
            let finalPrice = 0;
            let formatFinalPrice = 0;
            let hasOldPrice = false;
            let formatSellPrice = 0;
            let path = `/th/propertyforsale/`;

            let typeNameArr = data.PropertyTypeName.split(" ");

            name = data.VillageTH && data.VillageTH.length > 1 ? data.VillageTH : typeNameArr[1];

            if (data.PropertyMediaes.length > 0 && data.PropertyMediaes[0].MediaPath) {
                image = imagePath + `${data.PropertyMediaes[0].MediaPath}`;
            }
            if (data.PropertyID) {
                path = `/th/propertyforsale/detail/${data.PropertyID}.html`;
            }

            location = `${data.AmphurName}, ${data.ProvinceName}`;
            finalPrice = data.PromotionPrice || data.AdjustPrice || data.SellPrice;
            formatFinalPrice = numberFormat(finalPrice);
            hasOldPrice = parseInt(data.SellPrice) > 0 && parseInt(data.PromotionPrice) > 0;
            formatSellPrice = numberFormat(data.SellPrice) ? numberFormat(data.SellPrice) : 0;

            return `
          <div class="map-btn-wrapper d-none d-lg-block">
              <button class="more-filter-btn map" aria-label="Close">
                  <img src="/SiteCollectionDocuments/assets/PFS2022/pages/search/img/close-filter.svg" />
              </button>
          </div>
          
          <div id="infowindow-content" class="d-none d-lg-block">
              <div class="md-thumbnail-slide">
                  <div class="md-thumbnail-img">
                      <img src="${image}" alt="asset" />
                  </div>
                  <div class="md-thumbnail-detail">
                      <div class="md-thumbnail-top">
                        <h3 class="asset-title"><a href="${path}" target="_blank" data-kbct="item_click" data-kblb="map_item_detail" data-kbgp="search_map" data-kbid="${data.PropertyID}" >${name}</a></h3>
                        <div class="location mb-1">
                            <i class="ic-npa ic-npa-icon-pin"></i>
                            <p>${location}</p>
                        </div>
                      </div>
                      <div class="map-detail-prop">
                          ${data.PromotionPrice ? '<div class="special-price">ราคาพิเศษ</div>' : "<div></div>"}
                          ${data.AdjustPrice ? '<div class="adjust-price">ราคาลดลงเหลือ</div>' : "<div></div>"}

                          <div>
                              <p class=${data.PromotionPrice ? "special-price" : ""}>${formatFinalPrice} <span>บาท</span></p>
                              ${hasOldPrice ? `<p class="old-price">${formatSellPrice} บาท</p>` : ``}
                          </div>
                      </div>
                  </div>
              </div>
          </div>
          <a href="${path}"">
          <div id="infowindow-content-m" class="map-balloon-mobile d-block d-lg-none">
              ดูรายละเอียดเพิ่มเติม
          </div>
          </a>
          `;
        } catch (error) {
            console.error("Error creating content string:", error.message);
            return `<div class="error">Data is incomplete or invalid</div>`;
        }
    }

    function getZoom(locations) {
        let latitudes = locations.map( (loc) => loc.lat);
        let longitudes = locations.map( (loc) => loc.lng);

        let maxLatDiff = Math.max(...latitudes) - Math.min(...latitudes);
        let maxLngDiff = Math.max(...longitudes) - Math.min(...longitudes);
        let maxDiff = Math.max(maxLatDiff, maxLngDiff);

        // Define a scale based on your desired zoom for coverage area
        let zoomScale = 0.001;
        // Adjust this value to achieve the desired zoom level

        let zoom = Math.log(1 / (maxDiff * zoomScale)) / Math.LN2;

        return Math.ceil(zoom);
    }
    const btnExpandMap = document.querySelector("#btn-expand-map");
    const boxList = document.querySelector(".map-list-properties");
    const goTolistBtn = document.querySelector("#goTolist");
    btnExpandMap.addEventListener("click", function() {
        btnExpandMap.classList.toggle("go-to-expand");
        boxList.classList.toggle("hide");

        // if (windowWidth >= 1024) {
        if (btnExpandMap.classList.contains("go-to-expand")) {
            goTolistBtn.classList.remove("active");
        } else {
            goTolistBtn.classList.add("active");
        }
        // }
    });

    function getPropertyMap(payload, requestFetch=true) {
        $(".map-container .g-load-div").removeClass("hide");
        $("#map-lg").addClass("d-none");
        $(".map-list-properties").addClass("d-none");
        $(".map-wrapper").addClass("d-none");

        const allGContentNavMap = document.querySelectorAll(`.g-tab-list`);

        const gContentNavMap = document.querySelector(`.g-tab-list[data-tab='${tabActive}']`);

        let fetchedData = getStoredData("npa_fetchedData");

        allGContentNavMap.forEach( (item) => {
            item.classList.remove("active");
        }
        );
        gContentNavMap.classList.add("active");

        if (fetchedData.length > 0 && requestFetch === false) {
            // console.log("render map by fetchdata");
            let htmlMap = "";

            let setDataMap = {};
            let setLocations = [];
            let resData = getSessionDataObj("npa_fetchedData");
            let data = resData;
            let items = data && data.items;
            let fetchedMapID = getStoredData("npa_mapItemID");
            items.forEach(function(v, i) {
                htmlMap += renderSlideMap(v, setDataMap, setLocations);
            });
            initAllMap(setLocations, items);
            handleMapDOM(true);
            renderMaps(htmlMap, true, TotalRows[tabActive]);
            activeSelectedItem(fetchedMapID);
            // }
        } else {
            console.log("DDD 3")
            $.ajax({
                url: URL,
                type: "POST",
                data: JSON.stringify(payload),
                contentType: "application/json",
                success: function(result) {
                    let htmlMap = "";
                    TotalRows[tabActive] = JSON.parse(result.d).Data?.TotalRows || 0;
                    if (result && TotalRows[tabActive]) {
                        // saveToSession("npa_fetchedData", result);
                        appendToSession("npa_fetchedData", result);
                        let resData = JSON.parse(result.d);
                        let data = resData && resData.Data;
                        let items = data && data.Items;
                        let setDataMap = {};
                        let setLocations = [];

                        writeJSONSchema(result, tabActive);

                        let metaObj = addDataLayerMeta(items);
                        pushDataLayer(metaObj);

                        items.forEach(function(v, i) {
                            htmlMap += renderSlideMap(v, setDataMap, setLocations);
                        });
                        initAllMap(setLocations, items);
                        renderMaps(htmlMap, true, TotalRows[tabActive]);
                        handleMapDOM(true);

                        // toggle first asset after initAllMap
                        let firstElementID = items[0].PropertyID;
                        const defaultAsset = document.querySelector(`a[data-id="${firstElementID}"]`);
                        defaultAsset.click();
                    } else {
                        html = "";
                        handleMapDOM(false);
                    }
                },
                error: function(jqXHR, exception) {// console.log("jqXHR =====> ", jqXHR);
                },
            });
        }
    }

    function activeSelectedItem(id) {
        if (!id) {
            // console.log("no fetched map id");
            return;
        }

        let mapSlideDOM = document.querySelector(`[data-id="${id}"]`);
        setTimeout( () => {
            mapSlideDOM.click();
        }
        , 300);
    }

    function handleMapDOM(condition) {
        if (condition) {
            $("#map-lg").removeClass("d-none");
            $(".map-list-properties").removeClass("d-none");
            $(".map-wrapper").removeClass("d-none");
            $(".map-container .g-load-div").addClass("d-none");

            $(".map-container .not-found").addClass("hide");
            //$("#goTolist").removeClass("d-none");
        } else {
            $("#map-lg").html("");
            $("#map-lg").removeClass("d-none");
            $(".map-container .not-found").removeClass("hide");
            $(".map-container .g-load-div").addClass("d-none");
            //$("#goTolist").addClass("d-none");
        }
    }

    function renderMaps(html, status, TotalRows) {
        document.querySelector(".map-list-properties .swiper-wrapper").innerHTML = html;
        document.querySelector(".search-toltal").innerHTML = TotalRows[tabActive] > 0 && TotalRows[tabActive] ? TotalRows.toLocaleString() : `หลากหลาย`;
        if (status) {
            onclickFavorite();
            handleJumpToMapClick();
            slideMap();
        }
    }

    function renderSlideMap(v, setDataMap, setLocations) {
        let propSplit = v.PropertyTypeName ? v.PropertyTypeName.split(" ") : "";
        let PropertyTypeID = propSplit ? propSplit[0] : "";
        let PropertyTypeName = propSplit ? propSplit[1] : "";
        let nameProp = splitPropTypeFn(v.PropertyTypeName, PropertyTypeID, v.ProvinceName, v.VillageTH);

        let pathImage = "https://pfsapp.kasikornbank.com/pfs-frontend-api/property-images/";
        let img = "/SiteCollectionDocuments/assets/PFS2022/image/default_thumbnail.jpg";
        $.each(v.PropertyMediaes, function(idx) {
            let MediaType = v.PropertyMediaes[idx] && v.PropertyMediaes[idx].MediaType;
            if (MediaType && MediaType === "IMAGE-THUMBNAIL") {
                img = pathImage + v.PropertyMediaes[idx].MediaPath;
            }
        });

        let finalPrice = v.PromotionPrice || v.AdjustPrice || v.SellPrice;
        let formatFinalPrice = numberFormat(finalPrice);

        setDataMap.image = img;
        setDataMap.name = nameProp;
        setDataMap.id = v.PropertyID;
        setDataMap.location = v.AmphurName + " " + v.ProvinceName;
        setDataMap.spacialPrice = formatFinalPrice;
        setDataMap.PromotionPrice = finalPrice;
        setDataMap.SellPrice = v.SellPrice;

        setLocations.push({
            id: v.PropertyID,
            name: nameProp,
            lat: v.Latitude,
            lng: v.Longtitude,
        });

        let hasOldPrice = parseInt(v.SellPrice) > 0 && parseInt(finalPrice) > 0;

        let html = `  <div class="swiper-slide">
              <div data-lat="${v.Latitude}" data-long="${v.Longtitude}" data-id="${v.PropertyID}" data-set='${JSON.stringify(setDataMap)}' class="jump-to-map w-100">
              <div class="d-flex h-100">
                <div class="img-prop-map">
                  <img src="${img}" alt="${nameProp}"/>
                </div>
              <div class="map-thumbnail-detail">
                <div class="wrap-asset-title">
                    
                      <h3 class="asset-title">${nameProp}</h3>
                    

                </div>
                <div class="location">
                    <i class="ic-npa ic-npa-icon-pin"></i>
                    <p>${v.AmphurName} ${v.ProvinceName}</p>
                </div>
                <div class="wrap-end">
                ${v.PromotionPrice ? `<div class="badge-box">
                                    <div class="special-badge">
                                        <p>ราคาพิเศษ</p>
                                    </div>
                                  </div>` : `<div class="badge-box">
                    </div>`} 
                    <div class="price-box">
                      <p class=${v.PromotionPrice ? "spacial-price" : ""}>${formatFinalPrice} <span>บาท</span></p>
                      ${v.SellPrice > finalPrice && hasOldPrice ? `<p class="old-price">${numberFormat(v.SellPrice)} บาท</p>` : ``}
                    </div>
                </div>
              </div>
              </div>
              </div>
            </div>`;

        return html;
    }

    function lazyLoadImages() {
        const lazyImages = document.querySelectorAll("img.lazy");

        if ("IntersectionObserver"in window) {
            const lazyImageObserver = new IntersectionObserver( (entries, observer) => {
                entries.forEach( (entry) => {
                    if (entry.isIntersecting) {
                        const lazyImage = entry.target;
                        lazyImage.src = lazyImage.getAttribute("data-src");
                        lazyImage.removeAttribute("data-src");
                        lazyImage.classList.remove("lazy");
                        lazyImageObserver.unobserve(lazyImage);
                    }
                }
                );
            }
            );

            lazyImages.forEach( (lazyImage) => {
                lazyImageObserver.observe(lazyImage);
            }
            );
        } else {
            // Fallback for browsers without IntersectionObserver support
            const lazyLoad = () => {
                lazyImages.forEach( (img) => {
                    if (img.getBoundingClientRect().top < window.innerHeight && img.getBoundingClientRect().bottom > 0 && getComputedStyle(img).display !== "none") {
                        img.src = img.getAttribute("data-src");
                        img.removeAttribute("data-src");
                        img.classList.remove("lazy");
                    }
                }
                );

                if (lazyImages.length === 0) {
                    document.removeEventListener("scroll", lazyLoad);
                    window.removeEventListener("resize", lazyLoad);
                    window.removeEventListener("orientationchange", lazyLoad);
                }
            }
            ;
            document.addEventListener("scroll", lazyLoad);
            window.addEventListener("resize", lazyLoad);
            window.addEventListener("orientationchange", lazyLoad);
        }
    }

    function handleJumpToMapClick() {
        const jumpToMapElements = document.querySelectorAll(".jump-to-map");
        jumpToMapElements.forEach(function(element) {
            element.addEventListener("click", function(event) {
                event.preventDefault();

                jumpToMapElements.forEach(function(item) {
                    item.classList.remove("active");
                });
                element.classList.add("active");

                const swiperSlide = element.closest(".swiper-slide");
                if (swiperSlide) {
                    const swiperSlides = document.querySelectorAll(".swiper-slide");
                    swiperSlides.forEach(function(item) {
                        item.classList.remove("active");
                    });
                    swiperSlide.classList.add("active");
                }

                let latitude = element.getAttribute("data-lat");
                let longitude = element.getAttribute("data-long");
                let id = element.getAttribute("data-id");
                let dataSet = JSON.parse(element.getAttribute("data-set"));

                saveToSession("npa_mapItemID", id);

                selectPropertyMap(latitude, longitude, dataSet);
            });
        });
    }

    function slideMap() {
        let objSwiperMap = {
            slidesPerView: "auto",
            spaceBetween: 8,
            loop: false,
            centeredSlides: true,
            pagination: {
                el: ".swiper-pagination",
                type: "fraction",
            },
            navigation: {
                nextEl: ".swiper-button-next",
                prevEl: ".swiper-button-prev",
            },
            on: {
                slideChange: function() {
                    // Remove 'swiper-slide-active' class from all slides
                    document.querySelectorAll(".swiper-slide").forEach(function(slide) {
                        slide.classList.remove("active");
                    });
                    // Add 'active' class to the active slide
                    this.slides[this.activeIndex].classList.add("active");
                    setTimeout( () => {
                        document.querySelector(".map-properties-swiper .swiper-slide.active a").click();
                    }
                    , 500);
                },
            },
        };
        swiperMap = new Swiper(".map-properties-swiper",objSwiperMap);

        function destroySwiper() {
            if (swiperMap !== undefined && swiperMap !== null) {
                swiperMap.destroy(true, true);
                swiperMap = null;
            }
        }

        window.addEventListener("resize", function() {
            if (window.innerWidth >= 1024) {
                destroySwiper();
            } else {
                if (swiperMap === null) {
                    swiperMap = new Swiper(".map-properties-swiper",objSwiperMap);
                }
            }
        });

        if (window.innerWidth >= 1024) {
            destroySwiper();
        }
    }

    //########################## End Google map ###################################

    //########################## Render Assets ###################################

    function getSaleTypeTag(sourceSaleType) {
        const saleTypeTags = {
            kbank: "",
            partner: `<div class="tag partner">
                <i class="ic-npa ic-npa-icon-partnershipbadge"></i>
                <span>ทรัพย์ผู้ขาย</span>
              </div>`,
            bank: `<div class="tag wait-for-sale">
              <i class="ic-npa ic-npa-icon-propertywaitsale-badge"></i>
              <span>ทรัพย์ฝากขาย</span>
            </div>`,
            npl: `<div class="tag wait-for-sale">
              <i class="ic-npa ic-npa-icon-propertywaitsale-badge"></i>
              <span>ทรัพย์ฝากขาย</span>
            </div>`,
        };
        let other = ``;

        return saleTypeTags[sourceSaleType.toLocaleLowerCase()] || other;
    }

    function getProperty(dataTab, tab, requestFetch=true, callback, extraTab) {
        saveToSession("npa_payload", dataTab);

        let sessionActiveTab = getStoredData("npa_activeTab");
        clearActiveTab();
        if (sessionActiveTab.length > 0) {
            console.log(sessionActiveTab)
            manualActiveTab(sessionActiveTab);
        }

        let assetSwiperElement = document.querySelector(`.g-content.${tab} .assets-swiper`);

        // Check if the data is already stored in sessionStorage
        let fetchedData = getStoredData("npa_fetchedData");
        console.log('getProperty() fired')

        // ***Temporarily turn off sessionStorage condition due to corrupted data processing
        if (/* fetchedData.length > 0 && requestFetch ===  */false) {
            // If data exists, process it
            TotalRows[tab] = JSON.parse(fetchedData[0].d).Data.TotalRows || 0;
            /* if(!TotalRows[tab]) {
            } */

            let resData = getSessionDataObj("npa_fetchedData");
            let data = resData && resData.items || [];
            let items = data

            let html = "";
            if (data && TotalRows[tab] > 0) {
                let metaObj = addDataLayerMeta(items);
                pushDataLayer(metaObj);

                html = renderAssets(items);
                callback(html, TotalRows[tab]);
                handleTab(tab, TotalRows[tab], TotalRows[tab] > 0 ? true : false);
                initPropertySwiper();
                addDataLayerSearch(objDisplayValue, "found");
                console.log(`----- Condition 1 -----`);
            } else {
                callback(html, TotalRows[extraTab ?? tab]);
                handleTab(tab, TotalRows[tab ?? tab], false);
                addDataLayerSearch(objDisplayValue, "not_found");
                console.log(`----- Condition 2 -----`, items, resData, tab, TotalRows);
            }
            onclickFavorite();
            isClearSearch = false;
        } else {
            // If no data, make the AJAX call
            console.log('NPA Source URL :', URL)
            console.log("- DDD 4 -");
            console.log(dataTab)

            console.log("Check Loading >>> "+_checkIsLoading);
            if(_checkIsLoading) return false;
            _checkIsLoading = true;
            $.ajax({
                url: URL,
                type: "POST",
                data: JSON.stringify(dataTab),
                contentType: "application/json",
                success: function(result) {
                    _checkIsLoading = false;
                    // console.log(">>>>>> ajax called");
                    console.log("SSS 1 >> ");
                    console.log("payload ----> ");
                    console.log(JSON.stringify(dataTab))
                    console.log("result.d", JSON.parse(result.d));

                    writeJSONSchema(result, tab);
                    TotalRows[tab] = JSON.parse(result?.d)?.Data?.TotalRows || 0;

                    console.log(TotalRows)
                    // console.log("TotalRows :", TotalRows);
                    // console.log("TotalRows[tab] :", TotalRows[tab]);

                    appendToSession("npa_fetchedData", result);

                    let resData = getSessionDataObj("npa_fetchedData");
                    let items = resData && resData.items;

                    let html = "";
                    console.log('getProperty extraTab(', extraTab, TotalRows[tab], true)
                    if (items && TotalRows[tab] > 0) {
                        let metaObj = addDataLayerMeta(items);
                        pushDataLayer(metaObj);
                        html = renderAssets(items);
                        callback(html, TotalRows[tab]);
                        handleTab(extraTab ?? tab, TotalRows[tab], true);
                        initPropertySwiper();
                        addDataLayerSearch(objDisplayValue, "found");
                        console.log(`----- Condition 3 -----`, tab, TotalRows[tab], true);
                    } else {
                        // console.log(`----- No data -----`);
                        callback(html, TotalRows[tab]);
                        handleTab(extraTab ?? tab, TotalRows[tab], false);
                        addDataLayerSearch(objDisplayValue, "not_found");
                        console.log(`----- Condition 4 -----`, tab, TotalRows[tab], false);
                    }
                    onclickFavorite();
                    isClearSearch = false;

                    resumeScroll()

                },
                error: function(jqXHR, exception) {
                    _checkIsLoading = false;
                    // loaderElement.classList.remove("hide");
                    console.log("NPA Error Report : jqXHR =====> ", jqXHR);
                },
            });
        }
    }

    function resumeScroll() {
        // If a scroll position was saved, scroll to that position
        if (savedPosition !== null) {
            console.log('savedPosition : ', savedPosition)
            setTimeout( () => window.scrollTo(0, parseInt(savedPosition)), 2000);
        }
    }

    function clearActiveTab() {
        $(".g-tab-list").removeClass("active");
        $(".g-content").removeClass("active");
    }

    function manualActiveTab(tab) {
        $(`.g-tab-list[data-tab="${tab}"]`).addClass("active");
        $(`.g-content.${tab}`).addClass("active");
    }

    // Change tab but not load its content
    function handleTab(tab, rowNum, condition) {
        const activeTabContentElm = document.querySelector(`.g-content.active`);
        const tabContentElm = document.querySelector(`.g-content.${tab}`);
        const tabNotFoundElm = document.querySelector(`.g-content.${tab} .not-found`);
        updateTabNumTotal(tab, rowNum);

        if (activeTabContentElm) {
            activeTabContentElm.classList.remove("active");
        }
        // Condition = Found or not : TRUE/FALSE
        if (condition) {
            console.log('handleTab() : Found')
            tabNotFoundElm.classList.add("hide");
        } else {
            console.log('handleTab() : Not found')
            tabNotFoundElm.classList.remove("hide");
        }

        tabContentElm.classList.add("active");
    }

    function splitPropTypeFn(PropertyTypeName, PropertyTypeID, ProvinceName, VillageTH) {
        let splitPropType = PropertyTypeName.substring(PropertyTypeName.lastIndexOf(" ") + 1, PropertyTypeName.length);

        if (PropertyTypeID == "01") {
            splitPropType = "ที่ดิน";
        }

        let fullPropTypeName = splitPropType + " " + ProvinceName;
        let nameProp = VillageTH === "-" || VillageTH == null || VillageTH == "" ? fullPropTypeName : VillageTH;
        return nameProp;
    }

    function updateTabNumTotal(tab, num) {
        let numHtml
        const tabNumTotalElm = document.querySelectorAll(".num-total");

        if (isSearch) {
            if (tab !== "PromotionProperties") {
                tab = "AllProperties";
            }
        }
        if (typeof num !== 'number') {
            numHtml = '\&nbsp\;';
            tabNumTotalElm.forEach( (e, i) => {
                e.classList.add('loading')
                e.innerText = numHtml
            }
            )
        } else {
            numHtml = Number(num).toLocaleString();
            tabNumTotalElm.forEach( (e, i) => {
                e.classList.remove('loading')
                e.innerText = numHtml
            }
            )
        }
    }

    function renderAssets(items, typeExtra) {
        let html = "";
        items.forEach(function(v, i) {
            const propSplit = v.PropertyTypeName ? v.PropertyTypeName.split(" ") : "";
            const PropertyTypeID = propSplit ? propSplit[0] : "";
            const PropertyTypeName = propSplit ? propSplit[1] : "";
            const nameProp = splitPropTypeFn(v.PropertyTypeName, PropertyTypeID, v.ProvinceName, v.VillageTH);
            let hasArea = getArea(v) ? true : false;
            let unitProp = hasArea ? getArea(v).unit : "";
            let sizeProp = hasArea ? getArea(v).value : 0;

            let pathImage = "https://pfsapp.kasikornbank.com/pfs-frontend-api/property-images";
            let img = "/SiteCollectionDocuments/assets/PFS2022/image/default_thumbnail.jpg";

            let finalPrice = v.PromotionPrice || v.AdjustPrice || v.SellPrice || 0;
            let isPromotion = v.PromotionPrice ? true : false;
            let formatFinalPrice = numberFormat(finalPrice);
            let hasAI = v.AIFlag ? true : false;
            let promotionName = v.PromotionName;

            let reserveClass = v.IsReserve ? ' is-reserved-thumb' : '';
            let soldoutClass = v.IsSoldOut ? ' is-soldout-thumb' : '';
            //   let soldoutClass = !v.IsSoldOut ? ' is-soldout-thumb' : ''; // หากเงื่อนไข false
            let extraClass = reserveClass + soldoutClass;

            // console.log({id: v.PropertyID,content: v})

            html += `<li class="item">`;

            html += `<div class="md-thumbnail-slide ${v.SourceSaleType.toLocaleLowerCase() === "partner" ? `partner` : ``}">
        <a href="/th/propertyforsale/detail/${v.PropertyID}.html" target="_blank" class="result-img md-thumbnail-img"
            title="ทรัพย์แนะนำ-${nameProp}"
            data-kbct="link_click"
            data-kblb="${kblbTab}-link_photo"
            data-kbgp="content_card"
            data-kbid="${v.PropertyID}"
            data-kbsc="recommend_property"
            
            data-kbpo="${i}"
            >`;
            if (typeExtra === 'renovate') {
                html += `<div class="npa-logo-renovate">
                    <img src="/SiteCollectionDocuments/assets/PFS2022/pages/home/img/Renovate-icon-trim.png" alt="Logo renovate" loading="lazy">
                </div>`;
            }
            if (promotionName) {
                html += renderPromotionbar(promotionName);
            }
            if (v.SourceSaleType === "Partner") {
                html += `<div class="npa-logo-partner">
                          <img src="/SiteCollectionDocuments/assets/PFS2022/theme/img/logo/${v.SourceImageLogo}" alt="Logo partner">
                      </div>`;
            }

            html += `<div class="property-img-swiper${extraClass}">
                      <div class="swiper-wrapper">`;
            let countImg = 0;
            let totalImages = v.PropertyMediaes.filter( (media) => media.MediaType === "IMAGE-THUMBNAIL" || media.MediaType === "IMAGE-PC").length;

            if (v.PropertyMediaes.length > 0) {
                $.each(v.PropertyMediaes, function(idx) {
                    let MediaType = v.PropertyMediaes[idx] && v.PropertyMediaes[idx].MediaType;

                    if (MediaType && (MediaType === "IMAGE-THUMBNAIL" || MediaType === "IMAGE-PC")) {
                        countImg++;
                        img = pathImage + v.PropertyMediaes[idx].MediaPath;
                        if (countImg <= 4) {
                            html += `<div class="swiper-slide">`;
                            if (countImg >= totalImages || countImg === 4) {
                                html += `<div class="hover">
                                  <div class="inner">
                                      <div class="icon">
                                          <img src="/SiteCollectionDocuments/assets/PFS2022/theme/img/icon/npa-icon-moreimg.svg" alt="ดูเพิ่มเติม">
                                      </div>
                                      <span class="txt">ดูเพิ่มเติม</span>
                                  </div>
                                </div>`;
                            }
                            html += `<div class="property-img-inner">
                                    <img  data-src="${img}" class="swiper-lazy opacity-0" alt="${nameProp}" onload="this.classList.remove('opacity-0');"/>
                                    <div class="g-loader"></div>
                                </div>
                              </div>`;
                        }
                    }
                });
            } else {
                html += `<div class="swiper-slide">
                      <div class="property-img-inner">
                            <img  data-src="${img}" class="swiper-lazy" alt="${nameProp}"/>
                            <div class="g-loader"></div>
                        </div>
                    </div>`;
            }

            html += `</div>
              <div class="swiper-button-next"></div>
              <div class="swiper-button-prev"></div>
              <div class="swiper-pagination ${countImg > 4 ? "swiper-pagination-limit" : ""}"></div>
          </div>
      </a>
      <div class="md-thumbnail-detail">
          <div class="wrapper-tag">
              <div class="asset-tag">
      ${v.IsNew ? `<div class="tag new">
                    <i class="ic-npa ic-npa-icon-new-badge"></i>
                    <span>NEW</span>
                </div>` : ``}
      ${v.IsHot ? ` <div class="tag hot">
                      <i class="ic-npa ic-npa-icon-hot-badge"></i>
                      <span>HOT</span>
                  </div>` : ``}
      ${v.PromotionPrice ? `<div class="tag promotion">
                              <i class="ic-npa ic-npa-icon-promotion-badge"></i>
                              <span>Promotion</span>
                            </div>` : ``}
      ${hasAI ? `<div class="ic-ai"><img src="/SiteCollectionDocuments/assets/PFS2022/theme/img/logo/Icon_AI-Decoration.png" alt="AI Decoration" loading="lazy"></div>` : ``}
      ${getSaleTypeTag(v.SourceSaleType)}
              </div>
          </div>
          <div class="wrap-asset-title result-text">
              <a href="/th/propertyforsale/detail/${v.PropertyID}.html" 
                target="_blank"
                data-kbct="link_click"
                data-kblb="${kblbTab}-link_title"
                data-kbgp="content_card"
                data-kbid="${v.PropertyID}"
                title="${nameProp}"
                data-kbsc="recommend_property"
                data-kbpo="${i}"
                                    <h3 class="asset-title">${nameProp}</h3>
                                </a>
                                <div class="icon-wrapper">
                                    <div class="box-favorite">
                                        <button role="button" class="property-favorite favorite-btn"
                                            data-kblb="${kblbTab}-favorite"
                                            data-id="${v.PropertyID}"
                                            data-kbct="click"
                                            data-kbgp="content_card"
                                            data-kbid="${v.PropertyID}"
                                            
                                            title="${nameProp}"
                                            data-kbsc="recommend_property"
                                            data-kbpo="${i}">
                                          <i class="ic-npa ic-npa-icon-like"></i>
                                        </button>
                                        <div class="tooltip-favorite">
                                            <button type="button" class="close-tooltip"></button>
                                            <span>กรุณากดยอมรับ <br> Cookie สำหรับ <br> การเพิ่มทรัพย์ถูกใจ</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="location">
                                <i class="ic-npa ic-npa-icon-pin"></i>
                                <p>${v.AmphurName} ${v.ProvinceName}</p>
                            </div>
                            <div class="wrap-address">
                                <p class="asset-address">${PropertyTypeName}</p>
                                <p class="asset-code">รหัส ${v.PropertyIDFormat}</p>
                            </div>
                            <div class="wrap-detail">
                                <div class="asset-room">
                                    ${v.Bedroom ? `<span>
                                                        <i class="ic-npa ic-npa-icon-bedroom"></i>
                                                        <span>${v.Bedroom}</span>
                                                    </span>` : ``}
                                    
                                    ${v.Bedroom && v.Bathroom ? `<span class="pipe"></span>` : ``}
                                    ${v.Bathroom ? `<span>
                                                        <i class="ic-npa ic-npa-icon-bathroom"></i>
                                                        <span>${v.Bathroom}</span>
                                                    </span>` : ``}
                                    
                                </div>
                                <div class="asset-area">
                                      ${hasArea ? `<i class="ic-npa ic-npa-icon-area"></i>
                                    <span>${sizeProp} ${unitProp}</span>` : ``}
                                    
                                </div>
                            </div>
                            <div class="wrap-price ${isPromotion ? `` : `c-black`}">
                                ${v.PromotionPrice ? `<div class="special-badge">
                                                        <p>ราคาพิเศษ</p>
                                                    </div>` : `<div></div>`} 
                                ${!v.PromotionPrice && v.AdjustPrice ? `<div class="adjust-badge">
                                          <p>ราคาลดลงเหลือ</p>
                                      </div>` : `<div></div>`} 
                                <div class="price">
                                    <p class="spacial-price">${formatFinalPrice} <span>บาท</span></p>
                                    ${finalPrice < v.SellPrice && v.SellPrice && v.SellPrice !== "-" ? `<p class="old-price">${numberFormat(v.SellPrice)} บาท</p>` : ``}
                                </div>
                            </div>
                        </div>
                    </div>`;
            html += `</li>`;
        });
        return html;
    }

    function renderPromotionbar(casename) {
        let html = "";
        switch (casename) {
        case "0_Fee_10Yrs":
            html = `<div class="npa-0per">
      <p class="f-13"><img src="/SiteCollectionDocuments/assets/PFS2022/pages/home/img/npa-0percent.png"><strong>พิเศษ!</strong> สินเชื่อดอกเบี้ย <strong class="f-16">0%</strong> 10 ปี</p>
    </div>`;
            break;
        case "0_Fee_3Yrs":
            html = `<div class="npa-0per">
        <p class="f-13"><img src="/SiteCollectionDocuments/assets/PFS2022/pages/home/img/npa-0percent.png"><strong>พิเศษ!</strong> สินเชื่อดอกเบี้ย <strong class="f-16">0%</strong> 3 ปี</p>
      </div>`;
            break;

        default:
            html = "";
            break;
        }
        return html;
    }

    // Load tab content when switching tab
    function getContentTab(dataTab, load, clear) {
        console.log(".... Load Content TAB ....")
        saveToSession("npa_activeTab", dataTab);
        const filteredObj = Object.fromEntries(Object.entries(loadMorePage).filter( ([key,value]) => key === tabActive));
        saveToSession("npa_loadMorePage", filteredObj);

        let loadMoreElement = document.querySelector(".load-" + dataTab + " .btn");
        let loaderContentElement = document.querySelector(`.g-content.${dataTab} .g-load-div`);
        let loaderLoadMoreElement = document.querySelector(`.load-${dataTab} .g-load-div`);
        console.info(loaderLoadMoreElement);
        console.log("getContentTab() ", dataTab, load);
        let countTimeLoad = 0;

        console.log("MNX 2")
        let payload = {
            filter: {
                CurrentPageIndex: load[dataTab],
                PageSize: perLoad,
                SearchPurposes: haveAiParam ? [dataTab, 'HaveAi'] : [dataTab]
                //Ordering: "New",
            },
        };

        // Peace Edit
        if(sessionStorage.getItem("npa_search") != null){
           payload.filter.Search = JSON.parse(sessionStorage.getItem("npa_search")).keyword;
        }

        if (!load[dataTab]) {
            load[dataTab] = 1;
        }

        let amount = load[dataTab] * perLoad;
        tabActive = dataTab;

        if (dataTab !== 'renovate') {
            
            if (load[dataTab] == 1) {
                loaderContentElement.classList.remove("hide");
                console.log("RRR 1x")
                getProperty(payload, dataTab, (requestFetch = false), function(htmlProperty, TotalRows) {
                    countTimeLoad++;
                    const gContent = document.querySelector(".g-content." + dataTab + " .assets-swiper");

                    if (clear) {
                        gContent.innerHTML = "";
                    }

                    loaderContentElement.classList.add("hide");
                    if (loaderLoadMoreElement) {
                        loaderLoadMoreElement.classList.add("hide");
                    }

                    if (countTimeLoad <= perLoad) {
                        if (load[dataTab] === 1) {
                            gContent.innerHTML = "";
                            gContent.innerHTML = htmlProperty;
                            lazyLoadImages();
                        } else {
                            gContent.innerHTML += htmlProperty;
                            lazyLoadImages();
                        }

                        if (TotalRows > amount) {
                            if (loadMoreElement) {
                                loadMoreElement.classList.remove("hide");
                            }
                        } else {
                            if (loadMoreElement) {
                                loadMoreElement.classList.add("hide");
                            }
                        }
                    }
                    resumeScroll();
                });
            } else {
                if (loaderLoadMoreElement) {
                    loaderLoadMoreElement.classList.remove("hide");
                }
                getProperty(payload, dataTab, (requestFetch = false), function(htmlProperty, TotalRows) {
                    countTimeLoad++;
                    const gContent = document.querySelector(".g-content." + dataTab + " .assets-swiper");

                    if (clear) {
                        gContent.innerHTML = "";
                    }

                    loaderContentElement.classList.add("hide");
                    if (loaderLoadMoreElement) {
                        loaderLoadMoreElement.classList.add("hide");
                    }

                    if (countTimeLoad <= perLoad) {
                        if (load[dataTab] === 1) {
                            gContent.innerHTML = "";
                            gContent.innerHTML = htmlProperty;
                            lazyLoadImages();
                        } else {
                            gContent.innerHTML = "";
                            gContent.innerHTML += htmlProperty;
                            lazyLoadImages();
                        }

                        if (TotalRows > amount) {
                            if (loadMoreElement) {
                                loadMoreElement.classList.remove("hide");
                            }
                        } else {
                            if (loadMoreElement) {
                                loadMoreElement.classList.add("hide");
                            }
                        }
                    }
                });
            }
        } else {
            console.log('renovate DataTab fired');
            const callback = function(htmlProperty, TotalRows) {
                countTimeLoad++;
                const gContent = document.querySelector(".g-content." + dataTab + " .assets-swiper");

                loaderContentElement.classList.add("hide");
                if (loaderLoadMoreElement) {
                    loaderLoadMoreElement.classList.add("hide");
                }

                if (countTimeLoad <= perLoad) {
                    if (load[dataTab] === 1) {
                        gContent.innerHTML = "";
                        gContent.innerHTML = htmlProperty;
                        lazyLoadImages();
                    } else {
                        gContent.innerHTML += htmlProperty;
                        lazyLoadImages();
                    }

                    if (TotalRows > amount) {
                        if (loadMoreElement) {
                            loadMoreElement.classList.remove("hide");
                        }
                    } else {
                        if (loadMoreElement) {
                            loadMoreElement.classList.add("hide");
                        }
                    }
                }
            };
            const tabName = 'renovate';
            console.log("DDD 6")
            $.ajax({
                url: renovateURL,
                type: "GET",
                data: JSON.stringify(dataTab),
                contentType: "application/json",
                success: function(result) {
                    console.log(">>>>>> RENOVATE ajax called", result);

                    //writeJSONSchema(result, tab);
                    TotalRows[tabName] = result.length || 0;

                    appendToSession("npa_fetchedData", result);

                    let items = result;

                    let html = "";

                    if (items && TotalRows[tabName] > 0) {
                        let metaObj = addDataLayerMeta(items);
                        pushDataLayer(metaObj);
                        html = renderAssets(items, tabName);
                        callback(html, TotalRows[tabName]);
                        handleTab(tabName, TotalRows[tabName], true);
                        //document.querySelector(`.g-tab-list[data-tab="${tabName}"]`).click();
                        initPropertySwiper();
                        addDataLayerSearch(objDisplayValue, "found");
                        console.log(`----- Condition 5.1 -----`, tabName, TotalRows[tabName], true);
                    } else {
                        // console.log(`----- No data -----`);
                        callback(html, TotalRows[tabName]);
                        handleTab(tabName, TotalRows[tabName], false);
                        addDataLayerSearch(objDisplayValue, "not_found");
                        console.log(`----- Condition 5.2 -----`, tabName, TotalRows[tabName], false);
                    }
                    onclickFavorite();
                    isClearSearch = false;
                    resumeScroll();
                },
                error: function(jqXHR, exception) {
                    // loaderElement.classList.remove("hide");
                    console.log("NPA Error Report : jqXHR =====> ", jqXHR);
                },
            });
        }
    }

    function initPropertySwiper() {
        let propertyImgSwiper = new Swiper(".property-img-swiper",{
            slidesPerView: 1,
            spaceBetween: 0,
            centeredSlides: false,
            freeMode: false,
            loop: false,
            autoplay: false,
            navigation: {
                nextEl: ".swiper-button-next",
                prevEl: ".swiper-button-prev",
            },
            pagination: {
                el: ".swiper-pagination",
                type: "fraction",
            },
            lazy: {
                enabled: true,
                // checkInView:true,
                loadOnTransitionStart: true,
                loadPrevNext: true,
            },
            on: {
                init() {
                    let swiperContainers = document.querySelectorAll(".property-img-swiper");

                    swiperContainers.forEach( (container) => {
                        let isSlideOver = container.querySelector(".swiper-pagination-limit");
                        let paginationTotalElement = container.querySelector(".swiper-pagination-total");

                        if (isSlideOver) {
                            if (paginationTotalElement) {
                                paginationTotalElement.textContent = "4+";
                            }
                        }
                    }
                    );
                },
                slideChange() {
                    let swiperContainers = document.querySelectorAll(".property-img-swiper");

                    swiperContainers.forEach( (container) => {
                        let isSlideOverLimit = container.querySelector(".swiper-pagination-limit");
                        let paginationTotalElement = container.querySelector(".swiper-pagination-total");

                        if (isSlideOverLimit) {
                            if (paginationTotalElement) {
                                paginationTotalElement.textContent = "4+";
                            } else {
                                console.error("paginationTotalElement not found");
                            }
                        } else {
                            // Reset the pagination to the actual number of slides if needed
                            if (paginationTotalElement) {
                                let totalSlides = container.querySelectorAll(".swiper-slide").length;
                                paginationTotalElement.textContent = totalSlides;
                            }
                        }
                    }
                    );
                },
            },
        });
    }

    function hiddenMobileFooter(isHidden) {
        if (!document.querySelector("#react-app-login-footer"))
            return;
        if (window.innerWidth < 768 && isHidden) {
            document.querySelector("#react-app-login-footer").classList.add("d-none");
        } else {
            document.querySelector("#react-app-login-footer").classList.remove("d-none");
        }
    }

    const attachEventListeners = () => {
        document.querySelectorAll(".action .btn").forEach( (button) => {
            button.addEventListener("click", loadMore);
        }
        );
    }
    ;
    const loadMore = function() {
        console.log('loadMore()')
        const button = this;
        let dataTab = button.parentNode.getAttribute("data-tab");
        if (!loadMorePage[dataTab]) {
            loadMorePage[dataTab] = 1;
        }
        loadMorePage[dataTab] += 1;

        if (isSearch) {
            updateContent(dataTab, `.g-content.${dataTab} .assets-swiper`, loadMorePage[dataTab]);
        } else {
            // getContentTab(dataTab, loadMorePage);
            updateContent(dataTab, `.g-content.${dataTab} .assets-swiper`, loadMorePage[dataTab]);
        }
    };

    // Attach event listeners
    attachEventListeners();

    const tab = document.querySelectorAll(".g-tab-list");

    const updateTabs = () => {
        const isSearchStarted = exceptionParams.filter(e => e !== 'advancedsearch').some(e => window.location.search.includes(e))
        console.log('updateTabs() isSearchStarted', isSearchStarted)
        if (isSearchStarted) {
            tabDefaultElements.forEach( (tabDefault) => {
                tabDefault.style.display = "none";
            }
            );

            document.querySelectorAll(".g-tab-button").forEach( (tab) => {
                tab.style.display = "none";
            }
            );
            //clickDefaultTab()
        } else {
            tabDefaultElements.forEach( (tabDefault) => {
                tabDefault.style.display = "";
            }
            )
        }
    }

    const getParams = (url) => {
        const queryString = url.split('?')[1] || '';
        // Get the part after "?"
        const params = new URLSearchParams(queryString);
        const paramObj = {};

        for (const [key,value] of params) {
            paramObj[key] = value;
        }

        return paramObj;
    }

    const handleTabClick = (v) => {
        let dataTab = v.getAttribute("data-tab");
        tabActive = dataTab;

        console.log("TabClick: ", dataTab, tabActive)

        //clearStoredData("npa_activeTab");
        saveToSession("npa_activeTab", tabActive);

        document.querySelectorAll(`.g-content`).forEach( (e, i) => {
            e.classList.remove('active')
        }
        )
        document.querySelector(`.g-content.${dataTab}`).classList.add('active')

        console.log("TotalRows: ", TotalRows)
        console.log("IsSearch: ", isSearch)

        // Reset mode
        //goToList()

        if (!isSearch) {
            clearStoredData("npa_fetchedData");

            if (mode === "map") {
                hiddenMobileFooter();
                console.log("MNX 3")
                let payload = {
                    filter: {
                        CurrentPageIndex: 1,
                        PageSize: 20,
                        SearchPurposes: haveAiParam ? [dataTab, 'HaveAi'] : [tabActive]
                        //Ordering: "New",
                    },
                };
                if (!loadMorePage[dataTab]) {
                    getPropertyMap(payload, (requestFetch = true));
                } else {}
            } else {
                console.log('loadMorePage', loadMorePage)
                // console.log(dataTab)

                if (!loadMorePage[dataTab]) {
                    console.log("BBF 4")
                    getContentTab(tabActive, loadMorePage);
                } else {
                    console.log('--- Tab Clicked ---', dataTab, TotalRows[tabActive], TotalRows[tabActive] ? true : false)
                    handleTab(dataTab, TotalRows[tabActive], TotalRows[tabActive] ? true : false)
                }
            }
        } else {
            if (mode === "map") {
                payloadMapAdvanceSearch = JSON.parse(JSON.stringify(objPayload));
                payloadMapAdvanceSearch.filter.SearchPurposes = [tabActive];
                if (!loadMorePage[dataTab]) {
                    getPropertyMap(payloadMapAdvanceSearch, (requestFetch = true));
                }
            } else {
                console.log(">>> check list and search mode");
                if (!getContentTabException) {
                    console.log("BBF 5")
                    getContentTab(dataTab, loadMorePage);
                }
            }
        }
        updateTabNumTotal(tabActive, TotalRows[tabActive]);
        //if(!getContentTabException) {
        //}

        if (dataTab !== 'PromotionProperties') {
            updateTabs()
        }

        updateParam()
    }
    // Handle tab click
    tab.forEach( (v, i) => {
        v.addEventListener("click", () => {
            handleTabClick(v)
            console.log("Debug tab click -- Debug tab click -- Debug tab click -- Debug tab click")
        }
        );
    }
    );

    //########################## END Render Assets ###################################

    function numberFormat(num) {
        return num ? num.toLocaleString() : "-";
    }

    function addCommas(input) {
        const num = parseFloat(input.value.replace(/[^\d.-]/g, ""));
        if (!isNaN(num)) {
            const formattedNum = num.toLocaleString("en-US");
            input.value = formattedNum;
        } else {
            input.value = "";
        }
    }

    //########################## Advanced Search ###################################

    filterBtn.addEventListener("click", function() {
        // console.log('click')
        toggleSearch("open", 1);
    });
    searchCloseBtns.forEach( (btn) => {
        btn.addEventListener("click", function() {
            closeAdvanceSearch();
            toggleSearch("close", 2);
        });
    }
    );

    function initializeSelect2(element, placeholderText, headingText, isMultiSelect=false, sessionSearchKey) {
        element.select2({
            placeholder: placeholderText,
            allowClear: true,
            multiple: isMultiSelect,
        });

        //console.log('getSessionObj' , getSessionObj('npa_search')[sessionSearchKey])

        if (getSessionObj('npa_search')[sessionSearchKey]) {
            const option = $(element).find(`option[data-label='${getSessionObj('npa_search')[sessionSearchKey]}']`)
            const optionLabel = $(option).val()
            //console.log('option' , option)
            //console.log('optionLabel' , optionLabel)
            $(element).val(optionLabel).trigger('change')
        }

        element.on("select2:open", function(e) {
            openDropdown(headingText);
        });
        element.on("select2:close", function(e) {
            closeDropdown();
        });
    }

    // config select2 plugin
    initializeSelect2(propTypeElement, "ประเภททรัพย์", "เลือกประเภททรัพย์", false, 'propertyType');
    initializeSelect2(provinceElement, "จังหวัด", "เลือกจังหวัด", false, 'province');
    initializeSelect2(districtElement, "เขต/อำเภอ", "เลือกเขต/อำเภอ", false, 'district');
    initializeSelect2(priceElement, "ช่วงราคา", "เลือกช่วงราคา", false, 'Price');
    initializeSelect2(areaElement, "เนื้อที่", "เลือกเนื้อที่", false, 'Area');
    initializeSelect2(usableAreaElement, "พื้นที่ใช้สอย", "เลือกพื้นที่ใช้สอย", false, 'UsableArea');

    function saveSearchValue() {
        console.log($(propTypeElement).val())
        currentSearchSession = {
            keyword: $(propertyName)?.val() ?? '',
            propTypeElement: $(propTypeElement)?.val() ?? '',
            provinceElement: $(provinceElement)?.val() ?? '',
            priceElement: $(priceElement)?.val() ?? '',

        }
        if ($(districtElement).val() && $(districtElement).val()) {
            currentSearchSession['districtElement'] = $(districtElement).val() ?? ''
        }

    }
    function eraseSearchValue() {
        $(propertyName).val(''),
        $(propTypeElement).val('').trigger('change')
        $(provinceElement).val('').trigger('change')
        $(priceElement).val('').trigger('change')

        currentSearchSession = {}
    }
    function restoreSearchValue() {
        // console.log('currentSearchSession', currentSearchSession)

        $(propertyName).val(currentSearchSession['keyword']),
        $(propTypeElement).val(currentSearchSession.propTypeElement).trigger('change')
        $(provinceElement).val(currentSearchSession.provinceElement).trigger('change')
        $(priceElement).val(currentSearchSession.priceElement).trigger('change')

        if (currentSearchSession['districtElement']) {
            $(districtElement).val(currentSearchSession['districtElement']).trigger('change')
        }
    }

    //restoreSearchValue()

    function toggleSearch(state, num) {
        // console.log("toggleSearch : ", num);

        switch (state) {
        case "open":
            isAdvanceSearchOpen = true;
            advanceSearch.classList.add("active");
            searchDOM.classList.add("active");
            searchDropdownDOM.classList.add("active");
            searchActionDOM.classList.add("active");
            searcbMobileHeading.classList.add("active");
            propertyName.focus();
            getStationData();
            document.body.classList.add("no-scroll");
            saveSearchValue();
            break;

        case "close":
            advanceSearch.classList.remove("active");
            searchDOM.classList.remove("active");
            searchDropdownDOM.classList.remove("active");
            searchActionDOM.classList.remove("active");
            searcbMobileHeading.classList.remove("active");
            isAdvanceSearchOpen = false;
            document.body.classList.remove("no-scroll");
            restoreSearchValue();
            break;

        case "auto":
            advanceSearch.classList.toggle("active");
            searchDOM.classList.toggle("active");
            searchDropdownDOM.classList.toggle("active");
            searchActionDOM.classList.toggle("active");
            searcbMobileHeading.classList.toggle("active");
            isAdvanceSearchOpen = !isAdvanceSearchOpen;
            break;
        }
    }

    propertyName.addEventListener("keyup", function(e) {
        const value = e.target.value || '';
        objPayload.filter.Search = value;
        objDisplayValue["keyword"] = value;

        if (e.key === "Enter") {
            e.preventDefault()
            handleSearchClick(e)
        }
    });

    const labelSourceSaleTypes = (value) => {
        let label = "";
        if (value === "kbank") {
            label = "ทรัพย์ธนาคาร";
        } else if (value === "npl") {
            label = "ทรัพย์ฝากขาย";
        } else if (value === "Partner") {
            label = "ทรัพย์ผู้ขาย";
        } else {
            label = "ทรัพย์ฝากขาย";
        }
        return label;
    }
    ;
    let arrSourceSaleTypes = [];
    let arrLabelSourceSaleTypes = [];

    sourceSaleTypes.forEach(function(checkbox) {
        checkbox.addEventListener("change", function(event) {
            const changedCheckbox = event.target;
            const value = changedCheckbox.value;
            const isChecked = changedCheckbox.checked;
            if (isChecked) {
                arrSourceSaleTypes.includes(value) || arrSourceSaleTypes.push(value);
                arrLabelSourceSaleTypes.includes(labelSourceSaleTypes(value)) || arrLabelSourceSaleTypes.push(labelSourceSaleTypes(value));
            } else {
                arrSourceSaleTypes = arrSourceSaleTypes.filter( (item) => item !== value);
                arrLabelSourceSaleTypes = arrLabelSourceSaleTypes.filter( (item) => item !== labelSourceSaleTypes(value));
            }

            if (arrSourceSaleTypes.length > 0) {
                objPayload.filter.SourceSaletypes = arrSourceSaleTypes;
                objDisplayValue["SourceSaletypes"] = arrLabelSourceSaleTypes;
            } else {
                delete objPayload.filter.SourceSaletypes;
                delete objDisplayValue["SourceSaletypes"];
            }
        });
    });

    //-------------- Advanced Search : handle dropdown --------------
    function appendDropdownHeading(text) {
        if (window.innerWidth <= 576) {
            if ($(".dropdown-heading-container").length === 0) {
                const customTextbox = `
          <div class="dropdown-heading-container">
            <h4 class="dropdown-heading">${text}</h4>
            <button class="dropdown-heading-btn btn-close-dropdown">
            <i class="ic-npa ic-close"></i>
            </button>
          </div>`;
                $(".select2-container--open .select2-search--dropdown").before(customTextbox);

                $(".btn-close-dropdown").on("click", function() {
                    $(".select-field select").select2("close");
                });
            }
        }
    }
    function removeDropdownHeading() {
        $(".dropdown-heading-container").remove();
    }
    function openDropdown(headingText) {
        $(".select2-container--open").addClass("npa-select2-dropdown");
        $("body").addClass("no-scroll");
        appendDropdownHeading(headingText);
        $(".select2-container--open").css("pointer-events", "none");
        setTimeout(function() {
            $(".select2-container--open").css("pointer-events", "auto");
        }, 100);
    }
    function closeDropdown() {
        $(".select2-container--open").removeClass("npa-select2-dropdown");
        $(".select2-container").css("pointer-events", "auto");
        if (!isSearch) {
            $("body").removeClass("no-scroll");
        }
        removeDropdownHeading();
    }
    function populateDropdown(element, data) {
        let htmlOptions = "<option></option>";
        if (element === _provinceElement || element === _districtElement || element === _subDistrictElement || element === _transportationElement) {
            htmlOptions += `<option value="clear">ดูทั้งหมด</option>`;
        }
        if (element === _transportationElement) {
            console.log(">> init station dropdown");
            data.forEach(function(item) {
                htmlOptions += `<option value="${item.StationID}" title="${item.PlaceType}">${item.StationNameTH}</option>`;
            });
        } else {
            data.forEach(function(item) {
                htmlOptions += `<option value="${item.value}" data-label='${item.text}'>${item.text}</option>`;
            });
        }

        element.innerHTML = htmlOptions;
    }

    console.log(propertyData)
    populateDropdown(_provinceElement, provinces);
    populateDropdown(_propTypeElement, propertyData);
    populateDropdown(_usableAreaElement, usableAreaData);
    populateDropdown(_areaElement, areaData);
    populateDropdown(_priceElement, priceData);

    const getOptionValueByLabel = (label) => {
        const query = `option[data-label='${label}']`
        const value = $(query).attr('value')
        console.log(value)
        return value
    }
    ;

    provinceElement.on("select2:open", function(e) {
        $("input.select2-search__field").prop("placeholder", "ชื่อจังหวัด");
    });

    const handleProvinceElement = () => {
        const selectedValue = provinceElement.val();
        const selectedLabel = provinceElement.find("option:selected").text();

        console.log('provinces', provinces)
        console.log('selectedValue', selectedValue)

        if (selectedValue == "clear") {
            provinceElement.val(null).trigger("change");
            districtElement.val(null).trigger("change");
            objPayload.filter.Provinces = [];
            objDisplayValue["province"] = "";
            objPayload.filter.Amphurs = [];
            objDisplayValue["district"] = "";
            populateDropdown(_districtElement, []);
        } else if (selectedValue) {
            objPayload.filter.Provinces = [selectedValue];
            objDisplayValue["province"] = selectedLabel;
            objPersonalizedValue["personalizedData-province-filter"] = selectedValue;

            console.log(parseInt(selectedValue ?? currentParams.get('province')))

            const selectedProvince = provinces.find( (item) => item.value == parseInt(selectedValue ?? currentParams.get('province')));
            populateDropdown(_districtElement, selectedProvince.child);
            /* if (selectedProvince) {
                console.log('selectedProvince', selectedProvince)
                console.log('handleProvinceElement selectedProvince', selectedProvince)
                console.log('handleProvinceElement selectedProvince.child', selectedProvince.child)
            } else {
                populateDropdown(_districtElement, []);
            } */
        }

    }

    handleProvinceElement()

    $(provinceElement).on("change", () => handleProvinceElement());

    //district
    districtElement.on("select2:open", function(e) {
        $("input.select2-search__field").prop("placeholder", "ชื่อเขต/อำเภอ");
    });

    const handleDistrictElement = () => {
        const selectedValue = districtElement.val();
        const selectedLabel = districtElement.find("option:selected").text();
        if (selectedValue == "clear") {
            //districtElement.val(null).trigger("change");
            objPayload.filter.Amphurs = [];
            objDisplayValue["district"] = "";
        } else if (selectedValue) {
            //districtElement.val(selectedValue ?? currentParams.get('district')).trigger("change");
            objPayload.filter.Amphurs = [selectedValue];
            objDisplayValue["district"] = selectedLabel;
            console.log('handleDistrictElement selectedValue', selectedValue)
        }

        console.log('currentParams.get("district")', currentParams.get('district'))
    }

    handleDistrictElement()

    $(districtElement).on("change", () => handleDistrictElement());

    const handlePropTypeElement = () => {
        const selectedValue = $(propTypeElement).val();
        const selectedLabel = $(propTypeElement).find("option:selected").text();
        if (selectedValue == "clear") {
            propTypeElement.val(null).trigger("change");
            objPayload.filter.PropertyTypes = [];
            objDisplayValue["propertyType"] = "";
        } else if (selectedValue) {
            objPayload.filter.PropertyTypes = [selectedValue];
            objDisplayValue["propertyType"] = selectedLabel;
            objPersonalizedValue["personalizedData-property-type"] = selectedValue;
            // console.log(objPayload.filter);
            // console.log(objDisplayValue);
        }
    }
    handlePropTypeElement()
    $(propTypeElement).on("change", () => handlePropTypeElement());

    const handlePriceElement = () => {
        const selectedValue = $(priceElement).val();
        const selectedLabel = $(priceElement).find("option:selected").text();
        if (selectedValue == "clear") {
            priceElement.val(null).trigger("change");
            objPayload.filter.MinPrice = 0;
            objDisplayValue["Price"] = "";
        } else if (selectedValue) {
            // console.log(selectedValue);
            let valArr = selectedValue.split("-");
            objPayload.filter.MinPrice = parseInt(valArr[0] || 0);
            if(parseInt(valArr[1]) > 0){
                objPayload.filter.MaxPrice = parseInt(valArr[1] || 0);
            }else{
                objPayload.filter.MaxPrice = "";
            }

            objDisplayValue["Price"] = selectedLabel;
        }
    }

    handlePriceElement()

    $(priceElement).on("change", () => handlePriceElement());

    let arrPropertyType = [];
    let arrLabelPropertyType = [];
    let arrLabelPropertyTypeCode = [];
    let valueOther = ["19", "06", "07", "08", "11", "13", "14", "16", "17", "18", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "81", "83", "99", ];

    transportationElement.select2({
        placeholder: "สถานีใกล้เคียง",
        allowClear: true,
        templateResult: function(idioma) {
            if (idioma.title == "bts") {
                var $span = $("<span class='d-flex align-items-center justify-content-between'>" + idioma.text + "<img src='../../../../SiteCollectionDocuments/assets/theme/img/logo/bts.png' width='24'/></span>");
            } else if (idioma.title == "mrt") {
                var $span = $("<span class='d-flex align-items-center justify-content-between'>" + idioma.text + "<img src='../../../../SiteCollectionDocuments/assets/theme/img/logo/mrt.png' width='24'/></span>");
            } else {
                var $span = $("<span>" + idioma.text + "</span>");
            }
            return $span;
        },
        templateSelection: function(idioma) {
            if (idioma.id) {
                if (idioma.title == "bts") {
                    var $span = $("<span class='d-flex align-items-center justify-content-between'>" + idioma.text + "<img src='../../../../SiteCollectionDocuments/assets/theme/img/logo/bts.png' width='24' style='margin-right: 10px;'/></span>");
                } else {
                    var $span = $("<span class='d-flex align-items-center justify-content-between'>" + idioma.text + "<img src='../../../../SiteCollectionDocuments/assets/theme/img/logo/mrt.png' width='24' style='margin-right: 10px;'/></span>");
                }
            } else {
                var $span = $("<span>" + idioma.text + "</span>");
            }
            return $span;
        },
    });

    transportationElement.one("select2:open", function(e) {
        $("input.select2-search__field").prop("placeholder", "ชื่อสถานี");
    });

    areaElement.on("change", function(e) {
        let selectedValue = $(this).val();
        let selectedLabel = $(this).find("option:selected").text();

        if (selectedValue == "clear") {
            objDisplayValue["Area"] = "";
            delete objPayload.filter.MinArea;
            delete objPayload.filter.MaxArea;
        } else if (selectedValue) {
            let areaArr = selectedValue.split("-");
            let minArea = parseInt(areaArr[0]);
            let maxArea = parseInt(areaArr[1]);
            objPayload.filter.MinArea = minArea;
            objPayload.filter.MaxArea = maxArea;

            objDisplayValue["Area"] = selectedLabel;
        }
    });

    transportationElement.on("change", function(e) {
        let selectedStationValue = $(this).val();
        let selectedLabel = $(this).find("option:selected").text();
        let selectedStation;
        if (stationData && Array.isArray(stationData)) {
            selectedStation = stationData.find( (station) => station.StationID === selectedStationValue);
        }

        let NearbyMeters = 3000;
        let selectedStationLocation;
        if (selectedStation) {
            selectedStationLocation = {
                Latitude: selectedStation.Latitude,
                Longitude: selectedStation.Longitude,
            };
        }

        if (selectedStationValue == "clear") {
            delete objPayload.filter.Nearby;
            delete objPayload.filter.NearbyMeters;
            objDisplayValue["Nearby"] = "";
            objDisplayValue["Station"] = "";
        } else if (selectedStationValue) {
            objPayload.filter.Nearby = selectedStationLocation;
            objPayload.filter.NearbyMeters = NearbyMeters;
            objDisplayValue["Nearby"] = selectedStationLocation;
            objDisplayValue["Station"] = `${selectedStation.PlaceType.toUpperCase()} ${selectedStation.StationNameTH}`;
        }
    });

    bedRoomElement.forEach(function(checkbox) {
        checkbox.addEventListener("change", function(event) {
            let changedCheckbox = event.target;
            let value = changedCheckbox.value;
            if (value) {
                objPayload.filter.Bedroom = parseInt(value);
                objDisplayValue["bedroom"] = `ห้องนอน ${value} ห้อง`;
            } else {
                delete objPayload.filter.Bedroom;
                objDisplayValue["bedroom"] = "";
            }
        });
    });

    bathRoomElement.forEach(function(checkbox) {
        checkbox.addEventListener("change", function(event) {
            let changedCheckbox = event.target;
            let value = changedCheckbox.value;

            if (value) {
                objPayload.filter.Bathroom = parseInt(value);
                objDisplayValue["bathroom"] = `ห้องน้ำ ${value} ห้อง`;
            } else {
                delete objPayload.filter.Bathroom;
                objDisplayValue["bathroom"] = "";
            }
        });
    });

    aiCheckbox.addEventListener("change", function() {
        if (this.checked) {
            objPayload.filter.SearchPurposes = [tabActive, "HaveAi"];
            objDisplayValue["ai"] = "AI Decoration";
            haveAiParam = true
        } else {
            objPayload.filter.SearchPurposes = ["AllProperties"];
            objDisplayValue["ai"] = "";
            haveAiParam = false
        }
    });

    function setRangeDisplay(objName, label, min, max, unit) {
        if (!min && !max) {
            delete objDisplayValue[objName];
            return;
        }

        if (min) {
            objDisplayValue[objName] = `${label} ขั้นต่ำ ${numberFormat(min)} ${unit}` + (max ? ` - สูงสุด ${numberFormat(max)} ${unit}` : "");
        } else if (max) {
            if (max) {
                objDisplayValue[objName] = `${label} สูงสุด ${numberFormat(max)} ${unit}`;
            }
        }
        return objDisplayValue[objName];
    }

    function setpersonalizedDataBySearch() {
        let personalizedData = {};
        if (objPersonalizedValue["personalizedData-province-filter"]) {
            personalizedData.Provinces = [objPersonalizedValue["personalizedData-province-filter"], ];
        }
        if (objPersonalizedValue["personalizedData-property-type"]) {
            personalizedData.PropertyTypes = objPersonalizedValue["personalizedData-property-type"];
        }
        setPersonalizedData(personalizedData);
    }

    // Change tab content on search
    function updateContent(searchPurpose, selector, page, requestFetch=true, extraTab) {
        console.log("updateContent fired");
        // console.log(sessionPayload);
        if (sessionStorage.getItem("npa_search")) {
            let params = JSON.parse(sessionStorage.getItem("npa_search"));
            let sessionPayload = JSON.parse(sessionStorage.getItem("npa_payload"));
            console.log('params', params)

            params.PropertyTypes = params.propertyTypeCode;
            params.PropertyTypes = params.propertyTypeCode;

            objPayload = {
                ...sessionPayload,
            };
        }

        let obj = JSON.parse(JSON.stringify(objPayload));
        // console.log(obj);
        let loadMoreElement = document.querySelector(".load-" + searchPurpose + " .btn");
        let loaderContentElement = document.querySelector(`.g-content.${searchPurpose} .g-load-div`);
        let loaderLoadMoreElement = document.querySelector(`.load-${searchPurpose} .g-load-div`);

        obj.filter.CurrentPageIndex = page;

        //check on promotion on search case
        if (!isSearch) {
            obj.filter.SearchPurposes = [searchPurpose];
        } else if (searchPurpose === "PromotionProperties" && !obj?.filter?.SearchPurposes?.includes("PromotionProperties")) {
            obj.filter.SearchPurposes = ["PromotionProperties", searchPurpose];
        } else {
            obj.filter.SearchPurposes = ["AllProperties", searchPurpose];
        }

        if (objPayload.filter.SearchPurposes && objPayload.filter.SearchPurposes.includes('HaveAi')) {
            obj.filter.SearchPurposes.push('HaveAi')
        }

        let amount = page * perLoad;

        if (page <= 1) {
            loaderContentElement.classList.remove("hide");
        } else {
            loaderLoadMoreElement.classList.remove("hide");
        }

        const filteredObj = Object.fromEntries(Object.entries(loadMorePage).filter( ([key,value]) => key === tabActive));
        saveToSession("npa_loadMorePage", filteredObj);

        // Ensure getProperty is only called once by checking the flag

        console.log('extraTab', extraTab)
        if (!isPropertyFetched) {
            isPropertyFetched = true;
            console.log('PROPERTIES NOT FETCHED - obj : ', objPayload);
            // Set flag to true to avoid repeated calls
            console.log('obj', obj)
            console.log('searchPurpose', searchPurpose)
            console.log('requestFetch', requestFetch)

            console.log("XXF 1")
            getProperty(obj, searchPurpose, requestFetch, function(htmlProperty, TotalRows) {
                document.querySelector(selector).innerHTML = "";
                document.querySelector(selector).innerHTML = htmlProperty;

                lazyLoadImages();
                loaderContentElement.classList.add("hide");
                loaderLoadMoreElement.classList.add("hide");
                if (TotalRows > amount) {
                    loadMoreElement.classList.remove("hide");
                } else {
                    loadMoreElement.classList.add("hide");
                }
                // Reset the flag once the property fetching is done (if needed for future calls)
                isPropertyFetched = false;
            }, extraTab);
        }
    }

    function toggleAdvancedSearch(searchObject) {
        console.log("toggleAdvancedSearch");
        console.log(objPayload)
        if (Object.keys(searchObject).length < 1) {
            console.log("DDD 1")
            console.log('toggleAdvancedSearch() Empty search object')
            return;
        } else {
            console.log("DDD 2")
            console.log('toggleAdvancedSearch()', Object.keys(searchObject))
            clearStoredData("npa_fetchedData");
            clearSearchResult();
            clearJSONSchema();
            saveToSession("npa_search", searchObject);
            isSearch = true;

            setpersonalizedDataBySearch(searchObject);

            setRangeDisplay("rangePrice", "ช่วงราคา", minPriceDisplay, maxPriceDisplay, "บาท");
            setRangeDisplay("areaRange", "เนื้อที่", minAreaDisplay, maxAreaDisplay, "ตร.ว");
            setRangeDisplay("useableAreaRange", "พื้นที่ใช้สอย", minUseableAreaDisplay, maxUseableAreaDisplay, "ตร.ว");

            if (mode === "list") {
                // Call the function for both All and Promotion
                document.querySelector(".g-content.AllProperties .assets-swiper").innerHTML = "";

                saveToSession("npa_payload", objPayload);

                if (typeof objPayload.filter.SearchPurposes == "undefined") {
                    objPayload.filter.SearchPurposes = ["AllProperties"];
                }

                if (tabActive === 'PromotionProperties') {
                    //objPayload.filter.SearchPurposes = ["PromotionProperties"];
                    updateContent("PromotionProperties", ".g-content.PromotionProperties .assets-swiper", 1, (requestFetch = false), 'PromotionProperties');
                    document.querySelector(`[data-tab="PromotionProperties"]`).click();
                    updateTabNumTotal("PromotionProperties", TotalRows);
                } else {
                    //objPayload.filter.SearchPurposes = ["AllProperties"];
                    updateContent(objPayload.filter.SearchPurposes[0], ".g-content.AllProperties .assets-swiper", 1, (requestFetch = false), 'AllProperties');
                    document.querySelector(`[data-tab="AllProperties"]`).click();
                    updateTabNumTotal("AllProperties", TotalRows);
                }

                saveToSession("npa_payload", objPayload);

            } else {
                payloadMapAdvanceSearch = JSON.parse(JSON.stringify(objPayload));
                payloadMapAdvanceSearch.filter.SearchPurposes = [tabActive];

                getPropertyMap(payloadMapAdvanceSearch, (requestFetch = true));
            }
        }
    }

    // Display the search value in the input field
    function updateSearchInputDisplay(searchObject) {
        let displayValue = "";
        let displayKeys = ["keyword"];

        for (let key in searchObject) {
            if (Object.hasOwnProperty.call(searchObject, key)) {
                let value = searchObject[key];
                // Only include keys in the displayKeys array
                if (value !== "" && displayKeys.includes(key)) {
                    if (Array.isArray(value)) {
                        displayValue += value.join(", ") + ", ";
                    } else {
                        displayValue += value + ", ";
                    }
                }
            }
        }

        displayValue = displayValue.slice(0, -2);

        console.log("currentParams.get('keyword')", currentParams.get('keyword'))

        document.querySelector("#input-popup-search").value = currentParams.get('keyword') ?? '';
    }

    updateSearchInputDisplay(objDisplayValue);

    //Get PromotionProperties in List and Searching mode
    const PromotionPropertiesTab = document.querySelectorAll('[data-tab="PromotionProperties"]');
    const PromotionPropertiesTabContent = document.querySelector(".g-content.PromotionProperties .assets-swiper");

    PromotionPropertiesTab.forEach( (tab) => {
        tab.addEventListener("click", () => {
            if (objPayload.filter.SearchPurposes && !objPayload.filter.SearchPurposes.includes('PromotionProperties')) {//objPayload.filter.SearchPurposes = ["PromotionProperties", ...objPayload.filter.SearchPurposes];
            }
            saveToSession("npa_payload", objPayload);
            //Handle PromotionTab when no Promotions
            const notFoundPromotion = document.querySelector(".g-content.PromotionProperties .not-found-wrapper");
            notFoundPromotion.innerHTML = `<p>เตรียมพบกับโปรโมชันสุดพิเศษครั้งใหม่ เร็วนี้ๆ</p>`;

            // Handle PromotionTab when have Promotions
            if (isSearch) {
                if (PromotionPropertiesTabContent.innerHTML == "") {
                    clearStoredData("npa_fetchedData");
                    updateContent("PromotionProperties", ".g-content.PromotionProperties .assets-swiper", 1);
                    isShowPromotionOnSearch = false;
                } else {
                    if (!isShowPromotionOnSearch) {
                        clearAssets("PromotionProperties");
                        updateContent("PromotionProperties", ".g-content.PromotionProperties .assets-swiper", 1, (requestFetch = false));
                        isShowPromotionOnSearch = true;
                    } else {// console.log("promotion search has data");
                    }
                }
            }

            setTimeout( () => {
                $('.PromotionProperties .g-load-div').addClass('hide')
            }
            , 500)
        }
        );
    }
    );

    function clearSearchResult() {
        isShowPromotionOnSearch = false;
        clearAssets("AllProperties");
        clearAssets("PromotionProperties");
    }

    function handleSearchClick(e) {
        e && e.preventDefault();
        //TotalRows = {}
        if (typeof toggleAdvancedSearch === "function") {
            console.log(">>> start search");
            toggleAdvancedSearch(objDisplayValue);
            // console.log(objDisplayValue);
        }
        if (isAdvanceSearchOpen) {
            toggleSearch("close", 6);
        }
    }

    updateTabs();

    const clearTabNameParam = () => {
        const paramObj = getParams(window.location.href);
        delete paramObj['tabname'];
        const queryString = new URLSearchParams(paramObj).toString();
        window.history.pushState(null, '', '?' + queryString);
    }

    const updateParam = () => {

        const paramObj = getParams(window.location.href);

        if ($('#input-popup-search').val() && $('#input-popup-search').val() !== '' && $('#input-popup-search').val() !== 'clear') {
            paramObj['keyword'] = $('#input-popup-search').val()
        } else {
            delete paramObj['keyword']
        }

        if ($('#province-filter').val() && $('#province-filter').val() !== '' && $('#province-filter').val() !== 'clear') {
            paramObj['province'] = $('#province-filter').val()
        } else {
            delete paramObj['province']
        }

        if ($('#district-filter').val() && $('#district-filter').val() !== '' && $('#district-filter').val() !== 'clear') {
            paramObj['district'] = $('#district-filter').val()
        } else {
            delete paramObj['district']
        }

        if ($('#property-type-filter').val() && $('#property-type-filter').val() !== '' && $('#property-type-filter').val() !== 'clear') {
            paramObj['propertyType'] = $('#property-type-filter').val()
        } else {
            delete paramObj['propertyType']
        }

        if ($('#price-filter').val() && $('#price-filter') !== '' && $('#price-filter') !== 'clear') {
            paramObj['price'] = $('#price-filter').val()
        } else {
            delete paramObj['price']
        }

        if (haveAiParam) {
            paramObj['haveAi'] = true
        } else {
            delete paramObj['haveAi']
        }

        /* Get active tab param */
        const activeTab = document.querySelector('.g-tab-list.active')

        if (activeTab && activeTab.getAttribute('data-tab')) {
            const dataTab = activeTab.getAttribute('data-tab')
            paramObj['tabname'] = dataTab
        }

        const queryString = new URLSearchParams(paramObj).toString();

        if (queryString !== '') {
            window.history.pushState({}, '', '?' + queryString);
        } else {
            window.history.pushState({}, '', window.location.pathname);
        }
    }

    const searchHandlers = [searchProperty, searchPropertyAdvance];
    searchHandlers.forEach( (handler) => {
        if (handler) {
            handler.addEventListener("click", (e) => {
                saveSearchValue()
                handleSearchClick(e)
                clearTabNameParam()
                updateParam()
                if (tabActive !== 'PromotionProperties') {
                    updateTabs()
                }
            }
            );
        }
    }
    );

    const closeAdvanceSearch = () => {
        // Reset obj
        // console.log("closeAdvanceSearch");

        const noDeleteKeys = ["keyword", "province", "district", "propertyType", "Price", ];
        for (const key in objDisplayValue) {
            if (objDisplayValue.hasOwnProperty(key) && !noDeleteKeys.includes(key)) {
                delete objDisplayValue[key];
            }
        }

        // propertyName.value = "";
        // provinceElement.val(null).trigger("change");
        // districtElement.val(null).trigger("change");
        // priceElement.val(null).trigger("change");
        // propTypeElement.val(null).trigger("change");

        areaElement.val(null).trigger("change");
        usableAreaElement.val(null).trigger("change");
        transportationElement.val(null).trigger("change");

        areaDisplay = "";
        usableAreaDisplay = "";
        areaElement.value = "";

        bedRoomElement.forEach(function(radio) {
            radio.checked = false;
        });
        bathRoomElement.forEach(function(radio) {
            radio.checked = false;
        });
        aiCheckbox.checked = false;
    }
    ;
    const clearAdvanceSearch = () => {
        isClearSearch = true;
        clearSearchResult();
        //clearStoredData("npa_search");
        clearStoredData("npa_fetchedData");

        if (mode === "map") {
            console.log("MNX 4")
            let payload = {
                filter: {
                    CurrentPageIndex: 1,
                    PageSize: 20,
                    SearchPurposes: [tabActive]
                    //Ordering: "New",
                },
            };

            getPropertyMap(payload, (requestFetch = true));
        } else {
            // Clear old data before loading new content
            const gContents = document.querySelectorAll(".g-content .assets-swiper");
            gContents.forEach( (content) => {
                content.innerHTML = "";
            }
            );
            //Clear loadMorePage
            for (const key in loadMorePage) {
                delete loadMorePage[key];
            }
            // loadMorePage[tabActive] = 1;
            console.log("BBF 6")
            getContentTab(tabActive, loadMorePage);

            updateTabs()
        }

        // Reset obj
        objDisplayValue = {};

        for (const key in objDisplayValue) {
            // Important: Check if the property belongs to the object itself
            // (not inherited from the prototype chain) before deleting.
            if (objDisplayValue.hasOwnProperty(key)) {
                delete objDisplayValue[key];
            }
        }

        objPayload = {
            filter: {
                AllCurrentPageIndex: 1,
                CurrentPageIndex: 1,
                // Ordering: "Hot",
                PageSize: 20,
                propertyList: "newProperty",
            },
        };
        objPersonalizedValue = {};

        isSearch = false;

        tabDefaultElements.forEach( (tabDefault) => {
            tabDefault.style.display = "inline-block";
        }
        );

        document.querySelectorAll(".g-tab-button").forEach( (tab) => {
            tab.style.display = "block";
        }
        );

        arrSourceSaleTypes = [];
        arrLabelSourceSaleTypes = [];

        propertyName.value = "";
        sourceSaleTypes.forEach(function(checkbox) {
            checkbox.checked = false;
        });

        provinceElement.val(null).trigger("change");
        districtElement.val(null).trigger("change");
        subDistrictElement.val(null).trigger("change");
        areaElement.val(null).trigger("change");
        priceElement.val(null).trigger("change");
        usableAreaElement.val(null).trigger("change");
        transportationElement.val(null).trigger("change");
        propTypeElement.val(null).trigger("change");

        arrPropertyType = [];
        arrLabelPropertyType = [];

        areaDisplay = "";
        usableAreaDisplay = "";
        areaElement.value = "";

        bedRoomElement.forEach(function(radio) {
            radio.checked = false;
        });
        bathRoomElement.forEach(function(radio) {
            radio.checked = false;
        });
        aiCheckbox.checked = false;
        clearJSONSchema();

        handleSearchClick()
    }
    ;
    resetSearchProperty.addEventListener("click", function() {
        eraseSearchValue()
        clearAdvanceSearch();
    });

    function getProvinceFromValue(value) {
        const province = provinces.find( (province) => province.value === value);
        if (province) {
            return province.text;
        } else {
            return null;
        }
    }

    function getDistrictFromValue(province, value) {
        const provinceData = provinces.find( (e) => e.value == province.value || e.value == currentParams.get('province'));
        if (provinceData) {
            const district = provinceData.child.find( (e) => e.value == value);
            if (district) {
                return district.text;
            } else {
                // console.log("District not found.");
                return null;
            }
        }
    }

    //########################## End Advanced Search ###################################

    //########################## JSON SCHEMA ###################################

    function writeJSONSchema(result, tab) {
        let data = JSON.parse(result?.d)?.Data?.Items;
        if (!data) {
            console.error("writeJSONSchema()", data)
            return
        }
        let templateData = {};

        if (!tab && !tabActive) {

            getItemListElement(data, "Recommend");
            templateData = {
                context: "http://schema.org",
                type: "ItemList",
                name: "ทรัพย์สินรอการขายทั่วประเทศ",
                description: "ทรัพย์สินรอการขาย NPA บ้านมือสอง บ้านหลุดจำนองกสิกรไทย ทำเลเด็ดทั่วไทย ค้นหาบ้าน, ทาวน์เฮ้าส์, คอนโดมิเนียม, ที่ดิน, โกดัง หรือโรงงาน คัด คุ้ม ครบ",
                itemListElement: schemaData["Recommend"],
            };
        } else if (tabActive) {

            getItemListElement(data, tabActive);
            templateData = {
                context: "http://schema.org",
                type: "ItemList",
                name: "ทรัพย์สินรอการขายทั่วประเทศ",
                itemListElement: schemaData[tabActive],
            };
        } else {

            getItemListElement(data, tab);
            templateData = {
                context: "http://schema.org",
                type: "ItemList",
                name: "ทรัพยแนะนำที่ไม่ควรพลาด",
                description: "ทรัพย์สินรอการขาย จากทั่วประเทศที่คัดสรรมาให้คุณ เพื่อให้คุณเจอทรัพย์ที่ชอบ ในราคาที่ใช่",
                itemListElement: schemaData[tab],
            };
        }

        let schemaTemplate = {
            "@context": templateData["context"],
            "@type": templateData["type"],
            name: templateData["name"],
            description: templateData["description"],
            itemListElement: templateData["itemListElement"],
        };

        switch (mode) {
        case "list":
            // Case : Recommend : no tab data
            if (!loadMorePage[tab]) {
                createJSONSchema(schemaTemplate, "Recommend");

                // Case : Tab : init tab
            } else if (loadMorePage[tab] == 1) {
                createJSONSchema(schemaTemplate, tab);

                // Case : Tab : loadmore
            } else {
                updateJSONSchema(schemaTemplate, tab);
            }
            break;

        case "map":
            clearJSONSchema();
            createJSONSchema(schemaTemplate, tabActive);
            break;
        }
    }

    function createJSONSchema(schemaTemplate, tab) {
        let newScript = document.createElement("script");
        newScript.type = "application/ld+json";
        newScript.id = `schema_${tab}`;
        newScript.text = `${JSON.stringify(schemaTemplate)}`;
        document.body.appendChild(newScript);
        // console.log(`>>> json schema written `);
    }

    function updateJSONSchema(schemaTemplate, tab) {
        let existingScript = document.getElementById(`schema_${tab}`);
        if (!existingScript) {
            createJSONSchema(schemaTemplate, tab);
            existingScript = document.getElementById(`schema_${tab}`);
        }

        existingScript.text = `${JSON.stringify(schemaTemplate)}`;
        // console.log(`>>> json schema updated `);
    }

    function clearJSONSchema() {
        let existingScripts = document.querySelectorAll(`script[id^="schema_"]`);

        if (!existingScripts)
            return;

        existingScripts.forEach( (script) => {
            script.remove();
        }
        );

        schemaData = {};

        // console.log(`>>> json schema removed `);
    }

    //########################## END JSON SCHEMA ###################################

    function getItemListElement(data, tab) {
        console.log('getItemListElement(tab)', tab)
        if (!data) {
            console.error('getItemListElement()')
            return null
        }
        let itemListElement = [];
        let urlImagePath = "https://pfsapp.kasikornbank.com/pfs-frontend-api/property-images";
        data.forEach( (item) => {
            let nameProp2 = getNameProp(item.PropertyTypeName, item.PropertyTypeID, item.ProvinceName, item.VillageTH);

            itemListElement.push({
                "@type": "Product",
                image: `${urlImagePath}${item.PropertyMediaes.find( (item) => item.MediaType === "IMAGE-THUMBNAIL")?.MediaPath}` || "",
                url: `https://www.kasikornbank.com/th/propertyforsale/detail/${item.PropertyID}.html`,
                name: nameProp2,
                offers: {
                    "@type": "Offer",
                    priceCurrency: "THB",
                    price: `${item.PromotionPrice || item.AdjustPrice || item.SellPrice}`,
                },
            });
        }
        );

        if (!tab) {
            schemaData["Recommend"] = itemListElement;
        } else if (schemaData[tab] == null) {
            schemaData[tab] = itemListElement;
        } else {
            schemaData[tab] = schemaData[tab].concat(itemListElement);
        }
    }

    function getNameProp(PropertyTypeName, PropertyTypeID, ProvinceName, VillageTH) {
        let splitPropType = PropertyTypeName.substring(PropertyTypeName.lastIndexOf(" ") + 1, PropertyTypeName.length);

        if (PropertyTypeID == "01") {
            splitPropType = "ที่ดิน";
        }

        let fullPropTypeName = splitPropType + " " + ProvinceName;
        let nameProp = VillageTH === "-" || VillageTH == null || VillageTH == "" ? fullPropTypeName : VillageTH;
        return nameProp;
    }

    //########################## DATA LAYER ###################################

    function addDataLayerSearch(filterObj, state) {
        if (!window.dataLayer)
            return;
        if (isClearSearch) {
            // isClearSearch = false
            // console.log("dataLayer not trigger");
            return;
        }

        let keyword_search = filterObj.keyword;
        let text_all_filter;
        if (filterObj) {// text_all_filter = Object.values(filterObj).join(",");
        // text_all_filter = getAdvancedSearchDataLayerObj();
        }

        switch (state) {
        case "found":
            window.dataLayer.push({
                event: "track_event",
                event_category: "link_click",
                event_label: "main_search",
                element_grouping: "search",
                element_section: "search",
                search_text: `kwd:${keyword_search}`,
                search_filters_1: `${text_all_filter}`,
                search_filters_2: "found",
            });
            break;
        case "not_found":
            window.dataLayer.push({
                event: "track_event",
                event_category: "link_click",
                event_label: "main_search",
                element_grouping: "search",
                element_section: "search",
                search_text: `kwd:${keyword_search}`,
                search_filters_1: `${text_all_filter}`,
                search_filters_2: "not found",
            });
            break;
        }
    }

    function convertPropertyType(PropertyTypeName) {
        let typeId = PropertyTypeName.substring(0, 2);
        switch (typeId) {
        case "02":
            return "house";
        case "01":
            return "land";
        case "15":
            return "apartment";
        case "03":
            return "townhouse";
        case "05":
            return "condo";
        case "09":
            return "manufactured";
        default:
            return "other";
        }
    }

    function getMetaObject(obj) {
        let itemListElement = [];
        if (obj) {
            obj.forEach( (item) => {
                let price = item.PromotionPrice || item.AdjustPrice || item.SellPrice;
                if (price) {
                    itemListElement.push({
                        content_id: item.PropertyID,
                        content_type: "home_listing",
                        property_type: convertPropertyType(item.PropertyTypeName),
                        price: price,
                    });
                }
            }
            );
        }
        return itemListElement;
    }

    function addDataLayerMeta(obj) {
        let assetArr = getMetaObject(obj);
        let baseObj = {
            event: "facebook_event",
            trigger_type: "page view",
            position: "page load npa list",
            fb_npa_list: [],
        };

        baseObj.fb_npa_list = assetArr;

        return baseObj;
    }

    function pushDataLayer(obj) {
        if (!window.dataLayer)
            return;
        if (!isClearSearch) {
            window.dataLayer.push(obj);
            // console.log(`>>> pushDataLayer is called `);
        }
        // isClearSearch = false
    }

    function getAdvancedSearchDataLayerObj() {
        const selectedPropertyName = propertyName.value;
        const selectedSourceSaleType = Array.from(document.querySelectorAll('[name="source-sale-types"]:checked')).map( (e) => valueFromLabel(e.value)).join("|");

        const selectedProvinceFilter = getSelectedLabel("province-filter");
        const selectedDistrictFilter = getSelectedLabel("district-filter");
        const selectedSubdistrictFilter = getSelectedLabel("sub-district-filter");

        const selectedPropertyType = Array.from(document.querySelectorAll('[name="property-type"]:checked')).map( (e) => valueFromLabel(e.value) || e.value).join("|");

        // const selectedMinPriceFilter =
        //   document.querySelector("#min-price-filter").value || null;
        // const selectedMaxPriceFilter =
        //   document.querySelector("#max-price-filter").value || null;

        // let priceRange =
        //   selectedMinPriceFilter || selectedMaxPriceFilter !== null
        //     ? `${selectedMinPriceFilter}|${selectedMaxPriceFilter}`
        //     : null;

        // const selectedMinArea =
        //   document.querySelector("#min-area").value &&
        //   document.querySelector("#min-area").value !== "clear"
        //     ? document.querySelector("#min-area").value
        //     : null;
        // const selectedMaxArea =
        //   document.querySelector("#max-area").value &&
        //   document.querySelector("#max-area").value !== "clear"
        //     ? document.querySelector("#max-area").value
        //     : null;

        // let areaRange =
        //   selectedMinArea || selectedMaxArea !== null
        //     ? `${selectedMinArea}|${selectedMaxArea}`
        //     : null;

        // const selectedMinUseableArea =
        //   document.querySelector("#min-useable-area").value &&
        //   document.querySelector("#min-useable-area").value !== "clear"
        //     ? document.querySelector("#min-useable-area").value
        //     : null;
        // const selectedMaxUseableArea =
        //   document.querySelector("#max-useable-area").value &&
        //   document.querySelector("#max-useable-area").value !== "clear"
        //     ? document.querySelector("#max-useable-area").value
        //     : null;

        // let useableAreaRange =
        //   selectedMinUseableArea || selectedMaxUseableArea !== null
        //     ? `${selectedMinUseableArea}|${selectedMaxUseableArea}`
        //     : null;

        const selectedBedroom = Array.from(document.querySelectorAll('[name="bed-room"]:checked')).map( (e) => e.value).join("|");
        const selectedBathroom = Array.from(document.querySelectorAll('[name="bath-room"]:checked')).map( (e) => e.value).join("|");

        const selectedTransportationFilter = getSelectedLabel("transportation-filter");

        const selectedAi = document.querySelector("#ai").checked ? "AI Decoration" : null;

        function getSelectedLabel(selectId) {
            const selectElement = document.querySelector(`#${selectId}`);
            const selectedOption = selectElement?.selectedOptions[0];
            return selectedOption ? selectedOption.textContent : null;
        }

        const obj = {
            kwd: selectedPropertyName,
            pp_grp: selectedSourceSaleType,
            prvd: selectedProvinceFilter,
            dist: selectedDistrictFilter,
            pp_ty: selectedPropertyType,
            pric: priceRange,
            area: areaRange,
            use_area: useableAreaRange,
            bed: selectedBedroom,
            bath: selectedBathroom,
            bts_mrt: selectedTransportationFilter,
            hav_ai: selectedAi,
        };
        // // console.log(obj);
        let result = Object.entries(obj).filter( ([key,value]) => value != null && value !== "").map( ([key,value]) => `${key}:${value}`).join(",");
        // // console.log(result);

        return result;
    }

    //########################## END DATA LAYER ###################################

    let elmBtn = document.querySelectorAll(".favorite-btn");
    elmBtn.forEach( (elm) => {
        elm.addEventListener("click", function() {
            // console.log(`favorite clicked`);
            let isActive = elm.classList.contains("active");
            let id = elm.getAttribute("data-id");
            if (isActive) {
                toggleFavoriteTracking(elm, "0", id);
            } else {
                toggleFavoriteTracking(elm, "1", id);
            }
        });
    }
    );

    function toggleFavoriteTracking(element, state, id) {
        switch (state) {
        case "1":
            element.setAtrribute("data-kbct", "click");
            element.setAtrribute("data-kbgp", "content_card");
            element.setAtrribute("data-kbid", id);
            break;
        case "0":
            element.removeAttribute("data-kbct");
            element.removeAttribute("data-kbgp");
            element.removeAttribute("data-kbid");
            break;
        }
    }
    //########################## Session ###################################
    const handleUnload = () => {
        console.log('PAGEHIDE');
        sessionStorage.setItem("npa_scrollPosition", window.scrollY);
        //sessionStorage.setItem("npa_mode", mode ?? 'list');
        /* sessionStorage.setItem('npa_search', {
            'province': $(_provinceElement).val(),
            'district': $(_districtElement).val(),
            'subDistrict': $(_subDistrictElement).val(),
            'area': $(_areaElement).val(),
            'usableArea': $(_usableAreaElement).val(),
            'price': $(_priceElement).val(),
            'propType': $(_propTypeElement).val(),
            'keyword': $(propertyName).val(),
        }) */
        const filteredObj = Object.fromEntries(Object.entries(loadMorePage).filter( ([key,value]) => key === tabActive));
        saveToSession("npa_loadMorePage", filteredObj);
    }
    window.addEventListener('visibilitychange', handleUnload)
    window.addEventListener('pagehide', handleUnload)
    window.addEventListener('beforeunload', handleUnload)
}
);

// Function to get stored data from sessionStorage
function getStoredData(sessionName) {
    const data = sessionStorage.getItem(sessionName);
    let dataArr = data ? JSON.parse(data) : [];
    return dataArr;
}

function getSessionDataObj(sessionName) {
    const data = sessionStorage.getItem(sessionName);
    let dataArr = data ? JSON.parse(data) : [];

    let dataObj = {};
    dataObj.items = [];

    dataArr.length > 0 && dataArr.forEach( (item) => {
        let parsedItem = JSON.parse(item?.d)?.Data?.Items;
        if (parsedItem) {
            dataObj.items = [...dataObj.items, ...parsedItem];
        }
    }
    );

    return dataObj;
}

function getSessionObj(sessionName) {
    const data = sessionStorage.getItem(sessionName);
    let dataObj = data ? JSON.parse(data) : [];
    return dataObj;
}

// Function to save data to sessionStorage
function appendToSession(sessionName, newData) {
    let currentData = getStoredData(sessionName);
    // Retrieve existing data
    currentData = currentData.concat(newData);
    // Append new data
    sessionStorage.setItem(sessionName, JSON.stringify(currentData));
    // Save back to sessionStorage
}

// Function to replace data in sessionStorage
function saveToSession(sessionName, newData) {
    sessionStorage.setItem(sessionName, JSON.stringify(newData));
}
function clearStoredData(sessionName) {
    console.log("clearStoredData >> ", sessionName);
    sessionStorage.removeItem(sessionName);
}

function clearAssets(tab) {
    const assets = document.querySelector(`.g-content.${tab} .assets-swiper`);
    if (assets) {
        assets.innerHTML = "";
    }
}

//########################## END Session ###################################

const labelPropertyType = (value) => {
    let label = "";
    if (value == "02") {
        label = "บ้านเดี่ยว";
    } else if (value == "01") {
        label = "ที่ดิน";
    } else if (value == "03") {
        label = "ทาวน์เฮ้าส์";
    } else if (value == "05") {
        label = "คอนโดมิเนียม";
    } else if (value == "04") {
        label = "อาคารพาณิชย์";
    } else if (value == "12") {
        label = "โกดัง";
    } else if (value == "09") {
        label = "โรงงาน";
    } else if (value == "15") {
        label = "อพาร์ทเม้นท์";
    } else if (value == "10") {
        label = "อาคารสำนักงาน";
    } else if (value == "20") {
        label = "รีสอร์ท";
    } else if (value == "other") {
        label = "อื่นๆ";
    }
    return label;
}
;
function valueFromLabel(label) {
    return labelToValueMap[label] || null;
}
