const configs = {
  mediaURLPrefix: "https://pfsapp.kasikornbank.com/pfs-frontend-api/property-images",
  defaultThumbnailURL:
    "/SiteCollectionDocuments/assets/PFS2022/image/default_thumbnail.jpg",
  // searchPagePath: "/th/PropertyForSale/Pages/search2022.aspx",
  backendPFSURL: "/Custom/KWEB2020/NPA2023Backend13.aspx",
  backendNPAURL: "/Custom/KWEB2020/GarageBackendNPA108.aspx",
  backendHLURL: '/Custom/KWEB2020/GarageBackendHL28.aspx',
  MaxPropertyReturnCount: 12,
  MaxPromoPropertyReturnCount: 10,
  FavMaxPropertyReturnCount: 50,
  MaxPropertyReturnCountBeforeRandom: 35,
  SearchNearbyMeters: 3000,
  ReCAPTCHASiteKey: "6LdiScgUAAAAAMdIWuDKUvcBGC0W-ncWrGcFiCXe",
  pagesLink: {
    searchTag: "/th/propertyforsale/search-tag/",
    home: "/th/propertyforsale",
    search: "/th/propertyforsale/search/pages/index.aspx",
    promotion: "/th/propertyforsale/promotion",
    tutorial: "/th/propertyforsale/pages/propertyforsale-tutorial.aspx",
    announcement: "/th/propertyforsale/announcement/pages/index.aspx",
    faq: "/th/propertyforsale/faq",
    detail: "/th/propertyforsale/detail/{{PropID}}.html",
    offer: "/th/propertyforsale/property/offering/pages/index.aspx",
    promoProperty:
      "/th/propertyforsale/search/pages/index.aspx?Tab=promoProperty",
    HotProperty:
      "/th/propertyforsale/search/pages/index.aspx?Tab=popularProperty",
    NewProperty: "/th/propertyforsale/search/pages/index.aspx?Tab=newProperty",
    Compare: "/th/propertyforsale/compare/pages/index.aspx",
    printDetail: "/th/propertyforsale/detail/pages/print-detail.aspx?propID={{PropID}}",
    login: "/th/propertyforsale/login/pages/index.aspx",
    aiDecorate: "/th/propertyforsale/pages/ai-decoration.aspx",
    secondHand: "/th/personal/loan/homeLoan/pages/home.aspx#loan-interest-npa",
  },
  priceFilter: [
    {
      title: "ไม่เกิน ",
      price: 1,
      start: true,
    },
    {
      title: "",
      price: 1,
      price2: 3,
    },
    {
      title: "",
      price: 3,
      price2: 5,
    },
    {
      title: "",
      price: 5,
      price2: 10,
    },
    {
      title: "",
      price: 10,
      price2: 20,
    },
    {
      title: "มากกว่า ",
      price: 20,
      end: true,
    },
  ],
  provinceFilter: [
    {
      class: "travel-1",
      provinceName: "กรุงเทพฯ",
      provinceCode: "10",
    },
    {
      class: "travel-2",
      provinceName: "นนทบุรี",
      provinceCode: "12",
    },
    {
      class: "travel-3",
      provinceName: "ปทุมธานี",
      provinceCode: "13",
    },
    {
      class: "travel-4",
      provinceName: "สมุทรปราการ",
      provinceCode: "11",
    },
    {
      class: "travel-5",
      provinceName: "นครปฐม",
      provinceCode: "73",
    },
    {
      class: "travel-6",
      provinceName: "เชียงใหม่",
      provinceCode: "50",
    },
    {
      class: "travel-7",
      provinceName: "ชลบุรี",
      provinceCode: "20",
    },
    {
      class: "travel-8",
      provinceName: "ขอนแก่น",
      provinceCode: "40",
    },
    {
      class: "travel-9",
      provinceName: "นครราชสีมา",
      provinceCode: "30",
    },
    {
      class: "travel-10",
      provinceName: "ภูเก็ต",
      provinceCode: "83",
    },
  ],
  propertyTypeFilter: [
    {
      class: "ic-npa-icon-housetype",
      propertyTypeName: "บ้านเดี่ยว",
      propertyTypeCode: "02",
    },
    {
      class: "ic-npa-icon-land",
      propertyTypeName: "ที่ดิน",
      propertyTypeCode: "01",
    },
    {
      class: "ic-npa-icon-townhouse",
      propertyTypeName: "ทาวน์เฮ้าส์",
      propertyTypeCode: "03",
    },
    {
      class: "ic-npa-icon-condo",
      propertyTypeName: "คอนโดมิเนียม",
      propertyTypeCode: "05",
    },
    {
      class: "ic-npa-icon-commercialbuilding",
      propertyTypeName: "อาคารพาณิชย์",
      propertyTypeCode: "04",
    },
    {
      class: "ic-npa-icon-warehouse",
      propertyTypeName: "โกดัง",
      propertyTypeCode: "12",
    },
    {
      class: "ic-npa-icon-factory",
      propertyTypeName: "โรงงาน",
      propertyTypeCode: "09",
    },
    {
      class: "ic-npa-icon-apartment",
      propertyTypeName: "อพาร์ทเม้นท์",
      propertyTypeCode: "15",
    },
    {
      class: "ic-npa-icon-office",
      propertyTypeName: "อาคารสำนักงาน",
      propertyTypeCode: "10",
    },
    {
      class: "ic-npa-icon-resort",
      propertyTypeName: "รีสอร์ท",
      propertyTypeCode: "20",
    },
    {
      class: "ic-npa-icon-houseother",
      propertyTypeName: "อื่น ๆ",
      propertyTypeCode: 19,
    },
  ],
  placeTypes: [
    {
      Priority: 1,
      TypeCode: ["bts", "mrt", "airport_link"],
      NameTH: "รถไฟฟ้า",
      icon: "skytrain",
    },
    {
      Priority: 2,
      TypeCode: ["department_store", "shopping_mall"],
      NameTH: "ห้างสรรพสินค้า/ร้านค้า",
      icon: "shopping",
    },
    {
      Priority: 3,
      TypeCode: "hospital",
      NameTH: "โรงพยาบาล",
      icon: "hospital",
    },
    {
      Priority: 4,
      TypeCode: "restaurant",
      NameTH: "ร้านอาหาร",
      icon: "restaurant",
    },
    {
      Priority: 5,
      TypeCode: "supermarket",
      NameTH: "ซูปเปอร์มาร์เก็ต",
      icon: "shopping",
    },
    {
      Priority: 6,
      TypeCode: "primary_school",
      NameTH: "โรงเรียน",
      icon: "primaryschool",
    },
    {
      Priority: 6,
      TypeCode: "secondary_school",
      NameTH: "โรงเรียน",
      icon: "secondaryschool",
    },
    {
      Priority: 7,
      TypeCode: "university",
      NameTH: "มหาวิทยาลัย",
      icon: "university",
    },
    {
      Priority: 8,
      TypeCode: "bank",
      NameTH: "ธนาคาร",
      icon: "bank",
    },
    {
      Priority: 10,
      TypeCode: "tourist_attraction",
      NameTH: "สถานที่ท่องเที่ยว",
      icon: "touristattraction",
    },
    {
      Priority: 11,
      TypeCode: "movie_theater",
      NameTH: "โรงภาพยนตร์",
      icon: "movietheater",
    },
    {
      Priority: 12,
      TypeCode: "park",
      NameTH: "สวนสาธารณะ",
      icon: "park",
    },
    {
      Priority: 13,
      TypeCode: "cafe",
      NameTH: "คาเฟ่",
      icon: "cafe",
    },
    {
      Priority: 14,
      TypeCode: "stadium",
      NameTH: "สนามกีฬา",
      icon: "sportstadium",
    },
    {
      Priority: 15,
      TypeCode: "electronic_store",
      NameTH: "ร้านเครื่องใช้ไฟฟ้า",
      icon: "electronicstore",
    },
  ],
  CalculatorHomeLoanSetting: [
    {
      Code: "LimitBotHouse1LessThan10MB",
      Value: "100",
    },
    {
      Code: "LimitBotHouse1GreaterThan10MB",
      Value: "100",
    },
    {
      Code: "LimitBotHouse2InstallLessThan2Years",
      Value: "100",
    },
    {
      Code: "LimitBotHouse2InstallGreaterThan2Years",
      Value: "100",
    },
    {
      Code: "LimitBotHouse3",
      Value: "100",
    },
    {
      Code: "LimitKBank",
      Value: "100",
    },
    {
      Code: "F8SalaryLessThan30000",
      Value: "70",
    },
    {
      Code: "F8Salary30000To70000",
      Value: "80",
    },
    {
      Code: "F8SalaryGreaterThan70000",
      Value: "90",
    },
    {
      Code: "F9SalaryLessThan30000",
      Value: "70",
    },
    {
      Code: "F9Salary30000To70000",
      Value: "80",
    },
    {
      Code: "F9SalaryGreaterThan70000",
      Value: "90",
    },
    {
      Code: "KBankMRR",
      Value: "5.97",
    },
    {
      Code: "CentralMRR",
      Value: "1.25",
    },
    {
      Code: "BaseRateF17GreaterThan1_75",
      Value: "0.50",
    },
    {
      Code: "BaseRateF17From1_5To1_75",
      Value: "0.50",
    },
    {
      Code: "BaseRateF17From1_25To1_5",
      Value: "0.50",
    },
    {
      Code: "BaseRateF17From1To1_25",
      Value: "0.50",
    },
    {
      Code: "BaseRateF17From0_5To1",
      Value: "0.50",
    },
    {
      Code: "BaseRateF17From0_15To0_5",
      Value: "0.50",
    },
    {
      Code: "BaseRateF17LessThan0_15",
      Value: "0.50",
    },
  ],
  CalculatorLandSetting: [
    {
      Code: "LimitBotHouse1LessThan10MB",
      Value: "100",
    },
    {
      Code: "LimitBotHouse1GreaterThan10MB",
      Value: "90",
    },
    {
      Code: "LimitBotHouse2InstallLessThan2Years",
      Value: "80",
    },
    {
      Code: "LimitBotHouse2InstallGreaterThan2Years",
      Value: "90",
    },
    {
      Code: "LimitBotHouse3",
      Value: "70",
    },
    {
      Code: "LimitKBank",
      Value: "85",
    },
    {
      Code: "F8SalaryLessThan30000",
      Value: "70",
    },
    {
      Code: "F8Salary30000To70000",
      Value: "80",
    },
    {
      Code: "F8SalaryGreaterThan70000",
      Value: "90",
    },
    {
      Code: "F9SalaryLessThan30000",
      Value: "70",
    },
    {
      Code: "F9Salary30000To70000",
      Value: "80",
    },
    {
      Code: "F9SalaryGreaterThan70000",
      Value: "90",
    },
    {
      Code: "KBankMRR",
      Value: "5.97",
    },
    {
      Code: "CentralMRR",
      Value: "0.5",
    },
    {
      Code: "BaseRateF17GreaterThan1_75",
      Value: "0.5",
    },
    {
      Code: "BaseRateF17From1_5To1_75",
      Value: "0.5",
    },
    {
      Code: "BaseRateF17From1_25To1_5",
      Value: "0.5",
    },
    {
      Code: "BaseRateF17From1To1_25",
      Value: "0.5",
    },
    {
      Code: "BaseRateF17From0_5To1",
      Value: "0.5",
    },
    {
      Code: "BaseRateF17From0_15To0_5",
      Value: "0.5",
    },
    {
      Code: "BaseRateF17LessThan0_15",
      Value: "0.5",
    },
  ],
  CalculatorSMESetting: [
    {
      Code: "C1_MRR",
      Value: "5.970",
    },
    {
      Code: "C2_LNRateForInstallmentSecured",
      Value: "3.00",
    },
    {
      Code: "C3_MinimumDSCR",
      Value: "1.2",
    },
    {
      Code: "C4_NetProfitDeptRatioConfig",
      Value: "0.2",
    },
    {
      Code: "C6_MaxLoanPeriod",
      Value: "20",
    },
    {
      Code: "C7_MaxAge",
      Value: "70",
    },
    {
      Code: "C8_LTV",
      Value: "100.00",
    },
  ],
};
