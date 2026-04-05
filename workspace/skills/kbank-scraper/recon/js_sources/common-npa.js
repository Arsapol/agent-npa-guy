"use strict";

// ********************* Favorite *********************

const elmBtn = document.querySelectorAll(".favorite-btn");
const elmCloseTooltip = document.querySelectorAll(".close-tooltip");
const elmTooltip = document.querySelectorAll(".tooltip-favorite");

const eventFavorite = function() {
  Array.from(elmBtn).map((elm) => {
    elm.addEventListener("click", function(){
      if (allowCookieValue !== "Y") {
        const tooltip = elm.parentElement.querySelector(".tooltip-favorite");
        tooltip.classList.toggle('active');
      }
    })
  })
}

const allowCookieValue = getCookie('Allow_Cookies');
eventFavorite(allowCookieValue);

Array.from(elmCloseTooltip).map((e) => {
  e.addEventListener("click", function(){
    Array.from(elmTooltip).map((elm) => {
      elm.classList.remove('active');
    });
  });
})


function getCookie(name) {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
          return cookie.substring(name.length + 1);
      }
  }
  return null;
}

function initializeSwiper(elm, option) {
  if (!option) {
    option = {
      slidesPerView: "auto",
      loop: false,
      spaceBetween: 0,
      freeMode: false,
      pagination: {
        el: ".swiper-pagination",
        clickable: true,
      },
    };
  }
  return new Swiper(elm, option);
}

function fbShare() {
  dataLayer.push({
    event: "track_event",
    event_category: "social_share",
    event_action: "click",
    event_label: "facebook-share"
  });

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
  dataLayer.push({
    event: "track_event",
    event_category: "social_share",
    event_action: "click",
    event_label: "twitter-share"
  });

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
  dataLayer.push({
    event: "track_event",
    event_category: "social_share",
    event_action: "click",
    event_label: "line-share"
  });
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

//Personalized
function setPersonalizedData(personalizedDataArray) {
    const jsonData = JSON.stringify(personalizedDataArray);
    document.cookie = `personalizedData=${jsonData}; path=/;`;
    const expirationDate = new Date();
    expirationDate.setDate(expirationDate.getDate() + 30);
    document.cookie = `expires=${expirationDate.toUTCString()}; path=/;`;
}


// Cookie
function getCookieValue(cookieName) {
    const cookies = document.cookie.split(';').map(cookie => cookie.trim());
    const targetCookie = cookies.find(cookie => cookie.startsWith(`${cookieName}=`));

    if (targetCookie) {
        const cookieValue = targetCookie.split('=')[1];
        return cookieValue;
    } else {
        return null;
    }
}

//Favorite
function onclickFavorite() {
  const favoriteButtons = document.querySelectorAll('.property-favorite');
  

  favoriteButtons.forEach(function(favoriteButton) {
      const propertyID = favoriteButton.getAttribute('data-id');
      const favoriteProperties = getCookieValue('favoriteProperty');
      const isLiked = favoriteProperties && favoriteProperties.split(',').includes(propertyID);


      if (isLiked) {
        favoriteButton.classList.add("active");
        const icon = favoriteButton.querySelector('.ic-npa');
        icon.classList.remove('ic-npa-icon-like');
        icon.classList.add('ic-npa-icon-like-active');
        toggleFavoriteTracking(this, '0', propertyID);
      }

      favoriteButton.addEventListener('click', function(e) {
          e.preventDefault();
		  
          const propertyID = this.getAttribute('data-id');
          const isLiked = this.classList.contains('active');
          this.classList.toggle('active');

          setLikeProperty(propertyID, !isLiked);
          const icon = this.querySelector('.ic-npa');

          if (!isLiked) {
            toggleFavoriteTracking(this, '0', propertyID);
              icon.classList.remove('ic-npa-icon-like');
              icon.classList.add('ic-npa-icon-like-active');
          } else {
            toggleFavoriteTracking(this, '1', propertyID);
              icon.classList.remove('ic-npa-icon-like-active');
              icon.classList.add('ic-npa-icon-like');
          }
      });
  });
}

function toggleFavoriteTracking(element, state, id) {
	if(!element) return;
  switch (state) {
    case "1":
      element.setAttribute("data-kbct", "click");
      element.setAttribute("data-kbgp", "content_card");
      element.setAttribute("data-kbid", id);
      break;
    case "0":
      element.removeAttribute("data-kbct");
      element.removeAttribute("data-kbgp");
      element.removeAttribute("data-kbid");
      break;
  }
}

// GetArea
 function getArea(property) {
  var typeCode;

  if (hasValue(property.PropertyTypeName)) {
    typeCode = property.PropertyTypeName.trim().split(" ")[0];
  } else {
    typeCode = null;
  }

  if (typeCode === "05") {
    //condo
    if (hasValue(property.UseableArea) && property.UseableArea !== 0) {
      return {
        value: property.UseableArea.toFixed(2),
        unit: "ตร.ม.",
      };
    } else if (hasValue(property.AreaValue) && property.AreaValue !== 0) {
      return {
        value: property.AreaValue.toFixed(2),
        unit: "ตร.ม.",
      };
    } else {
      return null;
    }
  } else if (typeCode === "17") {
    //Office suite
    if (hasValue(property.UseableArea) && property.UseableArea !== 0) {
      return {
        value: property.UseableArea.toFixed(2),
        unit: "ตร.ม.",
      };
    } else if (hasValue(property.AreaValue) && property.AreaValue !== 0) {
      return {
        value: property.AreaValue.toFixed(2),
        unit: "ตร.ม.",
      };
    } else {
      return null;
    }
  } else if (typeCode === "02" || typeCode === "03" || typeCode === "04" || typeCode === "15") {
    // House , Townhouse , Commercial building , Apartment
    if (hasValue(property.AreaValue) && property.AreaValue !== 0) {
      return {
        value: property.AreaValue.toFixed(2),
        unit: "ตร.ว.",
      };
    } else {
      return null;
    }
  } else if (typeCode === "99") {
    // Machine
    return null;
  } else {
    //other
    if (hasValue(property.Area) && property.Area !== "0-0-0.00") {
      return {
        value: property.Area,
        unit: "ไร่",
      };
    } else if (hasValue(property.Rai) && hasValue(property.Ngan) && hasValue(property.SquareArea)) {
      const formattedString = `${property.Rai}-${property.Ngan}-${
        property.SquareArea.toFixed(2) || "0.00"
      }`;
      if (formattedString == "0-0-0.00") {
        return null;
      }
      return {
        value: formattedString,
        unit: "ไร่",
      };
    } else {
      return null;
    }
  }
}

 function hasValue(val) {
  if (val === null || val === "" || val === undefined) {
    return false;
  }

  return true;
}
  