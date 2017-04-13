$(document).ready(function() {
  $('#moreBlocks').click(function(e){
    e.preventDefault()
    last = $('#recentBlocks tr:last-child td:first-child').html()
    height = last - 1
    window.location = "/height/" + height
  });
});
