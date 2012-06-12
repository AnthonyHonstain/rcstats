
// usage: log('inside coolFunc', this, arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function(){
  log.history = log.history || [];   // store logs to an array for reference
  log.history.push(arguments);
  if(this.console) {
    arguments.callee = arguments.callee.caller;
    var newarr = [].slice.call(arguments);
    (typeof console.log === 'object' ? log.apply.call(console.log, console, newarr) : console.log.apply(console, newarr));
  }
};

// make it safe to use console.log always
(function(b){function c(){}for(var d="assert,clear,count,debug,dir,dirxml,error,exception,firebug,group,groupCollapsed,groupEnd,info,log,memoryProfile,memoryProfileEnd,profile,profileEnd,table,time,timeEnd,timeStamp,trace,warn".split(","),a;a=d.pop();){b[a]=b[a]||c}})((function(){try
{console.log();return window.console;}catch(err){return window.console={};}})());


/*-------------------------------
* jQuery UI Modules
-------------------------------*/
$(function(){

	// Accordion
	$("#accordion").accordion({ header: "h3", collapsible: true, active: false, autoHeight: false  });

	// Tabs
	$('#tabs').tabs();

});

jQuery(document).ready(function(){
$('#toggle h3').click(function() {
	$(this).next().toggle('fast');
	return false;
}).next().hide();
});

			
/*-------------------------------
* jQuery Plugin: For image hover
-------------------------------*/

