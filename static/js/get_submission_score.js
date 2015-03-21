$(document).ready(function() {
  // Dummy translations for makemessages
  gettext("Judging");
  gettext("Judged");
  gettext("Waiting");

  function getSubmissionScore(element) {
    finished = $(element).attr("data-finished");
    if(finished === 'true') {
      return;
    }

    $.ajax({
      url: "/rest/submission/" + $(element).data("id") + "/?format=json",
      dataType: "json",
      error: function() {
        $(element).text(gettext("Communication error"));
      },
      success: function(json) {
        this.status = json['status'];
        this.score = json['score'];

        if(this.status=="Judged") {
          $(element).text(this.score);
          $(element).attr("data-finished", true);
        } else {
          $(element).text(gettext(this.status));
          // Perform a new check in 5 seconds
          setTimeout(function(){
            $(element).text(gettext(this.status));
            getSubmissionScore(element);
          }, 5000);

          // In the meantime add some dots to show we're doing something
          for(var i = 1; i < 4; i++) {
            setTimeout(function() {
              $(element).append(".");
            }, i*1200);
          }
        }
      },
    });
  }
  $("span[data-ajax='submission'][data-finished='false']").each(function(){
    var that = this;
    setTimeout(function(){
      getSubmissionScore(that);
    }, 5000);
    for(var i = 1; i < 4; i++) {
      setTimeout(function() {
        $(that).append(".");
      }, i*1200);
    }
  });
});
