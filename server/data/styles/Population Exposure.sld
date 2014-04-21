<?xml version="1.0" encoding="ISO-8859-1"?>
<StyledLayerDescriptor version="1.0.0" 
    xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" 
    xmlns="http://www.opengis.net/sld" 
    xmlns:ogc="http://www.opengis.net/ogc" 
    xmlns:xlink="http://www.w3.org/1999/xlink" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>Tacloban Population</Name>
    <UserStyle>
      <Title>Tacloban Population</Title>
      <FeatureTypeStyle>
        <Rule>
          <RasterSymbolizer>
            <Opacity>0.6</Opacity>
            <ColorMap>
              <ColorMapEntry color="#0000FF" quantity="0" opacity="0"/>
              <ColorMapEntry color="#08FFDA" quantity="0.1"/>
              <ColorMapEntry color="#38A800" quantity="0.5"/>
              <ColorMapEntry color="#79C900" quantity="1"/>
              <ColorMapEntry color="#CEED00" quantity="2"/>
              <ColorMapEntry color="#FFCC00" quantity="5" />
              <ColorMapEntry color="#FF6600" quantity="10" />
              <ColorMapEntry color="#FF0000" quantity="20" />
              <ColorMapEntry color="#7A0000" quantity="50" />
            </ColorMap>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
