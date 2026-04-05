$(function () {
  // 1.1
$(document).on("click.tracking", ".noti-content .announcemain .tab-promotion-btn a", function () {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({
    event: "track_event",
    event_category: "click",
    event_action: "#maincontentBox",
    event_label: "try_ai",
    element_position: "1",
    element_grouping: "product_highlight",
    element_layer: "2",
    element_section: "product_highlight",
    element_title: $(this).text().trim(),
    click_url: $(this).attr("href") || "",
    additional01: "v2",
  });
});

  // 1.2 ปุ่ม ทดลองได้เลย
  $(".sc-ai-decoration .btn-control a.btn").on(
    "click.tracking",
    function () {
      var dl_sc = $(this).closest("[data-dl-section]").attr("data-dl-section");
      window.dataLayer.push({
        event: "track_event",
        event_category: "click",
        event_action: "#sc-ai-decoration",
        event_label: "try_ai",
        element_position: "1",
        element_grouping: "product_highlight",
        element_layer: "1",
        element_section: "product_highlight",
        element_title: $(this).text().trim(),
        click_url: $(this).attr("href"),
        additional01: "v2",
      });
    }
  );

  // 1.3
  $(".ai-decoration .btn-control button").on("click.tracking", function () {
    window.dataLayer.push({
      event: "track_event",
      event_category: "click",
      event_action: "#idea-ai-decoration",
      event_label: "try_ai",
      element_position: "1",
      element_grouping: "product_detail",
      element_layer: "1",
      element_section: "product_highlight",
      element_title: $(this).text().trim(),
      click_url: $(this).attr("href"),
      additional01: "v2",
    });
  });

  // 2 วิธีการใช้งาน ai decoration
  $(".sc-ai-decoration .btn-control a.txt-link").on(
    "click.tracking",
    function () {
      var dl_sc = $(this).closest("[data-dl-section]").attr("data-dl-section");
      window.dataLayer.push({
        event: "track_event",
        event_category: "click",
        event_action: "#sc-ai-decoration",
        event_label: "howto_ai",
        element_position: "1",
        element_grouping: "product_highlight",
        element_layer: "1",
        element_section: "product_highlight",
        element_title: "วิธีการใช้งาน Ai Decoration",
        click_url: $(this).attr("href"),
        additional01: "v2",
      });
    }
  );

  // 2.1
  $(".idea-ai-decoration .ai-decoration .btn-control a.txt-link").on("click.tracking", function () {
    window.dataLayer.push({
      event: "track_event",
      event_category: "click",
      event_action: "#idea-ai-decoration",
      event_label: "howto_ai",
      element_position: "1",
      element_grouping: "product_detail",
      element_layer: "1",
      element_section: "product_highlight",
      element_title: $(this).text().trim(),
      click_url: $(this).attr("href"),
      additional01: "v2",
    });
  });

    // 3 tab
  $(".menu-tab .btn-tabs").on("click.tracking", function () {
  window.dataLayer.push({
    event: "track_event",
    event_category: "tab_content",
    event_action: "#how-to",
    event_label: $(this).data("label") || "",
    element_position: $(this).index() + 1,
    element_grouping: "product_detail",
    element_layer: "1",
    element_section: "product_detail",
    element_title: $(this).text().trim(),
    click_url: $(this).attr("href") || "",
    additional01: "v2",
  });
});

  // function bindEventsByScreen() {
  //   $(".button .btn-tabs.mobile").off("click.trk");
  //   $(".button .btn-tabs.computer").off("click.trk");

  //   if (window.matchMedia("(max-width: 1199px)").matches) {
  //     $(".button .btn-tabs.mobile").on("click.trk", function () {
  //       window.dataLayer.push({
  //         event: "track_event",
  //         event_category: "tab_content",
  //         event_action: "#how-to",
  //         event_label: "mobile",
  //         element_position: $(this).index() + 1,
  //         element_grouping: "product_detail",
  //         element_layer: "1",
  //         element_section: "product_detail",
  //         element_title: $(this).text().trim(),
  //         click_url: $(this).attr("href") || "",
  //         additional01: "v2",
  //       });
  //     });
  //   }

  //   if (window.matchMedia("(min-width: 1200px)").matches) {
  //     $(".button .btn-tabs.computer").on("click.trk", function () {
  //       window.dataLayer.push({
  //         event: "track_event",
  //         event_category: "tab_content",
  //         event_action: "#how-to",
  //         event_label: "desktop",
  //         element_position: $(this).index() + 1,
  //         element_grouping: "product_detail",
  //         element_layer: "1",
  //         element_section: "product_detail",
  //         element_title: $(this).text().trim(),
  //         click_url: $(this).attr("href") || "",
  //         additional01: "v2",
  //       });
  //     });
  //   }
  // }

  bindEventsByScreen();

  let resizeTimer;
  $(window).on("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(bindEventsByScreen, 200);
  });

  // 4 gallery-modal
  $(".gallery-backdrop .idea-ai-decoration-btn-create").on(
    "click.tracking",
    function () {
      window.dataLayer.push({
        event: "track_event",
        event_category: "click",
        event_action: "#gallery-modal",
        event_label: "ai_design_apply",
        element_position: $(this).index() + 1,
        element_grouping: "ai_design",
        element_layer: "1",
        element_section: "product_detail",
        element_title: $(this).text().trim(),
        click_url: $(this).attr("href") || "",
        additional01: "v2",
      });
    }
  );

  // 5 regenerate
  $(".button-generate.js-tracking-generate").on("click.tracking", function () {
    // ดึง property_id จาก href ใน .head a
    const href =
      $(".head a[href*='/th/propertyforsale/detail/']").attr("href") || "";
    const match = href.match(/detail\/(\d+)\.html/i);
    const propertyId = match ? match[1] : "";

    // รวบรวมค่าจากกลุ่มที่ active เฉพาะตอนกด
    const additional02 = (function () {
      const pairs = [];
      $(".ai-deco-tools-inner .tool-card-group .tool-card").each(function () {
        const key = $(this).data("tool-name"); // room, style, floor, ceiling, wall, color
        const $active = $(this).find(".tool-checkbox.active").first();
        if (!$active.length) return; // ข้ามกลุ่มที่ไม่มี active

        // ดึงค่าหลักจาก value ของ input ถ้าไม่มีค่อย fallback เป็นข้อความบน label
        let val =
          $active.find("input").val() ||
          $active.find("label span").first().text().trim().toLowerCase();

        // ตัด prefix (room-/style-/floor-/...) แล้ว normalize ให้เป็น snake_case
        if (val) {
          val = val
            .replace(/^(room|style|floor|ceiling|wall|color)-/i, "") // ตัด prefix แรกออก
            .replace(/-/g, "_") // แปลง - เป็น _
            .replace(/\s+/g, "_"); // เผื่อ fallback จาก label
        }

        // กรณีพิเศษ room: living_room -> living
        if (key === "room") {
          val = val.replace(/_room$/i, "");
        }

        pairs.push(`${key}:${val}`);
      });
      return pairs.join(", ");
    })();

    window.dataLayer.push({
      event: "track_event",
      event_category: "click",
      event_action: "#react-app-ai-decor",
      event_label: "ai_design_generate",
      element_position: $(this).index() + 1,
      element_grouping: "ai_design",
      element_layer: "1",
      element_section: "product_detail",
      element_title: $(this).text().trim(),
      click_url: $(this).attr("href") || "",
      element_id: propertyId,
      additional01: "v2",
      additional02: additional02, // ตัวอย่าง: "room:living, style:scandinavian, floor:whitewashed_wood, ceiling:smooth_plaster, wall:laminate, color:soft_white_and_natural_wood"
    });
  });

  // 6 reset desktop
  $(".tool-bottom .button-reset").on("click.tracking", function () {
    window.dataLayer.push({
      event: "track_event",
      event_category: "click",
      event_action: "#react-app-ai-decor",
      event_label: "ai_design_regenerate",
      element_position: "1",
      element_grouping: "ai_design",
      element_layer: "1",
      element_section: "product_detail",
      element_title: $(this).find("span").text().trim(),
      click_url: $(this).attr("href") || "",
      additional01: "v2",
    });
  });

  // 6 regenerate mobile
  $(".ai-deco-preview-bottom .btn-regenerate").on(
    "click.tracking",
    function () {
      window.dataLayer.push({
        event: "track_event",
        event_category: "click",
        event_action: "#react-app-ai-decor",
        event_label: "ai_design_regenerate",
        element_position: "1",
        element_grouping: "ai_design",
        element_layer: "1",
        element_section: "product_detail",
        element_title: $(this).find(".text").text().trim(),
        click_url: $(this).attr("href") || "",
        additional01: "v2",
      });
    }
  );
});



