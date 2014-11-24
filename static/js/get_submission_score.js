$(document).ready(function() {
  function getSubmissionScore(element) {
    finished = $(element).attr("data-finished");
    if(finished) {
      return;
    }

    $.ajax({
      url: "/rest/submission/" + $(element).data("id") + "/?format=json",
      dataType: "json",
      error: function() {
        $(element).text("Error");
      },
      success: function(json) {
        this.status = json['status'];
        this.score = json['score'];

        if(this.status=="judged") {
          $(element).text(this.score);
          $(element).attr("data-finished", true);
        } else {
          $(element).text(this.status);
          // Perform a new check in 5 seconds
          setTimeout(function(){
            $(element).text(this.status);
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
  $("span[data-ajax='submission']").each(function(){
    getSubmissionScore(this);
  });
});
