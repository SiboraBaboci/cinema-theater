$("#main_search_button").click(function(){    
    console.log($("#main_search_form").val())
    var search_string = $("#main_search_form").val().toString().toUpperCase()

    if ($("#main_search_form").val() == ""){
        alert("Please insert a search term.")
        /*display all*/
        $( ".card-title" ).each(function() {
            $(this).parent().parent().css("display","block")
            });
    }
    else{
        $( ".card-title" ).each(function() {
            var title = $(this).text().toString().toUpperCase()
            if (title.indexOf(search_string) > -1){
                $(this).parent().parent().css("display","block")
            }  
            else {
                $(this).parent().parent().css("display","none")
            }
            });
    }   
});

