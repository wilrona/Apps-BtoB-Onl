var lastClickedMarker;
var searchClicked;
var mapAutoZoom;

// Hero Map on Home ----------------------------------------------------------------------------------------------------

function heroMap(_latitude,_longitude, element, markerTarget, sidebarResultTarget, showMarkerLabels, mapDefaultZoom, formulaire, url_data, infobox_url){
    if( document.getElementById(element) != null ){

        // Create google map first -------------------------------------------------------------------------------------

        if( !mapDefaultZoom ){
            mapDefaultZoom = 14;
        }

        if( !optimizedDatabaseLoading ){
            var optimizedDatabaseLoading = 0;
        }

        var map = new google.maps.Map(document.getElementById(element), {
            zoom: mapDefaultZoom,
            scrollwheel: true,
            center: new google.maps.LatLng(_latitude, _longitude),
            mapTypeId: "roadmap",
            styles: [{"featureType":"administrative","elementType":"labels.text.fill","stylers":[{"color":"#c6c6c6"}]},{"featureType":"landscape","elementType":"all","stylers":[{"color":"#f2f2f2"}]},{"featureType":"poi","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"road","elementType":"all","stylers":[{"saturation":-100},{"lightness":45}]},{"featureType":"road.highway","elementType":"all","stylers":[{"visibility":"simplified"}]},{"featureType":"road.highway","elementType":"geometry.fill","stylers":[{"color":"#ffffff"}]},{"featureType":"road.arterial","elementType":"labels.icon","stylers":[{"visibility":"off"}]},{"featureType":"transit","elementType":"all","stylers":[{"visibility":"off"}]},{"featureType":"water","elementType":"all","stylers":[{"color":"#dde6e8"},{"visibility":"on"}]}]
        });

        // Load necessary data for markers using PHP (from database) after map is loaded and ready ---------------------

        var allMarkers;

        //  When optimization is enabled, map will load the data in Map Bounds every time when it's moved. Otherwise will load data at once

        if( optimizedDatabaseLoading == 1 ){
            google.maps.event.addListener(map, 'idle', function(){
                if( searchClicked != 1 ){
                    var ajaxData = {
                        optimized_loading: 1,
                        north_east_lat: map.getBounds().getNorthEast().lat(),
                        north_east_lng: map.getBounds().getNorthEast().lng(),
                        south_west_lat: map.getBounds().getSouthWest().lat(),
                        south_west_lng: map.getBounds().getSouthWest().lng()
                    };
                    if( markerCluster != undefined ){
                        markerCluster.clearMarkers();
                    }
                    loadData(url_data, ajaxData);
                }
            });
        }
        else {
            google.maps.event.addListenerOnce(map, 'idle', function(){
                loadData(url_data, formulaire);
            });
        }

        if( showMarkerLabels == true ){
            $(".hero-section .map").addClass("show-marker-labels");
        }

        // Create and place markers function ---------------------------------------------------------------------------

        var i;
        var a;
        var newMarkers = [];
        var resultsArray = [];
        var visibleMarkersId = [];
        var visibleMarkersOnMap = [];
        var markerCluster;

        function placeMarkers(markers){

            newMarkers = [];

            for (i = 0; i < markers.length; i++) {

                var marker;
                var markerContent = document.createElement('div');
                var thumbnailImage;

                if( markers[i]["image"] != undefined ){
                    thumbnailImage = markers[i]["image"];
                }
                else {
                    thumbnailImage = "/static/images/bg-flou.jpg";
                }

                if( markers[i]["featured"] == 1 ){
                    markerContent.innerHTML =
                    '<div class="marker" data-id="'+ markers[i]["id"] +'">' +
                        '<div class="title">'+ markers[i]["name"] +'</div>' +
                        '<div class="marker-wrapper">' +
                            '<div class="tag"><i class="fa fa-check"></i></div>' +
                            '<div class="pin">' +
                                '<div class="image" style="background-image: url('+ thumbnailImage +');"></div>' +
                            '</div>' +
                        '</div>' +
                    '</div>';
                }
                else {
                    markerContent.innerHTML =
                        '<div class="marker" data-id="'+ markers[i]["id"] +'">' +
                            '<div class="title">'+ markers[i]["name"] +'</div>' +
                            '<div class="marker-wrapper">' +
                                '<div class="pin">' +
                                '<div class="image" style="background-image: url('+ thumbnailImage +');"></div>' +
                            '</div>' +
                        '</div>';
                }

                // Latitude, Longitude and Address

                if ( markers[i]["latitude"] && markers[i]["longitude"]){
                    renderRichMarker(i,"latitudeLongitude");
                }
                //
                //// Only Address
                //
                //else if ( markers[i]["address"] && !markers[i]["latitude"] && !markers[i]["longitude"] ){
                //    renderRichMarker(i,"address");
                //}
                //
                //// Only Latitude and Longitude
                //
                //else if ( markers[i]["latitude"] && markers[i]["longitude"] && !markers[i]["address"] ) {
                //    renderRichMarker(i,"latitudeLongitude");
                //}

                // No coordinates

                else {
                    console.log( "No location coordinates");
                }
            }

            // Create marker using RichMarker plugin -------------------------------------------------------------------

            function renderRichMarker(i,method){
                if( method == "latitudeLongitude" ){
                    marker = new RichMarker({
                        position: new google.maps.LatLng( markers[i]["latitude"], markers[i]["longitude"] ),
                        map: map,
                        draggable: false,
                        content: markerContent,
                        flat: true
                    });
                    google.maps.event.addListener(marker, 'click', (function(marker, i) {
                        return function() {
                            //if( markerTarget == "sidebar"){
                            //    openSidebarDetail( $(this.content.firstChild).attr("data-id") );
                            //}
                            if( markerTarget == "infobox" ){
                                openInfobox( $(this.content.firstChild).attr("data-id"), this, i );
                            }
                            //else if( markerTarget == "modal" ){
                            //    openModal($(this.content.firstChild).attr("data-id"), "modal_item.php");
                            //}
                        }
                    })(marker, i));
                    newMarkers.push(marker);
                }
                //else if ( method == "address" ){
                //    a = i;
                //    var geocoder = new google.maps.Geocoder();
                //    var geoOptions = {
                //        address: markers[i]["address"]
                //    };
                //    geocoder.geocode(geoOptions, geocodeCallback(markerContent));
                //
                //}


                var bounds  = new google.maps.LatLngBounds();
                for (var i = 0; i < newMarkers.length; i++ ) {
                    bounds.extend(newMarkers[i].getPosition());
                }
                map.fitBounds(bounds);


            }

            // Ajax loading of infobox -------------------------------------------------------------------------------------

            var lastInfobox;

            function openInfobox(id, _this, i){
                $.ajax({
                    url: infobox_url,
                    dataType: "html",
                    data: { id: id },
                    method: "POST",
                    success: function(results){
                        infoboxOptions = {
                            content: results,
                            disableAutoPan: false,
                            pixelOffset: new google.maps.Size(-135, -50),
                            zIndex: null,
                            alignBottom: true,
                            boxClass: "infobox-wrapper",
                            enableEventPropagation: true,
                            closeBoxMargin: "0px 0px -8px 0px",
                            closeBoxURL: "/static/images/close-btn.png",
                            infoBoxClearance: new google.maps.Size(1, 1)
                        };

                        if( lastInfobox != undefined ){
                            lastInfobox.close();
                        }

                        newMarkers[i].infobox = new InfoBox(infoboxOptions);
                        newMarkers[i].infobox.open(map, _this);
                        lastInfobox = newMarkers[i].infobox;

                        setTimeout(function(){
                            //$("div#"+ id +".item.infobox").parent().addClass("show");
                            $(".item.infobox[data-id="+ id +"]").parent().addClass("show");
                        }, 10);

                        google.maps.event.addListener(newMarkers[i].infobox,'closeclick',function(){
                            $(lastClickedMarker).removeClass("active");
                        });
                    },
                    error : function () {
                        console.log("error");
                    }
                });
            }


            //function openSidebarDetail(id){
            //    $.ajax({
            //        url: "assets/external/sidebar_detail.php",
            //        data: { id: id },
            //        method: "POST",
            //        success: function(results){
            //            $(".sidebar-wrapper").html(results);
            //            $(".results-wrapper").removeClass("loading");
            //            initializeOwl();
            //            ratingPassive(".sidebar-wrapper .sidebar-content");
            //            initializeFitVids();
            //            socialShare();
            //            initializeReadMore();
            //            $(".sidebar-wrapper .back").on("click", function(){
            //                $(".results-wrapper").removeClass("show-detail");
            //                $(lastClickedMarker).removeClass("active");
            //            });
            //            $(document).keyup(function(e) {
            //                switch(e.which) {
            //                    case 27: // ESC
            //                        $(".sidebar-wrapper .back").trigger('click');
            //                        break;
            //                }
            //            });
            //            $(".results-wrapper").addClass("show-detail");
            //        },
            //        error : function (e) {
            //            console.log("error " + e);
            //        }
            //    });
            //}

            // Highlight result in sidebar on marker hover -------------------------------------------------------------

            //$(".marker").on("mouseenter", function(){
            //    var id = $(this).attr("data-id");
            //    $(".results-wrapper .results-content .result-item[data-id="+ id +"] a" ).addClass("hover-state");
            //}).on("mouseleave", function(){
            //    var id = $(this).attr("data-id");
            //        $(".results-wrapper .results-content .result-item[data-id="+ id +"] a" ).removeClass("hover-state");
            //});

            $(".marker").on("click", function(){
                var id = $(this).attr("data-id");
                $(lastClickedMarker).removeClass("active");
                $(this).addClass("active");
                lastClickedMarker = $(this);
            });

            // Marker clusters -----------------------------------------------------------------------------------------

            var clusterStyles = [
                {
                    url: 'assets/img/cluster.png',
                    height: 36,
                    width: 36
                }
            ];

            markerCluster = new MarkerClusterer(map, newMarkers, { styles: clusterStyles, maxZoom: 16, ignoreHidden: true });

            // Show results in sidebar after map is moved --------------------------------------------------------------

            //google.maps.event.addListener(map, 'idle', function() {
            //    renderResults();
            //});

            //renderResults();

            // Results in the sidebar ----------------------------------------------------------------------------------

            function renderResults(){
                resultsArray = [];
                visibleMarkersId = [];
                visibleMarkersOnMap = [];

                for (var i = 0; i < newMarkers.length; i++) {
                    if ( map.getBounds().contains(newMarkers[i].getPosition()) ){
                        visibleMarkersOnMap.push(newMarkers[i]);
                        visibleMarkersId.push( $(newMarkers[i].content.firstChild).attr("data-id") );
                        newMarkers[i].setVisible(true);
                    }
                    else {
                        newMarkers[i].setVisible(false);
                    }
                }
                markerCluster.repaint();

                // Ajax load data for sidebar results after markers are placed

                //$.ajax({
                //    url: "assets/external/sidebar_results.php",
                //    method: "POST",
                //    data: { markers: visibleMarkersId },
                //    success: function(results){
                //        resultsArray.push(results); // push the results from php into array
                //        $(".results-wrapper .results-content").html(results); // render the new php data into html element
                //        $(".results-wrapper .section-title h2 .results-number").html(visibleMarkersId.length); // show the number of results
                //        ratingPassive(".results-wrapper .results"); // render rating stars
                //
                //        // Hover on the result in sidebar will highlight the marker
                //
                //        $(".result-item").on("mouseenter", function(){
                //            $(".map .marker[data-id="+ $(this).attr("data-id") +"]").addClass("hover-state");
                //        }).on("mouseleave", function(){
                //                $(".map .marker[data-id="+ $(this).attr("data-id") +"]").removeClass("hover-state");
                //        });
                //
                //        trackpadScroll("recalculate");
                //
                //        //Show detailed information in sidebar
                //
                //        $(".result-item").children("a").on("click", function(e){
                //            if( sidebarResultTarget == "sidebar" ){
                //                e.preventDefault();
                //                openSidebarDetail( $(this).parent().attr("data-id") );
                //            }
                //            else if( sidebarResultTarget == "modal" ){
                //                e.preventDefault();
                //                openModal( $(this).parent().attr("data-id"), "modal_item.php" );
                //            }
                //
                //            $(lastClickedMarker).removeClass("active");
                //
                //            $(".map .marker[data-id="+ $(this).parent().attr("data-id") +"]").addClass("active");
                //            lastClickedMarker = $(".map .marker[data-id="+ $(this).parent().attr("data-id") +"]");
                //        });
                //
                //    },
                //    error : function (e) {
                //        console.log(e);
                //    }
                //});

            }
        }

        /*
        $("[data-ajax-live='location']").on("changed.bs.select", function (e) {
            ajaxAction( $(this), "location" );
        });

        $("[data-ajax-live='string']").on("changed.bs.select", function (e) {
            ajaxAction( $(this), "string" );
        });
        */

        $("[data-ajax-response='map']").on("click", function(e){
            e.preventDefault();
            var dataFile = $(this).attr("data-ajax-data-file");
            searchClicked = 1;
            if( $(this).attr("data-ajax-auto-zoom") == 1 ){
                mapAutoZoom = 1;
            }
            var form = $(this).closest("form");
            var ajaxData = form.serialize();
            markerCluster.clearMarkers();
            loadData(dataFile, ajaxData);
        });

        function loadData(url, ajaxData){
            $.ajax({
                url: url,
                dataType: "json",
                method: "POST",
                data: ajaxData,
                cache: false,
                success: function(results){
                    for( var i=0; i <newMarkers.length; i++ ){
                        newMarkers[i].setMap(null);
                    }
                    allMarkers = results;
                    placeMarkers(results);
                },
                error : function (e) {
                    console.log(e);
                }
            });
        }

        // Geo Location ------------------------------------------------------------------------------------------------

        function success(position) {
            var center = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
            map.panTo(center);
            $('#map').removeClass('fade-map');
        }

        // Geo Location on button click --------------------------------------------------------------------------------

        $('.geo-location').on("click", function() {
            if (navigator.geolocation) {
                $('#map').addClass('fade-map');
                navigator.geolocation.getCurrentPosition(success);
            } else {
                error('Geo Location is not supported');
            }
        });

        // Autocomplete

        //autoComplete(map);


    }
    else {
        console.log("No map element");
    }
}