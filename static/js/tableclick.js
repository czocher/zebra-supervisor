$(document).ready(function(){
  $('tr').on({
    'click': function() {
      var href = $(this).find("a").attr("href");
      if(href) {
        window.location = href;
      }
    },
  });
});