// data-kb ที่ต้องลบ
(function ($) {
  // รายชื่อ 
  const KB_ATTRS = [
    "kbct","kblb","kbgp","kbsc","kbpo",
    "data-kbct","data-kblb","data-kbgp","data-kbsc","data-kbpo","data-kbid"
  ];

  const TARGET_SELECTOR = ".ai-decoration button#try-ai";

  function stripKB($scope) {
    const $targets = ($scope && $scope.length ? $scope : $(TARGET_SELECTOR))
      .find(TARGET_SELECTOR)
      .addBack(TARGET_SELECTOR);

    $targets.each(function () {
      const $el = $(this);

      const classes = ($el.attr("class") || "").split(/\s+/).filter(Boolean);
      classes.forEach(cls => {
        if (/^pxtm-click-/.test(cls)) {
          $el.removeClass(cls);
        }
      });

      KB_ATTRS.forEach(name => {
        if (this.hasAttribute && this.hasAttribute(name)) {
          $el.removeAttr(name);
        }
      });
    });
  }
  $(function () {
    stripKB($(TARGET_SELECTOR));
  });

  $(window).on("load", function () {
    stripKB($(TARGET_SELECTOR));

    // กันสคริปต์อื่นใส่กลับเฉพาะปุ่มนี้
    try {
      const btn = document.querySelector(TARGET_SELECTOR);
      if (!btn) return;

      const observer = new MutationObserver(mutations => {
        mutations.forEach(m => {
          const t = m.target;
          if (m.type === "attributes") {
            if (m.attributeName === "class") {
              const classes = (t.className || "").split(/\s+/);
              classes.forEach(cls => {
                if (/^pxtm-click-/.test(cls)) t.classList.remove(cls);
              });
            } else if (KB_ATTRS.includes(m.attributeName)) {
              t.removeAttribute(m.attributeName);
            }
          } else if (m.type === "childList") {
            m.addedNodes.forEach(node => {
              if (node.nodeType === 1) {
                stripKB($(node));
              }
            });
          }
        });
      });

      observer.observe(btn, {
        subtree: true,
        childList: true,
        attributes: true,
        attributeFilter: ["class", ...KB_ATTRS],
      });
    } catch (e) {
      console.warn("MutationObserver not supported:", e);
    }
  });

  setTimeout(() => stripKB($(TARGET_SELECTOR)), 1200);
})(jQuery);