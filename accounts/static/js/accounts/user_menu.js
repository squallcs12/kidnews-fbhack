jQuery(function () {
    var $ = jQuery;

    var opened_links = [];
    var opened_menu = $.cookie("user_openned_menu");
    if (opened_menu) {
        opened_links = opened_menu.split(";");
    }

    $("#userMenu .panel-heading a").each(function () {
        var this_link = $(this).prop("href").split("#")[1];
        if (opened_links.indexOf(this_link) !== -1) {
            $(this).click();
        }
    });

    $("#userMenu .panel-heading a").click(function (e) {
        var this_link = $(this).prop("href").split("#")[1];

        var found = opened_links.indexOf(this_link);

        if (found === -1) {
            opened_links.push(this_link);
        } else {
            opened_links.splice(found, 1);
        }
        opened_menu = opened_links.join(";");

        var date = new Date();
        date.setTime(date.getTime() + (8 * 60 * 60 * 1000));
        $.cookie("user_openned_menu", opened_menu, {path: '/', expires: date});
    });

    $("#userMenu .top-buttons a").click(function (e) {
        var click = $(this).data("click");
        if (click == "expand") {
            $("#userMenu .panel-heading a").each(function () {
                var this_link = $(this).prop("href").split("#")[1];
                if (opened_links.indexOf(this_link) === -1) {
                    $(this).click();
                }
            });
        } else {
            $("#userMenu .panel-heading a").each(function () {
                var this_link = $(this).prop("href").split("#")[1];
                if (opened_links.indexOf(this_link) !== -1) {
                    $(this).click();
                }
            });
        }
        e.preventDefault();
        return false;
    });
});
