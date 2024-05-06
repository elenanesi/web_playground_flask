//Add your own GTM ID
const GTM_ID = "GTM-WZ4DNGJW";
//Add your own GA measurement ID, skip the "G-" prefix
const GA_MEASUREMENT_ID = "1L1YW7SZFP";
//Add the ID of your cookie banner HTML element below
const cookie_banner_id = "cookie-banner"
const ga_cookie_name = "_ga_"+GA_MEASUREMENT_ID;


function getCookie(name){
  var cookies = document.cookie.split("; ");
  var i = 0;
  var l = cookies.length;
  var cookie, cookieName, cookieValue;
  for (i = 0; i < l; i++) {
    cookie = cookies[i].split("=");
    cookieName = cookie[0];
    cookieValue = cookie[1];
    if (cookieName === name) {
      return cookieValue;
    }
  }
  return null; // Return null if cookie not found
  }

function setCookie(name, value, days){
    var domain = window.location.hostname;
    // Extract the main domain by removing subdomains, if any
    // var mainDomain = domain.includes('.') ? domain.substring(domain.lastIndexOf('.', domain.lastIndexOf('.') - 1) + 1) : domain;
    var date
    var expires = "";
    if (days) {
        date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }

    // Include the domain in the cookie string
    document.cookie = name + "=" + (value || "") + expires + "; path=/; domain=" + domain;
  }

function closePopup(){ 
  var Popup = document.getElementById(cookie_banner_id);
  Popup.style.display = "none";
  //document.querySelector('.overlay').style.display = 'none';
  }

function acceptAll(){
        // Define dataLayer and the gtag function.
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('consent', 'update', {
          'ad_storage': 'granted',
          'ad_user_data': 'granted',
          'ad_personalization': 'granted',
          'analytics_storage': 'granted'
        });
        setCookie("cookie_consent", "11", 365)
  }

function denyAll(){
    // Define dataLayer and the gtag function.
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}

    gtag('consent', 'update', {
      'ad_storage': 'denied',
      'ad_user_data': 'denied',
      'ad_personalization': 'denied',
      'analytics_storage': 'denied'
    });
    setCookie("cookie_consent", "00")
  }

function allowSelection(){
    var analyticsToggle = document.getElementById('analyticsToggle')  || "denied";
    var marketingToggle = document.getElementById('marketingToggle') || "denied";
    var analytics_storage = analyticsToggle.checked ? "granted" : "denied"
    var ad_storage = marketingToggle.checked ? "granted" : "denied"
    var analytics_cookie = analyticsToggle.checked ? "1" : "0"
    var ad_storage_cookie = marketingToggle.checked ? "1" : "0"
    setCookie("cookie_consent", analytics_cookie+ad_storage_cookie)


    // Define dataLayer and the gtag function.
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('consent', 'update', {
      'ad_storage': ad_storage,
      'ad_user_data': ad_storage,
      'ad_personalization': ad_storage,
      'analytics_storage': analytics_storage
    });
  }

function returningUser(clientIds){
  var randomClient = clientIds[Math.floor(Math.random() * clientIds.length)];
  setCookie("_ga", randomClient._ga, 365);
  setCookie(ga_cookie_name, randomClient[ga_cookie_name], 365);
  // assuming cookie consent has been given in the past
  acceptAll()
  console.log("returning user", randomClient[ga_cookie_name])
  }

function pdp_analytics() {
    window.dataLayer.push({
      'content_group': 'product_detail'
    });

    if (document.referrer.indexOf(document.location.host)>=0) {
      select_item(analytics_items);
    }

    window.dataLayer.push({ ecommerce: null });  // Clear the previous ecommerce object.
    window.dataLayer.push({
      event: "view_item",
      ecommerce: {
        currency: "EUR",
        value: 7.77,
        items: [analytics_items]
      }
    });
  }

function plp_analytics() {
  window.dataLayer.push({
    'content_group': 'product_category'
  })
  dataLayer.push({ ecommerce: null });  // Clear the previous ecommerce object.
  dataLayer.push({
    event: "view_item_list",
    ecommerce: {
      item_list_id: "product_category",
      item_list_name: "product_category",
      items: analytics_items
    }
  });
  }

function checkout_analytics(){
  window.dataLayer.push({
    'content_group': 'checkout'
  });

  dataLayer.push({ ecommerce: null });  // Clear the previous ecommerce object.
  dataLayer.push({
  event: "begin_checkout",
  ecommerce: {
      currency: "EUR",
      items: analytics_items
  }
});

  }

function purchase_analytics(){
    var url = window.location.pathname;
    var category = url.split('/')[2]

    window.dataLayer.push({
    'content_group': 'purchase'
  });


  dataLayer.push({ ecommerce: null });  // Clear the previous ecommerce object.
  dataLayer.push({
  event: "purchase",
  ecommerce: {
      transaction_id: Date.now(),
      value: analytics_value,
      tax: analytics_value*0.1,
      shipping: 2.99,
      currency: "EUR",
      coupon: "SUMMER_SALE",
      items: analytics_items
  }
});
  }

function select_item(){
  dataLayer.push({ ecommerce: null });  // Clear the previous ecommerce object.
  dataLayer.push({
    event: "select_item",
    ecommerce: {
      items: [analytics_items]
    }
  });
  }

function add_to_cart(category, productName){
  fetch(`/add_to_cart/${category}/${productName}`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        // Include CSRF token header if needed
    },
  })
  .then(response => response.json())
  .catch(error => {
      console.error('Error:', error);
  });



  window.dataLayer.push({ ecommerce: null });  // Clear the previous ecommerce object.
  window.dataLayer.push({
    event: "add_to_cart",
    ecommerce: {
      currency: "EUR",
      value: analytics_items.price,
      items: [analytics_items]
    }
  });
  }

window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}

// Set default consent to 'denied' as a placeholder
// Determine actual values based on your own requirements
gtag('consent', 'default', {
  'ad_storage': 'denied',
  'ad_user_data': 'denied',
  'ad_personalization': 'denied',
  'analytics_storage': 'denied',
  'wait_for_update' : 500
});
gtag('set', 'ads_data_redaction', true);

(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer',GTM_ID);

const urlPath = window.location.pathname;
if (/^\/$/.test(urlPath)) {
  //console.log("home!")
  window.dataLayer.push({
    'content_group': 'home'
  })
}
else if (/cart/.test(urlPath)) {
  console.log("checkout page")
  checkout_analytics()
}

else if (/thank/.test(urlPath)) {
  console.log("purchase page")
  purchase_analytics()
}

else if (/\/category/.test(urlPath)) {
  console.log("plp page")
  plp_analytics()
}

else if (/\/\w+\/\w+(\/)?/.test(urlPath)) {
  console.log("pdp page")
  pdp_analytics()
}
