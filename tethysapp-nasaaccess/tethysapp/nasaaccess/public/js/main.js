/*****************************************************************************
 * FILE:    nasaaccess MAIN JS
 * DATE:    3/28/18
 * AUTHOR: Spencer McDonald
 * COPYRIGHT:
 * LICENSE:
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var LIBRARY_OBJECT = (function() {
    // Wrap the library in a package function
    "use strict"; // And enable strict mode for this library

    /************************************************************************
     *                      MODULE LEVEL / GLOBAL VARIABLES
     *************************************************************************/
        var current_layer,
        element,
        layers,
        map,
        public_interface,			// Object returned by the module
        variable_data,
        wms_workspace,
        geoserver_url = 'http://localhost:8081/geoserver/wms',
        gs_workspace = 'nasaaccess',
        wms_url,
        wms_layer,
        wms_source,
        basin_layer,
        dem_layer,
        featureOverlaySubbasin,
        subbasin_overlay_layers,
        geojson_list;

    /************************************************************************
     *                    PRIVATE FUNCTION DECLARATIONS
     *************************************************************************/
    var add_basins,
        add_dem,
        init_events,
        init_all,
        init_map,
        nasaaccess,
        validateQuery,
        clear_selection,
        getCookie,
        uploadShapefile,
        uploadDEM,
        submitAccessCode;



    /************************************************************************
     *                    PRIVATE FUNCTION IMPLEMENTATIONS
     *************************************************************************/

    //Get a CSRF cookie for request
    getCookie = function(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    //find if method is csrf safe
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    //add csrf token to appropriate ajax requests
    $(function() {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
                }
            }
        });
    }); //document ready


    //send data to database with error messages
    function ajax_update_database(ajax_url, ajax_data) {
        //backslash at end of url is required
        if (ajax_url.substr(-1) !== "/") {
            ajax_url = ajax_url.concat("/");
        }
        //update database
        var xhr = jQuery.ajax({
            type: "POST",
            url: ajax_url,
            dataType: "json",
            data: ajax_data
        });
        xhr.done(function(data) {
            if("success" in data) {
                // console.log("success");
            } else {
                console.log(xhr.responseText);
            }
        })
        .fail(function(xhr, status, error) {
            console.log(xhr.responseText);
        });

        return xhr;
        console.log(xhr)
    }

    init_map = function() {

//      Set initial map projection, basemap, center, and zoom
        var projection = ol.proj.get('EPSG:4326');
        var baseLayer = new ol.layer.Tile({
            source: new ol.source.BingMaps({
                key: '5TC0yID7CYaqv3nVQLKe~xWVt4aXWMJq2Ed72cO4xsA~ApdeyQwHyH_btMjQS1NJ7OHKY8BK-W-EMQMrIavoQUMYXeZIQOUURnKGBOC7UCt4',
                imagerySet: 'AerialWithLabels', // Options 'Aerial', 'AerialWithLabels', 'Road',
            }),
            title: 'baselayer'
        });

        var view = new ol.View({
            center: [0, 0],
            projection: projection,
            zoom: 3
        });
        wms_source = new ol.source.ImageWMS();

        wms_layer = new ol.layer.Image({
            source: wms_source
        });

        layers = [baseLayer];

        map = new ol.Map({
            target: document.getElementById("map"),
            layers: layers,
            view: view
        });

        map.crossOrigin = 'anonymous';
    };


    init_events = function(){
//      Set map interactions
        (function () {
            var target, observer, config;
            // select the target node
            target = $('#app-content-wrapper')[0];

            observer = new MutationObserver(function () {
                window.setTimeout(function () {
                    map.updateSize();
                }, 350);
            });
            $(window).on('resize', function () {
                map.updateSize();
            });

            config = {attributes: true};

            observer.observe(target, config);
        }());

    };


    add_basins = function(){
//      Get the selected value from the select watershed drop down
        var layer = $('#select_watershed').val();
        var options = $('#select_watershed option');

        var values = $.map(options ,function(option) {
            if(option.value !== ""){
                return option.value;
            }
        });
        if(values.length < 2){
            layer = values[0];
        }

        var layerParams
        var layer_xml
        var bbox
        var srs
        var wms_url = geoserver_url + "?service=WMS&version=1.1.1&request=GetCapabilities&"
        $.ajax({
            type: "GET",
            url: wms_url,
            dataType: 'xml',
            success: function (xml) {
//                  Get the projection and extent of the selected layer from the wms capabilities xml file
                var layers = xml.getElementsByTagName("Layer");
                var parser = new ol.format.WMSCapabilities();
                var result = parser.read(xml);
                var layers = result['Capability']['Layer']['Layer']
                for (var i=0; i<layers.length; i++) {
                    if(layers[i].Title == layer) {
                        layer_xml = xml.getElementsByTagName('Layer')[i+1]
                        layerParams = layers[i]
                    }
                }
                srs = layer_xml.getElementsByTagName('SRS')[0].innerHTML
                bbox = layerParams.BoundingBox[0].extent
                var new_extent = ol.proj.transformExtent(bbox, srs, 'EPSG:4326');
                var center = ol.extent.getCenter(new_extent)
//                  Create a new view using the extent of the new selected layer
                var view = new ol.View({
                    center: center,
                    projection: 'EPSG:4326',
                    extent: new_extent,
                    zoom: 6
                });
//                  Move the map to center on the selected watershed
                map.setView(view)
                map.getView().fit(new_extent, map.getSize());
            }
        });




//      Display styling for the selected watershed boundaries
        var sld_string = '<StyledLayerDescriptor version="1.0.0"><NamedLayer><Name>nasaaccess:'+ layer + '</Name><UserStyle><FeatureTypeStyle><Rule>\
            <PolygonSymbolizer>\
            <Name>rule1</Name>\
            <Title>Watersheds</Title>\
            <Abstract></Abstract>\
            <Fill>\
              <CssParameter name="fill">#ccd5e8</CssParameter>\
              <CssParameter name="fill-opacity">0</CssParameter>\
            </Fill>\
            <Stroke>\
              <CssParameter name="stroke">#ffffff</CssParameter>\
              <CssParameter name="stroke-width">1.5</CssParameter>\
            </Stroke>\
            </PolygonSymbolizer>\
            </Rule>\
            </FeatureTypeStyle>\
            </UserStyle>\
            </NamedLayer>\
            </StyledLayerDescriptor>';
//      Identify the wms source url, workspace, and datastore
        wms_source = new ol.source.ImageWMS({
            url: geoserver_url,
            params: {'LAYERS':gs_workspace + ':' + layer,'SLD_BODY':sld_string},
            serverType: 'geoserver',
            crossOrigin: 'Anonymous',
        });

        basin_layer = new ol.layer.Image({
            source: wms_source,
            title: 'subbasins'
        });

//      add the selected layer to the map
        map.addLayer(basin_layer);


    };


    add_dem = function(){
//      Get the selected value from the select watershed drop down
        var layer = $('#select_dem').val();
        var options = $('#select_dem option');

        var values = $.map(options ,function(option) {
            if(option.value !== ""){
                return option.value;
            }
        });
        if(values.length < 2){
            layer = values[0];
        }


        var store_id = gs_workspace + ':' + layer
        var style = 'DEM' // Corresponds to a custom SLD style in geoserver


//      Set the wms source to the url, workspace, and store for the dem layer of the selected watershed
        wms_source = new ol.source.ImageWMS({
            url: geoserver_url,
            params: {'LAYERS':store_id,'STYLES':style},
            serverType: 'geoserver',
            crossOrigin: 'Anonymous'
        });

        dem_layer = new ol.layer.Image({
            source: wms_source
        });

//      add dem layer to the map
        map.addLayer(dem_layer);
        var watershed = $('#select_watershed').val()

        if (watershed == '') {
            var layerParams
            var layer_xml
            var bbox
            var srs
            var wms_url = geoserver_url + "?service=WMS&version=1.1.1&request=GetCapabilities&"
            $.ajax({
                type: "GET",
                url: wms_url,
                dataType: 'xml',
                success: function (xml) {
    //                  Get the projection and extent of the selected layer from the wms capabilities xml file
                    var layers = xml.getElementsByTagName("Layer");
                    var parser = new ol.format.WMSCapabilities();
                    var result = parser.read(xml);
                    var layers = result['Capability']['Layer']['Layer']
                    for (var i=0; i<layers.length; i++) {
                        if(layers[i].Title == layer) {
                            layer_xml = xml.getElementsByTagName('Layer')[i+1]
                            layerParams = layers[i]
                        }
                    }
                    srs = layer_xml.getElementsByTagName('SRS')[0].innerHTML
                    bbox = layerParams.BoundingBox[0].extent
                    var new_extent = ol.proj.transformExtent(bbox, srs, 'EPSG:4326');
                    var center = ol.extent.getCenter(new_extent)
    //                  Create a new view using the extent of the new selected layer
                    var view = new ol.View({
                        center: center,
                        projection: 'EPSG:4326',
                        extent: new_extent,
                        zoom: 6
                    });
    //                  Move the map to center on the selected layer
                    map.setView(view)
                    map.getView().fit(new_extent, map.getSize());
                }
            });
        } else {
            add_basins(); // Re-add basins layer if at watershed is selected
        }
    };

    init_all = function(){
        init_map();
        init_events();
    };

    nasaaccess = function() {
//      Get the values from the nasaaccess form and pass them to the run_nasaaccess python controller
        var start = $('#start_pick').val();
        var end = $('#end_pick').val();
        var functions = [];
        var NEXT_GDPPswat_inputs = [];
        var NEX_GDPP_CMIP6_inputs = []; 

        $('.chk:checked').each(function() {
             functions.push( $( this ).val());
        });
        if(functions.includes("NEXT_GDPPswat")){
            NEXT_GDPPswat_inputs = [$("#NEXT_GDPPswat_model_select").val(),$("#NEXT_GDPPswat_type_select").val(),$("#NEXT_GDPPswat_slice_select").val()];
        }
        if(functions.includes("NEX_GDPP_CMIP6")){
            NEX_GDPP_CMIP6_inputs = [$("#NEX_GDPP_CMIP6_model_select").val(),$("#NEX_GDPP_CMIP6_type_select").val(),$("#NEX_GDPP_CMIP6_slice_select").val()];
        }
        var watershed = $('#select_watershed').val();
        var dem = $('#select_dem').val();
        var email = $('#id_email').val();
        $.ajax({
            type: 'POST',
            // url: "/apps/nasaaccess2/run/",
            url: "run/",
            data: {
                'startDate': start,
                'endDate': end,
                'functions': functions,
                'watershed': watershed,
                'dem': dem,
                'email': email,
                'nexgdpp':NEXT_GDPPswat_inputs,
                'nextgdppcmip':NEX_GDPP_CMIP6_inputs
            },
        }).done(function(data) {
            console.log(data)
            if (data.Result === 'nasaaccess is running') {
                $('#job_init').removeClass('hidden')
                setTimeout(function () {
                    $('#job_init').addClass('hidden')
                }, 10000);
            }

        });
    }

    validateQuery = function() {
        var watershed = $('#select_watershed').val()
        var dem = $('#select_dem').val()
        var start = $('#start_pick').val()
        var end = $('#end_pick').val()
        var models = [];
        $('.chk:checked').each(function() {
             models.push( $( this ).val());
        });
        if (watershed === undefined || dem === undefined || start === undefined || end === undefined || models.length == 0) {
            alert('Please be sure you have selected a watershed, DEM, start and end dates, and at least 1 function')
        } else {
            $("#cont-modal").modal('show');
        }
    }

    uploadShapefile = function () {
        let files = $('#shapefile-upload')[0].files;
        if (files.length !== 4) {
          alert('The files you selected were rejected. Upload exactly 4 files ending in shp, shx, prj and dbf.');
          return
        }
        let data = new FormData();
        Object.keys(files).forEach(function (file) {
          data.append('files', files[file]);
        });
        console.log(data);
        console.log(files);
        $.ajax({
          url: 'upload_shp/',
          type: 'POST',
          data: data,
          dataType: 'json',
          processData: false,
          contentType: false,
          success: function (result) {
            $("#loading").hide();
            let shpSelect = document.getElementById('select_watershed');
            shpSelect.options[shpSelect.options.length] = new Option(`${result.file}`, `${result.file}`);
            // $('#select_watershed').val(result.file);
            // $(`select[name^="${select_watershed}"] option:selected`).attr("selected",null);

            // $(`select[name^="${select_watershed}"] option[value="${result.file}"]`).attr("selected","selected");

            console.log(result.response);    
            map.removeLayer(basin_layer);
            map.removeLayer(dem_layer);
            add_basins();    
          },
          error: function (error) {
            console.log(error);
            $("#loading").hide();
          }
        });
      }

      uploadDEM = function () {
        let files = $('#dem-upload')[0].files;

        let data = new FormData();
        Object.keys(files).forEach(function (file) {
          data.append('files', files[file]);
        });
        console.log(data);
        console.log(files);
        $.ajax({
          url: 'upload_dem/',
          type: 'POST',
          data: data,
          dataType: 'json',
          processData: false,
          contentType: false,
          success: function (result) {
            $("#loading").hide();
            let demSelect = document.getElementById('select_dem');
            demSelect.options[demSelect.options.length] = new Option(`${result.file}`, `${result.file}`);
            // $('#select_dem').val(result.file);
            console.log(result.response);
            map.removeLayer(basin_layer);
            map.removeLayer(dem_layer);
            add_dem();       
          },
          error: function (error) {
            console.log(error);
            $("#loading").hide();
          }
        });
      }
      submitAccessCode = function(){
          let data = {
            access_code: $('#access_code_input').val()
          }
          $.ajax({
            url: 'download/',
            type: 'POST',
            data: data,
            dataType: 'json',
            xhrFields: {
                responseType: 'blob' // to avoid binary data being mangled on charset conversion
            },
            success: function(blob, status, xhr) {
                // check for a filename
                var filename = "";
                var disposition = xhr.getResponseHeader('Content-Disposition');
                if (disposition && disposition.indexOf('attachment') !== -1) {
                    var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                    var matches = filenameRegex.exec(disposition);
                    if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
                }
        
                if (typeof window.navigator.msSaveBlob !== 'undefined') {
                    // IE workaround for "HTML7007: One or more blob URLs were revoked by closing the blob for which they were created. These URLs will no longer resolve as the data backing the URL has been freed."
                    window.navigator.msSaveBlob(blob, filename);
                } else {
                    var URL = window.URL || window.webkitURL;
                    var downloadUrl = URL.createObjectURL(blob);
        
                    if (filename) {
                        // use HTML5 a[download] attribute to specify filename
                        var a = document.createElement("a");
                        // safari doesn't support this yet
                        if (typeof a.download === 'undefined') {
                            window.location.href = downloadUrl;
                        } else {
                            a.href = downloadUrl;
                            a.download = filename;
                            document.body.appendChild(a);
                            a.click();
                        }
                    } else {
                        window.location.href = downloadUrl;
                    }
        
                    setTimeout(function () { URL.revokeObjectURL(downloadUrl); }, 100); // cleanup
                }
            },
            error: function (error) {
              console.log(error);
            //   $("#loading").hide();
            }
          });
          
      }



    /************************************************************************
     *                        DEFINE PUBLIC INTERFACE
     *************************************************************************/

    public_interface = {

    };

    /************************************************************************
     *                  INITIALIZATION / CONSTRUCTOR
     *************************************************************************/

    // Initialization: jQuery function that gets called when
    // the DOM tree finishes loading

    $(function() {
        init_all();
//        $("#help-modal").modal('show');
        $('#loading').addClass('hidden')

        $('#shp_submit').click(function(){
            $('#loading').removeClass('hidden')
        });

        $('#dem_submit').click(function(){
            $('#loading').removeClass('hidden')
        });

        $('#nasaaccess').click(function() {
            validateQuery();
        });

        $('#submit_form').click(function() {
            $("#cont-modal").modal('hide');
            nasaaccess();
        });

        $('#download_data').click(function() {
            $("#download-modal").modal('show');
        });

        $('#select_watershed').change(function() {
            map.removeLayer(basin_layer);
            add_basins();
        });

        $('#select_dem').change(function() {
            map.removeLayer(basin_layer);
            map.removeLayer(dem_layer);
            add_dem();
        });

        $('#addShp').click(function() {
            console.log('Add Watershed')
            $("#shp-modal").modal('show');
        })

        $('#addDem').click(function() {
            console.log('Add DEM')
            $("#dem-modal").modal('show');
        })
        $("#shp_submit").click(uploadShapefile)
        $("#dem_submit").click(uploadDEM)
        $("#submit_access_code").click(submitAccessCode)

        $("#NEXT_GDPPswat_input").change(function(){
            if(this.checked){
                $("#NEXT_GDPPswat_id_block").removeClass("h-0");
                $("#NEXT_GDPPswat_id_block").addClass("max-h-fit");
                $("#NEXT_GDPPswat_id_block").removeClass("overflow-hidden");
                $("#NEXT_GDPPswat_id_block").addClass("ease-in");
                $("#NEXT_GDPPswat_id_block").addClass("duration-700");
            }
            else{
                $("#NEXT_GDPPswat_id_block").removeClass("max-h-fit");
                $("#NEXT_GDPPswat_id_block").addClass("h-0");
                $("#NEXT_GDPPswat_id_block").addClass("overflow-hidden");
                $("#NEXT_GDPPswat_id_block").removeClass("ease-in");
                $("#NEXT_GDPPswat_id_block").removeClass("duration-700");
            }
        });

        $("#NEX_GDPP_CMIP6_input").change(function(){
            if(this.checked){
                $("#NEX_GDPP_CMIP6_id_block").removeClass("h-0");
                $("#NEX_GDPP_CMIP6_id_block").addClass("max-h-fit");
                $("#NEX_GDPP_CMIP6_id_block").removeClass("overflow-hidden");
                $("#NEX_GDPP_CMIP6_id_block").addClass("ease-in");
                $("#NEX_GDPP_CMIP6_id_block").addClass("duration-700");
            }
            else{
                $("#NEX_GDPP_CMIP6_id_block").removeClass("max-h-fit");
                $("#NEX_GDPP_CMIP6_id_block").addClass("h-0");
                $("#NEX_GDPP_CMIP6_id_block").addClass("overflow-hidden");
                $("#NEX_GDPP_CMIP6_id_block").removeClass("ease-in");
                $("#NEX_GDPP_CMIP6_id_block").removeClass("duration-700");
            }
        });

    });




    return public_interface;


}());// End of package wrapper