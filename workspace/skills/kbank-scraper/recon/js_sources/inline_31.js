
            var digitalData = {};
            var _spBodyOnLoadFunctions = [];

            function loadLink(attributes, callback) {
                if (callback === undefined) {
                    callback = function () { };
                }

                var linkEl = document.createElement('link');

                if (attributes.rel !== undefined) {
                    linkEl.rel = attributes.rel;
                }

                if (attributes.sizes !== undefined) {
                    linkEl.sizes = attributes.sizes;
                }

                if (attributes.href !== undefined) {
                    linkEl.href = attributes.href;
                }

                linkEl.onload = function (event) {
                    callback(false, event);
                };

                linkEl.onerror = function (event) {
                    callback(true, event); 
                };

                $('head').append(linkEl);

                return linkEl;
            }

            function loadCss(url, callback) {
                return loadLink({
                    rel: 'stylesheet',
                    href: url,
                }, callback);
            }

            function GetCurrentLang() {
                return _spPageContextInfo.currentCultureName.substr(0, 2);
            }
        