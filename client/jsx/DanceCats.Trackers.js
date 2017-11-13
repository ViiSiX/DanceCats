var Constants = require('../js/DanceCats.Constants');


var TrackerList = React.createClass({
  getInitialState: function() {
    return {
      seq: 0,
      data: null
    };
  },

  _trackersUpdated: function(data) {
    if (data.seq > this.state.seq) {
      this.setState({
        seq: data.seq,
        data: data.trackers
      })
    }
  },
  
  render: function () {
    var tracker_rows = null;
    if (this.state.seq > 0) {
      tracker_rows =
        <tbody>
        {this.state.data.map(function (tracker) {
          return <tr key={tracker.id}>
            <td>{tracker.id}</td>
            <td>{tracker.jobName}<br/><b>DB: {tracker.database}</b></td>
            <td>{tracker.ranOn}</td>
            <td>{tracker.duration}</td>
            <td>{tracker.status}</td>
            <td>
              {tracker.csv !== null ? <a href={tracker.csv}>CSV</a> : null}<br/>
              {tracker.xlsx !== null ? <a href={tracker.xlsx}>XLSX</a> : null}
            </td>
          </tr>
        })}
        </tbody>
    }
    return (
      <div className="table-responsive">
        <table className="table table-condensed">
          <thead>
            <tr>
              <th>Track Id</th>
              <th>Job Name</th>
              <th>Ran On</th>
              <th>Duration (ms)</th>
              <th>Status</th>
              <th>Download</th>
            </tr>
          </thead>
          {tracker_rows}
        </table>
      </div>
    )
  }
});

var tr = ReactDOM.render(
  <TrackerList/>,
  document.getElementById('dc-trackers')
);

socket.on(Constants.WS_TRACKERS_RECEIVE, function(data){
  tr._trackersUpdated(data);
  setTimeout(function() {
    socket.emit(Constants.WS_TRACKERS_SEND)
  }, 3000);
});