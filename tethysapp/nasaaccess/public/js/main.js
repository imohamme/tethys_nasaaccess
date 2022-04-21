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

var LIBRARY_OBJECT = (function () {
  // Wrap the library in a package function
  "use strict"; // And enable strict mode for this library

  /************************************************************************
   *                      MODULE LEVEL / GLOBAL VARIABLES
   *************************************************************************/
  var current_layer,
    element,
    layers,
    map,
    public_interface, // Object returned by the module
    variable_data,
    wms_workspace,
    geoserver_url = GEOSERVER_REST_URL.replace("rest", "wms"),
    gs_workspace = GEOSERVER_WORKSPACE,
    wms_url,
    wms_layer,
    wms_source,
    basin_layer,
    dem_layer,
    featureOverlaySubbasin,
    subbasin_overlay_layers,
    geojson_list,
    colors_unique = ["#FF0000", "#00FF00", "#000000", "#00FFFF", "#FF00FF"],
    myChart,
    baseLayer,
    view,
    projection,
    layer_points = {};
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
    submitAccessCode,
    create_graphs,
    create_series_dict,
    plotAccessCode,
    map_layers,
    featureStyle,
    getValues,
    getIconLegend,
    removeLayersFunctions,
    updateLegend,
    showPlot;

  /************************************************************************
   *                    PRIVATE FUNCTION IMPLEMENTATIONS
   *************************************************************************/
  showPlot = function () {
    $("#map").addClass("h-[48rem]");
    $("#map").removeClass("h-full");
    $("#graphs__panel").removeClass("hidden");
    setTimeout(function () {
      map.updateSize();
    }, 200);
  };

  //Get a CSRF cookie for request
  getCookie = function (name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != "") {
      var cookies = document.cookie.split(";");
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  //find if method is csrf safe
  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
  }

  //add csrf token to appropriate ajax requests
  $(function () {
    $.ajaxSetup({
      beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        }
      },
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
      data: ajax_data,
    });
    xhr
      .done(function (data) {
        if ("success" in data) {
          // console.log("success");
        } else {
          console.log(xhr.responseText);
        }
      })
      .fail(function (xhr, status, error) {
        console.log(xhr.responseText);
      });

    return xhr;
    console.log(xhr);
  }

  init_map = function () {
    //      Set initial map projection, basemap, center, and zoom
    projection = ol.proj.get("EPSG:4326");
    baseLayer = new ol.layer.Tile({
      source: new ol.source.BingMaps({
        key: "5TC0yID7CYaqv3nVQLKe~xWVt4aXWMJq2Ed72cO4xsA~ApdeyQwHyH_btMjQS1NJ7OHKY8BK-W-EMQMrIavoQUMYXeZIQOUURnKGBOC7UCt4",
        imagerySet: "AerialWithLabels", // Options 'Aerial', 'AerialWithLabels', 'Road',
      }),
      title: "baselayer",
    });

    view = new ol.View({
      center: [0, 0],
      projection: projection,
      zoom: 3,
    });
    wms_source = new ol.source.ImageWMS();

    wms_layer = new ol.layer.Image({
      source: wms_source,
    });

    layers = [baseLayer];

    map = new ol.Map({
      target: document.getElementById("map"),
      layers: layers,
      view: view,
    });

    map.crossOrigin = "anonymous";
  };

  init_events = function () {
    //      Set map interactions
    (function () {
      var target, observer, config;
      // select the target node
      target = $("#app-content-wrapper")[0];

      observer = new MutationObserver(function () {
        window.setTimeout(function () {
          map.updateSize();
        }, 350);
      });
      $(window).on("resize", function () {
        map.updateSize();
      });

      config = { attributes: true };

      observer.observe(target, config);
    })();
  };

  add_basins = function () {
    //      Get the selected value from the select watershed drop down
    var layer = $("#select_watershed").val();
    var options = $("#select_watershed option");

    var values = $.map(options, function (option) {
      if (option.value !== "") {
        return option.value;
      }
    });
    if (values.length < 2) {
      layer = values[0];
    }

    var layerParams;
    var layer_xml;
    var bbox;
    var srs;
    var wms_url =
      geoserver_url + "?service=WMS&version=1.1.1&request=GetCapabilities&";
    $.ajax({
      type: "GET",
      url: wms_url,
      dataType: "xml",
      success: function (xml) {
        //                  Get the projection and extent of the selected layer from the wms capabilities xml file
        var layers = xml.getElementsByTagName("Layer");
        var parser = new ol.format.WMSCapabilities();
        var result = parser.read(xml);
        var layers = result["Capability"]["Layer"]["Layer"];
        for (var i = 0; i < layers.length; i++) {
          if (layers[i].Title == layer) {
            layer_xml = xml.getElementsByTagName("Layer")[i + 1];
            layerParams = layers[i];
          }
        }
        srs = layer_xml.getElementsByTagName("SRS")[0].innerHTML;
        bbox = layerParams.BoundingBox[0].extent;
        var new_extent = ol.proj.transformExtent(bbox, srs, "EPSG:4326");
        var center = ol.extent.getCenter(new_extent);
        //                  Create a new view using the extent of the new selected layer
        var view = new ol.View({
          center: center,
          projection: "EPSG:4326",
          extent: new_extent,
          zoom: 6,
        });
        //                  Move the map to center on the selected watershed
        map.setView(view);
        map.getView().fit(new_extent, map.getSize());
      },
    });

    //      Display styling for the selected watershed boundaries
    var sld_string =
      '<StyledLayerDescriptor version="1.0.0"><NamedLayer><Name>nasaaccess:' +
      layer +
      '</Name><UserStyle><FeatureTypeStyle><Rule>\
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
      params: { LAYERS: gs_workspace + ":" + layer, SLD_BODY: sld_string },
      serverType: "geoserver",
      crossOrigin: "Anonymous",
    });

    basin_layer = new ol.layer.Image({
      source: wms_source,
      title: "subbasins",
    });

    //      add the selected layer to the map
    map.addLayer(basin_layer);
  };

  add_dem = function () {
    //      Get the selected value from the select watershed drop down
    var layer = $("#select_dem").val();
    var options = $("#select_dem option");

    var values = $.map(options, function (option) {
      if (option.value !== "") {
        return option.value;
      }
    });
    if (values.length < 2) {
      layer = values[0];
    }

    var store_id = gs_workspace + ":" + layer;
    var style = "DEM"; // Corresponds to a custom SLD style in geoserver

    //      Set the wms source to the url, workspace, and store for the dem layer of the selected watershed
    wms_source = new ol.source.ImageWMS({
      url: geoserver_url,
      params: { LAYERS: store_id, STYLES: style },
      serverType: "geoserver",
      crossOrigin: "Anonymous",
    });

    dem_layer = new ol.layer.Image({
      source: wms_source,
    });

    //      add dem layer to the map
    map.addLayer(dem_layer);
    var watershed = $("#select_watershed").val();

    if (watershed == "") {
      var layerParams;
      var layer_xml;
      var bbox;
      var srs;
      var wms_url =
        geoserver_url + "?service=WMS&version=1.1.1&request=GetCapabilities&";
      $.ajax({
        type: "GET",
        url: wms_url,
        dataType: "xml",
        success: function (xml) {
          //                  Get the projection and extent of the selected layer from the wms capabilities xml file
          var layers = xml.getElementsByTagName("Layer");
          var parser = new ol.format.WMSCapabilities();
          var result = parser.read(xml);
          var layers = result["Capability"]["Layer"]["Layer"];
          for (var i = 0; i < layers.length; i++) {
            if (layers[i].Title == layer) {
              layer_xml = xml.getElementsByTagName("Layer")[i + 1];
              layerParams = layers[i];
            }
          }
          srs = layer_xml.getElementsByTagName("SRS")[0].innerHTML;
          bbox = layerParams.BoundingBox[0].extent;
          var new_extent = ol.proj.transformExtent(bbox, srs, "EPSG:4326");
          var center = ol.extent.getCenter(new_extent);
          //                  Create a new view using the extent of the new selected layer
          var view = new ol.View({
            center: center,
            projection: "EPSG:4326",
            extent: new_extent,
            zoom: 6,
          });
          //                  Move the map to center on the selected layer
          map.setView(view);
          map.getView().fit(new_extent, map.getSize());
        },
      });
    } else {
      add_basins(); // Re-add basins layer if at watershed is selected
    }
  };

  init_all = function () {
    init_map();
    init_events();
  };

  create_series_dict = function (code) {};
  create_graphs = function (data) {
    chart = Highcharts.stockChart("graphs__panel", {
      rangeSelector: {
        selected: 1,
      },
      series: [data],
    });
  };
  nasaaccess = function () {
    //      Get the values from the nasaaccess form and pass them to the run_nasaaccess python controller
    var start = [];
    var end = [];

    if (!$("#sameDates_input").is(":checked")) {
      start = [
        $("#start_GLDASpolycentroid").val(),
        $("#start_GLDASwat").val(),
        $("#start_GPMpolyCentroid").val(),
        $("#start_GPMswat").val(),
        $("#start_NEXT_GDPPswat").val(),
        $("#start_NEX_GDPP_CMIP6").val(),
      ];
      end = [
        $("#end_GLDASpolycentroid").val(),
        $("#end_GLDASwat").val(),
        $("#end_GPMpolyCentroid").val(),
        $("#end_GPMswat").val(),
        $("#end_NEXT_GDPPswat").val(),
        $("#end_NEX_GDPP_CMIP6").val(),
      ];

      if (
        !$("#NEX_GDPP_CMIP6_input").is(":checked") &&
        !$("#NEXT_GDPPswat_input").is(":checked")
      ) {
        start = [
          $("#start_GLDASpolycentroid").val(),
          $("#start_GLDASwat").val(),
          $("#start_GPMpolyCentroid").val(),
          $("#start_GPMswat").val(),
          "",
          "",
        ];
        end = [
          $("#end_GLDASpolycentroid").val(),
          $("#end_GLDASwat").val(),
          $("#end_GPMpolyCentroid").val(),
          $("#end_GPMswat").val(),
          "",
          "",
        ];
      }
      if (
        $("#NEX_GDPP_CMIP6_input").is(":checked") &&
        $("#NEXT_GDPPswat_input").is(":checked")
      ) {
        start = [
          $("#start_GLDASpolycentroid").val(),
          $("#start_GLDASwat").val(),
          $("#start_GPMpolyCentroid").val(),
          $("#start_GPMswat").val(),
          $("#start_NEXT_GDPPswat").val(),
          $("#start_NEX_GDPP_CMIP6").val(),
        ];
        end = [
          $("#end_GLDASpolycentroid").val(),
          $("#end_GLDASwat").val(),
          $("#end_GPMpolyCentroid").val(),
          $("#end_GPMswat").val(),
          $("#end_NEXT_GDPPswat").val(),
          $("#end_NEX_GDPP_CMIP6").val(),
        ];
      }
      if (
        !$("#NEX_GDPP_CMIP6_input").is(":checked") &&
        $("#NEXT_GDPPswat_input").is(":checked")
      ) {
        start = [
          $("#start_GLDASpolycentroid").val(),
          $("#start_GLDASwat").val(),
          $("#start_GPMpolyCentroid").val(),
          $("#start_GPMswat").val(),
          $("#start_NEXT_GDPPswat").val(),
          "",
        ];
        end = [
          $("#end_GLDASpolycentroid").val(),
          $("#end_GLDASwat").val(),
          $("#end_GPMpolyCentroid").val(),
          $("#end_GPMswat").val(),
          $("#end_NEXT_GDPPswat").val(),
          "",
        ];
      }
      if (
        $("#NEX_GDPP_CMIP6_input").is(":checked") &&
        !$("#NEXT_GDPPswat_input").is(":checked")
      ) {
        start = [
          $("#start_GLDASpolycentroid").val(),
          $("#start_GLDASwat").val(),
          $("#start_GPMpolyCentroid").val(),
          $("#start_GPMswat").val(),
          "",
          $("#start_NEX_GDPP_CMIP6").val(),
        ];
        end = [
          $("#end_GLDASpolycentroid").val(),
          $("#end_GLDASwat").val(),
          $("#end_GPMpolyCentroid").val(),
          $("#end_GPMswat").val(),
          "",
          $("#end_NEX_GDPP_CMIP6").val(),
        ];
      }
    } else {
      if (
        !$("#NEX_GDPP_CMIP6_input").is(":checked") &&
        !$("#NEXT_GDPPswat_input").is(":checked")
      ) {
        start = [
          $("#start_pick").val(),
          $("#start_pick").val(),
          $("#start_pick").val(),
          $("#start_pick").val(),
          "",
          "",
        ];
        end = [
          $("#end_pick").val(),
          $("#end_pick").val(),
          $("#end_pick").val(),
          $("#end_pick").val(),
          "",
          "",
        ];
      }
      if (
        $("#NEX_GDPP_CMIP6_input").is(":checked") &&
        $("#NEXT_GDPPswat_input").is(":checked")
      ) {
        start = [
          $("#start_pick").val(),
          $("#start_pick").val(),
          $("#start_pick").val(),
          $("#start_pick").val(),
          $("#start_NEXT_GDPPswat").val(),
          $("#start_NEX_GDPP_CMIP6").val(),
        ];
        end = [
          $("#end_pick").val(),
          $("#end_pick").val(),
          $("#end_pick").val(),
          $("#end_pick").val(),
          $("#end_NEXT_GDPPswat").val(),
          $("#end_NEX_GDPP_CMIP6").val(),
        ];
      }
      if (
        !$("#NEX_GDPP_CMIP6_input").is(":checked") &&
        $("#NEXT_GDPPswat_input").is(":checked")
      ) {
        start = [
          $("#start_pick").val(),
          $("#start_pick").val(),
          $("#start_pick").val(),
          $("#start_pick").val(),
          $("#start_NEXT_GDPPswat").val(),
          "",
        ];
        end = [
          $("#end_pick").val(),
          $("#end_pick").val(),
          $("#end_pick").val(),
          $("#end_pick").val(),
          $("#end_NEXT_GDPPswat").val(),
          "",
        ];
      }
      if (
        $("#NEX_GDPP_CMIP6_input").is(":checked") &&
        !$("#NEXT_GDPPswat_input").is(":checked")
      ) {
        start = [
          $("#start_pick").val(),
          $("#start_pick").val(),
          $("#start_pick").val(),
          $("#start_pick").val(),
          "",
          $("#start_NEX_GDPP_CMIP6").val(),
        ];
        end = [
          $("#end_pick").val(),
          $("#end_pick").val(),
          $("#end_pick").val(),
          $("#end_pick").val(),
          "",
          $("#end_NEX_GDPP_CMIP6").val(),
        ];
      }
    }
    // var start = $('#start_pick').val();
    // var end = $('#end_pick').val();
    console.log(start);
    console.log(end);
    var functions = [];
    var NEXT_GDPPswat_inputs = [];
    var NEX_GDPP_CMIP6_inputs = [];

    $(".chk:checked").each(function () {
      if ($(this).val() != "sameDates") {
        functions.push($(this).val());
      }
    });
    if (functions.includes("NEXT_GDPPswat")) {
      NEXT_GDPPswat_inputs = [
        $("#NEXT_GDPPswat_model_select").val(),
        $("#NEXT_GDPPswat_type_select").val(),
        $("#NEXT_GDPPswat_slice_select").val(),
      ];
    }
    if (functions.includes("NEX_GDPP_CMIP6")) {
      NEX_GDPP_CMIP6_inputs = [
        $("#NEX_GDPP_CMIP6_model_select").val(),
        $("#NEX_GDPP_CMIP6_type_select").val(),
        $("#NEX_GDPP_CMIP6_slice_select").val(),
      ];
    }
    var watershed = $("#select_watershed").val();
    var dem = $("#select_dem").val();
    var email = $("#id_email").val();
    $.ajax({
      type: "POST",
      // url: "/apps/nasaaccess2/run/",
      url: "run/",
      data: {
        startDate: start,
        endDate: end,
        functions: functions,
        watershed: watershed,
        dem: dem,
        email: email,
        nexgdpp: NEXT_GDPPswat_inputs,
        nextgdppcmip: NEX_GDPP_CMIP6_inputs,
      },
    }).done(function (data) {
      console.log(data);
      if (data.Result === "nasaaccess is running") {
        $("#job_init").removeClass("hidden");
        setTimeout(function () {
          $("#job_init").addClass("hidden");
        }, 10000);
      }
    });
  };

  validateQuery = function () {
    var watershed = $("#select_watershed").val();
    var dem = $("#select_dem").val();
    var start = $("#start_pick").val();
    var end = $("#end_pick").val();
    var models = [];
    $(".chk:checked").each(function () {
      models.push($(this).val());
    });
    if (
      watershed === undefined ||
      dem === undefined ||
      start === undefined ||
      end === undefined ||
      models.length == 0
    ) {
      alert(
        "Please be sure you have selected a watershed, DEM, start and end dates, and at least 1 function"
      );
    } else {
      $("#cont-modal").modal("show");
    }
  };

  uploadShapefile = function () {
    let files = $("#shapefile-upload")[0].files;
    if (files.length !== 4) {
      alert(
        "The files you selected were rejected. Upload exactly 4 files ending in shp, shx, prj and dbf."
      );
      return;
    }
    let data = new FormData();
    Object.keys(files).forEach(function (file) {
      data.append("files", files[file]);
    });
    console.log(data);
    console.log(files);
    $.ajax({
      url: "upload_shp/",
      type: "POST",
      data: data,
      dataType: "json",
      processData: false,
      contentType: false,
      success: function (result) {
        $("#loading").hide();
        let shpSelect = document.getElementById("select_watershed");
        shpSelect.options[shpSelect.options.length] = new Option(
          `${result.file}`,
          `${result.file}`
        );
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
      },
    });
  };

  uploadDEM = function () {
    let files = $("#dem-upload")[0].files;

    let data = new FormData();
    Object.keys(files).forEach(function (file) {
      data.append("files", files[file]);
    });
    console.log(data);
    console.log(files);
    $.ajax({
      url: "upload_dem/",
      type: "POST",
      data: data,
      dataType: "json",
      processData: false,
      contentType: false,
      success: function (result) {
        $("#loading").hide();
        let demSelect = document.getElementById("select_dem");
        demSelect.options[demSelect.options.length] = new Option(
          `${result.file}`,
          `${result.file}`
        );
        // $('#select_dem').val(result.file);
        console.log(result.response);
        map.removeLayer(basin_layer);
        map.removeLayer(dem_layer);
        add_dem();
      },
      error: function (error) {
        console.log(error);
        $("#loading").hide();
      },
    });
  };
  submitAccessCode = function () {
    let data = {
      access_code: $("#access_code_input").val(),
    };
    $.ajax({
      url: "download/",
      type: "POST",
      data: data,
      dataType: "binary",
      xhr: function () {
        // Seems like the only way to get access to the xhr object
        var xhr = new XMLHttpRequest();
        xhr.responseType = "blob";
        return xhr;
      },
      success: function (data) {
        var a = document.createElement("a");
        var blob = new Blob([data], { type: "application/zip" });
        var url = window.URL.createObjectURL(blob);
        a.href = url;
        a.download = "nasaaccess.zip";
        document.body.append(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      },
      error: function (error) {
        console.log(error);
      },
    });
  };

  removeLayersFunctions = function () {
    Object.keys(layer_points).forEach(function (layer) {
      map.removeLayer(layer_points[layer]);
    });
  };
  updateLegend = function () {
    $("#tableLegend").removeClass("hidden");
    $("#tableLegend").empty();
  };

  plotAccessCode = function () {
    let data = {
      access_code: $("#access_code_input2").val(),
    };
    $.ajax({
      url: "plot/",
      type: "POST",
      data: data,
      dataType: "json",
      success: function (data) {
        updateLegend();
        removeLayersFunctions();

        if (Object.keys(data).length === 0) {
          $.notify("No Data found for any requested function", "warn");
          return;
        }

        console.log(data);
        var indice = 0;
        var arrayZooms = [];

        var func__names = Object.keys(data);

        func__names.forEach((func__name) => {
          var list__points = Object.keys(data[func__name]).map(function (key) {
            return data[func__name][key];
          });
          var layers_mapa = map_layers(
            list__points,
            func__name,
            indice,
            $("#access_code_input2").val()
          );
          console.log(layers_mapa[0]);
          var vectorSource = layers_mapa[1];
          var vectorLayer = layers_mapa[0];
          layer_points[func__name] = vectorLayer;
          map.addLayer(layer_points[func__name]);

          map.getView().fit(vectorSource.getExtent());
          arrayZooms.push(map.getView().getZoom());

          let test_style = new ol.style.Style({
            image: new ol.style.Circle({
              radius: 10,
              stroke: new ol.style.Stroke({
                color: "white",
              }),
              fill: new ol.style.Fill({
                color: colors_unique[indice],
              }),
            }),
          });
          let rowHTML = `<tr id= ${func__name}-row-complete>

                                 <th id="${func__name}-row-legend" class="flex items-center" >
                                     <span>${func__name}</span>

                                 </th>


                               </tr>`;
          let newSwitch = `
                            <div class="flex justify-between items-center">

                            <label 
                                for="${func__name}-switch"
                                class="flex items-center cursor-pointer"
                            >
                                <!-- toggle -->
                                <div class="relative">
                                <!-- input -->
                                <input id="${func__name}-switch" type="checkbox" class="sr-only chk" value="${func__name}" checked />
                                <!-- line -->
                                <div class="w-10 h-4 bg-gray-400 rounded-full shadow-inner"></div>
                                <!-- dot -->
                                <div class="dot absolute w-6 h-6 bg-white rounded-full shadow -left-1 -top-1 transition"></div>
                                </div>
                                <!-- label -->
                                <div class="ml-3 text-gray-700 font-medium">
                                </div>
                            </label>
                        </div>`;
          if (!document.getElementById(`${func__name}-row-complete`)) {
            $(rowHTML).appendTo("#tableLegend");
          }
          $(`#${func__name}-row-legend`).prepend($(getIconLegend(test_style)));
          $(`#${func__name}-row-legend`).prepend(newSwitch);

          $(`#${func__name}-switch`).change(function () {
            if (this.checked) {
              map.addLayer(layer_points[func__name]);
            } else {
              map.removeLayer(layer_points[func__name]);
            }
          });

          indice += 1;
        });
        let zoomLevel = Math.min(...arrayZooms);
        map.getView().setZoom(zoomLevel - 2);

        $.notify("Success", "success");
      },
      error: function (error) {
        console.log(error);
        $.notify("An Error was found while plotting your data", "error");
      },
    });
  };
  getValues = function () {
    map.on("singleclick", function (evt) {
      evt.stopPropagation();

      var feature = map.forEachFeatureAtPixel(
        evt.pixel,
        function (feature2, layer) {
          return feature2;
        }
      );
      if (feature) {
        let feature_single = feature
          .getProperties()
          ["features"][0].getProperties();
        console.log(feature_single);
        let data_json = {
          id: feature_single.id,
          name: feature_single.name,
          func: feature_single.func,
          access_code: feature_single.access_code,
        };
        console.log(feature_single.func);
        $.ajax({
          url: "getValues/",
          type: "POST",
          data: data_json,
          dataType: "json",
          success: function (data) {
            console.log(data);
            if (Object.keys(data).length === 0) {
              $.notify("No Data found", "warn");
              return;
            }
            let datasets = [];
            let y__axis__title = "";
            if (
              feature_single.func == "GLDASpolyCentroid" ||
              feature_single.func == "GLDASwat"
            ) {
              let min_temp = {
                data: data.min_val,
                label: "Min Tempt",
                borderColor: "#8e5ea2",
                fill: false,
              };
              let max_temp = {
                data: data.max_val,
                label: "Max Tempt",
                borderColor: "#3cba9f",
                fill: false,
              };
              datasets = [min_temp, max_temp];
              y__axis__title = "Temperature (°C)";
            } else {
              let val__rain = {
                data: data.val,
                label: "Precipitation",
                borderColor: "#8e5ea2",
                fill: false,
              };
              datasets = [val__rain];
              y__axis__title = "Precipitation (mm)";
            }
            const ctx = $("#time__series");
            if (myChart) {
              myChart.data = {
                labels: data.labels,
                datasets: datasets,
              };
              myChart.options.plugins.title.text = feature_single.func;
              myChart.options.scales.y.title.text = y__axis__title;

              myChart.update();
            } else {
              myChart = new Chart(ctx, {
                type: "line",
                data: {
                  labels: data.labels,
                  datasets: datasets,
                },
                options: {
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      title: {
                        display: true,
                        text: y__axis__title,
                      },
                    },
                  },
                  plugins: {
                    legend: {
                      position: "bottom",
                    },
                    title: {
                      display: true,
                      text: feature_single.func,
                    },
                    zoom: {
                      zoom: {
                        wheel: {
                          enabled: true,
                        },
                        pinch: {
                          enabled: true,
                        },
                        mode: "xy",
                      },
                    },
                  },
                },
              });
            }
            showPlot();
            $.notify("Success", "success");
          },
          error: function (error) {
            console.log(error);
            $.notify("An Error was found while plotting your data", "error");
          },
        });
      }
    });
  };
  map_layers = function (sites, func__name, indice, access_code) {
    try {
      sites = sites.map((site) => {
        return {
          type: "Feature",
          geometry: {
            type: "Point",
            coordinates: ol.proj.transform(
              [parseFloat(site.LONG), parseFloat(site.LAT)],
              "EPSG:4326",
              "EPSG:4326"
            ),
          },
          properties: {
            func: func__name,
            id: site.ID,
            name: site.NAME,
            lon: parseFloat(site.LONG),
            lat: parseFloat(site.LAT),
            elevation: site.ELEVATION,
            access_code: access_code,
          },
        };
      });

      let sitesGeoJSON = {
        type: "FeatureCollection",
        crs: {
          type: "name",
          properties: {
            name: "EPSG:4326",
          },
        },
        features: sites,
      };

      const vectorSource = new ol.source.Vector({
        features: new ol.format.GeoJSON().readFeatures(sitesGeoJSON),
      });
      var clusterSource = new ol.source.Cluster({
        distance: parseInt(30, 10),
        source: vectorSource,
      });
      var color_new = colors_unique[indice];

      let style_custom = featureStyle(color_new);
      var vectorLayer = new ol.layer.Vector({
        source: clusterSource,
        style: style_custom,
      });
      return [vectorLayer, vectorSource];
    } catch (error) {
      console.log(error);
      //   $.notify(
      //       {
      //           message: `Seems that there is no sites in the service`
      //       },
      //       {
      //           type: "info",
      //           allow_dismiss: true,
      //           z_index: 20000,
      //           delay: 5000,
      //           animate: {
      //             enter: 'animated fadeInRight',
      //             exit: 'animated fadeOutRight'
      //           },
      //           onShow: function() {
      //               this.css({'width':'auto','height':'auto'});
      //           }
      //       }
      //   )
    }
  };
  featureStyle = function (myColor) {
    var styleCache = {};
    var style2 = function (feature) {
      var size = feature.get("features").length;
      var style = styleCache[size];
      if (!style) {
        style = new ol.style.Style({
          image: new ol.style.Circle({
            radius: 10,
            stroke: new ol.style.Stroke({
              color: "white",
            }),
            fill: new ol.style.Fill({
              color: myColor,
            }),
          }),
          text: new ol.style.Text({
            text: size.toString(),
            fill: new ol.style.Fill({
              color: "#fff",
            }),
          }),
        });
        styleCache[size] = style;
      }
      return style;
    };

    return style2;
  };
  getIconLegend = function (style) {
    try {
      style = style.getImage();
      var radius = style.getRadius();
      var strokeWidth = style.getStroke().getWidth();
      var dx = radius + strokeWidth;

      var svgElem = $("<svg/>").attr({
        class: "svgs_legend",
        width: 11,
        height: 11,
      });
      $("<circle />")
        .attr({
          cx: 5,
          cy: 5,
          r: 5,
          stroke: style.getStroke().getColor(),
          "stroke-width": strokeWidth,
          fill: style.getFill().getColor(),
        })
        .appendTo(svgElem);

      // Convert DOM object to string to overcome from some SVG manipulation related oddities
      return $("<div>").append(svgElem).html();
    } catch (e) {
      console.log(e);
    }
  };

  /************************************************************************
   *                        DEFINE PUBLIC INTERFACE
   *************************************************************************/

  public_interface = {};

  /************************************************************************
   *                  INITIALIZATION / CONSTRUCTOR
   *************************************************************************/

  // Initialization: jQuery function that gets called when
  // the DOM tree finishes loading

  $(function () {
    $(document).ready(function () {
      if (ERROR_STR != "") {
        console.log("ready!");
        $.notify(ERROR_STR, "info");
      }
    });
    init_all();
    getValues();
    const start_all_4 = datepicker("#start_pick", {
      id: 0,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });
    const end_all_4 = datepicker("#end_pick", {
      id: 1,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });

    const start_1 = datepicker("#start_GLDASpolycentroid", {
      id: 2,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });
    const end_1 = datepicker("#end_GLDASpolycentroid", {
      id: 3,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });

    const start_2 = datepicker("#start_GLDASwat", {
      id: 4,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });
    const end_2 = datepicker("#end_GLDASwat", {
      id: 5,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });

    const start_3 = datepicker("#start_GPMpolyCentroid", {
      id: 6,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });
    const end_3 = datepicker("#end_GPMpolyCentroid", {
      id: 7,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });

    const start_4 = datepicker("#start_GPMswat", {
      id: 8,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });
    const end_4 = datepicker("#end_GPMswat", {
      id: 9,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });

    const start_5 = datepicker("#start_NEXT_GDPPswat", {
      id: 10,
      startDate: new Date(2006, 0, 1),
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });
    const end_5 = datepicker("#end_NEXT_GDPPswat", {
      id: 11,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });
    const start_6 = datepicker("#start_NEX_GDPP_CMIP6", {
      id: 12,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });
    const end_6 = datepicker("#end_NEX_GDPP_CMIP6", {
      id: 13,
      formatter: (input, date, instance) => {
        const value = date
          .toLocaleDateString("en-GB", {
            // you can use undefined as first argument
            year: "numeric",
            month: "2-digit",
            day: "2-digit",
          })
          .split("/")
          .reverse()
          .join("-");

        input.value = value; // => '1/1/2099'
      },
    });

    start_6.setDate(new Date(2015, 0, 1), true);
    end_6.setDate(new Date(), true);
    start_5.setDate(new Date(2006, 0, 1), true);
    end_5.setDate(new Date(), true);
    //        $("#help-modal").modal('show');
    $("#loading").addClass("hidden");

    $("#shp_submit").click(function () {
      $("#loading").removeClass("hidden");
    });

    $("#dem_submit").click(function () {
      $("#loading").removeClass("hidden");
    });

    $("#nasaaccess").click(function () {
      validateQuery();
    });

    $("#submit_form").click(function () {
      console.log("PRINT ME!");
      $("#cont-modal").modal("hide");
      nasaaccess();
    });

    $("#funcs_def").click(function () {
      $("#functions-modal").modal("show");
    });

    $("#download_data").click(function () {
      $("#download-modal").modal("show");
    });
    $("#plot_data").click(function () {
      $("#plot-modal").modal("show");
    });
    $("#select_watershed").change(function () {
      map.removeLayer(basin_layer);
      add_basins();
    });

    $("#select_dem").change(function () {
      map.removeLayer(basin_layer);
      map.removeLayer(dem_layer);
      add_dem();
    });

    $("#addShp").click(function () {
      console.log("Add Watershed");
      $("#shp-modal").modal("show");
    });

    $("#addDem").click(function () {
      console.log("Add DEM");
      $("#dem-modal").modal("show");
    });
    $("#shp_submit").click(uploadShapefile);
    $("#dem_submit").click(uploadDEM);
    $("#submit_access_code").click(submitAccessCode);
    $("#plot_access_code").click(plotAccessCode);

    $("#GLDASpolycentroid_input").change(function () {
      if (!$("#sameDates_input").is(":checked")) {
        if (this.checked) {
          $("#GLDASpolycentroid_id_block").removeClass("h-0");
          $("#GLDASpolycentroid_id_block").addClass("max-h-fit");
          $("#GLDASpolycentroid_id_block").removeClass("overflow-hidden");
          $("#GLDASpolycentroid_id_block").addClass("ease-in");
          $("#GLDASpolycentroid_id_block").addClass("duration-700");
        } else {
          $("#GLDASpolycentroid_id_block").removeClass("max-h-fit");
          $("#GLDASpolycentroid_id_block").addClass("h-0");
          $("#GLDASpolycentroid_id_block").addClass("overflow-hidden");
          $("#GLDASpolycentroid_id_block").removeClass("ease-in");
          $("#GLDASpolycentroid_id_block").removeClass("duration-700");
        }
      }
    });

    $("#GLDASwat_input").change(function () {
      if (!$("#sameDates_input").is(":checked")) {
        if (this.checked) {
          $("#GLDASwat_id_block").removeClass("h-0");
          $("#GLDASwat_id_block").addClass("max-h-fit");
          $("#GLDASwat_id_block").removeClass("overflow-hidden");
          $("#GLDASwat_id_block").addClass("ease-in");
          $("#GLDASwat_id_block").addClass("duration-700");
        } else {
          $("#GLDASwat_id_block").removeClass("max-h-fit");
          $("#GLDASwat_id_block").addClass("h-0");
          $("#GLDASwat_id_block").addClass("overflow-hidden");
          $("#GLDASwat_id_block").removeClass("ease-in");
          $("#GLDASwat_id_block").removeClass("duration-700");
        }
      }
    });

    $("#GPMpolyCentroid_input").change(function () {
      if (!$("#sameDates_input").is(":checked")) {
        if (this.checked) {
          $("#GPMpolyCentroid_id_block").removeClass("h-0");
          $("#GPMpolyCentroid_id_block").addClass("max-h-fit");
          $("#GPMpolyCentroid_id_block").removeClass("overflow-hidden");
          $("#GPMpolyCentroid_id_block").addClass("ease-in");
          $("#GPMpolyCentroid_id_block").addClass("duration-700");
        } else {
          $("#GPMpolyCentroid_id_block").removeClass("max-h-fit");
          $("#GPMpolyCentroid_id_block").addClass("h-0");
          $("#GPMpolyCentroid_id_block").addClass("overflow-hidden");
          $("#GPMpolyCentroid_id_block").removeClass("ease-in");
          $("#GPMpolyCentroid_id_block").removeClass("duration-700");
        }
      }
    });

    $("#GPMswat_input").change(function () {
      if (!$("#sameDates_input").is(":checked")) {
        if (this.checked) {
          $("#GPMswat_id_block").removeClass("h-0");
          $("#GPMswat_id_block").addClass("max-h-fit");
          $("#GPMswat_id_block").removeClass("overflow-hidden");
          $("#GPMswat_id_block").addClass("ease-in");
          $("#GPMswat_id_block").addClass("duration-700");
        } else {
          $("#GPMswat_id_block").removeClass("max-h-fit");
          $("#GPMswat_id_block").addClass("h-0");
          $("#GPMswat_id_block").addClass("overflow-hidden");
          $("#GPMswat_id_block").removeClass("ease-in");
          $("#GPMswat_id_block").removeClass("duration-700");
        }
      }
    });

    $("#NEXT_GDPPswat_input").change(function () {
      if (this.checked) {
        $("#NEXT_GDPPswat_id_block").removeClass("h-0");
        $("#NEXT_GDPPswat_id_block").addClass("max-h-fit");
        $("#NEXT_GDPPswat_id_block").removeClass("overflow-hidden");
        $("#NEXT_GDPPswat_id_block").addClass("ease-in");
        $("#NEXT_GDPPswat_id_block").addClass("duration-700");
      } else {
        $("#NEXT_GDPPswat_id_block").removeClass("max-h-fit");
        $("#NEXT_GDPPswat_id_block").addClass("h-0");
        $("#NEXT_GDPPswat_id_block").addClass("overflow-hidden");
        $("#NEXT_GDPPswat_id_block").removeClass("ease-in");
        $("#NEXT_GDPPswat_id_block").removeClass("duration-700");
      }
    });

    $("#NEX_GDPP_CMIP6_input").change(function () {
      if (this.checked) {
        $("#NEX_GDPP_CMIP6_id_block").removeClass("h-0");
        $("#NEX_GDPP_CMIP6_id_block").addClass("max-h-fit");
        $("#NEX_GDPP_CMIP6_id_block").removeClass("overflow-hidden");
        $("#NEX_GDPP_CMIP6_id_block").addClass("ease-in");
        $("#NEX_GDPP_CMIP6_id_block").addClass("duration-700");
      } else {
        $("#NEX_GDPP_CMIP6_id_block").removeClass("max-h-fit");
        $("#NEX_GDPP_CMIP6_id_block").addClass("h-0");
        $("#NEX_GDPP_CMIP6_id_block").addClass("overflow-hidden");
        $("#NEX_GDPP_CMIP6_id_block").removeClass("ease-in");
        $("#NEX_GDPP_CMIP6_id_block").removeClass("duration-700");
      }
    });
    $("#sameDates_input").change(function () {
      if (this.checked) {
        $("#sameDates_id_block").removeClass("h-0");
        $("#sameDates_id_block").addClass("max-h-fit");
        $("#sameDates_id_block").removeClass("overflow-hidden");
        $("#sameDates_id_block").addClass("ease-in");
        $("#sameDates_id_block").addClass("duration-700");

        //GPMswat_id_block
        $("#GPMswat_id_block").removeClass("max-h-fit");
        $("#GPMswat_id_block").addClass("h-0");
        $("#GPMswat_id_block").addClass("overflow-hidden");
        $("#GPMswat_id_block").removeClass("ease-in");
        $("#GPMswat_id_block").removeClass("duration-700");

        //GPMpolyCentroid_id_block
        $("#GPMpolyCentroid_id_block").removeClass("max-h-fit");
        $("#GPMpolyCentroid_id_block").addClass("h-0");
        $("#GPMpolyCentroid_id_block").addClass("overflow-hidden");
        $("#GPMpolyCentroid_id_block").removeClass("ease-in");
        $("#GPMpolyCentroid_id_block").removeClass("duration-700");

        //GLDASwat_id_block
        $("#GLDASwat_id_block").removeClass("max-h-fit");
        $("#GLDASwat_id_block").addClass("h-0");
        $("#GLDASwat_id_block").addClass("overflow-hidden");
        $("#GLDASwat_id_block").removeClass("ease-in");
        $("#GLDASwat_id_block").removeClass("duration-700");

        //GLDASpolycentroid_id_block
        $("#GLDASpolycentroid_id_block").removeClass("max-h-fit");
        $("#GLDASpolycentroid_id_block").addClass("h-0");
        $("#GLDASpolycentroid_id_block").addClass("overflow-hidden");
        $("#GLDASpolycentroid_id_block").removeClass("ease-in");
        $("#GLDASpolycentroid_id_block").removeClass("duration-700");
      } else {
        $("#sameDates_id_block").removeClass("max-h-fit");
        $("#sameDates_id_block").addClass("h-0");
        $("#sameDates_id_block").addClass("overflow-hidden");
        $("#sameDates_id_block").removeClass("ease-in");
        $("#sameDates_id_block").removeClass("duration-700");
        if ($("#GPMswat_input").is(":checked")) {
          $("#GPMswat_id_block").removeClass("h-0");
          $("#GPMswat_id_block").addClass("max-h-fit");
          $("#GPMswat_id_block").removeClass("overflow-hidden");
          $("#GPMswat_id_block").addClass("ease-in");
          $("#GPMswat_id_block").addClass("duration-700");
        }
        if ($("#GPMpolyCentroid_input").is(":checked")) {
          $("#GPMpolyCentroid_id_block").removeClass("h-0");
          $("#GPMpolyCentroid_id_block").addClass("max-h-fit");
          $("#GPMpolyCentroid_id_block").removeClass("overflow-hidden");
          $("#GPMpolyCentroid_id_block").addClass("ease-in");
          $("#GPMpolyCentroid_id_block").addClass("duration-700");
        }
        if ($("#GLDASwat_input").is(":checked")) {
          $("#GLDASwat_id_block").removeClass("h-0");
          $("#GLDASwat_id_block").addClass("max-h-fit");
          $("#GLDASwat_id_block").removeClass("overflow-hidden");
          $("#GLDASwat_id_block").addClass("ease-in");
          $("#GLDASwat_id_block").addClass("duration-700");
        }
        if ($("#GLDASpolycentroid_input").is(":checked")) {
          $("#GLDASpolycentroid_id_block").removeClass("h-0");
          $("#GLDASpolycentroid_id_block").addClass("max-h-fit");
          $("#GLDASpolycentroid_id_block").removeClass("overflow-hidden");
          $("#GLDASpolycentroid_id_block").addClass("ease-in");
          $("#GLDASpolycentroid_id_block").addClass("duration-700");
        }
      }
    });
    $("#NEX_GDPP_CMIP6_slice_select").change(function () {
      if ($(this).val() == "historical") {
        start_6.setMin();
        start_6.setMax();

        start_6.setDate(new Date(1950, 0, 1), true);
        start_6.setMin(new Date(1950, 0, 1));
        start_6.setMax(new Date(2014, 11, 31));

        end_6.setMin();
        end_6.setMax();

        end_6.setDate(new Date(2014, 11, 31), true);
        end_6.setMin(new Date());
      } else {
        start_6.setMin();
        start_6.setMax();

        start_6.setDate(new Date(2015, 0, 1), true);
        start_6.setMin(new Date(2015, 0, 1));

        end_6.setMin();
        end_6.setMax();

        end_6.setDate(new Date(), true);
        end_6.setMin(new Date());
      }
    });
    $("#NEXT_GDPPswat_slice_select").change(function () {
      if ($(this).val() == "historical") {
        start_5.setMin();
        start_6.setMax();

        start_5.setDate(new Date(1950, 0, 1), true);
        start_5.setMin(new Date(1950, 0, 1));
        start_5.setMax(new Date(2005, 11, 31));

        end_5.setMin();
        end_5.setMax();

        end_5.setDate(new Date(2005, 11, 31), true);
        end_5.setMin(new Date());
      } else {
        start_5.setMin();
        start_5.setMax();

        start_5.setDate(new Date(2006, 0, 1), true);

        start_5.setMin(new Date(2006, 0, 1));

        end_5.setMin();
        end_5.setMax();

        end_5.setDate(new Date(), true);
        end_5.setMin(new Date());
      }
    });
  });

  return public_interface;
})(); // End of package wrapper
