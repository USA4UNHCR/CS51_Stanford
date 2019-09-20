// Component for an entry in the influencer table
// Includes name, handle, location, and influence flag
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {
  M_WIDTH,
} from './data/numbers';
import InfluenceFlag from './influenceFlag.js';
import './fonts.css';

const cellStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  borderBottom: '2px solid whitesmoke',
};

const cellSelectedStyle = {
  ...cellStyle,
  backgroundColor: '#e2f3ff',
};

const entryStyle = {
  display: 'flex',
  padding: 20,
};

const infoStyle = {
  display: 'flex',
  flexDirection: 'column',
  whiteSpace: 'wrap',
  justifyContent: 'start',
};

const bodyStyle = {
  color: 'black',
  fontSize: 15,
  fontFamily: 'Roboto',
};

const nameStyle = {
  ...bodyStyle,
  fontWeight: 'bold',
  paddingBottom: '0em',
};

const handleStyle = {
  ...bodyStyle,
  fontSize: 14,
  color: 'gray',
  paddingBottom: '1em',
};

const locStyle = {
  ...bodyStyle,
  fontSize: 12,
  color: 'gray',
};

export default class TableEntry extends Component {
  static propTypes = {
    influence: PropTypes.number,
  };

  render() {
    // highlights the entry if its marker is active (has been clicked)
    let cellStyleFinal = cellStyle;
    if (this.props.activeMarker['Handle'] === this.props.marker['Handle']) {
      cellStyleFinal = cellSelectedStyle;
    }

    return (
      <a>
        <div style={cellStyleFinal}>

          <div style={entryStyle}>
            {/* influencer info */}
            <div style={infoStyle}>
              <div style={nameStyle}> {this.props.marker['User']} </div>
              <div style={handleStyle}> @{this.props.marker['Handle']} </div>
              <div style={locStyle}> {this.props.marker['User location']} </div>
            </div>
          </div>

          {/* influence flag */}
          <div style={{
            minWidth: M_WIDTH * 4,
          }}>
          {this.props.marker && this.props.marker.influence &&
            <InfluenceFlag
              influence={this.props.marker.influence}>
            </InfluenceFlag>
          }
          </div>
        </div>
      </a>
    );
  }
}
