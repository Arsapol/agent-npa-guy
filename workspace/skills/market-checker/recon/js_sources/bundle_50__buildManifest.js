self.__BUILD_MANIFEST = {
  "/[locale]/consumer/agent-directory/find-agent": [
    "static/chunks/fedf86039d5fc90e.js"
  ],
  "/[locale]/consumer/agent-profile/[slug]": [
    "static/chunks/9869cf2fcb70a030.js"
  ],
  "/[locale]/consumer/ai-search/[[...slug]]": [
    "static/chunks/08f3bafbf4172fa9.js"
  ],
  "/[locale]/consumer/condo-directory/[[...slug]]": [
    "static/chunks/4da237af385514ef.js"
  ],
  "/[locale]/consumer/contact-agent/[token]": [
    "static/chunks/25bc3be731c5e51b.js"
  ],
  "/[locale]/consumer/contact-consumer/[token]": [
    "static/chunks/fb403fa164a10b92.js"
  ],
  "/[locale]/consumer/contact-seller/[token]": [
    "static/chunks/66f4aef0b6260ea1.js"
  ],
  "/[locale]/consumer/hdb": [
    "static/chunks/08c3fd29a0363902.js"
  ],
  "/[locale]/consumer/hdb/[estate]": [
    "static/chunks/cf0df3a572abff2b.js"
  ],
  "/[locale]/consumer/hdb/[estate]/[street]": [
    "static/chunks/cddaf65f268b2fd6.js"
  ],
  "/[locale]/consumer/home": [
    "static/chunks/60cc4e9c84d021d6.js"
  ],
  "/[locale]/consumer/home-sellers": [
    "static/chunks/65e2721b817f458b.js"
  ],
  "/[locale]/consumer/home-sellers/landing": [
    "static/chunks/4f8c7721766df016.js"
  ],
  "/[locale]/consumer/home-sellers/seller-journey/[slug]": [
    "static/chunks/83345f4cbeb1f3f6.js"
  ],
  "/[locale]/consumer/home-sellers/valuation": [
    "static/chunks/176d648078cec094.js"
  ],
  "/[locale]/consumer/ldp/[[...slug]]": [
    "static/chunks/00e1bd364e2fffec.js"
  ],
  "/[locale]/consumer/open-app": [
    "static/chunks/c3d889e5f0f3c60f.js"
  ],
  "/[locale]/consumer/pdp/[[...slug]]": [
    "static/chunks/70e31241d0083346.js"
  ],
  "/[locale]/consumer/srp/[[...slug]]": [
    "static/chunks/2ba538b085502742.js"
  ],
  "/[locale]/consumer/user-consent": [
    "static/chunks/d2475a05eb16aa17.js"
  ],
  "/[locale]/consumer/user-preferences": [
    "static/chunks/9d9eea4343eb8edb.js"
  ],
  "/[locale]/consumer/user-profile": [
    "static/chunks/bdefe0f60252812c.js"
  ],
  "/[locale]/consumer/watchlist": [
    "static/chunks/a4dab036296ebfd1.js"
  ],
  "/[locale]/developer/new-launch": [
    "static/chunks/0378418d38dd922d.js"
  ],
  "/[locale]/developer/pldp/[[...slug]]": [
    "static/chunks/5db0c46d52761d10.js"
  ],
  "/[locale]/developer/profile/[slug]": [
    "static/chunks/1fa4723ab2a8f161.js"
  ],
  "/[locale]/error": [
    "static/chunks/c4020435f595c401.js"
  ],
  "/[locale]/finance/home-loan": [
    "static/chunks/92ab951e13000734.js"
  ],
  "/[locale]/finance/home-owner": [
    "static/chunks/924ca647b62b0642.js"
  ],
  "/[locale]/finance/home-owner/dashboard": [
    "static/chunks/d463d6055123cb45.js"
  ],
  "/[locale]/finance/home-owner/dashboard/[slug]": [
    "static/chunks/094100105028144a.js"
  ],
  "/[locale]/finance/home-sellers/dashboard": [
    "static/chunks/3bbb7fad6996b6ed.js"
  ],
  "/[locale]/finance/home-sellers/dashboard/[slug]": [
    "static/chunks/cf775014fe5248c2.js"
  ],
  "/[locale]/finance/mortgage": [
    "static/chunks/b7aa05bffae89fdd.js"
  ],
  "/[locale]/finance/prequal/landing": [
    "static/chunks/f57457972b1f006a.js"
  ],
  "/_error": [
    "static/chunks/1c0fc8cf2dd98900.js"
  ],
  "__rewrites": {
    "afterFiles": [
      {
        "has": [
          {
            "type": "header",
            "key": "x-guruland-proxy",
            "value": "true"
          }
        ],
        "source": "/:path*",
        "destination": "/en/guruland-proxy/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en",
        "destination": "/en/consumer/home"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/agent/:path*",
        "destination": "/en/consumer/agent-profile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/developer/:path*",
        "destination": "/en/developer/profile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property/project/:path*",
        "destination": "/en/developer/pldp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property/:path*",
        "destination": "/en/consumer/ldp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/new-property-launch",
        "destination": "/en/developer/new-launch"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/p-luxury-houses-for-sale",
        "destination": "/en/property-for-sale?listingType=sale&page=1&isCommercial=false&minPrice=10000000&propertyTypeGroup=B&propertyTypeCode=BUNG&isLuxury=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/p-luxury-houses-for-rent",
        "destination": "/en/property-for-rent?listingType=rent&page=1&propertyTypeGroup=B&propertyTypeCode=BUNG&isCommercial=false&minPrice=100000&isLuxury=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/p-luxury-condos-for-sale",
        "destination": "/en/property-for-sale?listingType=sale&page=1&propertyTypeGroup=N&propertyTypeCode=CONDO&isCommercial=false&minPrice=10000000&isLuxury=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/p-luxury-condos-for-rent",
        "destination": "/en/property-for-rent?listingType=rent&minPrice=100000&propertyTypeGroup=N&propertyTypeCode=CONDO&isCommercial=false&search=true&isLuxury=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/agent-directory/find-agent",
        "destination": "/en/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/agent-directory/:path",
        "destination": "/en/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/p-condos-near-universities-for-sale",
        "destination": "/en/consumer/srp/search?listingType=sale&isNearSchools=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/p-condos-near-universities-for-rent",
        "destination": "/en/consumer/srp/search?listingType=rent&isNearSchools=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/p-eco-houses-condos-for-sale",
        "destination": "/en/consumer/srp/search?listingType=sale&isSustainableLiving=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/p-eco-houses-condos-for-rent",
        "destination": "/en/consumer/srp/search?listingType=rent&isSustainableLiving=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/open-app",
        "destination": "/en/consumer/open-app"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/condo-hp/:path*",
        "destination": "/en/consumer/condo-directory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/condo-directory/:path*",
        "destination": "/en/consumer/condo-directory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/pdp-temp/:path*",
        "destination": "/en/consumer/pdp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/",
        "destination": "/th/consumer/home"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%99%E0%B8%99%E0%B8%97%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9B%E0%B8%97%E0%B8%B8%E0%B8%A1%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B9%80%E0%B8%8A%E0%B8%B5%E0%B8%A2%E0%B8%87%E0%B9%83%E0%B8%AB%E0%B8%A1%E0%B9%88)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B9%80%E0%B8%8A%E0%B8%B5%E0%B8%A2%E0%B8%87%E0%B8%A3%E0%B8%B2%E0%B8%A2)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%8A%E0%B8%A5%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A0%E0%B8%B9%E0%B9%80%E0%B8%81%E0%B9%87%E0%B8%95)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A3%E0%B8%B0%E0%B8%A2%E0%B8%AD%E0%B8%87)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%B8%E0%B8%A3%E0%B8%B2%E0%B8%A9%E0%B8%8E%E0%B8%A3%E0%B9%8C%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%AA%E0%B8%B5%E0%B8%A1%E0%B8%B2)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%82%E0%B8%AD%E0%B8%99%E0%B9%81%E0%B8%81%E0%B9%88%E0%B8%99)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9E%E0%B8%B1%E0%B8%97%E0%B8%A2%E0%B8%B2)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%A1%E0%B8%B8%E0%B8%97%E0%B8%A3%E0%B8%9B%E0%B8%A3%E0%B8%B2%E0%B8%81%E0%B8%B2%E0%B8%A3)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%A8%E0%B8%A3%E0%B8%B5%E0%B8%AD%E0%B8%A2%E0%B8%B8%E0%B8%98%E0%B8%A2%E0%B8%B2)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AD%E0%B9%88%E0%B8%B2%E0%B8%87%E0%B8%97%E0%B8%AD%E0%B8%87)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A5%E0%B8%9E%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%B4%E0%B8%87%E0%B8%AB%E0%B9%8C%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%8A%E0%B8%B1%E0%B8%A2%E0%B8%99%E0%B8%B2%E0%B8%97)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%88%E0%B8%B1%E0%B8%99%E0%B8%97%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%95%E0%B8%A3%E0%B8%B2%E0%B8%94)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%89%E0%B8%B0%E0%B9%80%E0%B8%8A%E0%B8%B4%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%A3%E0%B8%B2)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9B%E0%B8%A3%E0%B8%B2%E0%B8%88%E0%B8%B5%E0%B8%99%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%81)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%A3%E0%B8%B0%E0%B9%81%E0%B8%81%E0%B9%89%E0%B8%A7)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5%E0%B8%A3%E0%B8%B1%E0%B8%A1%E0%B8%A2%E0%B9%8C)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%B8%E0%B8%A3%E0%B8%B4%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B9%8C)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A8%E0%B8%A3%E0%B8%B5%E0%B8%AA%E0%B8%B0%E0%B9%80%E0%B8%81%E0%B8%A9)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AD%E0%B8%B8%E0%B8%9A%E0%B8%A5%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A2%E0%B9%82%E0%B8%AA%E0%B8%98%E0%B8%A3)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%8A%E0%B8%B1%E0%B8%A2%E0%B8%A0%E0%B8%B9%E0%B8%A1%E0%B8%B4)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AD%E0%B8%B3%E0%B8%99%E0%B8%B2%E0%B8%88%E0%B9%80%E0%B8%88%E0%B8%A3%E0%B8%B4%E0%B8%8D)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AB%E0%B8%99%E0%B8%AD%E0%B8%87%E0%B8%9A%E0%B8%B1%E0%B8%A7%E0%B8%A5%E0%B8%B3%E0%B8%A0%E0%B8%B9)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AD%E0%B8%B8%E0%B8%94%E0%B8%A3%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B9%80%E0%B8%A5%E0%B8%A2)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AB%E0%B8%99%E0%B8%AD%E0%B8%87%E0%B8%84%E0%B8%B2%E0%B8%A2)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A1%E0%B8%AB%E0%B8%B2%E0%B8%AA%E0%B8%B2%E0%B8%A3%E0%B8%84%E0%B8%B2%E0%B8%A1)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%A2%E0%B9%80%E0%B8%AD%E0%B9%87%E0%B8%94)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%81%E0%B8%B2%E0%B8%AC%E0%B8%AA%E0%B8%B4%E0%B8%99%E0%B8%98%E0%B8%B8%E0%B9%8C)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%81%E0%B8%A5%E0%B8%99%E0%B8%84%E0%B8%A3)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%9E%E0%B8%99%E0%B8%A1)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A1%E0%B8%B8%E0%B8%81%E0%B8%94%E0%B8%B2%E0%B8%AB%E0%B8%B2%E0%B8%A3)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A5%E0%B8%B3%E0%B8%9E%E0%B8%B9%E0%B8%99)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A5%E0%B8%B3%E0%B8%9B%E0%B8%B2%E0%B8%87)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AD%E0%B8%B8%E0%B8%95%E0%B8%A3%E0%B8%94%E0%B8%B4%E0%B8%95%E0%B8%96%E0%B9%8C)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B9%81%E0%B8%9E%E0%B8%A3%E0%B9%88)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%99%E0%B9%88%E0%B8%B2%E0%B8%99)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9E%E0%B8%B0%E0%B9%80%E0%B8%A2%E0%B8%B2)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B9%81%E0%B8%A1%E0%B9%88%E0%B8%AE%E0%B9%88%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%AD%E0%B8%99)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%AA%E0%B8%A7%E0%B8%A3%E0%B8%A3%E0%B8%84%E0%B9%8C)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AD%E0%B8%B8%E0%B8%97%E0%B8%B1%E0%B8%A2%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%81%E0%B8%B3%E0%B9%81%E0%B8%9E%E0%B8%87%E0%B9%80%E0%B8%9E%E0%B8%8A%E0%B8%A3)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%95%E0%B8%B2%E0%B8%81)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%B8%E0%B9%82%E0%B8%82%E0%B8%97%E0%B8%B1%E0%B8%A2)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9E%E0%B8%B4%E0%B8%A9%E0%B8%93%E0%B8%B8%E0%B9%82%E0%B8%A5%E0%B8%81)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9E%E0%B8%B4%E0%B8%88%E0%B8%B4%E0%B8%95%E0%B8%A3)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B9%80%E0%B8%9E%E0%B8%8A%E0%B8%A3%E0%B8%9A%E0%B8%B9%E0%B8%A3%E0%B8%93%E0%B9%8C)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%81%E0%B8%B2%E0%B8%8D%E0%B8%88%E0%B8%99%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%B8%E0%B8%9E%E0%B8%A3%E0%B8%A3%E0%B8%93%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%9B%E0%B8%90%E0%B8%A1)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%A1%E0%B8%B8%E0%B8%97%E0%B8%A3%E0%B8%AA%E0%B8%B2%E0%B8%84%E0%B8%A3)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%A1%E0%B8%B8%E0%B8%97%E0%B8%A3%E0%B8%AA%E0%B8%87%E0%B8%84%E0%B8%A3%E0%B8%B2%E0%B8%A1)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B9%80%E0%B8%9E%E0%B8%8A%E0%B8%A3%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%88%E0%B8%A7%E0%B8%9A%E0%B8%84%E0%B8%B5%E0%B8%A3%E0%B8%B5%E0%B8%82%E0%B8%B1%E0%B8%99%E0%B8%98%E0%B9%8C)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%A8%E0%B8%A3%E0%B8%B5%E0%B8%98%E0%B8%A3%E0%B8%A3%E0%B8%A1%E0%B8%A3%E0%B8%B2%E0%B8%8A)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%81%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%B5%E0%B9%88)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9E%E0%B8%B1%E0%B8%87%E0%B8%87%E0%B8%B2)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A3%E0%B8%B0%E0%B8%99%E0%B8%AD%E0%B8%87)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%8A%E0%B8%B8%E0%B8%A1%E0%B8%9E%E0%B8%A3)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%AA%E0%B8%95%E0%B8%B9%E0%B8%A5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%95%E0%B8%A3%E0%B8%B1%E0%B8%87)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9E%E0%B8%B1%E0%B8%97%E0%B8%A5%E0%B8%B8%E0%B8%87)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9B%E0%B8%B1%E0%B8%95%E0%B8%95%E0%B8%B2%E0%B8%99%E0%B8%B5)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%A2%E0%B8%B0%E0%B8%A5%E0%B8%B2)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%99%E0%B8%A3%E0%B8%B2%E0%B8%98%E0%B8%B4%E0%B8%A7%E0%B8%B2%E0%B8%AA)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%9A%E0%B8%B6%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%AC)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/%E0%B8%84%E0%B9%89%E0%B8%99%E0%B8%AB%E0%B8%B2%E0%B8%95%E0%B8%B1%E0%B8%A7%E0%B9%81%E0%B8%97%E0%B8%99",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2-%E0%B9%82%E0%B8%AB%E0%B8%A7%E0%B8%95)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path(%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94)",
        "destination": "/th/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9C%E0%B8%B9%E0%B9%89%E0%B8%9E%E0%B8%B1%E0%B8%92%E0%B8%99%E0%B8%B2%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3/:path*",
        "destination": "/th/developer/profile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/property/project/:path*",
        "destination": "/th/developer/pldp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/property/:path*",
        "destination": "/th/consumer/ldp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%83%E0%B8%AB%E0%B8%A1%E0%B9%88",
        "destination": "/th/developer/new-launch"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/p-%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B8%AB%E0%B8%A3%E0%B8%B9",
        "destination": "/รวมประกาศขาย?locale=en&listingType=sale&page=1&propertyTypeGroup=B&propertyTypeCode=BUNG&isCommercial=false&minPrice=10000000&isLuxury=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/p-%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B8%AB%E0%B8%A3%E0%B8%B9",
        "destination": "/รวมประกาศให้เช่า?locale=en&listingType=rent&page=1&propertyTypeGroup=B&propertyTypeCode=BUNG&isCommercial=false&minPrice=100000&isLuxury=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/p-%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%AB%E0%B8%A3%E0%B8%B9",
        "destination": "/รวมประกาศขาย?locale=en&listingType=sale&page=1&propertyTypeGroup=N&propertyTypeCode=CONDO&isCommercial=false&minPrice=10000000&isLuxury=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/p-%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B8%AB%E0%B8%A3%E0%B8%B9",
        "destination": "/รวมประกาศให้เช่า?locale=en&listingType=rent&page=1&propertyTypeGroup=N&propertyTypeCode=CONDO&isCommercial=false&minPrice=100000&isLuxury=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/p-%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B9%83%E0%B8%81%E0%B8%A5%E0%B9%89%E0%B8%A1%E0%B8%AB%E0%B8%B2%E0%B8%A7%E0%B8%B4%E0%B8%97%E0%B8%A2%E0%B8%B2%E0%B8%A5%E0%B8%B1%E0%B8%A2",
        "destination": "/th/consumer/srp/search?listingType=ขาย&isNearSchools=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/p-%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94%E0%B9%83%E0%B8%81%E0%B8%A5%E0%B9%89%E0%B8%A1%E0%B8%AB%E0%B8%B2%E0%B8%A7%E0%B8%B4%E0%B8%97%E0%B8%A2%E0%B8%B2%E0%B8%A5%E0%B8%B1%E0%B8%A2",
        "destination": "/th/consumer/srp/search?listingType=เช่า&isNearSchools=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/p-%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%AB%E0%B8%A2%E0%B8%B1%E0%B8%94%E0%B8%9E%E0%B8%A5%E0%B8%B1%E0%B8%87%E0%B8%87%E0%B8%B2%E0%B8%99",
        "destination": "/th/consumer/srp/search?listingType=ขาย&isSustainableLiving=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/p-%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94-%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%AB%E0%B8%A2%E0%B8%B1%E0%B8%94%E0%B8%9E%E0%B8%A5%E0%B8%B1%E0%B8%87%E0%B8%87%E0%B8%B2%E0%B8%99",
        "destination": "/th/consumer/srp/search?listingType=เช่า&isSustainableLiving=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/open-app",
        "destination": "/th/consumer/open-app"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2%E0%B9%81%E0%B8%A3%E0%B8%81%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/:path*",
        "destination": "/th/consumer/condo-directory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/:path*",
        "destination": "/th/consumer/condo-directory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9E%E0%B8%B5%E0%B8%94%E0%B8%B5%E0%B8%9E%E0%B8%B5-%E0%B9%80%E0%B8%97%E0%B8%A1%E0%B8%9B%E0%B9%8C/:path*",
        "destination": "/th/consumer/pdp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/p-pet-friendly-property-for-sale",
        "destination": "/en/consumer/srp/search?isPetFriendly=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property-for-:listingType",
        "destination": "/en/consumer/srp/search?listingType=:listingType"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property-for-:listingType/p/:freetext/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/:propertyTypeSlug-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?propertyTypeSlug=:propertyTypeSlug&listingType=:listingType"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/similar-listing/:page(\\d+)?",
        "destination": "/en/consumer/srp?page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/p-%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%AD%E0%B8%AA%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B2%E0%B9%80%E0%B8%A5%E0%B8%B5%E0%B9%89%E0%B8%A2%E0%B8%87%E0%B8%AA%E0%B8%B1%E0%B8%95%E0%B8%A7%E0%B9%8C%E0%B9%84%E0%B8%94%E0%B9%89",
        "destination": "/th/consumer/srp/search?isPetFriendly=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A8%E0%B8%82%E0%B8%B2%E0%B8%A2",
        "destination": "/th/consumer/srp/search?listingType=ขาย"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A8%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2",
        "destination": "/th/consumer/srp/search?listingType=ให้เช่า"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A8%E0%B8%82%E0%B8%B2%E0%B8%A2/p/:freetext/:page(\\d+)?",
        "destination": "/th/consumer/srp/search?listingType=ขาย&freetext=:freetext&page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A8%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2/p/:freetext/:page(\\d+)?",
        "destination": "/th/consumer/srp/search?listingType=ให้เช่า&freetext=:freetext&page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A8:listingType/:path*",
        "destination": "/th/consumer/srp/:path*?listingType=:listingType"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B8%B2%E0%B8%A2:propertyTypeSlug/:path*",
        "destination": "/th/consumer/srp/:path*?listingType=ขาย&propertyTypeSlug=:propertyTypeSlug"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2:propertyTypeSlug/:path*",
        "destination": "/th/consumer/srp/:path*?listingType=เช่า&propertyTypeSlug=:propertyTypeSlug"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/similar-listing/:page(\\d+)?",
        "destination": "/th/consumer/srp?page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/acceptable-use/:path*",
        "destination": "/en/guruland-proxy/en/acceptable-use/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/advertise-your-listings/:path*",
        "destination": "/en/guruland-proxy/en/advertise-your-listings/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/advertising-rules/:path*",
        "destination": "/en/guruland-proxy/en/advertising-rules/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/agent-directory/:path*",
        "destination": "/en/guruland-proxy/en/agent-directory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/bangkok/:path*",
        "destination": "/en/guruland-proxy/en/bangkok/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/chachoengsao/:path*",
        "destination": "/en/guruland-proxy/en/chachoengsao/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/chiang-mai/:path*",
        "destination": "/en/guruland-proxy/en/chiang-mai/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/chiang-rai/mae-sai/land-for-sale/:path*",
        "destination": "/en/guruland-proxy/en/chiang-rai/mae-sai/land-for-sale/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/chon-buri/:path*",
        "destination": "/en/guruland-proxy/en/chon-buri/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/condo-directory/:path*",
        "destination": "/en/guruland-proxy/en/condo-directory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/condo-for-rent/:path*",
        "destination": "/en/guruland-proxy/en/condo-for-rent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/condo-for-sale/:path*",
        "destination": "/en/guruland-proxy/en/condo-for-sale/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/ddproperty-review-video/:path*",
        "destination": "/en/guruland-proxy/en/ddproperty-review-video/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/detached-house-for-rent/:path*",
        "destination": "/en/guruland-proxy/en/detached-house-for-rent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/detached-house-for-sale/:path*",
        "destination": "/en/guruland-proxy/en/detached-house-for-sale/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/feedback/:path*",
        "destination": "/en/guruland-proxy/en/feedback/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/en/:path*",
        "destination": "/en/guruland-proxy/en/en/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/events/:path*",
        "destination": "/en/guruland-proxy/en/events/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/iphone_app/:path*",
        "destination": "/en/guruland-proxy/en/iphone_app/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/khon-kaen/:path*",
        "destination": "/en/guruland-proxy/en/khon-kaen/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/land-for-rent/:path*",
        "destination": "/en/guruland-proxy/en/land-for-rent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/land-for-sale/:path*",
        "destination": "/en/guruland-proxy/en/land-for-sale/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/mobile/:path*",
        "destination": "/en/guruland-proxy/en/mobile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/mortgage_affordability_calculator/:path*",
        "destination": "/en/guruland-proxy/en/mortgage_affordability_calculator/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/mortgage_calc_interest_only/:path*",
        "destination": "/en/guruland-proxy/en/mortgage_calc_interest_only/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/mortgage_calc_monthly/:path*",
        "destination": "/en/guruland-proxy/en/mortgage_calc_monthly/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/mortgage_loan_calculator/:path*",
        "destination": "/en/guruland-proxy/en/mortgage_loan_calculator/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/mortgage_refinancing_calculator/:path*",
        "destination": "/en/guruland-proxy/en/mortgage_refinancing_calculator/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/myactivities/:path*",
        "destination": "/en/guruland-proxy/en/myactivities/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/myquestions/:path*",
        "destination": "/en/guruland-proxy/en/myquestions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/nakhon-pathom/:path*",
        "destination": "/en/guruland-proxy/en/nakhon-pathom/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/nakhon-ratchasima/:path*",
        "destination": "/en/guruland-proxy/en/nakhon-ratchasima/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/nearby/:path*",
        "destination": "/en/guruland-proxy/en/nearby/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/nearby-for-rent/:path*",
        "destination": "/en/guruland-proxy/en/nearby-for-rent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/nonthaburi/:path*",
        "destination": "/en/guruland-proxy/en/nonthaburi/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/office-space-for-sale/:path*",
        "destination": "/en/guruland-proxy/en/office-space-for-sale/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/pathum-thani/:path*",
        "destination": "/en/guruland-proxy/en/pathum-thani/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/phetchaburi/:path*",
        "destination": "/en/guruland-proxy/en/phetchaburi/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/phuket/:path*",
        "destination": "/en/guruland-proxy/en/phuket/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/prachin-buri/:path*",
        "destination": "/en/guruland-proxy/en/prachin-buri/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/prachuap-khiri-khan/:path*",
        "destination": "/en/guruland-proxy/en/prachuap-khiri-khan/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/privacy/:path*",
        "destination": "/en/guruland-proxy/en/privacy/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/project/:path*",
        "destination": "/en/guruland-proxy/en/project/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property-developer-video-lists/:path*",
        "destination": "/en/guruland-proxy/en/property-developer-video-lists/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property-investment-questions/:path*",
        "destination": "/en/guruland-proxy/en/property-investment-questions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property-listings/:path*",
        "destination": "/en/guruland-proxy/en/property-listings/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property-map-search/:path*",
        "destination": "/en/guruland-proxy/en/property-map-search/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property-mortgages-calculator/:path*",
        "destination": "/en/guruland-proxy/en/property-mortgages-calculator/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property-news/:path*",
        "destination": "/en/guruland-proxy/en/property-news/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/province/:path*",
        "destination": "/en/guruland-proxy/en/province/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/rayong/:path*",
        "destination": "/en/guruland-proxy/en/rayong/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/reviews/:path*",
        "destination": "/en/guruland-proxy/en/reviews/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/samut-prakan/:path*",
        "destination": "/en/guruland-proxy/en/samut-prakan/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/samut-sakhon/:path*",
        "destination": "/en/guruland-proxy/en/samut-sakhon/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/search_form/:path*",
        "destination": "/en/guruland-proxy/en/search_form/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/subscriptions/:path*",
        "destination": "/en/guruland-proxy/en/subscriptions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/terms-of-purchase/:path*",
        "destination": "/en/guruland-proxy/en/terms-of-purchase/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/terms-of-service/:path*",
        "destination": "/en/guruland-proxy/en/terms-of-service/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/thailand-property-resources/:path*",
        "destination": "/en/guruland-proxy/en/thailand-property-resources/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/thailand-real-estate-event/:path*",
        "destination": "/en/guruland-proxy/en/thailand-real-estate-event/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/thailand-real-estate-past-events/:path*",
        "destination": "/en/guruland-proxy/en/thailand-real-estate-past-events/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/townhouse-for-sale/:path*",
        "destination": "/en/guruland-proxy/en/townhouse-for-sale/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/user/login/:path*",
        "destination": "/en/guruland-proxy/en/user/login/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/user/profile/:path*",
        "destination": "/en/guruland-proxy/en/user/profile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/user/security-preferences/:path*",
        "destination": "/en/guruland-proxy/en/user/security-preferences/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/videos/:path*",
        "destination": "/en/guruland-proxy/en/videos/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/en/warehouse-factory-for-rent/:path*",
        "destination": "/en/guruland-proxy/en/warehouse-factory-for-rent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage_affordability_calculator/:path*",
        "destination": "/th/guruland-proxy/mortgage_affordability_calculator/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage_calc_interest_only/:path*",
        "destination": "/th/guruland-proxy/mortgage_calc_interest_only/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage_calc_monthly/:path*",
        "destination": "/th/guruland-proxy/mortgage_calc_monthly/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage_loan_calculator/:path*",
        "destination": "/th/guruland-proxy/mortgage_loan_calculator/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage_refinancing_calculator/:path*",
        "destination": "/th/guruland-proxy/mortgage_refinancing_calculator/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/agency/:path*",
        "destination": "/th/guruland-proxy/agency/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/agent/:path*",
        "destination": "/th/guruland-proxy/agent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/alert_unsubscribe/:path*",
        "destination": "/th/guruland-proxy/alert_unsubscribe/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/areainsider/:path*",
        "destination": "/th/guruland-proxy/areainsider/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-map-search/:path*",
        "destination": "/th/guruland-proxy/commercial-map-search/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/covid-19/:path*",
        "destination": "/th/guruland-proxy/covid-19/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/data-widget/:path*",
        "destination": "/th/guruland-proxy/data-widget/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/feed/:path*",
        "destination": "/th/guruland-proxy/feed/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/feedback/:path*",
        "destination": "/th/guruland-proxy/feedback/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/images/:path*",
        "destination": "/th/guruland-proxy/images/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/insights/:path*",
        "destination": "/th/guruland-proxy/insights/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/listing/:path*",
        "destination": "/th/guruland-proxy/listing/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/map-search/:path*",
        "destination": "/th/guruland-proxy/map-search/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage/:path*",
        "destination": "/th/guruland-proxy/mortgage/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/myactivities/:path*",
        "destination": "/th/guruland-proxy/myactivities/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/preview-listing/:path*",
        "destination": "/th/guruland-proxy/preview-listing/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/property-map-search/:path*",
        "destination": "/th/guruland-proxy/property-map-search/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/property-mortgages-calculator/:path*",
        "destination": "/th/guruland-proxy/property-mortgages-calculator/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/ps_dialog_refer/:path*",
        "destination": "/th/guruland-proxy/ps_dialog_refer/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/ps_dialog_sms_developer_listing/:path*",
        "destination": "/th/guruland-proxy/ps_dialog_sms_developer_listing/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/ps_dialog_sms_project/:path*",
        "destination": "/th/guruland-proxy/ps_dialog_sms_project/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/ps_xmlhttp_fullmapsearch/:path*",
        "destination": "/th/guruland-proxy/ps_xmlhttp_fullmapsearch/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/sitemap/:path*",
        "destination": "/th/guruland-proxy/sitemap/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/smartsearch/:path*",
        "destination": "/th/guruland-proxy/smartsearch/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/subscriptions/:path*",
        "destination": "/th/guruland-proxy/subscriptions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/tools/:path*",
        "destination": "/th/guruland-proxy/tools/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/user/:path*",
        "destination": "/th/guruland-proxy/user/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%81%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%B5%E0%B9%88/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%81%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%B5%E0%B9%88/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%9E/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%81%E0%B8%B2%E0%B8%8D%E0%B8%88%E0%B8%99%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%81%E0%B8%B2%E0%B8%8D%E0%B8%88%E0%B8%99%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%81%E0%B8%B2%E0%B8%AC%E0%B8%AA%E0%B8%B4%E0%B8%99%E0%B8%98%E0%B8%B8%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%81%E0%B8%B2%E0%B8%AC%E0%B8%AA%E0%B8%B4%E0%B8%99%E0%B8%98%E0%B8%B8%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%81%E0%B8%B3%E0%B9%81%E0%B8%9E%E0%B8%87%E0%B9%80%E0%B8%9E%E0%B8%8A%E0%B8%A3/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%81%E0%B8%B3%E0%B9%81%E0%B8%9E%E0%B8%87%E0%B9%80%E0%B8%9E%E0%B8%8A%E0%B8%A3/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B8%AD%E0%B8%99%E0%B9%81%E0%B8%81%E0%B9%88%E0%B8%99/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B8%AD%E0%B8%99%E0%B9%81%E0%B8%81%E0%B9%88%E0%B8%99/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%81%E0%B8%B4%E0%B8%88%E0%B8%81%E0%B8%B2%E0%B8%A3/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%81%E0%B8%B4%E0%B8%88%E0%B8%81%E0%B8%B2%E0%B8%A3/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%95%E0%B8%B6%E0%B8%81%E0%B9%81%E0%B8%96%E0%B8%A7-%E0%B8%AD%E0%B8%B2%E0%B8%84%E0%B8%B2%E0%B8%A3%E0%B8%9E%E0%B8%B2%E0%B8%93%E0%B8%B4%E0%B8%8A%E0%B8%A2%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%95%E0%B8%B6%E0%B8%81%E0%B9%81%E0%B8%96%E0%B8%A7-%E0%B8%AD%E0%B8%B2%E0%B8%84%E0%B8%B2%E0%B8%A3%E0%B8%9E%E0%B8%B2%E0%B8%93%E0%B8%B4%E0%B8%8A%E0%B8%A2%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C%E0%B9%80%E0%B8%AE%E0%B9%89%E0%B8%B2%E0%B8%AA%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C%E0%B9%80%E0%B8%AE%E0%B9%89%E0%B8%B2%E0%B8%AA%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B9%80%E0%B8%94%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%A7/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B9%80%E0%B8%94%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%A7/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%A7%E0%B8%B4%E0%B8%A5%E0%B8%A5%E0%B9%88%E0%B8%B2/%E0%B9%83%E0%B8%99%E0%B8%AB%E0%B8%B1%E0%B8%A7%E0%B8%AB%E0%B8%B4%E0%B8%99-th7707/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%A7%E0%B8%B4%E0%B8%A5%E0%B8%A5%E0%B9%88%E0%B8%B2/%E0%B9%83%E0%B8%99%E0%B8%AB%E0%B8%B1%E0%B8%A7%E0%B8%AB%E0%B8%B4%E0%B8%99-th7707/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%AA%E0%B8%B3%E0%B8%99%E0%B8%B1%E0%B8%81%E0%B8%87%E0%B8%B2%E0%B8%99/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%AA%E0%B8%B3%E0%B8%99%E0%B8%B1%E0%B8%81%E0%B8%87%E0%B8%B2%E0%B8%99/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%AD%E0%B8%9E%E0%B8%B2%E0%B8%A3%E0%B9%8C%E0%B8%97%E0%B9%80%E0%B8%A1%E0%B8%99%E0%B8%97%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%AD%E0%B8%9E%E0%B8%B2%E0%B8%A3%E0%B9%8C%E0%B8%97%E0%B9%80%E0%B8%A1%E0%B8%99%E0%B8%97%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%AD%E0%B8%AA%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B2%E0%B8%AF-%E0%B9%80%E0%B8%8A%E0%B8%B4%E0%B8%87%E0%B8%9E%E0%B8%B2%E0%B8%93%E0%B8%B4%E0%B8%8A%E0%B8%A2%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%AD%E0%B8%AA%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B2%E0%B8%AF-%E0%B9%80%E0%B8%8A%E0%B8%B4%E0%B8%87%E0%B8%9E%E0%B8%B2%E0%B8%93%E0%B8%B4%E0%B8%8A%E0%B8%A2%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B9%82%E0%B8%81%E0%B8%94%E0%B8%B1%E0%B8%87-%E0%B9%82%E0%B8%A3%E0%B8%87%E0%B8%87%E0%B8%B2%E0%B8%99/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B9%82%E0%B8%81%E0%B8%94%E0%B8%B1%E0%B8%87-%E0%B9%82%E0%B8%A3%E0%B8%87%E0%B8%87%E0%B8%B2%E0%B8%99/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B9%88%E0%B8%B2%E0%B8%A7%E0%B8%AD%E0%B8%AA%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B2%E0%B8%A3%E0%B8%B4%E0%B8%A1%E0%B8%97%E0%B8%A3%E0%B8%B1%E0%B8%9E%E0%B8%A2%E0%B9%8C-%E0%B8%9A%E0%B8%97%E0%B8%84%E0%B8%A7%E0%B8%B2%E0%B8%A1/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B9%88%E0%B8%B2%E0%B8%A7%E0%B8%AD%E0%B8%AA%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B2%E0%B8%A3%E0%B8%B4%E0%B8%A1%E0%B8%97%E0%B8%A3%E0%B8%B1%E0%B8%9E%E0%B8%A2%E0%B9%8C-%E0%B8%9A%E0%B8%97%E0%B8%84%E0%B8%A7%E0%B8%B2%E0%B8%A1/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%82%E0%B9%89%E0%B8%AD%E0%B8%95%E0%B8%81%E0%B8%A5%E0%B8%87%E0%B9%81%E0%B8%A5%E0%B8%B0%E0%B9%80%E0%B8%87%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%99%E0%B9%84%E0%B8%82%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%83%E0%B8%8A%E0%B9%89%E0%B8%9A%E0%B8%A3%E0%B8%B4%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%80%E0%B8%A7%E0%B9%87%E0%B8%9A%E0%B9%84%E0%B8%8B%E0%B8%95%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%82%E0%B9%89%E0%B8%AD%E0%B8%95%E0%B8%81%E0%B8%A5%E0%B8%87%E0%B9%81%E0%B8%A5%E0%B8%B0%E0%B9%80%E0%B8%87%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%99%E0%B9%84%E0%B8%82%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%83%E0%B8%8A%E0%B9%89%E0%B8%9A%E0%B8%A3%E0%B8%B4%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%80%E0%B8%A7%E0%B9%87%E0%B8%9A%E0%B9%84%E0%B8%8B%E0%B8%95%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%88%E0%B8%B1%E0%B8%99%E0%B8%97%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%88%E0%B8%B1%E0%B8%99%E0%B8%97%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%89%E0%B8%B0%E0%B9%80%E0%B8%8A%E0%B8%B4%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%A3%E0%B8%B2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%89%E0%B8%B0%E0%B9%80%E0%B8%8A%E0%B8%B4%E0%B8%87%E0%B9%80%E0%B8%97%E0%B8%A3%E0%B8%B2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%8A%E0%B8%A5%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%8A%E0%B8%A5%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%8A%E0%B8%B1%E0%B8%A2%E0%B8%99%E0%B8%B2%E0%B8%97/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%8A%E0%B8%B1%E0%B8%A2%E0%B8%99%E0%B8%B2%E0%B8%97/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%8A%E0%B8%B1%E0%B8%A2%E0%B8%A0%E0%B8%B9%E0%B8%A1%E0%B8%B4/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%8A%E0%B8%B1%E0%B8%A2%E0%B8%A0%E0%B8%B9%E0%B8%A1%E0%B8%B4/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%8A%E0%B8%B8%E0%B8%A1%E0%B8%9E%E0%B8%A3/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%8A%E0%B8%B8%E0%B8%A1%E0%B8%9E%E0%B8%A3/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%95%E0%B8%A3%E0%B8%B1%E0%B8%87/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%95%E0%B8%A3%E0%B8%B1%E0%B8%87/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%95%E0%B8%A3%E0%B8%B2%E0%B8%94/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%95%E0%B8%A3%E0%B8%B2%E0%B8%94/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%95%E0%B8%B2%E0%B8%81/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%95%E0%B8%B2%E0%B8%81/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%96%E0%B8%B2%E0%B8%A1%E0%B8%81%E0%B8%B9%E0%B8%A3%E0%B8%B9-%E0%B8%84%E0%B8%B3%E0%B8%96%E0%B8%B2%E0%B8%A1%E0%B8%82%E0%B8%AD%E0%B8%87%E0%B8%89%E0%B8%B1%E0%B8%99/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%96%E0%B8%B2%E0%B8%A1%E0%B8%81%E0%B8%B9%E0%B8%A3%E0%B8%B9-%E0%B8%84%E0%B8%B3%E0%B8%96%E0%B8%B2%E0%B8%A1%E0%B8%82%E0%B8%AD%E0%B8%87%E0%B8%89%E0%B8%B1%E0%B8%99/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%96%E0%B8%B2%E0%B8%A1%E0%B8%81%E0%B8%B9%E0%B8%A3%E0%B8%B9/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%96%E0%B8%B2%E0%B8%A1%E0%B8%81%E0%B8%B9%E0%B8%A3%E0%B8%B9/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%94%E0%B8%B4%E0%B8%99/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%94%E0%B8%B4%E0%B8%99/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%81/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%81/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%9B%E0%B8%90%E0%B8%A1/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%9B%E0%B8%90%E0%B8%A1/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%9E%E0%B8%99%E0%B8%A1/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%9E%E0%B8%99%E0%B8%A1/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%AA%E0%B8%B5%E0%B8%A1%E0%B8%B2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%AA%E0%B8%B5%E0%B8%A1%E0%B8%B2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%A8%E0%B8%A3%E0%B8%B5%E0%B8%98%E0%B8%A3%E0%B8%A3%E0%B8%A1%E0%B8%A3%E0%B8%B2%E0%B8%8A/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%A8%E0%B8%A3%E0%B8%B5%E0%B8%98%E0%B8%A3%E0%B8%A3%E0%B8%A1%E0%B8%A3%E0%B8%B2%E0%B8%8A/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%AA%E0%B8%A7%E0%B8%A3%E0%B8%A3%E0%B8%84%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%AA%E0%B8%A7%E0%B8%A3%E0%B8%A3%E0%B8%84%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%99%E0%B8%97%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B8%99%E0%B8%97%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%99%E0%B8%97%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B8%81%E0%B8%A3%E0%B8%A7%E0%B8%A2/%E0%B8%A7%E0%B8%B1%E0%B8%94%E0%B8%8A%E0%B8%A5%E0%B8%AD/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B8%99%E0%B8%97%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B8%81%E0%B8%A3%E0%B8%A7%E0%B8%A2/%E0%B8%A7%E0%B8%B1%E0%B8%94%E0%B8%8A%E0%B8%A5%E0%B8%AD/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%A3%E0%B8%B2%E0%B8%98%E0%B8%B4%E0%B8%A7%E0%B8%B2%E0%B8%AA/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B8%A3%E0%B8%B2%E0%B8%98%E0%B8%B4%E0%B8%A7%E0%B8%B2%E0%B8%AA/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%AB%E0%B8%99%E0%B9%89%E0%B8%B2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B9%82%E0%B8%A2%E0%B8%9A%E0%B8%B2%E0%B8%A2%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%83%E0%B8%8A%E0%B9%89%E0%B8%87%E0%B8%B2%E0%B8%99%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%AD%E0%B8%A1%E0%B8%A3%E0%B8%B1%E0%B8%9A%E0%B9%84%E0%B8%94%E0%B9%89/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B9%82%E0%B8%A2%E0%B8%9A%E0%B8%B2%E0%B8%A2%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%83%E0%B8%8A%E0%B9%89%E0%B8%87%E0%B8%B2%E0%B8%99%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%AD%E0%B8%A1%E0%B8%A3%E0%B8%B1%E0%B8%9A%E0%B9%84%E0%B8%94%E0%B9%89/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B9%82%E0%B8%A2%E0%B8%9A%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%A7%E0%B8%B2%E0%B8%A1%E0%B9%80%E0%B8%9B%E0%B9%87%E0%B8%99%E0%B8%AA%E0%B9%88%E0%B8%A7%E0%B8%99%E0%B8%95%E0%B8%B1%E0%B8%A7/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B9%82%E0%B8%A2%E0%B8%9A%E0%B8%B2%E0%B8%A2%E0%B8%84%E0%B8%A7%E0%B8%B2%E0%B8%A1%E0%B9%80%E0%B8%9B%E0%B9%87%E0%B8%99%E0%B8%AA%E0%B9%88%E0%B8%A7%E0%B8%99%E0%B8%95%E0%B8%B1%E0%B8%A7/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%99%E0%B9%88%E0%B8%B2%E0%B8%99/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%99%E0%B9%88%E0%B8%B2%E0%B8%99/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9A%E0%B8%B6%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%AC/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9A%E0%B8%B6%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%AC/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5%E0%B8%A3%E0%B8%B1%E0%B8%A1%E0%B8%A2%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5%E0%B8%A3%E0%B8%B1%E0%B8%A1%E0%B8%A2%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5%E0%B8%A3%E0%B8%B1%E0%B8%A1%E0%B8%A2%E0%B9%8C/%E0%B8%AB%E0%B8%99%E0%B8%AD%E0%B8%87%E0%B8%AB%E0%B8%87%E0%B8%AA%E0%B9%8C/%E0%B9%80%E0%B8%AA%E0%B8%B2%E0%B9%80%E0%B8%94%E0%B8%B5%E0%B8%A2%E0%B8%A7/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5%E0%B8%A3%E0%B8%B1%E0%B8%A1%E0%B8%A2%E0%B9%8C/%E0%B8%AB%E0%B8%99%E0%B8%AD%E0%B8%87%E0%B8%AB%E0%B8%87%E0%B8%AA%E0%B9%8C/%E0%B9%80%E0%B8%AA%E0%B8%B2%E0%B9%80%E0%B8%94%E0%B8%B5%E0%B8%A2%E0%B8%A7/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9B%E0%B8%97%E0%B8%B8%E0%B8%A1%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9B%E0%B8%97%E0%B8%B8%E0%B8%A1%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%88%E0%B8%A7%E0%B8%9A%E0%B8%84%E0%B8%B5%E0%B8%A3%E0%B8%B5%E0%B8%82%E0%B8%B1%E0%B8%99%E0%B8%98%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%88%E0%B8%A7%E0%B8%9A%E0%B8%84%E0%B8%B5%E0%B8%A3%E0%B8%B5%E0%B8%82%E0%B8%B1%E0%B8%99%E0%B8%98%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B9%84%E0%B8%97%E0%B8%A2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B9%80%E0%B8%97%E0%B8%A8%E0%B9%84%E0%B8%97%E0%B8%A2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9B%E0%B8%A3%E0%B8%B2%E0%B8%88%E0%B8%B5%E0%B8%99%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9B%E0%B8%A3%E0%B8%B2%E0%B8%88%E0%B8%B5%E0%B8%99%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9B%E0%B8%B1%E0%B8%95%E0%B8%95%E0%B8%B2%E0%B8%99%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9B%E0%B8%B1%E0%B8%95%E0%B8%95%E0%B8%B2%E0%B8%99%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%A8%E0%B8%A3%E0%B8%B5%E0%B8%AD%E0%B8%A2%E0%B8%B8%E0%B8%98%E0%B8%A2%E0%B8%B2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%99%E0%B8%84%E0%B8%A3%E0%B8%A8%E0%B8%A3%E0%B8%B5%E0%B8%AD%E0%B8%A2%E0%B8%B8%E0%B8%98%E0%B8%A2%E0%B8%B2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9E%E0%B8%B0%E0%B9%80%E0%B8%A2%E0%B8%B2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9E%E0%B8%B0%E0%B9%80%E0%B8%A2%E0%B8%B2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9E%E0%B8%B1%E0%B8%87%E0%B8%87%E0%B8%B2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9E%E0%B8%B1%E0%B8%87%E0%B8%87%E0%B8%B2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9E%E0%B8%B1%E0%B8%97%E0%B8%A2%E0%B8%B2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9E%E0%B8%B1%E0%B8%97%E0%B8%A2%E0%B8%B2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9E%E0%B8%B1%E0%B8%97%E0%B8%A5%E0%B8%B8%E0%B8%87/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9E%E0%B8%B1%E0%B8%97%E0%B8%A5%E0%B8%B8%E0%B8%87/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9E%E0%B8%B1%E0%B8%97%E0%B8%A5%E0%B8%B8%E0%B8%87/%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%9E%E0%B8%B1%E0%B8%97%E0%B8%A5%E0%B8%B8%E0%B8%87/%E0%B8%9B%E0%B8%A3%E0%B8%B2%E0%B8%87%E0%B8%AB%E0%B8%A1%E0%B8%B9%E0%B9%88/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9E%E0%B8%B1%E0%B8%97%E0%B8%A5%E0%B8%B8%E0%B8%87/%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%9E%E0%B8%B1%E0%B8%97%E0%B8%A5%E0%B8%B8%E0%B8%87/%E0%B8%9B%E0%B8%A3%E0%B8%B2%E0%B8%87%E0%B8%AB%E0%B8%A1%E0%B8%B9%E0%B9%88/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9E%E0%B8%B4%E0%B8%88%E0%B8%B4%E0%B8%95%E0%B8%A3/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9E%E0%B8%B4%E0%B8%88%E0%B8%B4%E0%B8%95%E0%B8%A3/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%9E%E0%B8%B4%E0%B8%A9%E0%B8%93%E0%B8%B8%E0%B9%82%E0%B8%A5%E0%B8%81/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%9E%E0%B8%B4%E0%B8%A9%E0%B8%93%E0%B8%B8%E0%B9%82%E0%B8%A5%E0%B8%81/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A0%E0%B8%B9%E0%B9%80%E0%B8%81%E0%B9%87%E0%B8%95/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A0%E0%B8%B9%E0%B9%80%E0%B8%81%E0%B9%87%E0%B8%95/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A1%E0%B8%AB%E0%B8%B2%E0%B8%AA%E0%B8%B2%E0%B8%A3%E0%B8%84%E0%B8%B2%E0%B8%A1/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A1%E0%B8%AB%E0%B8%B2%E0%B8%AA%E0%B8%B2%E0%B8%A3%E0%B8%84%E0%B8%B2%E0%B8%A1/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A1%E0%B8%B8%E0%B8%81%E0%B8%94%E0%B8%B2%E0%B8%AB%E0%B8%B2%E0%B8%A3/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A1%E0%B8%B8%E0%B8%81%E0%B8%94%E0%B8%B2%E0%B8%AB%E0%B8%B2%E0%B8%A3/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A2%E0%B8%B0%E0%B8%A5%E0%B8%B2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A2%E0%B8%B0%E0%B8%A5%E0%B8%B2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A2%E0%B9%82%E0%B8%AA%E0%B8%98%E0%B8%A3/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A2%E0%B9%82%E0%B8%AA%E0%B8%98%E0%B8%A3/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A8%E0%B8%82%E0%B8%B2%E0%B8%A2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A8%E0%B8%82%E0%B8%B2%E0%B8%A2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A8%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A8%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A8%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%81%E0%B8%B2%E0%B8%A8%E0%B9%83%E0%B8%AB%E0%B9%89%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%B0%E0%B8%99%E0%B8%AD%E0%B8%87/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A3%E0%B8%B0%E0%B8%99%E0%B8%AD%E0%B8%87/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%B0%E0%B8%A2%E0%B8%AD%E0%B8%87/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A3%E0%B8%B0%E0%B8%A2%E0%B8%AD%E0%B8%87/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%B2%E0%B8%A2%E0%B8%8A%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%AD%E0%B8%AA%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B2%E0%B8%A3%E0%B8%B4%E0%B8%A1%E0%B8%97%E0%B8%A3%E0%B8%B1%E0%B8%9E%E0%B8%A2%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A3%E0%B8%B2%E0%B8%A2%E0%B8%8A%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%AD%E0%B8%AA%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B2%E0%B8%A3%E0%B8%B4%E0%B8%A1%E0%B8%97%E0%B8%A3%E0%B8%B1%E0%B8%9E%E0%B8%A2%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B8%B5%E0%B8%A7%E0%B8%B4%E0%B8%A7/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A3%E0%B8%B5%E0%B8%A7%E0%B8%B4%E0%B8%A7/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%A2%E0%B9%80%E0%B8%AD%E0%B9%87%E0%B8%94/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A3%E0%B9%89%E0%B8%AD%E0%B8%A2%E0%B9%80%E0%B8%AD%E0%B9%87%E0%B8%94/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A5%E0%B8%9E%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A5%E0%B8%9E%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A5%E0%B8%B3%E0%B8%9B%E0%B8%B2%E0%B8%87/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A5%E0%B8%B3%E0%B8%9B%E0%B8%B2%E0%B8%87/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A5%E0%B8%B3%E0%B8%9B%E0%B8%B2%E0%B8%87/%E0%B8%AB%E0%B9%89%E0%B8%B2%E0%B8%87%E0%B8%89%E0%B8%B1%E0%B8%95%E0%B8%A3/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A5%E0%B8%B3%E0%B8%9B%E0%B8%B2%E0%B8%87/%E0%B8%AB%E0%B9%89%E0%B8%B2%E0%B8%87%E0%B8%89%E0%B8%B1%E0%B8%95%E0%B8%A3/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A5%E0%B8%B3%E0%B8%9E%E0%B8%B9%E0%B8%99/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A5%E0%B8%B3%E0%B8%9E%E0%B8%B9%E0%B8%99/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%A8%E0%B8%A3%E0%B8%B5%E0%B8%AA%E0%B8%B0%E0%B9%80%E0%B8%81%E0%B8%A9/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%A8%E0%B8%A3%E0%B8%B5%E0%B8%AA%E0%B8%B0%E0%B9%80%E0%B8%81%E0%B8%A9/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%81%E0%B8%A5%E0%B8%99%E0%B8%84%E0%B8%A3/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%81%E0%B8%A5%E0%B8%99%E0%B8%84%E0%B8%A3/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%87%E0%B8%82%E0%B8%A5%E0%B8%B2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%95%E0%B8%B9%E0%B8%A5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%95%E0%B8%B9%E0%B8%A5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%A1%E0%B8%B8%E0%B8%97%E0%B8%A3%E0%B8%9B%E0%B8%A3%E0%B8%B2%E0%B8%81%E0%B8%B2%E0%B8%A3/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%A1%E0%B8%B8%E0%B8%97%E0%B8%A3%E0%B8%9B%E0%B8%A3%E0%B8%B2%E0%B8%81%E0%B8%B2%E0%B8%A3/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%A1%E0%B8%B8%E0%B8%97%E0%B8%A3%E0%B8%AA%E0%B8%87%E0%B8%84%E0%B8%A3%E0%B8%B2%E0%B8%A1/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%A1%E0%B8%B8%E0%B8%97%E0%B8%A3%E0%B8%AA%E0%B8%87%E0%B8%84%E0%B8%A3%E0%B8%B2%E0%B8%A1/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%A1%E0%B8%B8%E0%B8%97%E0%B8%A3%E0%B8%AA%E0%B8%B2%E0%B8%84%E0%B8%A3/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%A1%E0%B8%B8%E0%B8%97%E0%B8%A3%E0%B8%AA%E0%B8%B2%E0%B8%84%E0%B8%A3/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%A3%E0%B8%B0%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%A3%E0%B8%B0%E0%B9%81%E0%B8%81%E0%B9%89%E0%B8%A7/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%A3%E0%B8%B0%E0%B9%81%E0%B8%81%E0%B9%89%E0%B8%A7/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%B4%E0%B8%87%E0%B8%AB%E0%B9%8C%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%B4%E0%B8%87%E0%B8%AB%E0%B9%8C%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%B8%E0%B8%9E%E0%B8%A3%E0%B8%A3%E0%B8%93%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%B8%E0%B8%9E%E0%B8%A3%E0%B8%A3%E0%B8%93%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%B8%E0%B8%A3%E0%B8%B2%E0%B8%A9%E0%B8%8E%E0%B8%A3%E0%B9%8C%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%B8%E0%B8%A3%E0%B8%B2%E0%B8%A9%E0%B8%8E%E0%B8%A3%E0%B9%8C%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%B8%E0%B8%A3%E0%B8%B4%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%B8%E0%B8%A3%E0%B8%B4%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AA%E0%B8%B8%E0%B9%82%E0%B8%82%E0%B8%97%E0%B8%B1%E0%B8%A2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AA%E0%B8%B8%E0%B9%82%E0%B8%82%E0%B8%97%E0%B8%B1%E0%B8%A2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AB%E0%B8%99%E0%B8%AD%E0%B8%87%E0%B8%84%E0%B8%B2%E0%B8%A2/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AB%E0%B8%99%E0%B8%AD%E0%B8%87%E0%B8%84%E0%B8%B2%E0%B8%A2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AB%E0%B8%99%E0%B8%AD%E0%B8%87%E0%B8%9A%E0%B8%B1%E0%B8%A7%E0%B8%A5%E0%B8%B3%E0%B8%A0%E0%B8%B9/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AB%E0%B8%99%E0%B8%AD%E0%B8%87%E0%B8%9A%E0%B8%B1%E0%B8%A7%E0%B8%A5%E0%B8%B3%E0%B8%A0%E0%B8%B9/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AD%E0%B8%AA%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B2%E0%B8%AF-%E0%B9%80%E0%B8%8A%E0%B8%B4%E0%B8%87%E0%B8%9E%E0%B8%B2%E0%B8%93%E0%B8%B4%E0%B8%8A%E0%B8%A2%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AD%E0%B8%AA%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B2%E0%B8%AF-%E0%B9%80%E0%B8%8A%E0%B8%B4%E0%B8%87%E0%B8%9E%E0%B8%B2%E0%B8%93%E0%B8%B4%E0%B8%8A%E0%B8%A2%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AD%E0%B8%B3%E0%B8%99%E0%B8%B2%E0%B8%88%E0%B9%80%E0%B8%88%E0%B8%A3%E0%B8%B4%E0%B8%8D/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AD%E0%B8%B3%E0%B8%99%E0%B8%B2%E0%B8%88%E0%B9%80%E0%B8%88%E0%B8%A3%E0%B8%B4%E0%B8%8D/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AD%E0%B8%B8%E0%B8%94%E0%B8%A3%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AD%E0%B8%B8%E0%B8%94%E0%B8%A3%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AD%E0%B8%B8%E0%B8%95%E0%B8%A3%E0%B8%94%E0%B8%B4%E0%B8%95%E0%B8%96%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AD%E0%B8%B8%E0%B8%95%E0%B8%A3%E0%B8%94%E0%B8%B4%E0%B8%95%E0%B8%96%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AD%E0%B8%B8%E0%B8%97%E0%B8%B1%E0%B8%A2%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AD%E0%B8%B8%E0%B8%97%E0%B8%B1%E0%B8%A2%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AD%E0%B8%B8%E0%B8%9A%E0%B8%A5%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AD%E0%B8%B8%E0%B8%9A%E0%B8%A5%E0%B8%A3%E0%B8%B2%E0%B8%8A%E0%B8%98%E0%B8%B2%E0%B8%99%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%AD%E0%B9%88%E0%B8%B2%E0%B8%87%E0%B8%97%E0%B8%AD%E0%B8%87/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%AD%E0%B9%88%E0%B8%B2%E0%B8%87%E0%B8%97%E0%B8%AD%E0%B8%87/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%87%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%99%E0%B9%84%E0%B8%82%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%8B%E0%B8%B7%E0%B9%89%E0%B8%AD%E0%B8%82%E0%B8%B2%E0%B8%A2/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%87%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%99%E0%B9%84%E0%B8%82%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B8%8B%E0%B8%B7%E0%B9%89%E0%B8%AD%E0%B8%82%E0%B8%B2%E0%B8%A2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B8%B5%E0%B8%A2%E0%B8%87%E0%B8%A3%E0%B8%B2%E0%B8%A2/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%8A%E0%B8%B5%E0%B8%A2%E0%B8%87%E0%B8%A3%E0%B8%B2%E0%B8%A2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B8%B5%E0%B8%A2%E0%B8%87%E0%B8%A3%E0%B8%B2%E0%B8%A2/%E0%B9%81%E0%B8%A1%E0%B9%88%E0%B8%88%E0%B8%B1%E0%B8%99/%E0%B8%9B%E0%B9%88%E0%B8%B2%E0%B8%95%E0%B8%B6%E0%B8%87/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%8A%E0%B8%B5%E0%B8%A2%E0%B8%87%E0%B8%A3%E0%B8%B2%E0%B8%A2/%E0%B9%81%E0%B8%A1%E0%B9%88%E0%B8%88%E0%B8%B1%E0%B8%99/%E0%B8%9B%E0%B9%88%E0%B8%B2%E0%B8%95%E0%B8%B6%E0%B8%87/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B8%B5%E0%B8%A2%E0%B8%87%E0%B9%83%E0%B8%AB%E0%B8%A1%E0%B9%88/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%8A%E0%B8%B5%E0%B8%A2%E0%B8%87%E0%B9%83%E0%B8%AB%E0%B8%A1%E0%B9%88/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B8%B5%E0%B8%A2%E0%B8%87%E0%B9%83%E0%B8%AB%E0%B8%A1%E0%B9%88/%E0%B8%94%E0%B8%AD%E0%B8%A2%E0%B8%AA%E0%B8%B0%E0%B9%80%E0%B8%81%E0%B9%87%E0%B8%94/%E0%B8%95%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B9%83%E0%B8%AB%E0%B8%8D%E0%B9%88/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%8A%E0%B8%B5%E0%B8%A2%E0%B8%87%E0%B9%83%E0%B8%AB%E0%B8%A1%E0%B9%88/%E0%B8%94%E0%B8%AD%E0%B8%A2%E0%B8%AA%E0%B8%B0%E0%B9%80%E0%B8%81%E0%B9%87%E0%B8%94/%E0%B8%95%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B9%83%E0%B8%AB%E0%B8%8D%E0%B9%88/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%95%E0%B8%B6%E0%B8%81%E0%B9%81%E0%B8%96%E0%B8%A7-%E0%B8%AD%E0%B8%B2%E0%B8%84%E0%B8%B2%E0%B8%A3%E0%B8%9E%E0%B8%B2%E0%B8%93%E0%B8%B4%E0%B8%8A%E0%B8%A2%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%95%E0%B8%B6%E0%B8%81%E0%B9%81%E0%B8%96%E0%B8%A7-%E0%B8%AD%E0%B8%B2%E0%B8%84%E0%B8%B2%E0%B8%A3%E0%B8%9E%E0%B8%B2%E0%B8%93%E0%B8%B4%E0%B8%8A%E0%B8%A2%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C%E0%B9%80%E0%B8%AE%E0%B9%89%E0%B8%B2%E0%B8%AA%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C%E0%B9%80%E0%B8%AE%E0%B9%89%E0%B8%B2%E0%B8%AA%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B9%80%E0%B8%94%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%A7/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B9%80%E0%B8%94%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%A7/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%9E%E0%B8%B7%E0%B9%89%E0%B8%99%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%82%E0%B8%AD%E0%B8%87/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%9E%E0%B8%B7%E0%B9%89%E0%B8%99%E0%B8%97%E0%B8%B5%E0%B9%88%E0%B8%82%E0%B8%B2%E0%B8%A2%E0%B8%82%E0%B8%AD%E0%B8%87/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%AA%E0%B8%B3%E0%B8%99%E0%B8%B1%E0%B8%81%E0%B8%87%E0%B8%B2%E0%B8%99/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%AA%E0%B8%B3%E0%B8%99%E0%B8%B1%E0%B8%81%E0%B8%87%E0%B8%B2%E0%B8%99/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%AD%E0%B8%9E%E0%B8%B2%E0%B8%A3%E0%B9%8C%E0%B8%97%E0%B9%80%E0%B8%A1%E0%B8%99%E0%B8%97%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%AD%E0%B8%9E%E0%B8%B2%E0%B8%A3%E0%B9%8C%E0%B8%97%E0%B9%80%E0%B8%A1%E0%B8%99%E0%B8%97%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%AD%E0%B8%AA%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B2%E0%B8%AF-%E0%B9%80%E0%B8%8A%E0%B8%B4%E0%B8%87%E0%B8%9E%E0%B8%B2%E0%B8%93%E0%B8%B4%E0%B8%8A%E0%B8%A2%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B8%AD%E0%B8%AA%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B2%E0%B8%AF-%E0%B9%80%E0%B8%8A%E0%B8%B4%E0%B8%87%E0%B8%9E%E0%B8%B2%E0%B8%93%E0%B8%B4%E0%B8%8A%E0%B8%A2%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B9%82%E0%B8%81%E0%B8%94%E0%B8%B1%E0%B8%87-%E0%B9%82%E0%B8%A3%E0%B8%87%E0%B8%87%E0%B8%B2%E0%B8%99/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2%E0%B9%82%E0%B8%81%E0%B8%94%E0%B8%B1%E0%B8%87-%E0%B9%82%E0%B8%A3%E0%B8%87%E0%B8%87%E0%B8%B2%E0%B8%99/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%9E%E0%B8%8A%E0%B8%A3%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%9E%E0%B8%8A%E0%B8%A3%E0%B8%9A%E0%B8%B8%E0%B8%A3%E0%B8%B5/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%9E%E0%B8%8A%E0%B8%A3%E0%B8%9A%E0%B8%B9%E0%B8%A3%E0%B8%93%E0%B9%8C/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%9E%E0%B8%8A%E0%B8%A3%E0%B8%9A%E0%B8%B9%E0%B8%A3%E0%B8%93%E0%B9%8C/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%A5%E0%B8%A2/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%A5%E0%B8%A2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%80%E0%B8%A5%E0%B8%A2/%E0%B9%80%E0%B8%8A%E0%B8%B5%E0%B8%A2%E0%B8%87%E0%B8%84%E0%B8%B2%E0%B8%99/%E0%B8%9B%E0%B8%B2%E0%B8%81%E0%B8%95%E0%B8%A1/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%80%E0%B8%A5%E0%B8%A2/%E0%B9%80%E0%B8%8A%E0%B8%B5%E0%B8%A2%E0%B8%87%E0%B8%84%E0%B8%B2%E0%B8%99/%E0%B8%9B%E0%B8%B2%E0%B8%81%E0%B8%95%E0%B8%A1/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%81%E0%B8%9E%E0%B8%A3%E0%B9%88/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%81%E0%B8%9E%E0%B8%A3%E0%B9%88/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%81%E0%B8%A1%E0%B9%88%E0%B8%AE%E0%B9%88%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%AD%E0%B8%99/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%81%E0%B8%A1%E0%B9%88%E0%B8%AE%E0%B9%88%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%AD%E0%B8%99/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%81%E0%B8%A1%E0%B9%88%E0%B8%AE%E0%B9%88%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%AD%E0%B8%99/%E0%B9%81%E0%B8%A1%E0%B9%88%E0%B8%AA%E0%B8%B0%E0%B9%80%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B8%87/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%81%E0%B8%A1%E0%B9%88%E0%B8%AE%E0%B9%88%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%AD%E0%B8%99/%E0%B9%81%E0%B8%A1%E0%B9%88%E0%B8%AA%E0%B8%B0%E0%B9%80%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B8%87/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%81%E0%B8%AB%E0%B8%A5%E0%B9%88%E0%B8%87%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%84%E0%B8%A7%E0%B8%B2%E0%B8%A1%E0%B8%A3%E0%B8%B9%E0%B9%89%E0%B8%8B%E0%B8%B7%E0%B9%89%E0%B8%AD-%E0%B8%82%E0%B8%B2%E0%B8%A2-%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%81%E0%B8%AB%E0%B8%A5%E0%B9%88%E0%B8%87%E0%B8%A3%E0%B8%A7%E0%B8%A1%E0%B8%84%E0%B8%A7%E0%B8%B2%E0%B8%A1%E0%B8%A3%E0%B8%B9%E0%B9%89%E0%B8%8B%E0%B8%B7%E0%B9%89%E0%B8%AD-%E0%B8%82%E0%B8%B2%E0%B8%A2-%E0%B9%80%E0%B8%8A%E0%B9%88%E0%B8%B2/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3-%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%82%E0%B8%94/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3/:path*",
        "destination": "/th/guruland-proxy/%E0%B9%82%E0%B8%84%E0%B8%A3%E0%B8%87%E0%B8%81%E0%B8%B2%E0%B8%A3/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*ddproperty\\.com(?::[0-9]+)?$"
          }
        ],
        "source": "/%E0%B8%88%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%A7%E0%B8%B1%E0%B8%94/:path*",
        "destination": "/th/guruland-proxy/%E0%B8%88%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%A7%E0%B8%B1%E0%B8%94/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/",
        "destination": "/en/consumer/home"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-agents/:path(condo|residential-district|commercial-area|commercial-district|residential-area|kuala-lumpur|selangor|penang|johor|kedah|kelantan|labuan|melaka|negeri-sembilan|pahang|perak|perlis|putrajaya|sabah|sarawak|terengganu|most-active-agents|most-voted-agents)",
        "destination": "/en/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-agents/find-agent",
        "destination": "/en/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-developers/:path*",
        "destination": "/en/developer/profile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-listing/project/:path*",
        "destination": "/en/developer/pldp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-listing/:path*",
        "destination": "/en/consumer/ldp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/new-property-launch",
        "destination": "/en/developer/new-launch"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage",
        "destination": "/en/finance/mortgage"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/user/consent",
        "destination": "/en/consumer/user-consent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/watchlist",
        "destination": "/en/consumer/watchlist"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage/home-loan",
        "destination": "/en/finance/home-loan"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/open-app",
        "destination": "/en/consumer/open-app"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/condo-hp/:path*",
        "destination": "/en/consumer/condo-directory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/condo/:slug-:id((?=.*[a-zA-Z])[a-zA-Z0-9]+)/:page(\\d+)",
        "destination": "/en/consumer/condo-directory/:slug-:id/:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/condo/:slug-:id((?=.*[a-zA-Z])[a-zA-Z0-9]+)",
        "destination": "/en/consumer/condo-directory/:slug-:id"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/condo/:page(\\d+)",
        "destination": "/en/consumer/condo-directory/:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/condo",
        "destination": "/en/consumer/condo-directory"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/contact-consumer/:path*",
        "destination": "/en/consumer/contact-consumer/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/contact-agent/:path*",
        "destination": "/en/consumer/contact-agent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/pdp-temp/:path*",
        "destination": "/en/consumer/pdp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm",
        "destination": "/ms/consumer/home"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/ejen-hartanah/:path(pakar-kondo|daerah-perumahan|kawasan-perumahan|daerah-komersial|kawasan-komersial|kuala-lumpur|selangor|penang|johor|kedah|kelantan|labuan|melaka|negeri-sembilan|pahang|perak|perlis|putrajaya|sabah|sarawak|terengganu|pakar-askguru-dengan-jawapan|pakar-askguru-dengan-undi)",
        "destination": "/ms/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/ejen-hartanah/cari-ejen",
        "destination": "/ms/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/pemaju-hartanah/:path*",
        "destination": "/ms/developer/profile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/senarai-hartanah/projek/:path*",
        "destination": "/ms/developer/pldp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/senarai-hartanah/:path*",
        "destination": "/ms/consumer/ldp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/perumahan-baru",
        "destination": "/ms/developer/new-launch"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/gadai-janji",
        "destination": "/ms/finance/mortgage"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/user/consent",
        "destination": "/ms/consumer/user-consent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/mortgage/home-loan",
        "destination": "/ms/finance/home-loan"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/watchlist",
        "destination": "/ms/consumer/watchlist"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/open-app",
        "destination": "/ms/consumer/open-app"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/kondo-hp/:path*",
        "destination": "/ms/consumer/condo-directory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/kondo/:slug-:id((?=.*[a-zA-Z])[a-zA-Z0-9]+)/:page(\\d+)",
        "destination": "/ms/consumer/condo-directory/:slug-:id/:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/kondo/:slug-:id((?=.*[a-zA-Z])[a-zA-Z0-9]+)",
        "destination": "/ms/consumer/condo-directory/:slug-:id"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/kondo/:page(\\d+)",
        "destination": "/ms/consumer/condo-directory/:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/kondo",
        "destination": "/ms/consumer/condo-directory"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/contact-agent/:path*",
        "destination": "/ms/consumer/contact-agent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/pdp-temp/:path*",
        "destination": "/ms/consumer/pdp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-property/p/:freetext/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=sale&freetext=:freetext&page=:page&isCommercial=true&propertyTypeSlug=commercial-property"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-property/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=sale&isCommercial=true&propertyTypeSlug=commercial-property"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-search-proxy/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=sale&page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-for-:listingType/p/:freetext/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/residential-properties-for-:listingType/p/:freetext/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/residential-properties-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-properties-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-property-for-:listingType/p/:freetext/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page&isCommercial=true&propertyTypeSlug=commercial-property"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&isCommercial=true&propertyTypeSlug=commercial-property"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:districtSlug/:propertyTypeSlug-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?provinceSlug=:provinceSlug&locationSlug=:districtSlug&propertyTypeSlug=:propertyTypeSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:propertyTypeSlug-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?locationSlug=:provinceSlug&propertyTypeSlug=:propertyTypeSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:districtSlug/for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?provinceSlug=:provinceSlug&locationSlug=:districtSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?locationSlug=:provinceSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeSlug((?!search-property.*)[^/]+)/:locationSlug/property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug&locationSlug=:locationSlug&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeSlug((?!commercial-properties|residential-properties).*)-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/similar-listing/:page(\\d+)?",
        "destination": "/en/consumer/srp?page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-komersial/p/:freetext/:page(\\d+)?",
        "destination": "/ms/consumer/srp/search?listingType=dijual&freetext=:freetext&page=:page&isCommercial=true&propertyTypeSlug=hartanah-komersial"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-komersial/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=dijual&isCommercial=true&propertyTypeSlug=hartanah-komersial"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/property-search-proxy/:page(\\d+)?",
        "destination": "/ms/consumer/srp/search?listingType=dijual&page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-:listingType(dijual|disewa)/p/:freetext/:page(\\d+)?",
        "destination": "/ms/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-:listingType(dijual|disewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=:listingType"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-kediaman-:listingType(dijual|disewa)/p/:freetext/:page(\\d+)?",
        "destination": "/ms/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-kediaman-:listingType(dijual|disewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=:listingType&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-komersial-:listingType(dijual|disewa)/p/:freetext/:page(\\d+)?",
        "destination": "/ms/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page&isCommercial=true&propertyTypeSlug=hartanah-komersial"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-komersial-:listingType(dijual|disewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=:listingType&isCommercial=true&propertyTypeSlug=hartanah-komersial"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:districtSlug/:propertyTypeSlug-:listingType(dijual|disewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?provinceSlug=:provinceSlug&districtSlug=:districtSlug&propertyTypeSlug=:propertyTypeSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:propertyTypeSlug-:listingType(dijual|disewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?provinceSlug=:provinceSlug&propertyTypeSlug=:propertyTypeSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:districtSlug/:listingType(dijual|disewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?provinceSlug=:provinceSlug&districtSlug=:districtSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:listingType(dijual|disewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?provinceSlug=:provinceSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:propertyTypeSlug((?!search-property.*)[^/]+)/:locationSlug/hartanah-:listingType(dijual|disewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug&locationSlug=:locationSlug&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:propertyTypeSlug-:listingType(dijual|disewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/similar-listing/:page(\\d+)?",
        "destination": "/ms/consumer/srp?page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/about/:path*",
        "destination": "/en/guruland-proxy/about/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/account/:path*",
        "destination": "/en/guruland-proxy/account/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/advertise-with-us/:path*",
        "destination": "/en/guruland-proxy/advertise-with-us/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/agent/:path*",
        "destination": "/en/guruland-proxy/agent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/alert_unsubscribe/:path*",
        "destination": "/en/guruland-proxy/alert_unsubscribe/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/alerts-landing/:path*",
        "destination": "/en/guruland-proxy/alerts-landing/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/areainsider/:path*",
        "destination": "/en/guruland-proxy/areainsider/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/blog/:path*",
        "destination": "/en/guruland-proxy/blog/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-property/:path*",
        "destination": "/en/guruland-proxy/commercial-property/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/condo/:path*",
        "destination": "/en/guruland-proxy/condo/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/covid-19/:path*",
        "destination": "/en/guruland-proxy/covid-19/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/customer-service/:path*",
        "destination": "/en/guruland-proxy/customer-service/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/en/about/:path*",
        "destination": "/en/guruland-proxy/en/about/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/en/agent-register-activation-confirmation/:path*",
        "destination": "/en/guruland-proxy/en/agent-register-activation-confirmation/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/en/agent-register-verification/:path*",
        "destination": "/en/guruland-proxy/en/agent-register-verification/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/en/agents/:path*",
        "destination": "/en/guruland-proxy/en/agents/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/en/customer-service/:path*",
        "destination": "/en/guruland-proxy/en/customer-service/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/en/privacy/:path*",
        "destination": "/en/guruland-proxy/en/privacy/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property-listing/:path*",
        "destination": "/en/guruland-proxy/en/property-listing/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property-mortgages-calculator/:path*",
        "destination": "/en/guruland-proxy/en/property-mortgages-calculator/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/en/property-news/:path*",
        "destination": "/en/guruland-proxy/en/property-news/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/en/user-sent-messages/:path*",
        "destination": "/en/guruland-proxy/en/user-sent-messages/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/events/:path*",
        "destination": "/en/guruland-proxy/events/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/facebook/:path*",
        "destination": "/en/guruland-proxy/facebook/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/featured-agent/:path*",
        "destination": "/en/guruland-proxy/featured-agent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/feedback/:path*",
        "destination": "/en/guruland-proxy/feedback/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/guru-picks/:path*",
        "destination": "/en/guruland-proxy/guru-picks/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/insights/:path*",
        "destination": "/en/guruland-proxy/insights/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/kyc/:path*",
        "destination": "/en/guruland-proxy/kyc/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/labuan/:path*",
        "destination": "/en/guruland-proxy/labuan/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/listing/:path*",
        "destination": "/en/guruland-proxy/listing/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/login/:path*",
        "destination": "/en/guruland-proxy/login/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/logout/:path*",
        "destination": "/en/guruland-proxy/logout/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/maintenance/:path*",
        "destination": "/en/guruland-proxy/maintenance/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/markettools/:path*",
        "destination": "/en/guruland-proxy/markettools/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/media/:path*",
        "destination": "/en/guruland-proxy/media/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/media/press-release/:path*",
        "destination": "/en/guruland-proxy/media/press-release/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/mobile/:path*",
        "destination": "/en/guruland-proxy/mobile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage/:path*",
        "destination": "/en/guruland-proxy/mortgage/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/myactivities/:path*",
        "destination": "/en/guruland-proxy/myactivities/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/myquestions/:path*",
        "destination": "/en/guruland-proxy/myquestions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/new-semi-detached-house-launch/:path*",
        "destination": "/en/guruland-proxy/new-semi-detached-house-launch/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/news-alert/:path*",
        "destination": "/en/guruland-proxy/news-alert/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/own-your-home/:path*",
        "destination": "/en/guruland-proxy/own-your-home/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/payment-method/:path*",
        "destination": "/en/guruland-proxy/payment-method/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/pengguna/:path*",
        "destination": "/en/guruland-proxy/pengguna/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/popular-areas/:path*",
        "destination": "/en/guruland-proxy/popular-areas/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/preview-listing/:path*",
        "destination": "/en/guruland-proxy/preview-listing/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/privacy/:path*",
        "destination": "/en/guruland-proxy/privacy/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/privasi/:path*",
        "destination": "/en/guruland-proxy/privasi/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/product/:path*",
        "destination": "/en/guruland-proxy/product/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-agents/:path*",
        "destination": "/en/guruland-proxy/property-agents/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-forum/:path*",
        "destination": "/en/guruland-proxy/property-forum/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-guides/:path*",
        "destination": "/en/guruland-proxy/property-guides/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-map-search/:path*",
        "destination": "/en/guruland-proxy/property-map-search/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-mortgages-calculator/:path*",
        "destination": "/en/guruland-proxy/property-mortgages-calculator/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-news/:path*",
        "destination": "/en/guruland-proxy/property-news/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-search/:path*",
        "destination": "/en/guruland-proxy/property-search/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/putrajaya/:path*",
        "destination": "/en/guruland-proxy/putrajaya/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/q/:path*",
        "destination": "/en/guruland-proxy/q/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/qvform/:path*",
        "destination": "/en/guruland-proxy/qvform/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/real-estate/:path*",
        "destination": "/en/guruland-proxy/real-estate/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/register-confirmation/:path*",
        "destination": "/en/guruland-proxy/register-confirmation/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/resource/:path*",
        "destination": "/en/guruland-proxy/resource/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/resources/:path*",
        "destination": "/en/guruland-proxy/resources/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/shortlist/:path*",
        "destination": "/en/guruland-proxy/shortlist/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/sitemap/:path*",
        "destination": "/en/guruland-proxy/sitemap/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/state/:path*",
        "destination": "/en/guruland-proxy/state/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/subscriptions/:path*",
        "destination": "/en/guruland-proxy/subscriptions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/take-down-policy/:path*",
        "destination": "/en/guruland-proxy/take-down-policy/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/terms-of-service/:path*",
        "destination": "/en/guruland-proxy/terms-of-service/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/user/:path*",
        "destination": "/en/guruland-proxy/user/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/valuation/:path*",
        "destination": "/en/guruland-proxy/valuation/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/viewvaluation/:path*",
        "destination": "/en/guruland-proxy/viewvaluation/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/universities/:path*",
        "destination": "/en/guruland-proxy/universities/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/factory/:path*",
        "destination": "/en/guruland-proxy/factory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/offices/:path*",
        "destination": "/en/guruland-proxy/offices/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/classroom/:path*",
        "destination": "/en/guruland-proxy/classroom/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bungalow/:path*",
        "destination": "/en/guruland-proxy/bungalow/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/semi-d/:path*",
        "destination": "/en/guruland-proxy/semi-d/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/warehouse/:path*",
        "destination": "/en/guruland-proxy/warehouse/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/shop/:path*",
        "destination": "/en/guruland-proxy/shop/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/johor/:path*",
        "destination": "/en/guruland-proxy/johor/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/kedah/:path*",
        "destination": "/en/guruland-proxy/kedah/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/kelantan/:path*",
        "destination": "/en/guruland-proxy/kelantan/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/kuala-lumpur/:path*",
        "destination": "/en/guruland-proxy/kuala-lumpur/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/malaysia/:path*",
        "destination": "/en/guruland-proxy/malaysia/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/perlis/:path*",
        "destination": "/en/guruland-proxy/perlis/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/melaka/:path*",
        "destination": "/en/guruland-proxy/melaka/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/negeri-sembilan/:path*",
        "destination": "/en/guruland-proxy/negeri-sembilan/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/pahang/:path*",
        "destination": "/en/guruland-proxy/pahang/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/penang/:path*",
        "destination": "/en/guruland-proxy/penang/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/perak/:path*",
        "destination": "/en/guruland-proxy/perak/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/sabah/:path*",
        "destination": "/en/guruland-proxy/sabah/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/sarawak/:path*",
        "destination": "/en/guruland-proxy/sarawak/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/selangor/:path*",
        "destination": "/en/guruland-proxy/selangor/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/terengganu/:path*",
        "destination": "/en/guruland-proxy/terengganu/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/kondo/:path*",
        "destination": "/ms/guruland-proxy/bm/kondo/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/ejen/:path*",
        "destination": "/ms/guruland-proxy/bm/ejen/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/ejen-hartanah/:path*",
        "destination": "/ms/guruland-proxy/bm/ejen-hartanah/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/perumahan-baru/review/:path*",
        "destination": "/ms/guruland-proxy/bm/perumahan-baru/review/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/logout/:path*",
        "destination": "/ms/guruland-proxy/bm/logout/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/berita-hartanah/:path*",
        "destination": "/ms/guruland-proxy/bm/berita-hartanah/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/forum-hartanah/:path*",
        "destination": "/ms/guruland-proxy/bm/forum-hartanah/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/myactivities/enquiries/:path*",
        "destination": "/ms/guruland-proxy/bm/myactivities/enquiries/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/feedback/:path*",
        "destination": "/ms/guruland-proxy/bm/feedback/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/pinjaman-rumah/kalkulator-kemampuan-beli-rumah/:path*",
        "destination": "/ms/guruland-proxy/bm/pinjaman-rumah/kalkulator-kemampuan-beli-rumah/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/sumber-hartanah/:path*",
        "destination": "/ms/guruland-proxy/bm/sumber-hartanah/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/peta-pencarian-lokasi/:path*",
        "destination": "/ms/guruland-proxy/bm/peta-pencarian-lokasi/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/areainsider/:path*",
        "destination": "/ms/guruland-proxy/bm/areainsider/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-komersial/:path*",
        "destination": "/ms/guruland-proxy/bm/hartanah-komersial/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/myactivities/:path*",
        "destination": "/ms/guruland-proxy/bm/myactivities/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/pengguna/:path*",
        "destination": "/ms/guruland-proxy/bm/pengguna/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/subscriptions/:path*",
        "destination": "/ms/guruland-proxy/bm/subscriptions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/myquestions/:path*",
        "destination": "/ms/guruland-proxy/bm/myquestions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/pinjaman-rumah/kalkulator/pembiayaan-ansuran-rumah/:path*",
        "destination": "/ms/guruland-proxy/bm/pinjaman-rumah/kalkulator/pembiayaan-ansuran-rumah/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:prefix-dijual/:path*",
        "destination": "/ms/guruland-proxy/:prefix-dijual/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:prefix-disewa/:path*",
        "destination": "/ms/guruland-proxy/:prefix-disewa/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/",
        "destination": "/en/consumer/home"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/agent/:path*",
        "destination": "/en/consumer/agent-profile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/developer/:path*",
        "destination": "/en/developer/profile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/listing/project/:path*",
        "destination": "/en/developer/pldp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/listing/:path*/markdown",
        "destination": "/api/consumer/markdown/ldp/:path*/markdown"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/listing/:path*",
        "destination": "/en/consumer/ldp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/home-sellers",
        "destination": "/en/consumer/home-sellers/landing"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/home-sellers/onboarding/:tab*",
        "destination": "/en/consumer/home-sellers/seller-journey/:tab*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/home-sellers/dashboard",
        "destination": "/en/finance/home-sellers/dashboard"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/home-sellers/dashboard/:tab*",
        "destination": "/en/finance/home-sellers/dashboard/:tab*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/home-sellers/property-valuation-tool",
        "destination": "/en/consumer/home-sellers/valuation"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/home-sellers/valuation",
        "destination": "/en/consumer/home-sellers/valuation"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/new-project-launch",
        "destination": "/en/developer/new-launch"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-agent-singapore/find-agent/:path*",
        "destination": "/en/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-agent-singapore/specialist/:path*",
        "destination": "/en/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-agent-singapore/:path+",
        "destination": "/en/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/user/consent",
        "destination": "/en/consumer/user-consent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/user/preferences",
        "destination": "/en/consumer/user-preferences"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-property-listing/hdb/:estate/:district/:hdb/last-transacted-prices-and-insights",
        "destination": "/en/guruland-proxy/singapore-property-listing/hdb/:estate/:district/:hdb/last-transacted-prices-and-insights"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-property-listing/hdb/:estate/:district/:hdb",
        "destination": "/en/guruland-proxy/singapore-property-listing/hdb/:estate/:district/:hdb"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-property-listing/hdb/hdb-singapore-estates",
        "destination": "/en/guruland-proxy/singapore-property-listing/hdb/hdb-singapore-estates"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-property-listing/hdb",
        "destination": "/en/consumer/hdb"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-property-listing/hdb/:estate*",
        "destination": "/en/consumer/hdb/:estate*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-property-listing/hdb/:estate*/:street*",
        "destination": "/en/consumer/hdb/:estate*/:street*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/contact-agent/:path*",
        "destination": "/en/consumer/contact-agent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/contact-consumer/:path*",
        "destination": "/en/consumer/contact-consumer/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/contact-seller/:path*",
        "destination": "/en/consumer/contact-seller/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage",
        "destination": "/en/finance/mortgage"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/my-home",
        "destination": "/en/finance/home-owner"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/my-home/dashboard",
        "destination": "/en/finance/home-owner/dashboard"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/my-home/dashboard/:tab*",
        "destination": "/en/finance/home-owner/dashboard/:tab*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage/onboarding/landing",
        "destination": "/en/finance/prequal/landing"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/watchlist",
        "destination": "/en/consumer/watchlist"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/open-app",
        "destination": "/en/consumer/open-app"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/vote-for-your-best-region",
        "destination": "/en/consumer/region-vote"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/embed/pgsg-vote-for-your-best-region/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/condo-hp/:path*",
        "destination": "/en/consumer/condo-directory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/condo-directory/:path*",
        "destination": "/en/consumer/condo-directory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/ai-search/:path*",
        "destination": "/en/consumer/ai-search/:path*"
      },
      {
        "has": [
          {
            "type": "host",
            "value": "local.propertyguru.com.sg"
          },
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          },
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/bff/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/pdp-temp/:path*",
        "destination": "/en/consumer/pdp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-property-listing/hdb-block-temp/:estate/:street(.*_\\d+)/:hdbBlock(\\d+[A-Z]?)",
        "destination": "/en/consumer/pdp/:estate/:street/:hdbBlock"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-for-:listingType/p/:freetext/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-search-proxy/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=sale&page=:page&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-for-:listingType/:path*/markdown",
        "destination": "/api/consumer/markdown/srp/:path*/markdown?listingType=:listingType&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeSlug(bungalow-house|hdb-apartment|semi-detached-house|all-residential|apartment-condo|landed-house|hdb|condo|apartment|walk-up-apartment|cluster-house|executive-condo|hdb-1-room-flat|hdb-2-room-flat|hdb-3-room-flat|hdb-4-room-flat|hdb-5-room-flat|jumbo-hdb|hdb-executive-apartment|hdb-executive-maisonette|multi-generation-hdb|hdb-terrace|terraced-house|detached-house|semi-d|corner-terrace|bungalow|good-class-bungalow|shophouse|residential-land|townhouse|conservation-house|cluster-house-land)-for-:listingType/:path*/markdown",
        "destination": "/api/consumer/markdown/srp/:path*/markdown?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeSlug(bungalow-house|hdb-apartment|semi-detached-house|all-residential|apartment-condo|landed-house|hdb|condo|apartment|walk-up-apartment|cluster-house|executive-condo|hdb-1-room-flat|hdb-2-room-flat|hdb-3-room-flat|hdb-4-room-flat|hdb-5-room-flat|jumbo-hdb|hdb-executive-apartment|hdb-executive-maisonette|multi-generation-hdb|hdb-terrace|terraced-house|detached-house|semi-d|corner-terrace|bungalow|good-class-bungalow|shophouse|residential-land|townhouse|conservation-house|cluster-house-land)-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-property-listing/property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&legacy=true&shouldRedirect=true&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/simple-listing/property-for-:listingType/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&page=:page&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeSlug(bungalow-house|hdb-apartment|semi-detached-house|all-residential|apartment-condo|landed-house|hdb|condo|apartment|walk-up-apartment|cluster-house|executive-condo|hdb-1-room-flat|hdb-2-room-flat|hdb-3-room-flat|hdb-4-room-flat|hdb-5-room-flat|jumbo-hdb|hdb-executive-apartment|hdb-executive-maisonette|multi-generation-hdb|hdb-terrace|terraced-house|detached-house|semi-d|corner-terrace|bungalow|good-class-bungalow|shophouse|residential-land|townhouse|conservation-house|cluster-house-land)/:locationSlug/property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug&locationSlug=:locationSlug&shouldRedirect=true&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeSlug(bungalow-house|hdb-apartment|semi-detached-house|all-residential|apartment-condo|landed-house|hdb|condo|apartment|walk-up-apartment|cluster-house|executive-condo|hdb-1-room-flat|hdb-2-room-flat|hdb-3-room-flat|hdb-4-room-flat|hdb-5-room-flat|jumbo-hdb|hdb-executive-apartment|hdb-executive-maisonette|multi-generation-hdb|hdb-terrace|terraced-house|detached-house|semi-d|corner-terrace|bungalow|good-class-bungalow|shophouse|residential-land|townhouse|conservation-house|cluster-house-land)/property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug&shouldRedirect=true&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/shophouse/:locationSlug/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=sale&propertyTypeSlug=shophouse&locationSlug=:locationSlug&shouldRedirect=true&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/similar-listing/:page(\\d+)?",
        "destination": "/en/consumer/srp?page=:page&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/user/security-preferences",
        "destination": "/en/guruland-proxy/user/security-preferences"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/subscriptions",
        "destination": "/en/guruland-proxy/subscriptions"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/user/profile",
        "destination": "/en/guruland-proxy/user/profile"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/myquestions",
        "destination": "/en/guruland-proxy/myquestions"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/project/:path*",
        "destination": "/en/guruland-proxy/project/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/myactivities/:path*",
        "destination": "/en/guruland-proxy/myactivities/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-investment-questions/:path*",
        "destination": "/en/guruland-proxy/property-investment-questions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/condo-directory/:path*",
        "destination": "/en/guruland-proxy/condo-directory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-management-news/:path*",
        "destination": "/en/guruland-proxy/property-management-news/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-condo-reviews/:path*",
        "destination": "/en/guruland-proxy/singapore-condo-reviews/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/guru-picks",
        "destination": "/en/guruland-proxy/guru-picks"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/customer-service/:path*",
        "destination": "/en/guruland-proxy/customer-service/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/shared-shortlist/:path*",
        "destination": "/en/guruland-proxy/shared-shortlist/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/sitemap/:path*",
        "destination": "/en/guruland-proxy/sitemap/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/areainsider/:path*",
        "destination": "/en/guruland-proxy/areainsider/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/market-news/:path*",
        "destination": "/en/guruland-proxy/market-news/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-resources/:path*",
        "destination": "/en/guruland-proxy/property-resources/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore",
        "destination": "/en/guruland-proxy/singapore"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/feedback",
        "destination": "/en/guruland-proxy/feedback"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/mobile",
        "destination": "/en/guruland-proxy/mobile"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/admiralty-woodlands",
        "destination": "/en/guruland-proxy/admiralty-woodlands"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/alexandra-commonwealth",
        "destination": "/en/guruland-proxy/alexandra-commonwealth"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/ang-mo-kio-bishan-thomson",
        "destination": "/en/guruland-proxy/ang-mo-kio-bishan-thomson"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/balestier-toa-payoh",
        "destination": "/en/guruland-proxy/balestier-toa-payoh"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/beach-road-bugis-rochor",
        "destination": "/en/guruland-proxy/beach-road-bugis-rochor"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/bedok-upper-east-coast",
        "destination": "/en/guruland-proxy/bedok-upper-east-coast"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/boat-quay-raffles-place-marina",
        "destination": "/en/guruland-proxy/boat-quay-raffles-place-marina"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/boon-lay-jurong-tuas",
        "destination": "/en/guruland-proxy/boon-lay-jurong-tuas"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/bukit-batok-bukit-panjang",
        "destination": "/en/guruland-proxy/bukit-batok-bukit-panjang"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/buona-vista-west-coast-clementi-new-town",
        "destination": "/en/guruland-proxy/buona-vista-west-coast-clementi-new-town"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/changi-airport-changi-village",
        "destination": "/en/guruland-proxy/changi-airport-changi-village"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/chinatown-tanjong-pagar",
        "destination": "/en/guruland-proxy/chinatown-tanjong-pagar"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/choa-chu-kang-tengah",
        "destination": "/en/guruland-proxy/choa-chu-kang-tengah"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/city-hall-clarke-quay",
        "destination": "/en/guruland-proxy/city-hall-clarke-quay"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/clementi-park-upper-bukit-timah",
        "destination": "/en/guruland-proxy/clementi-park-upper-bukit-timah"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/east-coast-marine-parade",
        "destination": "/en/guruland-proxy/east-coast-marine-parade"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/eunos-geylang-paya-lebar",
        "destination": "/en/guruland-proxy/eunos-geylang-paya-lebar"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/farrer-park-serangoon-rd",
        "destination": "/en/guruland-proxy/farrer-park-serangoon-rd"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/harbourfront-telok-blangah",
        "destination": "/en/guruland-proxy/harbourfront-telok-blangah"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/hougang-punggol-sengkang",
        "destination": "/en/guruland-proxy/hougang-punggol-sengkang"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/macpherson-potong-pasir",
        "destination": "/en/guruland-proxy/macpherson-potong-pasir"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/mandai-upper-thomson",
        "destination": "/en/guruland-proxy/mandai-upper-thomson"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/newton-novena",
        "destination": "/en/guruland-proxy/newton-novena"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/orchard-river-valley",
        "destination": "/en/guruland-proxy/orchard-river-valley"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/pasir-ris-tampines",
        "destination": "/en/guruland-proxy/pasir-ris-tampines"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/tanglin-holland",
        "destination": "/en/guruland-proxy/tanglin-holland"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/seletar-yio-chu-kang",
        "destination": "/en/guruland-proxy/seletar-yio-chu-kang"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/sembawang-yishun",
        "destination": "/en/guruland-proxy/sembawang-yishun"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/map-search",
        "destination": "/en/guruland-proxy/map-search"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/user/login",
        "destination": "/en/guruland-proxy/user/login"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/login",
        "destination": "/en/guruland-proxy/login"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-agent-singapore",
        "destination": "/en/guruland-proxy/property-agent-singapore"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage/:path*",
        "destination": "/en/guruland-proxy/mortgage/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*propertyguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-property-resources/:path*",
        "destination": "/en/guruland-proxy/singapore-property-resources/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/",
        "destination": "/en/consumer/home"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/find-commercial-agents/specialist/:path*",
        "destination": "/en/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/find-commercial-agents/find-agent",
        "destination": "/en/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-agents/:path*",
        "destination": "/en/consumer/agent-directory/find-agent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/agent/:path*",
        "destination": "/en/consumer/agent-profile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/developer/:path*",
        "destination": "/en/developer/profile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/listing/:path*",
        "destination": "/en/consumer/ldp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/user/consent",
        "destination": "/en/consumer/user-consent"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/watchlist",
        "destination": "/en/consumer/watchlist"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/contact-agent/:path*",
        "destination": "/en/consumer/contact-agent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/contact-consumer/:path*",
        "destination": "/en/consumer/contact-consumer/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/open-app",
        "destination": "/en/consumer/open-app"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeGroup(office|retail|industrial)-hp/:path*",
        "destination": "/en/consumer/condo-directory/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeGroup(office|retail|industrial)/:path*",
        "destination": "/en/consumer/condo-directory/:path*"
      },
      {
        "has": [
          {
            "type": "host",
            "value": "local.commercialguru.com.sg"
          },
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          },
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/bff/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/pdp-temp/:path*",
        "destination": "/en/consumer/pdp/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/find-commercial-properties/property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeSlug(retail|industrial|land)/for-:listingType/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug&page=:page&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeSlug(office)/for-:listingType/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&propertyTypeSlug=all-office&page=:page&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-for-:listingType/p/:freetext/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeSlug-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/simple-listing/property-for-:listingType/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&isTableView=true&page=:page&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/similar-listing/:page(\\d+)?",
        "destination": "/en/consumer/srp?page=:page&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/alerts-landing/:path*",
        "destination": "/en/guruland-proxy/alerts-landing/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/captcha.php/:path*",
        "destination": "/en/guruland-proxy/captcha.php/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/contact-confirmation/:path*",
        "destination": "/en/guruland-proxy/contact-confirmation/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/contactus/:path*",
        "destination": "/en/guruland-proxy/contactus/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/controller.php/:path*",
        "destination": "/en/guruland-proxy/controller.php/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/customer-service/:path*",
        "destination": "/en/guruland-proxy/customer-service/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/en/:path*",
        "destination": "/en/guruland-proxy/en/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/events/:path*",
        "destination": "/en/guruland-proxy/events/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/ex_xmlhttp_propertysearch/:path*",
        "destination": "/en/guruland-proxy/ex_xmlhttp_propertysearch/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/feedback/:path*",
        "destination": "/en/guruland-proxy/feedback/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/find-commercial-agents/:path*",
        "destination": "/en/guruland-proxy/find-commercial-agents/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/home/:path*",
        "destination": "/en/guruland-proxy/home/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/listing-map/:path*",
        "destination": "/en/guruland-proxy/listing-map/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/market-news/:path*",
        "destination": "/en/guruland-proxy/market-news/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/market-research/:path*",
        "destination": "/en/guruland-proxy/market-research/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/market-watch/:path*",
        "destination": "/en/guruland-proxy/market-watch/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/mortgage/:path*",
        "destination": "/en/guruland-proxy/mortgage/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/myactivities/:path*",
        "destination": "/en/guruland-proxy/myactivities/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/myquestions/:path*",
        "destination": "/en/guruland-proxy/myquestions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/new-property-listing/:path*",
        "destination": "/en/guruland-proxy/new-property-listing/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/preview-listing/:path*",
        "destination": "/en/guruland-proxy/preview-listing/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/project-questions/:path*",
        "destination": "/en/guruland-proxy/project-questions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/project/:path*",
        "destination": "/en/guruland-proxy/project/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-investment-questions/:path*",
        "destination": "/en/guruland-proxy/property-investment-questions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-management-news/:path*",
        "destination": "/en/guruland-proxy/property-management-news/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/property-map-search/:path*",
        "destination": "/en/guruland-proxy/property-map-search/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/question/:path*",
        "destination": "/en/guruland-proxy/question/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/register-confirmation/:path*",
        "destination": "/en/guruland-proxy/register-confirmation/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-property-listing/:path*",
        "destination": "/en/guruland-proxy/singapore-property-listing/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-real-estate-event/:path*",
        "destination": "/en/guruland-proxy/singapore-real-estate-event/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/singapore-real-estate-past-events/:path*",
        "destination": "/en/guruland-proxy/singapore-real-estate-past-events/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/sitemap/:path*",
        "destination": "/en/guruland-proxy/sitemap/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/subscriptions/:path*",
        "destination": "/en/guruland-proxy/subscriptions/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/user/login/:path*",
        "destination": "/en/guruland-proxy/user/login/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/user/profile/:path*",
        "destination": "/en/guruland-proxy/user/profile/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*commercialguru\\.com\\.sg(?::[0-9]+)?$"
          }
        ],
        "source": "/user/security-preferences/:path*",
        "destination": "/en/guruland-proxy/user/security-preferences/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/",
        "destination": "/en/consumer/home"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/privacy-policy",
        "destination": "/en/consumer/static/privacy-policy-malaysia"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/cookie-policy",
        "destination": "/en/consumer/static/cookie-policy-malaysia"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/terms-of-use",
        "destination": "/en/consumer/static/term-of-use-malaysia"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/acceptable-use-policy-developer-other-advertisers",
        "destination": "/en/consumer/static/acceptable-use-policy-malaysia"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/terms-and-conditions",
        "destination": "/en/consumer/static/legal-malaysia"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/acceptable-use-policy-agent-agency",
        "destination": "/en/consumer/static/acceptable-use-policy-agent-agency-malaysia"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property/:slug*/markdown{/}?",
        "destination": "/api/consumer/markdown/ldp/:slug*/markdown"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property/:slug*",
        "destination": "/en/consumer/ldp/:slug*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/pro/v2/add-listing/:id*",
        "destination": "/en/agentnet/listing-creation/:id*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/contact-consumer/:path*",
        "destination": "/en/consumer/contact-consumer/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/contact-agent/:path*",
        "destination": "/en/consumer/contact-agent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/new-property/developer/:_/:id",
        "destination": "/en/developer/profile/:id"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/new-property/property/:slug*",
        "destination": "/en/developer/pldp/:slug*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm",
        "destination": "/ms/consumer/home"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/dasar-privasi",
        "destination": "/ms/consumer/static/privacy-policy-malaysia-bm"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/polisi-kuki-cookie",
        "destination": "/ms/consumer/static/cookie-policy-malaysia-bm"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/terma-penggunaan",
        "destination": "/ms/consumer/static/term-of-use-malaysia-bm"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/dasar-guna-pelanggan-pemaju-pengiklan",
        "destination": "/ms/consumer/static/acceptable-use-policy-malaysia-bm"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/terma-syarat",
        "destination": "/ms/consumer/static/legal-malaysia-bm"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/dasar-guna-pelanggan-agen-agensi",
        "destination": "/ms/consumer/static/acceptable-use-policy-agent-agency-malaysia-bm"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/properti/:slug*/markdown{/}?",
        "destination": "/api/consumer/markdown/ldp/:slug*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/properti/:slug*",
        "destination": "/ms/consumer/ldp/:slug*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/contact-agent/:path*",
        "destination": "/ms/consumer/contact-agent/:path*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/perumahan-baru/pemaju/:_/:id",
        "destination": "/ms/developer/profile/:id"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/perumahan-baru/properti/:slug*",
        "destination": "/ms/developer/pldp/:slug*"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-property/p/:freetext/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=sale&freetext=:freetext&page=:page&isCommercial=true&propertyTypeSlug=commercial-property"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-property/:path*/markdown",
        "destination": "/api/consumer/markdown/srp/:path*?listingType=sale&isCommercial=true&propertyTypeSlug=commercial-property"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-property/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=sale&isCommercial=true&propertyTypeSlug=commercial-property"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-search-proxy/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=sale&page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-for-:listingType/p/:freetext/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-for-:listingType/:path*/markdown",
        "destination": "/api/consumer/markdown/srp/:path*?listingType=:listingType"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/residential-properties-for-:listingType/p/:freetext/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/residential-properties-for-:listingType/:path*/markdown",
        "destination": "/api/consumer/markdown/srp/:path*?listingType=:listingType&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/residential-properties-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-properties-for-:listingType/:path*/markdown",
        "destination": "/api/consumer/markdown/srp/:path*?listingType=:listingType&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-properties-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-property-for-:listingType/p/:freetext/:page(\\d+)?",
        "destination": "/en/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page&isCommercial=true&propertyTypeSlug=commercial-property"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-property-for-:listingType/:path*/markdown",
        "destination": "/api/consumer/markdown/srp/:path*?listingType=:listingType&isCommercial=true&propertyTypeSlug=commercial-property"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/commercial-property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&isCommercial=true&propertyTypeSlug=commercial-property"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:districtSlug/:propertyTypeSlug-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?provinceSlug=:provinceSlug&locationSlug=:districtSlug&propertyTypeSlug=:propertyTypeSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:propertyTypeSlug-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?locationSlug=:provinceSlug&propertyTypeSlug=:propertyTypeSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:districtSlug/for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?provinceSlug=:provinceSlug&locationSlug=:districtSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?locationSlug=:provinceSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeSlug((?!search-property.*)[^/]+)/:locationSlug/property-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug&locationSlug=:locationSlug&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:listingType(sale|rent)/:propertyType(apartment-flat|semi-d-bungalow|terrace-link-townhouse|bungalow-villa|residential-land|commercial-property|all-industrial|all-agricultural|other-commercial-properties|apartment|condominium|flat|serviced-residence|cluster-house|semi-detached-house|1-sty-terrace-link-house|1-5-sty-terrace-link-house|2-sty-terrace-link-house|2-5-sty-terrace-link-house|3-sty-terrace-link-house|3-5-sty-terrace-link-house|4-sty-terrace-link-house|4-5-sty-terrace-link-house|terraced-house|townhouse|bungalow|zero-lot-bungalow|link-bungalow|bungalow-land|villa|office|shop|shop-office|retail-office|retail-space|sofo|shop-office-retail-space-soho|sovo|commercial-bungalow|commercial-semi-d|hotel-resort|commercial-land|factory|industrial-land|warehouse|cluster-factory|semi-d-factory|detached-factory|terrace-factory|agricultural-land)/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:listingType(sale|rent)/:township/:propertySlug(.*)-:propertyId([^/]+)/:propertyType(apartment-flat|semi-d-bungalow|terrace-link-townhouse|bungalow-villa|residential-land|commercial-property|all-industrial|all-agricultural|other-commercial-properties|apartment|condominium|flat|serviced-residence|cluster-house|semi-detached-house|1-sty-terrace-link-house|1-5-sty-terrace-link-house|2-sty-terrace-link-house|2-5-sty-terrace-link-house|3-sty-terrace-link-house|3-5-sty-terrace-link-house|4-sty-terrace-link-house|4-5-sty-terrace-link-house|terraced-house|townhouse|bungalow|zero-lot-bungalow|link-bungalow|bungalow-land|villa|office|shop|shop-office|retail-office|retail-space|sofo|shop-office-retail-space-soho|sovo|commercial-bungalow|commercial-semi-d|hotel-resort|commercial-land|factory|industrial-land|warehouse|cluster-factory|semi-d-factory|detached-factory|terrace-factory|agricultural-land)/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&propertySlug=:propertySlug&propertyTypeSlug=:propertyType&propertyId=:propertyId&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:listingType(sale|rent)/all-residential/transport/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeSlug((?!commercial-properties|residential-properties).*)-for-:listingType/:path*/markdown",
        "destination": "/api/consumer/markdown/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:propertyTypeSlug((?!commercial-properties|residential-properties).*)-for-:listingType/:path*",
        "destination": "/en/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/similar-listing/:page(\\d+)?",
        "destination": "/en/consumer/srp?page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/:listingType(sale|rent)/:path*",
        "destination": "/en/consumer/srp?listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-komersial/p/:freetext/:page(\\d+)?",
        "destination": "/ms/consumer/srp/search?listingType=dijual&freetext=:freetext&page=:page&isCommercial=true&propertyTypeSlug=hartanah-komersial"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-komersial/:path*/markdown",
        "destination": "/api/consumer/markdown/srp/:path*?listingType=dijual&isCommercial=true&propertyTypeSlug=hartanah-komersial"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-komersial/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=dijual&isCommercial=true&propertyTypeSlug=hartanah-komersial"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/property-search-proxy/:page(\\d+)?",
        "destination": "/ms/consumer/srp/search?listingType=dijual&page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-:listingType(dijual|disewa)/p/:freetext/:page(\\d+)?",
        "destination": "/ms/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-:listingType(dijual|disewa|sewa)/:path*/markdown",
        "destination": "/api/consumer/markdown/srp/:path*?listingType=:listingType"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-:listingType(dijual|disewa|sewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=:listingType"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-kediaman-:listingType(dijual|disewa)/p/:freetext/:page(\\d+)?",
        "destination": "/ms/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-kediaman-:listingType(dijual|disewa)/:path*/markdown",
        "destination": "/api/consumer/markdown/srp/:path*?listingType=:listingType&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-kediaman-:listingType(dijual|disewa|sewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=:listingType&isCommercial=false"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/hartanah-komersial-:listingType(dijual|disewa)/p/:freetext/:page(\\d+)?",
        "destination": "/ms/consumer/srp/search?listingType=:listingType&freetext=:freetext&page=:page&isCommercial=true&propertyTypeSlug=hartanah-komersial"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:districtSlug/:propertyTypeSlug-:listingType(dijual|disewa|sewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?provinceSlug=:provinceSlug&districtSlug=:districtSlug&propertyTypeSlug=:propertyTypeSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:propertyTypeSlug-:listingType(dijual|disewa|sewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?provinceSlug=:provinceSlug&propertyTypeSlug=:propertyTypeSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:districtSlug/:listingType(dijual|disewa|sewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?provinceSlug=:provinceSlug&districtSlug=:districtSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:provinceSlug(johor|kedah|kelantan|kuala-lumpur|labuan|melaka|negeri-sembilan|pahang|penang|perak|perlis|putrajaya|sabah|sarawak|selangor|terengganu)/:listingType(dijual|disewa|sewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?provinceSlug=:provinceSlug&listingType=:listingType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:propertyTypeSlug((?!search-property.*)[^/]+)/:locationSlug/hartanah-:listingType(dijual|disewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug&locationSlug=:locationSlug&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/semua-komersial-dijual/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=dijual&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/semua-komersial-:listingType(disewa|sewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=disewa&isCommercial=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:propertyTypeSlug-:listingType(dijual|disewa)/:path*/markdown",
        "destination": "/api/consumer/markdown/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:propertyTypeSlug-:listingType(dijual|disewa|sewa)/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyTypeSlug"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:listingType(dijual|disewa|sewa)/:propertyType(apartment-rumah-pangsa|rumah-berkembar-banglo|rumah-teres-rumah-berangkai-rumah-bandar|banglo-villa|tanah-kediaman|hartanah-komersial|semua-perindustrian|semua-pertanian|hartanah-komersial-yang-lain|apartment|kondominium|rumah-pangsa|residensi-servis|rumah-kluster|rumah-berkembar|rumah-teres-rumah-berangkai-1-tingkat|rumah-teres-rumah-berangkai-1-5-tingkat|rumah-teres-rumah-berangkai-2-tingkat|rumah-teres-rumah-berangkai-2-5-tingkat|rumah-teres-rumah-berangkai-3-tingkat|rumah-teres-rumah-berangkai-3-5-tingkat|rumah-teres-rumah-berangkai-4-tingkat|rumah-teres-rumah-berangkai-4-5-tingkat|rumah-teres|rumah-bandar|banglo|banglo-lot-kosong|banglo-pautan|tanah-banglo|vila|tanah-kediaman|pejabat|kedai|kedai-pejabat|pejabat-runcit|ruang-niaga|sofo|soho|sovo|banglo-komersial|rumah-berkembar-semi-d-komersial|hotel-resort|tanah-komersial|kilang|tanah-perindustrian|gudang|kilang-kluster|kilang-berkembar|kilang-sesebuah|kilang-teres|tanah-pertanian|hartanah-komersial-yang-lain)/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=:listingType&propertyTypeSlug=:propertyType&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:listingType(dijual|disewa|sewa)/semua-kediaman/transport/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=:listingType"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:listingType(dijual|disewa|sewa)/:township/:propertySlug(.*)-:propertyId([^/]+)/:propertyType(apartment-rumah-pangsa|rumah-berkembar-banglo|rumah-teres-rumah-berangkai-rumah-bandar|banglo-villa|tanah-kediaman|hartanah-komersial|semua-perindustrian|semua-pertanian|hartanah-komersial-yang-lain|apartment|kondominium|rumah-pangsa|residensi-servis|rumah-kluster|rumah-berkembar|rumah-teres-rumah-berangkai-1-tingkat|rumah-teres-rumah-berangkai-1-5-tingkat|rumah-teres-rumah-berangkai-2-tingkat|rumah-teres-rumah-berangkai-2-5-tingkat|rumah-teres-rumah-berangkai-3-tingkat|rumah-teres-rumah-berangkai-3-5-tingkat|rumah-teres-rumah-berangkai-4-tingkat|rumah-teres-rumah-berangkai-4-5-tingkat|rumah-teres|rumah-bandar|banglo|banglo-lot-kosong|banglo-pautan|tanah-banglo|vila|tanah-kediaman|pejabat|kedai|kedai-pejabat|pejabat-runcit|ruang-niaga|sofo|soho|sovo|banglo-komersial|rumah-berkembar-semi-d-komersial|hotel-resort|tanah-komersial|kilang|tanah-perindustrian|gudang|kilang-kluster|kilang-berkembar|kilang-sesebuah|kilang-teres|tanah-pertanian|hartanah-komersial-yang-lain)/:path*",
        "destination": "/ms/consumer/srp/:path*?listingType=:listingType&propertySlug=:propertySlug&propertyTypeSlug=:propertyType&propertyId=:propertyId&shouldRedirect=true"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/similar-listing/:page(\\d+)?",
        "destination": "/ms/consumer/srp?page=:page"
      },
      {
        "has": [
          {
            "type": "header",
            "key": "x-forwarded-host",
            "value": "^(?:[^.]*\\.)*iproperty\\.com\\.my(?::[0-9]+)?$"
          }
        ],
        "source": "/bm/:listingType(dijual|disewa|sewa)/:path*",
        "destination": "/ms/consumer/srp?listingType=:listingType&shouldRedirect=true"
      }
    ],
    "beforeFiles": [
      {
        "source": "/marketplace-web/_next/:path+",
        "destination": "/_next/:path+"
      }
    ],
    "fallback": []
  },
  "sortedPages": [
    "/_app",
    "/_error",
    "/api/consumer/agent-directory/details",
    "/api/consumer/agent-directory/recommended-agents",
    "/api/consumer/agent-directory/search",
    "/api/consumer/agent-directory/suggestions",
    "/api/consumer/agent-feedback/ratings",
    "/api/consumer/agent-feedback/reviews",
    "/api/consumer/agent-insights/similar-listings",
    "/api/consumer/agent-profile/agent-info",
    "/api/consumer/agent-profile/listing-by-id",
    "/api/consumer/agents/review/create",
    "/api/consumer/agents/review/enquired",
    "/api/consumer/agents/review/submitted",
    "/api/consumer/ai-search/__tests__/listings.test",
    "/api/consumer/ai-search/listings",
    "/api/consumer/ask-guru/questions",
    "/api/consumer/ask-guru/questions/me",
    "/api/consumer/autocomplete",
    "/api/consumer/condo-directory/search",
    "/api/consumer/enquiry",
    "/api/consumer/enquiry/notifications",
    "/api/consumer/enquiry/token",
    "/api/consumer/enquiry/whatsapp-url",
    "/api/consumer/fetch-recommendations",
    "/api/consumer/home-sellers/lead/create-cookie",
    "/api/consumer/home-sellers/lead/verify",
    "/api/consumer/home-sellers/missing-property",
    "/api/consumer/home-sellers/user/update",
    "/api/consumer/ipp/area-specialists",
    "/api/consumer/ipp/top-nav",
    "/api/consumer/ipp/user-details",
    "/api/consumer/listings/agent-details",
    "/api/consumer/listings/agents-details",
    "/api/consumer/listings/hide",
    "/api/consumer/listings/other",
    "/api/consumer/listings/report",
    "/api/consumer/listings/report-by-code",
    "/api/consumer/listings/restore",
    "/api/consumer/listings/shortlist",
    "/api/consumer/listings/unified-shortlists",
    "/api/consumer/location/mrt-distances",
    "/api/consumer/location/nearby-pois",
    "/api/consumer/location/places-autocomplete",
    "/api/consumer/location/routes",
    "/api/consumer/markdown/ldp/[...slug]",
    "/api/consumer/markdown/srp/[[...slug]]",
    "/api/consumer/market-watch/delete",
    "/api/consumer/market-watch/edit",
    "/api/consumer/market-watch/exists",
    "/api/consumer/market-watch/get-metadata",
    "/api/consumer/market-watch/get-watchlists",
    "/api/consumer/market-watch/save",
    "/api/consumer/market-watch/unread-notifications-count",
    "/api/consumer/mortgage/affordability-check",
    "/api/consumer/mortgage/current-best-interest-rate",
    "/api/consumer/mortgage/enquiry",
    "/api/consumer/project",
    "/api/consumer/project-price-insights",
    "/api/consumer/property-transactions/property-suggestions",
    "/api/consumer/property-transactions/transactions",
    "/api/consumer/property-transactions/transactions-aggregation",
    "/api/consumer/property-transactions/unit-specification",
    "/api/consumer/recommendation",
    "/api/consumer/save-search",
    "/api/consumer/save-search/exists",
    "/api/consumer/search/generate-url",
    "/api/consumer/search-with-filter/location-items",
    "/api/consumer/search-with-filter/mrt-items",
    "/api/consumer/transaction-summary/transaction-summary",
    "/api/consumer/unified-save-search",
    "/api/consumer/unified-save-search/exists",
    "/api/consumer/users/consent",
    "/api/consumer/users/fetch-user-profile",
    "/api/consumer/users/lead",
    "/api/consumer/users/listing-view",
    "/api/consumer/users/prequalification",
    "/api/consumer/users/save-user-profile",
    "/api/consumer/users/unified-lead",
    "/api/consumer/users/unified-lead-fdl",
    "/api/consumer/vast-media/fetch",
    "/api/consumer/vast-media/impression",
    "/api/core/auth/login",
    "/api/core/auth/otp",
    "/api/core/auth/otp/mobile",
    "/api/core/auth/otp/verify",
    "/api/core/auth/refresh-access-token",
    "/api/core/auth/session/from-cookie",
    "/api/core/auth/unauthorized",
    "/api/core/users/get-self-info",
    "/api/core/users/logout",
    "/api/core/users/password/reset",
    "/api/core/users/password/set",
    "/api/core/users/query",
    "/api/core/users/verify-and-update-mobile",
    "/api/developer/enquiry",
    "/api/developer/listing-search/map-cluster",
    "/api/developer/listing-search/new-launch",
    "/api/developer/mortgage/affordability-check",
    "/api/developer/new-launches/generate-url",
    "/api/developer/project",
    "/api/developer/project/purge",
    "/api/developer/project/purge/__tests__/purge.test",
    "/api/developer/project/purge/[propertyId]",
    "/api/developer/project-search",
    "/api/developer/upcoming-launches",
    "/api/developer/user/update",
    "/api/finance/banks",
    "/api/finance/consultation",
    "/api/finance/enquiry",
    "/api/finance/packages",
    "/api/finance/property/check-onboarding",
    "/api/finance/property/details",
    "/api/finance/property/home-seller-update",
    "/api/finance/property/mortgage",
    "/api/finance/property/overview/insights",
    "/api/finance/property/overview/prices/insights",
    "/api/finance/property/property-suggestion",
    "/api/finance/property/proposals",
    "/api/finance/property/proxy-price",
    "/api/finance/property/recommendedProposals",
    "/api/finance/property/report-purchase-intent/update",
    "/api/finance/property/search-property",
    "/api/finance/property/similar-listings",
    "/api/finance/property/transactions/insights",
    "/api/finance/property/transactions/records",
    "/api/finance/property/transactions/trends",
    "/api/finance/property/unavailable",
    "/api/finance/property/unit-specification",
    "/api/finance/property/update",
    "/api/finance/seller/lead",
    "/api/finance/user/home-seller-onboard",
    "/api/finance/user/home-seller-update-user-account",
    "/api/finance/user/onboard",
    "/api/finance/user/seller-details",
    "/api/health",
    "/api/internal/datadog/metrics/[...slug]",
    "/api/internal/page-cache/purge",
    "/api/internal/widgets/render/render-globals",
    "/api/ready",
    "/[locale]/consumer/agent-directory/find-agent",
    "/[locale]/consumer/agent-profile/[slug]",
    "/[locale]/consumer/ai-search/[[...slug]]",
    "/[locale]/consumer/condo-directory/[[...slug]]",
    "/[locale]/consumer/contact-agent/[token]",
    "/[locale]/consumer/contact-consumer/[token]",
    "/[locale]/consumer/contact-seller/[token]",
    "/[locale]/consumer/hdb",
    "/[locale]/consumer/hdb/[estate]",
    "/[locale]/consumer/hdb/[estate]/[street]",
    "/[locale]/consumer/home",
    "/[locale]/consumer/home-sellers",
    "/[locale]/consumer/home-sellers/landing",
    "/[locale]/consumer/home-sellers/seller-journey/[slug]",
    "/[locale]/consumer/home-sellers/valuation",
    "/[locale]/consumer/ldp/[[...slug]]",
    "/[locale]/consumer/open-app",
    "/[locale]/consumer/pdp/[[...slug]]",
    "/[locale]/consumer/srp/[[...slug]]",
    "/[locale]/consumer/user-consent",
    "/[locale]/consumer/user-preferences",
    "/[locale]/consumer/user-profile",
    "/[locale]/consumer/watchlist",
    "/[locale]/developer/new-launch",
    "/[locale]/developer/pldp/[[...slug]]",
    "/[locale]/developer/profile/[slug]",
    "/[locale]/error",
    "/[locale]/finance/home-loan",
    "/[locale]/finance/home-owner",
    "/[locale]/finance/home-owner/dashboard",
    "/[locale]/finance/home-owner/dashboard/[slug]",
    "/[locale]/finance/home-sellers/dashboard",
    "/[locale]/finance/home-sellers/dashboard/[slug]",
    "/[locale]/finance/mortgage",
    "/[locale]/finance/prequal/landing"
  ]
};self.__BUILD_MANIFEST_CB && self.__BUILD_MANIFEST_CB()