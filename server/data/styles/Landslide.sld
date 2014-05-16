<?xml version="1.0" encoding="ISO-8859-1"?>
<StyledLayerDescriptor version="1.0.0" 
 xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" 
 xmlns="http://www.opengis.net/sld" 
 xmlns:ogc="http://www.opengis.net/ogc" 
 xmlns:xlink="http://www.w3.org/1999/xlink" 
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!-- a Named Layer is the basic building block of an SLD document -->
  <NamedLayer>
    <Name>default_raster</Name>
    <UserStyle>
      <Title>Default Raster</Title>
      <Abstract>A sample style that draws a raster, good for displaying imagery</Abstract>
      <FeatureTypeStyle>
        <Rule>
          <Name>rule1</Name>
          <Title>Opaque Raster</Title>
          <Abstract>A raster with 100% opacity</Abstract>
          <RasterSymbolizer>
            <Opacity>0.7</Opacity>
            <ColorMap>
              <ColorMapEntry color="#000000" quantity="0" opacity="0"/>
              <ColorMapEntry color="#E60000" label="Low Hazard" quantity="2"/> 
              <ColorMapEntry color="#E69800" label="Moderate Hazard" quantity="3"/> 
              <ColorMapEntry color="#FFFF00" label="High Hazard" quantity="4"/> 
              <ColorMapEntry color="#FD7571" quantity="6" opacity="0"/>
            </ColorMap>
          </RasterSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