$(document).ready(function() {
    $('.viewport').mouseenter(function(e) {
        $(this).children('a').children('span').fadeIn(300);
    }).mouseleave(function(e) {
        $(this).children('a').children('span').fadeOut(300);
    });
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
* jQuery Plugin: Hook up the FlexSlider
-------------------------------*/ 

$(window).load(function() {
	$('.flexslider').flexslider({
		animation: "fade",              //String: Select your animation type, "fade" or "slide"
		slideDirection: "horizontal",   //String: Select the sliding direction, "horizontal" or "vertical"
		slideshow: true,                //Boolean: Animate slider automatically
		slideshowSpeed: 5000,           //Integer: Set the speed of the slideshow cycling, in milliseconds
		animationDuration: 600,         //Integer: Set the speed of animations, in milliseconds
		directionNav: true,             //Boolean: Create navigation for previous/next navigation? (true/false)
		controlNav: true,               //Boolean: Create navigation for paging control of each clide? Note: Leave true for manualControls usage
		keyboardNav: true,              //Boolean: Allow slider navigating via keyboard left/right keys
		mousewheel: false,              //Boolean: Allow slider navigating via mousewheel
		prevText: "Previous",           //String: Set the text for the "previous" directionNav item
		nextText: "Next",               //String: Set the text for the "next" directionNav item
		pausePlay: false,               //Boolean: Create pause/play dynamic element
		pauseText: 'Pause',             //String: Set the text for the "pause" pausePlay item
		playText: 'Play',               //String: Set the text for the "play" pausePlay item
		randomize: false,               //Boolean: Randomize slide order
		slideToStart: 0,                //Integer: The slide that the slider should start on. Array notation (0 = first slide)
		animationLoop: true,            //Boolean: Should the animation loop? If false, directionNav will received "disable" classes at either end
		pauseOnAction: false,            //Boolean: Pause the slideshow when interacting with control elements, highly recommended.
		pauseOnHover: true,            //Boolean: Pause the slideshow when hovering over slider, then resume when no longer hovering
		controlsContainer: "",          //Selector: Declare which container the navigation elements should be appended too. Default container is the flexSlider element. Example use would be ".flexslider-container", "#container", etc. If the given element is not found, the default action will be taken.
		manualControls: "",             //Selector: Declare custom control navigation. Example would be ".flex-control-nav li" or "#tabs-nav li img", etc. The number of elements in your controlNav should match the number of slides/tabs.
		start: function(){},            //Callback: function(slider) - Fires when the slider loads the first slide
		before: function(){},           //Callback: function(slider) - Fires asynchronously with each slider animation
		after: function(){},            //Callback: function(slider) - Fires after each slider animation completes
		end: function(){}               //Callback: function(slider) - Fires when the slider reaches the last slide (asynchronous)
	});
});

/*-------------------------------
* jQuery Plugin: Slides - jQuery Slider
-------------------------------*/

$(function(){
			$('#testimonial').slides({
				preload: true,
				preloadImage: 'images/loading.gif',
				play: 5000,
				pause: 2500,
				hoverPause: true,
				effect: 'fade',
				crossfade: false,
				fadeSpeed: 200,
				generateNextPrev: true,
				generatePagination: true,
				autoHeight: true
			}); 
			$('#slide_content').slides({
				preload: true,
				preloadImage: 'images/loading.gif',
				generatePagination: false,
				generateNextPrev: true,
				autoHeight: true
			});
			$('#slide_content_gallery').slides({
				preload: true,
				preloadImage: 'images/loading.gif',
				generatePagination: false,
				generateNextPrev: true,
				autoHeight: true
			});
			$('#single_portfolio_slider').slides({
				preload: true,
				preloadImage: 'images/loading.gif',
				generatePagination: false,
				generateNextPrev: true,
				autoHeight: true,
				play: 3000,
				pause: 2500
			});
			$('#single_portfolio_slider_half').slides({
				preload: true,
				preloadImage: 'images/loading.gif',
				generatePagination: false,
				generateNextPrev: true,
				autoHeight: true,
				play: 3000,
				pause: 2500
			});
			$('#post_slider_1').slides({
				preload: true,
				preloadImage: 'images/loading.gif',
				generatePagination: false,
				generateNextPrev: true,
				autoHeight: true
			});
			
				$('#main_slider').slides({
				preload: true,
				play: 5000,			
				// effect: 'fade',
				// crossfade: false,
				preloadImage: 'images/loading.gif',
				generatePagination: true,
				generateNextPrev: true,
				autoHeight: true,
				animationStart: function(current){
					$('.caption').animate({
						bottom:-35
					},100);
					if (window.console && console.log) {
						// example return of current slide number
						console.log('animationStart on slide: ', current);
					};
				},
				animationComplete: function(current){
					$('.caption').animate({
						bottom:0
					},200);
					if (window.console && console.log) {
						// example return of current slide number
						console.log('animationComplete on slide: ', current);
					};
				},
				slidesLoaded: function() {
					$('.caption').animate({
						bottom:0
					},200);
				}
			});
			
			$('#main_slider_nocaption').slides({
				preload: true,
				play: 5000,			
				effect: 'fade',
				crossfade: false,
				preloadImage: 'images/loading.gif',
				generatePagination: false,
				generateNextPrev: true,
				autoHeight: true,
				animationStart: function(current){
					if (window.console && console.log) {
						// example return of current slide number
						console.log('animationStart on slide: ', current);
					};
				},
				animationComplete: function(current){
					
					if (window.console && console.log) {
						// example return of current slide number
						console.log('animationComplete on slide: ', current);
					};
				},
			
			});
			
			
			
		});


/*-------------------------------
* jQuery Plugin: Scroll to Top
* by Craig Wilson, Ph.Creative (http://www.ph-creative.com)
* 
* Copyright (c) 2009 Ph.Creative Ltd.
* Description: Adds an unobtrusive "Scroll to Top" link to your page with smooth scrolling.
* For usage instructions and version updates to go http://blog.ph-creative.com/post/jquery-plugin-scroll-to-top.aspx
* 
* Version: 1.0, 12/03/2009
-------------------------------*/

$(function(){$.fn.scrollToTop=function(){$(this).hide().removeAttr("href");if($(window).scrollTop()!="0"){$(this).fadeIn("slow")}var scrollDiv=$(this);$(window).scroll(function(){if($(window).scrollTop()=="0"){$(scrollDiv).fadeOut("slow")}else{$(scrollDiv).fadeIn("slow")}});$(this).click(function(){$("html, body").animate({scrollTop:0},"slow")})}});

  $(function() {
                $(".gotop").scrollToTop();
            });
			


	
