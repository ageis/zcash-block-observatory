$(document).ready(function() {
  $('#recentBlocks').DataTable({
    "info": false,
    "order": [[ 0, "desc" ]],
    "oLanguage": {
      "sSearch": "Filter blocks on page by search criteria:"
    }
  });

  $('#moreBlocks').click(function(e){
    e.preventDefault()
    last = $('#recentBlocks tr:last-child td:first-child').html()
    height = last - 1
    window.location = "/height/" + height
  });
});
