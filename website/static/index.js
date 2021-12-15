$("#add_projections").click(function(){
    $.post("/changeProjection",
    {
      name: "Donald Duck",
      city: "Duckburg"
    });
    
  });

  $(function(){
	$('#add_projections').click(function(){
		var user = $('#movie_insert').val();
		$.ajax({
			url: '/changeProjection',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});