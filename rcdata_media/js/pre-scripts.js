
/*-------------------------------
* jQuery Plugin: Super Fish Menu
-------------------------------*/

    jQuery(document).ready(function($){ 
        $("ul.main-menu").supersubs({ 
            minWidth:    12,   // minimum width of sub-menus in em units 
            maxWidth:    150,   // maximum width of sub-menus in em units 
            extraWidth:  1     // extra width can ensure lines don't sometimes turn over 
                               // due to slight rounding differences and font-family 
        }).superfish({ 
            delay:       300,                            // one second delay on mouseout 
            animation:   {opacity:'show',height:'show'},  // fade-in and slide-down animation 
            speed:       'normal',                          // faster animation speed 
            autoArrows:  false,                           // disable generation of arrow mark-up 
            dropShadows: true                            // disable drop shadows 
        });  // call supersubs first, then superfish, so that subs are 
                         // not display:none when measuring. Call before initialising 
                         // containing tabs for same reason. 
    }); 
	
/*-------------------------------
* jQuery Plugin: Pretty Photo
-------------------------------*/
jQuery(document).ready(function($){
	  $("a[data-rel^='prettyPhoto']").prettyPhoto({hook: 'data-rel'});
	  $(".slides_container:first a[rel^='prettyPhoto']").prettyPhoto({animation_speed:'normal'});
	  $(".content_container_fix:first a[rel^='prettyPhoto']").prettyPhoto({animation_speed:'normal'});
  });
  
  /*-------------------------------
* jQuery Plugin: Quicksand - filter plugin
-------------------------------*/		

var Sorter = jQuery.noConflict();
jQuery.noConflict();

jQuery(document).ready(function($){
 	// Clone applications to get a second collection
	var $data = Sorter(".filter-posts").clone();
	
	Sorter('.option-set li').click(function(e) {
		Sorter(".filter li").removeClass("active");	
		// Use the last category class as the category to filter by.
		var filterClass=Sorter(this).attr('class').split(' ').slice(-1)[0];
		
		if (filterClass == 'all-projects') {
			var $filteredData = $data.find('.view_box');
		} else {
			var $filteredData = $data.find('.view_box[data-type~=' + filterClass + ']');
		}
		Sorter(".filter-posts").quicksand($filteredData, {
			duration: 400,
			easing: 'jswing',
			adjustHeight: 'auto'
		}, function(){
			
	  		$("a[data-rel^='prettyPhoto']").prettyPhoto({hook: 'data-rel'});
			$(".content_container_fix:first a[rel^='prettyPhoto']").prettyPhoto({
				autoplay_slideshow: false, 
				overlay_gallery: false, 
				show_title: false
			});
		});

		Sorter(this).addClass("active");
		// Prevent the browser jump to the link anchor		
		return false;
	});
});