$(document).ready(function () {

	function delegateAddCssClass(ele, classname) {
		addCssClass(ele, classname);

		$(document).delegate("#loadmore", "click", function () {
			addCssClass(ele, classname);
		});
	}

	function addCssClass(ele, classname) {
		$('a.' + classname).each(function (index, e) { $(this).removeClass(classname); })
		$(ele).each(function (index, e) { $(this).addClass(classname); })
	}
	
	 //ใช้แทน settimeout 
	 var chkReadyState = setInterval(function () {

	   //console.log(document.readyState);
	   if (document.readyState == "complete") {

		 try {
		//code here  
		//variable 
		var cur_url = $(location).attr('pathname').toLowerCase();
		var spl = cur_url.split("/"); //เช็ค subsite โดยเริ่มจาก 0 ตัวอย่าง https://www.kasikornbank.com/th/personal/loan/home-loan/pages/home-equity.aspx ถ้าจะเอา personal ให้ใส่ spl[2]
		var last = cur_url.substring(cur_url.lastIndexOf("/") + 1, cur_url.length);
		var last_low = last.toLowerCase(); //เช็คชื่อเพจนั้นๆ ตัวอย่าง https://www.kasikornbank.com/th/personal/loan/home-loan/pages/home-equity.aspx ค่าที่ได้ = home-equity.aspx
		var page_name = last_low.split("."); // ให้ใช้ page_name[0] ตัวอย่าง https://www.kasikornbank.com/th/personal/loan/home-loan/pages/home-equity.aspx ค่าที่ได้ = home-equity

		var i;
		var socialShare = $("#popup-share > div > div > div > a > i");

		for (i = 0; i < socialShare.length; i++) {
			var social_className = socialShare[i].className;
			switch (social_className) {

				case "ic ic-facebook":
					$("#popup-share > div > div > div > a:nth-child(2)").addClass("share-facebook");
					break;

				case "ic ic-twitter":
					$("#popup-share > div > div > div > a:nth-child(3)").addClass("share-twitter");
					break;

				case "ic ic-google-plus":
					$("#popup-share > div > div > div > a:nth-child(4)").addClass("share-google-plus");
					break;

				case "ic ic-line":
					$("#popup-share > div > div > div > a:nth-child(5)").addClass("share-ic-line");
					break;
			}
		}

		$("#navmain > ul > li.li-tool.pull-right > div.tool.tool-login > div > ul > li > a").addClass("nav_login");

		if (spl[1].toLowerCase() == "kplus") {

			$("#page > header > div > div.logo > a").addClass("kplus_nav_header");
			$("#page > header > div > div.main-menu > ul > li > a").addClass("kplus_nav_header");
			$("#page > main > section.section.sc-box.sc-video > div > div").addClass("kplus_main_vdo");
			$("#section-App > div.px-wrapper.skrollable.skrollable-between > div > div > div > div > div > a").addClass("kplus_main_function");
			$(".section.section.sc-download > div > div > div.caption > div > a:nth-child(1)").addClass("kplus_main_download_ios");
			$(".section.section.sc-download > div > div > div.caption > div > a:nth-child(2)").addClass("kplus_main_download_android");
			$(".section.section.sc-box.sc-bg-gray > div > div.kplus-thumbnails > div:nth-child(1) > div.caption > a").addClass("kplus_main_shop_more");
			$(".section.section.sc-box.sc-bg-gray > div > div.kplus-thumbnails > div:nth-child(2) > div.caption > a").addClass("kplus_main_sme_more");
			$(".section > div.functions-detail > div.list-menu > ul > li > a").addClass("kplus_function_list");
		}

		if (spl[1].toLowerCase() == "special") {

			if (spl[2].toLowerCase() == "promptpay") {
				$("#open-block-receive").addClass("service_promptpay_receive");
				$("#open-block-transfer").addClass("service_promptpay_transfer");
				$("#section-howto > div.sc-inner.nopd > div > div > div.tile-headline.entrycontent > div > div > div.note-box.note-box-fixed > a").addClass("service_promptpay_fee");
				$("#section-register > section.section.section-items.section-bg-flexible.section-items-ways > div > div > div.row-items.row-4items.a-center.entrycontent > div > div > div > div > h3 > a").addClass("service_promptpay_channel");

			}
		}

		if (spl.length > 2) {
			switch (spl[2].toLowerCase()) {
				case "business":

					if (spl.length > 3) {
						switch (spl[3].toLowerCase()) {
							case "cash-management":

								if (spl[4].toLowerCase() == "collection-solutions") {
									delegateAddCssClass("#divItems > div > a", "business_collection_solution_list");
								}
								if (spl[4].toLowerCase() == "money-transfer") {
									delegateAddCssClass("#divMain > section > div > div.row > div > a", "business_money_transfer_list");
								}
								if (spl[4].toLowerCase() == "liquidity-solutions") {
									delegateAddCssClass("#divItems > div > a", "business_liquidity_solutions_list");
								}
								if (spl[4].toLowerCase() == "e-service-payment") {
									delegateAddCssClass("#divItems > div > a", "business_e-service_payment_list");

								}
								break;

							case "credit-card":
								delegateAddCssClass("#divItems > div > a", "business_credit_card_list");
								break;

							case "derivative-investments":
								delegateAddCssClass("#divItems > div > a", "business_derivative_investments_list");

								break;

							case "derivative-investments":
								delegateAddCssClass("#divItems > div > a", "business_derivative_investments_list");

								break;

							case "insure":

								if (spl[4].toLowerCase() == "life") {

									delegateAddCssClass("#divItems > div > a", "business_life_insurance_list");

								}
								if (spl[4].toLowerCase() == "non-life") {
									delegateAddCssClass("#divMain > section > div > div.row > div > a", "business_non-life_insurance_list");

								}
								break;

							case "international-trade":

								if (spl[4].toLowerCase() == "import") {

									delegateAddCssClass("#divItems > div > a", "business_import_list");

								}
								if (spl[4].toLowerCase() == "export") {
									delegateAddCssClass("#divItems > div > a", "business_export_list");

								}

								if (spl[4].toLowerCase() == "global-money-transfer") {

									delegateAddCssClass("#divItems > div > a", "business_global_money_transfer_list");

								}

								if (spl[4].toLowerCase() == "credit-guarantee") {
									delegateAddCssClass("#divItems > div > a", "business_inter_credit_guarantee_list");

								}

								if (spl[4].toLowerCase() == "loan") {
									delegateAddCssClass("#divItems > div > a", "business_loan_list");

								}
								break;

							case "investments":
								delegateAddCssClass("#divItems > div > a", "business_investments_list");
								break;

							case "loan":

								if (spl[4].toLowerCase() == "working-capital") {
									delegateAddCssClass("#divItems > div > a", "business_working_capital_loan_list");

								}
								if (spl[4].toLowerCase() == "term-loan") {
									delegateAddCssClass("#divItems > div > a", "business_term_loan_list");

								}
								if (spl[4].toLowerCase() == "supplychain-financing") {
									delegateAddCssClass("#divItems > div > a", "business_supplychain_financing_loan_list");

								}
								if (spl[4].toLowerCase() == "special") {
									delegateAddCssClass("#divItems > div > a", "business_special_loan_list");

								}
								if (spl[4].toLowerCase() == "credit-guarantee") {
									delegateAddCssClass("#divItems > div > a", "business_credit_guarantee_list");

								}
								break;

							case "saving":

								delegateAddCssClass("#divItems > div > a", "business_savings_list");

								break;

							case "sme":

								if (spl[4].toLowerCase() == "financial-services") {

									if (spl[5].toLowerCase() == "collection-solutions") {
										delegateAddCssClass("#divItems > div > a", "sme_payment_service_list");
									}

									if (spl[5].toLowerCase() == "money-transfer") {
										delegateAddCssClass("#divMain > section > div > div.row > div > a", "sme_money_transfer_list");
									}

									if (spl[5].toLowerCase() == "account") {
										delegateAddCssClass("#divItems > div > a", "sme_account_list");
									}
									if (spl[5].toLowerCase() == "credit-card") {
										delegateAddCssClass("#divItems > div > a", "sme_business_credit_card_list");
									}
								}

								if (spl[4].toLowerCase() == "insure") {

									if (spl[5].toLowerCase() == "life") {
										delegateAddCssClass("#divItems > div > a", "sme_life_insurance_list");
									}
									if (spl[5].toLowerCase() == "non-life") {
										delegateAddCssClass("#divMain > section > div > div.row > div > a", "sme_non-life_insurance_list");
									}
								}

								if (spl[4].toLowerCase() == "international-trade") {

									if (spl[5].toLowerCase() == "import") {
										delegateAddCssClass("#divItems > div > a", "sme_import_list");

									}
									if (spl[5].toLowerCase() == "export") {
										delegateAddCssClass("#divItems > div > a", "sme_export_list");

									}
									if (spl[5].toLowerCase() == "global-money-transfer") {
										delegateAddCssClass("#divItems > div > a", "sme_global_money_transfer_list");

									}
								}

								if (spl[4].toLowerCase() == "ksmeknowledge") {

									if (spl[5].toLowerCase() == "article") {

										if (spl[6].toLowerCase() == "ksmeanalysis") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_business_article_list");
										}

										if (spl[6].toLowerCase() == "smestory") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_success_story_list");
										}

										if (spl[6].toLowerCase() == "financialtips") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_financial_tips_list");
										}

										if (spl[6].toLowerCase() == "marketingtips") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_marketing_tips_list");
										}
										if (spl[6].toLowerCase() == "hrmtips") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_hr_tips_list");
										}

										if (spl[6].toLowerCase() == "smetips") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_other_tips_list");
										}

									}
									if (spl[5].toLowerCase() == "clipvdo") {

										if (spl[7].toLowerCase() == "businessstrategy_knowandrich.aspx") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_vdo_knowandrich_list");

										}
										if (spl[7].toLowerCase() == "nanekbukpeep.aspx") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_vdo_nanakebukpeep_list");

										}
										if (spl[7].toLowerCase() == "the_unicon_startup.aspx") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_vdo_theunicorn_list");

										}
										if (spl[7].toLowerCase() == "sme-webinar.aspx") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_vdo_smewebinar_list");

										}
										if (spl[7].toLowerCase() == "sme-survivor.aspx") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_vdo_smesurvivor_list");

										}
										if (spl[7].toLowerCase() == "business-helper.aspx") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_vdo_businesshelper_list");

										}
										if (spl[7].toLowerCase() == "sme-teetak.aspx") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_vdo_smeteetak_list");

										}
										if (spl[7].toLowerCase() == "business-strategy.aspx") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_vdo_business-strategy_list");
										}
										if (spl[7].toLowerCase() == "advertising.aspx") {
											delegateAddCssClass("#ListItem > div > a", "sme_knowledge_vdo_advertising_list");

										}
									}

									if (spl[5].toLowerCase() == "k-sme-inspired") {
										delegateAddCssClass("#ListItem > div > a", "sme_inspired_list");

									}
								}

								if (spl[4].toLowerCase() == "loan") {

									if (spl[5].toLowerCase() == "credit-guarantee") {
										delegateAddCssClass("#divItems > div > a", "bank_guarantee_list");
									}

									if (spl.length > 7 && spl[7].toLowerCase() == "franchise-credit.aspx") {
										delegateAddCssClass("#section-participating-franchise > div > div > div.row-items.row-3items.a-center.entrycontent > div > div > div.list-item-col.list-item-colimg > div > a", "sme_business_solutions_loan");
									}
								}

								break;
						}
					}
					break;
				case "international-business":

					if (spl[3].toLowerCase() == "loan") {
						delegateAddCssClass("#divItems > div > a", "inter-business_loan_list");

					}
					if (spl[3].toLowerCase() == "global-money-transfer") {
						delegateAddCssClass("#divItems > div > a", "inter-business_global_money_transfer_list");
					}
					break;

				case "ir":

					if (spl[3].toLowerCase() == "corporategovernance") {
						$("#LeftMenu > li > a").addClass("ir_corporate_governance_side_list");

					}
					if (spl[3].toLowerCase() == "generalinformation") {
						$("#LeftMenu > li > a").addClass("ir_general_information_side_list");

					}
					if (spl[3].toLowerCase() == "finaninforeports") {
						$("#LeftMenu > li > a").addClass("ir_financial_reports_side_list");

					}
					if (spl[3].toLowerCase() == "presentationjournal") {
						$("#LeftMenu > li > a").addClass("ir_presentation_journal_side_list");

					}
					if (spl[3].toLowerCase() == "shareholderservices") {
						$("#LeftMenu > li > a").addClass("ir_shareholder_services_side_list");

					}

					break;


				case "personal":

					if (spl.length > 3) {
						switch (spl[3].toLowerCase()) {
							case "debit-card":
								$("#section-filters > div > div > div > div > div > div > a").addClass("catalog_debit_card");

								break;

							case "digital-banking":

								if (spl[4].toLowerCase() == "kbankcyberrisk") {
									$("#divBanner > div > div > div > div > div.ms-view.ms-fade-basic-view.ms-grab-cursor > div > div > a").addClass("kcyber_risk_hero_banner");
									$("#WebPartWPQ2 > div.section-home > div > div > div > div > div > div > div > div.image > a").addClass("kcyber_risk_list");
									$("#WebPartWPQ2 > div.section-home > div > div > div > div > div > div > div > div.caption > div > h3 > a").addClass("kcyber_risk_list");

									$(".thumbnail-news").on('click', function () {

										var kcyber_risk_list = document.getElementsByClassName("kcyber_risk_list").length > 0 ? $(this)[0].lastElementChild.getElementsByClassName("kcyber_risk_list")[0].innerText : null;

										if (kcyber_risk_list) {
											dataLayer.push({
												"event": "track_event",
												"event_category": "kcyber_risk",
												"event_action": "click",
												"event_label": kcyber_risk_list
											});
										}
									});
								}

								if (spl[4].toLowerCase() == "sms") {
									$("#divItems > div > a").addClass("digital_banking_sms_list");
								}

								if (spl[4].toLowerCase() == "statement") {
									$("#divItems > div > a").addClass("digital_banking_kemail_list");
								}

								if (spl[4].toLowerCase() == "kplus") {

									$("#page > header > div > div.logo > a").addClass("kplus_nav_header");
									$("#page > header > div > div.main-menu > ul > li > a").addClass("kplus_nav_header");
									$("#page > main > section.section.sc-box.sc-video > div > div > button").addClass("kplus_main_vdo");
									$("#page > main > section > div.functions-detail > div.list-menu > ul > li > a").addClass("kplus_function_list");

									if (spl[6].toLowerCase() == "personalization") {
										$(".section > div.functions-detail > div.details > div.content > div.tab-menu.hidden-w767 > ul > li > a").addClass("kplus_function_sub_menu");
										$(".section > div.functions-detail > div.details > div.functions-action > div > div > div.download > a.app-store").addClass("kplus_function_download_ios");
										$(".section > div.functions-detail > div.details > div.functions-action > div > div > div.download > a.google-play").addClass("kplus_function_download_android");
										$(".section > div.functions-detail > div.details > div.functions-action > div > div > div.faq > a").addClass("kplus_function_faq");
									}

									if (spl[5].toLowerCase() == "applying") {
										$(".section > div.functions-detail.applying > div > div.content > div.tab-menu.hidden-w767 > ul > li > a").addClass("kplus_register_channel");
										$(".section > div.functions-detail.applying > div > div.functions-action > div > div > div.download > a.google-play").addClass("kplus_register_download_android");
										$(".section > div.functions-detail.applying > div > div.functions-action > div > div > div.download > a.app-store").addClass("kplus_register_download_ios");
										$(".section > div.functions-detail.applying > div > div.functions-action > div > div > div.faq > a").addClass("kplus_register_faq");

									}
									if (spl[5].toLowerCase() == "promotions") {
										$('.section.section.hl-promotions > div > div > div > a.item.slick-slide').addClass("kplus_promotion_hero_banner");
										$('.section.section.sc-box.sc-promotions > div > div.row > div > div > div.image > a').addClass("kplus_promotion_list");
										$('.section.section.sc-box.sc-promotions > div > div.row > div > div > div.caption > div > h3 > a').addClass("kplus_promotion_list");

										$(".thumbnail-promotions").on('click', function () {

											var kplus_promotion = document.getElementsByClassName("kplus_promotion_list").length > 0 ? $(this)[0].lastElementChild.getElementsByClassName("kplus_promotion_list")[0].innerText : null;

											if (kplus_promotion) {
												dataLayer.push({
													"event": "track_event",
													"event_category": "kplus_promotion",
													"event_action": "click",
													"event_label": kplus_promotion
												});
											}
										});
									}
									if (spl[5].toLowerCase() == "help") {
										$(".section.section.hl-faq > div > div.menu.hidden-w1199 > ul > li > a").addClass("kplus_faq_topic");
										$(".section.section.sc-box > div > div > div > div.accordion-title").addClass("kplus_faq_question");
									}

								}
								break;


							case "insure":

								if (spl[4].toLowerCase() == "life") {
									$("#divMain > section > div > div.row > div > a").addClass("life_insurance_list");

								}

								if (spl[4].toLowerCase() == "non-life") {
									$("#divItems > div > a").addClass("non-life_insurance_list");

								}
								break;

							case "services":

								if (spl[4].toLowerCase() == "payment") {

									$("#divMain > section > div > div.row > div > a").addClass("service_payment_list");
								}

								if (spl[4].toLowerCase() == "cheque") {
									$("#divItems > div > a").addClass("service_cheque_list");

								}

								if (spl[4].toLowerCase() == "foreign-currency") {
									$("#divItems > div > a").addClass("service_foreign_currency_list");

								}

								break;
							case "loan":

								if (spl[4].toLowerCase() == "personal-loan-special") {
									$("#stktitle > a").addClass("personal_special_loan_nav_header");
									$("#maincontentBox > section.section > div.sc-inner > div > div > div > div > a.btn.btn-green").addClass("personal_special_loan_register");
									$("#maincontentBox > section.section > div.sc-inner > div > div > div > div > a.more").addClass("personal_special_loan_read_more");
									$("#maincontentBox > section.section.section-compare.compare1 > div > div > div > div.sc-headline.sc-headline-compare > a").addClass("compare_loan_k-express_cash_and_k-personal_loan");
									$("#maincontentBox > section.section.section-compare.padding-bottom-0 > div > div > div > div.sc-headline.sc-headline-compare > a").addClass("compare_loan_k-home_for_cash_and_k-car_for_cash");
									$("#maincontentBox > section.section.section-compare.compare1 > div > div > div > div.hide-content-compare > div > div > div > table > tfoot > tr > td:nth-child(2) > div > a.btn.btn-green").addClass("personal_special_loan_compare_express_cash_register");
									$("#maincontentBox > section.section.section-compare.compare1 > div > div > div > div.hide-content-compare > div > div > div > table > tfoot > tr > td:nth-child(3) > div > a.btn.btn-green").addClass("personal_special_loan_compare_personal_loan_register");
									$("#maincontentBox > section.section.section-compare.padding-bottom-0 > div > div > div > div.hide-content-compare > div > div > div > table > tfoot > tr > td:nth-child(2) > div > a.btn.btn-green").addClass("personal_special_loan_compare_home_for_cash_register");
									$("#maincontentBox > section.section.section-compare.padding-bottom-0 > div > div > div > div.hide-content-compare > div > div > div > table > tfoot > tr > td:nth-child(3) > div > a.btn.btn-green").addClass("personal_special_loan_compare_car_for_cash_register");
									$("#maincontentBox > section.section.section-compare.compare1 > div > div > div > div.hide-content-compare > div > div > div > table > tfoot > tr > td:nth-child(2) > div > a.more").addClass("personal_special_loan_compare_express_cash_read_more");
									$("#maincontentBox > section.section.section-compare.compare1 > div > div > div > div.hide-content-compare > div > div > div > table > tfoot > tr > td:nth-child(3) > div > a.more").addClass("personal_special_loan_compare_personal_loan_read_more");
									$("#maincontentBox > section.section.section-compare.padding-bottom-0 > div > div > div > div.hide-content-compare > div > div > div > table > tfoot > tr > td:nth-child(2) > div > a.more").addClass("personal_special_loan_compare_home_for_cash_read_more");
									$("#maincontentBox > section.section.section-compare.padding-bottom-0 > div > div > div > div.hide-content-compare > div > div > div > table > tfoot > tr > td:nth-child(3) > div > a.more").addClass("personal_special_loan_compare_car_for_cash_read_more");
								}
								break;
						}
					}

				case "promotion":

					if (spl.length > 3) {

						$("#page > main > section > div > div > div.thumbnails-slider > div > div.owl-wrapper-outer > div > div > div > div > div > a").addClass("catalog_promotion");
						$("#page > main > section > div > div > div.thumbnails-slider > div > div.owl-wrapper-outer > div > div > div > div > div.caption > div > h3 > a").addClass("catalog_promotion");
						$("#page > main > section > div > div > div.sc-action > a").addClass("catalog_promotion_all");

					} else {
						$("#maincontentBox > main > div.carousel-slider > div > div > div > div.ms-view.ms-fade-basic-view.ms-grab-cursor > div > div > a").addClass("promotion_hero_banner");
						$("#drow_render > div > div > div.image > a").addClass("catalog_promotion");
						$("#drow_render > div > div > div.caption > div > h3 > a").addClass("catalog_promotion");
					}

					$(".thumbnail-news").on('click', function () {

						var catalog_promotion = document.getElementsByClassName("catalog_promotion").length > 0 ? $(this)[0].lastElementChild.getElementsByClassName("catalog_promotion")[0].innerText : null;

						if (catalog_promotion) {
							dataLayer.push({
								"event": "track_event",
								"event_category": "catalog_promotion",
								"event_action": "click",
								"event_label": catalog_promotion
							});
						}
					});

					break;

				case "rate":

					if (spl[4].toLowerCase() == "deposits.aspx") {

						$("#LeftMenu > li > a").addClass("rates_and_fees");
					}
					break;
			}

		}
		 }
		catch(e){
		 console.log(e);
		}

		clearInterval(chkReadyState);
		//page load complete
	   }
	 }, 100);


});