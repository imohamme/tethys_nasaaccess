
    <StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" version="1.0.0" xmlns:ogc="http://www.opengis.net/ogc" xmlns:sld="http://www.opengis.net/sld">
    <UserLayer>
        <sld:LayerFeatureConstraints>
        <sld:FeatureTypeConstraint/>
        </sld:LayerFeatureConstraints>
        <sld:UserStyle>
        <sld:Name>dem_TX_style</sld:Name>
        <sld:FeatureTypeStyle>
            <sld:Rule>
            <sld:RasterSymbolizer>
                <sld:ChannelSelection>
                <sld:GrayChannel>
                    <sld:SourceChannelName>1</sld:SourceChannelName>
                </sld:GrayChannel>
                </sld:ChannelSelection>
                <sld:ColorMap type="ramp">
                    <sld:ColorMapEntry color="#ea5739" label="0.0" quantity="0.0"/><sld:ColorMapEntry color="#fdbf71" label="15.5" quantity="15.5"/><sld:ColorMapEntry color="#feffc0" label="31.0" quantity="31.0"/><sld:ColorMapEntry color="#bde2ee" label="46.4" quantity="46.4"/><sld:ColorMapEntry color="#6399c7" label="61.9" quantity="61.9"/>
                </sld:ColorMap>
            </sld:RasterSymbolizer>
            </sld:Rule>
        </sld:FeatureTypeStyle>
        </sld:UserStyle>
    </UserLayer>
    </StyledLayerDescriptor>
    