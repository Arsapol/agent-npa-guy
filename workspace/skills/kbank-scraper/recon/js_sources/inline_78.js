
            var g_Workspace = "s4-workspace";

            var currentDocument = $(document);
            var loadDiv = $('.load-div');

            loadDiv.width(currentDocument.width());
            loadDiv.height(currentDocument.height());
            
            $(function () {
                $('[id^="status_preview"]').hide();
                $('.load-div').hide();
            });
        