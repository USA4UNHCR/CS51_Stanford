  import React, {Component} from 'react';
  import GoogleMap from 'google-map-react';
  import SplitterLayout from 'react-splitter-layout';
  import 'react-splitter-layout/lib/index.css';
  import {
    initialCenter,
    initialZoom,
    M_WIDTH,
  } from './data/numbers'
  import Marker from './marker.js';
  import PropTypes from 'prop-types';
  import TableEntry from './TableEntry.js';
  import './fonts.css';
  import { Timeline } from 'react-twitter-widgets';

  // keep track of data
  import {markerList} from './data/markerData';
  var finalData = markerList;

  // return map bounds based on list of places
  const getMapBounds = (map, maps, finalData) => {
    const bounds = new maps.LatLngBounds();
    finalData.forEach((marker) => {
      bounds.extend(new maps.LatLng(
        marker.Latitude,
        marker.Longitude,
      ));
    });
    return bounds;
  };

  // re-center map when resizing the window
  const bindResizeListener = (map, maps, bounds) => {
    maps.event.addDomListenerOnce(map, 'idle', () => {
      maps.event.addDomListener(window, 'resize', () => {
        map.fitBounds(bounds);
      });
    });
  };

  // fit map to its bounds after the api is loaded
  const apiIsLoaded = (map, maps, finalData, state, e) => {
    console.log(state);
    // console.log(maps);
    // Get bounds by our places
    const bounds = getMapBounds(map, maps, finalData);
    // Fit map to bounds
    map.fitBounds(bounds);
    // Bind the resize listener
    bindResizeListener(map, maps, bounds);
  };

  // abbreviates the number of followers on each marker
  const convertScore = (marker) => {
    var abbreviate = require('number-abbreviate');
    if (typeof marker['Followers'] === 'string') {
      return marker['Followers'];
    } else {
      return abbreviate(Math.round(marker['Followers'])).toString();
    }
  }

  // style for the title
  const titleStyle = {
    color: 'black',
    fontSize: 24,
    fontFamily: 'Roboto',
    padding: 15,
    fontWeight: 'bold',
  };

  class SimpleMap extends Component {
    static propTypes = {
      hoverKey: PropTypes.string, // @controllable
      clickKey: PropTypes.string, // @controllable
      onCenterChange: PropTypes.func, // @controllable generated fn
      onZoomChange: PropTypes.func, // @controllable generated fn
      onHoverKeyChange: PropTypes.func, // @controllable generated fn
    };

    // when a marker is clicked, the map re-centers around it and indicates that
    // it's the active marker by enlarging
    _onChildClick = (map, marker, maps) => {
      this.setState({
        center: [marker.lat, marker.lng],
        activeMarker: marker.marker,
      });
      console.log("child clicked");
    }

    constructor(props) {
      super(props);
      this.state = {
        activeMarker: {
          'Handle': 'twitter',
          'User': 'No selected marker',
          'User location': 'N/A',
        },
        center: initialCenter,
        zoom: initialZoom,
        places: null,
        maps: null,
        dataIsLoaded: false,
        data: markerList,
      }
    }

    componentDidMount() {
      const self = this;
      console.log('mounted!');

      fetch('https://gist.githubusercontent.com/pessoaflavio/340e51f7f14b2832ba5bdbb0a67d6432/raw/eccf68aa9818df16b979c3edab63ff8156c5645b/influencer.json', {
        method: 'GET',
        mode: 'cors',
        })
      .then(res => res.json())
      .then((result) => {
          /* star array */
          var starA = Object.values(result.star);
          for (var i = 0; i < starA.length; i++) {
            starA[i].influence = "star";
          }

          /* macro array */
          var macroA = Object.values(result.macro);
          for (var j = 0; j < macroA.length; j++) {
            macroA[j].influence = "macro";
          }

          // {/* mid array */}
          var midA = Object.values(result.mid);
          for (var k = 0; k < midA.length; k++) {
            midA[k].influence = "mid";
          }

          // {/* micro array */}
          var microA = Object.values(result.micro);
          for (var l = 0; l < microA.length; l++) {
            microA[l].influence = "micro";
          }

          // combine all the arrays together in order from highest rank -> lowest
          let newStar = starA.concat(macroA);
          let starB = newStar.concat(midA);
          let starC = starB.concat(microA);
          let finalData = starC;

          console.log(finalData);
          this.setState({isLoaded: true,data: finalData});
        },
        // Note: it's important to handle errors here
        // instead of a catch() block so that we don't swallow
        // exceptions from actual bugs in components.
        (error) => {this.setState({isLoaded: true,error})}
        )


      // makeData(data => self.setState({ data: data}));

      // self.setState(data => makeData())
      // self.setState({dataIsLoaded: true })
      //
      // if(this.state.dataIsLoaded === false) {
      //   console.log('data not yet loaded');
      // } else {
      //   console.log('data loaded');
      // }

    }

    render() {
      const { error, isLoaded, data } = this.state;
      if (error) {
      return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
      return <div><h1>Loading...</h1></div>;
    } else {
      return (
        // ====
        <div>
        {/* restrict sidebar to 20% of the screen */}
        { this.state && this.state.data &&
          <SplitterLayout
          primaryIndex={1}
          primaryMinSize={window.innerWidth*0.2}
          secondaryMinSize={window.innerWidth*0.8}>
            <div style={{ height: '100vh', width: '100%' }}>
              <GoogleMap
                bootstrapURLKeys={{key: 'AIzaSyDnupYTnmMzxiKq-hVRGMyaahGowNkFQUc'}}
                center={this.state.center}
                zoom={this.state.zoom}
                hoverDistance={M_WIDTH}
                yesIWantToUseGoogleMapApiInternals={true}
                onGoogleApiLoaded={({ map, maps }) => apiIsLoaded(map, maps, this.state.data, this.state )}
                onChildClick={this._onChildClick}
              >
                {(this.state.data).map((marker, index) => (
                    <Marker
                      key={index}
                      index={index}
                      activeMarker = {this.state.activeMarker}
                      lat={marker['Latitude']}
                      lng={marker['Longitude']}
                      text={convertScore(marker)}
                      hover={this.props.hoverKey === index}
                      marker={marker}
                      >
                    </Marker>
                ))}
              </GoogleMap>
            </div>

            {/* sidebar */}
            <div>
              <div style={titleStyle}> Selected Marker </div>

              {/* active marker entry */}
              <TableEntry
                activeMarker = {this.state.activeMarker}
                marker={this.state.activeMarker}
                >
              </TableEntry>

              {/* active marker's twitter feed */}
              <Timeline
                dataSource={{
                  sourceType: 'profile',
                  screenName: (this.state.activeMarker.Handle).toString(),
                }}
                options={{
                  username: 'Twitter Widget',
                  height: '400'
                }}
              />

              {/* divider */}
              <div style = {{
                border: '1px solid whitesmoke',
              }} />

              {/* influencer list */}
              <div style={titleStyle}> Influencers </div>
              {(this.state.data).map((marker, index) => (
                    <TableEntry
                      key={index}
                      index={index}
                      activeMarker = {this.state.activeMarker}
                      marker={marker}
                      >
                    </TableEntry>
                ))}
              </div>
          </SplitterLayout>
          }
        </div>
        // ====
      );
    }
  }


    }


  export default SimpleMap;
